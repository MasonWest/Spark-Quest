"""Read after an independent attempt; works with new CSV inputs too."""

def summarize(spark, csv_path):
    df = (spark.read.option("header", True)
          .schema("region string, amount long").csv(csv_path))
    return df.groupBy("region").sum("amount")


from pyspark.sql import SparkSession


def main():
    import sys
    spark = (SparkSession.builder.master("local[2]")
             .appName("first-sales").getOrCreate())
    try:
        summarize(spark, sys.argv[1] if len(sys.argv) > 1 else "sales.csv").show()
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
