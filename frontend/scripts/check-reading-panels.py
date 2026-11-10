"""Reading exits on mobile: sticky controls, focus, practice state, capstones.
Uses isolated browser storage and mocked read-only lesson APIs.
"""
from pathlib import Path
from contextlib import closing
import json
import sqlite3
import sys
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
ORIGIN='http://127.0.0.1:4173'
ENGINE='webkit' if '--webkit' in sys.argv else 'chromium'
with closing(sqlite3.connect((ROOT/'backend/spark_quest.db').as_uri()+'?mode=ro',uri=True)) as db:
    db.row_factory=sqlite3.Row
    details={r['slug']:dict(r) for r in db.execute('SELECT * FROM lessons')}
for l in details.values():
    l['content']=json.loads(l['content'])
    l.update(status='available',mastery_score=None,level_title='Reading fixture',next_lesson=None)

out=ROOT.parent/'ux_audit/reading-panels'/ENGINE;out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    browser=getattr(p,ENGINE).launch()
    context=browser.new_context(viewport=dict(width=390,height=844),is_mobile=True,has_touch=True)
    page=context.new_page();errors=[];writes=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    def api(route):
        if route.request.method!='GET':writes.append(route.request.url);return route.abort()
        if route.request.url.endswith('/notes'):return route.fulfill(json=[])
        ident=int(route.request.url.rsplit('/',1)[-1])
        route.fulfill(json=next(l for l in details.values() if l['id']==ident))
    page.route('**/api/**',api)

    def open_panel(ident):
        panel=page.locator('#'+ident)
        panel.locator(':scope > summary').click()
        assert panel.evaluate('(el)=>el.open')
        panel.evaluate('''el=>{
            const body=el.querySelector('.lrp-content');
            window.scrollTo(0, window.scrollY + body.getBoundingClientRect().top + body.offsetHeight * .6);
        }''')
        page.wait_for_timeout(100)
        toolbar=panel.locator('.lrp-toolbar')
        box=toolbar.bounding_box()
        assert box and 0<=box['y']<=24,(ident,box)
        return panel,toolbar

    for slug in ['l1-action','l7-executor-memory','l2-comprehensive']:
        page.goto(f"{ORIGIN}/lesson/{details[slug]['id']}")
        page.locator('#lesson-original').wait_for(state='attached')
        capstone=page.locator('#capstone-guided')
        if capstone.count():capstone.locator(':scope > summary').click()
        page.locator('[data-journey-heading]').wait_for()
        if slug=='l1-action':page.locator('.lj-field input').fill('count')
        for width in [320,390,768,1440]:
            page.set_viewport_size(dict(width=width,height=844))
            original,toolbar=open_panel('lesson-original')
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(slug,width,page.evaluate('''()=>({viewport:innerWidth,document:document.documentElement.scrollWidth,wide:[...document.querySelectorAll('.container,.card,.lrp-panel,.lrp-toolbar,.lrp-content,pre,table')].map(e=>({tag:e.tagName,cls:e.className,right:e.getBoundingClientRect().right,width:e.getBoundingClientRect().width})).filter(e=>e.right>innerWidth+1).slice(0,10)})'''))
            if width==390:page.screenshot(path=str(out/(slug+'-390.png')))
            if capstone.count():capstone.evaluate('(el)=>el.open=false')
            toolbar.get_by_role('button',name='返回当前练习 ↑').click()
            assert not original.evaluate('(el)=>el.open')
            page.wait_for_function("document.activeElement === document.querySelector('[data-journey-heading]')")
            heading=page.locator('[data-journey-heading]')
            assert heading.evaluate('(el)=>document.activeElement===el')
            box=heading.bounding_box();assert box and 0<=box['y']<120,box
            if capstone.count():assert capstone.evaluate('(el)=>el.open')
            if slug=='l1-action':assert page.locator('.lj-field input').input_value()=='count'
            original,toolbar=open_panel('lesson-original')
            toolbar.get_by_role('button',name='收起原文').click()
            page.wait_for_function("document.activeElement === document.querySelector('#lesson-original > summary')")
            summary=original.locator(':scope > summary')
            assert not original.evaluate('(el)=>el.open')
            assert summary.evaluate('(el)=>document.activeElement===el')
            page.wait_for_timeout(100)
            box=summary.bounding_box()
            assert 0<=box['y'] and box['y']+box['height']<=844,(slug,width,box)
        standard,toolbar=open_panel('lesson-reference')
        toolbar.get_by_role('button',name='返回当前练习 ↑').click()
        assert not standard.evaluate('(el)=>el.open')
        if slug=='l1-action':
            page.locator('.lj-reading > details > summary').click()
            page.get_by_role('button',name='打开本课标准讲解 →',exact=True).click()
            assert page.locator('#lesson-reference').evaluate('(el)=>el.open')
            page.locator('#lesson-reference .lrp-toolbar').get_by_role('button',name='返回当前练习 ↑').click()
            assert page.locator('.lj-field input').input_value()=='count'
            page.get_by_role('button',name='检查判断').click()
            page.get_by_role('button',name='继续下一步 →').click()
            lesson=json.loads((ROOT/'frontend/src/content/lessons/l1-action.json').read_text(encoding='utf-8'))
            field=lesson['tasks'][1]['fields'][0]
            wrong=next(i for i,o in enumerate(field['options']) if o['id']!=field['correctOptionId'])
            page.get_by_role('radio').nth(wrong).check()
            page.get_by_role('button',name='检查判断').click()
            page.get_by_role('button',name='换一道小题验证 →').click()
            page.get_by_role('radio').first.check()
            original,toolbar=open_panel('lesson-original')
            toolbar.get_by_role('button',name='返回当前练习 ↑').click()
            page.wait_for_function("document.activeElement === document.querySelector('[data-journey-heading]')")
            assert page.locator('.lj-remediation').is_visible()
            assert page.get_by_role('radio').first.is_checked()
        print('PASS',slug,'sticky navigation, collapse, practice return, focus and answer preservation')
    assert not errors,errors
    assert not writes,writes
    browser.close()
