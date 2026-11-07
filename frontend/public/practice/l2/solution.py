"""L2 reference solution. Uses a fresh output directory for every run.
Place orders.csv beside this script. Run: python solution.py
Does not read the learning application's database.
"""
from pathlib import Path
from tempfile import mkdtemp
from pyspark.sql import SparkSession, functions as F

EXPECTED = {"north": (2, 200, 0.20), "south": (1, 240, 0.24), "east": (1, 90, 0.09)}

def build_report(spark, source):
    orders = (spark.read.option("header", True).option("mode", "FAILFAST")
              .schema("order_id string, region string, amount long").csv(str(source)))
    clean = orders.filter(F.col("amount") > 0)
    report = clean.groupBy("region").agg(F.count("*").alias("cnt"), F.sum("amount").alias("total"))
    return orders, clean, report.withColumn("total_k", F.col("total") / 1000.0)

def validate(saved):
    assert set(saved.columns) == {"region", "cnt", "total", "total_k"}, "Unexpected output columns"
    rows = saved.collect()  # ONLY this known three-row teaching report.
    assert len(rows) == 3, "Expected three regions"
    actual = {r.region: (r.cnt, r.total, r.total_k) for r in rows}
    assert set(actual) == set(EXPECTED), "Unexpected region set"
    for region, (cnt, total, total_k) in EXPECTED.items():
        got = actual[region]
        assert got[:2] == (cnt, total), f"Wrong count or total for {region}: {got}"
        assert got[2] is not None and abs(got[2] - total_k) < 1e-9, f"Wrong thousand-unit total for {region}"
    assert sum(r.total for r in rows) == 530

if __name__ == "__main__":
    base = Path(__file__).resolve().parent
    practice = base / "practice"
    practice.mkdir(exist_ok=True)
    output = Path(mkdtemp(prefix="l2-", dir=practice)) / "report"
    spark = SparkSession.builder.master("local[1]").appName("l2-reference").getOrCreate()
    try:
        orders, clean, final = build_report(spark, base / "orders.csv")
        assert orders.count() == 6
        assert clean.count() == 4
        final.write.mode("error").parquet(str(output))
        saved = spark.read.parquet(str(output))
        validate(saved)
        saved.orderBy(F.desc("total"), F.asc("region")).show()
        print("PASS - result saved to", output)
    finally:
        spark.stop()
