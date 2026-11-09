"""Explicit teaching bridges shared by the three authoring sources.
Apply after baseline authoring. Stable old tasks stay intact; revisions get separate progress.
"""
from copy import deepcopy

TUNING='https://spark.apache.org/docs/3.5.7/tuning.html#memory-management-overview'
REVISIONS={
 'l1-what-is-rdd':2,'l1-action':2,'l1-lazy-evaluation':2,'l1-why-dataframe-replaces-rdd':2,'l1-rdd-exercise':2,
 'l2-what-is-dataframe':3,'l2-comprehensive':3,
 'l3-what-is-spark-sql':2,'l3-joins-intro':2,'l3-comprehensive':2,
 'l4-why-explain':2,'l4-logical-vs-physical':2,'l4-explain-api':2,'l4-read-plan':2,'l4-wholestage-codegen':2,'l4-comprehensive':2,
 'l5-what-is-partition':2,'l5-shuffle-trigger-operators':2,'l5-comprehensive':2,
 'l6-what-is-join':2,'l6-join-strategies-overview':2,'l6-broadcast-hash-join':2,'l6-join-data-skew':2,'l6-comprehensive':2,
 'l7-what-is-tuning':3,'l7-executor-memory':2,
}


def insert(lesson,guides,key,before,title,intro,code,prompt,options,correct,feedback,body,boundary,table=None):
    ident=lesson['slug']+'/bridge-'+key
    field=dict(id='answer',label='你的判断',correctOptionId=f'b{correct}',
               options=[dict(id=f'b{i}',text=text,feedback=feedback[i]) for i,text in enumerate(options)])
    # Stable identity with a mix of answer positions; do not rely on a positional key.
    field['options']=field['options'][1:]+field['options'][:1]
    reading=deepcopy(lesson['tasks'][0]['reading'])
    reading.update(id=ident+'/reading',title=title,connection=body,boundary=boundary)
    task=dict(id=ident,title=title,intro=intro,code=code,prompt=prompt,fields=[field],
              knowledgeIds=[ident],insight=body,ability=title,reading=reading)
    if table:task['table']=table
    index=next(i for i,t in enumerate(lesson['tasks']) if t['id']==lesson['slug']+'/'+before)
    lesson['tasks'].insert(index,task)
    guides['lessons'][lesson['slug']]['sections'].append(dict(id=ident,title=title,body=body,boundary=boundary))
    return task


def apply(lessons,guides,delayed):
    def add(slug,*args,**kwargs):
        if slug in lessons:return insert(lessons[slug],guides,*args,**kwargs)
    def expand(slug,key,intro,body):
        if slug not in lessons:return
        task=next(t for t in lessons[slug]['tasks'] if t['id']==slug+'/'+key)
        task['intro']=intro
        section=next(s for s in guides['lessons'][slug]['sections'] if s['id']==task['id'])
        section['body']=body
        task['reading']['connection']=body
    # Remove only this layer's additions when reapplying to a published lesson.
    for slug,l in lessons.items():
        if slug not in REVISIONS:continue
        l['tasks']=[t for t in l['tasks'] if not t['id'].startswith(slug+'/bridge-')]
        guide=guides['lessons'][slug]
        guide['sections']=[s for s in guide['sections'] if not s['id'].startswith(slug+'/bridge-')]
        l['version']=max(l['version'],REVISIONS[slug])

    add('l1-what-is-rdd','data-parts','parts','先看数据怎样分成几份',
        'RDD 可以先理解为：一批元素，加上“分成哪些份、怎样计算”的描述。每份叫分区。Driver 负责组织，执行端处理这些份；分区不是机器。',
        '# 教学分法，不模拟真实分区器\n分区 A：[2, 4]\n分区 B：[6, 8]',
        '这里整批数据有几个元素、几个分区？',['4 个元素、2 个分区','2 个元素、4 个分区','必须有 2 台机器'],0,
        ['对，元素是数据，分区是这些数据的份。','把元素与份数弄反了。','分区不等于机器。'],
        '把“元素”“分区”“机器”分开：四个数可分为两份，两份可由同一台机器处理。接下来才看 parallelize 如何建立这个描述。',
        '示意分法不承诺 Spark 自动采用相同的具体布局；本章假设你能读懂基础 Python 列表与函数。')
    expand('l1-what-is-rdd','immutable',
        '原 rdd 表示2、4、6。map 是给每个元素应用加工函数；lambda x:x+1 表示输入一个数，输出它加一。下一课会专门拆解这些转换。',
        'map 描述一个新 RDD，不把旧定义就地改掉。原查询仍表示2、4、6，新查询表示3、5、7；变量赋值也不是把整份原数据永久改写。')
    expand('l1-what-is-rdd','recover',
        '缓存是保留已经算过的数据，供之后复用。现在某份缓存丢失，但上游文件还在、加工函数可重算；血缘就是记录“从哪来、怎么算”的依赖关系。',
        '当所需上游仍可读取且计算能重做时，可以沿血缘重新计算丢失分区。血缘是重算依据，不是免费保存全部结果的备份；重算仍花时间与资源。')
    expand('l1-action','foreach',
        '闭包是函数连同它引用的外部变量。这里 lambda 引用了 seen；发送给任务的是序列化后的函数与所需状态，不是一个跨进程共享列表。',
        'Driver 的 seen 与任务使用的状态不能当成同一份共享结果。foreach 执行函数但不把各任务列表合并返回；有界预览用 take，计数用 count。外部副作用还需考虑重试。')
    expand('l1-lazy-evaluation','recovery',
        '副作用指写外部系统等会改变环境的操作。幂等指同一次业务操作重复执行，效果仍与一次一致。这里的外部写入不属于 Spark 原子提交，任务可能重试。',
        '血缘记录如何重算数据，不是外部系统的事务日志。若任务重试再次写入，要由幂等键、目标系统事务或适合的提交协议控制重复；不能靠“可重算”推断只写一次。')
    expand('l1-why-dataframe-replaces-rdd','optimizer',
        '优化器会在保持结果含义的前提下寻找执行方式。Spark SQL 的优化器叫 Catalyst；本课只需知道它能分析结构化列与关系，详细计划留到 L4。',
        'DataFrame/SQL 的列和关系表达向优化器暴露计算含义。任意 Python 函数体通常没有同样的可分析信息；不必现在掌握 Catalyst 的内部规则，也不能据此断言某接口总是更快。')
    add('l1-rdd-exercise','key-value','normalize','把词装进“键、值”小卡片',
        '词频要回答每个词出现几次。先把每次出现写成 (词, 1)：词是用来找同类的键，1 是本次出现贡献的值。这种二元组组成的 RDD 常叫 Pair RDD。',
        "tokens = sc.parallelize(['Spark', 'SQL', 'spark'])\npairs = tokens.map(lambda w: (w.lower(), 1))",
        '小写归一之后，三张卡片是什么？',
        ["('spark',1)、('sql',1)、('spark',1)","('spark',2)、('sql',1)",'只剩一个 spark'],0,
        ['对，还只是逐词制卡，没有合并。','这是之后按键求和的结果。','不能丢掉重复出现的贡献。'],
        'map 在这里为每个词生成一张卡片，不合并重复键。键决定按什么归类，值记录每次贡献；接下来才能按键合并。',
        '这一步用小词列表建立 RDD 来观察形状，完整实现先由 flatMap 从行生成词。')
    add('l1-rdd-exercise','reduce-key','sum','同名卡片怎样汇成一个次数',
        'reduceByKey 的意思是“按键归类，再用给定函数合并值”。lambda a,b:a+b 把同词的两个计数相加，直到每个词得到一份总量。',
        "pairs: ('spark',1), ('sql',1), ('spark',1)\npairs.reduceByKey(lambda a,b: a+b)",
        '结果中 spark 和 sql 的计数应分别是多少？',['都是 1','spark=2，sql=1','spark=3，sql=3'],1,
        ['重复出现也贡献一次。','对，只合并相同键的值。','不能把不同词混在一起。'],
        '按键求和不是对原始词去重：两个 spark 贡献相加。数据可能跨分区，Spark 负责把同键贡献汇合；L5 再展开局部合并和 Shuffle 的代价。',
        '这里使用整数加法；不能把任意不可重组的函数都当作安全规约。')

    for slug,before in [('l3-joins-intro','inner'),('l6-what-is-join','pairs')]:
        add(slug,'fact-dimension',before,'先认清两张表各记什么',
            '订单表记录一次次购买事件，这里称事实表；用户表记录用户的地区等属性，这里称维表。连接键是两表用来判断对应关系的字段，本例为 user_id。',
            '订单：o1 / u1 / 50元\n用户：u1 / north\n目标：给订单补上地区',
            '这条订单该从哪里取得地区？',['按 user_id=u1 找用户属性','按两张表的行号相同配对','把金额 50 当作用户编号'],0,
            ['对，按约定键找对应属性。','行序没有定义用户对应关系。','金额不是这里的连接键。'],
            '“补维”就是给事件补上属性。事实表与维表是本业务里的角色，不保证某张表总是大或总是小，也不自动保证维表键唯一。',
            '先建立键的含义，再决定未匹配行与重复匹配如何处理。L6 在 L3 的匹配基础上研究执行策略。')
    expand('l6-what-is-join','pairs',
        '订单 o1 的用户是 u1、金额 50。用户属性表中 u1 同时有 north、south 两条记录；按 user_id 相等匹配，因此同一订单能产生两个行对。',
        '连接会为每个满足条件的行对输出一行。此例得到 o1/u1/50/north 和 o1/u1/50/south，两行再求金额得到 100。“匹配基数”就是这种一对一、一对多或多对多的数量关系。')
    if 'l6-what-is-join' in lessons:
        lessons['l6-what-is-join']['tasks'][1]['table']=dict(caption='连接前：一条事实，两条同键属性',columns=['来源','订单','user_id','金额','地区'],rows=[['订单','o1','u1',50,'—'],['用户','—','u1','—','north'],['用户','—','u1','—','south']])

    add('l4-why-explain','plan-map','evidence','把前面的查询换成一张路线图',
        'L2/L3 已经写过筛选和聚合。执行计划展示 Spark 准备如何完成它们：Scan 读输入，Filter 留下符合条件的行，Aggregate 做分组计算。先读动作含义，再认节点名字。',
        '# 简化教学路线，沿箭头读\nScan 读取订单 → Filter 留下正金额 → Aggregate 按地区求和',
        '哪一步落实“只统计正金额”？',['Scan','Filter','Aggregate'],1,
        ['读取不自动实现这个业务条件。','对，它负责筛行。','聚合负责分组计算。'],
        '计划可以理解为查询的执行路线。它与用户代码有关，但不必逐行对应；物理计划说明采用哪些操作，不直接给出各操作实测耗时。',
        '这是一条简化示意，不是完整 Spark explain 输出。Exchange 等交接节点先认用途，L5 再推演机制。')
    expand('l4-logical-vs-physical','route',
        'L3 已学按键匹配。这里的维表是补用户属性的表。BroadcastHashJoin、SortMergeJoin 是实现同一匹配需求的两条路线；本步只辨认“结果含义”和“执行路线”，L6 再拆算法。',
        'INNER/LEFT 等逻辑类型约定哪些匹配与未匹配行保留；BroadcastHashJoin、SortMergeJoin 等物理节点描述如何计算。现在无需背算法细节，先知道同一含义可能由不同路线完成。')
    expand('l4-explain-api','cost',
        'sizeInBytes 是计划里的大小估计。广播指把一侧数据复制给参与匹配的执行端；哈希结构是按键查找的结构。这里只区分估计与实测，容量和算法在 L6 展开。',
        '计划估计帮助选择路线，却不是运行峰值内存：实际构建结构、并发和对象开销仍需测量。不要把 sizeInBytes、文件字节数与可用内存当成同一口径。')
    expand('l4-read-plan','exchange',
        'Exchange 表示数据交接。ShuffleExchange 通常为满足下游分布重新组织数据；BroadcastExchange 将一侧数据广播。先区分交接目的，L5 会用两份地区金额推演重分发。',
        '名字都有 Exchange 不代表动作相同。按键汇合与复制小关系是不同路线，不能只数这个单词就给出固定 Shuffle 次数。')
    expand('l4-read-plan','adaptive',
        'AQE 是自适应查询执行：运行中拿到统计后，可调整适用的执行路线。isFinalPlan=false 表示当前所见还不是最终路线；L7 再研究条件和控制。',
        '把“计划执行前的选择”和“运行后的实际路线”分开。AQE 不保证每条查询都改变，也不会修复错误的业务规则；核对同一目标查询完成后的证据。')
    expand('l4-read-plan','markers',
        'Task 是处理某份数据的执行任务；Stage 是一组可共同推进的任务；Job 是一次计算请求触发的调度工作。此处先分清名字，后面的调度课再展开。',
        '计划中的 *(N) 是 WholeStageCodegen 分组线索，不是调度 Stage 编号。生成代码的分组与运行中的 Job/Stage/Task 属于不同视角。')
    expand('l4-wholestage-codegen','tungsten',
        'spill 指某些算子在内存不足等条件下，把中间计算数据暂存到磁盘继续处理。紧凑布局可降低部分占用，但数据量、单份工作集和并发仍影响是否 spill。',
        '减少每条记录开销不等于内存无限。spill 与缓存块逐出是不同事件；本课先认识临时落盘，L7 将区分执行内存和缓存使用的存储内存。')
    expand('l5-shuffle-trigger-operators','join',
        '事实表记录订单等事件，维表记录用户等属性。L3 已学按键匹配；现在只问匹配前是否需要重新分发，不要求先掌握 L6 的连接算法。',
        'JOIN 的具体路线受连接条件、已有分布和策略影响，不能仅凭出现 JOIN 就断定两侧各做一次 Shuffle。复制小关系与两侧按键汇合也不是相同动作。')
    add('l6-join-strategies-overview','hash-lookup','equi','哈希匹配先建立什么',
        '可以先把一侧按 user_id 做成“用键找记录”的索引，再让另一侧逐条查找。建立这份结构的一侧叫构建侧；来查找的一侧叫探测侧。哈希负责定位候选，仍要比较键。',
        '# 教学索引，方括号表示同键可有多行\nu1 → [north, south]\n订单 o1/u1/50 来查 u1',
        '找到两个 u1 属性时，匹配应怎样处理？',['任取一个，哈希会自动去重','保留两个匹配，不能靠结构消除重复','不再比较键，所有记录都匹配'],1,
        ['索引不定义任取或去重规则。','对，执行结构仍要遵守原匹配语义。','哈希定位不能替代相等判断。'],
        '哈希匹配是组织查找的方式，不改变 JOIN 的行对规则。BHJ 与 SHJ 都会使用构建结构，区别之一是数据怎样到达参与匹配的位置。',
        '这不是实际 Spark 哈希实现，也不假定不同键永远没有碰撞。')
    add('l6-broadcast-hash-join','broadcast-route','build','广播是复制小关系，不是搬来所有订单',
        '上一课已认识按键查找结构。广播路线把适合构建的一侧发送到相关 Executor，让大表的各分区在执行端据此匹配。Executor 是运行任务的进程，不是分区本身。',
        '# 教学示意\n用户属性 → Executor A、Executor B\n订单分区 A → A 内匹配；订单分区 B → B 内匹配',
        '这个情境中主要被复制到执行端的是哪一侧？',['全部订单汇到 Driver','候选用户属性关系','最终报表的列名'],1,
        ['这不是所画的广播匹配路线。','对，另一侧按其分区参与匹配。','列名不是用于查找的关系数据。'],
        'Broadcast 是分发方式，Hash Join 是匹配方式，组合成广播哈希连接。构建结构仍有内存成本，是否适用要看连接类型、条件与容量。',
        '这不保证 Driver 无任何工作，也不承诺后续聚合没有 Shuffle。')
    expand('l6-join-data-skew','salting',
        '加盐是给热键附加拆分标记，把原本集中到一个键的工作拆开。若用于连接，另一侧必须配套匹配；若用于聚合，还要把拆开的贡献正确合回。',
        'salting 是改写数据组织的方法，有膨胀与复杂度成本。只改一侧键可能漏匹配，随意复制又可能多计；先验证逐组指标和基数，再测是否缓解长尾。')

    # A continuous memory lesson: scope -> two purposes -> idle sharing -> asymmetric reclaim -> parameters.
    s='l7-executor-memory'
    add(s,'memory-jobs','eviction','先分两种用途，而非两根内存条',
        '执行内存（Execution）用于排序、聚合、连接等计算中的工作状态；存储内存（Storage）用于缓存块等可复用数据。先辨认用途，才谈如何共享。',
        'A：排序时暂存待排序记录\nB：cache 后保留的一批数据块',
        'A、B 分别属于哪类用途？',['A 存储，B 执行','A 执行，B 存储','都等于 Python 进程内存'],1,
        ['把工作状态和缓存用途弄反了。','对，两种用途再共同进入统一管理。','Python 进程需另看，不能直接等同。'],
        'Execution 服务当前计算，Storage 服务缓存等复用。统一内存管理让两种用途共享区域 M；这里讲 Executor JVM 的堆内示意，M 不是整个机器内存。',
        '并非一切 JVM 对象都由这两个池管理；堆外、Python 与其他开销需分别核对。')
    add(s,'idle-borrow','eviction','一边空闲，另一边可以多用',
        '把统一区域 M 暂画成 100 格，存储保护区 R=50 格。R 是保护阈值，不是一堵把空间永久切半的墙。先看完全没有缓存的情况。',
        '# 简化总体容量模型，单位为格\nM=100，R=50\n缓存实际占用 S=0\n执行总体希望使用 80',
        '仅从这张容量图看，执行会被固定卡在 50 吗？',['会，50 是执行永久上限','不会，空闲空间可供执行使用','必须先造出 50 格缓存'],1,
        ['保护的是实际存在的缓存，不是空闲配额。','对，没有缓存时不必空留半池。','不需要为占空间而缓存。'],
        '两类用途可以利用对方空闲空间：没有执行工作时缓存也可增长。所谓动态借用首先是共享空闲容量，并不意味着能任意夺走对方已占用的数据。',
        '这是总体容量推演，不是对某个 task 一次申请必获 80 格的承诺；运行中还受任务公平性与块粒度影响。')
    reclaimed=add(s,'execution-reclaim','eviction','执行来要空间，先回收哪部分缓存',
        '缓存曾在执行空闲时增长到 80 格。现在执行需要 40 格。逐出是把缓存块移出内存；它与把计算中间状态 spill 到磁盘不是同一件事。',
        'M=100，R=50\nS=80，E=0，空闲=20\n执行希望占 40\n# 简化容量图，不模拟块粒度',
        '下面哪种状态符合保护阈值且足以提供空间？',['E=40，S=60，逐出20','E=40，S=80，不用改动','S=80，所以执行永远不能开始'],0,
        ['对，先用20空闲，再回收20超出保护线的缓存。','两者合计120，超过M。','超出R的缓存部分可以被执行回收。'],
        '执行有需要时，可逐出缓存超出保护区 R 的部分来回收空间。此例缓存从80降到60，尚未触及50保护线。存储级别约定缓存允许放在哪些介质：允许磁盘的块可能保留磁盘副本，未保留的分区以后需要时可重算。',
        '保护指不因这类执行内存回收而挤掉阈值内的缓存，不是永久保存承诺；主动解除持久化（unpersist）、进程丢失等另论。')
    add(s,'protected-limit','eviction','需要更多时，不能无限赶走缓存',
        '仍是同一个池：缓存80格，保护线50格。假设只通过空闲与合法逐出为执行腾空间，不改变配置、不主动 unpersist，也不计块粒度。',
        'M=100，R=50，S=80，E=0\n空闲20 + 最多回收(80-50)=30',
        '这轮容量推演最多可为执行腾出多少？',['80','50','100'],1,
        ['不能把保护线以下的缓存也按此规则赶走。','对，20+30=50。','缓存保护不是零。'],
        'R 描述执行回收缓存的边界，不是缓存固定上限。若算子工作集仍超出可用空间，应观察 spill、任务工作集与并发；不是继续无限逐出，也不保证必定 OOM。',
        '这个上限只属于给定占用状态与简化假设，不是所有作业固定一半执行内存。')
    add(s,'storage-cannot-evict','eviction','反过来，缓存能赶走正在计算的数据吗',
        '现在执行已使用70格，缓存20格，空闲10格。又来一个需要新增40格的缓存块。虽然R=50，存储也不能因此强制赶走已被执行使用的内存。',
        'M=100，R=50\nE=70，S=20，空闲=10\n新增缓存块需要40',
        '“R是50，所以必须抢30执行内存来装缓存”对吗？',['对，双方已占用空间都能随便抢','不对，存储不能逐出执行已用空间','对，缓存比结果正确更重要'],1,
        ['共享空闲不等于对称强占。','对，缓存需求可能不能在内存满足。','不能为缓存破坏执行。'],
        '回收不对称：存储可以利用执行的空闲空间，却不能逐出执行已占用空间。新缓存块可能无法放入内存，后续行为受存储级别等影响；R不是随时能强制获得的预留配额。',
        '这是新块额外需要40格的情境，不把总缓存目标40与新增40混淆。')
    add(s,'fraction-meaning','eviction','两个参数分别画哪条线',
        '以 Spark 3.5.7 的常规堆内配置作示意：spark.memory.fraction 决定统一区域 M，spark.memory.storageFraction 决定其中的保护阈值 R。先会解释，不急着改默认值。',
        'JVM heap=2300 MiB\n扣除保留量300 MiB\nmemory.fraction=0.6 → M=1200 MiB\nstorageFraction=0.5 → R=600 MiB',
        '这里的600 MiB是什么意思？',['Executor 总内存','缓存绝对不能超过600','M内缓存受执行回收保护的阈值'],2,
        ['heap和M都比它大，Python等开销也不能归进这个数。','空闲时缓存可以超过R。','对，它既不是固定缓存上限，也不是执行永久分界。'],
        'M=(heap-300MiB)×fraction，R=M×storageFraction，是该版本常规堆内说明。提高R可能减少执行可回收空间，不能当作免费增内存；默认值应先保留，以实际工作集和指标验证。',
        '公式不是容器总内存预算；保留设置、测试配置、堆外和运行版本可能改变具体路径。')
    if s in lessons:
        expand(s,'eviction',
            '回顾刚才的容量推演：双方能用空闲空间，执行可在保护线外回收缓存，存储不能逐出执行已用空间。现在回到实际诊断。',
            '不能把规则概括为“完全独立”或“无限互借”。先定位进程、执行工作集、缓存实际占用和存储级别，再判断回收、spill或重算；Python内存问题不能单靠调整这个JVM池解决。')
        guide=guides['lessons'][s]
        if not any(x['url']==TUNING for x in guide['sources']):guide['sources'].append(dict(title='统一内存管理：用途、共享与回收边界',url=TUNING))
        ident=s+'/bridge-execution-reclaim'
        reclaimed['remediation']=dict(id=s+'/memory-reclaim-transfer',knowledgeId=ident,title='换一张容量图再算一次',intro='只看简化总体容量，不模拟任务公平性与块粒度。',
            code='M=200，R=80，S=160，E=0\n执行目标100；当前空闲40',prompt='要满足该执行目标，需要逐出多少缓存？',
            field=dict(id='answer',label='回收量',correctOptionId='r1',options=[dict(id='r0',text='100',feedback='漏算了已有40格空闲。'),dict(id='r1',text='60',feedback='对，40空闲加60回收；剩余缓存100仍不低于R=80。'),dict(id='r2',text='160',feedback='不能随意赶走全部缓存。')]),
            insight='先用空闲，再在R以上回收不足部分；R不是缓存上限。')
        delayed_id=s+'/memory-reclaim-delayed-v1'
        delayed['items']=[i for i in delayed['items'] if i['id']!=delayed_id]
        delayed['items'].append(dict(id=delayed_id,slug=s,taskId=ident,knowledgeId=ident,title='隔天再看保护线',
            code='M=300，R=120，S=210，E=0\n只靠空闲和逐出保护线外缓存腾空间',prompt='这张简化容量图中，最多能给执行腾出多少？',
            options=[dict(id='d0',text='90'),dict(id='d1',text='180'),dict(id='d2',text='300')],correctOptionId='d1',
            explanation='空闲90，加上可回收缓存210-120=90，共180；不能以执行需求为由继续逐出保护线内缓存。不是单task必获该配额的保证。'))
        delayed['version']=max(delayed['version'],5)

    starts={
      'l1-what-is-rdd':'从 L0 的 Driver/执行端角色出发，先用数字和分份建立 RDD 模型，再讨论转换与执行。',
      'l2-what-is-dataframe':'L1 已认识分份数据和惰性转换；这一章改用带列名与类型的表来处理订单。先观察筛选结果，再逐步补齐 Schema。',
      'l3-what-is-spark-sql':'L2 已用 DataFrame 做过筛选和汇总；这一章用 SQL 表达同类需求，复用行、列、NULL和分组概念。',
      'l4-why-explain':'L2/L3 解决了“结果要什么”；这一章学习读“Spark准备怎么做”。先认路线，不要求现在掌握全部节点算法。',
      'l5-what-is-partition':'回到 L1 的数据分份，并接上 L4 的交接节点：这一章用具体数值推演为什么要汇合、如何重分发、成本在哪里。',
      'l6-what-is-join':'L3 已按键匹配订单与用户，L5 已推演同键汇合。这章先重建两张表和行对，再比较完成匹配的不同路线。',
      'l7-what-is-tuning':'前面已认识计划、分区、连接与资源代价；现在把这些线索组织成“证据→假设→单一实验→验证与回退”。'}
    endings={
      'l1-rdd-exercise':'下一章 L2 把元素集合换成带列名、类型的表；继续沿用不可变查询和有界结果回收。先完成独立词频任务，卡在按键合并时回看卡片步骤。',
      'l2-comprehensive':'下一章 L3 用 SQL 重写熟悉的筛选与汇总。NULL、去重、分组与单位约定继续有效，变化的是表达方式。',
      'l3-comprehensive':'下一章 L4 读执行路线。先确认自己能解释查询要什么结果；暂不要求认识所有物理节点。',
      'l4-comprehensive':'下一章 L5 具体推演 Exchange 背后的数据交接。现在记住计划不等于耗时，后面再用分区和键解释交接原因。',
      'l5-comprehensive':'下一章 L6 用分区与汇合模型理解连接策略。先分清同键贡献怎么到一起，再比较复制、排序与建查找结构的代价。',
      'l6-comprehensive':'下一章 L7 综合这些机制做诊断。正确行对与金额仍是底线，策略变化只是待验证实验，不是自动加速证明。'}
    for slug,text in starts.items():
        if slug in lessons:lessons[slug]['mission']=text
    for slug,text in endings.items():
        if slug in lessons:lessons[slug]['next']=text
    for slug,l in lessons.items():
        if slug not in REVISIONS:continue
        order={t['id']:i for i,t in enumerate(l['tasks'])}
        guides['lessons'][slug]['sections'].sort(key=lambda section:order[section['id']])
    guides['version']=max(guides['version'],5)
    delayed['items'].sort(key=lambda i:(i['slug'],i['id']))


if __name__=='__main__':
    import json
    import sys
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]/'src/content'
    lessons={p.stem:json.loads(p.read_text(encoding='utf-8')) for p in (root/'lessons').glob('*.json')}
    guides=json.loads((root/'standardGuides.json').read_text(encoding='utf-8'))
    delayed=json.loads((root/'delayedChecks.json').read_text(encoding='utf-8'))
    apply(lessons,guides,delayed)
    from question_polish import apply as apply_question_polish
    apply_question_polish(lessons,guides,delayed)
    outputs={root/'lessons'/f'{slug}.json':l for slug,l in lessons.items() if slug in REVISIONS}
    outputs.update({root/'standardGuides.json':guides,root/'delayedChecks.json':delayed})
    for path,data in outputs.items():
        text=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
        if '--check' in sys.argv:assert path.read_text(encoding='utf-8')==text,str(path)
        else:path.write_text(text,encoding='utf-8')
    print('PASS explicit concept bridges:',len(REVISIONS),'revised lessons;',sum(len(l['tasks']) for l in lessons.values()),'total steps')
