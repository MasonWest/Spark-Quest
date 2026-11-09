独立实作：证明一次有边界的优化

实现 build_report(orders)，只统计 amount>0，输出 region string、cnt long、total long，每地区一行。
地区仅去掉两端 ASCII 空格再转小写；NULL 变 unknown，空字符串仍是空字符串。制表符不属于这里约定的 trim 字符。
不得硬编码地区或总额，不把明细 collect 到 Python。用等价的 Spark 内置表达式替换基线普通 Python UDF。
验收独立核对新地区、NULL、空串、空格、无效金额、空输入；保存当前 Spark 版本和实际前后计划，候选不能保留 Python UDF 边界。
task.json 的症状为合成教学设定。实际运行只证明本数据结果与计划结构，不自动证明提速、容量安全、AQE 收益或生产可用。
diagnosis() 写出假设、保持的语义、现有证据、下一轮测量和回退。文字与调优决策需要人工复核。

运行：python verify.py --solution starter.py
需 Python、Java 与 PySpark。所有测试为小型本地教学数据，不访问应用数据库。
验收自动创建新的 practice/evidence-* 目录；--output 只接受尚不存在的新目录。
PASS 仅指自动检查，诊断质量始终 manual_review=required。失败时查看 validation-result.json 的具体阶段；环境失败不等于知识错误。
本任务不写 Parquet，也不替代 L2/L3 的真实文件验收。
