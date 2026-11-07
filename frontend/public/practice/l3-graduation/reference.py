"""Compare after trying your implementation. No import-time Spark actions.
Run: python verify.py --solution reference.py
"""


def read_orders(spark, source):
    return (spark.read.option("header", True).option("mode", "FAILFAST")
            .schema("order_id string, city string, amount long").csv(str(source)))


def build_report(spark, orders):
    orders.createOrReplaceTempView("graduation_orders")
    return spark.sql("""
        SELECT city, COUNT(*) AS cnt, SUM(amount) AS total,
               CAST(SUM(amount) AS DOUBLE) / 1000.0 AS total_k
        FROM (SELECT DISTINCT order_id, city, amount FROM graduation_orders) clean
        WHERE amount > 0
        GROUP BY city
        HAVING SUM(amount) >= 200
    """)


def write_report(report, target):
    report.write.mode("overwrite").parquet(str(target))
