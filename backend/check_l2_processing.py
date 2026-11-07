"""Verify the processing-course examples against the installed local PySpark.
Uses synthetic rows only; never opens the application's learning database.
"""
import os
import sys
os.environ.setdefault('PYSPARK_PYTHON', sys.executable)
from pyspark.sql import SparkSession, functions as F

spark = (SparkSession.builder.master('local[1]').appName('spark-quest-content-check')
         .config('spark.ui.enabled', 'false')
         .config('spark.ui.showConsoleProgress', 'false')
         .config('spark.driver.host', '127.0.0.1')
         .config('spark.driver.bindAddress', '127.0.0.1')
         .config('spark.sql.shuffle.partitions', '2').getOrCreate())
spark.sparkContext.setLogLevel('ERROR')
try:
    orders = spark.createDataFrame([('north', 120), ('north', 80), ('south', 200), ('east', 60)], 'region string, amount long')
    selected = orders.filter((orders['region']=='north') & (orders['amount']>100)).select('region','amount')
    assert [tuple(r) for r in selected.collect()] == [('north',120)]
    assert orders.count()==4
    assert orders.withColumn('amount_k',F.col('amount')/1000.0).filter('amount=120').first()['amount_k']==0.12
    assert orders.withColumn('source',F.lit('web')).first()['source']=='web'
    converted=orders.withColumn('amount',F.col('amount')/1000.0)
    assert orders.agg(F.max('amount')).first()[0]==200
    assert converted.agg(F.max('amount')).first()[0]==0.2
    missing=spark.createDataFrame([('north',120),('north',80),('north',None)],'region string, amount long')
    tagged=missing.withColumn('tag',F.when(F.col('amount')>=100,'large').otherwise('normal'))
    assert tagged.filter(F.col('amount').isNull()).first()['tag']=='normal'
    repaired=missing.withColumn('tag',F.when(F.col('amount').isNull(),'check').when(F.col('amount')>=100,'large').otherwise('normal'))
    assert repaired.filter(F.col('amount').isNull()).first()['tag']=='check'
    assert missing.filter(F.col('amount')>100).count()==1
    assert [r['amount'] for r in orders.orderBy(F.desc('amount')).limit(2).collect()]==[200,120]
    dup=spark.createDataFrame([('u1',120),('u1',120),('u1',80),('u2',200)],'user string, amount long')
    assert dup.distinct().count()==3
    assert dup.dropDuplicates(['user']).count()==2
    tie=spark.createDataFrame([('o2',200),('o1',200),('o3',120)],'order_id string, amount long')
    assert [r.order_id for r in tie.orderBy(F.desc('amount'),F.asc('order_id')).collect()]==['o1','o2','o3']
    report=orders.groupBy('region').agg(F.sum('amount').alias('total'))
    assert report.filter("region='north'").first()['total']==200
    r=missing.groupBy('region').agg(F.count('*').alias('cnt'),F.count('amount').alias('known'),F.avg('amount').alias('avg')).first()
    assert (r.cnt,r.known,r.avg)==(3,2,100.0)
    top=dup.groupBy('user').agg(F.max('amount').alias('mx')).orderBy(F.desc('mx'),F.asc('user')).collect()
    assert [(r.user,r.mx) for r in top]==[('u2',200),('u1',120)]
    print('PASS real PySpark',spark.version,': filtering, NULL, calculated columns, tags, immutable queries, sorting, dedup keys, grouped metrics and per-user maxima')
finally:
    spark.stop()
