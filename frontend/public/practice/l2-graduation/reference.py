"""Reference implementation. Try starter.py first; compare after running checks.
Run: python verify.py --solution reference.py
No Spark session or filesystem write is started merely by importing this module.
"""
from pyspark.sql import functions as F


def read_orders(spark, source):
    return (spark.read.option("header", True).option("mode", "FAILFAST")
            .schema("order_id string, region string, amount long").csv(str(source)))


def build_report(orders):
    clean = orders.dropDuplicates().filter(F.col("amount") > 0)
    return (clean.groupBy("region")
            .agg(F.count("*").alias("cnt"), F.sum("amount").alias("total"))
            .withColumn("total_k", F.col("total") / 1000.0))


def write_report(report, target):
    report.write.mode("overwrite").parquet(str(target))
