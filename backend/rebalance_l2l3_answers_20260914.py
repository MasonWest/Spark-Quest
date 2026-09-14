"""L2/L3 答案位置重排（2026-09-14）——修复「偏 A / 偏 B」缺陷。

背景：L2 correct_index 分布 [63,13,12,12]（63% A），L3 [30,57,3,0]（57% B、D 从不出现）。

关于「冻结题」：quiz_answer_log 只做只写事实层，派生逻辑（weak_questions）只读
is_correct + question_id，从不回读 selected_index/correct_index（已核对源码）。
所以连同已作答题目一并重排，不会破坏任何派生/判分逻辑；本脚本不触碰日志。

做法：仅置换选项顺序并重算 correct_index，正确项文本零改动。
用法： python rebalance_l2l3_answers_20260914.py [--apply]
"""
import sqlite3, json, os, shutil, sys

DB = "spark_quest.db"
BACKUP = "spark_quest.db.bak_before_l2l3rebalance_20260914"


def main():
    apply = "--apply" in sys.argv
    if apply and not os.path.exists(BACKUP):
        shutil.copy(DB, BACKUP); print(f"backup -> {BACKUP}")

    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("select id,title from course_levels order by order_index")
    levels = cur.fetchall()
    updates = []
    for lvl_idx, (lid, ltitle) in enumerate(levels):
        if not ltitle.startswith("Level 2") and not ltitle.startswith("Level 3"):
            continue
        cur.execute("select id from lessons where level_id=? order by order_index", (lid,))
        lesson_ids = [r[0] for r in cur.fetchall()]
        from collections import Counter
        before = Counter()
        n = 0
        for lesson_ord, lesson_id in enumerate(lesson_ids):
            cur.execute("select id,options,correct_index from quizzes where lesson_id=? order by order_index", (lesson_id,))
            qs = cur.fetchall()
            for j, (qid, opts, ci) in enumerate(qs):
                o = json.loads(opts)
                correct = o[ci]
                before[ci] += 1
                target = (lesson_ord + j) % 4   # 每课轮转，避免同一课答案扎堆
                others = [o[k] for k in range(len(o)) if k != ci]
                new = [None] * len(o)
                new[target] = correct
                k = 0
                for p in range(len(o)):
                    if p == target:
                        continue
                    new[p] = others[k]; k += 1
                assert new[target] == correct
                assert len(set(x.strip() for x in new)) == len(new), f"q{qid} dup"
                for x in new:
                    assert "\ufffd" not in x
                updates.append((json.dumps(new, ensure_ascii=False), target, qid))
                n += 1
        # 统计本 level 的目标分布
        tgt = Counter(t for _, t, _ in updates[-n:])
        print(f"{ltitle}: n={n} before[A,B,C,D]={[before.get(i,0) for i in (0,1,2,3)]} "
              f"-> target[A,B,C,D]={[tgt.get(i,0) for i in (0,1,2,3)]}")

    print(f"total updates: {len(updates)}")
    if apply:
        cur.executemany("update quizzes set options=?, correct_index=? where id=?", updates)
        con.commit()
        print("APPLIED.")
    else:
        print("dry-run (use --apply)")
    con.close()


if __name__ == "__main__":
    main()
