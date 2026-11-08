from operator import add

def build_totals(sc, rows, partitions):
    return sc.parallelize([tuple(r) for r in rows], partitions).reduceByKey(add, numPartitions=partitions)

def diagnosis():
    return "Integer keyed sum supports local combine and final merge. Partition count changes placement, not totals. Row counts do not measure byte/CPU skew or prove cluster performance."
