"""Representative real Spark semantics and negative lab-result checks.
No app DB access or Parquet writes; controlled AQE-off plans are not benchmarks.
"""
from pathlib import Path
from contextlib import redirect_stdout
import importlib.util
import io
import json
import os
import sys
os.environ.setdefault('PYSPARK_PYTHON',sys.executable)
from pyspark.sql import SparkSession, functions as F
ROOT=Path(__file__).resolve().parents[1]/'frontend/public/practice'
def load(level,name):
    spec=importlib.util.spec_from_file_location(level+'_'+name,ROOT/f'{level}-graduation/{name}.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
v=load('l4','verify');r4=load('l4','reference');r6=load('l6','reference')
spark=(SparkSession.builder.master('local[2]').appName('l4-l6-independent-check')
 .config('spark.ui.enabled','false').config('spark.ui.showConsoleProgress','false')
 .config('spark.driver.host','127.0.0.1').config('spark.driver.bindAddress','127.0.0.1')
 .config('spark.sql.shuffle.partitions','2').config('spark.sql.adaptive.enabled','false')
 .config('spark.sql.autoBroadcastJoinThreshold','-1').getOrCreate())
spark.sparkContext.setLogLevel('ERROR')
def reject(label,frame,expected):
    try:v.check_report(frame,expected)
    except AssertionError:print('PASS rejects',label,flush=True)
    else:raise AssertionError('Accepted '+label)
try:
    task=json.loads((ROOT/'l4-graduation/task.json').read_text(encoding='utf-8'))
    source=spark.createDataFrame([tuple(r) for r in task['orders']],task['schema'])
    good=r4.build_report(source).cache();expected={'east':(2,100),'west':(1,90)}
    v.check_report(good,expected)
    moved=good.withColumn('total',F.when(F.col('region')=='east',80).otherwise(110).cast('long'))
    assert moved.agg(F.sum('total')).first()[0]==190
    reject('same grand total, wrong regions',moved,expected)
    reject('wrong output types',good.withColumn('cnt',F.col('cnt').cast('double')),expected)
    reject('duplicate report rows',good.union(good),expected)
    capture=io.StringIO()
    with redirect_stdout(capture):good.explain('extended')
    assert 'Optimized Logical Plan' in capture.getvalue() and 'Physical Plan' in capture.getvalue()
    print('PASS extended plan API and grouped query semantics',flush=True)

    sc=spark.sparkContext
    local=sc.parallelize([[1,9],[2,8]],2).flatMap(lambda x:x).mapPartitions(lambda it:sorted(it)).collect()
    assert local==[1,9,2,8]
    assert sc.parallelize([9,1,8,2],2).sortBy(lambda x:x,numPartitions=2).collect()==[1,2,8,9]
    pairs=[('a',2),('a',3),('b',8),('a',4)]
    for count in (2,4):assert dict(sc.parallelize(pairs,count).reduceByKey(lambda a,b:a+b,numPartitions=count).collect())=={'a':9,'b':8}
    assert (1-2)-3 != 1-(2-3)
    print('PASS local/global sort, integer reduce invariance and non-associative counterexample',flush=True)

    left=spark.createDataFrame([(1,10),(1,20),(2,30),(None,9)],'k long, v long')
    right=spark.createDataFrame([(1,'x'),(3,'z'),(None,'null')],'k long, tag string')
    joins=[('BroadcastHashJoin',left.join(F.broadcast(right),'k','inner')),
           ('SortMergeJoin',left.hint('merge').join(right.hint('merge'),'k','inner')),
           ('ShuffledHashJoin',left.hint('shuffle_hash').join(right.hint('shuffle_hash'),'k','inner'))]
    expected_rows=[(1,10,'x'),(1,20,'x')]
    for node,query in joins:
        assert sorted(tuple(r) for r in query.collect())==expected_rows
        assert node in v.plan_text(query),(node,v.plan_text(query))
    assert left.alias('l').join(right.alias('r'),F.col('l.k').eqNullSafe(F.col('r.k'))).count()==3
    print('PASS controlled BHJ/SMJ/SHJ routes, explicit hint with auto threshold disabled, ordinary versus null-safe keys',flush=True)

    task=json.loads((ROOT/'l6-graduation/task.json').read_text(encoding='utf-8'))
    orders=spark.createDataFrame([tuple(r) for r in task['orders']],task['order_schema'])
    dim=spark.createDataFrame([tuple(r) for r in task['dimension']],task['dimension_schema'])
    report=r6.build_enriched_report(orders,dim).cache()
    exp={'east':(1,30),'west':(1,70),'unknown':(2,60)};v.check_report(report,exp)
    reject('lost unknown orders',report.filter(F.col('region')!='unknown'),exp)
    conflict=spark.createDataFrame([('u1','A'),('u1','A')],task['dimension_schema'])
    try:r6.build_enriched_report(orders,conflict)
    except ValueError:pass
    else:raise AssertionError('Exact duplicate non-null dimension keys accepted')
    empty_label=spark.createDataFrame([('u1','')],task['dimension_schema'])
    single=spark.createDataFrame([('z','u1',4)],task['order_schema'])
    v.check_report(r6.build_enriched_report(single,empty_label),{'':(1,4)})
    print('PASS left preservation, unknown allocation, duplicate rejection and empty string distinct from NULL',flush=True)
    print('PASS representative L4-L6 examples on Spark',spark.version,'not a production or Parquet-write certification',flush=True)
finally:spark.stop()
