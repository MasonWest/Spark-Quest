"""L0's five introductory journeys, purpose pools and small runnable exercise.

Explicit material; --check is read-only. Does not change course rows or grades.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
CONTENT = ROOT/'frontend/src/content'
BASE = 'https://spark.apache.org/docs/3.5.7/'


def build():
    seed=json.loads((ROOT/'backend/app/course_seed.json').read_text(encoding='utf-8'))
    originals={l['slug']:l['content']['explanation'] for lv in seed['levels'] for l in lv['lessons']}
    lessons={}; guides={}; delayed=[]; bank=[]
    current=None

    def lesson(slug,title,mission,next_text,source,correction):
        nonlocal current
        current=dict(slug=slug,version=2 if slug in ('l0-driver-executor','l0-first-pyspark-program') else 1,title=title,mission=mission,next=next_text,source=BASE+source,
                     correction=correction,tasks=[])
        lessons[slug]=current
        guides[slug]=dict(title=title,sections=[],sources=[dict(title='Spark 3.5.7 官方说明',url=BASE+source)])
        bank.append(dict(lesson_slug=slug,questions=[]))

    def step(key,title,intro,code,prompt,choices,feedback,insight,boundary,a,b,kind=None,label='你的判断'):
        """choices / a / b put the right answer first; display positions vary."""
        ident=current['slug']+'/'+key
        field=dict(id='answer',label=label,correctOptionId='o0',options=[dict(id=f'o{i}',text=text,feedback=feedback[i]) for i,text in enumerate(choices)])
        offset=(len(current['tasks'])+len(lessons))%3
        field['options']=field['options'][offset:]+field['options'][:offset]
        if kind:
            field['input']=dict(kind=kind,acceptedAnswers=[choices[0]],incorrectOptionId='o1',placeholder='填写整数' if kind=='integer' else '填写名称')
        markers=[line.strip() for line in originals[current['slug']].splitlines() if line.startswith('【')]
        task=dict(id=ident,knowledgeIds=[ident],title=title,intro=intro,code=code,prompt=prompt,fields=[field],
                  insight=insight,ability=title,reading=dict(id=ident+'/reading',title=title,sectionTitle=markers[0].strip('【】'),
                  startMarker=markers[0],endMarker=markers[1],connection=insight,boundary=boundary,
                  caution='旧讲义保留查阅，其中的绝对化说法已在本课标准讲解修正，请结合这里的条件理解。'))
        current['tasks'].append(task)
        guides[current['slug']]['sections'].append(dict(id=ident,title=title,body=insight,boundary=boundary))
        j=len(current['tasks'])-1
        for variant,(question,options,explanation) in enumerate((a,b)):
            correct=(j+variant+len(lessons)-1)%4
            opts=options[1:].copy(); opts.insert(correct,options[0])
            purpose='assessment' if variant==0 else ('review' if j<3 else 'remediation')
            bank[-1]['questions'].append(dict(key=f'{ident}/{purpose}-v1',knowledge_id=ident,task_id=ident,purpose=purpose,
                type='single_choice',prompt=question,options=opts,correct_index=correct,explanation=explanation,
                dimension=['concept','apply','mechanism','debug','transfer'][j]))
        return task

    def transfer(task,code,prompt,choices,feedback,insight,newcode,newprompt,newchoices,why):
        ident=task['id']+'/transfer'
        opts=[dict(id=f'r{i}',text=text,feedback=feedback[i]) for i,text in enumerate(choices)]
        opts=opts[1:]+opts[:1]
        task['remediation']=dict(id=ident,knowledgeId=task['id'],title='换一份材料再判断',intro='用同一个规则处理新材料。',
            code=code,prompt=prompt,field=dict(id='answer',label='变式判断',correctOptionId='r0',options=opts),insight=insight)
        opts=[dict(id=f'd{i}',text=text) for i,text in enumerate(newchoices)]
        opts=opts[2:]+opts[:2]
        delayed.append(dict(id=ident+'-delayed-v1',slug=current['slug'],taskId=task['id'],knowledgeId=task['id'],
            title=task['title']+' · 隔天验证',code=newcode,prompt=newprompt,options=opts,correctOptionId='d0',explanation=why))

    lesson('l0-what-is-spark','先认识这台计算引擎',
        '从三份小统计开始：先看Spark帮谁做计算，再分清计算、存储与部署。暂时不需要背API。',
        '下一课继续看分工的代价：有些工作可以并行，有些时间花在搬运与协调上。','quick-start.html',
        'Spark可以在单机运行，不是数据库，也不保证所有数据默认常驻内存。是否采用Spark取决于需求与成本，没有通用的GB门槛。')
    step('fit','小表也一定要上集群吗',
        '你要给一张200行的表求和，当前单机工具已经能快速完成。Spark是数据处理引擎：可组织并行工作，但启动与协调也有成本。',
        '# 情境：200行；当前工具秒级完成；没有集群或统一流水线的额外要求。','此时更合适的起点是？',
        ['先评估现有工具','立即改用Spark','先扩成多台机器'],
        ['对，先看实际需求。','Spark能处理小表，不代表一定值得切换。','先增加机器并未证明有收益。'],
        'Spark提供处理数据的能力，选工具仍需看输入、操作、交付需求与资源。小数据可用于学习Spark；业务中现有工具已够用时，不必为了分布式而迁移。',
        '没有统一的数据量门槛，也不能仅凭行数断言某个工具永远更快。',
        ('300行报表当前工具运行很快、没有额外平台要求，下一步最合理的是？',['先评估现有工具','必须迁移Spark','必须增加机器','必须引入缓存'],'先确认需求，不凭工具名决定迁移。'),
        ('只有几KB数据却计划启动集群，评估时还应算入什么？',['启动与协调成本','只看输出列数','只看代码行数','只看工具流行度'],'分工有成本，输入很小也能学习，但不能直接推导收益。'))
    t=step('combine','三份计数怎样合成一份',
        '同一天的订单被分成互不重叠的三份，各自数出12、8、5条。分工计算后，还要按同一个业务规则合并。',
        '三份互不重叠的订单\n份A：12条；份B：8条；份C：5条','全日共多少条订单？',
        ['25','12','8'],['对，12+8+5=25。','12只是其中一份，不是总数。','这里需要相加，不是取某一份。'],
        '分布式计算常把工作拆成多份，再合并各份的贡献。对互不重叠的计数可以相加；“分工”不自动决定所有指标都用同一种合并规则。',
        '本题已约定无重叠；若同一订单重复出现，需要先明确去重规则。',
        ('三份互不重叠的访问分别计4、7、9次，总访问数是？',['20','9','7','3'],'总数是各份贡献相加，不是份数或最大值。'),
        ('两份无重叠的告警计数为6、11，合成总数应？',['17','11','6','2'],'每份合法贡献都需要计入。'),kind='integer',label='总条数')
    transfer(t,'互不重叠的两份记录：6条、9条','总数应是多少？',['15','9','2'],
        ['对，两份贡献相加。','9只是其中一份。','2是份数，不是记录数。'],'总量与数据分成几份不是同一个数字。',
        '互不重叠的三份记录：2条、10条、7条','合并后的条数是？',['19','10','3'],'无重叠计数相加得到19；分工不应丢贡献。')
    step('engine','负责计算，不等于长期存放',
        '订单文件已经保存在对象存储中。Spark读取文件、计算每日统计，再把报表写回指定位置。对象存储在这里负责保存文件。',
        '对象存储中的订单 → Spark计算 → 外部位置中的日报','这条流程中，Spark主要承担什么？',
        ['读取并计算报表','永久保存源文件','替代外部的存储'],
        ['对，计算与存储要分开理解。','长期保存需要明确的存储系统和写出策略。','使用Spark不意味着移除原来的存储系统。'],
        '计算引擎描述、组织并执行数据处理，数据通常来自外部文件或系统，结果也可以写到外部。把“能读写数据”理解成“自动成为永久数据库”，会混淆职责。',
        'Spark生态有目录和表等能力，本课只建立计算与持久保存的职责区别。',
        ('文件留在外部存储，Spark读取后生成日报。Spark主要属于哪一层？',['数据计算处理层','长期文件保存层','集群资源分配层','业务索引保存层'],'读写外部数据不等于替代其保存职责。'),
        ('日报计算结束后，怎样让结果长期保留？',['写到约定的持久存储','只保留Python变量','只关闭终端窗口','仅让查询对象存在'],'应明确保存位置和写出规则，不依赖临时变量。'))
    step('local','只有一台电脑，也可以开始',
        '分布式描述的是组织计算的能力，不是“每次启动必须有多台物理机器”。本地学习可以让同一台电脑执行这套流程。',
        '# 后面会实际使用：本地模式 local[2]\n# 现在先认清：local 指本机，不是两台机器。','只有一台电脑，能学习Spark吗？',
        ['可以在本机运行','至少两台机器','先建远程集群'],
        ['对，本地可以学习接口与分工。','不需要用多台机器才能创建应用。','本课不要求先部署远程集群。'],
        '本地模式可以在一台机器上运行Spark，便于学习和小规模验证。后续再区分负责协调与负责执行的角色；角色有区别，不代表必须各占一台机器。',
        '本地成功不等于已验证集群权限、网络、规模或生产性能。',
        ('学习者只有一台电脑，尚未部署集群，可以怎样开始？',['使用本地运行模式','等待第二台机器','先租用多节点集群','必须先安装分布式存储'],'本地模式可运行学习样例。'),
        ('小程序在本机通过，能直接认定远程集群部署已验证吗？',['不能，还需部署验证','能，运行位置没有区别','能，本地就是远程认证','能，接口相同即全部相同'],'程序语义与部署条件需要分别验证。'))
    step('memory','内存计算不是永远不碰磁盘',
        '内存可加快某些工作，但输入、缓存和处理中间状态受容量与策略影响。Spark也可能读写磁盘或重新计算。',
        '# 数据比可用内存大；运行方式与具体操作仍需检查。','哪种理解更可靠？',
        ['可能使用内存和磁盘','默认全量永久驻内存','使用Spark就不再读盘'],
        ['对，后面会逐步学习这些条件。','创建数据对象并没有这样的永久承诺。','外部输入和执行过程仍可能涉及磁盘。'],
        'Spark能够利用内存，也可能发生磁盘读写与重算。缓存是需要讨论复用、容量和生命周期的策略，不是给所有结果自动贴上的“永久存放”标签。',
        '本课不要求记缓存级别或内存比例；先去掉“永远不读盘”的误解。',
        ('看到Spark作业发生磁盘读写，可以立即断言它不是Spark吗？',['不能，磁盘仍可能参与','能，系统永不读写磁盘','能，只可处理内存输入','能，所有结果永久缓存'],'Spark不是不使用磁盘的系统。'),
        ('只创建数据查询对象，就能保证所有结果永久缓存吗？',['不能，需要另看策略','能，变量即完整缓存','能，内存即永久保存','能，本地运行即保证'],'创建对象与结果持久化不是同一件事。'))

    lesson('l0-what-problem-spark-solves','分工之后，还要付出什么',
        '接着上一课的分份计数：换一种指标、加入搬运和重算，看看引擎真正替我们组织哪些工作。',
        '下一课给这些工作安排角色：谁协调任务，谁处理每一份数据，结果又去哪里。','quick-start.html',
        '加机器不保证线性加速；缓存需要实际复用与容量；容错有上游与副作用边界；不承诺固定的加速倍数。')
    step('maximum','这次不是求和，而是找最大值',
        '上一课计数可以相加。这次业务要“全天最长响应时间”，两份数据各自的最大值是6秒和11秒。',
        '份A最大：6秒\n份B最大：11秒','全天最大响应时间是？',
        ['11','17','2'],['对，取两份最大值中的较大者。','17是相加，不是最大值。','2是份数，不是响应时间。'],
        '把工作分开后，合并规则必须跟着业务指标走。计数相加、最大值取最大；不能把“合并”都理解成求和。',
        '这里只处理最大值；平均值等指标的合并规则会在后续课程具体推演。',
        ('两份数据的最大响应时间为5秒和13秒，全天最大值？',['13','18','9','2'],'最大值取较大者，不做求和或局部平均。'),
        ('三份最高温度为18、21、19，整体最高温度？',['21','58','19','3'],'合并的是同一指标的各份最大值。'),kind='integer',label='最大秒数')
    step('movement','算得快，也可能等在搬运上',
        '一份对照记录：计算本身花2秒，数据跨机器搬运花8秒。这里的秒数只是教学记录，不是Spark固定规律。',
        '本次记录：计算2秒；搬运8秒\n只把计算阶段从2秒缩到1秒','哪一部分最值得继续调查？',
        ['优先调查数据搬运','仅缩短计算用时','仅增加计算节点'],
        ['对，先看当前主要代价。','计算更快不代表解决了主要等待。','更多机器还可能增加协调和搬运。'],
        '并行计算要交换数据、等待依赖并协调任务。观察完整流程后再定位主要成本，才能避免只盯着CPU计算。后面会把某些数据交接称为Shuffle。',
        '单次教学记录只能说明本次线索，不是所有作业都由网络限制。',
        ('本次计算1秒、数据搬运9秒，只加快计算就能解决主要成本吗？',['不能，搬运仍占主要部分','能，计算快即整体快','能，搬运不会影响总时间','能，增加机器必消除搬运'],'先关注已观察到的主要代价。'),
        ('节点增加后更慢，同时看到搬运与调度开销上升，应如何理解？',['继续定位这些新增代价','认定Spark不能并行','认定结果一定计算错误','仅按机器数量宣称提速'],'横向扩展有代价，不能按节点数承诺加速。'))
    t=step('reuse','重复工作可以复用，但先确认条件',
        '两份报告都要用同一份清洗结果。缓存的意思是尝试保留可复用结果，减少重复计算；是否划算还要看建立、读取与资源成本。',
        '原流程：清洗 → 报告A；重新清洗 → 报告B\n候选：清洗 → 保留共享结果 → A、B复用','候选方案要先确认什么？',
        ['同一结果确实能复用','调用缓存就必定更快','只要同源就自动命中'],
        ['对，复用对象与资源条件都要明确。','建立和管理缓存也有成本。','同一来源不代表同一个待复用结果。'],
        '缓存可帮助重复使用同一结果，但要有实际复用、足够资源和正确生命周期。只运行一次、重算便宜或容量不足时，不应直接宣布缓存有收益。',
        '本课不要求操作缓存API；L1会区分登记与执行，后续再做具体缓存实验。',
        ('两份报告共用昂贵清洗结果，评估缓存时第一项条件是？',['确认实际共享复用','只看是否写了cache','仅看变量名是否相同','只看原文件来自同处'],'要确认复用关系，不能把接口调用当收益证明。'),
        ('某结果只用一次且重算便宜，应该怎样评价缓存？',['比较全流程成本','一定值得永久缓存','命中一次就保证回本','只按内存计算名词判断'],'建立与管理成本也需要计入。'))
    transfer(t,'同一输入：报告A用原始明细，报告B用不同过滤后的明细。','仅凭输入来源相同，能认定两份查询自动复用同一缓存吗？',
        ['不能，要查复用关系','能，同源就必命中','能，同名就必命中'],
        ['对，来源相同不足以证明复用。','查询计算不同，不能仅凭同源保证。','变量名也不是复用证据。'],
        '先确认复用的是哪个计算结果，再看实际采用与成本。',
        '昂贵结果只生成一次供两份报告使用，但缓存建立时间尚未计入。','能直接用热缓存那一次耗时宣称全流程收益吗？',
        ['不能，还要计建立成本','能，命中就证明回本','能，原始输入没变即可'],'比较范围必须一致，复用收益需扣除建立和资源成本。')
    step('retry','一份任务失败，不等于答案能凭空恢复',
        '某份计算失败，但原始输入仍可读，规则可重新执行。系统可以尝试重新安排这份工作；重新读取和计算仍要时间。',
        '输入仍可读 + 计算可重做\n其中一份任务失败','哪种理解正确？',
        ['按条件重做该份','丢结果能猜回','写外部天然去重'],
        ['对，恢复有前提也有成本。','没有输入和规则就不能凭空重建。','重新执行与外部系统去重是不同问题。'],
        '容错帮助系统处理某些任务失败，但不等于所有故障都可恢复，更不等于任意外部写入只发生一次。先记住“可读输入、可重做工作”，L1再讲记录依赖的血缘。',
        '若上游已不可读、整个应用失败或外部写入不可重复，需要其他恢复设计。',
        ('一份任务失败，输入仍可读且计算可重做，系统可尝试什么？',['重新安排该份计算','按结果长度猜原值','跳过该份仍算总量','直接把失败份填成零'],'恢复要重新获得正确贡献，不能漏算或造数。'),
        ('输入已永久丢失，仅知道过去做过一次计算，能保证恢复原结果吗？',['不能保证恢复','能，从任务名字恢复','能，增加机器即可恢复','能，补零等于恢复'],'恢复依赖可用来源或其他可靠副本。'))
    step('measure','“这次更快”与“永远更快”',
        '同一输入、相同资源下，旧流程三次为12/11/12秒，新流程为8/9/8秒；逐组结果已经核对一致。',
        '旧：12、11、12秒\n新：8、9、8秒\n相同条件；结果一致','目前能支持哪项结论？',
        ['本次条件下更快','所有数据必提速','节点翻倍快一倍'],
        ['对，明确已验证范围。','换输入与执行条件后需要重新验证。','数据分布和协调成本不由节点数单独决定。'],
        '收益要由正确结果和可比较的测量支持。重复测量帮助观察波动；报告应说清输入、资源和范围，不从一份样例推导固定倍数。',
        '这些是合成教学记录，不是本项目的真实性能基准。',
        ('同条件多次运行更快且结果一致，合理报告是？',['该条件下观察到收益','所有输入保证同倍加速','所有集群保证耗时减半','不再需要未来验证'],'结论应限制在已经测量的范围。'),
        ('原方案冷缓存、新方案热缓存且输入量更小，直接比较秒数缺少什么？',['可比较的实验条件','更短的变量名称','更多结果截图','固定的加速倍数'],'同时改变多个条件，不能直接把收益归于某一改动。'))

    lesson('l0-driver-executor','一份工作，谁协调，谁执行',
        '上一课知道要分工与重做，现在给角色起名：Driver协调，Executor执行任务。先分清职责，再看本地并行。',
        '下一课用SparkSession取得编程入口，再把这些角色串成一个可以启动的小程序。','cluster-overview.html',
        'Driver不只是“永不计算的包工头”，结果也不必全部回Driver；本地模式下角色与物理机器不是一一对应。')
    step('coordinate','谁安排这份任务',
        'Driver运行应用的主程序，并组织与跟踪任务。Executor执行分配到的任务；Task就是交给执行端的一份工作。',
        '主程序 → 安排任务 → 跟踪完成情况','这里负责全局协调的角色是？',
        ['Driver','Executor','每一行订单'],
        ['对，协调应用任务属于Driver职责。','Executor主要执行分配来的任务。','记录是待处理的数据，不是协调进程。'],
        'Driver负责应用级协调与调度；Executor是执行进程，接收Task并处理数据。先把角色和职责分清，再去看它们运行在哪台机器。',
        '这是经典Spark应用的入门模型，不把Spark Connect等部署路径混在本课。',
        ('主程序组织并跟踪各份任务，主要对应哪个角色？',['Driver','Executor','输入记录','输出字段'],'Driver协调应用计算。'),
        ('执行端完成一份工作后，谁负责跟踪整个应用的进度？',['Driver','单条数据记录','一个输出列名','源文件的表头'],'区分应用级协调与单份工作执行。'))
    t=step('execute','谁处理分到的那份数据',
        'Driver已经安排任务A和B。Executor接收任务，处理分到的数据，也可保存缓存或写外部结果。',
        '任务A：处理这一份订单\n任务B：处理另一份订单','正常分布式执行中，谁运行这些任务？',
        ['Executor','全由Driver逐行处理','原文件负责计算'],
        ['对，任务交给执行进程。','不是把所有分份工作都先收回Driver。','文件保存数据，不负责执行Spark任务。'],
        'Executor可以在应用期间执行许多Task；它不是只处理一次工作的“任务本身”。应用有几个Executor、每次能同时跑多少任务，取决于资源与配置。',
        '一个分区通常对应某个阶段的一份任务，但阶段与分区会在后续课程展开，本课不据源码行数数Task。',
        ('Driver已分发任务，对相应数据份实际执行计算的是？',['Executor','源文件表头','输出字段名','Driver变量名称'],'Executor运行被分配的任务。'),
        ('一个Executor完成任务A后，能继续执行任务B吗？',['可以，进程可运行多个任务','不能，一进程只准一个任务','不能，必须换机器','不能，必须改业务结果'],'执行进程和一次任务不是同一个概念。'))
    transfer(t,'同一个执行进程先完成任务1，再接任务2。','应怎样区分进程和任务？',
        ['一个Executor可接多个Task','每个Task必是一台机器','一个Executor只准一个Task'],
        ['对，任务是工作单元，Executor是执行进程。','Task不是物理机器。','进程在应用期间可执行多项任务。'],
        '分清执行进程、任务与物理机器，不从编号猜部署。',
        '节点X上一个Executor先后运行Task 3和Task 7。','这条记录能证明什么？',
        ['该进程执行过两个任务','必有两台物理机器','必须同时运行两个任务'],'先后运行不等于同时运行，任务数也不等于机器数。')
    step('slots','两份并发能力，不是两台机器',
        '把同时能做的工作位置叫“槽位”。教学模型中共有5个等长任务，每轮最多同时做2个；没有重试和额外开销。',
        '第1轮最多2项\n第2轮最多2项\n共有5项工作','至少需要几轮才能全部完成？',
        ['3','2','5'],['对，2+2+1需要3轮。','两轮最多完成4项。','不必每轮只做一个任务。'],
        '任务总数与可用并发位置不同。即使有5份任务，也可能分几轮执行；机器数、进程数和槽位数不能直接画等号。',
        '这里只算理想轮数，不承诺真实调度时间或某个作业的准确Task数。',
        ('教学模型：7项等长任务，每轮最多3项，至少几轮？',['3','7','2','1'],'3+3+1，共3轮。'),
        ('教学模型：6项等长任务，每轮最多2项，至少几轮？',['3','2','6','4'],'并发容量限制一轮能完成的任务数量。'),kind='integer',label='轮数')
    step('results','回传数字，还是写出明细',
        '应用只请求总条数时，可以把最终小计数交回主程序；交付大量明细时，可以让任务写到外部存储，不必把全部明细收回Driver。',
        '请求A：返回一个总条数\n请求B：交付大量明细文件','哪种路线更符合职责与规模？',
        ['计数回传，明细写出','明细全收，再做切片','全表回传，才能计数'],
        ['对，结果去向取决于请求。','先收全表会把规模压力集中到Driver。','请求数量不要求把全部明细交给主程序。'],
        '并不是每个任务都把全部数据沿原路交回Driver。结果可以作为小值返回，也可以由执行端写外部；中间数据也可能在执行端之间交换。',
        '具体接口和数据搬运路径会在后续课程学习；有界返回也不保证上游计算成本很小。',
        ('只要最终总条数，应回传给主程序什么？',['小计数结果','全部明细再数','所有源文件副本','每台机器的完整磁盘'],'返回数量与回传所有明细不同。'),
        ('要交付海量明细，哪条路线避免强制全部收回Driver？',['按任务写约定存储','先全量collect再切片','先全量转Python列表','把Driver变量名改短'],'交付大结果要设计写出方式和容量。'))
    step('local-roles','本地模式也保留职责区别',
        'local模式在同一台电脑上学习协调与执行。不要把“角色不同”理解成“必须分别买一台机器”。PySpark也涉及Python与JVM边界。',
        '# 一台电脑上的local模式\n# 角色：协调、执行；不据此推断两台机器。','哪句话成立？',
        ['可在本机学习两类职责','两种角色必占两台机器','本地模式没有任务执行'],
        ['对，职责与物理部署分开理解。','角色不同不要求各占一台机器。','本地仍会运行计算任务。'],
        '经典本地模式的调度和执行可在同一个JVM里进行；PySpark的Python进程又是另一层边界。本课先理解职责，不用进程比喻替代实际部署检查。',
        '集群与本地的进程布局不同；不能仅凭“本地模式”断言整个PySpark程序只有一个进程。',
        ('本机只有一台电脑，仍能演练Driver协调与任务执行吗？',['可以，本地模式可运行','不能，角色必须各占一机','不能，本地只有代码没有计算','不能，必须先租集群'],'职责不等于物理机器数量。'),
        ('看到Driver与Executor两个名字，可以直接推断有两台机器吗？',['不能，需看部署方式','能，一个名字就是一台机','能，所有应用固定两台机','能，本地模式也固定两台机'],'角色、进程与机器需要分别区分。'))

    lesson('l0-sparksession','把程序接到Spark入口',
        '有了协调与执行的角色图，现在获得一个真正的编程入口。下面按创建、命名、本地并发、数据和释放逐步练习。',
        '下一课把这些调用串成读CSV、预览、统计、释放资源的小程序；不要求先背完DataFrame语法。','sql-getting-started.html',
        'SparkSession是现代DataFrame/SQL常用入口，RDD也可从SparkContext使用；getOrCreate不等于每次重建应用或重置所有配置。')
    step('entry','builder还差最后一步',
        'SparkSession是现代DataFrame/SQL程序的常用入口。builder先描述如何取得会话，getOrCreate()才取得现有或新建的会话。',
        'from pyspark.sql import SparkSession\nspark = SparkSession.builder.appName("first-app").__A__()','A应填哪个方法名？',
        ['getOrCreate','appName','show'],['对，取得会话入口。','appName设置名字，不完成取得会话。','show是查看数据结果，不是构造入口。'],
        '把builder看作准备创建会话的设置链，把getOrCreate看作取得会话的动作。在笔记本环境中可能已经有spark变量，可使用现有入口，不需要反复创建。',
        '已有会话可能被复用；不要把再次调用当作清空数据或重置全部配置。',
        ('SparkSession.builder.appName("demo")后，取得会话还需要哪一步？',['getOrCreate()','show()','count()','printSchema()'],'builder设置与会话对象不同。'),
        ('笔记本环境已经提供spark变量，合理起点是？',['先了解并使用现有会话','每条查询重建一个应用','先停止所有共享会话','只因变量存在就重设全部配置'],'先确认环境和会话所有权。'),kind='text',label='方法名')
    step('local-two','local[2]里的2是什么',
        'master指定运行位置。本课选local[2]：在本机用两个工作线程演练，和上一课“两份并发能力”的模型衔接。',
        'SparkSession.builder.master("local[2]")','这里的2主要表示什么？',
        ['本地工作线程数','远程物理机器数','输入数据的总行数'],
        ['对，是本地运行的线程设置。','local指本机，不是在申请两台机器。','运行配置不规定业务行数。'],
        'local[N]表示本地使用N个工作线程；local[*]使用可用的逻辑核心数。教学采用较小并发，便于观察；它不代表创建N个独立远程Executor。',
        '真实能同时完成多少工作还受依赖、资源和操作影响，不按线程数保证加速倍数。',
        ('master("local[3]")中的3表示什么？',['本地工作线程设置','远程机器数量','数据记录总条数','查询返回字段数'],'local参数不是机器或业务数据数。'),
        ('想在本机用两个工作线程练习，哪项配置表达这个意图？',['local[2]','local[20]','local[1]','远程两台机器'],'配置数字表达本地工作线程数。'))
    step('name','应用名不是输入路径',
        'appName给应用一个便于识别的名字，常用于界面与日志。本课稍后会读取sales.csv，文件路径要写在读取调用中。',
        '.appName("sales-intro")\n# 输入文件仍由read.csv("sales.csv")指定','sales-intro在这里是什么？',
        ['应用识别的名字','CSV输入路径','结果分组的字段'],
        ['对，它帮助辨认应用。','设置名字不会自动读取同名文件。','它也不修改数据列。'],
        '应用名、输入路径和数据列名是三个不同概念。名字帮助人识别应用，不会创建业务数据、打开同名文件或改变查询口径。',
        '不把appName当作性能参数、唯一应用ID或SQL表注册操作。',
        ('appName("daily-demo")会自动读取daily-demo文件吗？',['不会，只设置应用名','会，名字就是路径','会，名字就是SQL表','会，名字就是输出目录'],'读取路径由实际读取调用指定。'),
        ('要给应用起名便于日志辨认，应使用哪一项？',['appName','master','header','region'],'识别应用与配置运行位置、文件表头不同。'))
    step('table','第一次看到带列名的数据',
        'DataFrame可先理解成带列名和类型的数据表。下面直接给出两行与类型；创建后用count请求条数。类型的细节到L2再展开。',
        'df = spark.createDataFrame(\n [("north", 3), ("south", 5)],\n "region string, amount long")\nprint(df.count())','这次count返回多少？',
        ['2','8','1'],['对，输入是两行。','8是金额相加，不是行数。','两行不会自动合成一行。'],
        'region、amount是列名；string表示文本，long表示整数类型。count请求记录条数，不对金额求和。先会分清行数与业务指标，再逐步学习列操作。',
        '这里只是很小的本地输入，不代表大数据应先放进Driver的Python列表。',
        ('给出三行(city,amount)，amount分别2、4、8，df.count()返回？',['3','14','8','2'],'count数行，不求金额总和。'),
        ('只有一行("north",100)，count返回？',['1','100','2','0'],'一行包含多列仍只贡献一条记录。'),kind='integer',label='条数')
    t=step('stop','谁创建，谁负责收尾',
        '在这个独立脚本中，我们自己创建并拥有会话。所有结果使用结束后再stop；不要在每个show前都关闭入口。',
        '# 自己拥有的独立脚本\n# 取得会话 → 数据处理 → 查看结果 → spark.stop()','stop在这里主要负责什么？',
        ['结束自有会话资源','删除原CSV文件','永久保存计算结果'],
        ['对，计算资源也需要生命周期。','stop不是删除输入的业务指令。','永久交付需要明确写出，不由stop代办。'],
        'stop结束相应Spark上下文所用资源；本课在独立脚本中负责清理自己拥有的会话。在共享笔记本或平台上，先确认资源所有权，不能随意停止他人共享环境。',
        '释放资源不等于删除原始数据，也不等于把结果持久保存。',
        ('自己创建会话的独立脚本完成后，stop主要表示什么？',['释放相应计算资源','删除输入业务文件','永久保存所有结果','清空所有外部数据库'],'资源生命周期与业务数据保存不同。'),
        ('共享平台已有会话，是否应在每个练习结束时盲目stop？',['先确认会话所有权','必须无条件停止','必须先删除源数据','只要名字相同就能停止'],'共享环境需尊重会话所有权，不能照搬独立脚本。'))
    transfer(t,'共享笔记本提供现成spark，其他单元格还要继续查询。','应该怎样处理停止会话这一步？',
        ['先确认共享资源约定','每次查看前先stop','用stop把结果永久保存'],
        ['对，不随意结束共享会话。','先停止会让后续查询无法按原流程继续。','stop不负责业务持久化。'],'独立脚本与共享环境的所有权不同。',
        '自己创建的独立脚本已经取完结果，原始文件仍需保留。','结束计算资源应选择？',
        ['调用spark.stop()','删除所有输入文件','把全部明细collect回来'],'stop释放计算资源，不删除输入，也无需为关闭而收集全部明细。')

    lesson('l0-first-pyspark-program','读三行订单，跑完第一个程序',
        '把前四课拼起来：检查环境、读一份小CSV、预览、分组求和、释放资源。手机上先推演，电脑上可下载同一任务实际运行。',
        'L0到这里有了一次完整计算。下一章L1用整数和分份建立RDD模型，再学转换与结果请求；L2会回来细讲这里的DataFrame与列类型。','quick-start.html',
        '使用有表头、显式列类型的小CSV。历史CSV示例中的north行有拼写问题，请以本课下载的sales.csv为准。读取可能做文件发现等工作，不能说action前绝对零IO；推演通过不等于代码已实际运行。')
    step('environment','错误发生在哪一层',
        'PySpark程序需要可用的Python环境、匹配的pyspark包以及兼容的Java运行时。Java虚拟机（JVM）运行Spark主体。先看错误发生在哪一步。',
        'from pyspark.sql import SparkSession\n# ModuleNotFoundError: No module named "pyspark"','这个错误应先检查什么？',
        ['当前Python环境中的包','业务分组汇总公式','Driver返回的数据行数'],
        ['对，导入还未成功，先查实际解释器和包。','程序还没有进入分组阶段。','也还没有运行到结果回传。'],
        '先确认运行脚本的Python解释器与安装包对应，再检查Java版本、JAVA_HOME及启动错误。不要把环境失败当成SQL或业务理解错误；版本要求以所用Spark发行版官方说明为准。',
        '本课程按经典PySpark本地运行；Spark Connect等远程客户端的环境要求不混入本任务。',
        ('导入pyspark就报ModuleNotFoundError，优先核对？',['当前解释器与包安装','分组聚合与金额计算','地区保留与缺失处理','线程数量与并发配置'],'导入失败先处理当前Python环境。'),
        ('导入成功但启动时报Java相关错误，应先查？',['Java环境兼容性','地区求和的业务公式','CSV某地区的拼写','结果显示的排序方向'],'区分Python导入、JVM启动和业务计算阶段。'))
    step('read','表头不是一条订单',
        '文件第一行是列名，后面有三条订单。header=True表示使用首行为表头；schema在这里直接给出列名与类型，不要求现在背语法。',
        'region,amount\nnorth,12\nnorth,8\nsouth,5\n\n# 读取：header=True，schema="region string, amount long"','正确读取后，df.count()应为多少？',
        ['3','4','2'],['对，三条订单，不包含表头。','4把表头误当数据。','2是地区数量，不是订单数量。'],
        '读取时把表头、数据行与列类型分清。这里显式指定amount为整数，避免把文本外观等同于数值类型；类型推断与错误数据处理会在L2详细学习。',
        '文件路径按实际工作目录解析；读取也可能做文件发现等工作，不承诺action前绝对零IO。',
        ('CSV有一行表头与四条订单，header=True且类型正确，count应为？',['4','5','1','0'],'表头不是订单记录。'),
        ('文件有一行表头、两条订单且属于同一地区，正确读取后count是？',['2','1','3','0'],'记录数不等于不同地区数。'),kind='integer',label='订单条数')
    t=step('preview','看两行，不是只剩两行',
        '这张表仍有三条订单。show(2)只是请求显示少量结果；不会把原查询改成只有两行。',
        'df.show(2)\nprint(df.count())\n# 输入仍是上一步的三条订单','第二行打印什么？',
        ['3','2','1'],['对，预览不删记录。','显示上限不是全表行数。','也没有按地区去重。'],
        'show的显示上限与count返回的记录数不同。少量预览便于检查形状，但不能只凭屏幕显示两行就推断总量、数据质量或读取成本。',
        '返回少量结果不等于上游只做同样少量工作；本步不要求理解完整计划。',
        ('8条记录先show(3)，随后count，打印条数？',['8','3','5','1'],'预览不原地截断查询。'),
        ('show(1)只显示一条，能据此证明输入只有一条吗？',['不能，还需请求条数','能，显示上限等于总量','能，其余记录已被删除','能，所有记录已被去重'],'可见样本不等于完整数据规模。'),kind='integer',label='打印条数')
    transfer(t,'输入有6条，执行df.show(2)，然后df.count()。','count应是多少？',['6','2','4'],
        ['对，显示不删除原记录。','2只是显示上限。','不是显示后把两条删掉。'],'查询预览不修改原来的逻辑内容。',
        '输入有9条，先show(4)，之后再请求完整count。','count返回？',['9','4','5'],'仍是9；show显示多少与原查询的总条数不同。')
    task=step('aggregate','按地区把金额合起来',
        'groupBy("region")表示按地区分组，sum("amount")把各组金额相加。north有12和8，south有5，输出每个地区一行。',
        'report = df.groupBy("region").sum("amount")\n# north: 12、8；south: 5','填写两个地区的总金额：',
        ['20','12','2'],['对，north的两次贡献都需要计入。','12只算了一条。','2是north订单条数，不是金额。'],
        '每个分组先接收属于自己的记录，再按指定指标合并。这里的输入是3条订单、输出是2个地区汇总；sum(amount)是Spark给求和结果列的默认名称。',
        '本题金额均为非空整数，地区非空；NULL、金额精度和更复杂分组留给后续章节。',
        ('订单east/7、east/4、west/9，按地区求和，east金额？',['11','7','2','20'],'同地区金额相加，既不计条数也不混入其他组。'),
        ('订单A/3、B/5、A/6，按地区求和后的结果是？',['A=9，B=5','A=3，B=5','A=14，B=14','A=2，B=1'],'逐组汇总保持各组的业务贡献。'),kind='integer',label='north金额')
    task['fields'].append(dict(id='south',label='south金额',correctOptionId='s0',
        options=[dict(id='s0',text='5',feedback='对，south只有一条5元订单。'),dict(id='s1',text='1',feedback='1是订单条数，不是金额。'),dict(id='s2',text='25',feedback='25是全局金额，不是south分组金额。')],
        input=dict(kind='integer',acceptedAnswers=['5'],incorrectOptionId='s1',placeholder='填写整数')))
    step('cleanup','成功和报错都要收尾',
        '这是自己拥有会话的独立脚本。try内执行读取与统计；finally会在正常结束或异常路径尝试运行，适合放资源清理。',
        'spark = SparkSession.builder.master("local[2]").getOrCreate()\ntry:\n    # 读CSV、计算并显示report\n    report.show()\nfinally:\n    spark.stop()','finally在这里主要保证哪条路径？',
        ['异常时也尝试清理','异常被修成成功','原文件自动删除'],
        ['对，清理也要覆盖异常路径。','原异常仍需正确报告和处理。','stop负责计算资源，不删除CSV。'],
        '程序能跑通，不只看屏幕上有没有表，还要检查结果与预期一致、收尾路径清楚。下载任务可换数据运行验证；网页推演本身不会启动Spark，也不会把你标记为已完成真实编程。',
        '进程崩溃、强制终止或清理自身失败仍需环境处理；finally不是一切故障的绝对保证。',
        ('独立脚本统计途中抛错，怎样仍尝试释放自己创建的会话？',['在finally中stop','只在成功末尾stop','删输入文件代替stop','吞掉异常宣称成功'],'清理覆盖异常路径，不伪造成功。'),
        ('本机运行新CSV结果与预期不同，但程序没有异常，应怎样评价？',['先修结果差异','无异常就是计算正确','只看打印格式通过','直接删除原预期值'],'环境能启动与业务结果正确不是同一个验收。'))

    return lessons,guides,delayed,dict(version=1,scope='L0',lessons=bank)


def assets():
    prefix=ROOT/'frontend/public/practice/l0-first-run'
    common='''from pyspark.sql import SparkSession


def main():
    import sys
    spark = (SparkSession.builder.master("local[2]")
             .appName("first-sales").getOrCreate())
    try:
        summarize(spark, sys.argv[1] if len(sys.argv) > 1 else "sales.csv").show()
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
'''
    starter='''"""Complete summarize; keep the provided runner and cleanup."""

def summarize(spark, csv_path):
    # CSV header: region,amount; schema: region string, amount long.
    # Return a DataFrame with columns region and sum(amount), one row per region.
    raise NotImplementedError("Read the CSV and compute each region's amount sum")


'''+common
    reference='''"""Read after an independent attempt; works with new CSV inputs too."""

def summarize(spark, csv_path):
    df = (spark.read.option("header", True)
          .schema("region string, amount long").csv(csv_path))
    return df.groupBy("region").sum("amount")


'''+common
    verifier='''"""Small local program checks. No app data, grades, or persistent output files."""
import argparse
import csv
import importlib.util
import os
from pathlib import Path
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--solution", default="starter.py")
    args = parser.parse_args()
    path = Path(args.solution).resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    spec = importlib.util.spec_from_file_location("learner_solution", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
    from pyspark.sql import SparkSession, DataFrame
    spark = (SparkSession.builder.master("local[2]")
             .appName("first-sales-check").config("spark.ui.enabled", "false")
             .config("spark.ui.showConsoleProgress", "false")
             .config("spark.driver.host", "127.0.0.1")
             .config("spark.driver.bindAddress", "127.0.0.1")
             .config("spark.sql.shuffle.partitions", "2").getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    cases = [
        ([("east", 4), ("east", 9), ("west", 2)], {"east": 13, "west": 2}),
        ([("north", 3), ("north", 3), ("south", 0)], {"north": 6, "south": 0}),
        ([], {}),
        ([("west", 1), ("north", 2), ("west", 5), ("east", 7)], {"west": 6, "north": 2, "east": 7}),
    ]
    try:
        with tempfile.TemporaryDirectory(prefix="spark-first-check-") as folder:
            for index, (rows, expected) in enumerate(cases):
                sample = Path(folder) / (str(index) + ".csv")
                with sample.open("w", encoding="utf-8", newline="") as stream:
                    writer = csv.writer(stream)
                    writer.writerow(["region", "amount"])
                    writer.writerows(rows)
                result = module.summarize(spark, sample.as_uri())
                assert isinstance(result, DataFrame), "Return a DataFrame"
                assert set(result.columns) == {"region", "sum(amount)"}, "Check output columns"
                records = result.collect()  # only these tiny verification fixtures
                actual = {r["region"]: r["sum(amount)"] for r in records}
                assert len(records) == len(actual), "Duplicate output region"
                assert actual == expected, "Case %s: expected %r, got %r" % (index, expected, actual)
                print("PASS case", index + 1, flush=True)
        print("PASS four small fixtures; not a production benchmark or automatic course grade", flush=True)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
'''
    readme='''第一个PySpark程序：小CSV地区汇总

把这些文件放在同一目录，在终端进入该目录。
环境：Python、pyspark包和兼容的Java。按实际Spark版本核对官方安装要求：
https://spark.apache.org/docs/3.5.7/api/python/getting_started/install.html
版本不兼容或无法启动属于环境失败，不等于课程知识作答错误。

先填写starter.py里的summarize(spark, csv_path)。
输入CSV带region,amount表头；region是非空地区文本，amount是非负整数。
同一地区每行贡献都必须计入，重复行不会自动去重；空输入应没有分组。
返回DataFrame，列名region和sum(amount)，每地区一行；不要求输出排序。
本任务不处理NULL、坏记录或小数金额；这些在后续课程学习。

运行自己的程序：python starter.py sales.csv
样例应得到north=20、south=5；不能只写死这份答案。
换输入验证：python verify.py --solution starter.py
验证器使用四份独立小CSV，包含重复记录、零金额、空输入与新地区。
它只在临时目录写入并清理测试文件；不访问应用数据库，不提交课程成绩。
本地PASS只说明这些小样例通过，不认证独立编程能力或生产性能。

先独立尝试，再看reference.py；可对照运行：
python verify.py --solution reference.py
参考代码中count数行、groupBy分组、sum求和；show只显示结果，stop释放资源。
网页的推演不会执行Spark，真实运行需要本地环境。
'''
    return {prefix/'starter.py':starter,prefix/'reference.py':reference,prefix/'verify.py':verifier,
            prefix/'README.txt':readme,prefix/'sales.csv':'region,amount\nnorth,12\nnorth,8\nsouth,5\n'}


def outputs():
    lessons,newguides,newdelayed,bank=build()
    guides=json.loads((CONTENT/'standardGuides.json').read_text(encoding='utf-8'))
    delayed=json.loads((CONTENT/'delayedChecks.json').read_text(encoding='utf-8'))
    guides['version']=max(guides['version'],9); guides['lessons'].update(newguides)
    delayed['version']=max(delayed['version'],7)
    delayed['items']=[i for i in delayed['items'] if not i['slug'].startswith('l0-')]+newdelayed
    delayed['items'].sort(key=lambda i:(i['slug'],i['id']))
    kit=assets()
    downloads=[('任务说明 README.txt','README.txt'),('三条订单 sales.csv','sales.csv'),('填写代码 starter.py','starter.py'),('换数据验证 verify.py','verify.py')]
    project=dict(downloads=[dict(label=label,href='/practice/l0-first-run/'+name) for label,name in downloads],
                 solution=dict(label='下载参考实现 reference.py',href='/practice/l0-first-run/reference.py'),
                 solutionNote='先独立填写，再对照参考实现。verify.py会换四份小CSV检查结果，使用临时文件，不提交课程成绩。',
                 checksums={'/practice/l0-first-run/'+p.name:hashlib.sha256(text.encode('utf-8')).hexdigest() for p,text in kit.items()})
    lessons['l0-first-pyspark-program']['project']=project
    result={CONTENT/'lessons'/f'{slug}.json':json.dumps(l,ensure_ascii=False,indent=2)+'\n' for slug,l in lessons.items()}
    result.update({CONTENT/'standardGuides.json':json.dumps(guides,ensure_ascii=False,indent=2)+'\n',
                   CONTENT/'delayedChecks.json':json.dumps(delayed,ensure_ascii=False,indent=2)+'\n',
                   ROOT/'backend/app/l0_reviewed_bank.json':json.dumps(bank,ensure_ascii=False,indent=2)+'\n'})
    result.update(kit)
    return result


if __name__=='__main__':
    for path,text in outputs().items():
        if '--check' in sys.argv:
            assert path.read_bytes()==text.encode('utf-8'), f'Authoring drift: {path}'
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(text,encoding='utf-8',newline='\n')
    print('PASS L0: five lessons / 25 steps / 50 purpose questions / five remedies and delayed checks / small CSV kit')
