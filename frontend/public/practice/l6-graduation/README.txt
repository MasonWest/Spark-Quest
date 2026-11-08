L6 不丢不重的补维汇总（任务 v1）

下载 task.json、starter.py、verify.py、README.txt 到同一练习文件夹，使用已配置且版本兼容的 Python/Java/PySpark 环境。
完成 starter.py，再运行：python verify.py --solution starter.py
不要先打开 reference.py。先写预期与计划，失败后按阶段定位，再逐级看提示。

任务数据由 verify 用明确 Schema 或 Pair RDD 载入；此任务不是 CSV/Parquet 文件读写考核，不依赖通过写 Parquet 来证明执行计划/分区/连接语义。
每次运行新建独立证据目录，包含 validation-result.json、实际计划或分区证据，以及你的 diagnosis 文字。
--output 可以指定一个尚不存在的新证据目录；不会覆盖已有目录。
自动检查 PASS 只表示本任务代码/结果/结构检查通过。diagnosis 的论证质量仍需人工核对，manual_review=required，不提供防作弊或生产性能认证，不更新应用正式成绩、SRS 或解锁。

要求以页面交付约定和 starter 函数契约为准：
L4：正金额的 region/cnt/total，移除控制场景中多余重分布；结果与基线相同，记录相对实际计划。
L5：整数增减均贡献一次，按键求和，保持请求的计算分区数；更换分区数不能改总量。空输入为空结果，不伪造键。
L6：仅正金额事实参与；每条有效事实行贡献一次，不自动按 id 去重。普通等值 LEFT JOIN，NULL 用户键不互配；未匹配或空 region 统一为 unknown。维表非空键重复必须 ValueError，不能任取或放大。

所有合成数据、计划比较和本机计数只用于可复现实作，不代表生产基准。实际 Spark 版本会记录在结果中。Spark 3.5.7 文档是语义参考，本机运行版本另记，不宣称所有版本均已认证。
本任务将小型已知教学结果收集到 Driver 做独立校验，不适用于收集大规模原始数据。
参考只在尝试后对照：python verify.py --solution reference.py
