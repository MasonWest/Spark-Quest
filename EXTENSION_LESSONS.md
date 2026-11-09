# 两课补齐与前后衔接 · 2026-11-09

新增的是正式课程与解锁节点，不是附录链接。总课数68，L1–L7互动63课/290步；课中补救与隔天目标各59个；正式题库1291行。

| 位置 | 新课 | 连续学习路线 |
| --- | --- | --- |
| L3第6课 | 窗口函数：每组Top N与最新整行 | GROUP BY/HAVING → 窗口 → JOIN |
| L7第4课 | 缓存实践：物化、复用与释放 | Executor内存模型 → 缓存生命周期 → Shuffle分区调优 |

每课8步，有标准讲解、逐项反馈、一次换材料补救、一道隔天验证，以及互不相交的5道课末/5道复习题。两课共20道正式题，原有题不替换。学习仍4/5，复习仍5/5。

新题每课的课末与复习两组各自覆盖四个答案位置，避免只在合并题库上看似均匀、单阶段却能猜位置。编写期仅调整了这20道尚无作答的新题位置，事务内再次确认无作答并另存备份；原1271道题及所有历史索引保持。

## 为什么放在这里

窗口课先沿用聚合里的“分组”，对比GROUP BY收拢行与OVER保留明细。之后依次学习每组编号、完整排序、CTE分层过滤、每组至多N行、RANK并列、DENSE_RANK分档和缺失时间。选整行之后再做JOIN，明确记录粒度和连接基数是两层不同的检查。

L2去重课的结尾已指向这节具体练习，GROUP BY末尾、JOIN开头也重写了连接语。窗口内ORDER BY不承诺最终展示有序；PARTITION BY是逻辑组，不承诺物理分布。时间相同必须约定稳定的唯一排序键。窗口聚合例子特意不加ORDER BY，避免把默认帧产生的累计结果误讲成整组总额。

缓存课接住上一课的M/R与逐出模型，再依次选择复用边界、核对DataFrame存储级别、触发物化、观察实际块与缓存扫描、核对复用关系、unpersist、异常清理和公平实验。之后才调分区，保持缓存冷热条件可比，避免同时改多个因素却无法归因。

本课明确采用Spark3.5.7 DataFrame的默认MEMORY_AND_DISK_DESER，分别核对RDD与DataFrame默认值。登记缓存、实际物化、目标查询采用与实测收益互不冒充。unpersist不删除输入或计算定义，也不承诺JVM立刻归还OS内存；finally不会把业务失败变成成功。

参考：[官方窗口语法](https://spark.apache.org/docs/3.5.7/sql-ref-syntax-qry-select-window.html)、[DataFrame持久化](https://spark.apache.org/docs/3.5.7/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.persist.html)、[unpersist](https://spark.apache.org/docs/3.5.7/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.unpersist.html)。

## 进度与升级

- 既有66课的ID、标题、内容、笔记、成绩、SRS、历史作答均保留。只有L3/L7后续十课的order_index按新位置顺延，追加两条新课和20道题。
- 新学习者按新顺序解锁：前置课掌握后开放新课，再开放它后面的课。
- 已掌握的后续课程继续保持掌握；新课不伪造完成。未开始的后续课可能需要先完成新插入的前置节点，这是新课程链的正常行为。已有未通过记录也按现有needs_review规则保留入口。
- 五个衔接课仅改引导，提升独立互动版本；旧本机记录保留，正式掌握不重置。
- 冷启动种子含全部68课；已有库在启动时检查扩展，发现待升级才备份并事务安装。新课不存在时补齐，已完整时不重复插入；异常顺序或新课内容漂移明确拒绝，不静默覆盖。
- 通用正式题安装器只装题；已有库补课程使用 `backend/install_extension_lessons.py`，默认dry-run，`--apply`先备份。升级运行在旧661题播种之前，新课仅播种自己的20题，防止冷库被新题“占坑”导致旧题漏播。

本轮前备份：`backend/spark_quest.db.bak_extensions_before_20261109_151112`。
自动升级备份：`backend/spark_quest.db.bak_course_extensions_20261109_151605_833176`。
已与前备份逐行核对：1271道旧题完整，旧课除order_index外逐字段一致，其余八个表（课程层级与七个学习/徽章相关表）全部不变。

## 验证范围

- 后端22项隔离测试通过，包含两课升级/回滚/幂等、旧ID与笔记保留、解锁链、真实响应Schema、两题池隔离、漂移拒绝、空库重建68课/1291题，保留旧661题。
- 内容护栏与构建、12项互动进度单测、CSS检查通过；全部作者源可重复检查，新增标准讲解与延迟库v6，毕业配置仍v5。
- 新课和五个相邻课的完整互动及讲解关联做浏览器回归；正式测验与复习扩展至63×2页，补救/隔天目标覆盖59项。浏览器使用只读API夹具，不写用户成绩。
- 真实PySpark4.2.0独立检查窗口保留明细、每组Top2、RANK与DENSE_RANK、并列/NULL时间下选整行，并用反例区分全局LIMIT与逐列MAX拼接。
- 缓存实验使用极小三分区输入，观察登记前后实际块、物化、InMemoryTableScan和正确汇总，再模拟报告异常，由finally等待unpersist；释放后仍能重算。没有测试真实磁盘spill，不宣称固定生产加速或所有版本兼容。
- `sync_seed.py`68课/题源零漂移；安装器重复dry-run无待修改。

本轮没有新增整个Level，也没有改七个毕业任务契约。两课独立练习主要由八步新材料与正式题承担；手写代码示例可用下列脚本在实际Spark运行。L2/L3原有Parquet写出环境限制没有据此解决。

```powershell
python frontend/scripts/author-extension-lessons.py --check
python backend/check_extension_examples.py
# backend目录，使用项目虚拟环境
.\.venv\Scripts\python.exe -m unittest test_extension_lessons test_l2_bank test_l3_l6_bank test_l1_l7_bank
.\.venv\Scripts\python.exe install_extension_lessons.py
```

作者源为 `frontend/scripts/extension_lessons.py` 与发布脚本。分章作者在既有递进层后应用相同衔接内容，并保留新课的延迟材料，避免重新生成时丢课或改写答案。修改已安装的新课数据库文本仍需显式迁移，不能仅重新运行作者脚本覆盖用户库。
