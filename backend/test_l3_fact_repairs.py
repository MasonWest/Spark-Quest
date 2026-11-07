"""Exercise the existing backed-up repair mechanism on an isolated DB copy.
Checks all unrelated questions, answer positions and all non-quiz tables.
"""
from contextlib import closing
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
from tempfile import TemporaryDirectory
import repair_l2_quizzes as repairer

ROOT = Path(__file__).resolve().parent
def snapshot(db):
    tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    return {table: hashlib.sha256(repr(db.execute(f'SELECT * FROM "{table}" ORDER BY rowid').fetchall()).encode()).hexdigest()
            for table in tables if table != 'quizzes'}

with TemporaryDirectory(prefix='spark-l3-repair-test-') as temp:
    target = Path(temp)
    (target / 'app').mkdir()
    for name in ('quiz_seed.json', 'l3_quiz_fact_corrections.json'):
        shutil.copyfile(ROOT / 'app' / name, target / 'app' / name)
    with closing(sqlite3.connect((ROOT / 'spark_quest.db').as_uri() + '?mode=ro', uri=True)) as source:
        with closing(sqlite3.connect(target / 'spark_quest.db')) as dest:
            source.backup(dest)
    repairer.BASE = target
    with closing(sqlite3.connect(target / 'spark_quest.db')) as db:
        before = snapshot(db)
        questions = {r[0]: r for r in db.execute('SELECT * FROM quizzes')}
        columns = [r[1] for r in db.execute('PRAGMA table_info(quizzes)')]
    preview = repairer.repair(False, 'app/l3_quiz_fact_corrections.json')
    applied = repairer.repair(True, 'app/l3_quiz_fact_corrections.json')
    with closing(sqlite3.connect(target / 'spark_quest.db')) as db:
        assert snapshot(db) == before
        after = {r[0]: r for r in db.execute('SELECT * FROM quizzes')}
        assert set(after) == set(questions)
        changed = [qid for qid in after if after[qid] != questions[qid]]
        assert len(changed) == preview['pending']
        assert len(changed) in (0, 34)
        for qid in changed:
            assert questions[qid][columns.index('correct_index')] == after[qid][columns.index('correct_index')]
            assert questions[qid][columns.index('lesson_id')] == after[qid][columns.index('lesson_id')]
            options = json.loads(after[qid][columns.index('options')])
            assert len(options) == len(set(options)) == 4
        fixes = json.loads((target / 'app/l3_quiz_fact_corrections.json').read_text(encoding='utf-8'))
        for fix in fixes:
            row = db.execute('SELECT q.prompt,q.options,q.correct_index,q.explanation FROM quizzes q JOIN lessons l ON q.lesson_id=l.id WHERE l.slug=? AND q.prompt=?',
                             (fix['slug'],fix.get('new_prompt',fix['prompt']))).fetchone()
            assert row and row[2] == fix['correct_index']
            assert json.loads(row[1])[row[2]] == fix['answer'] and row[3] == fix['explanation']
    if changed:
        assert Path(applied['backup']).is_file() and applied['history_unchanged']
    assert repairer.repair(True, 'app/l3_quiz_fact_corrections.json')['pending'] == 0
    print('PASS L3 repairs: preview/apply/idempotence, 34 targets verified, stable IDs/answer positions, unrelated questions and non-quiz tables unchanged')
