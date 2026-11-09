"""Two explicitly authored courses and the adjacent continuity edits."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]
WINDOW='l3-window-topn'
CACHE='l7-cache-lifecycle'
SOURCES={WINDOW:'https://spark.apache.org/docs/3.5.7/sql-ref-syntax-qry-select-window.html',
         CACHE:'https://spark.apache.org/docs/3.5.7/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.persist.html'}


def task(slug,key,title,intro,code,prompt,choices,correct,feedback,body,boundary):
    ident=slug+'/'+key
    return dict(id=ident,title=title,intro=intro,code=code,prompt=prompt,knowledgeIds=[ident],ability=title,insight=body,
      fields=[dict(id='answer',label='你的判断',correctOptionId=f'o{correct}',options=[dict(id=f'o{i}',text=text,feedback=feedback[i]) for i,text in enumerate(choices)])],
      reading=dict(id=ident+'/reading',title=title,sectionTitle='本课模型',startMarker='【先用人话理解】',endMarker='【一个直观的心智模型】',connection=body,boundary=boundary))


def build():
    lessons={};s=WINDOW;ts=[]
    def q(*args):ts.append(task(s,*args))
    q('keep-rows','汇总一组，还是给每行补一列',
      '上一课GROUP BY把每个城市收成一行。现在运营要保留每张订单，同时带上所属城市总额。窗口计算在相关行之间计算，再把结果附到各行。',
      "-- 输入：north/30、north/20、south/8\nSELECT city, amount,\n SUM(amount) OVER (PARTITION BY city) AS city_total\nFROM orders",
      '没有其他筛选时，这段结果有几行？',['2行，每城市一行','3行，保留三张订单','1行，全表总额'],1,
      ['那是GROUP BY城市的输出形状。','对，north两行各带50，south一行带8。','窗口没有把全表收成一行。'],
      'OVER定义窗口；PARTITION BY city把同城行作为逻辑计算组。这里没有窗口ORDER BY，SUM覆盖整个城市组，原订单行仍保留。',
      '窗口分组不是写目录partitionBy，也不承诺物理分区布局；本课先固定业务分组。加ORDER BY后的默认窗口帧可能改变聚合含义，本课不把它一概当整组总额。')
    q('number','每个城市从一号重新排',
      'ROW_NUMBER给组内每行一个连续序号。先按city分组，再按金额降序、订单号升序明确顺序。',
      "-- north: a/70,b/40；south: c/90\nROW_NUMBER() OVER (\n PARTITION BY city ORDER BY amount DESC, id ASC\n) AS rn",
      '订单a、b、c的rn分别是？',['1、2、3','1、1、1','1、2、1'],2,
      ['漏掉了按城市重新编号。','同组不同行的ROW_NUMBER不相同。','对，south独立从1开始。'],
      'PARTITION BY回答“在哪组里比”，ORDER BY回答“按什么顺序比”。ROW_NUMBER从1开始，每个组独立编号。',
      '窗口内的排序用于计算序号，不等于最终结果展示全局有序；展示还需外层ORDER BY。')
    q('stable','最新时间相同，还得约定选谁',
      'L2已知道dropDuplicates不保证保留最新整行。现在按用户保留一条最新事件：event_id唯一且非空，时间相同时约定event_id降序选较大者。',
      "-- u1: e10/time=5/status=old；e11/time=5/status=new\nROW_NUMBER() OVER (PARTITION BY user_id\n ORDER BY event_time DESC NULLS LAST, event_id DESC) AS rn",
      'u1保留rn=1，按这个约定选谁？',['e11，按完整排序规则','任意一行，规则没有作用','把两行status拼接'],0,
      ['对，时间并列由唯一event_id打破。','最后一个排序键已明确。','窗口选行不自动合并业务字段。'],
      '“最新”先定义时间口径，并给并列补充稳定且唯一的排序键。用ROW_NUMBER选整行，才能保留同一条记录上的字段；不能分别MAX每列拼出不存在的行。',
      'event_id的顺序是业务约定，不自动代表真实发生先后；缺少稳定键时不能承诺每次选中同一条。')
    q('filter','先生成序号，再筛第一行',
      '序号要先计算出来。用CTE（给子查询起一个临时名字）分两层表达：内层编号，外层过滤。',
      "WITH numbered AS (\n SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id\n  ORDER BY event_time DESC NULLS LAST,event_id DESC) AS rn\n FROM events\n)\nSELECT * FROM numbered WHERE rn = 1",
      '为什么不在同一层SELECT的WHERE里直接用rn？',['WHERE只能比较字符串','同层WHERE不能依赖尚未算出的窗口结果','窗口禁止后续过滤'],1,
      ['WHERE支持多种条件。','对，用子查询把计算阶段分开。','外层过滤正是这里需要的。'],
      'CTE只组织查询表达，不自动缓存或保存数据。先计算窗口列，再让外层WHERE筛选；这里使用Spark3.5.7支持的两层写法。',
      '不要依赖其他SQL方言的QUALIFY语法；本课不把CTE当物化保证。')
    q('topn','每组两单，不是全表两单',
      '运营要每城市金额最高的至多两张订单；不足两张则保留实际存在的订单，不补假行。',
      "-- north:70,40,10；south:90\n-- 已按city分组、amount DESC和唯一id编号\nSELECT * FROM numbered WHERE rn <= 2",
      '两个城市合计输出几张订单？',['2张，等同LIMIT 2','4张，每组必须补满','3张，north两张、south一张'],2,
      ['LIMIT 2只限制整份结果，不等同每组Top2。','不足不补造订单。','对，分别按组筛选已有序号。'],
      'ROW_NUMBER配rn<=N表达每组至多N行，并列也要按已定义的次序取舍。全表ORDER BY/LIMIT与每组TopN是不同问题。',
      '如果业务要求并列名次全部保留，先重新明确“N”指行数还是名次，不要继续套固定行数方案。')
    q('rank','同分算并列时，名次怎样走',
      '三名选手分数100、100、90。现在按分数相同视为并列，排名窗口只按score降序，不添加唯一id打破业务并列。',
      'RANK() OVER (PARTITION BY team ORDER BY score DESC)\n-- 同队分数：100、100、90',
      '三人的RANK是哪组？',['1、1、3','1、2、3','1、1、2'],0,
      ['对，并列占用两个位置，下一名跳到3。','这是逐行序号，不是同分并列名次。','这是DENSE_RANK的连续档位。'],
      'RANK把相同排序值视为并列，并在其后跳过相应位置；DENSE_RANK也并列，但下一档不跳号。按这些名次筛选<=N时，行数可能超过N。',
      '排名的别名在示例中可自定；若在排名ORDER BY中加入唯一id，同分行便不再按该完整排序键并列。')
    q('dense','取前两档成绩，需要哪种名次',
      '仍是100、100、90。业务要前两种不同分数的所有人，不能为了凑两行丢掉一个并列者。',
      'DENSE_RANK() OVER (PARTITION BY team ORDER BY score DESC) AS tier\n-- 外层WHERE tier <= 2',
      '会保留几人？',['2人，名次就是行数','1人，只保留第一个100','3人，100和90都是前两档'],2,
      ['这里限制的是分数档位。','相同分数两人都应保留。','对，档位1、1、2均达标。'],
      '固定行数用有完整次序的ROW_NUMBER；保留前N档不同排序值可用DENSE_RANK；竞赛式并列名次可用RANK。先说清业务再选函数。',
      '多列排序时“相同”指整个排序值组合相同，而不仅第一列。')
    q('null-latest','缺时间的事件，别默默选成最新',
      '新用户u9有e1/time=NULL、e2/time=7。约定已知时间优先，全部时间未知时再用唯一event_id降序决定。',
      'ORDER BY event_time DESC NULLS LAST, event_id DESC\n-- 选每用户ROW_NUMBER=1',
      'u9应选哪条？',['e1，因为NULL总是最新','e2，因为已知时间按约定优先','不保留任何u9事件'],1,
      ['NULL不是一个自动更大的业务时间。','对，缺失时间规则明确写入排序。','仍有符合选行契约的记录。'],
      '把缺失与并列规则写进窗口，换数据才能继续成立。选行后再做JOIN补属性，仍要检查维表键唯一，不能让已选一行在连接后再次放大。',
      '本题user_id非空；若允许NULL用户键，窗口会把它们放同一组，必须另行约定是否应排除或区分。')
    lessons[s]=dict(slug=s,version=1,title='窗口：每组Top N与最新整行',mission='从上一课聚合出发：同样按组计算，这次保留每张明细，并为后续JOIN准备明确的记录粒度。',correction='',source=SOURCES[s],next='下一课JOIN会给已选记录补用户属性。窗口负责组内计算与选行，连接负责跨表匹配，二者都要验证输出粒度。',tasks=ts)

    s=CACHE;ts=[]
    q('worth','先圈出真正会被重复用的结果',
      '上一课分清了执行与存储的共享内存。这次要让两份报告复用同一段昂贵清洗结果；两份报告的筛选条件不同，但清洗规则相同。',
      'raw → expensive_clean → clean\nclean → report_A\nclean → report_B',
      '优先评估在哪个位置持久化？',['每个中间变量都缓存','共享的clean，并核对容量与复用次数','只缓存report_A的列名'],1,
      ['缓存也占资源，不应全标记。','对，先明确可复用边界再测收益。','列名不是共享计算结果。'],
      'persist是让计算结果可复用的策略，先看是否重复使用、重算多贵、缓存多大。它不把任何慢作业自动变快，也不替代输入与结果契约。',
      '两份语义不同的清洗不能仅因变量名相同就视为同一个可复用结果。')
    q('level','明确这次说的是DataFrame缓存',
      'Spark3.5.7中，DataFrame.cache()使用默认持久化级别，persist(level)可指定级别。RDD的默认值不能直接套到DataFrame。',
      'from pyspark import StorageLevel\ncached = clean.persist(StorageLevel.MEMORY_AND_DISK_DESER)\n# 另一选择：clean.cache() 使用DataFrame默认级别',
      '本课这个级别允许怎样存储？',['只在Driver列表里存放','永远完全驻留内存','允许内存和磁盘，不能保证全在内存'],2,
      ['持久化不是把明细搬到Driver。','级别不提供这种容量保证。','对，容量与运行条件仍影响实际存储。'],
      '3.5.7的DataFrame cache/persist默认MEMORY_AND_DISK_DESER；persist可以显式选级别。级别描述允许的存储方式，实际缓存状态还要观察。',
      '不要据名字推断任意Python对象的布局；RDD与DataFrame以及不同版本的默认值分别核对。')
    q('materialize','登记缓存，不等于已经把数据装满',
      '调用persist后，查询尚未实际遍历数据。惰性规则仍在：需要一个结果请求驱动计算。',
      'cached = clean.persist(StorageLevel.MEMORY_AND_DISK_DESER)\n# 还没有action\n# 可在需要时：cached.count()',
      '此时能保证全部分区已经物化吗？',['不能，persist先登记策略','能，调用即全部读完','能，Python变量出现就等于落盘'],0,
      ['对，实际块由后续执行需求填充。','没有完整计算请求。','变量不是存储证据。'],
      'count会请求全量计数，常用于驱动物化；take只请求有限结果，不能据此认定所有分区都已填充。是否仍完整缓存还受逐出、失败和容量影响。',
      'count本身有成本，不能为了缓存再无条件多跑一次；应把预热计入整体实验。')
    q('observe','设置成功与真正复用要看两种证据',
      'cached.storageLevel可读到登记的级别。还要检查Storage页中的实际缓存块，并对执行后的查询观察是否使用缓存扫描。',
      'print(cached.storageLevel)\ncached.count()\nreport = cached.groupBy("region").count()\nreport.collect()  # 本课只有极小教学报告\nreport.explain()',
      '哪组证据更完整？',['只看storageLevel非空','实际块占用、缓存扫描与运行条件一起核对','只看变量叫cached'],1,
      ['登记不等于所有数据已存好。','对，策略、实际数据和采用路线分开看。','名称不是运行证据。'],
      '常见计划会显示InMemoryTableScan等缓存线索，Storage页展示缓存占用；这些仍不是固定提速证明。检查目标查询和版本，并在同条件下测量整体成本。',
      '小报告collect用于教学核对，不是允许收集海量明细；具体计划包装可能随版本变化。')
    q('scope','别把缓存当成永久快照或新查询的保证',
      '同一cached变量供两份报告使用时，要保持来源与清洗语义一致。现在另建一个不同过滤规则的查询，不能只因数据源相同就假定自动命中。',
      'cached = expensive_clean(raw).persist(...)\nother = raw.filter("amount > 999")\n# 同源不等于同一个缓存结果',
      '可靠做法是什么？',['所有同源查询都必然命中','缓存相当于持久化数据产品','核对复用关系、结果与实际计划'],2,
      ['缓存匹配不是按文件名或变量名保证。','缓存不是永久交付或隔离级别承诺。','对，明确复用对象并用证据确认。'],
      '复用逻辑必须保持正确，缓存也不替代数据版本或快照契约。需要稳定交付时，应设计正式数据产物，而非依赖缓存永远存在。',
      '本课不假定缓存如何响应所有外部源变更；生产需另定输入版本与刷新规则。')
    q('release','两份报告做完，把缓存还回去',
      '缓存不再使用时，unpersist解除持久化并移除对应缓存块；不是删除原始文件，也不删除DataFrame计算定义。',
      'cached.unpersist(blocking=True)\n# blocking=True：等待缓存块删除完成\n# 以后仍可按有效来源重新计算cached',
      '这一步的准确含义是什么？',['释放缓存，保留查询定义和原始来源','删除所有原始订单文件','把清洗结果永久保存'],0,
      ['对，释放资源和删除业务输入不同。','unpersist不是删文件接口。','没有写出正式数据产物。'],
      'unpersist默认blocking=False；需要等待块移除的受控实验可使用True。之后再次执行仍可能重算，原数据可用性与逻辑规则依旧重要。',
      '不能把缓存块释放等同于JVM立刻把全部内存还给操作系统，其他查询共享同一缓存关系时也要协调释放时机。')
    q('finally','中途报错，也要走到清理步骤',
      '报告A成功，报告B失败。释放不应该只写在“两个报告都成功”那条路径上。finally会在try结束时执行，包括异常路径。',
      'cached = clean.persist(StorageLevel.MEMORY_AND_DISK_DESER)\ntry:\n    make_report_a(cached)\n    make_report_b(cached)\nfinally:\n    cached.unpersist(blocking=True)',
      'finally在这里主要保护什么？',['自动修复报告B的业务错误','让失败任务自动变成成功','异常路径也会尝试释放本段负责的缓存'],2,
      ['它负责清理，不修复业务逻辑。','异常仍应正确报告。','对，明确资源所有权和生命周期。'],
      '让缓存创建、复用与释放处于明确的作用域，异常也要清理；不要吞掉原异常假装交付成功。本课小任务由该作用域拥有缓存，不随意释放其他任务共享资源。',
      '进程崩溃或清理本身失败仍需运行环境处理，finally不是一切故障的绝对保证。')
    q('fair-test','比较方案，预热与冷启动要算同一本账',
      '原方案统计了两份报告全流程；新方案只报告缓存热好后第二份的时间，省略首次清洗、物化与释放。',
      '完整对照范围：\n读取/清洗 → 缓存登记与物化 → A/B报告 → 释放\n固定输入、资源与结果；记录冷热状态',
      '能直接把这个差值称为全流程加速吗？',['不能，先统一范围并重复测量','能，只挑最快一段','能，cache方法名就是证据'],0,
      ['对，复用收益要扣除建立与管理成本。','选择性计时不能代表整体。','接口采用不等于性能收益。'],
      '接下来调分区时继续采用相同方法：明确单一改动，保留完整时间与资源证据，保持结果不变。缓存与分区都应由需求和测量决定。',
      '本课不提供固定倍数的性能保证；正式报告的缓存冷热条件应可复核。')
    lessons[s]=dict(slug=s,version=1,title='缓存实践：从复用到释放',mission='上一课理解了执行与存储内存的共享边界；这一课把模型变成DataFrame的缓存生命周期，再进入分区实验。',correction='',source=SOURCES[s],next='下一课调Shuffle分区时，继续记录缓存冷热状态。先区分复用是否有效，再比较每份工作的大小和并发，避免把两个变量混在一起。',tasks=ts)
    return lessons


def apply_continuity(lessons,guides,delayed):
    edits={
      'l2-sort-dedup':(4,'next','在L3的聚合课后，窗口与每组Top N会具体练习如何按完整排序规则保留最新整行；目前先分清去重与选行。'),
      'l3-groupby-having':(2,'next','下一课窗口继续按组计算，但保留每条明细；先对比GROUP BY收拢行与OVER为每行补信息，再处理每组Top N。'),
      'l3-joins-intro':(3,'mission','刚才窗口已练过组内编号与选行；现在跨表补字段，先认清订单和用户属性，再检查连接是否放大或丢失记录。'),
      'l7-executor-memory':(3,'next','下一课缓存实践把M/R与逐出模型落到persist、物化、观察、复用和unpersist；先学会管理缓存生命周期，再调分区。'),
      'l7-shuffle-partitions':(2,'mission','上一课已完成缓存的建立、观察与释放；这一课保持缓存冷热条件可比，再根据任务大小、热点和并发选择分区实验。')}
    for slug,(version,key,text) in edits.items():
        if slug in lessons:
            lessons[slug]['version']=max(lessons[slug]['version'],version);lessons[slug][key]=text
    guides['version']=max(guides['version'],6)
    delayed['version']=max(delayed['version'],6)
    from question_polish import apply as apply_question_polish
    apply_question_polish(lessons,guides,delayed)


def extension_specs(lessons):
    specs=[]
    for slug,anchor,title,minutes in [(WINDOW,'l3-groupby-having','窗口函数：每组Top N与最新整行',18),(CACHE,'l7-executor-memory','缓存实践：物化、复用与释放',18)]:
        l=lessons[slug]
        explanation='【先用人话理解】\n\n'+l['mission']+'\n\n【一个直观的心智模型】\n\n'+'\n\n'.join(t['title']+'：'+t['insight'] for t in l['tasks'])+'\n\n【边界与验证】\n\n'+'\n'.join(t['reading']['boundary'] for t in l['tasks'])
        content=dict(explanation=explanation,examples=[dict(title=t['title'],code=t['code'],note=t['insight']) for t in l['tasks']],key_points=[t['insight'] for t in l['tasks']],common_mistakes=[dict(mistake='忽略本步适用边界',why=t['reading']['boundary'],fix=t['insight']) for t in l['tasks']],review=l['mission'],problem='按真实规则推演，再用换材料练习验证。',preview=l['next'])
        specs.append(dict(after=anchor,lesson=dict(slug=slug,title=title,description=l['mission'],objective='完成本课八步推演，能解释关键规则，并在新材料上选择与实现正确流程。',estimated_minutes=minutes,prerequisites=anchor,content=content)))
    return specs
