"""L2 graduation. Implement the three functions, then run:
python verify.py --solution starter.py
Only use isolated practice data; this module must not start Spark on import.
"""


def read_orders(spark, source):
    """Return the raw CSV DataFrame with order_id/region string and amount long.
    Keep all input rows here. source is a local CSV path.
    """
    raise NotImplementedError("Implement CSV reading with an explicit schema")


def build_report(orders):
    """Return region, cnt, total, total_k following the task contract.
    The verifier will also pass in-memory DataFrames with different values.
    Do not hardcode regions, totals or the number of output rows.
    """
    raise NotImplementedError("Implement cleaning, exact deduplication and reporting")


def write_report(report, target):
    """Save Parquet to target. Re-running the same batch must not duplicate rows.
    The verifier supplies a disposable path; never point this at production data.
    """
    raise NotImplementedError("Implement a repeatable write to the practice target")
