"""Implement, then run python verify.py --solution starter.py."""
def build_enriched_report(orders, dimension):
    """Return region/cnt/total for positive order rows.
    LEFT equi-join on user_id; unmatched or NULL region -> 'unknown'.
    NULL user keys do not match one another. Reject duplicated non-NULL
    dimension keys with ValueError, including exact duplicate dimension rows.
    Each valid input fact row contributes once; this task doesn't deduplicate facts.
    """
    raise NotImplementedError("Implement safe enrichment")

def diagnosis():
    """Explain cardinality checks, actual plan and limits of performance evidence."""
    return ""
