"""Explicit v2 L1 materials and focused L6/L7 option repairs.

Authors call apply() before emitting their canonical bank. Revised prompts get
new rows on installation; old IDs and grading remain intact.
"""
from copy import deepcopy
from pathlib import Path
import json

# Each objective has independent assessment and return-visit material.
# Correct answer first; output preserves the source's balanced answer positions.
L1 = {
'l1-what-is-rdd': [
 ('parts','sc.parallelize([2,4,6,8,10,12],3)在local[2]中创建。能确定的是？',['3个分区','3台机器','3个同时运行的任务','每个分区必定1个元素'],
  '12个元素分为4个分区、可用2个槽位。分区数代表什么？',['4份逻辑数据','4个并发槽位','4份完整副本','4台物理机器'],'分区是数据的逻辑份数，并发还取决于可用资源。'),
 ('immutable','a包含2、5；b=a.map(lambda x:x+3)。a请求结果仍是？',['2、5','5、8','3、3','只剩8'],
  'a包含4、9；b=a.filter(lambda x:x>5)。随后a.count()是多少？',['2','1','0','9'],'转换生成新RDD，不就地修改原RDD。'),
 ('recover','没有缓存副本或检查点，某分区丢失；上游仍可读，转换可重算。重建依据是？',['血缘依赖','结果排序','分区编号','Driver变量名'],
  '重算需要的源文件已不可读。仅有血缘能保证恢复原值吗？',['不能保证','能，从编号恢复','能，从函数名恢复','能，补零即可'],'血缘记录依赖和计算规则，重算仍需要可用上游。'),
 ('storage','只创建RDD、未调用cache或persist。哪项有证据？',['已有RDD定义','所有分区已缓存','首分区已缓存','结果已永久写出'],
  '仅看到rdd变量存在，能确认哪件事？',['定义已创建','缓存已填满','磁盘副本已持久化','全部结果已回传'],'创建抽象不等于缓存或完成结果求值。'),
 ('result','a为1、3，b=a.map(lambda x:x*2)。分别请求后，b应包含？',['2、6','1、3','3、5','只有6'],
  'x为2、8，y=x.filter(lambda n:n<5)。请求y得到？',['2','2、8','8','0'],'原查询保持不变，新查询按转换规则得到自己的结果。'),
],
'l1-transformation': [
 ('map','输入2、4、5，map(lambda x:x*x)请求结果后是？',['4、16、25','2、4、5','4、8、10','只有25'],
  '输入1、3，map(lambda x:x+2)后有几个输出元素？',['2','1','3','5'],'map对每个输入应用函数，各产生一个输出。'),
 ('flatmap','输入"red blue"、"red"，flatMap(split)后有几个词元素？',['3','2','1','0'],
  '输入""、"a a"、"b"，flatMap(split)后有几个词元素？',['3','2','1','4'],'展开保留每次出现；空行split结果为空列表，不贡献词。'),
 ('filter','输入-3、0、2、6，filter(lambda x:x>0)保留？',['2、6','0、2、6','3、0、2、6','只有6'],
  '输入1、4、7，先map加1，再filter大于4，留下？',['5、8','4、7','2、5、8','只有8'],'按转换顺序求值；filter筛选，不改写元素。'),
 ('shape','两行文本分别split；希望每个RDD元素仍是一行的词列表，应选？',['map(split)','flatMap(split)','filter(split)','count()'],
  '要把各行拆成独立词供后续计数，哪一步完成这一层展开？',['flatMap(split)','map(split)','filter(split)','collect()'],'map保留函数返回的列表元素，flatMap展开这一层。'),
 ('chain','只定义map后filter，尚未请求结果。此时建立的是？',['计算依赖链','两个完成的job','两份热缓存','一个已回传列表'],
  '看到源码调用三个转换，就能确定运行时三个stage吗？',['不能直接确定','一定是三个','一定只有一个','一定还没有RDD'],'转换调用数与运行时job/stage数没有逐行对应关系。'),
],
'l1-action': [
 ('count','过滤后只需要总条数，直接调用？',['count()','collect()','map()','cache()'],
  'a含1、3、5、7，a.filter(lambda x:x>3).count()返回？',['2','4','3','7'],'count返回数量，仍可能执行上游转换。'),
 ('collect','只预览5条，Driver容量有限，先用哪种方式限制返回数量？',['take(5)','collect()[:5]','cache().collect()','map(lambda x:x).collect()'],
  '先collect全部再切片，能避免全集回传Driver的风险吗？',['不能，切片在回传后','能，只保留切片内数据','能，Python会改写Spark计划','能，切片会取消其余任务'],'先限制返回规模；本地切片不能撤销已经发生的collect。'),
 ('closure','任务在foreach中append普通Python列表，能把它当Driver全局汇总接口吗？',['不能这样依赖','所有任务共享该列表','仅首分区共享该列表','同名变量会自动合并'],
  '分布式任务中给普通闭包变量加1，Driver读到0。优先理解为？',['任务状态不等于Driver共享状态','所有任务均未运行','RDD输入必定为空','变量名被Spark忽略'],'闭包副作用不是可靠的分布式结果收集接口。'),
 ('again','未持久化，第一次count结束后再次请求同一RDD，哪项仍可能发生？',['上游重算','复用完整热缓存','只读取上次计数','返回首次请求的明细列表'],
  '只因一次action成功，就认定下一次无需计算，缺少什么？',['可复用状态的证据','变量名足够短','相同输出列顺序','action调用行号'],'action不自动把全部计算结果永久缓存。'),
 ('bounded','take(4)返回4条，可据此认定Driver已收到完整十亿条结果吗？',['不能，只请求有界结果','能，take内部等于全量回传','能，返回4就是总共4条','能，其他行已被删除'],
  '取少量结果后能保证上游工作量也固定很小吗？',['不能，还要看上游依赖','能，只算返回的几行','能，所有聚合都会跳过','能，所有分区都不执行'],'限制返回数量不等于保证上游读取或聚合成本极小。'),
],
'l1-lazy-evaluation': [
 ('definition','建立平方RDD后只打印type，确认了什么？',['创建了查询对象','取回了全部平方值','保存了永久结果','填满了缓存'],
  '建立过滤RDD后尚未请求结果，下一步count的角色是？',['请求求值并返回数量','只重命名查询对象','只登记缓存策略','只打印Python类型'],'区分查询定义与请求结果。'),
 ('branches','定义a=base.filter(正数)、b=base.filter(负数)，仅a.count()。工作需求沿哪里追踪？',['a的依赖','a和b全部分支','只沿最后定义的b','不再需要base'],
  '先定义p和q，随后仅q.take(2)，p是否因变量存在就必完整运行？',['不必','必定完整运行','只有p会运行','p已自动缓存'],'action由其所需依赖驱动，不因定义了变量就遍历所有分支。'),
 ('persist','cache后尚无遍历，哪项已经确认？',['登记了缓存意图','缓存全部物化','结果全部回传','源文件已经删除'],
  'persist后只请求少量元素，能保证所有分区已经热缓存吗？',['不能保证全量','已经全部物化','已经永久写出','下一次必不计算'],'登记持久化与实际物化分开，部分请求不证明全量就绪。'),
 ('retry','任务写外部系统后重试，哪种设计有助于防止重复业务写入？',['幂等写入或提交协议','依靠RDD变量不变','增加map调用次数','把输出列重新命名'],
  '任务已向外部写入但确认丢失，直接重试会有什么风险？',['重复写入','自动回滚全部外部数据','只重写Python变量','所有重试自动跳过副作用'],'RDD容错不代替任意外部系统的事务协议。'),
 ('request','b=a.map加1，c=b.filter正数；只请求c.count()。b在此处是什么？',['c所需的上游依赖','必独立完成的第二个job','已经落盘的中间文件','和c无关的未使用分支'],
  '先定义转换链再调用collect，结果回传由哪一步请求？',['collect','第一个map','最后一个filter','变量赋值'],'推迟求值不等于上游依赖无须执行。'),
],
'l1-why-dataframe-replaces-rdd': [
 ('structured','已有team、amount字段，要按team汇总，优先用哪种结构化表达？',['DataFrame/SQL聚合','把全表拼成字符串','按行号关联字段','先collect全部明细'],
  '订单有清晰字段与类型，要筛选并分组，哪种方式更直接暴露列关系？',['内置列表达式','任意Python对象函数','普通闭包列表修改','字符串化整行处理'],'列与关系表达暴露更多可分析结构。'),
 ('schema','金额显示为"12"，准备建立结构化列，仍需明确什么？',['类型与输入规则','仅显示宽度','仅变量名称','仅原始行号'],
  '字段允许NULL但业务要求有效金额，Schema能替代所有质量校验吗？',['不能，还需业务检查','能，类型通过即业务有效','能，NULL会自动补合法金额','能，转换会自动删除冲突'],'类型契约和业务质量约定互相补充。'),
 ('opaque','把列表达式封入任意Python函数体，能假定优化器看到相同语义吗？',['不能这样假定','函数名称相同就能','惰性执行就能','返回列名相同就能'],
  '两段代码输出相同，Python UDF与内置表达式的执行边界能直接视为相同吗？',['不能直接视为相同','相同列名就相同','同样行数就相同','使用相同变量就相同'],'表达能力与执行边界需要分别验证。'),
 ('rdd','确需低层分区处理，合理选择是？',['按需求评估RDD及转换成本','禁止一切RDD操作','先收集全表再分区','按API名称决定结果正确'],
  '现有DataFrame流程中需要特殊分区逻辑，先做什么？',['评估接口边界与正确性','直接宣布RDD永远更快','直接宣布RDD不再可用','忽略Schema转换的成本'],'工具选择依赖具体需求和成本。'),
 ('measure','改为DataFrame后结果与原流程不同，能只凭接口名称验收吗？',['不能，先查语义差异','能，结构化接口保证业务正确','能，行数减少即可','能，只要代码更短'],
  '两种实现结果相同，只测过一次小样本，能保证所有生产负载更快吗？',['不能，仍需代表性测量','能，同结果就同收益','能，使用SQL就有固定倍数','能，小样本决定所有规模'],'语义验证与性能测量支持的结论范围不同。'),
],
'l1-rdd-exercise': [
 ('normalize','约定空白分词并小写，"Go GO go"中go计数？',['3','1','2','0'],
  '保留标点并小写，"Hi hi! HI"中hi计数？',['2','3','1','0'],'大小写归一不等于去重或删除标点。'),
 ('pairs','"A b a"分词小写后，计数前应得到哪些卡片？',["(a,1),(b,1),(a,1)","(a,2),(b,1)","(a,1),(b,1)","(a,3),(b,3)"],
  '"x X"归一后，两次出现应分别贡献什么？',["(x,1),(x,1)","(x,2)","(x,1)","(x,0),(x,0)"],'每次出现先映射为词与1，再按键求和。'),
 ('empty','输入仅"  "和空行，词频输出应是？',['空键集合','空词计数2','空词计数1','沿用上一批计数'],
  '空输入参与词频统计，是否应为每个分区补造一个词？',['不应造词','应各造一个空词','应补上上次结果','应补一个总数为1的词'],'空白分词不贡献词，不能凭空制造键。'),
 ('sum','同词两个局部计数为4与7，合并为？',['11','4','7','2'],
  '同词三个局部计数为1、2、5，合并为？',['8','5','3','1'],'按键合并应累加全部合法贡献。'),
 ('partitions','同文本从2改成4分区，验收必须保持什么？',['每词整数计数','输出遍历顺序','每词所在机器','每个任务耗时'],
  '新数据中词分布改变，程序仍固定返回样例词频，问题是？',['没有按实际输入计算','分区数量太少','输出排序方式不同','变量名称不一致'],'实现按契约计算输入，分区布局变化不应改变业务计数。'),
],
}

# Focused replacements for the most conspicuous formal-question distractors.
# Existing numeric questions remain intact; their alternatives are already parallel.
FORMAL = json.loads(Path(__file__).with_name('question_choice_edits.json').read_text(encoding='utf-8'))


def apply(bank):
    result = deepcopy(bank)
    for entry in result['lessons']:
        slug = entry['lesson_slug']
        if slug in L1:
            old = entry['questions']
            questions = []
            for j, (key, pa, oa, pb, ob, why) in enumerate(L1[slug]):
                task_suffix = {'parts':'parts','recover':'recover','result':'immutable','storage':'storage',
                    'shape':'flatmap','bounded':'collect','request':'branches','pairs':'bridge-key-value',
                    'structured':'schema','opaque':'optimizer','rdd':'still-rdd','measure':'still-rdd',
                    'definition':'predict','retry':'recovery','partitions':'accept',
                    'closure':'foreach','schema':'bridge'}.get(key,key)
                for i, (prompt, options) in enumerate(((pa,oa),(pb,ob))):
                    q = deepcopy(old[j*2+i])
                    choices = options[1:].copy(); choices.insert(q['correct_index'],options[0])
                    q.update(key=f'{slug}/{key}/{q["purpose"]}-v2',knowledge_id=f'{slug}/{key}',
                        prompt=prompt,options=choices,explanation=why,task_id=f'{slug}/{task_suffix}')
                    questions.append(q)
            entry['questions'] = questions
        elif slug in FORMAL:
            for q in entry['questions']:
                key = q['knowledge_id'].split('/')[-1]
                if key not in FORMAL[slug]:
                    continue
                choices = FORMAL[slug][key]
                wrong = choices[1:].copy(); wrong.insert(q['correct_index'],choices[0])
                q.update(key=q['key'].replace('-v1','-v3'),prompt='独立验证：'+q['prompt'],options=wrong)
                if q['purpose'] != 'assessment':
                    revised_prompts = {
                        ('l6-broadcast-hash-join','build'): '事实表很大、维表很小，BHJ以维表构建。主要复制什么给执行节点？',
                        ('l6-broadcast-hint-and-control','intent'): 'SQL中的BROADCAST(dim)主要表达什么？',
                        ('l6-sort-merge-join','resource'): '排序合并连接可以因为不建哈希表而保证没有内存压力吗？',
                    }
                    if (slug,key) in revised_prompts:
                        q['prompt'] = revised_prompts[slug,key]
        elif slug == 'l7-executor-memory':
            # Match new M/R bridge teaching instead of re-testing cache economics.
            rows = [
                ('driver','collect后Driver失败、Executor未报告同样错误，先检查？',['Driver结果回传规模','Executor缓存块数量','Executor聚合状态大小','Shuffle写出文件数量'],
                 '只需要少量预览，哪种动作优先限制Driver返回规模？',['take(5)','collect()[:5]','cache().collect()','collect后再过滤'],'先定位失败进程，再限制结果回传。'),
                ('scope','节点总内存上升，能把全部占用都算作JVM heap吗？',['不能，需分进程核对','能，Python与JVM共用同一堆','能，缓存块代表所有占用','能，节点占用就是heap上限'],
                 'Python进程占用上升但JVM heap稳定，下一步更合理的是？',['检查Python及节点限制','只提高JVM堆内缓存比例','仅查看缓存块数量','仅增加广播阈值'],'JVM、Python和其他开销不是同一统计口径。'),
                ('idle-borrow','简化容量图M=100、R=50，当前E=0、S=0。执行请求70，会被R固定卡在50吗？',['不会，空闲可共享','会，R是执行的上限','会，必须先装入50缓存','会，执行只能用M-R'],
                 'M=120、R=60且无执行占用，空闲充分。缓存能否使用超过60的空间？',['可以，R不是缓存上限','不能，R是缓存绝对上限','不能，执行必须永久占一半','不能，空闲也只能由执行用'],'空闲可共享，R是缓存保护阈值，不是双方固定配额。'),
                ('reclaim','简化模型M=100、R=50、S=80、E=0；执行目标40。先用空闲后，仅回收不足部分，应逐出多少缓存？',['20','40','50','80'],
                 '简化模型M=200、R=80、S=160、E=0；执行目标100。仅回收不足部分，逐出多少？',['60','100','80','160'],'先用已有空闲，再回收R以上缓存中满足目标所缺部分；不模拟块粒度或任务公平性。'),
                ('protected','M=100、R=50、S=80、E=0；仅凭空闲和保护线外缓存，执行最多可获得多少？',['50','20','80','100'],
                 'M=100、R=50、E=80、S=0；缓存请求50，能逐出30执行占用来满足吗？',['不能，存储不逐出执行','能，R保证即时分配50','能，双方能任意抢占','能，缓存优先于执行'],'执行回收缓存有保护阈值；存储不能反向逐出执行已占用空间。这是总体容量模型，不是单任务配额保证。'),
            ]
            old=entry['questions']; qs=[]
            links=['driver','scope','bridge-idle-borrow','bridge-execution-reclaim','bridge-protected-limit']
            for j,(key,pa,oa,pb,ob,why) in enumerate(rows):
                for i,(prompt,options) in enumerate(((pa,oa),(pb,ob))):
                    q=deepcopy(old[j*2+i]); choices=options[1:].copy();choices.insert(q['correct_index'],options[0])
                    q.update(key=f'{slug}/{key}/{q["purpose"]}-v2',knowledge_id=f'{slug}/{key}',prompt=prompt,
                        options=choices,explanation=why,task_id=f'{slug}/{links[j]}')
                    qs.append(q)
            entry['questions']=qs
    if any(e['lesson_slug'] in L1 or e['lesson_slug'] in FORMAL or e['lesson_slug']=='l7-executor-memory' for e in result['lessons']):
        result['version']=3
    return result
