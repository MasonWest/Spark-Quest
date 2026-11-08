"""Check per-lesson content loading and stale lesson fetch cancellation."""
from pathlib import Path
from contextlib import closing
import json,sqlite3
from playwright.sync_api import sync_playwright, Error
root=Path(__file__).resolve().parents[2]
with closing(sqlite3.connect((root/'backend/spark_quest.db').as_uri()+'?mode=ro',uri=True)) as db:
    db.row_factory=sqlite3.Row
    lessons={r['slug']:dict(r) for r in db.execute('SELECT * FROM lessons')}
for row in lessons.values():
    row['content']=json.loads(row['content']);row.update(status='available',mastery_score=None,level_title=row['slug'].split('-')[0],next_lesson=None)
with sync_playwright() as p:
    browser=p.chromium.launch();page=browser.new_page();requested=[];errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('request',lambda r:requested.append(r.url) if '/assets/l' in r.url and r.url.endswith('.js') else None)
    def api(route):
        if route.request.url.endswith('/notes'):return route.fulfill(json=[])
        return route.fulfill(json=next(l for l in lessons.values() if l['id']==int(route.request.url.rsplit('/',1)[1])))
    page.route('**/api/lessons/**',api)
    slug='l4-why-explain';detail=lessons[slug]
    page.goto(f"http://127.0.0.1:4173/lesson/{detail['id']}");page.locator('.lj-mission').wait_for()
    assert len(requested)==1 and f'/assets/{slug}-' in requested[0],requested
    held=[];a=lessons['l5-what-is-partition'];b=lessons['l6-what-is-join']
    def delayed(route):
        if route.request.url.endswith(f"/{a['id']}"):held.append(route)
        else:api(route)
    page.unroute('**/api/lessons/**');page.route('**/api/lessons/**',delayed)
    page.evaluate('(id)=>{history.pushState({},"",`/lesson/${id}`);dispatchEvent(new PopStateEvent("popstate"))}',a['id'])
    page.wait_for_timeout(200);assert held
    page.evaluate('(id)=>{history.pushState({},"",`/lesson/${id}`);dispatchEvent(new PopStateEvent("popstate"))}',b['id'])
    page.get_by_role('heading',name=b['title'],exact=True).wait_for()
    try:held[0].fulfill(json=a)
    except Error:pass
    page.wait_for_timeout(100)
    assert page.get_by_role('heading',name=b['title'],exact=True).is_visible()
    assert not errors,errors
    print('PASS only requested lesson chunk loaded; stale fetch cannot replace later lesson')
    browser.close()
