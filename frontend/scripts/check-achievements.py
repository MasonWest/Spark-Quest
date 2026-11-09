"""Isolated browser fixtures; never submits grades or edits the learning DB."""
import json
from pathlib import Path
from datetime import datetime,timedelta,timezone
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
badges=json.loads((root/'backend/_achievement_fixture.json').read_text(encoding='utf-8'))
for b in badges:
 if b['code'] in ['FIRST_SPARK','FIVE_PAGES','REVIEW_ECHO','REVIEW_VISITOR','OLD_PIT','REPAIR_CREW','STEADY_FIRE','WELCOME_BACK']:
  b.update(unlocked=False,unlocked_at=None,progress=3 if b['code']=='FIVE_PAGES' else 0)
 if b['is_secret']:b.update(unlocked=False,name='',description='',image='',goal=None,action='')
lessons={p.stem:json.loads(p.read_text(encoding='utf-8')) for p in (root/'frontend/src/content/lessons').glob('*.json')}
bank=json.loads((root/'frontend/src/content/delayedChecks.json').read_text(encoding='utf-8'))['items']
now=datetime.now(timezone.utc);source=(now-timedelta(days=3)).isoformat();passed=(now-timedelta(days=1)).isoformat()
storage={}
def state(slug):
 l=lessons[slug];key=f"spark-quest:learning:{slug}:v{l['version']}"
 if key not in storage:storage[key]=dict(version=l['version'],runId='test',cursorId=l['tasks'][0]['id'],completedIds=[],migratedIds=[],attempts=[])
 return storage[key]
def attempt(task,at,correct=True,activity=None):
 fields=task['fields'];options={f['id']:f['correctOptionId'] for f in fields};answers=options.copy()
 if not correct:answers[fields[0]['id']]=next(o['id'] for o in fields[0]['options'] if o['id']!=fields[0]['correctOptionId'])
 return dict(runId='test',taskId=task['id'],answers=answers,correctOptions=options,correct=correct,at=at,**({'activity':activity} if activity else {}))
for slug,key in [('l2-select-filter','step-a4e9ad8ec5'),('l3-where-order-limit','l3-where-order-limit/conditions')]:
 t=next(t for t in lessons[slug]['tasks'] if t['id']==key);state(slug)['attempts'].append(attempt(t,source))
events=[]
for item in bank[:5]:
 t=next(t for t in lessons[item['slug']]['tasks'] if t['id']==item['taskId']);p=state(item['slug']);p['completedIds'].append(t['id']);p['attempts'].append(attempt(t,source));events.append(dict(itemId=item['id'],sourceAt=source,answer=item['correctOptionId'],correctOptionId=item['correctOptionId'],correct=True,at=passed))
slug='l2-groupby-agg';t=next(t for t in lessons[slug]['tasks'] if t.get('remediation'));p=state(slug)
p['attempts'].append(attempt(t,source,False));r=t['remediation'];f=r['field']
p['attempts'].append(dict(runId='test',taskId=t['id'],activity='remediation',remediationId=r['id'],knowledgeId=r['knowledgeId'],answers={f['id']:f['correctOptionId']},correctOptions={f['id']:f['correctOptionId']},correct=True,at=source))
p['attempts'].append(attempt(t,source))
encoded={k:json.dumps(v) for k,v in storage.items()};encoded['spark-quest:delayed:v1']=json.dumps(events)
with sync_playwright() as pw:
 browser=pw.chromium.launch();context=browser.new_context(viewport={'width':390,'height':844});page=context.new_page();errors=[];writes=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 def route(r):
  if r.request.method!='GET':writes.append(r.request.url)
  r.fulfill(json=badges)
 context.route('**/api/badges',route)
 context.route('**/api/dashboard',lambda r:r.fulfill(json=json.loads((root/'backend/_achievement_home.json').read_text(encoding='utf-8'))))
 context.add_init_script('const fixture='+json.dumps(encoded)+'; for(const [k,v] of Object.entries(fixture))localStorage.setItem(k,v);')
 page.goto('http://127.0.0.1:4173/badges');page.get_by_text('两种表达',exact=True).wait_for()
 page.get_by_text('本机新成就已收录：',exact=False).wait_for()
 local=page.locator('section').filter(has=page.get_by_role('heading',name='本机练习',exact=True))
 assert local.locator('article.unlocked').count()==4
 assert page.locator('.ag-goal h2').inner_text()=='翻开新页'
 assert page.locator('article.secret progress').count()==0 and page.locator('article.secret a').count()==0
 for w in [320,390,768,1440]:
  page.set_viewport_size({'width':w,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 page.set_viewport_size({'width':390,'height':844});out=root.parent/'ux_audit/achievements';out.mkdir(parents=True,exist_ok=True);page.screenshot(path=str(out/'wall-390.png'),full_page=True)
 page.get_by_role('button',name='已获得',exact=True).click();assert page.locator('article.locked').count()==0
 page.get_by_role('button',name='待点亮',exact=True).click();assert page.locator('article.unlocked').count()==0
 for b in badges:
  if b['image']:
   assert page.request.get('http://127.0.0.1:4173'+b['image']).ok,b['image']
 page.goto('http://127.0.0.1:4173/');page.locator('.ag-goal').wait_for();assert page.locator('.ag-goal h2').inner_text()=='翻开新页'
 assert page.locator('.ag-goal a').get_attribute('href')=='/map'
 page.screenshot(path=str(out/'home-390.png'),full_page=True)
 broken=browser.new_context();broken.route('**/api/badges',route);broken.add_init_script("Storage.prototype.getItem=()=>{throw Error('denied')}");bp=broken.new_page();bp.goto('http://127.0.0.1:4173/badges');bp.get_by_text('本机记录暂时无法读取或保存',exact=False).wait_for();assert bp.locator('.ag-goal').count()==1
 retry=browser.new_context();retry.route('**/api/badges',route)
 invalid=encoded.copy();bad_event=events[0].copy();bad_event.update(correct=False,at=(now-timedelta(days=1,hours=2)).isoformat());late=events[0].copy();late['at']=(now-timedelta(days=1,hours=1)).isoformat()
 invalid['spark-quest:delayed:v1']=json.dumps([bad_event,late]);retry.add_init_script('const data='+json.dumps(invalid)+';for(const [k,v] of Object.entries(data))localStorage.setItem(k,v);');rp=retry.new_page();rp.goto('http://127.0.0.1:4173/badges');rp.get_by_text('隔天还会',exact=True).wait_for();assert rp.locator('article').filter(has=rp.get_by_text('隔天还会',exact=True)).get_by_text('等待下一次进步',exact=False).count()==1
 corrupt=browser.new_context();corrupt.route('**/api/badges',route);corrupt.add_init_script("localStorage.setItem('spark-quest:local-achievements:v1','[]')");cp=corrupt.new_page();cp.goto('http://127.0.0.1:4173/badges');cp.get_by_text('本机记录暂时无法读取或保存',exact=False).wait_for();assert cp.evaluate("localStorage.getItem('spark-quest:local-achievements:v1')")=='[]'
 assert not errors and not writes,(errors,writes)
 print('PASS four local achievements, retry delay, exact pair mapping, secret protection, filter, progress, SVG assets, denied storage, mobile layout; no grade writes')
 browser.close()
