"""Append L3-L6 bank. Dry-run default, --apply backs up before insertion.
All pre-existing quiz rows and all non-quiz tables must remain unchanged.
"""
import argparse
from contextlib import closing
from datetime import datetime
import hashlib
import json
import sqlite3
from app.database import DB_PATH, SessionLocal
from app.reviewed_question_bank import seed_reviewed_bank


def snapshot(db):
    tables=[r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name!='quizzes' ORDER BY name")]
    return hashlib.sha256(repr([(t,db.execute(f'SELECT * FROM "{t}" ORDER BY rowid').fetchall()) for t in tables]).encode()).hexdigest()


def install(apply=False):
    with closing(sqlite3.connect(DB_PATH.as_uri()+'?mode=rw',uri=True)) as raw:
        before=snapshot(raw);old=raw.execute('SELECT * FROM quizzes ORDER BY id').fetchall()
        backup=None
        if apply:
            backup=DB_PATH.with_name(DB_PATH.name+'.bak_l3l6_bank_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
            with closing(sqlite3.connect(backup)) as target:raw.backup(target)
        with SessionLocal() as session:
            count=seed_reviewed_bank(session)
            if apply:session.commit()
            else:session.rollback()
        assert snapshot(raw)==before,'Historical data changed'
        actual={r[0]:r for r in raw.execute('SELECT * FROM quizzes')}
        assert all(actual[r[0]]==r for r in old),'Existing question changed'
        return dict(inserted=count if apply else 0,pending=0 if apply else count,history_unchanged=True,existing_questions_unchanged=True,backup=str(backup) if backup else None)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply',action='store_true')
    print(json.dumps(install(parser.parse_args().apply)))
