"""Small local program checks. No app data, grades, or persistent output files."""
import argparse
import csv
import importlib.util
import os
from pathlib import Path
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--solution", default="starter.py")
    args = parser.parse_args()
    path = Path(args.solution).resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    spec = importlib.util.spec_from_file_location("learner_solution", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
    from pyspark.sql import SparkSession, DataFrame
    spark = (SparkSession.builder.master("local[2]")
             .appName("first-sales-check").config("spark.ui.enabled", "false")
             .config("spark.ui.showConsoleProgress", "false")
             .config("spark.driver.host", "127.0.0.1")
             .config("spark.driver.bindAddress", "127.0.0.1")
             .config("spark.sql.shuffle.partitions", "2").getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    cases = [
        ([("east", 4), ("east", 9), ("west", 2)], {"east": 13, "west": 2}),
        ([("north", 3), ("north", 3), ("south", 0)], {"north": 6, "south": 0}),
        ([], {}),
        ([("west", 1), ("north", 2), ("west", 5), ("east", 7)], {"west": 6, "north": 2, "east": 7}),
    ]
    try:
        with tempfile.TemporaryDirectory(prefix="spark-first-check-") as folder:
            for index, (rows, expected) in enumerate(cases):
                sample = Path(folder) / (str(index) + ".csv")
                with sample.open("w", encoding="utf-8", newline="") as stream:
                    writer = csv.writer(stream)
                    writer.writerow(["region", "amount"])
                    writer.writerows(rows)
                result = module.summarize(spark, sample.as_uri())
                assert isinstance(result, DataFrame), "Return a DataFrame"
                assert set(result.columns) == {"region", "sum(amount)"}, "Check output columns"
                records = result.collect()  # only these tiny verification fixtures
                actual = {r["region"]: r["sum(amount)"] for r in records}
                assert len(records) == len(actual), "Duplicate output region"
                assert actual == expected, "Case %s: expected %r, got %r" % (index, expected, actual)
                print("PASS case", index + 1, flush=True)
        print("PASS four small fixtures; not a production benchmark or automatic course grade", flush=True)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
