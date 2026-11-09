# 概念递进修补 · 2026-11-09

本轮解决“有互动，但首次术语过快、跨章缺台阶”的问题。课程仍66课，L1–L7仍61课；修订26课，新增14个主步骤，总计274步。课中补救与隔天目标各57个。数据库、正式题库及评分规则没有修改。

## 具体补了哪些台阶

| 位置 | 修补 |
| --- | --- |
| L1 RDD 初识 | 先画出元素与分区，再看parallelize；在第一次map、缓存、血缘出现时解释用途 |
| L1 动作与惰性 | 解释闭包、副作用和幂等，而不是只用它们描述限制 |
| L1 通向DataFrame | 说明优化器做什么，Catalyst先认职责，规则留给L4 |
| L1 词频 | 两道新增题先建立(词,1)键值卡片，再按键合并；解释为什么不是去重 |
| L3与L6 JOIN入口 | 都先展示事件表和属性表，定义事实、维度、连接键；L6再画重复匹配的输入表 |
| L4入口与读计划 | 先认Scan/Filter/Aggregate的动作；Exchange、广播、AQE先交代最低理解层次，标明后续深入章节；区分Job/Stage/Task与代码生成编号 |
| L5 | 将计算分份接回L1、数据交接接回L4；JOIN题先重述事件与属性角色 |
| L6连接策略 | 新增哈希查找与广播路线题，定义构建侧/探测侧；加盐先讲拆键、配套匹配和还原 |
| 各章首尾 | 明确前面已学的模型、本章增加哪一层、下一章会接什么，不要求提前精通以后才解释的算法 |

L1–L7当前步数分别为29、41、39、39、39、41、46。原260步全部保留，其相对顺序、题干、代码、答案字段/选项ID和知识目标不变；主要扩展题前语境和标准讲解。26课增加独立版本，新版本机互动记录独立开始，旧记录不删除，正式掌握状态不重置。原56道延迟材料逐项不变，仅增加一项内存回收材料。

## 执行内存与存储内存

之前的L7第三课 `l7-executor-memory` 只有进程定位、共享规则的一句提醒和缓存成本核算，不能算已经系统教过动态借用。本轮在现有课中补齐，从4步扩为10步：

1. 定位Driver结果收集问题。
2. 区分JVM、Python进程和其他开销。
3. 区分Execution工作状态与Storage缓存用途。
4. 用M=100、R=50推演空闲共享，解释R不固定切半。
5. 缓存80、空闲20时执行要40，推演回收20后的状态。
6. 执行需求继续变大时，计算保护线限制，认识spill和容量边界。
7. 反过来缓存不能逐出执行已用空间，R也不是随时能强占的配额。
8. 明确fraction画M、storageFraction画R；用2300MiB堆内示例算1200/600。
9. 回到真实诊断，区分回收、spill、缓存级别与进程口径。
10. 把复用次数、预热和读取成本一起纳入缓存选择。

配套新增一次换数字补救与一道隔天验证。以Spark3.5.7常规堆内统一内存模型为参考，缓存保护仅针对执行回收这一机制；主动unpersist、进程丢失、缓存块粒度、任务公平分配和堆外/Python预算另论。没有把简化容量图宣传为某个Task的精确运行配额。

参考：[3.5.7调优说明](https://spark.apache.org/docs/3.5.7/tuning.html#memory-management-overview)、[内存配置](https://spark.apache.org/docs/3.5.7/configuration.html#memory-management)、[固定版本UnifiedMemoryManager实现](https://github.com/apache/spark/blob/v3.5.7/core/src/main/scala/org/apache/spark/memory/UnifiedMemoryManager.scala)。

## 验证范围

- 内容护栏、构建、CSS检查和12项进度/延迟单测通过；作者源与输出可重复比对。
- 全61课/274步浏览器检查通过；26课标准讲解、历史原文、跳转与手机布局检查通过。57补救与57延迟目标回归通过，最后的内存措辞补充又单独复跑该课。
- 代码卡片在真实PySpark4.2.0验证了中间Pair RDD形状、reduceByKey结果和空白输入。容量题与参数题按独立计算核对，隔天题另算新数字。
- 直接实例化实际运行版本的UnifiedMemoryManager，以100/50容量验证：没有缓存时执行可获80；此时新增40缓存申请失败，执行占用仍为80。此实验未放入真实缓存块，不认证其他容量图中的实际逐出过程，不制造OOM或性能结果。
- 浏览器使用只读API夹具，不向用户学习数据库提交分数。正式题库未改，因此没有重复安装或改写已答题的答案语义。
- 本次未改七个毕业工具包；上一轮L2/L3的Windows Parquet限制仍然存在。

## 是否需要再加课

这次动态借用属于既有内存课的内容缺口，放回原课能维持前后关系，暂不新增章节。课程总量不是判断覆盖完整度的依据。

后续值得安排的两个具体补充点：

- **缓存生命周期的实际操作**：cache/persist如何选择、存储级别、物化、Storage页核对与unpersist。目前有模型判断，完整独立操作训练仍不足；可作为L7缓存实践短课，而不是新增整个Level。
- **窗口与每组Top N/保留最新整行**：L2去重讲解提到需要完整排序规则的窗口，但当前互动主线没有窗口专项训练。这是实用扩展优先项，适合接在L3聚合之后另编一课，不能把“提到过”算作“教会了”。

checkpoint、复杂GC/堆外参数和流处理等可留作后续进阶模块，本轮没有为了名词覆盖将它们塞进基础主线。正式五题组对新增细分内存规则的覆盖没有同步扩大，本轮主要依靠课中推演、变式和隔天验证；后续题库改版应继续采用备份后追加与历史ID兼容策略。

## 维护入口

`frontend/scripts/concept_progression.py` 是显式修补层，三个分章作者源在输出前共同调用它，避免下次生成丢失修补。L2原有手工内容由同一层更新。新增内容时应先维护作者源，按发布规则增加版本，审查后再记录摘要。

```powershell
python frontend/scripts/concept_progression.py --check
python frontend/scripts/author-l1-l7-content.py --check
python frontend/scripts/author-l3-content.py --check
python frontend/scripts/author-l4-l6-content.py --check
python frontend/scripts/check-concept-examples.py --model-only
python frontend/scripts/check-concept-examples.py
```

真实Spark与版本语义的边界、诊断仍需人工复核和实际学习效果仍待观察，均继续保留。以上是已落实的递进修补，不代表完整Spark知识体系已全部覆盖。
