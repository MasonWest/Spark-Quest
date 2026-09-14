"""把 quiz options + correct_index 从 DB 回写 app/quiz_seed.json（全 Level，2026-09-14）。

按 lesson_slug + 归一化 prompt 匹配。幂等。用法： python sync_quiz_seed_all_20260914.py [--apply]

背景：App 的 _seed_quizzes() 只读 app/quiz_seed.json。此前 L5 修复只回写了
seed_level5.py、漏了 quiz_seed.json → 清库重跑 seed 会复活 L5 旧缺陷。本次一并修正。
"""
import sqlite3, json, re, os, shutil, sys

DB = "spark_quest.db"
SEED = "app/quiz_seed.json"
BACKUP = "app/quiz_seed.json.bak_before_syncall_20260914"


def norm(s):
    return re.sub(r"\s+", "", s).replace("“", '"').replace("”", '"')


def main():
    apply = "--apply" in sys.argv
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("select id,slug from lessons")
    lessons = {slug: lid for lid, slug in cur.fetchall()}

    dbmap = {}
    for slug, lid in lessons.items():
        cur.execute("select prompt,options,correct_index from quizzes where lesson_id=?", (lid,))
        dbmap[slug] = {norm(p): (json.loads(o), ci) for p, o, ci in cur.fetchall()}

    data = json.load(open(SEED, encoding="utf-8"))
    matched = updated = missing = 0
    per_level = {}
    cur.execute("select l.slug, c.title from lessons l join course_levels c on l.level_id=c.id")
    lvl_of = {slug: title.split("：")[0] for slug, title in cur.fetchall()}
    for entry in data["quizzes"]:
        slug = entry["lesson_slug"]
        m = dbmap.get(slug)
        if m is None:
            continue
        for q in entry["questions"]:
            key = norm(q["prompt"])
            if key not in m:
                missing += 1; print(f"  MISSING: {slug} :: {q['prompt'][:40]}"); continue
            opts, ci = m[key]
            matched += 1
            if [norm(x) for x in q["options"]] != [norm(x) for x in opts] or q["correct_index"] != ci:
                q["options"] = opts; q["correct_index"] = ci
                updated += 1
                per_level[lvl_of.get(slug, "?")] = per_level.get(lvl_of.get(slug, "?"), 0) + 1

    print(f"matched={matched} updated={updated} missing={missing}")
    print("updated per level:", per_level)
    if apply:
        if not os.path.exists(BACKUP):
            shutil.copy(SEED, BACKUP); print(f"backup -> {BACKUP}")
        json.dump(data, open(SEED, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("seed written")
    else:
        print("dry-run (use --apply)")
    con.close()


if __name__ == "__main__":
    main()
