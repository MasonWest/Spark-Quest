"""Complete summarize; keep the provided runner and cleanup."""

def summarize(spark, csv_path):
    # CSV header: region,amount; schema: region string, amount long.
    # Return a DataFrame with columns region and sum(amount), one row per region.
    raise NotImplementedError("Read the CSV and compute each region's amount sum")


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
