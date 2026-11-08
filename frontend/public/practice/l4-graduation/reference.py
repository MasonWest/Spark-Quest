from pyspark.sql import functions as F

def build_report(orders):
    return (orders.filter(F.col("amount") > 0).select("region", "amount")
            .groupBy("region").agg(F.count("*").alias("cnt"),F.sum("amount").alias("total")))

def diagnosis():
    return "Remove unnecessary round-robin repartition; preserve grouped results. Plan comparison is not a production speed guarantee; test representative load and metrics next."
