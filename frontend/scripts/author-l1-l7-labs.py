"""Publish two explicit independent labs; copy the shared verifier to all five kits."""
import json
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
content=root/'src/content/capstones.json'
bank=json.loads(content.read_text(encoding='utf-8'))
outputs={}
def write(path,text):
 outputs[path]=text.encode('utf-8')
specs={
 'l1-rdd-exercise':dict(folder='l1-graduation',title='独立实作：从文本得到可靠词频',minutes=35,
  brief='把多行短文本转换为词频。先手算一个预期，再自己编写 RDD 链，面对新词、空行和不同分区数验收。',
  task=dict(task='rdd',lines=['Spark spark makes progress','Learn Spark','', 'word, word'],partitions=[2,4]),
  signature='build_counts(sc, lines, partitions)',
  code="return (sc.parallelize(lines, partitions).flatMap(lambda line: line.split())\n            .map(lambda word: (word.lower(), 1))\n            .reduceByKey(lambda a, b: a+b, numPartitions=partitions))",
  note='flatMap 将每行变成词，map 产生键值，reduceByKey 汇合计数。构建链是惰性的，验收中的 take 才触发计算；返回 Driver 的教学结果有界。换分区改变布局，不改变每个词的次数。',
  contract=['实现 build_counts(sc, lines, partitions)，返回 Pair RDD；每个词一行整数次数，输出分区数采用传入参数。',
   '按 Python str.split() 的空白规则拆词，再 lower()；标点保留，所以 word 与 word, 是不同的词。每次出现都计数，不对原文或词去重。',
   '空行、纯空白行不生成空词；空输入返回空键集合。不可写死词、次数或结果行数。',
   '验收使用新词、大小写、制表空白、标点和空输入，在 2/4 分区下分别核对独立预期。',
   '不要先将整个 RDD collect 到 Driver 再统计；diagnosis() 说明转换、动作、分区和有界回收的区别，代码策略及论证质量需人工复核。'],
  hints=[('先手算规则','给 Spark spark 和 word, word 分别手算，确定大小写与标点规则。'),('把一行变多个元素','想清楚拆词该产生列表还是多个 RDD 元素，再建立 (词,1)。'),('处理顺序骨架','parallelize → flatMap 拆词 → map 小写键值 → 按键加法并指定分区。不要去重每次出现。')],
  checks=[('词频语义','独立 Counter 核对出现次数、大小写和标点。'),('边界与分区','新词、空白和空输入在两种分区数下检查。'),('独立解释','保存词频证据与诊断草稿，人工核对是否理解惰性与 Driver 边界。')]),
 'l7-comprehensive':dict(folder='l7-graduation',title='独立实作：证明一次有边界的优化',minutes=60,
  brief='一份地区报表为简单文本清洗使用了 Python UDF。保留业务语义，改用内置表达式，再保存真实前后计划；用证据区分结构变化和性能收益。',
  task=dict(task='tuning',schema='id string, region string, amount long',orders=[['a',' North ',30],['b','NORTH',20],['c',None,10],['d','',8],['e','south',-4]],
   observation=dict(source='synthetic teaching scenario, not a measured benchmark',symptom='Python boundary appears in baseline plan; speedup is unknown')),
  signature='build_report(orders)',
  code="from pyspark.sql import functions as F\n    return (orders.filter(F.col('amount') > 0)\n            .withColumn('region', F.coalesce(F.lower(F.trim('region')), F.lit('unknown')))\n            .groupBy('region').agg(F.count('*').alias('cnt'), F.sum('amount').alias('total')))",
  note='基线和候选都只统计正金额；ASCII 空格 trim 后 lower，NULL 归 unknown，空字符串保留。受控计划去掉了 Python UDF 边界，但没有测定生产加速。下一步需同输入同资源重复测量时延、CPU、Shuffle 和结果，并保留基线回退。',
  contract=['实现 build_report(orders)，只统计 amount>0，输出 region string、cnt long、total long，每地区一行。',
   '地区仅去掉两端 ASCII 空格再转小写；NULL 变 unknown，空字符串仍是空字符串。制表符不属于这里约定的 trim 字符。',
   '不得硬编码地区或总额，不把明细 collect 到 Python。用等价的 Spark 内置表达式替换基线普通 Python UDF。',
   '验收独立核对新地区、NULL、空串、空格、无效金额、空输入；保存当前 Spark 版本和实际前后计划，候选不能保留 Python UDF 边界。',
   'task.json 的症状为合成教学设定。实际运行只证明本数据结果与计划结构，不自动证明提速、容量安全、AQE 收益或生产可用。',
   'diagnosis() 写出假设、保持的语义、现有证据、下一轮测量和回退。文字与调优决策需要人工复核。'],
  hints=[('先固定结果','先核对 NULL、空串、正金额和清洗后的分组，再谈更快。'),('寻找等价表达式','把简单清洗拆为 trim、lower 和 coalesce；检查 Python strip 默认规则是否太宽。'),('证据链骨架','核对逐组结果 → 保存前后实际计划 → 检查 Python 边界 → 明确未测性能 → 设计公平重复实验与回退。')],
  checks=[('结果契约','独立 Python 预期核对逐地区笔数、金额与清洗边界。'),('实际计划','受控基线含 Python 边界，候选移除该边界并保存文本。'),('审慎结论','记录实际版本和人工待审诊断，计划变化不冒充性能测量。')])}
for slug,s in specs.items():
 folder=root/'public/practice'/s['folder'];folder.mkdir(parents=True,exist_ok=True)
 write(folder/'task.json',json.dumps(s['task'],ensure_ascii=False,indent=2)+'\n')
 write(folder/'starter.py',f'"""Implement the contract in task.json / README.txt; do not hard-code results."""\n\ndef {s["signature"]}:\n    raise NotImplementedError("Write your own transformation chain")\n\ndef diagnosis():\n    raise NotImplementedError("Explain correctness, execution and remaining evidence")\n')
 write(folder/'reference.py',f'"""Reference for comparison after an independent attempt."""\n\ndef {s["signature"]}:\n    {s["code"]}\n\ndef diagnosis():\n    return {s["note"]!r}\n')
 write(folder/'README.txt',s['title']+'\n\n'+'\n'.join(s['contract'])+'\n\n运行：python verify.py --solution starter.py\n需 Python、Java 与 PySpark。所有测试为小型本地教学数据，不访问应用数据库。\n验收自动创建新的 practice/evidence-* 目录；--output 只接受尚不存在的新目录。\nPASS 仅指自动检查，诊断质量始终 manual_review=required。失败时查看 validation-result.json 的具体阶段；环境失败不等于知识错误。\n本任务不写 Parquet，也不替代 L2/L3 的真实文件验收。\n')
 assets=[('任务数据 task.json','task.json'),('代码骨架 starter.py','starter.py'),('独立验收 verify.py','verify.py'),('运行说明 README.txt','README.txt')]
 bank['lessons'][slug]=dict(id=s['folder']+'-v1',title=s['title'],estimatedMinutes=s['minutes'],brief=s['brief'],contract=s['contract'],
  downloads=[dict(label=label,href=f'/practice/{s["folder"]}/{name}') for label,name in assets],
  solution=dict(label='下载参考实现 reference.py',href=f'/practice/{s["folder"]}/reference.py'),command='python verify.py --solution starter.py',
  checks=[dict(title=a,body=b) for a,b in s['checks']],hints=[dict(title=a,body=b) for a,b in s['hints']],
  validationNote='自动 PASS 表示小型教学数据的程序检查通过。诊断质量仍标记 manual_review=required；真实优化收益需另做公平测量。本任务不考核 Parquet 写出。')
bank['version']=max(bank['version'],5)
write(content,json.dumps(bank,ensure_ascii=False,indent=2)+'\n')
source=(root/'scripts/lab-verifier-template.py').read_bytes()
for level in [1,4,5,6,7]:outputs[root/f'public/practice/l{level}-graduation/verify.py']=source
for path,data in outputs.items():
 if '--check' in sys.argv:assert path.read_text(encoding='utf-8')==data.decode('utf-8').replace('\r\n','\n'),str(path)
 elif path.name=='verify.py':path.write_bytes(data)
 else:path.write_text(data.decode('utf-8'),encoding='utf-8',newline='\n')
print('PASS seven independent capstones; five self-contained verifier copies')
