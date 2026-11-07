"""Fix the PySpark relationship question in DB and seed, preserving IDs.

Dry run by default. --apply creates backups and updates only this question.
The correct option stays at index 3 so historic answer indices stay meaningful.
"""
from contextlib import closing
import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
PROMPT = "关于 Spark 与 PySpark 的关系，正确的是？"
OPTIONS = [
    "PySpark 是独立于 Spark 的 Python 计算引擎",
    "PySpark 是把 pandas 自动转成分布式的工具",
    "PySpark 是只供本地调试使用的简化版 Spark",
    "PySpark 是通过 Python 使用 Spark 的官方接口",
]
EXPLANATION = "PySpark 是 Apache Spark 的官方 Python 接口，让你用 Python 调用 Spark 的能力。它不是另一套计算引擎，也不只用于本地调试；Spark 仍有相应的运行环境要求。"


def repair(base=BASE, apply=False):
    seed_path = base / "app" / "quiz_seed.json"
    db_path = base / "spark_quest.db"
    seed = json.loads(seed_path.read_text(encoding="utf-8"))
    matches = [q for group in seed["quizzes"] if group["lesson_slug"] == "l0-what-is-spark"
               for q in group["questions"] if q["prompt"] == PROMPT]
    if len(matches) != 1:
        raise RuntimeError("Expected exactly one seed question")
    # mode=rw prevents accidentally creating a new empty user database.
    with closing(sqlite3.connect(db_path.as_uri() + "?mode=rw", uri=True)) as db, db:
        rows = db.execute("SELECT q.id, q.options, q.correct_index, q.explanation FROM quizzes q JOIN lessons l ON l.id=q.lesson_id WHERE l.slug=? AND q.prompt=?", ("l0-what-is-spark", PROMPT)).fetchall()
        if len(rows) != 1 or rows[0][2] != 3 or matches[0]["correct_index"] != 3:
            raise RuntimeError("Question identity or answer position changed; inspect manually")
        qid, options, _, explanation = rows[0]
        target = matches[0]
        drift = json.loads(options) != OPTIONS or explanation != EXPLANATION or target["options"] != OPTIONS or target["explanation"] != EXPLANATION
        if not apply or not drift:
            return {"changed": False, "needs_repair": drift, "question_id": qid}
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup_path = base / f"spark_quest.db.bak_intro_{stamp}"
        with closing(sqlite3.connect(backup_path)) as backup:
            db.backup(backup)
        seed_path.with_name(seed_path.name + f".bak_intro_{stamp}").write_bytes(seed_path.read_bytes())
        target.update(options=OPTIONS, explanation=EXPLANATION)
        updated = json.dumps(seed, ensure_ascii=False, indent=2) + "\n"
        # Keep the original seed formatting: replace just the matched question.
        original = seed_path.read_text(encoding="utf-8")
        old_question = json.loads(original)
        old = next(q for g in old_question["quizzes"] if g["lesson_slug"] == "l0-what-is-spark" for q in g["questions"] if q["prompt"] == PROMPT)
        old_block = json.dumps(old, ensure_ascii=False, indent=2)
        new_block = json.dumps(target, ensure_ascii=False, indent=2)
        old_block = "\n".join("        " + line if i else line for i, line in enumerate(old_block.splitlines()))
        new_block = "\n".join("        " + line if i else line for i, line in enumerate(new_block.splitlines()))
        if original.count(old_block) == 1:
            updated = original.replace(old_block, new_block)
        db.execute("UPDATE quizzes SET options=?, explanation=? WHERE id=?", (json.dumps(OPTIONS, ensure_ascii=False), EXPLANATION, qid))
        try:
            seed_path.write_text(updated, encoding="utf-8")
            db.commit()
        except Exception:
            db.rollback()
            seed_path.write_text(original, encoding="utf-8")
            raise
        return {"changed": True, "needs_repair": False, "question_id": qid, "backup": str(backup_path)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    print(json.dumps(repair(apply=parser.parse_args().apply), ensure_ascii=True))
