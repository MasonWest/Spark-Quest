"""Run the hard-lesson toy examples in local Spark. No benchmarks or app DB writes."""
import os,sys
os.environ.setdefault('PYSPARK_PYTHON',sys.executable)
from pyspark.sql import SparkSession
spark=(SparkSession.builder.master('local[1]').appName('hard-lesson-validation')
 .config('spark.ui.enabled','false').config('spark.ui.showConsoleProgress','false')
 .config('spark.driver.host','127.0.0.1').config('spark.driver.bindAddress','127.0.0.1').getOrCreate())
spark.sparkContext.setLogLevel('ERROR')
try:
 sc=spark.sparkContext
 pairs=sc.parallelize([('north',120),('south',200),('north',80),('east',60)],2)
 assert pairs.glom().collect()==[[('north',120),('south',200)],[('north',80),('east',60)]]
 def partial(rows):
  result={}
  for k,v in rows:result[k]=result.get(k,0)+v
  return iter(result.items())
 partials=pairs.mapPartitions(partial)
 routed=partials.partitionBy(2,lambda k:0 if k in ['north','east'] else 1)
 buckets=routed.glom().collect()
 assert sorted(buckets[0])==[('east',60),('north',80),('north',120)]
 assert buckets[1]==[('south',200)]
 assert dict(pairs.reduceByKey(lambda a,b:a+b,2).collect())=={'north':200,'south':200,'east':60}
 debug=routed.toDebugString().decode()
 assert 'ShuffledRDD' in debug,debug
 # The explicitly local runtime still contains a shuffled dependency.
 data=[('north',i) for i in range(90)]+[('south',i) for i in range(10)]
 rdd=sc.parallelize(data,4)
 baseline=rdd.groupByKey(2).mapValues(sum)
 candidate=rdd.reduceByKey(lambda a,b:a+b,2)
 assert dict(baseline.collect())==dict(candidate.collect())=={'north':4005,'south':45}
 assert 'ShuffledRDD' in candidate.toDebugString().decode()
 missing=dict(candidate.filter(lambda kv:kv[0]!='north').collect())
 assert missing!={'north':4005,'south':45}
 assert dict(sc.parallelize([('north',120),('north',30),('north',50),('north',80)],2).reduceByKey(lambda a,b:a+b).collect())=={'north':280}
 print('PASS local PySpark',spark.version,': partition routing, partial/global sums, local Shuffle dependency, groupByKey/reduceByKey integer equivalence, rejected key loss. NO performance benchmark.',flush=True)
finally:
 spark.stop()
