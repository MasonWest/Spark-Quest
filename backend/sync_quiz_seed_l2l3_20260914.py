"""把 L2/L3 的 quiz options + correct_index 从 DB 回写 app/quiz_seed.json（2026-09-14）。

按 lesson_slug + 归一化 prompt 匹配。用法： python sync_quiz_seed_l2l3_20260914.py [--apply]
"""
import sqlite3, json, re, os, shutil, sys

DB = "spark_quest.db"
SEED = "app/quiz_seed.json"
BACKUP = "app/quiz_seed.json.bak_before_l2l3sync_20260914"


def norm(s):
    return re.sub(r"\s+", "", s).replace("“", '"').replace("”", '"')


def main():
    apply = "--apply" in sys.argv
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("select id,slug from lessons where level_id in "
                "(select id from course_levels where title like 'Level 2%' or title like 'Level 3%')")
    lessons = {slug: lid for lid, slug in cur.fetchall()}

    dbmap = {}  # slug -> {norm_prompt: (options, correct_index)}
    for slug, lid in lessons.items():
        cur.execute("select prompt,options,correct_index from quizzes where lesson_id=?", (lid,))
        dbmap[slug] = {norm(p): (json.loads(o), ci) for p, o, ci in cur.fetchall()}

    data = json.load(open(SEED, encoding="utf-8"))
    matched = mismatch_before = updated = missing = 0
    for entry in data["quizzes"]:
        slug = entry["lesson_slug"]
        if slug not in dbmap:
            continue
        m = dbmap[slug]
        for q in entry["questions"]:
            key = norm(q["prompt"])
            if key not in m:
                missing += 1
                print(f"  MISSING in DB: {slug} :: {q['prompt'][:40]}")
                continue
            opts, ci = m[key]
            matched += 1
            if [norm(x) for x in q["options"]] != [norm(x) for x in opts] or q["correct_index"] != ci:
                mismatch_before += 1
                q["options"] = opts
                q["correct_index"] = ci
                updated += 1

    print(f"L2/L3 seed questions matched={matched} mismatched_before={mismatch_before} updated={updated} missing={missing}")
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
