L3 SQL 独立毕业任务（版本 1）

下载 orders.csv、starter.py、verify.py、README.txt 到同一练习目录。
在与你的 Spark 发行版兼容的 Python/Java/PySpark 环境实现 starter.py 中三个函数，然后运行：
python verify.py --solution starter.py

交付约定
- read_orders(spark, source)：显式读取 order_id string、city string、amount long，保留全部原始行，空金额为 NULL。
- build_report(spark, orders)：注册当前 DataFrame 的临时视图，用 SQL 表达主体处理：完全相同的输入行只计一次，仅保留正金额，按 city 聚合，合计至少 200 元的城市才输出。相同订单号的冲突版本不在本任务范围。
- 输出 city string、cnt long（有效笔数）、total long（元）、total_k double（千元）。不要求目录中的存储顺序；若预览排名，按 total 降序、city 升序。
- write_report(report, target)：写 Parquet，同批次重跑到同一隔离目标后不得重复追加。只能使用练习目录，不能指向生产数据。
- 不写死城市、金额、结果数量；每次调用都应注册本次传入的 DataFrame，不能依赖前一次视图内容。
- 本任务不强迫使用 JOIN 或 UDF：单表需求不应为了覆盖语法而凭空增加业务步骤。

先推导：哪些行重复、哪些行无效？“至少 200”与“超过 200”有什么区别？先写自己的预期，再执行脚本。
验收器用 Python 标准库独立推导结果，不调用 reference 产生答案；会使用新金额、新城市、额外重复、空值、199/200 阈值边界、空输入和全无效输入。它检查真实 Spark 输出与文件交付，不审核你是否确实用 SQL 写出了主体逻辑；不是防作弊认证。

默认命令包括 CSV 读取、Parquet 写出/读回、同批次重跑，全部通过才输出 PASS / files=PASS。
python verify.py --solution starter.py --query-only 只检查查询，输出 PARTIAL / files=skipped，不等于毕业通过。
validation-result.json 保存在当前目录，可用 --result 指定新路径。它不接入应用的正式成绩、解锁、SRS 或连续天数。

环境说明
Windows 缺少 Hadoop 本地文件系统支持时可能出现 NativeIO$Windows.access0/winutils 错误。项目开发机存在这个限制，查询通过不能当成完整文件验证通过。需在支持文件读写的 Spark 环境运行默认命令，不要改用 Python 文件操作冒充 Parquet 写出。
Spark、Python、Java 的兼容组合请按所用 Spark 发行版的官方安装说明配置，未宣称已支持所有版本。

对照前先保存自己的实现与失败记录。确需对照时再下载 reference.py，执行：
python verify.py --solution reference.py
看过参考后可再用新输入独立实现，熟悉答案的重跑不是新的独立能力证明。
