"""Targeted L2 fact corrections. Dry-run by default; --apply backs up DB/seed.

Preserves question IDs, option positions and historical records; optional prompt corrections are explicit.
"""
import argparse
from contextlib import closing
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sqlite3

BASE = Path(__file__).resolve().parent


def repair(apply=False, corrections_file="app/l2_quiz_corrections.json"):
    path = BASE / "app/quiz_seed.json"
    original = path.read_bytes()
    seed = json.loads(original)
    corrections = json.loads((BASE / corrections_file).read_text(encoding="utf-8"))
    changes = []
    with closing(sqlite3.connect((BASE / "spark_quest.db").as_uri() + "?mode=rw", uri=True)) as db:
        for fix in corrections:
            new_prompt = fix.get("new_prompt", fix["prompt"])
            matches = [q for g in seed["quizzes"] if g["lesson_slug"] == fix["slug"] for q in g["questions"] if q["prompt"] in (fix["prompt"], new_prompt)]
            rows = db.execute("SELECT q.id,q.options,q.correct_index,q.explanation FROM quizzes q JOIN lessons l ON l.id=q.lesson_id WHERE l.slug=? AND q.prompt IN (?,?)", (fix["slug"], fix["prompt"], new_prompt)).fetchall()
            if len(matches) != 1 or len(rows) != 1:
                raise RuntimeError("Missing or ambiguous question: " + fix["prompt"])
            question = matches[0]
            qid, raw, correct, explanation = rows[0]
            options = json.loads(raw)
            if correct != fix["correct_index"] or correct != question["correct_index"] or options != question["options"] or explanation != question["explanation"]:
                raise RuntimeError("DB/seed drift; inspect before repair: " + fix["prompt"])
            desired_options = list(fix.get("options", options))
            if len(desired_options) != len(options) or len(set(desired_options)) != len(desired_options):
                raise RuntimeError("Invalid replacement options")
            desired_options[correct] = fix["answer"]
            if options == desired_options and explanation == fix["explanation"] and question["prompt"] == new_prompt:
                continue
            options = desired_options
            question.update(options=options, explanation=fix["explanation"], prompt=new_prompt)
            changes.append((json.dumps(options, ensure_ascii=False), fix["explanation"], new_prompt, qid))
        if not apply or not changes:
            return {"pending": len(changes), "applied": False}
        tables = ["lesson_mastery", "lesson_notes", "study_days", "user_stats", "user_badges", "quiz_answer_log"]
        def history():
            return hashlib.sha256(repr([db.execute("SELECT * FROM " + t + " ORDER BY rowid").fetchall() for t in tables]).encode()).hexdigest()
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup = BASE / f"spark_quest.db.bak_l2_{stamp}"
        with closing(sqlite3.connect(backup)) as dest:
            db.backup(dest)
        path.with_name(path.name + f".bak_l2_{stamp}").write_bytes(original)
        db.execute("BEGIN IMMEDIATE")
        before = history()
        try:
            db.executemany("UPDATE quizzes SET options=?, explanation=?, prompt=? WHERE id=?", changes)
            assert history() == before, "Historical data changed"
            path.write_text(json.dumps(seed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            db.commit()
        except Exception:
            db.rollback()
            path.write_bytes(original)
            raise
        return {"pending": 0, "applied": True, "count": len(changes), "history_unchanged": True, "backup": str(backup)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--corrections", default="app/l2_quiz_corrections.json")
    args = parser.parse_args()
    print(json.dumps(repair(args.apply, args.corrections)))
