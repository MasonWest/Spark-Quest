L2 章末本地挑战

1. 将 orders.csv、starter.py 下载到同一文件夹。使用你已配置的 Python/Java/PySpark 环境运行。
2. 编辑 starter.py 完成读取、清洗、聚合、新增 total_k、写出及读回验证。
3. 有效订单：amount > 0；不要用 append 重复写同一批完整结果。
4. 预期按 total 降序：south cnt=1 total=240 total_k=0.24；north cnt=2 total=200 total_k=0.20；east cnt=1 total=90 total_k=0.09。合计 530。
5. 先自己写，再下载 solution.py 对照。参考实现每次创建新的 practice/l2-* 目录，不覆盖历史输出；互动练习中的 overwrite 演示只针对指定练习目录。
6. Parquet 目录可包含多个文件；读回后重新排序展示。参考脚本只对已知三行小报表 collect，不适用于海量明细。
7. Windows 真实文件写出还依赖可用的 Hadoop 本地文件系统支持。浏览器不会代你执行脚本；本地运行不会自动更新应用的学习进度。
