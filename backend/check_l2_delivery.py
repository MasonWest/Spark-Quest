"""Check capstone assets and local Spark read/transform/write semantics.
Only creates a fresh temporary directory; never opens the learning DB.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import importlib.util
import os
import sys
os.environ.setdefault('PYSPARK_PYTHON',sys.executable)
from pyspark.sql import SparkSession, functions as F

parser=argparse.ArgumentParser()
parser.add_argument('--query-only',action='store_true',help='Validate input and report only; explicitly skip filesystem write checks')
args=parser.parse_args()
base=Path(__file__).resolve().parents[1]/'frontend/public/practice/l2'
spec=importlib.util.spec_from_file_location('capstone',base/'solution.py')
capstone=importlib.util.module_from_spec(spec);spec.loader.exec_module(capstone)
spark=(SparkSession.builder.master('local[1]').appName('l2-delivery-check')
 .config('spark.ui.enabled','false').config('spark.ui.showConsoleProgress','false')
 .config('spark.driver.host','127.0.0.1').config('spark.driver.bindAddress','127.0.0.1')
 .config('spark.sql.shuffle.partitions','2').getOrCreate())
spark.sparkContext.setLogLevel('ERROR')
try:
 orders,clean,final=capstone.build_report(spark,base/'orders.csv')
 assert orders.count()==6
 assert clean.count()==4
 capstone.validate(final)
 assert [r.region for r in final.orderBy(F.desc('total'),F.asc('region')).collect()]==['south','north','east']
 # A three-row report with the right grand total but wrong per-region count must fail.
 broken=final.withColumn('cnt',F.when(F.col('region')=='north',F.lit(1)).otherwise(F.col('cnt')))
 try:
  capstone.validate(broken)
 except AssertionError:
  pass
 else:
  raise AssertionError('Validation missed wrong regional count')
 print('PASS real PySpark',spark.version,'CSV read, clean, grouped report, per-region validation, wrong-count rejection',flush=True)
 if args.query_only:
  print('SKIP Parquet write/read and mode checks (--query-only)',flush=True)
  sys.exit(0)
 with TemporaryDirectory(prefix='l2-delivery-') as folder:
  path=str(Path(folder)/'report')
  final.write.parquet(path)
  capstone.validate(spark.read.parquet(path))
  try:
   final.write.parquet(path)
  except Exception as error:
   assert 'PATH_ALREADY_EXISTS' in str(error) or 'already exists' in str(error).lower(),str(error)
  else:
   raise AssertionError('Default mode did not reject existing path')
  final.write.mode('ignore').parquet(path)
  assert spark.read.parquet(path).count()==3
  final.write.mode('append').parquet(path)
  assert spark.read.parquet(path).count()==6
  final.write.mode('overwrite').parquet(path)
  capstone.validate(spark.read.parquet(path))
  print('PASS isolated Parquet roundtrip, default error, ignore, append duplicates, overwrite',flush=True)
finally:
 spark.stop()
