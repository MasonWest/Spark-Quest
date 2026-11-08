from pyspark.sql import functions as F

def build_enriched_report(orders, dimension):
    duplicate = (dimension.filter(F.col("user_id").isNotNull()).groupBy("user_id")
                 .count().filter(F.col("count") > 1).limit(1).count())
    if duplicate:
        raise ValueError("Duplicate non-NULL dimension key violates the contract")
    o = orders.filter(F.col("amount") > 0).alias("o")
    d = F.broadcast(dimension).alias("d")
    joined = o.join(d,F.col("o.user_id") == F.col("d.user_id"),"left")
    return (joined.select(F.coalesce(F.col("d.region"),F.lit("unknown")).alias("region"), F.col("o.amount").alias("amount"))
            .groupBy("region").agg(F.count("*").alias("cnt"),F.sum("amount").alias("total")))

def diagnosis():
    return "Reject conflicting dimension keys before enrichment, preserve unmatched positive facts as unknown. Broadcast is a candidate for this tiny fixture; verify build-side capacity and actual plan on representative data."
