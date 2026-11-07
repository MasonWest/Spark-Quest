L2 独立实作：交付可重跑的地区日报（任务版本 1）

先自己推导，再写代码；参考实现不是入口。
下载 orders.csv、starter.py、verify.py、README.txt 到同一个练习目录。
已有 Python、Java 和 PySpark 环境时，先执行 python -c "import pyspark; print(pyspark.__version__)" 检查包，再实现 starter.py。
验收命令：python verify.py --solution starter.py

交付约定
1. CSV 原始结构：order_id string、region string、amount long（整数元）。空金额读为 NULL，先保留全部输入行。
2. 同一批次可能重复导入完全相同的行，完全相同行只计一次。本任务没有同一订单号对应不同内容的冲突，不需要选最新版本。
3. 只有 amount 严格大于 0 的订单有效；未知、零、负值不参与日报。
4. 每个有有效订单的地区一行：region string、cnt long（有效订单数）、total long（元）、total_k double（千元）。不要求文件存储顺序。
5. 写为 Parquet 数据目录；同一批输入重复写到同一练习目标后，读回结果不能翻倍。
6. 不允许把地区名称、预期金额或输出行数写死；验收会改变数据。所有操作仅针对一次性练习目录。

先给自己留三个答案：哪些行应该排除，哪些行是重复导入，两个总额相同的地区分别应该是什么结果？
不要先打开 reference.py。验收失败后，先看阶段名与错误原因，修正代码再运行。

验收会做什么
- Python 标准库单独推导期望值，不从参考实现调用答案。
- 查询阶段直接构造 DataFrame，覆盖原始数据、重复/空值/新地区扰动、空结果、只有无效金额的数据；检查列名、类型、逐地区笔数/金额/千元值。
- 文件阶段实际读取 CSV，核对未清洗的输入、写 Parquet、读回，以及同批重跑。所有输出都在临时目录，结束后清理。
- 结果写到 validation-result.json，包含各阶段状态。它不更新学习应用的正式成绩或解锁，也不是防作弊证书。

遇到环境问题
需要使用与你安装的 Spark 版本兼容的 Python 和 Java。Windows 还可能缺少 Hadoop 本地文件系统支持；如果出现 NativeIO$Windows/access0 或 winutils 相关错误，属于文件阶段环境问题，不能算写出通过。
可先运行 python verify.py --solution starter.py --query-only 验证查询逻辑。此模式明确输出 PARTIAL / files=skipped，不等于完整毕业验收。完整通过仍需在支持文件读写的 Spark 环境运行默认命令。
当前项目开发机已知存在 Windows 原生文件系统限制；不要通过改成 Python 写文件来冒充 Spark Parquet 验收。
本任务未声明已验证所有 Python/Java/Spark 版本兼容；安装环境请按你所用 Spark 发行版的官方说明配置。

需要对照时再下载 reference.py，运行同一验收命令：
python verify.py --solution reference.py
看过参考实现后也可以换一份数据重新写；再次运行熟悉的答案不应当作独立能力证明。
