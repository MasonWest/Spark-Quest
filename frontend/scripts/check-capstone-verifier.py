"""Real Spark negative checks: the graduation verifier must reject plausible mistakes."""
from pathlib import Path
import importlib.util
import os
import sys
os.environ.setdefault('PYSPARK_PYTHON', sys.executable)
from pyspark.sql import SparkSession, functions as F

kit = Path(__file__).resolve().parents[1] / 'public/practice/l2-graduation'
def load(name):
    spec = importlib.util.spec_from_file_location(name, kit / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
verify, reference = load('verify'), load('reference')
rows = verify.read_fixture(kit / 'orders.csv')
assert verify.expected_report(rows) == {'north': (2, 200), 'south': (2, 350), 'west': (1, 150), 'island': (1, 200)}
spark = (SparkSession.builder.master('local[1]').appName('capstone-negative-checks')
         .config('spark.ui.enabled', 'false').config('spark.ui.showConsoleProgress', 'false')
         .config('spark.driver.host', '127.0.0.1').config('spark.driver.bindAddress', '127.0.0.1')
         .config('spark.sql.shuffle.partitions', '2').getOrCreate())
spark.sparkContext.setLogLevel('ERROR')
def rejected(label, action):
    try:
        action()
    except AssertionError:
        print('PASS rejects', label, flush=True)
    else:
        raise AssertionError('Verifier accepted ' + label)
try:
    frame = spark.createDataFrame(rows, verify.SCHEMA)
    good = reference.build_report(frame).cache()
    verify.check_report(good, rows)
    verify.check_input(frame, rows)
    no_dedup = (frame.filter(F.col('amount') > 0).groupBy('region')
                .agg(F.count('*').alias('cnt'), F.sum('amount').alias('total'))
                .withColumn('total_k', F.col('total') / 1000.0))
    rejected('missing deduplication', lambda: verify.check_report(no_dedup, rows))
    moved = good.withColumn('total', F.when(F.col('region') == 'north', 100)
                            .when(F.col('region') == 'west', 250).otherwise(F.col('total')))
    moved = moved.withColumn('total_k', F.col('total') / 1000.0)
    assert moved.agg(F.sum('total')).first()[0] == 900
    rejected('correct grand total but wrong regions', lambda: verify.check_report(moved, rows))
    rejected('wrong units', lambda: verify.check_report(good.withColumn('total_k', F.col('total').cast('double')), rows))
    rejected('duplicate output rows', lambda: verify.check_report(good.union(good), rows))
    rejected('wrong field types', lambda: verify.check_report(good.withColumn('cnt', F.col('cnt').cast('double')), rows))
    rejected('hardcoded old output for changed input', lambda: verify.check_report(good, [('different', 'new', 7)]))
    rejected('reader silently cleaned the input', lambda: verify.check_input(frame.dropDuplicates(), rows))
    print('PASS independent oracle and 7 negative checks on Spark', spark.version, flush=True)
finally:
    spark.stop()
