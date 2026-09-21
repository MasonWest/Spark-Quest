# -*- coding: utf-8 -*-
"""重写 L4 题库的干扰项（正确项零改动），消除「正确答案恒最长」线索。

背景
    2026-09-21 实测 L4 90 题：71/90（78.9%）正确项是唯一最长选项，
    「猜最长」命中率 82.2%（随机基线 25%，Wilson 95% CI [73.1%, 88.8%]），
    正确项均长 23.1 字 vs 干扰项均长 9.0 字，62 题存在 <8 字的桩式干扰项。
    82.2% > MASTERY_THRESHOLD(80) → 完全不看内容也能及格。

策略（对齐 2026-09-14 L2/L3 修复口径）
    1. **正确项文本零改动** —— prompt / explanation / dimension / correct_index 一律不动。
       `quiz_answer_log` 保持 append-only，历史作答的 `selected_index` 仍指向同一正确项。
    2. 只替换干扰项，改成「事实错误、但长度与正确项相当」的完整说法。
    3. 干扰项必须是**真的错的**（不能是另一种正确答案，否则会引入新的歧义缺陷）。
    4. **不改正确项、不缩题**：正确项本身写得较长时（如 Project Tungsten 75 字），
       让干扰项去匹配它，而不是缩短正确项 —— 否则 661 题里凡是与正确项长度相近的
       其它选项都会被牵连。
    5. 代码/标识符类题（explain() / show() / Parsed 等）保留原短写法：这类题的
       正确项本身就短，长度线索风险低，强行加长反而不自然。
    6. L4 答案位置分布 `[22,24,22,22]` 已均衡 → **不做选项重排**。

数据文件
    backend/app/l4_distractors_20260921.json
    每条 {"l": lesson_slug, "qi": 题内序号, "d": {"0": "新干扰项", ...}}
    键是选项下标，只允许出现在「非 correct_index」的位置。

用法
    cd backend
    python app/rewrite_l4_distractors_20260921.py            # dry-run
    python app/rewrite_l4_distractors_20260921.py --apply    # 写 DB + quiz_seed.json
"""

from __future__ import annotations

import json
import re
import shutil
import sqlite3
import statistics
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent          # backend/
APP = BASE / "app"
DB = BASE / "spark_quest.db"
SEED = APP / "quiz_seed.json"
PATCH = APP / "l4_distractors_20260921.json"
PREFIX = "l4-"


def norm(s: str) -> str:
    """归一化用于 prompt 匹配（与 sync_seed.py 同口径）。"""
    return re.sub(r"\s+", "", s).replace("\u201c", '"').replace("\u201d", '"')


def backup(path: Path) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = path.with_name(path.name + f".bak_before_l4distractors_{ts}")
    shutil.copy(path, dst)
    return dst


def load_db_lessons(cur) -> dict:
    """slug -> lesson_id（仅 L4）。"""
    out = {}
    for slug, lid in cur.execute(
        "SELECT slug, id FROM lessons WHERE slug LIKE ?", (PREFIX + "%",)
    ):
        out[slug] = lid
    return out


def stats(questions):
    """长度线索体检：返回 (严格最长题数, 最长含并列, 命中数, 排名分布, margin 列表)。"""
    strict = tied = never = 0
    rank = Counter()
    margins, correct_lens, distractor_lens = [], [], []
    dup_opt = 0
    for q in questions:
        opts = q["options"]
        ci = q["correct_index"]
        if len({o.strip() for o in opts}) < len(opts):
            dup_opt += 1
        L = [len(o) for o in opts]
        mx = max(L)
        long_set = {i for i, l in enumerate(L) if l == mx}
        if ci in long_set:
            if len(long_set) == 1:
                strict += 1
            else:
                tied += 1
        else:
            never += 1
        order = sorted(range(len(L)), key=lambda i: -L[i])
        rank[order.index(ci) + 1] += 1
        margins.append(L[ci] - sorted(L, reverse=True)[1])
        correct_lens.append(L[ci])
        distractor_lens.extend(L[i] for i in range(len(L)) if i != ci)
    n = len(questions)
    return {
        "n": n,
        "strict_longest": strict,
        "longest_inc_tied": strict + tied,
        "hit": (strict + tied) / n if n else 0,
        "rank": dict(sorted(rank.items())),
        "margin_mean": round(statistics.mean(margins), 1) if n else 0,
        "margin_gt10": sum(1 for m in margins if m > 10),
        "margin_ge3": sum(1 for m in margins if m >= 3),
        "correct_mean_len": round(statistics.mean(correct_lens), 1) if n else 0,
        "distractor_mean_len": round(statistics.mean(distractor_lens), 1) if n else 0,
        "dup_options": dup_opt,
    }


def build_new_seed(seed: dict, patch: list) -> dict:
    """在内存里应用 patch，返回新的 seed dict + 变更明细。"""
    by_slug = {e["lesson_slug"]: e for e in seed["quizzes"]}
    changed = []
    for item in patch:
        slug, qi, dmap = item["l"], item["qi"], item["d"]
        entry = by_slug.get(slug)
        if entry is None:
            raise SystemExit(f"[FATAL] seed 里没有课 {slug}")
        q = entry["questions"][qi]
        ci = q["correct_index"]
        for idx_str, new_text in dmap.items():
            idx = int(idx_str)
            if idx == ci:
                raise SystemExit(f"[FATAL] {slug} Q{qi} 试图改动正确项 {idx}")
            if idx >= len(q["options"]):
                raise SystemExit(f"[FATAL] {slug} Q{qi} 下标越界 {idx}")
            changed.append((slug, qi, idx, q["options"][idx], new_text))
            q["options"][idx] = new_text
    return seed, changed


def main() -> int:
    apply = "--apply" in sys.argv
    for p in (DB, SEED, PATCH):
        if not p.exists():
            print(f"[FAIL] 缺文件: {p}")
            return 2

    patch = json.loads(PATCH.read_text(encoding="utf-8"))
    seed_old = json.loads(SEED.read_text(encoding="utf-8"))
    seed_new, changed = build_new_seed(seed_old, patch)
    print(f"mode = {'APPLY' if apply else 'DRY-RUN'}")
    print(f"patch 条目 = {len(patch)}，将改动的干扰项 = {len(changed)}")

    con = sqlite3.connect(DB)
    cur = con.cursor()
    slugs = load_db_lessons(cur)
    print(f"DB 中 L4 课数 = {len(slugs)}")

    # ---- 应用 DB 更新 ----
    updated_rows = 0
    for slug, qi, idx, old_text, new_text in changed:
        lid = slugs.get(slug)
        cur.execute(
            "SELECT id FROM quizzes WHERE lesson_id=? ORDER BY order_index", (lid,)
        )
        qids = [r[0] for r in cur.fetchall()]
        if qi >= len(qids):
            raise SystemExit(f"[FATAL] {slug} 第 {qi} 题在 DB 里不存在（共 {len(qids)} 题）")
        qid = qids[qi]
        cur.execute("SELECT options, correct_index FROM quizzes WHERE id=?", (qid,))
        opts, ci = cur.fetchone()
        opts = json.loads(opts)
        if idx == ci:
            raise SystemExit(f"[FATAL] qid={qid} 试图改动正确项 {idx}")
        opts[idx] = new_text
        cur.execute("UPDATE quizzes SET options=? WHERE id=?", (json.dumps(opts, ensure_ascii=False), qid))
        updated_rows += 1
    if apply:
        con.commit()
    else:
        con.rollback()
    print(f"DB 更新行数 = {updated_rows}" + ("" if apply else "（已回滚）"))

    # ---- 统计：前后对比 ----
    def all_q(seed):
        return [q for e in seed["quizzes"] if e["lesson_slug"].startswith(PREFIX) for q in e["questions"]]

    before = stats(all_q(seed_old))
    after = stats(all_q(seed_new))
    print("\n--- 修复前 ---")
    for k, v in before.items():
        print(f"  {k}: {v}")
    print("--- 修复后 ---")
    for k, v in after.items():
        print(f"  {k}: {v}")

    # ---- 答案位置分布 ----
    dist_after = Counter(q["correct_index"] for q in all_q(seed_new))
    dist_before = Counter(q["correct_index"] for q in all_q(seed_old))
    print(f"\n答案位置分布 前={dict(sorted(dist_before.items()))} 后={dict(sorted(dist_after.items()))}")

    # ---- 高风险残留 ----
    risky = []
    for e in seed_new["quizzes"]:
        if not e["lesson_slug"].startswith(PREFIX):
            continue
        for qi, q in enumerate(e["questions"]):
            L = [len(o) for o in q["options"]]
            if L[q["correct_index"]] - sorted(L, reverse=True)[1] >= 10:
                risky.append((e["lesson_slug"], qi, q["prompt"], L))
    print(f"\n残留「领先>=10字」高风险题 = {len(risky)}")
    for r in risky:
        print("  ", r[0], f"Q{r[1]}", r[2][:34], r[3])

    # ---- 写 seed ----
    if apply:
        b1 = backup(SEED)
        b2 = backup(DB)
        SEED.write_text(json.dumps(seed_new, ensure_ascii=False, indent=2), encoding="utf-8")
        con.close()
        print(f"\n备份: {b1.name}")
        print(f"备份: {b2.name}")
        print("[written] seed 已写入；DB 已 commit")
        return 0
    con.close()
    print("\n[dry-run] 未写入任何文件；加 --apply 生效")
    return 0


if __name__ == "__main__":
    sys.exit(main())
