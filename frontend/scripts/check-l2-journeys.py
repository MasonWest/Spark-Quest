from pathlib import Path
from contextlib import closing
import sqlite3,json,sys
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
with closing(sqlite3.connect((root/'backend/spark_quest.db').as_uri()+'?mode=ro',uri=True)) as db:
 db.row_factory=sqlite3.Row
 lessons={r['slug']:dict(r) for r in db.execute('SELECT * FROM lessons')}
for l in lessons.values():
 l['content']=json.loads(l['content']);l.update(status='available',mastery_score=None,level_title=f"Level {l['slug'].split('-')[0][1:]}",next_lesson=None)
capstones=json.loads((root/'frontend/src/content/capstones.json').read_text(encoding='utf-8'))['lessons']
content={p.stem:json.loads(p.read_text(encoding='utf-8')) for p in (root/'frontend/src/content/lessons').glob('*.json')}
answers={slug:[[next(i for i,o in enumerate(f['options']) if o['id']==f['correctOptionId']) for f in t['fields']] for t in l['tasks']] for slug,l in content.items()}

out=root.parent/'ux_audit/learning-repair';out.mkdir(exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch();context=b.new_context(viewport={'width':390,'height':844});page=context.new_page()
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 def api(route):
  url=route.request.url
  if url.endswith('/notes'):return route.fulfill(json=[])
  id=int(url.rsplit('/',1)[-1]);return route.fulfill(json=next(l for l in lessons.values() if l['id']==id))
 page.route('**/api/lessons/**',api)
 for slug,steps in answers.items():
  if sys.argv[1:] and slug not in sys.argv[1:]:continue
  l=lessons[slug];url=f"http://127.0.0.1:4173/lesson/{l['id']}"
  page.goto(url)
  if slug in capstones:page.locator('#capstone-guided > summary').click()
  page.locator('.lj-mission').wait_for()
  if slug not in capstones:assert page.locator('.dfj-reference').first.get_attribute('open') is None
  if slug.startswith(('l1-','l2-','l3-','l4-','l5-','l6-','l7-')):
   assert page.locator('#lesson-reference').get_attribute('open') is None
   assert page.locator('#lesson-original').get_attribute('open') is None
  elif content[slug]['correction']:assert page.get_by_text('原文勘误 · 阅读时以此为准').is_visible()
  for width in [320,390,768,1440]:
   page.set_viewport_size({'width':width,'height':844});assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),(slug,width)
  page.set_viewport_size({'width':390,'height':844})
  page.screenshot(path=str(out/(slug+'-390.png')),full_page=True)
  for n,expected in enumerate(steps):
   if page.locator('.lj-field input').count():
    assert page.get_by_role('button',name='检查判断').is_disabled()
    assert page.get_by_role('radio').count()==0
    for i,f in enumerate(content[slug]['tasks'][n]['fields']):page.locator('.lj-field input').nth(i).fill('999')
   elif page.locator('.lj-field select').count():
    for i,index in enumerate(expected):page.locator('.lj-field select').nth(i).select_option(content[slug]['tasks'][n]['fields'][i]['options'][(index+1)%3]['id'])
   else:
    assert page.get_by_role('button',name='检查判断').is_disabled()
    page.get_by_role('radio').nth((expected[0]+1)%3).check()
   page.get_by_role('button',name='检查判断').click()
   assert page.get_by_role('status').is_visible()
   assert page.get_by_role('button',name='继续下一步 →').count()==0
   page.get_by_role('button',name='先重试原题' if content[slug]['tasks'][n].get('remediation') else '调整后再试').click()
   if page.locator('.lj-field input').count():
    for i,f in enumerate(content[slug]['tasks'][n]['fields']):page.locator('.lj-field input').nth(i).fill(f['input']['acceptedAnswers'][0])
    page.screenshot(path=str(out/(slug+'-input-'+str(n)+'-390.png')),full_page=True)
   elif page.locator('.lj-field select').count():
    for i,index in enumerate(expected):page.locator('.lj-field select').nth(i).select_option(content[slug]['tasks'][n]['fields'][i]['options'][index]['id'])
   else:page.get_by_role('radio').nth(expected[0]).check()
   page.get_by_role('button',name='检查判断').click()
   page.get_by_role('button',name='看看我的收获' if n==len(steps)-1 else '继续下一步 →').click()
   if n==0:
    page.reload()
    if slug in capstones:page.locator('#capstone-guided > summary').click()
    page.get_by_text(f'第 2 步 / 共 {len(steps)} 步',exact=False).wait_for()
  page.get_by_role('heading',name='这次练会了什么？').wait_for()
  assert page.locator('.lj-evidence').count()==len(steps)
  if slug=='l2-comprehensive':
   page.locator('#capstone-guided').get_by_text('展开参考实现下载',exact=True).click()
   for asset in ['orders.csv','starter.py','README.txt','solution.py']:
    response=page.request.get('http://127.0.0.1:4173/practice/l2/'+asset)
    assert response.ok and len(response.body())>50,asset
  page.reload()
  if slug in capstones:page.locator('#capstone-guided > summary').click()
  page.get_by_role('heading',name='这次练会了什么？').wait_for()
  assert page.get_by_role('link',name='开始测验').get_attribute('href')==f"/lesson/{l['id']}/quiz"
  page.get_by_role('button',name='重新练一遍').click();page.locator('.lj-mission').wait_for()
  print('PASS',slug,l['id'],'all tasks, feedback, persistence, reset, quiz link, responsive')
 page.goto(f"http://127.0.0.1:4173/lesson/{lessons['l2-what-is-dataframe']['id']}")
 page.get_by_role('heading',name='先猜一猜：四条订单，算得动吗？').wait_for()
 isolated=b.new_context();isolated.add_init_script("Storage.prototype.getItem = () => { throw new Error('blocked') }; Storage.prototype.setItem = () => { throw new Error('blocked') }")
 blocked=isolated.new_page();blocked.route('**/api/lessons/**',api)
 blocked.goto(f"http://127.0.0.1:4173/lesson/{lessons['l2-inspect']['id']}");blocked.locator('.lj-mission').wait_for()
 assert not errors,errors
 print('PASS original pilot regression, denied storage fallback, no browser errors. API fixtures used; Spark execution not tested.')
 b.close()
