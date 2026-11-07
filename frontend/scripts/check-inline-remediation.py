"""UI-only remediation checks; lesson fixtures read from DB without writing grades."""
from pathlib import Path
from contextlib import closing
import json, sqlite3
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[2]
with closing(sqlite3.connect((root / 'backend/spark_quest.db').as_uri() + '?mode=ro', uri=True)) as db:
    db.row_factory = sqlite3.Row
    lessons = {r['slug']: dict(r) for r in db.execute('SELECT * FROM lessons')}
for row in lessons.values():
    row['content'] = json.loads(row['content'])
    row.update(status='available', mastery_score=None, level_title='L2', next_lesson=None)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 390, 'height': 844})
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.route('**/api/lessons/**', lambda r: r.fulfill(json=[] if r.request.url.endswith('/notes') else next(d for d in lessons.values() if d['id'] == int(r.request.url.rsplit('/', 1)[1]))))
    count = 0
    for file in sorted((root / 'frontend/src/content/lessons').glob('*.json')):
        lesson = json.loads(file.read_text(encoding='utf-8'))
        for index, task in enumerate(lesson['tasks']):
            remedy = task.get('remediation')
            if not remedy:
                continue
            page.goto(f"http://127.0.0.1:4173/lesson/{lessons[lesson['slug']]['id']}")
            page.locator('.dfj-root').wait_for()
            key = f"spark-quest:learning:{lesson['slug']}:v{lesson['version']}"
            initial = dict(version=lesson['version'], runId='qa', cursorId=task['id'], completedIds=[t['id'] for t in lesson['tasks'][:index]], migratedIds=[], attempts=[])
            page.evaluate('([k,v])=>localStorage.setItem(k,JSON.stringify(v))', [key, initial])
            page.reload()
            def choose(correct):
                for i, field in enumerate(task['fields']):
                    option = next(o for o in field['options'] if (o['id'] == field['correctOptionId']) == correct)
                    if len(task['fields']) == 1:
                        page.get_by_role('radio').nth(field['options'].index(option)).check()
                    else:
                        page.locator('.lj-field select').nth(i).select_option(option['id'])
            choose(False)
            page.get_by_role('button', name='检查判断').click()
            page.get_by_role('button', name='先重试原题').click()
            page.get_by_role('button', name='检查判断').click()
            page.get_by_role('button', name='换一道小题验证 →').click()
            panel = page.locator('.lj-remediation')
            for width in [320, 390, 768, 1440]:
                page.set_viewport_size({'width': width, 'height': 844})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (remedy['id'], width)
            page.set_viewport_size({'width': 390, 'height': 844})
            field = remedy['field']
            wrong = next(i for i, o in enumerate(field['options']) if o['id'] != field['correctOptionId'])
            right = next(i for i, o in enumerate(field['options']) if o['id'] == field['correctOptionId'])
            panel.get_by_role('radio').nth(wrong).check()
            panel.get_by_role('button', name='检查变式').click()
            panel.get_by_role('button', name='再想一次').click()
            panel.get_by_role('radio').nth(right).check()
            panel.get_by_role('button', name='检查变式').click()
            state = page.evaluate('(k)=>JSON.parse(localStorage.getItem(k))', key)
            assert state['cursorId'] == task['id'] and state['completedIds'] == initial['completedIds']
            assert len(state['attempts']) == 4 and sum(a.get('activity') == 'remediation' for a in state['attempts']) == 2
            assert state['attempts'][-1]['knowledgeId'] == remedy['knowledgeId'] and state['attempts'][-1]['correct']
            if count == 0:
                out = root.parent / 'ux_audit/learning-repair'
                out.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(out / 'l2-inline-remediation-390.png'), full_page=True)
                page.reload()
                assert page.locator('.lj-remediation').count() == 0
                assert page.evaluate('(k)=>JSON.parse(localStorage.getItem(k)).attempts.length', key) == 4
            else:
                panel.get_by_role('button', name='回原题再判断 →').click()
            assert page.get_by_role('button', name='检查判断').is_disabled()
            choose(True)
            page.get_by_role('button', name='检查判断').click()
            page.get_by_role('button', name='看看我的收获' if index == len(lesson['tasks']) - 1 else '继续下一步 →').click()
            state = page.evaluate('(k)=>JSON.parse(localStorage.getItem(k))', key)
            assert task['id'] in state['completedIds'] and len(state['completedIds']) == index + 1
            print('PASS', remedy['id'], 'wrong/retry/transfer/return, separate records, responsive')
            count += 1
    assert count == 5 and not errors, (count, errors)
    browser.close()
