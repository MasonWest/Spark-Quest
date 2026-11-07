"""Read-only lesson fixtures; checks the independent task entry and optional warmup."""
from pathlib import Path
from contextlib import closing
import json
import sqlite3
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[2]
with closing(sqlite3.connect((root / 'backend/spark_quest.db').as_uri() + '?mode=ro', uri=True)) as db:
    db.row_factory = sqlite3.Row
    detail = dict(db.execute("SELECT * FROM lessons WHERE slug='l2-comprehensive'").fetchone())
detail['content'] = json.loads(detail['content'])
detail.update(status='available', mastery_score=None, level_title='L2', next_lesson=None)
project = json.loads((root / 'frontend/src/content/capstones.json').read_text(encoding='utf-8'))['lessons'][detail['slug']]
key = f"spark-quest:capstone:{project['id']}:draft"
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 390, 'height': 844})
    errors = []
    writes = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    def api(route):
        if route.request.method != 'GET':
            writes.append(route.request.url)
        route.fulfill(json=[{'id': 1, 'content': '我的旧笔记仍在这里', 'created_at': '2026-11-01T00:00:00'}] if route.request.url.endswith('/notes') else detail)
    page.route('**/api/lessons/**', api)
    url = f"http://127.0.0.1:4173/lesson/{detail['id']}"
    page.goto(url)
    board = page.locator('.cp-root')
    board.wait_for()
    assert page.locator('#capstone-guided').get_attribute('open') is None
    assert page.get_by_role('radio').count() == 0
    assert page.locator('.lj-mission').is_visible() is False
    assert board.get_by_role('link', name=project['solution']['label'] + ' ↓').count() == 0
    for width in [320, 390, 768, 1440]:
        page.set_viewport_size({'width': width, 'height': 844})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), width
    page.set_viewport_size({'width': 390, 'height': 844})
    out = root.parent / 'ux_audit/learning-repair'
    out.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(out / 'l2-graduation-390.png'), full_page=True)
    before = page.evaluate('JSON.stringify(localStorage)')
    board.get_by_text('我卡住了，给一点提示', exact=True).click()
    for index, button in enumerate(['给我一个方向', '提示再具体一点', '看处理顺序骨架']):
        assert board.locator('.cp-hint').count() == index
        board.get_by_role('button', name=button).click()
    assert board.locator('.cp-hint').count() == 3
    assert page.evaluate('JSON.stringify(localStorage)') == before
    for i, text in enumerate(['我的预期', '我的计划', '修正记录']):
        board.get_by_role('textbox').nth(i).fill(text)
    board.get_by_role('button', name='保存本机草稿').click()
    assert board.get_by_role('status').is_visible()
    assert page.evaluate('(k)=>JSON.parse(localStorage.getItem(k)).plan', key) == '我的计划'
    page.reload()
    assert board.get_by_role('textbox').nth(0).input_value() == '我的预期'
    assert board.locator('.cp-hint').count() == 0
    board.get_by_text('我已经尝试，想对照参考实现', exact=True).click()
    board.get_by_role('button', name='展开参考实现下载').click()
    assert board.get_by_role('link', name=project['solution']['label'] + ' ↓').is_visible()
    for asset in project['downloads'] + [project['solution']]:
        response = page.request.get('http://127.0.0.1:4173' + asset['href'])
        assert response.ok and len(response.body()) > 50, asset
    assert board.get_by_role('link', name='进入课后测验 →').get_attribute('href') == f"/lesson/{detail['id']}/quiz"
    page.locator('#capstone-guided > summary').click()
    page.locator('.lj-mission').wait_for()
    page.locator('#capstone-guided > summary').click()
    page.get_by_text('我的学习笔记（展开查看或记录）', exact=True).click()
    assert page.get_by_text('我的旧笔记仍在这里', exact=True).is_visible()
    assert page.evaluate('Object.keys(localStorage).every(k=>k.includes(":capstone:"))')
    page.evaluate("() => { Storage.prototype.setItem=()=>{throw Error('denied')} }")
    board.get_by_role('button', name='保存本机草稿').click()
    assert '暂时无法保存' in board.get_by_role('status').inner_text()
    assert not errors and not writes, (errors, writes)
    print('PASS task first, optional warmup, staged hints, gated reference, draft restore, files, notes, quiz link, denied save, responsive; no grade writes')
    browser.close()
