"""Independent L2 contract checks. Only imports the explicitly selected local solution.
Outputs use a temporary directory; never touches the learning app or its database.
"""
import argparse
from collections import Counter
import csv
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

SCHEMA = "order_id string, region string, amount long"


def read_fixture(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return [(r["order_id"], r["region"], None if r["amount"] == "" else int(r["amount"]))
                for r in csv.DictReader(handle)]


def expected_report(rows):
    """Python oracle, independent of the learner and the Spark reference pipeline."""
    result = {}
    for _, region, amount in set(rows):
        if amount is not None and amount > 0:
            count, total = result.get(region, (0, 0))
            result[region] = (count + 1, total + amount)
    return result


def check_report(report, rows):
    expected = expected_report(rows)
    columns = ["region", "cnt", "total", "total_k"]
    assert len(report.columns) == 4 and set(report.columns) == set(columns), "Output needs exactly region/cnt/total/total_k"
    types = {f.name: f.dataType.simpleString() for f in report.schema.fields}
    assert types == dict(region="string", cnt="bigint", total="bigint", total_k="double"), f"Wrong output types: {types}"
    actual = report.select(*columns).limit(len(expected) + 1).collect()
    assert len(actual) == len(expected), "Wrong number of regions, or duplicate report rows"
    got = {r.region: r for r in actual}
    assert len(got) == len(actual) and set(got) == set(expected), "Missing, extra or duplicate regions"
    for region, (count, total) in expected.items():
        r = got[region]
        assert r.cnt == count, f"{region}: order count differs; check exact duplicates and validity"
        assert r.total == total, f"{region}: total differs; check grouping, filtering and units"
        assert r.total_k is not None and math.isfinite(r.total_k) and math.isclose(r.total_k, total / 1000, rel_tol=0, abs_tol=1e-9), f"{region}: total_k must be total in yuan / 1000"


def check_input(frame, rows):
    assert len(frame.columns) == 3 and set(frame.columns) == {"order_id", "region", "amount"}, "CSV column names differ"
    types = {f.name: f.dataType.simpleString() for f in frame.schema.fields}
    assert types == dict(order_id="string", region="string", amount="bigint"), f"CSV schema differs: {types}"
    actual = frame.select("order_id", "region", "amount").limit(len(rows) + 1).collect()
    assert Counter(tuple(r) for r in actual) == Counter(rows), "read_orders must retain original rows, NULLs and duplicates"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--solution", default="starter.py")
    parser.add_argument("--query-only", action="store_true", help="Skip file I/O; result is PARTIAL, never PASS")
    parser.add_argument("--result", default="validation-result.json")
    args = parser.parse_args()
    result = {"task": "l2-graduation", "version": 1, "status": "FAIL", "checks": [], "files": "skipped" if args.query_only else "not-run"}
    spark = None
    stage = "load-solution"
    try:
        target = Path(args.solution).resolve()
        spec = importlib.util.spec_from_file_location("l2_student_solution", target)
        if spec is None or spec.loader is None:
            raise ValueError("Cannot load selected solution")
        student = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(student)
        for name in ("read_orders", "build_report", "write_report"):
            assert callable(getattr(student, name, None)), f"Missing function: {name}"
        stage = "spark-environment"
        os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
        from pyspark.sql import SparkSession
        spark = (SparkSession.builder.master("local[1]").appName("l2-graduation-verifier")
                 .config("spark.ui.enabled", "false").config("spark.ui.showConsoleProgress", "false")
                 .config("spark.driver.host", "127.0.0.1").config("spark.driver.bindAddress", "127.0.0.1")
                 .config("spark.sql.shuffle.partitions", "2").getOrCreate())
        spark.sparkContext.setLogLevel("ERROR")
        result["spark_version"] = spark.version
        rows = read_fixture(Path(__file__).with_name("orders.csv"))
        cases = {
            "base-query": rows,
            "changed-values": [("v1", "delta", 13), ("v2", "delta", 27), ("v3", "omega", 40), ("v4", "delta", None)],
            "duplicate-null-new-region": list(reversed(rows + [rows[0], ("extra", "new-region", 75), ("missing", "new-region", None)])),
            "empty-input": [],
            "no-valid-orders": [("z1", "zero", 0), ("z2", "negative", -10), ("z3", "unknown", None)],
        }
        for stage, case in cases.items():
            frame = spark.createDataFrame(case, SCHEMA)
            check_report(student.build_report(frame), case)
            result["checks"].append({"stage": stage, "status": "PASS"})
            print("PASS", stage, flush=True)
        if not args.query_only:
            result["files"] = "running"
            with TemporaryDirectory(prefix="spark-l2-graduation-") as directory:
                directory = Path(directory)
                # The fixture input is separate from all output directories.
                source = directory / "orders.csv"
                with source.open("w", encoding="utf-8", newline="") as handle:
                    writer = csv.writer(handle)
                    writer.writerow(["order_id", "region", "amount"])
                    writer.writerows(rows)
                stage = "read-csv"
                raw = student.read_orders(spark, str(source))
                check_input(raw, rows)
                result["checks"].append({"stage": stage, "status": "PASS"})
                report = student.build_report(raw)
                check_report(report, rows)
                output = directory / "report"
                for stage in ("write-readback", "rerun-same-batch"):
                    student.write_report(report, str(output))
                    check_report(spark.read.parquet(str(output)), rows)
                    result["checks"].append({"stage": stage, "status": "PASS"})
                    print("PASS", stage, flush=True)
            result["files"] = "PASS"
        result["status"] = "PARTIAL" if args.query_only else "PASS"
    except Exception as error:
        message = str(error)
        environmental = any(marker in message for marker in ("NativeIO$Windows", "winutils", "JAVA_GATEWAY_EXITED", "UnsupportedClassVersionError"))
        result["checks"].append({"stage": stage, "status": "ENVIRONMENT_ERROR" if environmental else "FAIL", "error": message[:1600]})
        if result["files"] == "running":
            result["files"] = "ENVIRONMENT_ERROR" if environmental else "FAIL"
        print("NOT PASSED", stage, message[:800], flush=True)
    finally:
        Path(args.result).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(result["status"], "files=" + result["files"], "result=" + str(Path(args.result).resolve()), flush=True)
        if spark is not None:
            spark.stop()
    return 0 if result["status"] in ("PASS", "PARTIAL") else 1


if __name__ == "__main__":
    raise SystemExit(main())
