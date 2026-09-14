"""L2/L3 干扰项第二轮补丁应用（2026-09-14）。
用法： python patch_l2l3_distractors_20260914.py [--apply]
"""
import sqlite3, json, os, shutil, sys

DB = "spark_quest.db"
BACKUP = "spark_quest.db.bak_before_l2l3patch_20260914"
PATCH = "l2l3_distractors_patch_20260914.json"


def main():
    apply = "--apply" in sys.argv
    DIST = {int(k): v for k, v in json.load(open(PATCH, encoding="utf-8"))["distractors"].items()}
    print(f"loaded patch: {len(DIST)} questions")
    if apply and not os.path.exists(BACKUP):
        shutil.copy(DB, BACKUP); print(f"backup -> {BACKUP}")

    con = sqlite3.connect(DB); cur = con.cursor()
    updates = []
    for qid, d in DIST.items():
        cur.execute("select options,correct_index from quizzes where id=?", (qid,))
        r = cur.fetchone()
        if not r:
            print(f"WARN q{qid} not found"); continue
        o = json.loads(r[0]); ci = r[1]; correct = o[ci]
        if len(d) != 3:
            print(f"WARN q{qid} needs 3, got {len(d)}"); continue
        new = list(o); di = 0
        for i in range(len(o)):
            if i == ci:
                continue
            new[i] = d[di]; di += 1
        assert new[ci] == correct, f"q{qid} correct changed"
        assert len(set(x.strip() for x in new)) == len(new), f"q{qid} dup: {new}"
        for x in new:
            assert "\ufffd" not in x, f"q{qid} fffd"
        updates.append((json.dumps(new, ensure_ascii=False), qid))
    print(f"to update: {len(updates)}")
    if apply:
        cur.executemany("update quizzes set options=? where id=?", updates); con.commit(); print("APPLIED.")
    else:
        print("dry-run")
    con.close()


if __name__ == "__main__":
    main()
