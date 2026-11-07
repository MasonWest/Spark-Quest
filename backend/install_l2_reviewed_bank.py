"""Add the new bank without rewriting old questions or learning records.
Default: dry run. --apply creates an SQLite backup before inserting.
"""
import argparse
from contextlib import closing
from datetime import datetime
import hashlib
import json
import sqlite3
from app.database import DB_PATH, SessionLocal
from app.l2_question_bank import seed_reviewed_bank

TABLES = ['lesson_mastery', 'lesson_notes', 'study_days', 'user_stats', 'user_badges', 'quiz_answer_log']


def snapshot(db):
    return hashlib.sha256(repr([db.execute('SELECT * FROM '+t+' ORDER BY rowid').fetchall() for t in TABLES]).encode()).hexdigest()


def install(apply=False):
    with closing(sqlite3.connect(DB_PATH.as_uri()+'?mode=rw', uri=True)) as raw:
        before = snapshot(raw)
        old_rows = raw.execute('SELECT * FROM quizzes ORDER BY id').fetchall()
        backup = None
        if apply:
            backup = DB_PATH.with_name(DB_PATH.name+'.bak_reviewed_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
            with closing(sqlite3.connect(backup)) as dest:
                raw.backup(dest)
        with SessionLocal() as session:
            count = seed_reviewed_bank(session)
            if apply:
                session.commit()
            else:
                session.rollback()
        assert snapshot(raw) == before, 'Historical learning records changed'
        actual = {r[0]: r for r in raw.execute('SELECT * FROM quizzes ORDER BY id')}
        assert all(actual[r[0]] == r for r in old_rows), 'Existing question changed'
        return dict(inserted=count if apply else 0, pending=0 if apply else count, history_unchanged=True, existing_questions_unchanged=True, backup=str(backup) if backup else None)


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true')
    print(json.dumps(install(parser.parse_args().apply)))
