"""Small real-Spark checks for revised L1 materials; never accesses app DB."""
import os
import sys
os.environ.setdefault('PYSPARK_PYTHON',sys.executable)
from pyspark.sql import SparkSession

spark=(SparkSession.builder.master('local[2]').appName('l1-question-validation')
    .config('spark.ui.enabled','false').config('spark.ui.showConsoleProgress','false')
    .config('spark.driver.host','127.0.0.1').config('spark.driver.bindAddress','127.0.0.1').getOrCreate())
spark.sparkContext.setLogLevel('ERROR')
try:
    sc=spark.sparkContext
    rdd=sc.parallelize([2,4,6,8,10,12],3)
    assert rdd.getNumPartitions()==3 and rdd.count()==6
    a=sc.parallelize([2,5],2);b=a.map(lambda x:x+3)
    assert a.collect()==[2,5] and b.collect()==[5,8]
    a=sc.parallelize([4,9],2);b=a.filter(lambda x:x>5)
    assert a.count()==2 and b.collect()==[9]
    assert sc.parallelize([2,4,5]).map(lambda x:x*x).collect()==[4,16,25]
    assert sc.parallelize(['','a a','b']).flatMap(lambda s:s.split()).count()==3
    assert sc.parallelize(['red blue','red']).map(lambda s:s.split()).collect()==[['red','blue'],['red']]
    assert sc.parallelize([-2,0,4,7]).filter(lambda x:x>0).collect()==[4,7]
    assert sc.parallelize([1,4,7]).map(lambda x:x+1).filter(lambda x:x>4).collect()==[5,8]
    assert sc.parallelize([1,3,5,7]).filter(lambda x:x>3).count()==2
    assert len(rdd.take(4))==4
    def counts(lines,partitions):
        return dict(sc.parallelize(lines,partitions).flatMap(lambda s:s.split())
            .map(lambda s:(s.lower(),1)).reduceByKey(lambda x,y:x+y).collect())
    assert counts(['Go GO go'],2)=={'go':3}
    assert counts(['Hi hi! HI'],2)=={'hi':2,'hi!':1}
    assert counts(['  ',''],2)=={}
    assert counts(['Spark SQL spark'],2)==counts(['Spark SQL spark'],4)=={'spark':2,'sql':1}
    assert counts([],2)=={}
    # The revised LEFT/FULL distractor needs an orphan dimension to distinguish it.
    orders=spark.createDataFrame([('u1',10),('u9',20)],'uid string,amount long')
    dim=spark.createDataFrame([('u1','north'),('u8','south')],'uid string,region string')
    assert orders.join(dim,'uid','left').count()==2
    assert orders.join(dim,'uid','full').count()==3
    print('PASS real Spark L1 transformations, immutability, bounded results, word-count edge cases and LEFT/FULL counterexample')
finally:
    spark.stop()
