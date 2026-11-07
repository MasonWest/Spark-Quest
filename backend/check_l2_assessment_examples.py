"""Independent numeric/API checks for representative new bank families; no app DB."""
import os,sys,json
from pathlib import Path
os.environ.setdefault('PYSPARK_PYTHON',sys.executable)
from pyspark.sql import SparkSession,functions as F
from pyspark.sql.readwriter import DataFrameWriter
bank=json.loads((Path(__file__).parent/'app/l2_reviewed_bank.json').read_text(encoding='utf-8'))
by_slug={l['lesson_slug']:l['questions'] for l in bank['lessons']}
def answer(slug,index):
 q=by_slug[slug][index];return q['options'][q['correct_index']]
spark=(SparkSession.builder.master('local[1]').appName('l2-assessment-check')
 .config('spark.ui.enabled','false').config('spark.ui.showConsoleProgress','false')
 .config('spark.driver.host','127.0.0.1').config('spark.driver.bindAddress','127.0.0.1')
 .config('spark.sql.shuffle.partitions','2').getOrCreate())
spark.sparkContext.setLogLevel('ERROR')
try:
 for v,(a,b,field,group) in enumerate([(7,13,'score','team'),(11,23,'weight','zone')]):
  offset=v*5
  df=spark.createDataFrame([('red',a),('blue',None),('blue',b)],f'{group} string, {field} long')
  kept=df.filter((F.col(group)=='red') | (F.col(field)>a)).collect()
  assert {(r[group],r[field]) for r in kept}=={('red',a),('blue',b)}
  assert answer('l2-select-filter',offset)==f'red/{a} 与 blue/{b}'
  cases=spark.createDataFrame([(a,),(None,)],f'{field} long')
  assert [r.tag for r in cases.withColumn('tag',F.when(F.col(field)>a,'high').otherwise('other')).collect()]==['other','other']
  assert cases.withColumn('tag',F.when(F.col(field)>a,'high')).first().tag is None
  nulls=spark.createDataFrame([(None,),(None,),(None,)],f'{field} long')
  r=nulls.agg(F.count('*').alias('n'),F.count(field).alias('known'),F.sum(field).alias('s')).first()
  assert (r.n,r.known,r.s)==(3,0,None)
  assert answer('l2-groupby-agg',offset)=='3、0、NULL'
  values=spark.createDataFrame([(a,),(b,),(None,)],f'{field} long')
  r=values.agg(F.count('*'),F.avg(field)).first()
  assert r[0]==3 and r[1]==(a+b)/2
  assert answer('l2-groupby-agg',offset+1)==f'3、{(a+b)/2:g}'
  seq=spark.createDataFrame([(1,a),(2,b),(3,99)],f'seq long, {field} long')
  assert [r[field] for r in seq.orderBy('seq').limit(2).orderBy(F.desc(field)).collect()]==[b,a]
  assert answer('l2-sort-dedup',offset+3)==f'{b}、{a}'
  tie=spark.createDataFrame([('B',a),('A',a),('C',a+1)],f'id string, {field} long')
  assert [r.id for r in tie.orderBy(F.desc(field),F.asc('id')).collect()]==['C','A','B']
  raw=spark.createDataFrame([('A',a),('A',b),('B',0),('B',None)],f'{group} string, {field} long')
  clean=raw.filter(F.col(field)>0)
  report=clean.groupBy(group).agg(F.count('*').alias('cnt'),F.sum(field).alias('total'))
  result=report.collect();assert len(result)==1 and result[0].cnt==2 and result[0].total==a+b
  assert answer('l2-comprehensive',offset+1)=='仅 A，cnt=2'
  assert isinstance(raw.write.mode('overwrite'),DataFrameWriter)
  print('PASS variant',v,'OR/NULL, when branches, all-null aggregate, count/avg, ordered-limit, tie-break, clean/report, writer property',flush=True)
 print('PASS local PySpark',spark.version,'query examples; actual file write modes NOT executed',flush=True)
finally:spark.stop()
