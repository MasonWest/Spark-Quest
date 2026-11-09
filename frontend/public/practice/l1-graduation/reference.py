"""Reference for comparison after an independent attempt."""

def build_counts(sc, lines, partitions):
    return (sc.parallelize(lines, partitions).flatMap(lambda line: line.split())
            .map(lambda word: (word.lower(), 1))
            .reduceByKey(lambda a, b: a+b, numPartitions=partitions))

def diagnosis():
    return 'flatMap 将每行变成词，map 产生键值，reduceByKey 汇合计数。构建链是惰性的，验收中的 take 才触发计算；返回 Driver 的教学结果有界。换分区改变布局，不改变每个词的次数。'
