"""L2/L3 干扰项重写应用脚本（2026-09-14）。

只替换每题的「非正确槽位」为长度相当的干扰项；正确项文本与 correct_index 保持不变。
用法： python rewrite_l2l3_distractors_20260914.py           # dry-run
       python rewrite_l2l3_distractors_20260914.py --apply    # 写库（先备份）
"""
import sqlite3, json, os, shutil, sys

DB = "spark_quest.db"
BACKUP = "spark_quest.db.bak_before_l2l3distractors_20260914"
FILES = {"2": "l2_distractors_20260914.json", "3": "l3_distractors_20260914.json"}
L2 = list(range(12, 22))   # Level 2: DataFrame 核心
L3 = list(range(22, 31))   # Level 3: Spark SQL


def main():
    apply = "--apply" in sys.argv
    DIST = {}
    for tag, fn in FILES.items():
        d = json.load(open(fn, encoding="utf-8"))["distractors"]
        for k, v in d.items():
            DIST[int(k)] = v
    print(f"loaded distractors: {len(DIST)} questions")

    if apply and not os.path.exists(BACKUP):
        shutil.copy(DB, BACKUP)
        print(f"backup -> {BACKUP}")

    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("select id,lesson_id,options,correct_index from quizzes where lesson_id in (%s)"
                % ",".join(map(str, L2 + L3)))
    rows = cur.fetchall()
    present = set(r[0] for r in rows)
    missing = [q for q in DIST if q not in present]
    if missing:
        print("WARN: distractor ids not found in DB:", missing)

    updates = []
    for qid, lid, opts, ci in rows:
        if qid not in DIST:
            continue
        o = json.loads(opts)
        correct = o[ci]
        d = DIST[qid]
        if len(d) != 3:
            print(f"WARN q{qid}: has {len(d)} distractors, skip"); continue
        new = list(o); di = 0
        for i in range(len(o)):
            if i == ci:
                continue
            new[i] = d[di]; di += 1
        assert new[ci] == correct, f"q{qid} correct text changed"
        assert len(set(x.strip() for x in new)) == len(new), f"q{qid} duplicate options: {new}"
        for x in new:
            assert "\ufffd" not in x, f"q{qid} has U+FFFD"
        updates.append((json.dumps(new, ensure_ascii=False), qid))

    print(f"questions to update: {len(updates)}")
    if apply:
        cur.executemany("update quizzes set options=? where id=?", updates)
        con.commit()
        print("APPLIED.")
    else:
        print("dry-run (use --apply to write)")
    con.close()


if __name__ == "__main__":
    main()
