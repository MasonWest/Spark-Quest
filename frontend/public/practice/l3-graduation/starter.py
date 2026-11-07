"""SQL graduation. Run: python verify.py --solution starter.py
Implement the query in SQL, with an application-local temporary view.
No Spark session should start merely by importing this module.
"""


def read_orders(spark, source):
    """Return all raw CSV rows: order_id string, city string, amount long."""
    raise NotImplementedError("Implement explicit-schema CSV reading")


def build_report(spark, orders):
    """Register orders as a temporary view, then express the report with SQL.
    Exact duplicate input rows count once; positive amounts only; keep cities
    with total >= 200. Output city/cnt/total/total_k; see README for types.
    Must work with different DataFrames and repeated calls in one session.
    """
    raise NotImplementedError("Implement a SQL report without hardcoded answers")


def write_report(report, target):
    """Save Parquet to the disposable target; the same batch may be run twice."""
    raise NotImplementedError("Implement repeatable practice output")
