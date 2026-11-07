"""UI regression for all five Shuffle reading links. Uses read-only DB fixtures."""
from pathlib import Path
from contextlib import closing
import json,sqlite3
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
with closing(sqlite3.connect((root/'backend/spark_quest.db').as_uri()+'?mode=ro',uri=True)) as db:
 db.row_factory=sqlite3.Row
 data=dict(db.execute("SELECT * FROM lessons WHERE slug='l5-what-is-shuffle'").fetchone())
data['content']=json.loads(data['content']);data.update(status='available',mastery_score=None,level_title='Level 5',next_lesson=None)
lesson=json.loads((root/'frontend/src/content/lessons/l5-what-is-shuffle.json').read_text(encoding='utf-8'))
original=data['content']['explanation'];key=f"spark-quest:learning:{lesson['slug']}:v{lesson['version']}"
out=root.parent/'ux_audit/learning-repair';out.mkdir(exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch();page=b.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.route('**/api/lessons/**',lambda r:r.fulfill(json=[] if r.request.url.endswith('/notes') else data))
 page.goto(f"http://127.0.0.1:4173/lesson/{data['id']}")
 for index,t in enumerate(lesson['tasks']):
  reading=page.locator('.lj-reading');reading.locator('summary').click()
  ref=t['reading'];excerpt=original.split(ref['startMarker'])[1].split(ref['endMarker'])[0].strip()
  assert reading.locator('blockquote').inner_text().split()==excerpt.replace('`','').replace('**','').split(), t['id']
  before=page.evaluate('(key)=>localStorage.getItem(key)',key)
  reading.locator('summary').click();assert page.evaluate('(key)=>localStorage.getItem(key)',key)==before
  if len(t['fields'])==1:
   f=t['fields'][0];wrong=next(i for i,o in enumerate(f['options']) if o['id']!=f['correctOptionId']);page.get_by_role('radio').nth(wrong).check()
  else:
   for i,f in enumerate(t['fields']):page.locator('.lj-field select').nth(i).select_option(next(o['id'] for o in f['options'] if o['id']!=f['correctOptionId']))
  page.get_by_role('button',name='检查判断').click()
  assert reading.get_by_text('这一步没想通？借原文再想一想').is_visible()
  reading.locator('summary').click();assert reading.locator('blockquote').is_visible()
  page.get_by_role('button',name='调整后再试').click()
  if len(t['fields'])==1:
   page.get_by_role('radio').nth(next(i for i,o in enumerate(t['fields'][0]['options']) if o['id']==t['fields'][0]['correctOptionId'])).check()
  else:
   for i,f in enumerate(t['fields']):page.locator('.lj-field select').nth(i).select_option(f['correctOptionId'])
  page.get_by_role('button',name='检查判断').click()
  assert reading.get_by_text('把这次判断连成原理').is_visible()
  assert reading.get_by_text(ref['connection'],exact=False).is_visible()
  reading.locator('summary').click();assert reading.get_by_text(ref['boundary'],exact=True).is_visible()
  for width in [320,390,768,1440]:
   page.set_viewport_size({'width':width,'height':844});assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),t['id']
  page.set_viewport_size({'width':390,'height':844})
  page.screenshot(path=str(out/f"shuffle-integrated-{index+1}-390.png"),full_page=True)
  reading.get_by_role('button',name='打开本课完整原文 →').click();assert page.locator('#lesson-reference').get_attribute('open') is not None
  page.locator('#lesson-reference > summary').click()
  page.get_by_role('button',name='看看我的收获' if index==4 else '继续下一步 →').click()
  print('PASS',t['id'],'exact source, optional reading, wrong/correct guidance, source jump, responsive')
 page.get_by_role('heading',name='这次练会了什么？').wait_for()
 assert page.locator('.lj-evidence').count()==5
 assert page.get_by_role('link',name='开始测验').get_attribute('href')==f"/lesson/{data['id']}/quiz"
 page.reload();page.get_by_role('heading',name='这次练会了什么？').wait_for()
 assert not errors,errors
 print('PASS completion, persistence and unchanged quiz link; no learning DB writes')
 b.close()
