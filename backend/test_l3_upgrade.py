"""Upgrade old DB + old/new seed, reject unknown drift, preserve all history."""
from contextlib import closing
import json
from pathlib import Path
import shutil
import sqlite3
from tempfile import TemporaryDirectory
import repair_l3_quizzes as migration

ROOT = Path(__file__).resolve().parent
fixes = json.loads((ROOT/'app/l3_quiz_fact_corrections.json').read_text(encoding='utf-8'))
with TemporaryDirectory(prefix='l3-upgrade-check-') as directory:
    for source_is_old in (True,False):
        target = Path(directory)/('old-seed' if source_is_old else 'new-seed')
        (target/'app').mkdir(parents=True)
        for name in ('quiz_seed.json','l3_quiz_fact_corrections.json'):
            shutil.copyfile(ROOT/'app'/name,target/'app'/name)
        with closing(sqlite3.connect((ROOT/'spark_quest.db').as_uri()+'?mode=ro',uri=True)) as source:
            with closing(sqlite3.connect(target/'spark_quest.db')) as destination:
                source.backup(destination)
        seed = json.loads((target/'app/quiz_seed.json').read_text(encoding='utf-8'))
        with closing(sqlite3.connect(target/'spark_quest.db')) as db:
            all_ids = {r[0] for r in db.execute('SELECT id FROM quizzes')}
            target_ids = []
            answer_positions = {}
            for fix in fixes:
                before = fix['before']
                row = db.execute('SELECT q.id,q.correct_index FROM quizzes q JOIN lessons l ON q.lesson_id=l.id WHERE l.slug=? AND q.prompt IN (?,?)',
                                 (fix['slug'],before['prompt'],fix.get('new_prompt',fix['prompt']))).fetchone()
                target_ids.append(row[0]);answer_positions[row[0]]=row[1]
                db.execute('UPDATE quizzes SET prompt=?,options=?,explanation=? WHERE id=?',
                           (before['prompt'],json.dumps(before['options'],ensure_ascii=False),before['explanation'],row[0]))
                if source_is_old:
                    q = next(q for g in seed['quizzes'] if g['lesson_slug']==fix['slug'] for q in g['questions'] if q['prompt'] in (before['prompt'],fix.get('new_prompt',fix['prompt'])))
                    q.update(before)
            db.commit()
            history_before = migration.history(db)
            unrelated = {r[0]:r for r in db.execute('SELECT * FROM quizzes') if r[0] not in target_ids}
        (target/'app/quiz_seed.json').write_text(json.dumps(seed,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        migration.BASE = target
        assert migration.repair()['pending']==34
        applied = migration.repair(True)
        assert applied['count']==34 and applied['history_unchanged'] and Path(applied['backup']).is_file()
        with closing(sqlite3.connect(target/'spark_quest.db')) as db:
            assert migration.history(db)==history_before
            assert {r[0] for r in db.execute('SELECT id FROM quizzes')}==all_ids
            assert {r[0]:r for r in db.execute('SELECT * FROM quizzes') if r[0] not in target_ids}==unrelated
            assert {r[0]:r[1] for r in db.execute('SELECT id,correct_index FROM quizzes') if r[0] in target_ids}==answer_positions
            for fix in fixes:
                row=db.execute('SELECT q.options,q.correct_index,q.explanation FROM quizzes q JOIN lessons l ON l.id=q.lesson_id WHERE l.slug=? AND q.prompt=?',
                               (fix['slug'],fix.get('new_prompt',fix['prompt']))).fetchone()
                assert row and json.loads(row[0])[row[1]]==fix['answer'] and row[2]==fix['explanation']
        assert migration.repair(True)['pending']==0
        with closing(sqlite3.connect(target/'spark_quest.db')) as db:
            db.execute('UPDATE quizzes SET explanation=? WHERE id=?',('unknown editorial drift',target_ids[0]));db.commit()
        seed_before=(target/'app/quiz_seed.json').read_bytes()
        try:
            migration.repair(True)
        except ValueError as error:
            assert 'drift' in str(error)
        else:
            raise AssertionError('Unknown drift was silently overwritten')
        assert (target/'app/quiz_seed.json').read_bytes()==seed_before
        print('PASS old DB +', 'old seed' if source_is_old else 'new seed', ': backed up upgrade, IDs/positions/history/unrelated rows, idempotence and drift rejection')
