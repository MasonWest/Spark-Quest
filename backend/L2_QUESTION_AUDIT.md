# L2 题库分工与审查报告

旧 100 题保留身份与历史；下表是审查时的原文快照，建议用途不是直接重新上线的质量认证。新抽题使用独立题组。另对旧题 6 处事实错误做保留 ID/正确位置的修正，见 l2_legacy_fact_corrections_v2.json。

## 本次接入

- 新增 100 题：50 课末检验、30 延迟巩固、20 误区补救。每课 5+3+2。复习回合使用后五题，课末与复习集合无交集。
- 课末固定覆盖五类目标，仅顺序打乱；复习使用另一套五题。当前容量还不支持同课多轮持续换新，需要后续扩充。
- 补救题目前随课程复习出现，未实现根据刚才错项实时插入异题。knowledge_id 为后续细分调度保留。
- 新题采用 50 个问题模板各编写课末/复习材料；其中一部分是同概念在新字段或参数下重测，不等同于 100 个全新概念。
- 新题答案位置 A/B/C/D 各 25；正确项唯一最长 28/100（旧快照为 51/100）。长度统计只是风险信号，不证明答案质量。
- 历史得分、原题 ID、原始答题事实与旧题重练入口保留；已打开的旧五题提交可继续判分。L2 新提交需五道不同题，4/5 掌握、5/5 复习与粘性掌握规则保持。

## 旧题逐题用途

| 课程 | 原位置 | 原题干 | 建议用途 | 风险/处理 |
|---|---:|---|---|---|
| l2-what-is-dataframe | 1 | DataFrame 最准确的定义是？ | 课中解释素材 | 新回合使用独立题组 |
| l2-what-is-dataframe | 2 | Spark 为什么要在 RDD 之上再提供 DataFrame 这一层？ | 课中解释素材 | 新回合使用独立题组 |
| l2-what-is-dataframe | 3 | 写下 spark.createDataFrame(rows, schema) 后，下列说法正确的是？ | 误区补救素材 | 创建零工作口径已另修 |
| l2-what-is-dataframe | 4 | 下列哪类任务最符合「优先用 DataFrame」的场景？ | 应用检验候选 | 正确项唯一最长 |
| l2-what-is-dataframe | 5 | 以下关于 DataFrame 与 RDD 的关系，说法错误的是？ | 课中解释素材 | 否定/绝对措辞需复核 |
| l2-what-is-dataframe | 6 | 你想立刻在控制台看到 DataFrame 的前几行数据，却只看到对象的描述，应该？ | 课中解释素材 | 正确项唯一最长 |
| l2-what-is-dataframe | 7 | DataFrame 底层的数据是以什么形式存放和计算的？ | 课中解释素材 | 新回合使用独立题组 |
| l2-what-is-dataframe | 8 | 要得到一个 DataFrame 的「列名 + 类型」概览，应该？ | 延迟复习候选 | 新回合使用独立题组 |
| l2-what-is-dataframe | 9 | 为什么有了 pandas 这样的单机表，Spark 还要提供 DataFrame？ | 课中解释素材 | 新回合使用独立题组 |
| l2-what-is-dataframe | 10 | 关于 DataFrame 这种「表」的说法，正确的是？ | 延迟复习候选 | 新回合使用独立题组 |
| l2-create-dataframe | 1 | spark.read.csv(path) 返回的对象是？ | 课中解释素材 | 新回合使用独立题组 |
| l2-create-dataframe | 2 | 读 CSV 时通常要加 .option('header', True)，主要是为了？ | 课中解释素材 | 新回合使用独立题组 |
| l2-create-dataframe | 3 | 读 CSV 后调用 show(10)，数据真正被读取发生在？ | 误区补救素材 | 正确项唯一最长 |
| l2-create-dataframe | 4 | 要把一个 Python 列表 [('Alice',34),('Bob',28)] 变成分布式 DataFrame，应使用？ | 应用检验候选 | 新回合使用独立题组 |
| l2-create-dataframe | 5 | 关于 CSV 读取后的数据类型，下列说法错误的是？ | 误区补救素材 | 否定/绝对措辞需复核 |
| l2-create-dataframe | 6 | 为什么 spark.read 系列方法返回 DataFrame 是『惰性』的设计？ | 课中解释素材 | 正确项唯一最长 |
| l2-create-dataframe | 7 | spark.createDataFrame(rows, schema) 与 spark.read.csv(path) 的共同点是？ | 延迟复习候选 | 正确项唯一最长 |
| l2-create-dataframe | 8 | 已知 schema=StructType([...])，把一个已有 RDD 转成带结构的 DataFrame，应？ | 延迟复习候选 | 新回合使用独立题组 |
| l2-create-dataframe | 9 | spark.read.format('json').load(path) 中 format/load 的作用是？ | 课中解释素材 | 正确项唯一最长 |
| l2-create-dataframe | 10 | 用 createDataFrame 时如果不给 schema 而只给元组/Row，Spark 会？ | 延迟复习候选 | 正确项唯一最长 |
| l2-schema-types | 1 | Schema（StructType）的主要作用是什么？ | 课中解释素材 | 新回合使用独立题组 |
| l2-schema-types | 2 | 生产环境为何更推荐显式 StructType 声明 Schema，而非 inferSchema？ | 课中解释素材 | 新回合使用独立题组 |
| l2-schema-types | 3 | 显式声明 Schema 后读取数据，遇到「字符串无法转成 IntegerType」的行会怎样？ | 误区补救素材 | 正确项唯一最长 |
| l2-schema-types | 4 | 金额字段需要避免浮点误差、保持精确，应该使用哪种类型？ | 延迟复习候选 | 新回合使用独立题组 |
| l2-schema-types | 5 | 关于字段的 nullable，下列说法错误的是？ | 误区补救素材 | 正确项唯一最长；否定/绝对措辞需复核 |
| l2-schema-types | 6 | StructField('age', IntegerType(), True) 三个参数分别指？ | 课中解释素材 | 新回合使用独立题组 |
| l2-schema-types | 7 | 显式声明 Schema 与完全不声明（让 Spark 推断）相比，主要代价是？ | 课中解释素材 | 正确项唯一最长 |
| l2-schema-types | 8 | 要让某列允许为空并声明为整数，应写？ | 延迟复习候选 | 新回合使用独立题组 |
| l2-schema-types | 9 | StringType、IntegerType、BooleanType 等属于？ | 课中解释素材 | 新回合使用独立题组 |
| l2-schema-types | 10 | 为什么浮点金额不用 DoubleType 而用 DecimalType？ | 延迟复习候选 | 新回合使用独立题组 |
| l2-inspect | 1 | df.show(20) 的作用是？ | 课中解释素材 | 新回合使用独立题组 |
| l2-inspect | 2 | show() 默认只展示 20 行，这样设计是为了？ | 课中解释素材 | 新回合使用独立题组 |
| l2-inspect | 3 | 用 df.age 这种「属性式」引用列的局限是？ | 误区补救素材 | 正确项唯一最长 |
| l2-inspect | 4 | 想确认某列到底是 string 还是 bigint，应该？ | 延迟复习候选 | 新回合使用独立题组 |
| l2-inspect | 5 | 以下关于检视操作的错误说法是？ | 误区补救素材 | 否定/绝对措辞需复核 |
| l2-inspect | 6 | show() 与 collect() 在执行上有何关系？ | 延迟复习候选 | 正确项唯一最长 |
| l2-inspect | 7 | take(n) 与 show(n) 的区别是？ | 延迟复习候选 | 正确项唯一最长 |
| l2-inspect | 8 | 想在 Notebook 里拿到前 5 行数据做本地处理，应？ | 应用检验候选 | 正确项唯一最长 |
| l2-inspect | 9 | df.dtypes 返回的是什么？ | 课中解释素材 | 正确项唯一最长 |
| l2-inspect | 10 | 为什么不能依赖 print(df) 来查看数据内容？ | 误区补救素材 | 否定/绝对措辞需复核 |
| l2-select-filter | 1 | select 与 filter 分别用于？ | 课中解释素材 | 正确项唯一最长 |
| l2-select-filter | 2 | 为什么 filter 的多条件必须用 & / \| 而非 Python 的 and / or？ | 课中解释素材 | 正确项唯一最长 |
| l2-select-filter | 3 | 对于 df.filter((df.age>18) & (df.city=='BJ'))，下列说法正确的是？ | 延迟复习候选 | 正确项唯一最长 |
| l2-select-filter | 4 | 想保留「年龄 18–60 且城市为北京或上海」的行，应写成？ | 应用检验候选 | 新回合使用独立题组 |
| l2-select-filter | 5 | 以下关于 filter 的错误说法是？ | 误区补救素材 | 否定/绝对措辞需复核 |
| l2-select-filter | 6 | 为什么 select 只选需要的列通常能让作业更快？ | 课中解释素材 | 正确项唯一最长 |
| l2-select-filter | 7 | filter 与 where 的关系是？ | 延迟复习候选 | 正确项唯一最长 |
| l2-select-filter | 8 | 下面哪段代码一定会在运行时报错？ | 误区补救素材 | 正确项唯一最长；否定/绝对措辞需复核 |
| l2-select-filter | 9 | 只保留 city 为 'BJ' 且 age 大于 30 的行，正确的是？ | 应用检验候选 | 新回合使用独立题组 |
| l2-select-filter | 10 | select 表达式除了列名，还可以接受？ | 延迟复习候选 | 正确项唯一最长 |
| l2-withcolumn | 1 | withColumn(name, expr) 的作用是？ | 课中解释素材 | 新回合使用独立题组 |
| l2-withcolumn | 2 | 对 Column 做运算时，必须用 F.abs / F.round 等 Spark 函数，而不能用 Python 内置 abs / round，是因为？ | 课中解释素材 | 正确项唯一最长；否定/绝对措辞需复核 |
| l2-withcolumn | 3 | df.withColumn('flag', F.lit(1)) 中 F.lit(1) 的作用是？ | 课中解释素材 | 新回合使用独立题组 |
| l2-withcolumn | 4 | 想新增一列「是否成年」：age>=18 为 'adult'，否则 'minor'，应？ | 应用检验候选 | 正确项唯一最长 |
| l2-withcolumn | 5 | 以下关于 withColumn 的错误说法是？ | 误区补救素材 | 否定/绝对措辞需复核 |
| l2-withcolumn | 6 | 为什么 DataFrame 提供 withColumn 而不是让你改原表的某一格？ | 课中解释素材 | 正确项唯一最长 |
| l2-withcolumn | 7 | withColumn 与 select 增列的区别是？ | 延迟复习候选 | 正确项唯一最长 |
| l2-withcolumn | 8 | 写了 df.withColumn('x', df.a + 1) 却没看到 x 列，是因为？ | 误区补救素材 | 正确项唯一最长 |
| l2-withcolumn | 9 | df.withColumn('abs_a', F.abs(df.a)) 中 F.abs 为什么能在集群上执行？ | 延迟复习候选 | 正确项唯一最长 |
| l2-withcolumn | 10 | 把 'name' 列统一转为大写新增为 'name_up'，应？ | 应用检验候选 | 新回合使用独立题组 |
| l2-sort-dedup | 1 | distinct() 与 dropDuplicates(['name']) 的区别是？ | 课中解释素材 | 正确项唯一最长 |
| l2-sort-dedup | 2 | 为什么 orderBy 通常需要触发一次 Shuffle？ | 课中解释素材 | 新回合使用独立题组 |
| l2-sort-dedup | 3 | df.orderBy(F.desc('amount')).limit(10) 表达的语义是？ | 应用检验候选 | 正确项唯一最长 |
| l2-sort-dedup | 4 | 想按城市去重，每个城市保留一行，但不指定保留哪行，应？ | 延迟复习候选 | 新回合使用独立题组 |
| l2-sort-dedup | 5 | 以下关于排序的错误说法是？ | 误区补救素材 | 否定/绝对措辞需复核 |
| l2-sort-dedup | 6 | 为什么去重前常常先思考『按哪些列算重复』？ | 课中解释素材 | 正确项唯一最长 |
| l2-sort-dedup | 7 | limit 与 take 在『取前 N 行』上的区别是？ | 延迟复习候选 | 新回合使用独立题组 |
| l2-sort-dedup | 8 | 想按『城市+日期』去重却写成 dropDuplicates()（不传列），会？ | 误区补救素材 | 正确项唯一最长 |
| l2-sort-dedup | 9 | orderBy 触发的 Shuffle 中，数据如何被重新组织？ | 课中解释素材 | 新回合使用独立题组 |
| l2-sort-dedup | 10 | 金额非空、用户非空且至少有 5 个用户；要返回每个用户的最大金额，再取金额最高的 5 个用户（并列按用户升序），合理写法是？ | 应用检验候选 | 正确项唯一最长 |
| l2-groupby-agg | 1 | df.groupBy('city').agg(F.sum('amount')) 表达的是？ | 课中解释素材 | 正确项唯一最长 |
| l2-groupby-agg | 2 | groupBy 操作通常会触发 Shuffle，原因是？ | 课中解释素材 | 正确项唯一最长 |
| l2-groupby-agg | 3 | groupBy 之后，非分组列能否直接在 select 中使用？ | 误区补救素材 | 新回合使用独立题组 |
| l2-groupby-agg | 4 | 想统计每个城市的订单数与总销售额，应？ | 应用检验候选 | 新回合使用独立题组 |
| l2-groupby-agg | 5 | 以下关于聚合的错误说法是？ | 误区补救素材 | 否定/绝对措辞需复核 |
| l2-groupby-agg | 6 | 为什么分组聚合是 Spark 中最常见的 Shuffle 来源？ | 课中解释素材 | 正确项唯一最长 |
| l2-groupby-agg | 7 | agg(F.sum('a')) 与 groupBy('k').sum('a') 的关系是？ | 延迟复习候选 | 正确项唯一最长 |
| l2-groupby-agg | 8 | groupBy('city').agg(F.avg('amount')) 结果列名叫 'avg(amount)'，下游引用报错，应？ | 误区补救素材 | 正确项唯一最长 |
| l2-groupby-agg | 9 | 在 groupBy 聚合时，Catalyst 通常还会尝试做？ | 课中解释素材 | 正确项唯一最长 |
| l2-groupby-agg | 10 | 要同时算每个城市的最大金额与行数，应？ | 应用检验候选 | 新回合使用独立题组 |
| l2-write-data | 1 | df.write 属于？ | 误区补救素材 | 正确项唯一最长；write 属性口径已另修 |
| l2-write-data | 2 | write 的默认写入模式是 errorIfExists（mode 默认），这意味着？ | 课中解释素材 | 新回合使用独立题组 |
| l2-write-data | 3 | df.write.partitionBy('dt','city').parquet(path) 会产生？ | 课中解释素材 | 正确项唯一最长 |
| l2-write-data | 4 | 希望下游按日期读取时可跳过无关目录；关于写出布局与小文件，合理的方案是？ | 应用检验候选 | 新回合使用独立题组 |
| l2-write-data | 5 | 以下关于写出的错误说法是？ | 误区补救素材 | 否定/绝对措辞需复核 |
| l2-write-data | 6 | 为什么写出默认采用 errorIfExists 而不是覆盖？ | 课中解释素材 | 正确项唯一最长 |
| l2-write-data | 7 | mode('overwrite') 与 mode('append') 的区别是？ | 延迟复习候选 | 正确项唯一最长 |
| l2-write-data | 8 | 重复运行同一 write 代码却报『path already exists』，是因为？ | 误区补救素材 | 正确项唯一最长 |
| l2-write-data | 9 | partitionBy 写出的目录结构对下游查询有何影响？ | 延迟复习候选 | 正确项唯一最长 |
| l2-write-data | 10 | 要把结果以 Parquet 写出到 out/，且允许重复运行覆盖，应？ | 应用检验候选 | 正确项唯一最长 |
| l2-comprehensive | 1 | 在「读 CSV → filter → withColumn → groupBy → orderBy → write」链路中，哪些是 Transformation？ | 课中解释素材 | 新回合使用独立题组 |
| l2-comprehensive | 2 | 在正式 write 之前，先用 show(20) 验证聚合结果的好处是？ | 课中解释素材 | 正确项唯一最长 |
| l2-comprehensive | 3 | groupBy('region').sum('amount') 得到的聚合列，默认列名是？ | 延迟复习候选 | 正确项唯一最长 |
| l2-comprehensive | 4 | 在 ETL 中过滤「amount 非正或为空」的行，条件应写成？ | 应用检验候选 | 新回合使用独立题组 |
| l2-comprehensive | 5 | 以下关于这个迷你 ETL 链路的错误说法是？ | 误区补救素材 | 正确项唯一最长；否定/绝对措辞需复核 |
| l2-comprehensive | 6 | 整条 ETL 链路中，发生的 Shuffle 通常来自哪些步骤？ | 课中解释素材 | 新回合使用独立题组 |
| l2-comprehensive | 7 | 为什么先 show 验证、确认无误后再 write 是好习惯？ | 延迟复习候选 | 新回合使用独立题组 |
| l2-comprehensive | 8 | 『先做 Transformation 链、最后用 Action 触发』与『每步立即执行』相比？ | 延迟复习候选 | 正确项唯一最长 |
| l2-comprehensive | 9 | 已创建 df，执行 result = df.filter(df.amount > 0) 后语句很快返回但没有数据行打印，合理解释是？ | 误区补救素材 | 正确项唯一最长 |
| l2-comprehensive | 10 | 要读 CSV → 过滤异常行 → 按城市聚合 → 取金额前 10 写出，正确骨架是？ | 应用检验候选 | 新回合使用独立题组 |

## 验证与限制

- 隔离内存库测试覆盖十课题组选择、无答案泄露、重复安装/回滚、短提交拒绝、4/5 与 5/5 门槛、复习失败不降级、其他章节不变。
- 浏览器以只读 DB 派生的模拟响应检查十课两类题组在 320/390/768px 的展示和答题选择，不会提交用户成绩。
- 本机 PySpark 4.2.0 对两组材料的关键查询独立验证；没有实跑文件 append/ignore/overwrite，仍受已知 Windows Hadoop 原生库问题限制；没有宣称 Spark 3.5 运行全兼容。
- 题目正确性仍需后续使用反馈；技术结构校验不能替代真实学习效果、延迟迁移能力与干扰项有效性评估。

## 运维与源文件

- 原题源：app/quiz_seed.json；新题源：app/l2_reviewed_bank.json。新题用稳定 key 标记，运行中以 lesson slug + 不变题干定位 DB 行。修改已安装新题必须显式迁移，不能靠重跑作者脚本覆盖。
- 应用初始化会补齐缺少的新题；不覆盖原题和学习记录。本次因开发服务热重载，新题先由初始化补齐，随后安装器检查/备份时新增数为零；不能把该备份称为新增前备份。
- install_l2_reviewed_bank.py 默认 dry-run；--apply 先备份再插入。历史记录和已有题目行前后校验，旧事实修正另用修复工具。
- sync_seed.py 同时检查两份题源；策划题源漂移会报错，避免无意从 DB 覆盖作者内容。
