独立实作：从文本得到可靠词频

实现 build_counts(sc, lines, partitions)，返回 Pair RDD；每个词一行整数次数，输出分区数采用传入参数。
按 Python str.split() 的空白规则拆词，再 lower()；标点保留，所以 word 与 word, 是不同的词。每次出现都计数，不对原文或词去重。
空行、纯空白行不生成空词；空输入返回空键集合。不可写死词、次数或结果行数。
验收使用新词、大小写、制表空白、标点和空输入，在 2/4 分区下分别核对独立预期。
不要先将整个 RDD collect 到 Driver 再统计；diagnosis() 说明转换、动作、分区和有界回收的区别，代码策略及论证质量需人工复核。

运行：python verify.py --solution starter.py
需 Python、Java 与 PySpark。所有测试为小型本地教学数据，不访问应用数据库。
验收自动创建新的 practice/evidence-* 目录；--output 只接受尚不存在的新目录。
PASS 仅指自动检查，诊断质量始终 manual_review=required。失败时查看 validation-result.json 的具体阶段；环境失败不等于知识错误。
本任务不写 Parquet，也不替代 L2/L3 的真实文件验收。
