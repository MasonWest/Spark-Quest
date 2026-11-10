"""L0 remedy, delayed-check and downloadable-file browser integration.

Only mocked GET APIs and isolated browser storage; no learner writes.
"""
from contextlib import closing
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
ORIGIN='http://127.0.0.1:4173'
lessons={p.stem:json.loads(p.read_text(encoding='utf-8')) for p in (ROOT/'frontend/src/content/lessons').glob('l0-*.json')}
bank=json.loads((ROOT/'frontend/src/content/delayedChecks.json').read_text(encoding='utf-8'))['items']
with closing(sqlite3.connect((ROOT/'backend/spark_quest.db').as_uri()+'?mode=ro',uri=True)) as db:
    db.row_factory=sqlite3.Row
    details={r['slug']:dict(r) for r in db.execute("SELECT * FROM lessons WHERE slug LIKE 'l0-%'")}
for detail in details.values():
    detail['content']=json.loads(detail['content'])
    detail.update(status='available',mastery_score=None,level_title='Level 0',next_lesson=None)


with sync_playwright() as p:
    browser=p.chromium.launch()
    page=browser.new_page(viewport=dict(width=390,height=844))
    errors=[];writes=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    def api(route):
        if route.request.method!='GET':
            writes.append(route.request.url);return route.abort()
        if route.request.url.endswith('/notes'):return route.fulfill(json=[])
        ident=int(route.request.url.rsplit('/',1)[-1])
        return route.fulfill(json=next(l for l in details.values() if l['id']==ident))
    page.route('**/api/**',api)

    def state(key):
        return page.evaluate('key => JSON.parse(localStorage.getItem(key))',key)

    def fill(task,correct):
        if task['fields'][0].get('input'):
            for i,field in enumerate(task['fields']):
                page.locator('.lj-field input').nth(i).fill(field['input']['acceptedAnswers'][0] if correct else '999')
        else:
            field=task['fields'][0]
            index=next(i for i,o in enumerate(field['options']) if (o['id']==field['correctOptionId'])==correct)
            page.get_by_role('radio').nth(index).check()

    for slug,lesson in lessons.items():
        task=next(t for t in lesson['tasks'] if t.get('remediation'))
        index=lesson['tasks'].index(task)
        key=f"spark-quest:learning:{slug}:v{lesson['version']}"
        url=f"{ORIGIN}/lesson/{details[slug]['id']}"
        page.goto(url);page.locator('.lj-mission').wait_for()
        initial=dict(version=lesson['version'],runId='l0-browser',cursorId=task['id'],
                     completedIds=[t['id'] for t in lesson['tasks'][:index]],migratedIds=[],attempts=[])
        page.evaluate('([key,p])=>localStorage.setItem(key,JSON.stringify(p))',[key,initial])
        page.reload();page.get_by_role('heading',name=task['title'],exact=True).wait_for()
        fill(task,False);page.get_by_role('button',name='检查判断').click()
        page.get_by_role('button',name='换一道小题验证 →').click()
        remedy=task['remediation'];field=remedy['field']
        wrong=next(i for i,o in enumerate(field['options']) if o['id']!=field['correctOptionId'])
        right=next(i for i,o in enumerate(field['options']) if o['id']==field['correctOptionId'])
        page.get_by_role('radio').nth(wrong).check();page.get_by_role('button',name='检查变式').click()
        assert task['id'] not in state(key)['completedIds']
        page.get_by_role('button',name='再想一次').click()
        page.get_by_role('radio').nth(right).check();page.get_by_role('button',name='检查变式').click()
        assert task['id'] not in state(key)['completedIds']
        page.get_by_role('button',name='回原题再判断 →').click()
        fill(task,True);page.get_by_role('button',name='检查判断').click()
        page.get_by_role('button',name='继续下一步 →' if index<len(lesson['tasks'])-1 else '看看我的收获').click()
        progress=state(key)
        assert task['id'] in progress['completedIds']
        assert len([a for a in progress['attempts'] if a.get('activity')=='remediation'])==2
        print('PASS',slug,'wrong original -> wrong remedy -> right remedy -> right original')

    page.goto(ORIGIN+'/delayed-check')
    page.get_by_role('heading',name='暂时没有到期的验证').wait_for()
    assert 'L0–L7' in page.locator('main').inner_text()
    # Advance fixture evidence, not the browser's clock or any real learner data.
    old=(datetime.now(timezone.utc)-timedelta(hours=25)).isoformat()
    page.evaluate('''at=>{for(const key of Object.keys(localStorage)){if(key.startsWith('spark-quest:learning:l0-')){
      const p=JSON.parse(localStorage.getItem(key));p.attempts.forEach(a=>a.at=at);localStorage.setItem(key,JSON.stringify(p));}}}''',old)
    page.reload()
    items=[item for item in bank if item['slug'] in lessons]
    for i,item in enumerate(items):
        page.get_by_role('heading',name=item['title'],exact=True).wait_for()
        right=next(j for j,o in enumerate(item['options']) if o['id']==item['correctOptionId'])
        page.get_by_role('radio').nth(right).check();page.get_by_role('button',name='提交判断').click()
        page.get_by_text('隔了一天，这次独立判断正确',exact=True).wait_for()
        page.get_by_role('button',name='完成这一轮 →' if i==len(items)-1 else '验证下一个 →').click()
    page.get_by_role('heading',name='这一轮验证结束了').wait_for()
    page.reload();page.get_by_role('heading',name='暂时没有到期的验证').wait_for()
    print('PASS five L0 delayed materials wait 24h and retire after successful submission')

    project=lessons['l0-first-pyspark-program']['project']
    for href,digest in project['checksums'].items():
        response=page.request.get(ORIGIN+href)
        assert response.ok and hashlib.sha256(response.body()).hexdigest()==digest,href
    assert not errors,errors
    assert not writes,writes
    print('PASS five downloadable assets match released hashes; no browser errors or API writes')
    browser.close()
