"""Implement, then run python verify.py --solution starter.py."""
def build_totals(sc, rows, partitions):
    """Return a Pair RDD (key, integer total), with requested output partitions.
    All input quantities, including negative/zero adjustments, contribute once.
    Empty input returns an empty RDD; do not hardcode keys or totals.
    """
    raise NotImplementedError("Implement distributed keyed totals")

def diagnosis():
    """Explain local combine, partition invariance and remaining load limits."""
    return ""
