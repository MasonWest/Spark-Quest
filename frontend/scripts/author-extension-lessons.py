"""Publish two lessons, seed placement, purpose banks and delayed material. --check is read-only."""
import json
from pathlib import Path
import sys
from extension_lessons import ROOT,WINDOW,CACHE,SOURCES,build,extension_specs,apply_continuity

content=ROOT/'frontend/src/content'
lessons=build();guides=json.loads((content/'standardGuides.json').read_text(encoding='utf-8'));delayed=json.loads((content/'delayedChecks.json').read_text(encoding='utf-8'))
delayed['items']=[i for i in delayed['items'] if i['slug'] not in lessons]
for slug,l in lessons.items():
    for i,t in enumerate(l['tasks']):
        f=t['fields'][0];f['options']=f['options'][i%3:]+f['options'][:i%3]
    guides['lessons'][slug]=dict(title=l['title'],sources=[dict(title='Spark3.5.7官方文档',url=SOURCES[slug])],sections=[dict(id=t['id'],title=t['title'],body=t['insight'],boundary=t['reading']['boundary']) for t in l['tasks']])
    if slug==WINDOW:
        t=l['tasks'][2];code='u2同一时间有e20、e21；event_id唯一\n约定时间降序、event_id降序选1条'
        prompt='按此约定保留哪条？';choices=['e20','e21','都随机'];correct=1;why='并列时间由明确的唯一排序键决定，ROW_NUMBER选中整行。'
        newcode='u8: e1/time=NULL、e2/time=4\n已知时间优先，event_id打破剩余并列';newprompt='哪种排序符合约定？';newchoices=['time DESC NULLS LAST,event_id DESC','只按user_id','先dropDuplicates再猜最新'];newcorrect=0
    else:
        t=l['tasks'][2];code='shared.persist(StorageLevel.MEMORY_AND_DISK_DESER)\nshared.take(1)'
        prompt='能保证全部分区已缓存吗？';choices=['能，看到一条即全量','不能，只请求少量结果','persist自动永久落盘'];correct=1;why='登记策略和请求部分结果都不证明所有分区已物化；实际块与复用计划需另查。'
        newcode='base.persist(StorageLevel.MEMORY_AND_DISK_DESER)\nprint(base.storageLevel)\n# 无action';newprompt='哪种结论有证据？';newchoices=['全部数据已缓存','所有复用必提速','只确认登记级别，实际块还需执行与观察'];newcorrect=2
    knowledge=t['knowledgeIds'][0];rid=slug+'/transfer'
    t['remediation']=dict(id=rid,knowledgeId=knowledge,title='换一份材料再判断',intro='复用本步规则，不沿用上一份答案。',code=code,prompt=prompt,field=dict(id='answer',label='变式判断',correctOptionId=f'r{correct}',options=[dict(id=f'r{i}',text=x,feedback=why if i==correct else '回到本步的阶段与规则，再核对新材料。') for i,x in enumerate(choices)]),insight=why)
    delayed['items'].append(dict(id=rid+'-delayed-v1',slug=slug,taskId=t['id'],knowledgeId=knowledge,title=l['title']+' · 隔天换材料',code=newcode,prompt=newprompt,options=[dict(id=f'd{i}',text=x) for i,x in enumerate(newchoices)],correctOptionId=f'd{newcorrect}',explanation=why))

all_lessons={p.stem:json.loads(p.read_text(encoding='utf-8')) for p in (content/'lessons').glob('*.json')};all_lessons.update(lessons)
apply_continuity(all_lessons,guides,delayed);delayed['items'].sort(key=lambda i:(i['slug'],i['id']))
specs=extension_specs(lessons)
seed_path=ROOT/'backend/app/course_seed.json';seed=json.loads(seed_path.read_text(encoding='utf-8'))
for spec in specs:
    slug=spec['lesson']['slug'];level=next(lv for lv in seed['levels'] if any(l['slug']==spec['after'] for l in lv['lessons']))
    level['lessons']=[l for l in level['lessons'] if l['slug']!=slug]
    index=next(i for i,l in enumerate(level['lessons']) if l['slug']==spec['after'])
    level['lessons'].insert(index+1,spec['lesson'].copy())
    for i,l in enumerate(level['lessons']):l['order_index']=i

# Two purpose-separated materials for each of five objectives, not ten new concepts.
families={WINDOW:[
 ('shape','三条订单执行SUM(amount) OVER(PARTITION BY city)，无其他筛选，输出几行？','五条订单用窗口补上每城总额，原行数怎样？',['3行','5行'],['每城市只留一行','全表只剩一行','只有总额没有明细'],'窗口在组内计算并把值附给明细，不像GROUP BY收拢为每组一行。'),
 ('stable','时间并列时要求稳定选最新整行，应补什么？','单按更新时间无法区分两行，要稳定选一条应怎样？',['明确唯一且稳定的并列排序键','时间后加约定的唯一event_id排序'],['任取一行再宣称最新','分别MAX各列拼成结果','依赖dropDuplicates保留首行'],'完整排序规则决定选哪条整行，业务键的次序需明确约定。'),
 ('filter','Spark3.5.7中，如何筛每用户窗口序号为1？','先算ROW_NUMBER，再保留第一条，查询分层怎样写？',['内层计算rn，外层WHERE rn=1','CTE编号，外层按rn过滤'],['同层WHERE直接依赖窗口别名','只用全表LIMIT 1','用HAVING替代所有窗口计算'],'外层才能使用内层窗口结果，CTE不自动物化。'),
 ('topn','north三单、south一单，每城至多Top2，共几单？','A四单、B一单，每组至多两条，共几条？',['3单','3条'],['全表只留2条','必须补成4条','所有明细均不筛'],'ROW_NUMBER分组重启，rn<=2保留每组至多两条，少于两条不造行。'),
 ('ties','100、100、90按分数DENSE_RANK取前两档，保留几人？','9、9、8按值DENSE_RANK<=2，保留几行？',['3人','3行'],['固定2行','只保留第一名','固定只保留一个并列者'],'DENSE_RANK按不同排序值连续分档，并列可使输出行数超过N。')],
 CACHE:[
 ('intent','persist后只读storageLevel，确认了什么？','没有action，只调用DataFrame.cache后能确认什么？',['登记了持久化策略','请求了默认缓存策略'],['所有分区已经物化','生产性能已固定提升','数据已永久写出'],'持久化登记与实际物化分开，执行与观察才提供进一步证据。'),
 ('level','Spark3.5.7 DataFrame.cache默认级别是什么？','3.5.7 DataFrame.persist()未传级别时默认是哪项？',['MEMORY_AND_DISK_DESER','MEMORY_AND_DISK_DESER'],['MEMORY_ONLY且与RDD始终相同','所有块只存Driver列表','永久外部数据表'],'DataFrame默认级别与RDD不可混用；允许内存/磁盘不保证全驻内存。'),
 ('evidence','如何判断登记的缓存真的被目标查询采用？','同源新查询一定复用已缓存结果吗，应怎样确认？',['核对实际缓存块和目标执行计划','核对复用关系、块占用与计划'],['只看变量名含cached','只看storageLevel非空','只看原始文件路径相同'],'策略、实际数据和目标查询采用情况分别验证，计划不是性能保证。'),
 ('release','cached.unpersist(blocking=True)主要做什么？','小型受控实验结束，怎样等待自己拥有的缓存块释放？',['释放缓存并等待块删除','调用unpersist(blocking=True)'],['删除原始数据文件','把缓存永久写成业务产物','阻止以后按来源重算'],'unpersist不删除查询定义或源数据，也不等于JVM立刻归还全部OS内存。'),
 ('scope','报告B抛错，如何保证走到缓存清理路径？','异常时也需要释放本段缓存，结构应怎样组织？',['用finally清理本段拥有的缓存','将本段unpersist放进finally'],['只在成功路径释放就足够','吞掉异常宣称交付成功','任何cache都无需成本核对'],'明确资源生命周期，清理不修复业务错误，也不自动保证缓存收益。')]}
bank=[];ordinal=0
for slug,items in families.items():
    qs=[]
    for j,(key,prompt_a,prompt_b,answers,wrong,why) in enumerate(items):
        for i,prompt in enumerate([prompt_a,prompt_b]):
            correct=(j+i+(0 if slug==WINDOW else 2))%4;options=wrong.copy();options.insert(correct,answers[i]);ordinal+=1
            purpose='assessment' if i==0 else ('review' if j<3 else 'remediation')
            qs.append(dict(key=f'{slug}/{key}/{purpose}-v1',knowledge_id=f'{slug}/{key}',purpose=purpose,type='single_choice',prompt=lessons[slug]['title']+'：'+prompt,options=options,correct_index=correct,explanation=why,dimension=['concept','apply','mechanism','debug','transfer'][j]))
    bank.append(dict(lesson_slug=slug,questions=qs))

outputs={content/'lessons'/f'{slug}.json':l for slug,l in all_lessons.items() if slug in lessons or slug in ['l2-sort-dedup','l3-groupby-having','l3-joins-intro','l7-executor-memory','l7-shuffle-partitions']}
outputs.update({content/'standardGuides.json':guides,content/'delayedChecks.json':delayed,seed_path:seed,ROOT/'backend/app/course_extensions.json':dict(version=1,lessons=specs),ROOT/'backend/app/extension_reviewed_bank.json':dict(version=1,lessons=bank)})
for path,data in outputs.items():
    text=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
    if '--check' in sys.argv:assert path.read_text(encoding='utf-8')==text,str(path)
    else:path.write_text(text,encoding='utf-8')
print('PASS two ordered lessons / 16 steps / 20 purpose questions / two remedies and delayed materials')
