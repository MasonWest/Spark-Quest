"""Author the reviewed L2 bank; writes JSON only, never the learning database."""
import json
from pathlib import Path
BASE=Path(__file__).resolve().parent

def scenarios(slug,v):
 a,b=(7,13) if v==0 else (11,23)
 field='score' if v==0 else 'weight'
 group='team' if v==0 else 'zone'
 path='practice/check_a' if v==0 else 'practice/check_b'
 collision='count' if v==0 else 'collect'
 precision=8 if v==0 else 6
 max_money='999999.99' if v==0 else '9999.99'
 extrema='max' if v==0 else 'min'
 unit=1000.0 if v==0 else 1000000.0
 unit_name='total_k' if v==0 else 'total_m'
 if slug=='l2-what-is-dataframe':return [
 (f"传感器表有 (S1,{a})、(S1,{b}) 两行。df.select('sensor') 后再 show，不做去重，应有几行？",['两行 S1','一行 S1','一行 S1 加一个合计','零行，仅剩 Schema'],'select 改变列，不自动合并相同值；两个输入行仍各贡献一行。','projection'),
 (f"某表 {field} 在 show 中显示为 {a}，Schema 却是 string。现在能确认什么？",['它当前是文本列','它当前是整数列','它当前是浮点列','仅凭显示能确认精度'],'列类型以 Schema 为准，数字外观不能把文本列变成整数。','schema'),
 (f"同事创建了一个很小的 {group} 统计 DataFrame。它是否必须先分散在多台物理机器内存里才成立？",['不必须，local 模式也可以创建','必须，至少两台机器才能创建','必须，创建就会把各行缓存','不必须，但它只能保存文本'],'DataFrame 是带命名列的分布式抽象；不要求当前部署一定多机，也不承诺创建即缓存。','abstraction'),
 (f"df 中 {field} 为 {a}、{b}。执行 df.filter(df['{field}']>{a})，不保存返回值，再查看原 df 的行数，是多少？",['2','1','0','无法访问原 df'],'filter 返回新查询，不会原地改写原 df。这里输入明确为两行。','immutability'),
 (f"一份数据以 {group}、{field} 两个命名字段表达业务。相对于任意 Python 对象的 RDD，结构化列信息主要给 SQL 优化器什么帮助？",['分析列与表达式的关系','确定所有业务值都合法','保证每次查询无需扫描','固定每个任务的运行时长'],'Schema 与表达式结构给优化器分析机会，不提供业务正确性或固定性能保证。','optimizer')]
 if slug=='l2-create-dataframe':return [
 (f"已在本地准备 rows=[('k',{a}),('m',{b})]，需要列名 code、n。哪行创建 Spark DataFrame？",["spark.createDataFrame(rows, ['code','n'])","spark.read.csv('rows').select('code','n')","sc.parallelize(rows).collect()","pd.DataFrame(rows, columns=['code','n'])"],'createDataFrame 可直接接收本地列表；pandas、RDD、本地列表不是本题的 Spark DataFrame。','local-source'),
 (f"CSV 内容首行为 {group},{field}，第二行为 red,{a}。默认未给 schema、未开 header/inferSchema，第一行会怎样？",['作为普通数据，列名类似 _c0/_c1','作为列名，第二列自动成整数','被当成格式错误而忽略','作为列名，所有行已缓存'],'普通 CSV 默认不认首行为表头；未显式声明或推断时，字段通常按字符串读取。','csv-header'),
 (f"读取 {path}.csv 时打开 inferSchema，但还没写 show。观察到提前读取数据，哪种解释成立？",['推断类型可以额外遍历数据','show 已经被自动偷偷调用','全部业务行必已缓存到 Driver','说明 Spark 不支持惰性变换'],'Schema 推断是准备工作，可能提前执行；不能由此推导后续变换失去惰性。','inference-work'),
 (f"输入已确认是 {path}.parquet 数据集，需要保留文件中的类型信息。选择读取方式。",[f"spark.read.parquet('{path}.parquet')",f"spark.read.csv('{path}.parquet')",f"spark.read.json('{path}.parquet')",f"spark.read.text('{path}.parquet')"],'按实际文件格式选择读取器，不能把所有表状数据都当成 CSV。','file-format'),
 (f"CSV 的 {field} 必须按 long 读取，字段名也已知。如何减少自动类型推断这一步？",[f"read.schema('{group} string, {field} long')",f"read.option('header', True)",f"read.option('mode', 'FAILFAST')",f"read.option('delimiter', ',')"],'显式 Schema 规定类型；header、mode、delimiter 分别负责其他读取约定。','explicit-schema')]
 if slug=='l2-schema-types':return [
 (f"编号值为 {3000000000+v}，要用整数类型保存且超出 32 位有符号整数范围，选哪种？",['LongType','IntegerType','BooleanType','DateType'],'LongType 是更大范围的整数类型；选择应基于数值范围，不只看字段叫编号。','integer-range'),
 (f"CSV 的 {field} 显式声明为整数，默认 PERMISSIVE；出现文本 bad。仅凭显式 Schema 能保证遇错终止吗？",['不能，解析模式另有职责','能，Schema 自动变成 FAILFAST','能，nullable 总是强制失败','不能，因为 Schema 完全无作用'],'Schema 与解析模式是不同约定；默认 PERMISSIVE 的异常字段可能为 null。','parse-mode'),
 (f"某表 {field} 允许空值。现在业务要求核对实际空值行数，应选哪个检查？",[f"df.filter(df['{field}'].isNull()).count()",'df.printSchema()','len(df.columns)',f"df.select('{field}')"],'实际值的空值计数要对数据求值；结构说明不能替代实际数据检查。','business-validation'),
 (f"已知金额上限 {max_money}，需要两位小数。哪种类型直接表达十进制定点精度约定？",[f'DecimalType({precision},2)','LongType()','DoubleType()','DecimalType(2,2)'],'足够的总精度与两位小数可表示本题范围；DecimalType(2,2) 只剩零位整数部分。实际运算仍需约定舍入与溢出。','decimal'),
 (f"StructField('{field}', LongType(), True) 的 True 表达什么？",['字段允许出现空值','字段所有值必须大于零','读取错误时必须立刻报错','字段参与所有分区划分'],'nullable 是结构属性，不是正值约束、解析模式或分区策略。','nullable')]
 if slug=='l2-inspect':return [
 (f"表里恰有一列叫 {collision}，想引用这列而不是访问同名方法，应使用？",[f"df['{collision}']",f"df.{collision}()",f"df.{collision}","len(df)"],'中括号字符串按列名引用；同名属性可能与 DataFrame 方法冲突。','column-conflict'),
 (f"需要将至多 {a} 行已知小样本取回 Python 做断言，哪项返回 Row 列表？",[f"df.take({a})",f"df.show({a})",'df.printSchema()',f"df.limit({a})"],'take 返回本地 Row 列表；show 打印，limit 返回新的 DataFrame。要控制取回规模。','sample-return'),
 (f"备注超过默认显示长度，要显示 {a} 行且不截断文本，应使用？",[f"df.show({a}, truncate=False)",f"df.show({a}, truncate=True)",f"df.show(truncate={a})",f"df.limit({a})"],'show 的 n 控制行数，truncate=False 控制文本截断；不要把两个参数混为一谈。','display'),
 (f"只查看 {group}、{field} 的 printSchema 输出，能否证明 {field} 没有实际空值？",['不能，需要检查实际数据','能，结构打印会检查所有值','能，只要 show 没显示错误','不能，因为 Schema 没有类型'],'Schema 展示结构，不能据此证明实际值满足非空业务规则。','schema-vs-values'),
 (f"df.orderBy(df['{field}'].desc()).show({a}) 输出很少却仍慢，哪种解释合理？",['上游排名仍可能检查大量输入','show 会修改源文件来排序','show 的参数就是扫描行数','只要小输出就一定是网络故障'],'输出行数不等于上游处理量；具体成本需要结合计划和运行指标。','small-output')]
 if slug=='l2-select-filter':return [
 (f"数据 ({group},{field}) 为 ('red',{a})、('blue',null)、('blue',{b})。filter((col('{group}')=='red') | (col('{field}')>{a})) 保留哪些行？",[f"red/{a} 与 blue/{b}",f"只有 red/{a}",f"只有 blue/{b}",f"全部三行"],'OR 任一条件为真即可；blue/null 的两项分别是假与未知，最终不为真。','null-or'),
 (f"需要 {group}='red' 且 {field}>{a}，哪项是 Column 条件？",[f"(df['{group}']=='red') & (df['{field}']>{a})",f"(df['{group}']=='red') and (df['{field}']>{a})",f"(df['{group}'] is 'red') & (df['{field}']>{a})",f"df['{group}']=='red' & df['{field}']>{a}"],'使用 & 组合 Column 条件，并为每项比较加括号；不能用 Python and 或 is 替代。','column-boolean'),
 (f"使用 SQL 字符串调用 where，只要 {group} 等于 red，应写哪项？",[f'''df.where("{group} = 'red'")''',f'''df.where("{group} is 'red'")''',f'''df.where("{group} == red")''',f'''df.where("{group} = col('red')")'''],'SQL 字符串中的文本常量要加引号；不要把 Python 列表达式语法机械塞进去。','sql-condition'),
 (f"一行 {field}={a}，执行 selectExpr('{field} * 2 AS doubled')，输出列与值是什么？",[f"doubled={2*a}",f"{field}={2*a}",f"doubled={a}",f"{field}={a}"],'selectExpr 计算表达式并按 AS 命名，选择的不是原列的原值。','expression'),
 (f"新查询 df2=df.filter(df['{field}']>{a}).select('{group}') 建立后，对原 df 能确认什么？",['原查询未被原地修改','原 df 自动只剩一个列','原 df 自动被写回源文件','原 df 无法再触发 Action'],'变换返回新查询；赋给 df2 不会把 df 本身原地改掉。','immutability')]
 if slug=='l2-withcolumn':return [
 (f"要给每行新增 origin='{group}' 固定来源，应使用？",[f"df.withColumn('origin', F.lit('{group}'))",f"df.withColumn('origin', F.col('{group}'))",f"df.withColumn('origin', '{group}')",f"df.withColumn('{group}', F.col('origin'))"],'lit 构造固定值表达式，col 引用已有字段，裸字符串不是这里要求的 Column。','literal'),
 (f"{field}={a}、null 两行。when(col('{field}')>{a},'high').otherwise('other') 生成什么？",["other、other","high、other","other、null","high、null"],'大于不包含等于；null 比较也不为 true，两个输入都进入 otherwise。','when-null'),
 (f"原 df 的 {field}={a}；changed=df.withColumn('{field}',F.col('{field}')+1)。两份查询的值分别是？",[f"原 {a}，新 {a+1}",f"原 {a+1}，新 {a+1}",f"原 {a}，新 {a}",f"原 {a+1}，新 {a}"],'同名替换作用于返回的查询；原 df 没有原地改变。','replacement'),
 (f"要先由 {field} 得到 x，再由 x 得到 y，哪条链描述顺序正确？",[f"df.withColumn('x',F.col('{field}')+1).withColumn('y',F.col('x')*2)",f"df.withColumn('y',F.col('x')*2).withColumn('x',F.col('{field}')+1)",f"df.withColumn('x',F.lit('{field}')).withColumn('y',F.col('x')*2)",f"df.withColumn('y',F.lit('x')).withColumn('x',F.col('{field}')+1)"],'后一步的 x 要先成为前一步结果中的列，字符串常量不能替代数值列引用。','dependent-columns'),
 (f"when(col('{field}')>{a},'high') 未写 otherwise；输入 {field}={a}，结果是什么？",['NULL','high','False','原数值'],'when 没有命中又未指定 otherwise，返回 null；不是自动 False 或原值。','unmatched-when')]
 if slug=='l2-sort-dedup':return [
 (f"仅两列 (user,n) 为 (u,{a})、(u,{a})、(u,{b})、(z,{b})。distinct 与按 user 去重的行数分别为？",['3 与 2','2 与 2','3 与 3','4 与 2'],'整行有三种，user 只有两种；按键去重没有指定其他列保留规则。','dedup-grain'),
 (f"记录 (id,{field}) 为 (B,{a})、(A,{a})、(C,{a+1})。按 {field} 降序，平手按 id 升序，应怎样排序？",[f"orderBy(F.desc('{field}'),F.asc('id'))",f"orderBy(F.desc('{field}'),F.desc('id'))",f"orderBy(F.asc('id'),F.desc('{field}'))",f"orderBy(F.desc('id'),F.asc('{field}'))"],'首要键决定指标优先，次要键决定并列顺序；本题 id 唯一。','tie-break'),
 (f"同用户有 n={a} 和 n={b}。orderBy(desc('n')).dropDuplicates(['user']) 是否保证保留 {b}？",['不保证，需明确组内取值规则','保证，输入排序就是保留契约','保证，去重默认对 n 求最大','不保证，因为去重永远留最小'],'排序后的输入不为 dropDuplicates 增加保留最大值的承诺。','retention'),
 (f"输入已按唯一 seq 升序，{field} 依次为 {a}、{b}、99。orderBy('seq').limit(2).orderBy(desc('{field}')) 得到？",[f"{b}、{a}",f"99、{b}",f"99、{a}",f"{a}、{b}"],'在本题明确的输入序列中先截两行，再排序；不能当成全体数据的 Top 2。实际未排序数据的 limit 不应承诺稳定取哪两条。','operator-order'),
 (f"只要每用户 {'最大' if v==0 else '最小'} n 值，不需要其他明细列，哪项直接表达该需求？",[f"groupBy('user').agg(F.{extrema}('n').alias('extreme'))","dropDuplicates(['user']).select('user','n')","orderBy(F.desc('n')).dropDuplicates(['user'])","select('user','n').distinct()"],'显式极值聚合表达组内指标；随意保留一行不能替代该聚合。','max-per-key')]
 if slug=='l2-groupby-agg':return [
 (f"某 {group} 组的 {field} 三行全为 NULL。count('*')、count('{field}')、sum('{field}') 分别是？",['3、0、NULL','3、3、0','0、0、0','3、0、0'],'行数为三，非空值数为零；sum 的全空组结果为 null，不自动补零。','all-null'),
 (f"同组 {field} 为 {a}、{b}、NULL，count('*') 与 avg('{field}') 分别是？",[f"3、{(a+b)/2:g}",f"2、{(a+b)/2:g}",f"3、{(a+b)/3:g}","3、NULL"],'avg 忽略空值但 count(*) 数所有行；平均值分母与行数不一定相同。','count-avg'),
 (f"按 {group} 聚合 sum('{field}').alias('total') 后，正常结果中可以直接 select 什么？",[f"'{group}' 与 'total'",f"'{group}' 与原始 '{field}'",f"原始 '{field}' 与任意订单号",f"所有输入明细列均仍保留"],'分组结果的粒度已经改变，只有分组键与已生成的聚合结果可直接引用。','output-grain'),
 (f"A 分区有 {a}、{b} 两值，B 分区有 40 一值。求全局平均值，哪个思路可靠？",['汇合总和与数量，再相除','直接相加两个分区平均值','只取值最多分区的平均值','两个分区平均值不加权平均'],'各分区样本数不同，不能对分区均值不加权平均；使用总和和数量可保留权重。','weighted-mean'),
 (f"每 {group} 要最大 {field} 与记录数；该列可能有 NULL，且结果列名为 mx/cnt，选择表达式。",[f"agg(F.max('{field}').alias('mx'),F.count('*').alias('cnt'))",f"agg(F.sum('{field}').alias('mx'),F.count('*').alias('cnt'))",f"agg(F.max('{field}').alias('mx'),F.count('{field}').alias('cnt'))",f"agg(F.min('{field}').alias('mx'),F.count('*').alias('cnt'))"],'最大值用 max，总记录数用 count(*)；count(列) 在有空值时不同。','multi-metric')]
 if slug=='l2-write-data':return [
 (f"同一 {a} 行结果向一个初始不存在的目录成功 append 两次，无其他写入。读回应有多少行？",[str(a*2),str(a),'0',str(a+1)],'普通文件追加不按内容去重；重复批次会重复追加。','append'),
 (f"只运行 writer=df.write.mode('{'overwrite' if v==0 else 'append'}')，还未调用 parquet/csv/save。此时是否已经完成写出？",['没有，只准备了写入器与选项','已经完成，并覆盖默认路径','已经完成，但仅写入 Driver','没有，因为 overwrite 不支持文件'],'df.write 是 DataFrameWriter 入口；实际保存方法才请求写出。不能把访问属性本身当成已写盘。','writer-vs-action'),
 (f"按 {group} 调用 partitionBy 后，某个 {group} 目录下可否有多个 part 文件？",['可以，目录布局不承诺单文件','不可以，每值固定一个文件','可以，但说明数据一定重复','不可以，多个文件就是写入失败'],'目录分区和文件数量是不同维度；文件数受写任务、数据量和追加等影响。','layout'),
 (f"目标 {path} 已有昨日结果，今日使用 mode('ignore') 写出新完整结果，成功返回后应如何理解？",['已有目标保留，本次新结果被跳过','昨日结果与今日结果都已追加','昨日结果已被今日结果替换','今日按业务键更新了昨日结果'],'ignore 不承担追加、覆盖或按键更新；目标存在时跳过本次写入。','ignore'),
 (f"报表先按 total 排序再写到 {path}，读回后能否依赖文件读取顺序展示排名？",['不能，应按所需键重新排序','能，Parquet 固定保存全局行序','能，只要文件扩展名一致','不能，因为 Parquet 无法保存数值'],'读回数据集没有业务排序保证，展示排名时应明确 orderBy。','readback-order')]
 if slug=='l2-comprehensive':return [
 (f"新输入 {field} 为 {a}、{b}、0、-2、NULL。业务只保留正值，有效行数与合计是多少？",[f"2、{a+b}",f"3、{a+b}",f"4、{a+b-2}",f"5、{a+b}"],'严格大于零只保留两个正值；null 比较不为 true，零和负数也排除。','clean-verify'),
 (f"输入 (地区,金额) 为 (A,{a})、(A,{b})、(B,0)、(B,NULL)。只统计正金额后，每地区有效订单数应怎样？",['仅 A，cnt=2','A cnt=2，B cnt=2','A cnt=1，B cnt=1','A cnt=2，B cnt=1'],'B 没有有效行，普通过滤再 groupBy 不会凭空生成一个 B 零值组。','missing-groups'),
 (f"report 已按地区生成 total，现需 {unit_name}（除以 {unit:g}）。表达式应引用哪一列？",[f"F.col('total') / {unit}",f"F.col('amount') / {unit}",f"F.lit('total') / {unit}",f"F.col('region') / {unit}"],'聚合后的报告使用 total；原始 amount 明细列已不在结果粒度中。','post-aggregation'),
 (f"报告预期两地区合计 {a+b}，实际合计相同但两个地区的金额互换。只检查总和能否验收？",['不能，还要核对地区与各自指标','能，只要两个地区行数没变','能，因为总额包含全部语义','不能，因为总和不能作为指标'],'总量检查可能漏掉分组错配；总量有用，但不能替代关键分组明细。','group-validation'),
 (f"完整报表需要按计划重算，输出到专用练习目录 {path}。哪项最符合可验证交付？",['明确写入策略，读回核对字段与分组指标','默认 append，看到目录存在就结束','默认 ignore，只核对控制台没报错','写出前 show 一行便视为全量正确'],'明确目标、重跑语义与验收指标；抽查和成功返回都不是完整正确性证明。','delivery')]
 raise ValueError(slug)

def build():
 seed=json.loads((BASE/'app/quiz_seed.json').read_text(encoding='utf-8'))
 lessons=[]
 for li,g in enumerate(x for x in seed['quizzes'] if x['lesson_slug'].startswith('l2-')):
  questions=[]
  for v in range(2):
   for i,(prompt,options,explanation,knowledge) in enumerate(scenarios(g['lesson_slug'],v)):
    purpose='assessment' if v==0 else 'review' if i<3 else 'remediation'
    position=(li*10+v*5+i)%4
    rotated=options[-position:]+options[:-position] if position else options
    # Conceptual variants without numeric literals still need distinct prompts.
    prompt=('课末情境：' if v==0 else '复习情境：')+prompt
    questions.append(dict(key=f"{g['lesson_slug']}.v1.{purpose}.{i+1}",purpose=purpose,knowledge_id=g['lesson_slug']+'.'+knowledge,dimension=['apply','debug','mechanism','comparison','apply'][i],type='single_choice',prompt=prompt,options=rotated,correct_index=position,explanation=explanation))
  lessons.append(dict(lesson_slug=g['lesson_slug'],questions=questions))
 return dict(version=1,sources=['https://spark.apache.org/docs/3.5.6/sql-ref-null-semantics.html','https://spark.apache.org/docs/3.5.6/sql-data-sources-csv.html','https://spark.apache.org/docs/3.5.6/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.write.html'],lessons=lessons)
if __name__=='__main__':
 data=build();(BASE/'app/l2_reviewed_bank.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('Authored',sum(len(l['questions']) for l in data['lessons']),'purpose-separated questions')
