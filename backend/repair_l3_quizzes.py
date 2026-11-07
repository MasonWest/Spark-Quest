"""Explicit L3 upgrade, dry-run by default. Accept only known old/new content.
Supports an old DB after pulling the corrected seed. Preserve IDs, answer
positions and all history; refuse unrelated drift rather than overwriting it.
"""
import argparse
from contextlib import closing
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sqlite3

BASE = Path(__file__).resolve().parent
FIELDS = ('prompt', 'options', 'correct_index', 'explanation')


def history(db):
    names = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name!='quizzes' ORDER BY name")]
    return hashlib.sha256(repr([(name, [tuple(row) for row in db.execute(f'SELECT * FROM "{name}" ORDER BY rowid').fetchall()]) for name in names]).encode()).hexdigest()


def repair(apply=False):
    path = BASE / 'app/quiz_seed.json'
    original = path.read_bytes()
    seed = json.loads(original)
    fixes = json.loads((BASE / 'app/l3_quiz_fact_corrections.json').read_text(encoding='utf-8'))
    with closing(sqlite3.connect((BASE / 'spark_quest.db').as_uri() + '?mode=rw', uri=True)) as db:
        db.row_factory = sqlite3.Row
        # Lock before checking DB states so a writer cannot race the migration.
        db.execute('BEGIN IMMEDIATE' if apply else 'BEGIN')
        changes = []
        try:
            for fix in fixes:
                before = fix['before']
                after = dict(prompt=fix.get('new_prompt',fix['prompt']),
                             options=list(fix.get('options',before['options'])),
                             correct_index=fix['correct_index'],explanation=fix['explanation'])
                after['options'][after['correct_index']] = fix['answer']
                assert before['correct_index'] == after['correct_index']
                assert len(after['options']) == len(set(after['options'])) == len(before['options'])
                matches = [q for g in seed['quizzes'] if g['lesson_slug']==fix['slug'] for q in g['questions'] if q['prompt'] in (before['prompt'],after['prompt'])]
                rows = db.execute('SELECT q.id,q.prompt,q.options,q.correct_index,q.explanation FROM quizzes q JOIN lessons l ON l.id=q.lesson_id WHERE l.slug=? AND q.prompt IN (?,?)',
                                  (fix['slug'],before['prompt'],after['prompt'])).fetchall()
                if len(matches)!=1 or len(rows)!=1:
                    raise ValueError('Missing/ambiguous target: '+fix['prompt'])
                question, row = matches[0], rows[0]
                source_state = {k:question[k] for k in FIELDS}
                db_state = {k:row[k] for k in FIELDS}
                db_state['options'] = json.loads(db_state['options'])
                if source_state not in (before,after) or db_state not in (before,after):
                    raise ValueError('Unknown content drift; inspect before migration: '+fix['prompt'])
                if source_state == after and db_state == after:
                    continue
                question.update(after)
                changes.append((after['prompt'],json.dumps(after['options'],ensure_ascii=False),after['explanation'],row['id']))
            if not apply or not changes:
                db.rollback()
                return dict(pending=len(changes),applied=False)
            stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            backup = BASE / f'spark_quest.db.bak_l3_{stamp}'
            # Backup from a separate read connection: the write transaction is
            # locked but has not changed rows yet. Copy the committed state.
            with closing(sqlite3.connect((BASE/'spark_quest.db').as_uri()+'?mode=ro',uri=True)) as source:
                with closing(sqlite3.connect(backup)) as destination:
                    source.backup(destination)
            path.with_name(path.name+f'.bak_l3_{stamp}').write_bytes(original)
            before_history = history(db)
            db.executemany('UPDATE quizzes SET prompt=?,options=?,explanation=? WHERE id=?',changes)
            assert history(db) == before_history, 'Non-question data changed'
            path.write_text(json.dumps(seed,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            db.commit()
            return dict(pending=0,applied=True,count=len(changes),history_unchanged=True,backup=str(backup))
        except Exception:
            db.rollback()
            if path.read_bytes()!=original:
                path.write_bytes(original)
            raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true')
    print(json.dumps(repair(parser.parse_args().apply)))
