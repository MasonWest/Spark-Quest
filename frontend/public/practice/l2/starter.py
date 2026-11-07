"""L2 challenge. Put orders.csv beside this file; run python starter.py.
Use the project's chosen Python/Java/PySpark versions. Output is isolated
under a NEW practice directory per run. Never point it at production data.
"""
from pathlib import Path
from pyspark.sql import SparkSession, functions as F

BASE = Path(__file__).resolve().parent
spark = SparkSession.builder.master("local[1]").appName("l2-challenge").getOrCreate()
try:
    # 1. Read orders.csv with an explicit schema: order_id/region string, amount long.
    # 2. Keep only positive amounts. Expected: 4 rows.
    # 3. Group by region; calculate cnt and total.
    # 4. Add total_k from total, preserving total.
    # 5. Write Parquet into a new directory under BASE / "practice".
    # 6. Read it back and check each region, not just the grand total.
    raise NotImplementedError("Replace this line with your own solution")
finally:
    spark.stop()
