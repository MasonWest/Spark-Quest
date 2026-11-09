"""Execute the two new lessons on small independent fixtures; no application DB."""
import os
import sys
os.environ.setdefault('PYSPARK_PYTHON',sys.executable)
from pyspark import StorageLevel
from pyspark.sql import SparkSession,functions as F

spark=(SparkSession.builder.master('local[2]').appName('extension-course-check')
 .config('spark.ui.enabled','false').config('spark.ui.showConsoleProgress','false')
 .config('spark.driver.host','127.0.0.1').config('spark.driver.bindAddress','127.0.0.1')
 .config('spark.sql.shuffle.partitions','2').getOrCreate())
spark.sparkContext.setLogLevel('ERROR')
try:
    spark.createDataFrame([('a','north',70),('b','north',40),('c','north',10),('d','south',90)],'id string,city string,amount long').createOrReplaceTempView('orders')
    full=spark.sql('SELECT *,SUM(amount) OVER(PARTITION BY city) AS city_total FROM orders').collect()
    assert len(full)==4 and {r.id:r.city_total for r in full}=={'a':120,'b':120,'c':120,'d':90}
    numbered='SELECT *,ROW_NUMBER() OVER(PARTITION BY city ORDER BY amount DESC,id ASC) AS rn FROM orders'
    top=spark.sql(f'WITH numbered AS ({numbered}) SELECT id FROM numbered WHERE rn<=2').collect()
    assert {r.id for r in top}=={'a','b','d'}
    wrong=spark.sql('SELECT id FROM orders ORDER BY amount DESC,id ASC LIMIT 2').collect()
    assert {r.id for r in wrong}!={'a','b','d'}
    print('PASS window preserves details; independent per-city Top2; rejects global LIMIT substitution',flush=True)
    spark.createDataFrame([('a',100),('b',100),('c',90)],'id string,score long').createOrReplaceTempView('scores')
    ranks=spark.sql('SELECT id,RANK() OVER(ORDER BY score DESC) AS r,DENSE_RANK() OVER(ORDER BY score DESC) AS d FROM scores').collect()
    assert {r.id:(r.r,r.d) for r in ranks}=={'a':(1,1),'b':(1,1),'c':(3,2)}
    print('PASS business ties: RANK 1/1/3 versus DENSE_RANK 1/1/2',flush=True)
    events=[('u1','e10',5,'z'),('u1','e11',5,'a'),('u2','e3',None,'x'),('u2','e4',7,'b'),('u3','e5',None,'m'),('u3','e6',None,'n')]
    spark.createDataFrame(events,'user_id string,event_id string,event_time long,status string').createOrReplaceTempView('events')
    selected=spark.sql('''WITH numbered AS (
      SELECT *,ROW_NUMBER() OVER(PARTITION BY user_id ORDER BY event_time DESC NULLS LAST,event_id DESC) AS rn FROM events)
      SELECT user_id,event_id,event_time,status FROM numbered WHERE rn=1''').collect()
    expected={'u1':('e11',5,'a'),'u2':('e4',7,'b'),'u3':('e6',None,'n')}
    assert {r.user_id:(r.event_id,r.event_time,r.status) for r in selected}==expected
    wrong=spark.sql('SELECT user_id,MAX(event_id) AS event_id,MAX(event_time) AS event_time,MAX(status) AS status FROM events GROUP BY user_id').collect()
    assert {r.user_id:(r.event_id,r.event_time,r.status) for r in wrong}!=expected
    print('PASS latest whole row, deterministic tie key, NULL-time policy; rejects independent MAX-column assembly',flush=True)
    base=spark.range(0,12,1,3).selectExpr('id','id % 2 AS region','id * 10 AS amount')
    cached=base.persist(StorageLevel.MEMORY_AND_DISK_DESER)
    assert cached.storageLevel==StorageLevel.MEMORY_AND_DISK_DESER
    assert len(spark.sparkContext._jsc.sc().getRDDStorageInfo())==0
    try:
        assert cached.count()==12
        blocks=spark.sparkContext._jsc.sc().getRDDStorageInfo()
        assert len(blocks)>0 and all(r.numCachedPartitions()==r.numPartitions() for r in blocks)
        report=cached.groupBy('region').agg(F.sum('amount').alias('total'))
        assert {r.region:r.total for r in report.collect()}=={0:300,1:360}
        assert 'InMemoryTableScan' in report._jdf.queryExecution().executedPlan().toString()
        print('PASS persist intent versus actual blocks, materialization and cache scan with unchanged results',flush=True)
        raise ValueError('synthetic report-B failure')
    except ValueError as error:
        assert str(error)=='synthetic report-B failure'
    finally:
        cached.unpersist(blocking=True)
    assert not cached.storageLevel.useMemory and not cached.storageLevel.useDisk
    assert len(spark.sparkContext._jsc.sc().getRDDStorageInfo())==0
    assert cached.count()==12
    print('PASS finally cleans cache after error; unpersist removes blocks and leaves query recomputable',flush=True)
    print('Runtime Spark',spark.version,'; tiny fixture only, no disk spill or speedup certification',flush=True)
finally:
    spark.stop()
