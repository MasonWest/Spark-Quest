"""Execute L3 lesson examples with Spark, independently of UI answer lookup.
Also reject flawed graduation reports. No learning DB or file writes.
"""
from pathlib import Path
import importlib.util
import os
import sys
os.environ.setdefault('PYSPARK_PYTHON', sys.executable)
from pyspark.sql import SparkSession, functions as F

kit = Path(__file__).resolve().parents[1] / 'public/practice/l3-graduation'
def load(name):
    spec = importlib.util.spec_from_file_location('l3_' + name, kit / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
verify, reference = load('verify'), load('reference')
spark = (SparkSession.builder.master('local[1]').appName('l3-course-check')
         .config('spark.ui.enabled', 'false').config('spark.ui.showConsoleProgress', 'false')
         .config('spark.driver.host', '127.0.0.1').config('spark.driver.bindAddress', '127.0.0.1')
         .config('spark.sql.shuffle.partitions', '2').getOrCreate())
spark.sparkContext.setLogLevel('ERROR')
def sql(text):
    return spark.sql(text).collect()
def rejected(name, frame, rows):
    try:
        verify.check_report(frame, rows)
    except AssertionError:
        print('PASS rejects', name, flush=True)
    else:
        raise AssertionError('Accepted ' + name)
try:
    # SELECT -> DataFrame; view registration/rebinding; application-local global view.
    orders = spark.createDataFrame([(80,), (150,)], 'amount long')
    orders.createOrReplaceTempView('orders')
    result = spark.sql('SELECT amount FROM orders WHERE amount > 100')
    assert result.withColumn('amount_k', F.col('amount')/1000.0).first().amount_k == .15
    assert result.collect() == orders.filter(F.col('amount') > 100).select('amount').collect()
    df = spark.createDataFrame([(10,)], 'amount long');df.createOrReplaceTempView('v')
    df = spark.createDataFrame([(99,)], 'amount long')
    assert sql('SELECT amount FROM v')[0].amount == 10
    df.createOrReplaceTempView('v');assert sql('SELECT amount FROM v')[0].amount == 99
    df.createOrReplaceGlobalTempView('qa_l3_shared')
    other = spark.newSession()
    assert other.sql('SELECT amount FROM global_temp.qa_l3_shared').first().amount == 99
    assert not other.catalog.tableExists('v')
    # A DDL command is issued without a follow-up action on its returned DataFrame.
    spark.sql('CREATE OR REPLACE TEMP VIEW qa_l3_command AS SELECT 7 AS n')
    assert sql('SELECT n FROM qa_l3_command')[0].n == 7
    print('PASS SQL/API bridge, view target/rebinding/session scope, DDL command', flush=True)

    assert tuple(sql("SELECT 120 AS amount, 'amount' AS label")[0]) == (120, 'amount')
    assert sql('SELECT CAST(120 AS DOUBLE)/1000.0 AS amount_k')[0].amount_k == .12
    special = spark.createDataFrame([(120,)], ['order amount']);special.createOrReplaceTempView('special')
    assert sql('SELECT `order amount` AS amount FROM special')[0].amount == 120
    spark.createDataFrame([('north',10),('north',20),('south',10)], 'city string, amount long').createOrReplaceTempView('distinct_rows')
    assert {r.city for r in sql('SELECT DISTINCT city FROM distinct_rows')} == {'north','south'}
    spark.createDataFrame([('A','north',40),('B','south',200),('C','north',150)], 'id string, city string, amount long').createOrReplaceTempView('condition_rows')
    assert [r.id for r in sql("SELECT id FROM condition_rows WHERE city='north' AND amount>100")] == ['C']
    spark.createDataFrame([(None,),('',),('123',)], 'phone string').createOrReplaceTempView('people')
    assert sql('SELECT * FROM people WHERE phone = NULL') == []
    assert [r.phone for r in sql('SELECT * FROM people WHERE phone IS NULL')] == [None]
    assert sql('SELECT CAST(NULL AS STRING) = NULL AS unknown')[0].unknown is None
    spark.createDataFrame([('A',200),('B',200),('C',300)], 'id string, amount long').createOrReplaceTempView('ranking')
    assert [r.id for r in sql('SELECT id FROM ranking ORDER BY amount DESC,id ASC LIMIT 2')] == ['C','A']
    print('PASS SELECT literals/identifiers/alias/distinct, WHERE/NULL, deterministic Top N', flush=True)

    spark.createDataFrame([('A',70),('A',60),('B',120)], 'city string, amount long').createOrReplaceTempView('group_rows')
    assert {tuple(r) for r in sql('SELECT city,SUM(amount) AS total FROM group_rows GROUP BY city HAVING SUM(amount)>100')} == {('A',130),('B',120)}
    spark.createDataFrame([(10,),(None,),(20,)], 'amount long').createOrReplaceTempView('count_rows')
    assert tuple(sql('SELECT COUNT(*),COUNT(amount) FROM count_rows')[0]) == (3,2)
    spark.createDataFrame([('Z',None),('Z',None)], 'city string, amount long').createOrReplaceTempView('null_group')
    assert sql('SELECT SUM(amount) AS total FROM null_group')[0].total is None
    assert sql('SELECT city,SUM(amount) FROM null_group GROUP BY city HAVING SUM(amount)>0') == []
    print('PASS WHERE versus HAVING, COUNT objects, all-NULL SUM/HAVING', flush=True)

    spark.createDataFrame([('o1','u1'),('o2','u9')], 'id string, user_id string').createOrReplaceTempView('join_orders')
    spark.createDataFrame([('u1','Ana')], 'user_id string, name string').createOrReplaceTempView('join_users')
    assert [tuple(r) for r in sql('SELECT o.id,u.name FROM join_orders o JOIN join_users u ON o.user_id=u.user_id')] == [('o1','Ana')]
    spark.createDataFrame([(7,),(7,)], 'k long').createOrReplaceTempView('left_rows')
    spark.createDataFrame([(7,),(7,),(7,)], 'k long').createOrReplaceTempView('right_rows')
    assert sql('SELECT COUNT(*) AS n FROM left_rows l JOIN right_rows r ON l.k=r.k')[0].n == 6
    assert sql("SELECT CAST('7' AS INT)=7 AS matched")[0].matched
    print('PASS INNER unmatched rows, join multiplicity, explicit key conversion', flush=True)

    assert sql("SELECT UPPER(TRIM(' ana ')) AS name")[0].name == 'ANA'
    spark.createDataFrame([(None,),('',),('Ana',)], 'name string').createOrReplaceTempView('names')
    assert [r.name for r in sql("SELECT COALESCE(name,'unknown') AS name FROM names")] == ['unknown','','Ana']
    spark.createDataFrame([(None,),(50,),(150,)], 'amount long').createOrReplaceTempView('tags')
    assert [r.tag for r in sql("SELECT CASE WHEN amount IS NULL THEN '待核对' WHEN amount>100 THEN '高额' ELSE '普通' END AS tag FROM tags")] == ['待核对','普通','高额']
    def label_score(s):
        return 'missing' if s is None else ('high' if s>90 else 'low')
    spark.udf.register('qa_l3_label_score', label_score, 'string')
    assert tuple(sql('SELECT qa_l3_label_score(CAST(NULL AS INT)), qa_l3_label_score(95), qa_l3_label_score(80)')[0]) == ('missing','high','low')
    print('PASS builtins, COALESCE empty string/NULL, CASE, registered null-safe Python UDF', flush=True)

    rows = verify.read_fixture(kit / 'orders.csv')
    assert verify.expected_report(rows) == {'north':(2,250),'south':(1,250),'delta':(1,200)}
    good = reference.build_report(spark, spark.createDataFrame(rows,verify.SCHEMA)).cache()
    verify.check_report(good,rows)
    no_dedup = spark.sql('SELECT city,COUNT(*) AS cnt,SUM(amount) AS total,CAST(SUM(amount) AS DOUBLE)/1000.0 AS total_k FROM graduation_orders WHERE amount>0 GROUP BY city HAVING SUM(amount)>=200')
    rejected('missing DISTINCT', no_dedup, rows)
    boundary = good.filter(F.col('total') > 200)
    rejected('strict > instead of >= threshold', boundary, rows)
    moved = good.withColumn('total', F.when(F.col('city')=='north',200).when(F.col('city')=='delta',250).otherwise(F.col('total'))).withColumn('total_k',F.col('total')/1000.0)
    assert moved.agg(F.sum('total')).first()[0] == 700
    rejected('correct grand total but wrong city allocation', moved, rows)
    rejected('wrong units', good.withColumn('total_k',F.col('total').cast('double')), rows)
    rejected('wrong types', good.withColumn('cnt',F.col('cnt').cast('double')), rows)
    rejected('duplicate report', good.union(good), rows)
    print('PASS L3 semantic examples and 6 negative graduation checks on Spark', spark.version, 'file writes not tested here', flush=True)
finally:
    spark.stop()
