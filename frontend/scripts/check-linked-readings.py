"""Read-only fixture UI checks for linked lesson references. Pass slugs as arguments."""
from pathlib import Path
from contextlib import closing
import json,sqlite3,sys,re
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
slugs=sys.argv[1:] or ['l2-what-is-dataframe','l2-create-dataframe','l2-schema-types']
with closing(sqlite3.connect((root/'backend/spark_quest.db').as_uri()+'?mode=ro',uri=True)) as db:
 db.row_factory=sqlite3.Row
 lessons={r['slug']:dict(r) for r in db.execute('SELECT * FROM lessons')}
for d in lessons.values():d['content']=json.loads(d['content']);d.update(status='available',mastery_score=None,level_title='L2',next_lesson=None)
def normalize(text):return re.sub(r'[\W_①-⑳]','',text)
with sync_playwright() as p:
 b=p.chromium.launch();page=b.new_page(viewport={'width':390,'height':844});errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.route('**/api/lessons/**',lambda r:r.fulfill(json=[] if r.request.url.endswith('/notes') else next(d for d in lessons.values() if d['id']==int(r.request.url.rsplit('/',1)[1]))))
 for slug in slugs:
  d=lessons[slug];lesson=json.loads((root/'frontend/src/content/lessons'/f'{slug}.json').read_text(encoding='utf-8'))
  page.goto(f"http://127.0.0.1:4173/lesson/{d['id']}")
  key=f"spark-quest:learning:{slug}:v{lesson['version']}"
  for i,t in enumerate(lesson['tasks']):
   if t.get('reading'):
    ref=t['reading'];reading=page.locator('.lj-reading');before=page.evaluate('(k)=>localStorage.getItem(k)',key)
    reading.locator('summary').click();excerpt=d['content']['explanation'].split(ref['startMarker'])[1].split(ref['endMarker'])[0].strip()
    assert normalize(reading.locator('blockquote').inner_text())==normalize(excerpt),t['id']
    reading.locator('summary').click();assert before==page.evaluate('(k)=>localStorage.getItem(k)',key)
   if len(t['fields'])==1:
    f=t['fields'][0];page.get_by_role('radio').nth(next(j for j,o in enumerate(f['options']) if o['id']!=f['correctOptionId'])).check()
   else:
    for j,f in enumerate(t['fields']):page.locator('.lj-field select').nth(j).select_option(next(o['id'] for o in f['options'] if o['id']!=f['correctOptionId']))
   page.get_by_role('button',name='检查判断').click()
   assert page.get_by_role('button',name='继续下一步 →').count()==0
   if t.get('reading'):
    reading=page.locator('.lj-reading');assert reading.get_by_text('这一步没想通？借原文再想一想').is_visible()
    reading.locator('summary').click()
    if ref.get('caution'):
     assert reading.locator('.lj-reading-caution').is_visible()
     assert ref['caution'] in reading.locator('.lj-reading-caution').inner_text()
   page.get_by_role('button',name='调整后再试').click()
   if len(t['fields'])==1:
    f=t['fields'][0];page.get_by_role('radio').nth(next(j for j,o in enumerate(f['options']) if o['id']==f['correctOptionId'])).check()
   else:
    for j,f in enumerate(t['fields']):page.locator('.lj-field select').nth(j).select_option(f['correctOptionId'])
   page.get_by_role('button',name='检查判断').click()
   if t.get('reading'):
    reading=page.locator('.lj-reading');assert reading.get_by_text('把这次判断连成原理').is_visible()
    reading.locator('summary').click();assert reading.get_by_text(ref['boundary'],exact=True).is_visible()
    for w in [320,390,768,1440]:
     page.set_viewport_size({'width':w,'height':844});assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.set_viewport_size({'width':390,'height':844})
    if i==1:page.screenshot(path=str(root.parent/'ux_audit/learning-repair'/f'{slug}-reading-390.png'),full_page=True)
    reading.get_by_role('button',name='打开本课完整原文 →').click();assert page.locator('#lesson-reference').get_attribute('open') is not None
    page.locator('#lesson-reference > summary').click()
   page.get_by_role('button',name='看看我的收获' if i==len(lesson['tasks'])-1 else '继续下一步 →').click()
  page.get_by_role('heading',name='这次练会了什么？').wait_for()
  assert page.get_by_role('link',name='开始测验').get_attribute('href')==f"/lesson/{d['id']}/quiz"
  page.reload();page.get_by_role('heading',name='这次练会了什么？').wait_for()
  print('PASS',slug,'original links, concept bridges, source jump, responsive and completion')
 assert not errors,errors
 b.close()
