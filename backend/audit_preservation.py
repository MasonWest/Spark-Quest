"""Compare a backed-up DB against the current DB, using read-only connections."""
import argparse
from contextlib import closing
import json
from pathlib import Path
import sqlite3
from app.database import DB_PATH


def audit(before, current=DB_PATH):
    with closing(sqlite3.connect(Path(before).resolve().as_uri()+'?mode=ro',uri=True)) as old, closing(sqlite3.connect(Path(current).resolve().as_uri()+'?mode=ro',uri=True)) as new:
        tables=[r[0] for r in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        preserved=[]
        for table in tables:
            if table=='quizzes':continue
            assert old.execute(f'SELECT * FROM "{table}" ORDER BY rowid').fetchall()==new.execute(f'SELECT * FROM "{table}" ORDER BY rowid').fetchall(),f'Changed table: {table}'
            preserved.append(table)
        old_questions=old.execute('SELECT * FROM quizzes ORDER BY id').fetchall()
        current_questions={r[0]:r for r in new.execute('SELECT * FROM quizzes')}
        assert all(current_questions.get(row[0])==row for row in old_questions),'Old question changed or deleted'
        return dict(original_questions_unchanged=len(old_questions),current_questions=len(current_questions),added=len(current_questions)-len(old_questions),unchanged_tables=preserved)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('backup')
    print(json.dumps(audit(parser.parse_args().backup),ensure_ascii=False))
