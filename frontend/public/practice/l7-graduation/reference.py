"""Reference for comparison after an independent attempt."""

def build_report(orders):
    from pyspark.sql import functions as F
    return (orders.filter(F.col('amount') > 0)
            .withColumn('region', F.coalesce(F.lower(F.trim('region')), F.lit('unknown')))
            .groupBy('region').agg(F.count('*').alias('cnt'), F.sum('amount').alias('total')))

def diagnosis():
    return '基线和候选都只统计正金额；ASCII 空格 trim 后 lower，NULL 归 unknown，空字符串保留。受控计划去掉了 Python UDF 边界，但没有测定生产加速。下一步需同输入同资源重复测量时延、CPU、Shuffle 和结果，并保留基线回退。'
