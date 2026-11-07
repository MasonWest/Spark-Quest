"""Delayed-check UI QA with localStorage fixtures and a controlled browser clock; no DB writes."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
bank=json.loads((root/'frontend/src/content/delayedChecks.json').read_text(encoding='utf-8'))
with sync_playwright() as p:
 b=p.chromium.launch();context=b.new_context(viewport={'width':390,'height':844});page=context.new_page();errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.route('**/api/**',lambda r:r.fulfill(status=503,json={'detail':'UI fixture, backend unused'}))
 page.clock.install(time=1893492000000)
 page.goto('http://127.0.0.1:4173/delayed-check')
 page.get_by_role('heading',name='暂时没有到期的验证').wait_for()
 fixtures={}
 for item in bank['items']:
  lesson=json.loads((root/'frontend/src/content/lessons'/f"{item['slug']}.json").read_text(encoding='utf-8'))
  key=f"spark-quest:learning:{lesson['slug']}:v{lesson['version']}"
  state=fixtures.setdefault(key,dict(version=lesson['version'],runId='qa',cursorId=lesson['tasks'][0]['id'],completedIds=[],migratedIds=[],attempts=[]))
  task=next(t for t in lesson['tasks'] if t['id']==item['taskId'])
  state['completedIds'].append(task['id'])
  state['attempts'].append(dict(runId='qa',taskId=task['id'],answers={f['id']:f['correctOptionId'] for f in task['fields']},correctOptions={f['id']:f['correctOptionId'] for f in task['fields']},correct=True,at='2029-12-31T09:00:00Z'))
 page.evaluate('(f)=>Object.entries(f).forEach(([k,v])=>localStorage.setItem(k,JSON.stringify(v)))',fixtures)
 page.goto('http://127.0.0.1:4173/')
 page.get_by_role('link',name='开始隔天验证 →').click()
 for index,item in enumerate(bank['items']):
  page.get_by_role('heading',name=item['title'],exact=True).wait_for()
  assert page.get_by_role('button',name='提交判断').is_disabled()
  assert page.get_by_text(item['explanation'],exact=True).count()==0
  for width in [320,390,768,1440]:
   page.set_viewport_size({'width':width,'height':844});assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),(item['id'],width)
  page.set_viewport_size({'width':390,'height':844})
  option=next(i for i,o in enumerate(item['options']) if (o['id']==item['correctOptionId']) == (index!=0))
  page.get_by_role('radio').nth(option).check();page.get_by_role('button',name='提交判断').click()
  assert page.get_by_text(item['explanation'],exact=True).is_visible()
  assert page.get_by_role('radio').first.is_disabled()
  if index==0:
   out=root.parent/'ux_audit/learning-repair';out.mkdir(parents=True,exist_ok=True)
   page.screenshot(path=str(out/'l2-delayed-check-390.png'),full_page=True)
   page.reload();page.get_by_role('heading',name=bank['items'][1]['title'],exact=True).wait_for()
  else:page.get_by_role('button',name='完成这一轮 →' if index==len(bank['items'])-1 else '验证下一个 →').click()
  print('PASS',item['id'],'independent choice, explanation after submit, responsive')
 page.get_by_role('heading',name='这一轮验证结束了').wait_for()
 records=page.evaluate('JSON.parse(localStorage.getItem("spark-quest:delayed:v1"))');assert len(records)==len(bank['items']) and sum(e['correct'] for e in records)==len(bank['items'])-1
 for key,state in fixtures.items():assert page.evaluate('(k)=>JSON.parse(localStorage.getItem(k))',key)==state
 page.goto('http://127.0.0.1:4173/');assert page.get_by_role('link',name='开始隔天验证 →').count()==0
 page.clock.fast_forward(24*60*60*1000)
 page.reload();page.get_by_role('link',name='开始隔天验证 →').click();page.get_by_role('heading',name=bank['items'][0]['title'],exact=True).wait_for()
 assert '共 1 题' in page.locator('main').inner_text()
 # A new tab changed the schedule: stale submission must fail without showing success.
 page.evaluate('localStorage.setItem("spark-quest:delayed:v1",JSON.stringify(JSON.parse(localStorage.getItem("spark-quest:delayed:v1")).concat({...JSON.parse(localStorage.getItem("spark-quest:delayed:v1"))[0],correct:true,at:new Date().toISOString()})))')
 page.get_by_role('radio').first.check();page.get_by_role('button',name='提交判断').click();assert page.get_by_role('alert').is_visible();assert page.get_by_role('status').count()==0
 blocked=b.new_context();blocked.add_init_script("Storage.prototype.getItem=()=>{throw Error('denied')}");bp=blocked.new_page();bp.goto('http://127.0.0.1:4173/delayed-check');bp.get_by_role('heading',name='暂时无法读取验证安排').wait_for();assert bp.get_by_role('alert').is_visible()
 assert not errors,errors
 print('PASS homepage entry, refresh resumes pending items, 24h retry, unchanged original records, stale submit, denied storage')
 b.close()
