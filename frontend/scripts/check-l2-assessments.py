"""Render the two L2 pools using read-only DB fixture IDs; never submit grades."""
from pathlib import Path
from contextlib import closing
import json,sqlite3,sys
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
bank=json.loads((root/'backend/app/l2_reviewed_bank.json').read_text(encoding='utf-8'))
if '--all' in sys.argv:
 for name in ['l3_l6_reviewed_bank.json','l1_l7_reviewed_bank.json']:bank['lessons'] += json.loads((root/'backend/app'/name).read_text(encoding='utf-8'))['lessons']
with closing(sqlite3.connect((root/'backend/spark_quest.db').as_uri()+'?mode=ro',uri=True)) as db:
 ids=dict(db.execute('SELECT slug,id FROM lessons'))
 qids={(slug,prompt):qid for slug,prompt,qid in db.execute('SELECT l.slug,q.prompt,q.id FROM quizzes q JOIN lessons l ON l.id=q.lesson_id')}
with sync_playwright() as p:
 b=p.chromium.launch();page=b.new_page(viewport={'width':390,'height':844});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 for entry in bank['lessons']:
  slug=entry['lesson_slug'];lid=ids[slug]
  for phase in ['assessment','review']:
   selected=[q for q in entry['questions'] if (q['purpose']=='assessment')==(phase=='assessment')]
   payload={'lesson_id':lid,'lesson_title':slug,'questions':[{'id':qids[(slug,q['prompt'])],'type':q['type'],'prompt':q['prompt'],'options':q['options'],'dimension':q['dimension']} for q in selected]}
   path=f'/api/lessons/{lid}/quiz' if phase=='assessment' else f'/api/review/{lid}'
   def handle(route):return route.fulfill(json=payload)
   page.route('**'+path,handle)
   page.goto(f'http://127.0.0.1:4173/lesson/{lid}/quiz' if phase=='assessment' else f'http://127.0.0.1:4173/review/{lid}')
   page.locator('.quiz-question').first.wait_for();assert page.locator('.quiz-question').count()==5
   for width in [320,390,768]:
    page.set_viewport_size({'width':width,'height':844});assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),(slug,phase,width)
   page.set_viewport_size({'width':390,'height':844})
   assert page.get_by_role('button',name='请答完所有题目').is_disabled()
   for q in selected:page.locator(f'input[name="q-{qids[(slug,q["prompt"])]}"]').nth(q['correct_index']).check()
   assert page.get_by_role('button',name='提交测验' if phase=='assessment' else '提交复习').is_enabled()
   if slug=='l2-groupby-agg' and phase=='assessment':page.screenshot(path=str(root.parent/'ux_audit/learning-repair/l2-new-assessment-390.png'),full_page=True)
   page.unroute('**'+path)
  print('PASS browser',slug,'both pools, five questions, responsive and answer selection')
 assert not errors,errors
 b.close()
