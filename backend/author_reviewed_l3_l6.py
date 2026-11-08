"""Purpose-separated L3-L6 questions: 180 explicit objectives, two materials each.
Five assessment + three review + two remediation per lesson. No DB writes.
Each pair shares a learning objective; do not call 360 rows 360 concepts.
"""
from pathlib import Path
import json
import sys

cards = {}
def c(slug,key,a,b,right,w1,w2,w3,why):
    cards.setdefault(slug,[]).append((key,a,b,right,w1,w2,w3,why))
def value(x,v):
    return x[v] if isinstance(x,tuple) else x

# L3: new materials rather than copying the tutorial questions.
s='l3-what-is-spark-sql'
c(s,'entry','只有变量 stock_df，SQL 尚无 stock 关系。要查这批库存，应先？','只有 Python 变量 visits，SQL 中尚无 visits 关系。希望按此名查询，应先？','把目标 DataFrame 注册为所用临时视图名','先 show，名称会自动登记','把变量变成字符串','先 collect 全表才能查询','Python 变量不会自动成为 SQL 关系名；临时视图是一种命名入口。')
c(s,'result','q=spark.sql("SELECT sku FROM stock")，q 还可做什么？','q=spark.sql("SELECT event_id FROM events")，哪种后续有效？','继续用 DataFrame API 组合查询','只能处理字符串字符','必须已经是 Python 列表','必须先持久化为表','普通 SELECT 返回 DataFrame，可与 API 衔接。')
c(s,'equivalence','对同一输入，SQL 与 API 均表达 price>30 的同列投影。可判断？','对同一输入，两接口均按 dept 求相同指标。应先如何理解？','先核对等价语义，性能仍看计划与测量','SQL 必快一倍','API 不能做聚合','物理计划和秒数无条件完全相同','共享优化体系不提供任意写法的固定性能承诺。')
c(s,'command','执行 INSERT INTO audit SELECT * FROM batch，未接 show。可认定没写入吗？','执行 CREATE TEMP VIEW 命令后没有 show，能说目录一定未改变吗？','不能，命令与 SELECT 查询须分开理解','能，所有 sql 都无副作用','能，必须 collect 命令才执行','能，只有 Python write 能写入','SQL 命令可能在调用时执行，不能一概套用 SELECT 的惰性。')
c(s,'source','SQL 除临时视图，还可能从哪里读数据？','查询命名关系时，能否把 SQL 限定为只能读取 Python 临时视图？','还可访问目录表及支持的数据源路径','只能从 Python 列表','只能从本地字符串常量','必须把所有数据变成 pandas','临时视图不是 SQL 唯一数据入口。')
s='l3-temp-views'
c(s,'target','cleaned 已过滤，raw 未过滤。SQL v 应指向 cleaned，应注册谁？','selected 已选目标字段，source 仍全列。v 要对应 selected，应注册谁？',('cleaned','selected'),('raw','source'),'任意对象都一样','先 show 后会自动选择','注册对象决定 SQL 名称对应哪份查询。')
c(s,'replace','v 注册旧 df 后，仅把 Python df 重新赋值。v 自动更新吗？','把 Python 变量重新绑定到新文件查询，未重新注册 old_view，视图会自动替换吗？','不会，需要重新注册替换定义','会，变量名是动态指针','会，所有视图自动跟随变量','视图必定删除','视图登记与 Python 变量重新绑定不同。')
c(s,'global','同一应用中新建 session，要查全局临时视图 metrics，用？','同一 Spark 应用内另一 session 要访问全局临时视图 inventory，用？',('global_temp.metrics','global_temp.inventory'),('metrics','inventory'),('local.metrics','local.inventory'),'任意 Python 变量名','全局临时视图使用 global_temp 名称空间，范围是当前应用。')
c(s,'lifetime','独立退出应用后重启，global_temp.v 会永久保留吗？','普通临时视图想留给明天独立程序，单靠注册足够吗？','不足，需要持久数据与访问约定','足够，global 表示永久','足够，临时视图自动写文件','只要变量同名就能恢复','临时视图不是跨独立应用的持久交付机制。')
c(s,'cache','createOrReplaceTempView 是否自动缓存全部数据？','注册报表临时视图是否等于把查询物化并写到磁盘？','不是，命名、缓存、保存是不同操作','是，注册必定复制全表','是，自动建立 Parquet','是，自动给每行做备份','注册视图主要登记查询定义，不替代缓存或保存。')
s='l3-select-basics'
c(s,'literal',"sku='pen'。SELECT sku,'sku' AS tag，tag 是？","name='Lee'。SELECT name,'name' AS tag，tag 是？",('字符串 sku','字符串 name'),('pen','Lee'),'NULL','字段名错误','单引号内是常量，不是列引用。')
c(s,'units','fee=450 元，SELECT fee/1000.0 AS fee_k 的值？','fee=750 元，SELECT fee/1000.0 AS fee_k 的值？',('0.45','0.75'),('450000','750000'),('450','750'),'NULL','从元到千元除以一千，别名应表达单位。')
c(s,'identifier','字段名是 net amount，引用它应写？','字段名是 user label，引用它应写？',('`net amount`','`user label`'),("'net amount'","'user label'"),('net amount','user label'),'只能先 collect','反引号引用含空格标识符，单引号是字符串常量。')
c(s,'distinct','数据 city/value 为 A/1、A/2、B/1。SELECT DISTINCT city 几行？','数据 sku/qty 为 X/4、X/9、Y/4。SELECT DISTINCT sku 几行？','2','1','3','0','去重依据是输出字段，不是未选择的原始明细列。')
c(s,'alias','SELECT cost*2 AS doubled FROM t，输出表达式列名？','SELECT age+2 AS age_later FROM t，输出表达式列名？',('doubled','age_later'),('cost','age'),'固定叫 value','自动保留两个同名列','AS 为输出表达式指定名称，原字段是否保留取决于投影。')
s='l3-where-order-limit'
c(s,'conditions',"A:east/50,B:west/180,C:east/160，WHERE city='east' AND amount>100 留下？","A:blue/20,B:red/90,C:blue/80，WHERE team='blue' AND score>50 留下？",'只有 C','A 和 C','B 和 C','全部','AND 要两项同时为 true。')
c(s,'null','WHERE updated_at=NULL 为什么筛不到缺失时间？','WHERE price=NULL 为什么不等同于 price IS NULL？','普通比较得到未知，过滤只保留 true','缺失列永远是空字符串','SQL 不允许任何 NULL','NULL 比较一定是普通 false','NULL 的普通比较是未知，缺失判断使用 IS NULL。')
c(s,'limit','没有 ORDER BY 的 LIMIT 3 能保证什么？','没有排序约定的 limit(4) 是均匀抽样吗？','只约束数量，不保证最大或随机','保证最大值集合','保证均匀随机样本','保证最早导入记录','LIMIT 不表达稳定顺序或随机抽样。')
c(s,'tie','A:90,B:90,C:100，ORDER BY score DESC,id ASC LIMIT 2 得到？','A:60,B:60,C:80，ORDER BY score DESC,id ASC LIMIT 2 得到？','C、A','C、B','A、B','B、C','第二排序键决定同分记录的稳定取舍。')
c(s,'empty','phone 为 NULL、空字符串、555，WHERE phone IS NULL 留下？','tag 为 NULL、空字符串、X，WHERE tag IS NULL 留下？','仅 NULL 行','仅空字符串行','两种缺失都自动保留','没有行','空字符串不是 NULL，需要另定义业务缺失规则。')
s='l3-groupby-having'
c(s,'stage','A:30+90，B:95，GROUP BY city HAVING SUM(v)>100 保留？','A:50+70，B:99，GROUP BY k HAVING SUM(v)>100 保留？','只有 A','只有 B','A、B 都保留','都不保留','HAVING 比较组内合计，不能以逐笔大额筛选替代。')
c(s,'count','同组 v=5,NULL,9,NULL，COUNT(*) 与 COUNT(v)？','同组 v=NULL,8,NULL,3，COUNT(*) 与 COUNT(v)？','4、2','2、2','4、4','2、4','COUNT(*) 计行，COUNT(列) 只计非空。')
c(s,'grain','SELECT city,id,SUM(v) GROUP BY city，id 未聚合，问题？','SELECT dept,name,COUNT(*) GROUP BY dept，name 未聚合，问题？','组内普通字段取值未定义，需要明确粒度','Spark 自动稳定取第一条','只需加 LIMIT','字段名越短越正确','非分组字段不能不定义选择规则就进入汇总结果。')
c(s,'allnull','同组金额全 NULL，SUM(amount) 返回？','同组时长全 NULL，AVG(duration) 返回？','NULL','0','行数','空字符串','SUM/AVG 的全空组结果不是自动补零。')
c(s,'outer','聚合结果在外层 SELECT 中作为普通列 total。外层 WHERE total>100 可以吗？','先将按地区合计注册成 report，再 WHERE total>200，可以吗？','可以，外层看到的是已聚合结果','永远不能用 WHERE 筛汇总列','必须改回逐行 amount 条件','必须 collect 后筛','同层 WHERE 与 HAVING 的阶段区别不禁止外层筛聚合列。')
s='l3-joins-intro'
c(s,'inner','订单 o1/u2,o2/u8，用户只有 u2/Lin，INNER JOIN 输出？','订单 o1/u3,o2/u9，用户只有 u3/Kai，INNER JOIN 输出？',('仅 o1/Lin','仅 o1/Kai'),'两张订单都保留且补 NULL','没有行','把用户名填给所有订单','INNER 仅保留满足条件的匹配行对。')
c(s,'multiply','同键左 4 行，右 2 行，全部等值匹配，输出几行？','同键左 2 行，右 5 行，全部等值匹配，输出几行？',('8','10'),('4','5'),('6','7'),'1','同键匹配按行对组合，不能当作自动去重。')
c(s,'types','字符串键和整数键比较，尚未看值和配置，能说全不匹配吗？','不同类型连接键出现问题，能只凭类型不同断定结果为空吗？','不能，核对转换规则、实际值与配置','可以，绝对全部不匹配','名字相同就一定匹配','任何情况下必定报错','转换、坏值和设置会影响行为，类型不同不是固定空结果保证。')
c(s,'alias','o 和 u 都有 id，想明确引用用户侧，写？','a 和 b 都有 key，想明确引用 b 侧，写？',('u.id','b.key'),("'u.id'","'b.key'"),('id','key'),'COUNT(*)','用关系别名限定字段来源，避免同名列歧义。')
c(s,'unique','订单一行 40 元，维表同键三行，INNER 后 SUM(amount)？','订单一行 30 元，维表同键四行，INNER 后 SUM(amount)？','120',('40','30'),('3','4'),'0','维表重复会复制订单贡献，聚合前需验证键约定。')
s='l3-functions-and-udf'
c(s,'builtin',"UPPER(TRIM(' jo ')) 返回？","UPPER(TRIM(' li ')) 返回？",('JO','LI'),(' JO ',' LI '),('jo','li'),'NULL','先去首尾空格，再大写。')
c(s,'coalesce',"COALESCE('', 'NA') 返回？","COALESCE('', 'fallback') 返回？",'空字符串',('NA','fallback'),'NULL','报列名错误','COALESCE 只跳过 NULL，空字符串仍是非空值。')
c(s,'case',"x=NULL，CASE WHEN x IS NULL THEN 'missing' ELSE 'ok' END？","x=NULL，CASE WHEN x IS NULL THEN 'unknown' ELSE 'known' END？",('missing','unknown'),('ok','known'),'0','NULL','显式 NULL 分支可表达缺失标签。')
c(s,'register','Python 函数已验证，SQL 报函数名未解析，应？','DataFrame 里 F.udf 包装过函数，想按名称在 SQL 调用，还需要？','用 spark.udf.register 登记 SQL 名称和返回类型','只改 Python 变量名','只对 DataFrame 调 show','先把整个表 collect','列表达式包装不自动等于 SQL 函数名注册。')
c(s,'performance','内置能表达需求时，为何先比较内置而非直接 Python UDF？','想用 UDF 做简单大写，应优先核对什么？','可避免不必要的 Python 边界，收益仍需测量','UDF 任何场景必慢万倍','pandas UDF 任何场景必更快','内置函数保证绝不会占内存','优先表达能力与执行路径，避免无依据的绝对性能结论。')
s='l3-tables-and-formats'
c(s,'catalog','没有外部 Hive Metastore，能一概说所有目录表只活在 session 吗？','目录表重启后缺失，应只用“没 Hive”解释吗？','不能，检查 catalog 与元数据持久化约定','能，所有表只有临时视图','能，数据源表不可能存在','只看变量名即可','临时视图与数据源目录表不同，持久性取决于配置。')
c(s,'path','parquet.`/practice/items` 中前后分别是什么？','json.`/practice/events` 中前后分别是什么？','数据源格式与可信文件路径','数据库密码与用户名','输出字段与别名','两个 Python 变量','支持的数据源路径可直接成为 SQL 读取入口。')
c(s,'append','空练习表每批 6 行，INSERT INTO 两次，最终多少？','空练习表每批 7 行，INSERT INTO 两次，最终多少？',('12','14'),('6','7'),'0','1','追加不自动按批次幂等。')
c(s,'overwrite','希望替换目标表结果，应区分哪种语义？','同批完整结果重跑，不希望反复追加，应首先考虑？','覆盖与追加的目标规则','把所有写命令当 ignore','依靠 show 自动去重','把文件重命名成相同名字','写入成功与可重跑是不同要求，需明确目标和语义。')
c(s,'target','只有输入视图存在，直接 INSERT OVERWRITE 到未知表够吗？','SELECT 成功后能认定输出目录表一定可写吗？','不够，核对目标定义、列对应与权限','够，输入存在自动创建正确目标','够，普通视图就是可写文件表','只要 LIMIT 就会成功','输入可查询不能证明输出目标存在且可写。')
s='l3-comprehensive'
c(s,'dedup','重复导入完整相同行，SQL 应怎样定义去重对象？','同订单三列完全相同，只计一次，先应做什么？','对约定的完整输出行组合 DISTINCT','只保留随机一条城市','用 LIMIT 替代去重','把金额求平均','去重应匹配业务相等约定，不能任意丢键或值。')
c(s,'threshold','组内 90+110，需求至少 200，应？','组内 80+120，需求至少 200，应？','HAVING SUM(v)>=200，保留','WHERE v>=200，保留两笔','HAVING SUM(v)>200，仍保留','LIMIT 200，自动达标','至少包含边界，且比较组内合计应在聚合后。')
c(s,'filter','明细 10、-5、NULL，仅正金额参与汇总，WHERE 应？','明细 30、0、NULL，仅正金额参与汇总，WHERE 应？','amount>0','amount IS NOT NULL','SUM(amount)>0','amount=NULL','有效明细规则不能由非空或聚合门槛替代。')
c(s,'units','total=625 元，千元字段应是？','total=875 元，千元字段应是？',('0.625','0.875'),('625000','875000'),('625','875'),'NULL','元转千元除以一千并验证输出类型。')
c(s,'accept','全表总额相同但某城市分错，验收应？','查询样本正常但写出尚未读回，能完整通过吗？','逐组/类型/文件/重跑分别验收，不能只看总计','只看 show 正常就通过','只看总额就通过','只看脚本没有异常就通过','正确性与交付可用需要多层证据。')

# L4: plan interpretation, bounded claims, and experimental evidence.
s='l4-why-explain'
c(s,'plan','计划出现 Sort 与 Exchange，能直接得出准确耗时吗？','只看到 Scan 与 HashAggregate，能认定哪个节点耗时最多吗？','不能，计划结构还需运行指标','能，节点数乘一秒','能，Exchange 固定最慢','能，最上面固定最慢','计划不是计时器，必须用运行证据验证瓶颈。')
c(s,'hypothesis','读取 40 列只用两列，应优先验证什么？','报表没用长文本，却观察到宽读取，应先检查？','列裁剪与实际读取量','立即删除源数据列','总是缓存全部宽表','增加输出行数','先验证能否减少无用读取，不破坏源数据。')
c(s,'correct','优化后更快但少一个分组，能算成功吗？','总耗时下降，但有效订单数错误，应怎样评价？','先修结果差异，正确性不满足','只要更快就是成功','少数据自然正确','按节点数打分即可','性能改动以正确业务语义为前提。')
c(s,'metrics','多数任务快但一个慢，计划只提示聚合，应再看？','只知道总耗时增长，想定位长尾，应收集？','task 分布、数据量、spill 等指标','只看 SQL 文本长度','只看颜色','只看变量名','实际负载和运行分布帮助检验计划假设。')
c(s,'experiment','A/B 使用不同输入量，可以直接算加速倍数吗？','原方案冷缓存，新方案热缓存，可直接归因于改写吗？','不能，控制或记录可比条件','可以，不必核对条件','只挑最快一次即可','必然是优化器更新','性能归因需要结果正确与实验条件可比。')
s='l4-logical-vs-physical'
c(s,'meaning','“按门店求总量”首先是哪类描述？','“把两个关系按用户键匹配”首先是哪类描述？','逻辑业务计算需求','网络端口配置','物理机器编号','磁盘目录数量','逻辑描述说明计算语义，尚未确定具体执行路线。')
c(s,'routes','同一等值连接从 SMJ 变 BHJ，必然改业务吗？','同语义聚合选择不同物理实现，必定结果不同吗？','不必，物理路线可变但应保持语义','必然，节点名不同就是不同需求','必定少算行数','只能其中一个合法','语义与实现不同层，仍需核对实际条件和结果。')
c(s,'analysis','字段拼成 pricce，实际只有 price，应先解决？','引用不存在的关系，调 Shuffle 参数能补出来吗？','名称/类型的解析分析问题','先增内存即可','先加所有 hint','先改变输出排序','语义分析错误不能靠资源调参解决。')
c(s,'optimization','优化后 Filter 和 Project 被重排，应首先核对？','表达式被折叠后与源码不同，正确理解是？','规则应保持语义，计划不是源码逐行记录','节点越少就可以改结果','所有节点必须逐字对应代码','重排必定错误','计划重写有语义约束，不应按源码逐行计数。')
c(s,'aqe','初始计划未 final，选型能当最终事实吗？','运行统计可能改变路线，比较时应看？','初始与最终计划及运行条件','只看第一次打印','只看变量名','只看 SQL 注释','AQE 可能调整部分物理路线，应保存运行证据。')
s='l4-explain-api'
c(s,'extended','要看 parsed/analyzed/optimized/physical，用？','想比较优化前后多个计划阶段，用？','extended','formatted','codegen','collect','extended 适合追踪多阶段计划。')
c(s,'formatted','要先看物理轮廓和编号细节，用？','执行树很长，想先定位节点再看属性，用？','formatted','collect','count','缓存模式','formatted 帮助分层阅读物理结构与节点细节。')
c(s,'cost','cost 中估计 30 MiB 是精确峰值内存吗？','sizeInBytes 变化可直接当内存实测变化吗？','不能，统计估计与实际工作集不同','能，精确等于峰值','能，必等于磁盘文件','能，必等于每个 task 内存','统计可能缺失、陈旧，也不是哈希构建内存上限。')
c(s,'codegen','想核对可用生成代码，应选择？','检查兼容算子的代码生成信息，应选择？','codegen','show','count','repartition','codegen 提供实现线索，不直接承诺性能。')
c(s,'execution','explain 通常会完整计算并返回业务数据吗？','打印计划是否等于完成整个写出结果？','不是，可能分析计划但不是完整业务执行验收','是，必已完整落盘','是，所有行都 collect','是，已经通过性能验收','计划分析与请求完整结果是不同操作。')
s='l4-read-plan'
c(s,'source','Aggregate <- Exchange <- Filter <- Scan，来源在哪里？','Project <- Filter <- Scan，输入从哪里进入？','Scan 叶子','最上方结果节点','所有节点各读一份全表','代码行号','从叶子识别来源，再追踪数据变换。')
c(s,'exchange','BroadcastExchange 必是双侧按键 Shuffle 吗？','存在 BroadcastHashJoin，能把所有 Exchange 当同一种吗？','不能，区分广播与 Shuffle 分布要求','可以，所有交换相同','表示完全没通信','表示所有行进入 Python','交换类型不同，不可只数单词。')
c(s,'id','*(5) Project 是否就是 Spark UI Stage 5？','formatted 节点编号 (8) 是否就是 task ID 8？','不是，编号系统需区分','是，严格一一对应','表示第五/八台机器','表示输出行数','计划节点、代码生成区域和运行任务编号不同。')
c(s,'adaptive','isFinalPlan=false，应怎样解释？','运行前 AQE 计划还未 final，下一步？','代表执行后结合最终计划与指标核对','证明 AQE 一定失败','保证路线不再变化','只看初始图就最终定论','初始计划不能冒充最终执行证据。')
c(s,'time','树上下层次等于逐秒串行顺序吗？','顶层节点一定在所有下层完全结束后单机执行吗？','不能这样推断，存在管线与并行','可以，必定逐节点串行','每层固定耗一秒','层数等于 Executor 数','计划数据流不是精确 wall-clock 调度时间表。')
s='l4-catalyst-rules'
c(s,'prune','只输出两列，ReadSchema 裁到两列，是什么证据？','宽表去掉无用描述字段，扫描结构收窄，说明？','列裁剪的结构线索，收益仍需测','所有行已自动缓存','业务行数必须减半','数据已永久删除','裁剪字段与删行、缓存、物化不同。')
c(s,'pushdown','Scan 只下推 IsNotNull，仍有残余 Filter，应？','部分谓词可由数据源处理，另一些仍在执行树中，应？','保留并核对残余过滤语义','删掉所有 Filter','宣称全部条件已下推','认为数据源已永久清洗','部分下推不能替代全部业务条件。')
c(s,'fold','v*(3+4) 可在不变语义下怎样化简？','v*(4+5) 可在不变语义下怎样化简？',('v*7','v*9'),('把 v 改成 7','把 v 改成 9'),'删除 v','直接删除所有行','常量折叠不等于覆盖输入数据。')
c(s,'join-filter','把 LEFT JOIN 后右列过滤挪位置，应先检查？','跨外连接移动条件，节点少了就够吗？','NULL 与未匹配行的语义等价','只看代码更短','只看参数更大','直接改 INNER 保证快','外连接条件移动可能改变保留行。')
c(s,'benefit','计划少一个节点就保证更快吗？','列裁剪出现后能无条件承诺固定加速吗？','不能，结合数据源和实际运行指标','能，少一个固定快一倍','能，自动不耗 CPU','能，结果无需再验','规则实施与实际收益要分别验证。')
s='l4-wholestage-codegen'
c(s,'fusion','兼容算子融合主要减少什么？','生成代码执行能改善哪类开销？','部分调用与中间交接开销','业务要求中的记录','所有网络和磁盘成本','输入字段含义','执行实现优化不能改变业务结果。')
c(s,'python','出现 Python 执行边界，应怎样检查？','简单逻辑用 UDF，计划出现 Python 节点，应先？','比较等价内置表达式并测实际开销','认定函数体全被优化器等价重写','固定宣布慢万倍','只改函数名字','检查必要性与执行成本，避免绝对倍数结论。')
c(s,'exchange','Project 融合后 Exchange 必消失吗？','代码生成可自动满足任何跨分区分布要求吗？','不能，执行融合与数据分布是不同问题','能，所有交换必被消除','能，数据自动单分区','能，所有连接变广播','代码生成不自动取消交换要求。')
c(s,'memory','用了紧凑内部表示就不会 OOM 吗？','Tungsten 相关优化能保证没有 spill 吗？','不能，工作集与并发容量仍有限','能，内存自动无限','能，算法不再存状态','能，所有数据都在磁盘不用内存','表示优化不能取消资源约束。')
c(s,'markers','多个生成代码区域一定失败吗？','没有把所有算子放在同一区域，能判定未优化吗？','不能，算子与交换可能形成合理边界','能，只允许一个区域','表示分区数错误','表示数据必重复','兼容性和边界由实际实现决定。')
s='l4-dependency-narrow-wide'
c(s,'map','单行数值加一需要其他分区贡献吗？','每行字符串去空格本身需要全局汇合吗？','本身可局部处理','必须先 collect 全表','必须全局排序','必须广播所有行','局部变换的输入需求与全局汇合不同。')
c(s,'combine','同键局部总量 14 与 21，最终一行应？','同键局部总量 16 与 24，最终一行应？',('35','40'),('14','16'),('21','24'),'任意一份','保留所有分区贡献，局部不等于全局。')
c(s,'rows','filter 减少行数就一定宽依赖吗？','flatMap 增加行数就一定宽依赖吗？','不是，依赖看是否需要跨分区贡献','是，依赖由输出行数决定','必定变成一个分区','自动消除所有后续交换','行数变化与依赖关系不同。')
c(s,'existing','已满足按键分布，聚合必再交换一次吗？','上游分布可能满足下游要求，应怎样核对？','看实际计划，可能复用已有分布','任何 groupBy 必再一次','直接跳过聚合','只看代码行数','分布要求与已有条件共同决定额外工作。')
c(s,'stages','源码三个转换就固定三个 stage 吗？','有两个宽依赖名字就能承诺所有运行 stage 数吗？','不能，结合交换、复用、AQE 和运行证据','能，调用与 stage 严格一一对应','只数变量数量','只数 SELECT 列数','运行划分不能机械由源码步骤计数。')
s='l4-job-stage-task'
c(s,'slots','9 tasks、3 slots，忽略其他约束，大致？','10 tasks、2 slots，忽略其他约束，大致？','分批运行，总数不等于同时数','全部必须同时运行','只能存在 slots 个分区','自动丢弃未调度任务','资源槽位限制并发，不取消待处理数据。')
c(s,'jobs','一个 action 保证只有一个 job 吗？','一次 collect 出现多个 job 能直接判重复提交吗？','不保证，要核对内部执行与运行记录','保证，必然用户重复点','job 数等于结果行数','Spark 只能有一个 job','action 与运行 job 不保证固定一对一。')
c(s,'attempt','task 6 第一次失败第二次成功，说明？','同一 task 出现两个 attempt，必定两个逻辑分区吗？','同一逻辑任务可能有多次尝试','分区必定翻倍','结果必重复两份','stage 必新增两台机器','区分 task 与 attempt，重试不直接定义业务结果。')
c(s,'tail','中位数 1s，最大 80s，应优先检查？','平均不高但一个任务持续很久，应检查？','长尾任务的键、字节、spill 与异常','只看总平均就足够','只把所有参数加倍','先删除慢键','分布和异常证据比盲目调参更有针对性。')
c(s,'codegen','*(4) 是否表示四个 task？','计划节点 (9) 是否表示九个并发任务？','不能据此推断 task 数','是，严格等同','表示四/九台 Executor','表示输出行数','计划标记与调度计数不能混为一谈。')
s='l4-comprehensive'
c(s,'contract','两个方案报表结果不同，先比较什么？','改写少了一个组但更快，能直接交付吗？','先解决语义与结果差异','只交最快的','先删验收断言','只给计划截图','正确性是优化比较的前提。')
c(s,'change','聚合前额外随机重分区无业务要求，应怎样实验？','多一个重分布节点可疑，下一步？','单一可回退改动，比较结果与实际计划','把分区数无限增大','跳过所有聚合','直接删除输入记录','假设需要以等价结果和执行证据验证。')
c(s,'evidence','sizeInBytes 下降但未测内存，报告应写？','节点数下降但未跑代表规模，报告应写？','已观察结构/估计变化，收益仍待验证','内存/耗时必同倍下降','生产必快十倍','所有环境都已认证','结论不能超过证据范围。')
c(s,'record','AQE 开启的对照实验应保留什么？','路线执行后改变，应交付哪些证据？','初始/最终计划、结果和运行条件','只保留最短图','只保留代码行数','只保留最快秒数','记录足以让其他人重现实验与解释差异。')
c(s,'limits','小数据本地通过能保证生产性能吗？','诊断文字完成但还没生产试验，应如何说明？','明确已验范围、未验假设和回退','保证所有集群同样收益','把缺少证据删除','把计划节点当秒数','本地实作不是生产性能认证。')

# L5: load, algebra, partition and shuffle boundaries.
s='l5-what-is-partition'
c(s,'machine','6 个计算分区就一定 6 台机器吗？','local[2] 下 9 个分区能据此推出九个并发线程吗？','不能，分区与资源/并发不同','能，严格一分区一机器','分区就是文件目录','分区就是结果行数','计算份、机器、并行槽位和目录不同概念。')
c(s,'empty','2 行数据分 7 份，允许空分区吗？','空输入可以仍有多个计算分区吗？','允许，分区数不是非空行数','不允许，必须复制数据','不允许，自动丢弃分区定义','每分区必有一张表','空分区不需要伪造业务数据填满。')
c(s,'directory','write.partitionBy(day) 主要约定？','按 region 写分区目录主要说明？','存储目录按字段值组织','每个目录必一个文件','每键必一个 Executor','只剩一个计算 task','存储布局不等于计算分区与文件数承诺。')
c(s,'load','只有分区数，能认定均衡吗？','16 份计算数据是否保证每份工作量一样？','不能，还需负载和 task 分布','能，每份自动等字节','能，每份自动等 CPU','能，每份自动等行宽','数量不说明记录宽度、工作集和实际耗时。')
c(s,'inspect','查看负载只看行数够吗？','两分区行数相同但值宽度不同，工作量必一样吗？','不够，还看字节与每行计算成本','够，所有行同等成本','只看变量名','只看文件扩展名','记录数量不能独立代表全部资源负载。')
s='l5-partition-count-parallelism'
c(s,'waves','15 tasks、3 slots，能全同时吗？','18 tasks、2 slots，能全同时吗？','通常需要分批调度','全部必同时','只处理 slots 个','必须丢掉其余任务','分区提供潜在工作，资源约束并发。')
c(s,'tiny','极小任务成千上万，优先检查？','小数据切出过多份，启动调度占比大，应？','任务粒度与调度开销','继续盲目加十倍','认定管理完全免费','把行数当秒数','更多分区可能提高管理开销而非加速。')
c(s,'large','每任务工作集过大且 spill，多看什么？','少数超大分区导致长任务，应先看？','负载分布、容量与合理切分','只缩短文件名','保证内存自动够','只增加结果列','任务粒度与算子状态影响资源需求。')
c(s,'aqe','设置 Shuffle 分区 200 后 AQE 能调整吗？','配置值能代表所有阶段最终 task 数吗？','可能调整，核对最终计划与运行','永远严格所有阶段 200','代表 200 行输入','代表 200 台机器','初始相关配置不等于最终所有调度。')
c(s,'hot','一个键占大多数，只加分区保证拆散吗？','热键仍按同一键哈希路由，增加总份数能保证均分吗？','不能，需看键分布和热点处理','保证均分','会自动删除热键','总额自动降低','同键集中是单纯数量调节不能保证解决的问题。')
s='l5-what-is-shuffle'
c(s,'global','同键局部值 15、25 要交一行总量，应？','同键局部值 17、23 要交一行总量，应？','汇合全部局部贡献','取先到的一份','只改列名','随便去重一份','局部正确还需全局汇合。')
c(s,'local','只有单机 local 就一定没 Shuffle 吗？','同机多个分区重组织是否可有 Shuffle？','仍可发生分区重分布','完全不可能','只可能复制文件名','等同广播整表','Shuffle 不以跨机器网络为必要条件。')
c(s,'combine','支持局部预聚合时可能减少什么？','同键很多，交换前合并局部状态可能减少什么？','待交换中间内容','合法业务贡献','最终语义要求','所有运行成本','预聚合减少组织开销，不漏算贡献。')
c(s,'exchange','BroadcastExchange 和 ShuffleExchange 等同吗？','看到 Exchange 字样可直接数成同类按键交换吗？','不能，需区分交换类型','完全等同','都等于 Python collect','都表示没有通信','交换满足不同分布路线，不应只数单词。')
c(s,'skew','按键分区后热点仍集中，应该？','交换后一个任务远慢于其他，下一步？','核对热键、字节、匹配/聚合工作集','直接删热键','认定所有分区完全均衡','固定增加分区即保证解决','热点与任务分布需要具体证据。')
s='l5-shuffle-cost'
c(s,'components','网络低但磁盘与 spill 高，能说没有交换成本吗？','local 中交换阶段慢，能只因无远端网卡就排除 Shuffle 吗？','不能，IO/序列化/合并等仍有成本','能，无网络就零成本','一定是 SQL 文本长','一定是字段名太长','交换成本不只网络传输。')
c(s,'width','行数相同一批含大数组，另一批两个整数，哪个信息还重要？','一百条宽记录与一千条窄记录，能只数行吗？','字节宽度与结构/计算成本','只看行数就足够','只看列名长度','只看输入文件名','数据宽度影响序列化与传输、内存工作。')
c(s,'prune','交换前不需要的大文本字段，合理实验是？','查询后续只用键与数值，携带长备注应考虑？','在保持语义下裁剪并对照交换量','删除所有业务字段','只改别名','按最长字段排序','减少不必要内容可能降低交换开销。')
c(s,'compress','压缩后字节下降、CPU 上升，如何判断？','交换压缩变小是否自动代表总耗时下降？','同条件比较端到端和资源指标','只看字节即可宣称成功','压缩永远无效','CPU 永远免费','资源之间有权衡，目标指标需要实测。')
c(s,'spill','spill 增加最直接提示哪类排查？','交换相关任务频繁落盘，应先看？','任务工作集、内存压力与负载分布','只看变量大小写','删除正确性断言','认定网络必坏','spill 是运行证据，需要结合任务与资源解释。')
s='l5-narrow-wide-partition'
c(s,'flatmap','局部分词产生更多行，一定宽依赖吗？','每行独立扩展三行，需要先汇合全表吗？','不一定，输出量不决定依赖类型','一定，增加行数就是宽','必须 collect 全表','必须先全局排序','看数据来源需求，而不是行数变化。')
c(s,'sort','A=[2,9]，B=[3,8] 各自有序，串接全局有序吗？','A=[1,7]，B=[4,6] 各自有序，串接全局有序吗？','不是，跨分区范围仍交叠','是，局部有序自动全局有序','只要有四行就是','改列名即可','全局有序还需满足分区间范围顺序。')
c(s,'filter','过滤掉九成行会自动减九成分区吗？','filter 后只有几行能保证自动一个分区吗？','不能如此保证','能，严格按比例','必删除分区定义','必随机重分区所有行','行数和分区数不是比例绑定。')
c(s,'reuse','下游按 k 聚合，上游可能已按 k 分布，应？','已有分布满足要求时是否无条件再 repartition？','先核对计划，可能复用','必再交换固定一次','可以跳过求和语义','必须 collect','已有条件会影响额外分布工作。')
c(s,'local-global','各分区独立去重能保证全局唯一吗？','同一行在两个分区都存在，仅局部 distinct 够吗？','不够，还要覆盖跨分区重复候选','足够，名字相同会自动合并','随意删一个分区','只看 show 第一行','局部唯一和全局唯一不同。')
s='l5-shuffle-trigger-operators'
c(s,'aggregate','分散同键贡献需要汇总，常见交换原因？','全局按门店统计且上游分布不满足，应？','满足按键汇合的分布要求','函数名太长','所有行必须进 Driver','先把金额转字符串','交换服务具体分布要求，不是语法附加税。')
c(s,'joins','任何 JOIN 都双边 Shuffle 吗？','维表广播时能机械按两侧各算一次 Shuffle 吗？','不能，核对物理路线','能，任何场景固定两次','JOIN 完全不计算','所有 JOIN 都收集到 Driver','连接策略与输入分布共同影响交换。')
c(s,'dedup','重复跨多个分区，distinct 为何常需重组织？','全局唯一需要判断什么范围？','不同分区的重复候选','只有每份首行','只看字段名字','只看目录数量','全局判断不能只检查每份独立记录。')
c(s,'topn','ORDER BY LIMIT 必与全量排序逐字同计划吗？','只取最高几条时能假定完整长排序链必存在吗？','不能，优化可能选择 Top N 路线','必须逐字相同','LIMIT 等于随机抽样','LIMIT 不需要排序语义','语义与物理实现需分开。')
c(s,'count','仅数 Exchange 字样就得出实际阶段数可靠吗？','静态源码里三个疑似交换操作，能断言最终调度吗？','不可靠，结合类型、AQE 与实际运行','可靠，严格固定映射','等于输出列数','等于机器数','实际计划与运行证据决定执行划分。')
s='l5-reducebykey-vs-groupbykey'
c(s,'local-combine','只需整数总量，reduceByKey 相比先收集全部值可能省？','同键很多，局部规约为何有用？','部分中间传输/状态内容','全部最终合并','所有合法贡献','所有运行任务','可规约目标可以局部压缩贡献。')
c(s,'sum','A 局部 9+6，B 局部 12，最终加法结果？','A 局部 8+7，B 局部 15，最终加法结果？',('27','30'),('15','15'),('12','7'),'只保留第一个','局部合并不丢跨分区贡献。')
c(s,'algebra','减法直接分布式规约并依赖固定顺序，风险？','用有序字符串拼接做无序规约，应该检查？','结合/交换性质与顺序依赖','分区越多自然越正确','只看函数名字','默认结果顺序永远固定','重组贡献需要满足相应代数与验收约定。')
c(s,'values','业务确需原始同键事件集合，是否一律用加法规约？','目标需要检查每个值，简单 sum 不足，应该？','按信息需求选处理并评估状态容量','强制加法，丢事件也无妨','只保留最后一条','任何集合需求都不允许','工具选择必须保留业务需要的信息。')
c(s,'shuffle','reduceByKey 能保证没有任何 Shuffle 吗？','局部合并后各分区同键结果还需汇合吗？','仍可能需要最终分布与合并','永远零交换','只看局部即可完成','自动把所有键删掉','局部预聚合与全局完成不同。')
s='l5-repartition-coalesce'
c(s,'increase','从 3 份增加为 9 份，repartition 通常？','从 2 份增加为 6 份，repartition 通常？','通过重分布组织目标分区','只改变量名','保证相同数量机器','自动聚合成目标行数','重分区不是改元数据或业务聚合。')
c(s,'coalesce','默认 coalesce 减分区是否保证完美均衡？','合并现有份能保证每份字节完全相等吗？','不能，可能继承不均','能，任何数据严格等量','会自动去重','会自动创建目录分区','减少份数不等于完整重新均匀分布。')
c(s,'single','大数据 coalesce(1) 的主要风险？','昂贵工作集中单分区可能怎样？','限制并行并制造单任务容量瓶颈','无限内存','必零 IO','保证最快','过度集中会改变任务粒度和容量需求。')
c(s,'key','repartition(5,k) 自动得到每键一行吗？','按 region 重分区等于业务分组求和吗？','不是，只组织分布','是，自动求和','是，自动去重','是，自动单文件','重分区不替代聚合或唯一性规则。')
c(s,'files','小文件很多时应先量什么？','想调写入分区数，先看什么？','文件数量/大小、数据量与写入并发','无条件一个文件','只改扩展名','把目录全重命名','交付布局与吞吐需要具体测量和约定。')
s='l5-comprehensive'
c(s,'invariance','整数求和从 2 分区改 5 分区应保持？','同一输入从 3 分区改 6 分区，应先核对？','每键业务总量','每个 task 耗时完全相同','每条记录所在机器相同','中间记录顺序相同','分区调节不应改变可规约整数指标。')
c(s,'keys','不同商品归在同一输出分区，应怎样聚合？','哈希碰撞使多个键共处一份，可直接把键合并吗？','仍按真实键分别统计','按分区把所有键当同一商品','只保留一个键','按机器名替代键','分区位置不改变业务键的相等定义。')
c(s,'hot','热键占多数，单纯加分区足够吗？','最大 task 很大，中位数很小，应如何评价？','检查热点与实际负载，不能保证仅加数量解决','保证均匀','只看平均即可通过','删除热键就是优化','长尾需要有针对性的负载与语义证据。')
c(s,'empty','空输入的每键总量结果应？','没有任何商品记录时应硬造一个键吗？','空结果，不伪造业务键','固定一行 unknown=0','原样例总额','输出分区数行结果','空输入仍需符合业务语义，而不是凑固定行数。')
c(s,'proof','给出一份本地任务耗时能证明生产更快吗？','分区计数正常就等于网络/内存认证吗？','不能，记录已验证范围和待测指标','能，所有集群相同','只要截图漂亮即可','所有指标互相等价','测量证据有适用范围，不能超范围推断。')

# L6: cardinality before strategy, conditional physical explanations.
s='l6-what-is-join'
c(s,'pairs','一张 60 元订单匹配两条维度，SUM 得到？','一张 20 元订单匹配三条维度，SUM 得到？',('120','60'),('60','20'),'0','1','匹配行对放大贡献，维表唯一性要验证。')
c(s,'left','所有事实都保留，未匹配补空，选哪种语义？','订单用户缺维也不能丢，哪种关系合适？','fact LEFT JOIN dim','fact INNER JOIN dim','只保留 dim','无条件 CROSS JOIN','连接类型决定未匹配事实去向。')
c(s,'null','普通等号下两侧 NULL 键会互配吗？','ON a.k=b.k，两行 k 均 NULL，条件为 true 吗？','不会，普通比较为未知','会，缺失必相等','必类型报错','会，自动生成相同用户号','NULL 匹配需按普通或空安全语义显式约定。')
c(s,'unique','补维期望不放大事实，应先查？','维表更新后报表金额翻倍，优先核对？','键唯一、缺失、类型与匹配基数','只看名字','只调广播阈值','只把结果排序','先保证数据约束与连接语义。')
c(s,'postfilter','LEFT JOIN 后 WHERE dim.tag IS NOT NULL 可能？','左连接后排除右侧空值，可能违反什么？','排除本应保留的未匹配左行','保证保留所有左行','自动防止全部重复','自动广播','后过滤可能再次排除外连接保留行。')
s='l6-join-strategies-overview'
c(s,'layers','LEFT 与 SortMergeJoin 属于同一层吗？','INNER 与 BroadcastHashJoin 如何区分？','前者语义，后者物理实现','两者不能共存','后者自动改变前者','都是文件格式','逻辑类型与执行策略应分开。')
c(s,'equi','仅 a.x>b.y，没有等值键，能无条件选 BHJ 吗？','范围匹配能照搬等值哈希路线吗？','不能，检查条件与算法支持','能，所有 JOIN 都同算法','把条件改成相等即可忽略语义','必定零计算','适用条件约束候选算法。')
c(s,'tradeoff','比较 BHJ/SMJ/SHJ 应看？','不同物理路线怎么选证据？','数据规模/分布、条件、内存、计划和指标','仅看名字长度','只用最新名词','只看 SQL 大小写','不同路线有不同交换、排序和构建权衡。')
c(s,'aqe','初始 SMJ 但 AQE 开启，应以什么核对最终？','运行统计可能改变连接路线，报告应包含？','最终计划及运行条件和结果','只看最初图','只看源码 hint','只看输入路径','自适应变化与实际收益分别验证。')
c(s,'semantics','换物理策略应该自动改变 INNER 的保留规则吗？','为了更快把 LEFT 改 INNER，可以直接说只改了物理实现吗？','不可以，必须保持原业务语义','可以，所有策略结果可随意变','可以，只看秒数','可以，字段名相同就够','逻辑语义改变不是单纯物理优化。')
s='l6-broadcast-hash-join'
c(s,'build','小维表 BHJ 一般复制什么给执行节点？','广播构建关系主要服务什么？','适用的小构建侧及其匹配结构','全部事实表 Python 列表','固定业务答案','所有分区结果文件名','广播不等于把大事实收进 Python。')
c(s,'memory','压缩文件 3 MiB 能保证构建只用 3 MiB 吗？','文件很小就可忽略并发广播内存吗？','不能，展开、哈希和并发影响容量','能，精确等同','必定永不 OOM','内存自动转无限','文件体积不是节点工作集上限。')
c(s,'other-exchange','连接 BHJ 后下游 groupBy 还可能交换吗？','存在 BHJ 就能宣布全查询零 Shuffle 吗？','仍可能，逐段看分布要求','绝不可能','只有 SQL 才有交换','只有 API 才有交换','连接路线不取消其他算子要求。')
c(s,'hint','源码写 broadcast(dim) 就证明收益吗？','广播节点实际出现后能立刻认定更快吗？','还要验证采用、结果、容量和指标','源码即性能证明','节点即固定十倍收益','无需再验结果','实施和收益是不同验收项。')
c(s,'support','没有等值键但有广播提示，必 BHJ 吗？','广播提示会取消连接类型支持限制吗？','不会，核对实际可用路线','会，提示无条件强制哈希','会，自动改条件','会，自动删未匹配行','广播与具体算法的适用性不能混同。')
s='l6-sort-merge-join'
c(s,'requirements','SMJ 主要利用怎样的输入？','排序合并匹配需要计划满足什么？','相应键分布与分区内有序等要求','全部收进 Driver','所有行同一文件','字段名短于五字','算法路线建立在分布与排序要求上。')
c(s,'reuse','已有合适分布/顺序时 SMJ 必再双侧重排吗？','计划一侧无新 Sort 可直接判错误吗？','不必，可能复用已有条件，需核对计划','必须固定重做所有步骤','说明自动变 CROSS JOIN','说明没有任何计算','必要工作可能由上游满足。')
c(s,'resource','SMJ 保证没有 spill 或内存压力吗？','排序合并时慢 task 伴随 spill，应如何看？','排序、缓冲和倾斜仍需资源诊断','SMJ 完全不用内存','一定是广播过大','完全不必看运行指标','算法名不是资源问题豁免。')
c(s,'duplicate','维表重复，换 SMJ 会自动去重吗？','SMJ 能修复多对多金额放大吗？','不会，需解决数据基数与规则','会，排序即去重','会，每键自动一行','会，自动取第一条','物理策略不应悄悄修正或改变业务语义。')
c(s,'performance','SMJ 一定比 SHJ 慢吗？','少一个哈希结构就保证总成本最低吗？','不能，按负载与资源实测比较','永远更慢','永远更快','名字决定全部性能','物理路线需要条件化评价。')
s='l6-shuffle-hash-join'
c(s,'local','SHJ 的构建范围主要怎样理解？','与整侧广播不同，分区哈希主要在哪里建结构？','在满足分布的构建侧分区中','把大表 collect 到 Python','完全不使用匹配键','自动没有任何内存','局部分区建哈希仍有分布与容量要求。')
c(s,'max','构建分区为 2、2、2、50 MiB，只看平均够吗？','整表不大但一个构建分区巨大，应重点看？','最大任务工作集与并发余量','仅总平均','文件名','输出列名字数','峰值和并发决定局部容量风险。')
c(s,'disable','关闭自动广播就必定 SHJ 吗？','autoBroadcastJoinThreshold=-1 能强制选 SHJ 吗？','不能，仍看候选与实际计划','能，只有一个回退策略','必变 CROSS JOIN','必不运行','关闭一种候选不等于指定另一种。')
c(s,'tradeoff','少了排序就可保证 SHJ 更快吗？','对照 SMJ/SHJ 应怎样评价？','综合建表容量、分布、倾斜与实测','只看 Sort 字样','只看 SQL 长度','固定按名字排序','删除一个成本项不代表总成本最低。')
c(s,'semantics','分区哈希路线会自动修复 NULL 键业务规则吗？','选 SHJ 后可省略唯一性验证吗？','不能，语义与数据约束仍需验证','可以，算法替代契约','可以，匹配率自动百分百','可以，维表自动唯一','物理选型不代替数据质量与连接类型。')
s='l6-how-spark-chooses'
c(s,'statistics','catalog 统计陈旧，选型排查应？','文件变化后计划规模估计仍旧，应先查？','统计来源、时效与实际规模','只看文件后缀','认定优化器永远精确','只改变量名','可用统计质量影响策略判断。')
c(s,'threshold','估计小于阈值能无条件保证 BHJ 吗？','只知道自动阈值，能锁定最终连接节点吗？','不能，条件/类型/hint/AQE 仍相关','能，阈值是唯一因素','表示结果一定为空','表示内存一定足够','单个参数不是完整选择模型。')
c(s,'runtime','AQE 转换路线必定发生吗？','运行统计出现后，所有 SMJ 都必改 BHJ 吗？','不保证，检查适用条件和最终计划','总会发生','永不可能发生','只要有 JOIN 就发生','自适应优化有条件，不是固定改写口号。')
c(s,'compare','方案一冷缓存，方案二热缓存，可直接归因策略吗？','A/B 输入量不同，耗时差能直接证明 hint 收益吗？','不能，控制或记录混杂条件','可以，只看秒数','必须选快的宣称成功','按代码行数消除差异','实验条件会影响归因。')
c(s,'preserve','改变配置前后逐组结果不同，应？','策略试验丢失未匹配事实，怎样评价？','先修正语义/实现，不算正确优化','只看快慢','先删原断言','保留错误结果即可','正确结果先于性能结论。')
s='l6-broadcast-hint-and-control'
c(s,'intent','F.broadcast(dim) 表达什么？','SQL BROADCAST 提示主要表达什么？','广播选型倾向，仍需适用性验证','自动校验维表唯一','所有数据 collect 到 Python','固定加速十倍','提示不是语义、容量或收益认证。')
c(s,'disable','关闭自动广播阈值，显式 hint 必失效吗？','只改一个自动阈值，能保证 AQE/显式广播全关闭吗？','不能，控制层次不同需核对','能，所有广播都全禁','所有 JOIN 必报错','所有查询变单线程','自动、显式和自适应配置需分别理解。')
c(s,'unsupported','提示未采用，先检查？','连接条件不支持目标算法时应？','核对支持范围与实际解释信息','认定 Spark 必损坏','随意改业务条件','只加更多相同提示','hint 不能取消算法适用条件。')
c(s,'memory','实际广播后内存压力上升，合理做法？','hint 生效但总体更慢，应？','可回退并检查容量/并发/替代路线','只宣布 hint 已生效即成功','持续盲目放大阈值','删除结果校验','采用和收益应分别验收。')
c(s,'proof','证明广播采用主要看什么？','源码有提示而计划未知，缺什么？','实际物理节点、构建侧与最终计划','只看注释','只看变量名','只看函数被调用次数','源码倾向不等于实际执行路线。')
s='l6-join-data-skew'
c(s,'tail','中位 2s、最大 100s，热键占多数，应？','多数快但一个巨慢，连接阶段要查？','键/字节/匹配基数、spill 和异常','只看平均','删最慢键','固定所有资源翻倍','长尾有多种原因，需结合分布与运行证据。')
c(s,'partitions','同键哈希路由，分区翻倍保证热键均分吗？','repartition(200,k) 能保证拆开一个键所有行吗？','不能，需针对热点语义处理','保证均分','自动删热点','自动改键值','增加不同键的容器不保证拆开一个键。')
c(s,'salt','只给事实键随机加盐，维表不配套，风险？','salting 未定义还原规则就求和，风险？','漏配或重复，需要保语义扩展与还原','必定更正确','自动有序','自动唯一','加盐要保证原匹配关系，不是随意改键。')
c(s,'quality','维表重复千次使金额放大，应先？','预期一对一却实际一对多，应先？','确认唯一性与冲突规则','只调分区掩盖','认定正常现象','把金额随意除千','数据基数错误可同时制造正确性与性能问题。')
c(s,'aqe','开 AQE 就保证所有倾斜解决吗？','最终仍有长尾，能只说 AQE 已开启就验收吗？','不能，核对适用性、最终计划与实际分布','能，无需再看','能，所有键自动均匀','能，自动修复维表冲突','机制开启与实际适用/收益不同。')
s='l6-comprehensive'
c(s,'left','所有有效事实保留，未匹配标签 unknown，应？','缺维不能丢订单，主体关系怎样表达？','事实 LEFT JOIN 维度并定义缺失标签','INNER JOIN 后忽略缺失','无条件 CROSS JOIN','只输出维度','保留事实与缺失口径先于物理选择。')
c(s,'conflict','维表两个相同非空键，任务规定唯一，应？','遇到违反唯一约定的两个标签，需求未定义取舍，应？','明确拒绝契约冲突，而非任取/放大','随便取第一条','任意把金额乘二','用广播掩盖','异常输入需要明确失败行为。')
c(s,'unmatched','匹配订单 12 元、未匹配 18 元，约定保留 unknown，应？','匹配订单 14 元、未匹配 16 元，约定保留 unknown，应？',('已知组 12、unknown 18','已知组 14、unknown 16'),'全部归到已知组','只保留已知组','全部删除','未匹配贡献应按约定保留并明确标记。')
c(s,'null','任务规定普通等值，事实 NULL 键是否应和维度 NULL 互配？','为增加匹配率把 NULL 都变同一伪造用户号是否自然等价？','不应，需遵守既定 NULL 语义','应自动互配','只要更快就可改','全部变成字符串 NULL 即无影响','空安全策略改变要显式定义，不能偷偷改变基数。')
c(s,'accept','结果与计划正确就保证生产加速吗？','本地连接验收通过应怎样报告？','说明结果/策略已验范围，资源收益仍需代表测量','保证所有集群更快','只给一张 hint 截图','删除未验范围','正确性、实施、收益与适用范围是不同结论。')

# Concise answers keep the decision at the same level as the alternatives;
# detailed reasoning belongs in explanation, not a conspicuously long choice.
SHORT = {
('l3-what-is-spark-sql','equivalence'):'核对语义，性能看计划与实测',
('l3-what-is-spark-sql','command'):'不能，命令与查询需区分',
('l3-what-is-spark-sql','source'):'也可查询目录表和文件源',
('l3-temp-views','replace'):'不会，需重新注册',
('l3-temp-views','lifetime'):'不足，需另行持久交付',
('l3-temp-views','cache'):'不是，三种操作不同',
('l3-groupby-having','grain'):'未定义组内字段取值',
('l3-groupby-having','outer'):'可以，外层已看到聚合列',
('l3-joins-intro','types'):'不能，需查值与转换规则',
('l3-functions-and-udf','register'):'注册 SQL 名称与返回类型',
('l3-functions-and-udf','performance'):'先看内置可否表达，再实测',
('l3-tables-and-formats','catalog'):'不能，要查 catalog 配置',
('l3-tables-and-formats','target'):'不够，核对输出契约',
('l3-comprehensive','accept'):'还需逐组与交付验收',
('l4-why-explain','plan'):'不能，需运行指标',
('l4-why-explain','correct'):'先修正结果，不算成功',
('l4-logical-vs-physical','meaning'):'逻辑计算需求',
('l4-logical-vs-physical','routes'):'不必，需核对等价性',
('l4-logical-vs-physical','analysis'):'先修复语义分析问题',
('l4-logical-vs-physical','optimization'):'保持语义，不是逐行记录',
('l4-explain-api','cost'):'不能，估计不是实测',
('l4-read-plan','exchange'):'不能，交换类型不同',
('l4-read-plan','id'):'不是，两套编号不同',
('l4-read-plan','time'):'不能，有管线与并行',
('l4-catalyst-rules','prune'):'列裁剪线索，仍需实测',
('l4-catalyst-rules','pushdown'):'还需核对残余过滤',
('l4-catalyst-rules','benefit'):'不能，收益需要测量',
('l4-wholestage-codegen','fusion'):'部分调用与交接开销',
('l4-wholestage-codegen','exchange'):'不能，分布要求仍在',
('l4-wholestage-codegen','memory'):'不能，工作集仍有限',
('l4-wholestage-codegen','markers'):'不能，边界可能合理',
('l4-dependency-narrow-wide','rows'):'不是，先看数据来源需求',
('l4-dependency-narrow-wide','existing'):'看计划，可能复用分布',
('l4-job-stage-task','jobs'):'不保证，需核对实际执行',
('l4-job-stage-task','attempt'):'同一任务有多个尝试',
('l4-job-stage-task','codegen'):'不能，需看运行记录',
('l4-comprehensive','evidence'):'只报告已观察证据',
('l4-comprehensive','limits'):'列明范围与待验证项',
('l5-what-is-partition','machine'):'不能，分区不是资源数',
('l5-what-is-partition','empty'):'允许，分区可以为空',
('l5-what-is-partition','directory'):'按字段值组织目录',
('l5-what-is-partition','load'):'不能，还需看负载',
('l5-what-is-partition','inspect'):'不够，还需字节与计算成本',
('l5-partition-count-parallelism','aqe'):'可能调整，核对最终执行',
('l5-partition-count-parallelism','hot'):'不能，热键仍可能集中',
('l5-what-is-shuffle','local'):'仍可发生重分布',
('l5-what-is-shuffle','exchange'):'不能，交换类型要区分',
('l5-shuffle-cost','components'):'不能，仍可能有 IO 等成本',
('l5-shuffle-cost','width'):'还需记录宽度与结构',
('l5-narrow-wide-partition','flatmap'):'不一定，要看来源关系',
('l5-narrow-wide-partition','filter'):'不能按行数比例保证',
('l5-shuffle-trigger-operators','joins'):'不能，取决于路线',
('l5-shuffle-trigger-operators','topn'):'不能，可能优化为 Top N',
('l5-shuffle-trigger-operators','count'):'不可靠，需实际执行证据',
('l5-reducebykey-vs-groupbykey','algebra'):'检查结合性与顺序依赖',
('l5-reducebykey-vs-groupbykey','shuffle'):'仍可能需最终交换汇合',
('l5-repartition-coalesce','coalesce'):'不能，可能仍不均衡',
('l5-repartition-coalesce','single'):'单任务容量和并行瓶颈',
('l5-repartition-coalesce','key'):'不是，只改变分布',
('l5-comprehensive','proof'):'不能，证据有适用范围',
('l6-what-is-join','null'):'不会，条件为未知',
('l6-join-strategies-overview','layers'):'语义与物理实现两层',
('l6-join-strategies-overview','equi'):'不能，要核对算法适用性',
('l6-join-strategies-overview','semantics'):'不可以，需保持业务语义',
('l6-broadcast-hash-join','memory'):'不能，要看实际工作集',
('l6-broadcast-hash-join','other-exchange'):'仍可能，分段检查',
('l6-broadcast-hash-join','support'):'不会，仍需满足适用性',
('l6-sort-merge-join','reuse'):'不必，可能复用已有条件',
('l6-sort-merge-join','duplicate'):'不会，需解决基数问题',
('l6-sort-merge-join','performance'):'不能，按负载与资源比较',
('l6-shuffle-hash-join','disable'):'不能，未指定唯一回退',
('l6-shuffle-hash-join','semantics'):'不能，契约仍需检查',
('l6-how-spark-chooses','threshold'):'不能，阈值不是唯一因素',
('l6-how-spark-chooses','runtime'):'不保证，要看最终计划',
('l6-how-spark-chooses','compare'):'不能，实验条件不同',
('l6-broadcast-hint-and-control','disable'):'不能，控制层次不同',
('l6-join-data-skew','partitions'):'不能，热键仍可能集中',
('l6-join-data-skew','aqe'):'不能，需验证实际效果',
('l6-comprehensive','accept'):'说明已验范围和待测项',
}

def build():
    lessons=[];ordinal=0
    course=json.loads((Path(__file__).parent/"app/course_seed.json").read_text(encoding="utf-8"))
    titles={l["slug"]:l["title"] for level in course["levels"] for l in level["lessons"]}
    assert len(cards)==36
    for slug,families in cards.items():
        assert len(families)==5,slug
        questions=[]
        for index,(key,a,b,right,w1,w2,w3,why) in enumerate(families):
            for variant,prompt in enumerate((a,b)):
                options=[value(x,variant) for x in (w1,w2,w3)]
                answer=SHORT.get((slug,key),value(right,variant));correct=ordinal%4;options.insert(correct,answer)
                purpose='assessment' if variant==0 else ('review' if index<3 else 'remediation')
                questions.append(dict(key=f'{slug}/{key}/{purpose}-v1',knowledge_id=f'{slug}/{key}',purpose=purpose,
                    type='single_choice',prompt=f'{titles[slug]}：{prompt}',options=options,correct_index=correct,explanation=why,
                    dimension=['concept','apply','mechanism','debug','transfer'][index]))
                assert len(set(options))==4,(slug,key,variant,options)
                ordinal+=1
        lessons.append(dict(lesson_slug=slug,questions=questions))
    return dict(version=1,scope='L3-L6',lessons=lessons)

if __name__=='__main__':
    data=build();path=Path(__file__).parent/'app/l3_l6_reviewed_bank.json'
    text=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
    if '--check' in sys.argv:assert path.read_text(encoding='utf-8')==text
    else:path.write_text(text,encoding='utf-8')
    print('PASS 36 lessons / 360 questions / 180 paired learning objectives')
