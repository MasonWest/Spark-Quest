"""Reviewed choice edits, applied after the continuity authoring layers.

Each row lists the correct conclusion first, then two plausible misconceptions.
Existing option IDs/positions survive; a new lesson revision separates evidence.
"""
from pathlib import Path
import json

# Keys are stable task suffixes, not positional task numbers.
CHOICES = json.loads(Path(__file__).with_name('question_choice_edits.json').read_text(encoding='utf-8'))

INPUTS = {('l1-transformation', 'filter'): ('text', ['4,7', '4、7', '[4,7]', '4 7'], '用逗号分隔保留的数字'), ('l1-action', 'count'): ('text', ['count', 'count()'], '填写方法名'), ('l1-rdd-exercise', 'split'): ('integer', ['3'], '填写词元素个数'), ('l1-rdd-exercise', 'normalize'): ('integer', ['2'], '填写 spark 的次数'), ('l1-rdd-exercise', 'bridge-reduce-key'): ('text', ['spark=2,sql=1', 'spark=2，sql=1', 'spark=2 sql=1'], '例如：word=次数,other=次数')}


def apply(lessons, guides, delayed):
    for slug, edits in CHOICES.items():
        if slug not in lessons:
            continue
        lesson = lessons[slug]
        # Release versions are explicit: rerunning authors never increments them.
        revision = 4 if slug in ('l7-what-is-tuning','l7-executor-memory','l6-what-is-join','l1-why-dataframe-replaces-rdd') else 3
        lesson['version'] = max(lesson['version'], revision)
        for task in lesson['tasks']:
            key = task['id'].split('/')[-1]
            if key not in edits:
                continue
            field = task['fields'][0]
            right = next(o for o in field['options'] if o['id'] == field['correctOptionId'])
            wrong = [o for o in field['options'] if o['id'] != field['correctOptionId']]
            for option, text in zip([right] + wrong, edits[key]):
                option['text'] = text
                option['feedback'] = ('对。' if option is right else '这个判断还不成立。') + task['insight']
        for task in lesson['tasks']:
            key = task['id'].split('/')[-1]
            if (slug, key) in INPUTS:
                kind, accepted, placeholder = INPUTS[slug, key]
                field = task['fields'][0]
                field['input'] = dict(kind=kind,acceptedAnswers=accepted,placeholder=placeholder,
                    incorrectOptionId=next(o['id'] for o in field['options'] if o['id'] != field['correctOptionId']))
        if slug == 'l1-what-is-rdd':
            task = next(t for t in lesson['tasks'] if t['id'].endswith('/parts'))
            task['prompt'] = '只根据创建语句，哪项已经确定？'
            task = next(t for t in lesson['tasks'] if t['id'].endswith('/recover'))
            task['intro'] = '未登记持久化，也没有检查点；某个已计算分区丢失，上游文件仍可读且转换可重算。'
            task['code'] = '# 情境：无持久化副本；按可读上游重新计算丢失的分区。'
        if slug == 'l1-action':
            task = next(t for t in lesson['tasks'] if t['id'].endswith('/collect'))
            task['prompt'] = '只预览 5 条，哪种做法先限制返回 Driver 的数量？'
            task['insight'] = 'take(5)请求至多5个元素，collect()先回传全部结果，本地切片来不及限制回传规模。有界返回仍可能需要较多上游工作，也不保证随机抽样或全局排名。'
            # Keep the standard guide in sync with the newly explicit interface.
            for section in guides.get('lessons',{}).get(slug,{}).get('sections',[]):
                if section['id'] == task['id']:
                    section['body'] = task['insight']
            if task.get('reading'):
                task['reading']['connection'] = task['insight']
            for option in task['fields'][0]['options']:
                option['feedback'] = ('对。' if option['id'] == task['fields'][0]['correctOptionId'] else '再看请求与切片发生的先后。') + task['insight']
        if slug == 'l6-broadcast-hash-join':
            task = next(t for t in lesson['tasks'] if t['id'].endswith('/memory'))
            task['prompt'] = '判断广播构建是否安全，应优先估计什么？'
        if slug == 'l6-what-is-join':
            task = next(t for t in lesson['tasks'] if t['id'].endswith('/left'))
            task['intro'] = '订单有u1、u9；维表有u1、u8。要求保留全部订单，但不要为没有订单的u8新增一行。'
            task['code'] = '# 订单为左侧；未匹配订单补NULL；维表孤立行不输出。'
        if slug == 'l1-why-dataframe-replaces-rdd':
            task = next(t for t in lesson['tasks'] if t['id'].endswith('/still-rdd'))
            task['insight'] = '按需求选择接口，核对转换边界和资源成本。改写先验证结果；使用DataFrame不自动证明业务正确，也不承诺固定性能收益，仍需同条件代表性测量。'
            task['reading']['connection'] = task['insight']
            for section in guides.get('lessons',{}).get(slug,{}).get('sections',[]):
                if section['id'] == task['id']:
                    section['body'] = task['insight']
            for option in task['fields'][0]['options']:
                option['feedback'] = ('对。' if option['id'] == task['fields'][0]['correctOptionId'] else '先核对需求与接口边界。') + task['insight']
        if slug == 'l6-comprehensive':
            task = next(t for t in lesson['tasks'] if t['id'].endswith('/contract'))
            task['prompt'] = '订单为左侧，既保留订单，又落实缺失标签，应选择什么？'
        if slug == 'l7-executor-memory':
            task = next(t for t in lesson['tasks'] if t['id'].endswith('/bridge-execution-reclaim'))
            task['prompt'] = 'M=100、R=50、初始S=80且E=0；执行目标40。仅回收满足目标所缺的空间后，状态是？'
            task = next(t for t in lesson['tasks'] if t['id'].endswith('/eviction'))
            task['prompt'] = '缓存高于保护阈值，执行需要空间且空闲不足；这张共享模型允许什么？'
    if guides:
        guides['version'] = max(guides['version'], 8)


if __name__ == '__main__':
    import sys
    root = Path(__file__).resolve().parents[1] / 'src/content'
    lessons = {p.stem:json.loads(p.read_text(encoding='utf-8')) for p in (root/'lessons').glob('*.json')}
    guides = json.loads((root/'standardGuides.json').read_text(encoding='utf-8'))
    apply(lessons, guides, {})
    outputs = {root/'lessons'/f'{slug}.json':lessons[slug] for slug in CHOICES}
    outputs[root/'standardGuides.json'] = guides
    for path,data in outputs.items():
        text = json.dumps(data,ensure_ascii=False,indent=2)+'\n'
        if '--check' in sys.argv:
            assert path.read_text(encoding='utf-8') == text, path
        else:
            path.write_text(text,encoding='utf-8')
    print('PASS question polish:',len(CHOICES),'lessons;',len(INPUTS),'free responses')
