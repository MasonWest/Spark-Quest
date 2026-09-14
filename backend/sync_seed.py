# -*- coding: utf-8 -*-
"""真库 → 播种文件 的同步与漂移检查（course_seed.json + quiz_seed.json）。

为什么需要它
    App 运行时只读这两个 JSON：`database._seed_quizzes()` 读 quiz_seed.json，
    `init_db` 在 lessons 缺 content 时从 course_seed.json backfill。
    所以「只改 DB、不改 seed」= 清库重建后修复全部丢失。
    历史事故：L5 题库修复只回写了 seed_level5.py、漏了 quiz_seed.json，
    差点让「全 A + 正确项恒最长」在重建后复活。

用法
    cd backend
    python sync_seed.py            # dry-run：只报告漂移，不写任何文件
    python sync_seed.py --apply    # 写入（先自动备份 *.bak_before_sync_<时间戳>）

退出码
    0  无漂移，或 --apply 已写完
    1  dry-run 检测到漂移
    2  环境错误（DB / seed 文件缺失）

匹配规则
    course_seed：按 lesson.slug 对齐
    quiz_seed  ：按 lesson_slug + 归一化 prompt（去空白 + 统一引号）对齐
同步字段
    lesson：objective / description / content（七键）
    quiz  ：options / correct_index / explanation
    ⚠️ explanation 早期不在同步范围，导致「只改 DB 解析」在冷库重建后丢失；
       2026-09-14 补齐。首次运行会暴露历史上仅改过 DB 的解析差异。
    只更新「有差异」的条目；orphan（seed 有 DB 无）与 db_only（DB 有 seed 无）只报告、不自动删改。
"""

import json
import re
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB = BASE / "spark_quest.db"
COURSE = BASE / "app" / "course_seed.json"
QUIZ = BASE / "app" / "quiz_seed.json"


def norm(s: str) -> str:
    """归一化 prompt 用于匹配：去掉所有空白 + 统一中文引号。"""
    return re.sub(r"\s+", "", s).replace("“", '"').replace("”", '"')


def backup(path: Path) -> None:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = path.with_name(path.name + f".bak_before_sync_{ts}")
    shutil.copy(path, dst)
    print(f"  backup -> {dst.name}")


def sync_course(cur, apply: bool):
    cur.execute("SELECT slug, objective, description, content FROM lessons")
    db = {slug: (ob, de, json.loads(raw)) for slug, ob, de, raw in cur.fetchall()}
    seed = json.loads(COURSE.read_text(encoding="utf-8"))
    hit = drift = orphan = 0
    for level in seed["levels"]:
        for lesson in level["lessons"]:
            slug = lesson.get("slug")
            if slug not in db:
                orphan += 1
                continue
            hit += 1
            ob, de, content = db[slug]
            if (
                lesson.get("content") != content
                or (ob is not None and lesson.get("objective") != ob)
                or (de is not None and lesson.get("description") != de)
            ):
                drift += 1
                lesson["content"] = content
                if ob is not None:
                    lesson["objective"] = ob
                if de is not None:
                    lesson["description"] = de
    print(f"[course_seed] lessons hit={hit} drift={drift} orphan={orphan}")
    if apply and drift:
        backup(COURSE)
        COURSE.write_text(json.dumps(seed, ensure_ascii=False, indent=2), encoding="utf-8")
        print("  written")
    return hit, drift, orphan


def sync_quiz(cur, apply: bool):
    cur.execute("SELECT id, slug FROM lessons")
    db = {}
    for lid, slug in cur.fetchall():
        cur.execute(
            "SELECT prompt, options, correct_index, explanation FROM quizzes WHERE lesson_id=?",
            (lid,),
        )
        db[slug] = {norm(p): (json.loads(o), ci, ex) for p, o, ci, ex in cur.fetchall()}
    seed = json.loads(QUIZ.read_text(encoding="utf-8"))
    matched = drift = orphan = new = 0
    for entry in seed["quizzes"]:
        m = db.get(entry["lesson_slug"])
        if m is None:
            continue
        seen = set()
        for q in entry["questions"]:
            key = norm(q["prompt"])
            seen.add(key)
            if key not in m:
                orphan += 1
                continue
            matched += 1
            opts, ci, ex = m[key]
            if (
                [norm(x) for x in q["options"]] != [norm(x) for x in opts]
                or q["correct_index"] != ci
                or q.get("explanation") != ex
            ):
                drift += 1
                q["options"] = opts
                q["correct_index"] = ci
                q["explanation"] = ex
        new += len(set(m) - seen)
    print(f"[quiz_seed]   questions matched={matched} drift={drift} orphan={orphan} db_only={new}")
    if apply and drift:
        backup(QUIZ)
        QUIZ.write_text(json.dumps(seed, ensure_ascii=False, indent=2), encoding="utf-8")
        print("  written")
    return matched, drift, orphan, new


def main() -> int:
    apply = "--apply" in sys.argv
    for p in (DB, COURSE, QUIZ):
        if not p.exists():
            print(f"[FAIL] not found: {p}")
            return 2
    print(f"mode = {'APPLY' if apply else 'DRY-RUN'}")

    con = sqlite3.connect(DB)
    cur = con.cursor()
    _, c_drift, c_orphan = sync_course(cur, apply)
    _, q_drift, q_orphan, q_new = sync_quiz(cur, apply)
    con.close()

    total = c_drift + q_drift
    extra = []
    if c_orphan or q_orphan:
        extra.append(f"orphan={c_orphan + q_orphan}")
    if q_new:
        extra.append(f"db_only={q_new}")
    print("drift total = %d%s" % (total, ("  (" + ", ".join(extra) + ")") if extra else ""))

    if apply:
        print("[written]" if total else "[nothing to write]")
        return 0
    print("[dry-run] no files touched; add --apply to write")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
