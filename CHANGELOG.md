# Changelog — Spark Quest

## 2026-11-09 · L1打磨与L6/L7选项修复

- L1六课新增5处课中填写，重写60道测验/复习材料并关联教学步骤。
- L6/L7十九课修复主要选项线索，内存正式题增加共享、回收与保护阈值推演。
- 新题追加、旧ID和学习历史保留，新版互动记录独立。标准讲解v8。
- 32项后端、15项前端、25课浏览器与小型真实Spark验证通过；详见QUESTION_POLISH_RESULTS.md。

> 本文件回答：**系统是怎么一步步变成现在这样的？**
> 当前事实以同目录 `CURRENT_STATE.md` 为准；本文件只记录演进历史。
>
> 规则：每完成一个阶段，追加一个 `## YYYY-MM-DD` 段落，分 `Added / Changed / Fixed / Architecture` 小节。
> 后续增量更新只追加新条目，不要改写历史条目。
>
> **版本发布规则（轻量，2026-09-16 立）：阶段性验收完成 → commit → push → tag。**
> 只在**阶段验收通过**时打 annotated tag `vN.N`；**不给每个小改动打 tag**，小改动照常 commit + push 就行。
> 已发布 tag：`v1.2`（Spark Quest 首个稳定 UI + 工程规范基线）。一览用 `git tag -l`。

---

## 2026-08-28 — V1.0 基线（当前版本起点）

本条目汇总自项目启动至 2026-08-28 的全部累计演进，作为第一份正式基线。
后续每次完成一个阶段，单独追加新日期条目即可。

### Added
- **项目骨架**：React 18 + Vite 5 + TypeScript 前端；FastAPI + Uvicorn + SQLAlchemy + SQLite 后端；端口 6001（前端）/ 9000（后端）
- **Phase 1 课程地图**：`course_levels` / `lessons` 表 + `/map` 页面
- **Phase 2 Dashboard / 今日任务**：`/api/dashboard` + 推荐首课 + 进度条
- **Phase 3 Lesson 学习页**：`/lesson/:id`；七要素 `content`（explanation / examples / key_points / common_mistakes / review / problem / preview）
- **Phase 4 Lesson Mastery Quiz**：`quizzes` 表 + `lesson_mastery` 表；每课随机抽 5 题；掌握标准 ≥80% → `mastered`
- **Phase 5 统一派生学习状态**：`locked / available / mastered / needs_review` 由 `services.py` 统一计算，Dashboard / Map / Lesson 三处一致
- **Phase 6.1 Quiz Bank 扩充**：每课 10 题（共 210 题），`quizzes.dimension` 开放维度标签，`_sample_quiz_questions` 优先维度多样抽 5 题
- **Phase 6.2 Level 2 题库**：Level 2（DataFrame 核心，10 课）每课补齐至 10 题
- **课程内容**：Level 0（5 课）+ Level 1（6 课）+ Level 2（10 课）共 21 课，含【心智模型】+ ⚠️ 比喻边界
- **Lesson Notes**：`lesson_notes` 表 + `GET/POST/DELETE /api/lessons/{id}/notes`，append-only，前端 Lesson 页接入（草稿/保存/删除/时间显示）

### Changed
- 课程解锁规则：仅第一关第一课 `available`，其余前驱 `mastered` 才 `available`（Phase 5 前均为占位 `locked`）
- Mastery 状态改为纯派生（不再硬编码于 Lesson 行）
- 抽题逻辑：固定 4 题 → 题库 10 题随机抽 5 题、优先维度多样
- 概念解释排版增强：`RichText` 组件支持小节标题（`【】`）/ 行内 `code` / `**加粗**` / `⚠️` 警示块 / 有序·无序列表

### Fixed
- `RichText` 中 `·` 列举在「单换行混排」场景下的渲染修复（2026-08-28）
- 历史 bug：LessonOut 缺 `order_index`（地图 NaN）、`index.css` 颜色覆盖、后端 `attempts None+1`、uvicorn 陈旧字节码等（详见 `CURRENT_STATE.md` 关键约定与坑位）

### Architecture
- **学习状态模型冻结**：Dashboard / Course Map / Lesson 共用 `services.py` 派生逻辑，杜绝三套状态互不一致
- **不新增 learning state、不新增 progress 字段、不新增冗余表**；能派生的状态绝不存储
- 单用户本地应用：无登录鉴权、无用户系统
- 明确不引入：Alembic / Redis / Docker / AI
- 课程内容数据化：文本存于 `lessons.content`（JSON 文本列），React 端零硬编码课程文本

---

## 2026-08-28 — Level 3：Spark SQL（V1.0 基线之后增量）

V1.0 基线建立后，按用户确认的新路线图落地 Level 3（9 课），设计上严格不抢跑 L4–L7。

### Added
- **Level 3：Spark SQL**（9 课，order_index=3）：`l3-what-is-spark-sql` / `l3-temp-views` / `l3-select-basics` / `l3-where-order-limit` / `l3-groupby-having` / `l3-joins-intro` / `l3-functions-and-udf` / `l3-tables-and-formats` / `l3-comprehensive`
- 每课 10 题，共 90 题，全 `single_choice` + 开放 `dimension`（concept/why/mechanism/apply/comparison/debug）+ `explanation`
- 每课 explanation 含 v1.0 五固定小节（【先用人话理解】/【一个直观的心智模型】/⚠️ 比喻的边界（很重要）：/【正式的技术定义】/【写下代码后，Spark 内部发生了什么】）
- 课程总量升至 30 课（L0 5 + L1 6 + L2 10 + L3 9），题库 300 题

### Changed
- 课程结构：新增 Level 3 节点；JOIN 仅做轻量 INNER 入门，深类型/broadcast/调优显式留给 Level 6；UDF 点出"慢"作为 Level 7 伏笔；明确不接 Hive Metastore
- 种子机制：`seed_level3.py` 将 JSON 合并与 DB upsert 合二为一（此前 Level 2 用 `seed_level2.py` + `expand_quizzes_to_10.py` 分体），仍保持幂等且不动 L0–L2 与 lesson_mastery 进度

### Fixed
- l3-comprehensive 的 explanation 原本缺 3 个 v1.0 固定小节（含"先人话理解"笔误），已补回五小节并同步 DB / JSON / 源脚本
- 心智模型案例库 slug 不一致：`l2-sort-dedup-limit` / `l2-inspect-data` 校正为种子实际 slug `l2-sort-dedup` / `l2-inspect`

### Architecture
- 延续"不抢跑"原则：SQL 与 DataFrame API 共享同一 Catalyst 优化大脑，每课尽量与 Level 2 等价操作配对，避免重复造概念
- 复用 v1.0 道具表（Catalyst=同一套优化大脑；临时视图=仓库门口临时工牌），新隐喻登记入案例库

---

## 2026-08-28 — Level 4：执行计划（V1.0 基线之后增量）

V1.0 基线 + Level 3 之后，按设计稿 `Spark_Quest_Level4_执行计划_设计.md` 落地 Level 4（9 课），只教「怎么看懂 Spark 怎么算」，不抢跑 L5–L7 调优。

### Added
- **Level 4：执行计划**（9 课，order_index=4）：`l4-why-explain` / `l4-logical-vs-physical` / `l4-explain-api` / `l4-read-plan` / `l4-catalyst-rules` / `l4-wholestage-codegen` / `l4-dependency-narrow-wide` / `l4-job-stage-task` / `l4-comprehensive`
- 每课 10 题，共 90 题，全 `single_choice` + 开放 `dimension`（concept/why/mechanism/apply/comparison + 部分 debug）+ `explanation`
- 每课 explanation 含 v1.0 五固定小节（【先用人话理解】/【一个直观的心智模型】/⚠️ 比喻的边界（很重要）：/【正式的技术定义】/【写下代码后，Spark 内部发生了什么】）
- 课程总量升至 39 课（L0 5 + L1 6 + L2 10 + L3 9 + L4 9），题库 390 题
- 新脚本 `backend/seed_level4.py`（一次性幂等 upsert，JSON 合并 + DB upsert 一体，沿用 `seed_level3.py` 模式）

### Changed
- 课程结构：新增 Level 4 节点；红线不展开 Shuffle/分区调优（L5）、JOIN 策略（L6）、Tungsten 内存细节（L7）；综合练习只验收「读得懂」，不要求调优
- 案例库：全局道具表补 4 行（设计师概念图 vs 施工图 / Stage / WholeStageCodegen / Job→Stage→Task），新增「## 5. Spark 执行计划（Level 4）」章节，原使用约定/待升级章节顺延为 ## 6 / ## 7

### Fixed
- 落库前修正了两处 Quiz JSON 结构笔误（options 内误植 correct_index/explanation），已通过语法 + 数据合规校验（每课 10 题、七要素、五小节、correct_index∈[0,3]、dimension 覆盖五类）

### Architecture
- 延续「不抢跑」原则：复用 Catalyst=优化大脑、Shuffle=空中飞货、Driver=前台、Executor=工人 等已登记道具，避免重造概念
- 复用 v1.0 道具表，Level 4 新隐喻（概念图/施工图、Stage、WholeStageCodegen、Job→Stage→Task）登记入案例库

---

## 2026-08-28 — Level 5：分区与 Shuffle（V1.0 基线之后增量）

V1.0 基线 + Level 3 + Level 4 之后，按设计稿 `Spark_Quest_Level5_执行计划_设计.md` 落地 Level 5（9 课），只教「数据怎么被切分、又在什么情况下被搬来搬去（Shuffle）及其代价」，不抢跑 L6–L7 调优。

### Added
- **Level 5：分区与 Shuffle**（9 课，order_index=5）：`l5-what-is-partition` / `l5-partition-count-parallelism` / `l5-what-is-shuffle` / `l5-shuffle-cost` / `l5-narrow-wide-partition` / `l5-shuffle-trigger-operators` / `l5-reducebykey-vs-groupbykey` / `l5-repartition-coalesce` / `l5-comprehensive`
- 每课 10 题，共 90 题，全 `single_choice` + 开放 `dimension`（concept/why/mechanism/apply/comparison）+ `explanation`
- 每课 explanation 含 v1.0 五固定小节（【先用人话理解】/【一个直观的心智模型】/⚠️ 比喻的边界（很重要）：/【正式的技术定义】/【写下代码后，Spark 内部发生了什么】；综合练习亦含五小节）
- 课程总量升至 48 课（L0 5 + L1 6 + L2 10 + L3 9 + L4 9 + L5 9），题库 480 题
- 新脚本 `backend/seed_level5.py`（一次性幂等 upsert，JSON 合并 + DB upsert 一体，沿用 `seed_level4.py` 模式）

### Changed
- 课程结构：新增 Level 5 节点；红线不展开 JOIN 策略深类型（L6）、Tungsten 内存细节（L7）、具体调优参数/最优分区数（L7）；综合练习只验收「读得懂」，不要求调优
- 案例库：全局道具表补 5 行（托盘/货盘、工人数量上限=托盘数、装箱→装车→卸货分拣、车间本地先捆小包再空运、推倒重排 vs 就地并拢），新增「## 6. Spark 分区与 Shuffle（Level 5）」章节，原使用约定/待升级章节顺延为 ## 7 / ## 8

### Fixed
- 收尾核验按 `Spark_Quest_新增Level_收尾核验踩坑.md` §5 参数化脚本（ORDER_INDEX=5, PREFIX="l5-"）跑通：连真库 `backend/spark_quest.db`（非 `app/sparkquest.db`）、`quizzes` 用 `lesson_id` 关联、聚合结构、`content` 用实现态七键——全绿；lesson_mastery 进度未动（18）

### Architecture
- 延续「不抢跑」原则：复用 Catalyst=优化大脑、Shuffle=空中飞货、Driver=前台、Executor=工人、Stage=不跨车间工序段、Job→Stage→Task 等已登记道具；把 L4 窄/宽依赖定义延展到分区物化层面
- 复用 v1.0 道具表，Level 5 新隐喻（托盘/货盘、装箱→装车→卸货分拣、本地先捆包再空运、推倒重排 vs 就地并拢）登记入案例库

---

## 2026-08-29 — Level 6：JOIN 深类型与 Broadcast（V1.0 基线之后增量）

按设计稿 `Spark_Quest_Level6_执行计划_设计.md` 落地 Level 6（9 课），把 L3「JOIN 必 Shuffle、深类型留 L6」、L4 的 `BroadcastHashJoin`/`SortMergeJoin` 计划标记、L5「Shuffle 代价 / 空中飞货」全部延展到 JOIN 策略层面。

### Added
- **Level 6：JOIN 深类型与 Broadcast**（9 课，order_index=6）：`l6-what-is-join` / `l6-join-strategies-overview` / `l6-broadcast-hash-join` / `l6-sort-merge-join` / `l6-shuffle-hash-join` / `l6-how-spark-chooses` / `l6-broadcast-hint-and-control` / `l6-join-data-skew` / `l6-comprehensive`
- 每课 10 题，共 90 题，全 `single_choice` + `dimension` 五类（concept/why/mechanism/apply/comparison）各 2 题 + `explanation`；`correct_index` 在四个选项位上均匀打散（避免学员按位置猜答案）
- 每课 explanation 含 v1.0 五固定小节（含综合练习课 `l6-comprehensive`），examples 三件套、common_mistakes 三件套齐全
- 课程总量升至 57 课（L0 5 + L1 6 + L2 10 + L3 9 + L4 9 + L5 9 + L6 9），题库 570 题
- 新脚本 `backend/seed_level6.py`（复制 `seed_level5.py` 模式，一次性幂等 upsert）

### Changed
- 课程结构：新增 Level 6 节点；`CURRENT_STATE.md` 总体状态表 Phase 8 行改为「Level 2/3/4/5/6 已落地；Level 7 规划中」，数据量 6→7 levels / 48→57 lessons / 480→570 quizzes
- 案例库：全局道具表补 5 行（小册子复印 N 份=BHJ、两本按 key 排序的电话簿逐页对照=SMJ、抽屉柜流式查=SHJ、Catalyst 看两桌人数决定拼法=策略自动选择、某把椅子挤满 90% 的人=数据倾斜），新增「## 7. Spark JOIN 深类型（Level 6）」章节，原使用约定/待升级章节顺延为 ## 8 / ## 9

### RedLines（未抢跑 L7）
- 不展开 Tungsten 内存管理 / 堆外 / 编码字节级细节
- 不展开 shuffle 分区数最优值与深调优参数；广播阈值只讲概念（不给数值与调优）
- skew 只到「识别 + 原理级应对」（salting 加盐 / 隔离大 key / BHJ 绕过），不写 `skewJoin` 类开关
- 不重复 L3 INNER 语法、L4 explain 读法、L5 Shuffle 定义与代价

### Fixed
- 收尾核验按 `Spark_Quest_新增Level_收尾核验踩坑.md` §5 参数化脚本（ORDER_INDEX=6, PREFIX="l6-"）跑通：连真库 `backend/spark_quest.db`、`quizzes` 用 `lesson_id` 关联、`quiz_seed.json` 聚合结构、`content` 用实现态七键——全绿；`lesson_mastery` 总数未变（18）、新 Level 引用 = 0；L0–L5 课数未变
- 落库前备份 `spark_quest.db` / `course_seed.json` / `quiz_seed.json`（`*.bak_before_l6`）

### Architecture
- 延续「不抢跑」原则：复用 Catalyst=优化大脑、Shuffle=空中飞货、Driver=前台、Executor=工人、JOIN=两拨货按 key 拼桌、托盘=分区、Stage=不跨车间工序段等已登记道具
- 心智模型严格复用案例库已登记道具，L6 新增 5 个隐喻全部登记入案例库

---

## 2026-08-29 — Level 7：性能调优（V1.0 基线之后增量 · Phase 8 课程主线收官）

按设计稿 `Spark_Quest_Level7_执行计划_设计.md` 落地 Level 7（9 课），把 L3 埋下的 UDF 慢、L4 的 Tungsten/WholeStageCodegen 内存细节、L5 的 shuffle 分区数与 spill、L6 的广播阈值与 skew 深调优全部收口到一套调优方法论。**至此 Phase 8 课程主线（Level 0–7）全部完成。**

### Added
- **Level 7：性能调优**（9 课，order_index=7）：`l7-what-is-tuning` / `l7-tungsten-encoding` / `l7-executor-memory` / `l7-shuffle-partitions` / `l7-broadcast-threshold` / `l7-aqe` / `l7-skew-tuning` / `l7-read-less-data` / `l7-comprehensive`
- 每课 10 题，共 90 题，全 `single_choice` + `dimension` 五类（concept/why/mechanism/apply/comparison）各 2 题 + `explanation`；`correct_index` 在四个选项位上均匀打散
- 每课 explanation 含 v1.0 五固定小节（含综合练习课 `l7-comprehensive`），examples 三件套、common_mistakes 三件套齐全
- 课程总量升至 66 课（L0 5 + L1 6 + L2 10 + L3 9 + L4 9 + L5 9 + L6 9 + L7 9），题库 660 题
- 新脚本 `backend/seed_level7.py`（复制 `seed_level6.py` 模式，一次性幂等 upsert）

### Changed
- 课程结构：新增 Level 7 节点；`CURRENT_STATE.md` 总体状态表 Phase 8 行改为「Level 2/3/4/5/6/7 已全部落地——课程主线完成」，数据量 7→8 levels / 57→66 lessons / 570→660 quizzes
- 案例库：全局道具表补 7 行（木桶/最慢工序、真空压缩袋、货车车厢四格、车道数与车流、秤的刻度、会实时改路的导航、交警堵点分流），新增「## 8. 性能调优（Level 7）」章节，原使用约定/待升级章节顺延为 ## 9 / ## 10

### RedLines（不越界）
- 不讲集群资源调度层（YARN/K8s 队列、动态资源分配），不展开 GC 调优
- 不给万能最优参数值：所有旋钮只给「起点思路 + 取舍 + 实测收敛」
- 不重复 L4 explain 读法、L5 Shuffle 定义与代价、L6 JOIN 策略框架
- 不引入外部监控体系（只讲 Spark UI 与 explain）

### Fixed
- 收尾核验按 `Spark_Quest_新增Level_收尾核验踩坑.md` §5 参数化脚本（ORDER_INDEX=7, PREFIX="l7-"）跑通：连真库 `backend/spark_quest.db`、`quizzes` 用 `lesson_id` 关联、`quiz_seed.json` 聚合结构、`content` 用实现态七键——全绿；`lesson_mastery` 总数未变（18）、新 Level 引用 = 0；L0–L6 课数未变（5/6/10/9/9/9/9）
- 题库首版答案位置又一次全挤在 B（同 L6 首版），已按「base 序列 + 课序偏移」重排为每课 2/3/2/3 分布
- 程序化改写 quiz 块时再次出现括号问题（`questions": [[` 重复开括号），已修正并 `py_compile` 复验——**该坑已第二次出现，见项目记忆**
- 落库前备份 `spark_quest.db` / `course_seed.json` / `quiz_seed.json`（`*.bak_before_l7`）

### Architecture
- 延续「不抢跑 / 不越界」原则：L7 只收口前面各 Level 明确留下的伏笔，不引入集群运维与 JVM 调优话题
- 心智模型严格复用案例库已有道具，L7 新增 7 个隐喻全部登记入案例库

---

## 2026-08-29 — Phase 6b：Lesson 级间隔复习闭环（V1.0 基线之后增量）

在 Phase 6.1/6.2 建成题库与维度标签之后，落地真正的间隔复习。范围由用户明确划定并严格执行，未做任何扩大。

### Added
- **复习调度内核**（`services.py`）：`REVIEW_INTERVALS_DAYS = [1, 3, 7, 14, 30, 60, 120]`、`REVIEW_FAIL_INTERVAL_DAYS = 3`、`REVIEW_QUESTION_COUNT = 5`；`is_due_for_review / due_lesson_ids / due_reviews / init_review_schedule / advance_review_schedule / defer_review_schedule`
- **三个接口**（`routers/review.py`）：`GET /api/review/due`、`GET /api/review/{lesson_id}`（抽 5 题、不泄露答案）、`POST /api/review/{lesson_id}/submit`（5/5 判过 + 重新调度）
- **复习页** `/review/:id`（`ReviewPage.tsx` + CSS）：第 n/5 题进度、5/5 闸门、通过态显示「下次复习 N 天后」、失败态提供「重新阅读本课」与「直接再挑战一次」
- **Dashboard「🔁 今日复习」区块**（Home.tsx）：列出到期课程 + Level + 逾期天数
- **课程地图「待复习」角标**（MapPage.tsx）：mastered 课到期时显示 🔁，图例同步补项
- **学习页复习入口**（LessonPage.tsx）：mastered 课加「间隔复习（5 题）」；`?from=review` 时顶部显示「先重读一遍，再挑战复习」提示条 + 「再次复习」
- **验收脚本** `backend/_p6b_e2e_check.py`：37 项端到端断言，跑在 DB 临时副本上，不污染真库
- **弱维度优先抽题**：复用 Phase 6.1 的 `_sample_quiz_questions`，新增可选 `priority_dims`（上一轮答错题目所属 dimension 优先访问），仅排序偏好，不建权重模型

### Changed
- `lesson_mastery` 扩展 5 列：`first_mastered_at / srs_stage / next_review_at / last_review_at / review_count`（幂等迁移 + 存量回填 18 条）
- `GET /api/dashboard` 新增 `reviews_due`；`GET /api/levels` 的 lesson 新增 `due_for_review`（纯视觉提示，非第 5 种状态）
- `submit_quiz` 在「首次转 mastered」时写入 `first_mastered_at` 等复习锚点（后续重测不再移动锚点）
- 共用样式 `.btn-ghost` 由 `QuizPage.css` 上提到 `index.css`（现 Quiz / Lesson / Review 三处使用）

### Fixed
- 无 bug 修复（本阶段为纯新增）。已规避的坑：`srs_stage` 不可由 `next_review_at` 反推（失败与「通过 stage0」的间隔都是 3 天，会撞车），必须独立存储；`first_mastered_at` 与 `last_quiz_at` 语义分离，不混用

### Architecture
- **不新增任何表**：复习调度信息全部落在既有 `lesson_mastery`；原规划的 `review_items` 表不建，`review_attempts` 历史日志不做
- **不新增第 5 种学习状态**：`locked / available / needs_review / mastered` 四状态体系原封不动，复习是 `mastered` 之上的附加调度信息；`due_for_review` 只是布尔提示
- **失败不降级**：复习失败只插入一次 3 天后的短期巩固，`srs_stage` 保持不变
- **「立即重做」与「下一次调度」解耦**：失败后 `next_review_at` 推到 3 天后，但取题接口只看是否 mastered，用户读完本课可立即再挑战
- **复习不污染学习态**：`/api/review/.../submit` 绝不改动 `status / score / attempts / last_quiz_at`，5 题复习得分不覆盖 10 题学习测验得分
- 明确不做：SM-2 / Anki 式 SRS、个性化遗忘曲线拟合、单题级 SRS、每 dimension 独立进度、复杂统计、连错智能教学、AI 动态出题

---

## 2026-08-29 — 题库质量修复：Level 0/1 干扰项重构 + 答案位置洗牌

用户复习 Level 0 时发现「所有题目答案都是 A，且最长的选项就是答案」。经全库诊断确认属实，且为系统性缺陷。**本轮按用户指定范围，只修复 Level 0 / Level 1（110 题），其余关卡未触碰。**

### Added
- 无新增功能

### Changed
- **干扰项重写**：Level 0/1 共 330 个干扰项全部重写。旧干扰项是随手编的短废话（如 `q62` 的「因为 Python 太慢 / 硬盘太大 / 网络太快」），新干扰项针对每道题的真实常见误解撰写，且长度与正确项相当
- **答案位置洗牌**：对 110 题做确定性置换，`A/B/C/D` 分布由 `A=75 / B=29 / C=4 / D=2` 变为 `A=28 / B=28 / C=27 / D=27`
- **seed 与 DB 同步更新**：`backend/app/quiz_seed.json` 与 `spark_quest.db` 同时改写，避免下次 re-seed 把缺陷带回来（已校验两者完全一致）

### Fixed
- **位置偏置**：Level 0/1 答案落在 A 的比例由 **74%** 降至 **25.5%**
- **「最长即答案」**：正确项是唯一最长选项的比例由 **92%** 降至 **30.0%**；同时反向指标「正确项唯一最短」控制在 **10.9%**，避免形成新的可预测规律
- 修复前已验证 0/110 题的解析引用选项字母或位置（此前全库扫描到的 9 条「第 N 个」全是误报：CSV 第一行、排查第一步、第一视角），故洗牌不会让任何解析失效
- `weak_points` 存的是 `question_id` 而非选项下标，洗牌不污染 P6b 任何已有复习数据

### Architecture
- **只改内容，不改逻辑**：四状态体系、复习调度、判分阈值（学习 80% / 复习 5/5）均未改动
- **严格限定范围**：Level 2–7 的 550 题保持原样（其 A 占比 48.7%、最长即答案 88.4% 的旧特征被保留，作为「未修复关卡」的对照基线）
- 回归验证：110 题按 DB 正确答案提交全部通过；抽样 15 题提交错误答案均不被判满分；P6b 复习闭环（取题 / 5-5 通过 / 4-5 失败 / 失败后立即可重做）全部复测通过
- 改动前自动备份：`spark_quest.db.*.bak_before_l01_fix`、`app/quiz_seed.json.*.bak_before_l01_fix`（已被 `.gitignore` 排除，不入库）

---

## 2026-09-04 — 修复：答题页与结果页题目顺序不一致

### Fixed
- **结果页顺序错位**（用户报障）：`POST /api/lessons/{id}/quiz/submit` 遍历的是**按 `order_index` 排序的全库题目**，而 `GET /api/lessons/{id}/quiz` 返回的是**随机抽样并打乱顺序**的 5 题。前端结果页直接按后端 `results` 顺序渲染，导致「做题时看到的第 3 题」与「结果页列出的第 3 题」不是同一题。
  - 修复：改为按 `payload.answers`（= 前端呈现顺序）遍历构造 `results`，结果列表与呈现顺序严格一致。
- **间隔复习同源缺陷**：`POST /api/review/{id}/submit` 存在完全相同的遍历顺序问题，一并修复。
- **重复 `question_id` 未收敛**：重复提交同一题时 `total` 按提交条数计、但 `results` 去重渲染，分数与题数不符。现统一在计数前折叠重复（`last wins`）。
- **空提交除零**：`answers: []` 时 `correct / total` 触发 `ZeroDivisionError` → 500。现返回 422 `Empty submission: no answers provided`。

### Architecture
- 判分语义不变：仍以 `selected_index == correct_index` 为准，阈值不变（学习 ≥80%、复习 5/5），`weak_points` 仍存 `question_id`
- 复习提交的数量校验改为在**去重后**执行：`[A,A,B,C,D]` 现返回 422「需提交 5 道不同的题，本次收到 4 道」，避免 4 题作答被按 5 题计分而误判失败
- 只改后端两个路由（`app/routers/quizzes.py`、`app/routers/review.py`），前端 `QuizPage.tsx` / `ReviewPage.tsx` 无需改动（其提交顺序本就与呈现顺序一致）
- 回归验证：乱序提交 → 结果顺序 == 提交顺序；重复 id → `total` 收敛为 5；空提交 / 非法 id → 422；Quiz 与 Review 两链路抽题顺序与结果顺序逐一比对一致
- 验证过程产生的脏数据已还原：`lesson_id=1` 的 `lesson_mastery` 整行回滚至测试前快照（score 100、attempts 2、SRS 排期不变），全库 `mastery` 24 行、无非 `mastered` 残留
- 改动前自动备份：`spark_quest.db.bak_before_quizfix`

---

## 2026-09-07 — v1.1 Product Experience Polish：Course Map 重做

### Added
- **Course Map 全新视觉**：从「课程长列表」改为**区域化垂直旅程地图**（region-based vertical journey），单条蜿蜒路径 + 节点沿路径排布，可垂直滚动
- **5 态节点 + 6 态视觉**：
  - `mastered` 实心绿 + 白勾；`due_for_review` 在 mastered 之上叠加紫色外环（不新增状态，纯装饰）
  - `needs_review` 琥珀实心 + 白色叹号
  - `available`（全图唯一焦点）放大 1.32 倍 + 蓝色呼吸光环 + 浮动「开始」气泡
  - `locked` 灰虚线圈 + 锁图标，标题仍可见（预告前方）
- **完成感三层叠加**：
  1. 节点层（实心 + 勾）
  2. **路径层**（核心载体）：已掌握节点之间的道路从灰虚线变亮实线 ——「走过的路被点亮」
  3. 区域层（整区通关 → 绿色 + 插旗 + 已通关印章）
- **三档时间叙事**（`regionTone()` 纯函数派生 from `Level.status`）：
  - `past`（已通关）— `saturate(.65) brightness(1.06) contrast(.92)` + `scale(.985)`，徽章「已通关 · N/N」+ 旗帜
  - `present`（进行中）— 全饱和 + 蓝色描边 + 高光阴影，徽章「进行中 · N/N」
  - `future`（未解锁）— 节点 z-index 高于 ::after 蒙层，徽章「未解锁 · N 课」+ 锁
- **顶部区域导航胶囊**：8 个胶囊，当前高亮（蓝色），已通关用绿字，未解锁灰；点击跳转并展开 —— 直接回答 UX Audit Q1「我现在在哪里」
- **地图/列表视图切换**（无障碍兜底）：右上角 toggle，状态持久化到 `localStorage: sq_map_view`，列表视图为同一份数据的语义化 `<ol>` 呈现
- **首次进入自动滚动**到焦点节点（`scrollIntoView`），用户不用自己找「学到哪了」
- **氛围层**：`MapBackdrop.tsx`（纯装饰）— sticky 远景山 + 渐变天空 + 漂浮云，`z-index: 0`，**不接收任何 props，不知道课程/状态/进度的存在**。删掉它整个结构仍可读。

### Changed
- `pages/MapPage.tsx` **完全重写**：取数 / 折叠状态 / 自动定位 / 视图切换 / 区域导航 / 列表视图
- `pages/MapPage.css` **删除**（174 行旧样式全部废弃，CSS 现统一在 `components/map/map.css`）
- `types.ts`：`Level.status` 由 `string` 收窄为联合类型 `LevelStatus = 'completed' | 'in_progress' | 'available' | 'locked'`（仅前端类型收窄，后端 schema 未动）
- 地图页副标题由「Spark 学习路线：从环境搭建到 RDD 基础」改为数据驱动的「N 个区域 · M 课 · 已完成 K 课」

### Fixed
- **`currentLessonId` 抢占焦点 bug**：旧代码把 `needs_review` 也算进 current 焦点，导致琥珀节点被错误地套上 current 蓝色大圆 + 光环（needs_review 不该抢「下一步」的视觉焦点）。改为**只 `available` 才是 current**，needs_review 单独显示
- **节点标题重叠**：L1 RDD 基础（6 课）的 stepY=86 导致 5/6 课两行标题与下一节点 orb 重叠。改为 `stepY=96`，所有 9 课区域都安全

### Architecture
- **`components/map/mapLayout.ts` 纯函数布局算法**（v1.1 硬约束兑现点）：
  - `layoutRegion(count, opts)` 输入只有课程数，输出 `MapNode[]`，加课自动延长、零硬编码
  - 水平偏移用**预设偏移表循环** `[0, 58, 78, 58, 0, -58, -78, -58]`（不是 `sin()`，确定性、可单测）
  - `regionHeight(count)`、`segmentPath(a, b)`（S 曲线三次贝塞尔）、`regionTone(level)` 全部纯函数
  - **零新增依赖**（不引动画库/UI 库），仅用 CSS `@keyframes` + `prefers-reduced-motion` 关闭
- **新增文件清单**：
  - `components/map/mapLayout.ts`（纯函数）
  - `components/map/LessonNode.tsx`（5 态节点）
  - `components/map/LessonPath.tsx`（SVG 分段道路）
  - `components/map/JourneyRegion.tsx`（Level 区域）
  - `components/map/RegionNav.tsx`（顶部导航）
  - `components/map/MapBackdrop.tsx`（氛围层）
  - `components/map/map.css`（统一样式）
- **约束兑现：禁用全部氛围层与滤镜后结构 100% 可读**（已脚本验证）

### 验收
- `tsc -b && vite build` 零错误
- DOM 节点数 === 66（全展开地图视图）；列表 `<li>` 数 === 66
- 真实数据下 5 态全部出现（mastered:30 / locked:35 / current:1 / due:12；临时插入 needs_review 验证琥珀节点后还原）
- `mapLayout(11)` 返回 11 个坐标（数据驱动断言：`layoutRegion` 数量 === 输入）
- 375px 窄屏无横向溢出（节点最左 108 / 最右 298，视口 0..375）
- 31 个 `<a.lesson-node>`（可点）+ 35 个 `<div.lesson-node>`（locked 不可点）= 66
- 实机截图见 `E:\MMMason\Spark_dlg\ux_audit\v11-*.png`

---

## 2026-09-07 — v1.1.1 Product Experience Polish（地图交互修复 + 复习入口合并）

v1.1 Course Map 重做上线后，用户实机走查反馈三处地图交互问题，并发现已掌握课底部复习入口存在产品语义重复。均属 v1.1 范围内的打磨，不引入新功能、不碰后端。

### Fixed（地图交互，Round A）
- **展开/收起任意 Level 不再自动滚动到焦点节点**：`pages/MapPage.tsx` 原 `useEffect` 依赖 `expanded`，每次 toggle 都触发 `scrollIntoView`；改为 `useRef` 守卫，仅首次进入地图时滚动一次，切列表↔地图不重滚。
- **Level 介绍在收起/展开都能看全**：
  - 收起态 `components/map/map.css` 的 `.region-summary` 去掉 `-webkit-line-clamp:2` 截断，长介绍完整显示；
  - 展开态路径上方新增 `.region-intro` 浅蓝左边框卡片，长介绍不再丢失。
- **`due_for_review` 渲染确认**：设计为「绿勾 + 紫色外环」（`map.css` `.is-due .node-orb::before`），非黄色问号；用户确认紫环已存在，未改动。

### Changed（复习入口合并，Round B）
- 经代码核查确认：`复习测验`（`/lesson/{id}/quiz`）与 `间隔复习`（`/review/{id}`）出题逻辑完全相同——同一 `quizzes` 10 题库、同一采样函数 `_sample_quiz_questions(questions, n=5)`、同 n=5；review 仅多「上次错题维度优先」弱偏好（`priority_dims`，读 `weak_points`），非逐题遗忘曲线。
- **合并已掌握课底部入口**：`pages/LessonPage.tsx` mastered 分支删「复习测验」链接，仅留「下一课」（btn-primary）+「间隔复习（5 题）」（btn-ghost → `/review/{id}`）；available/needs_review 分支不变。
- **复习结果页显示本次得分**：`pages/ReviewPage.tsx` 结果 banner 加「本次复习得分 X%」+「仅本次反馈，不写回本课掌握得分」提示；后端 `submit_review` 本就不改 `score/attempts`，与约定一致，无需改。

### 验收
- `tsc -b && vite build` 零错误
- 地图：展开区 2 个 `.region-intro`、收起区 6 个 `.region-summary`；toggle 时 scrollY 0→0→0（不跳）
- 复习：已掌握课 CTA 仅剩「下一课 / 间隔复习（5 题）」；结果页 `🎉 复习通过 | 5/5 · 本次复习得分 100% | 不写回提示`

### 备注（教训已记入项目记忆）
- 本轮验证脚本跑完整 5/5 复习时真实推进了 lesson 1 的 SRS（违反「写库前先快照」约定，无真快照，已用 Python 还原为估算值）；核查全库仅 lesson 1 被碰且已还原，其余 29 行完好。单用户本地库影响可忽略，但规矩不能破。

---

## 2026-09-07 — Phase 9.1：🔥 Streak 连续学习

Phase 8 课程主线（Level 0–7）与 Phase 6b 复习闭环建成后，游戏化第一阶段落地 Streak。产品意义上的第三阶段：**Content（把学习内容系统化）→ Learning/Retention Loop（把学习过程闭环）→ Streak（把学习行为持续化）**。

### Added
- **新表 `study_days`**（一天一行，`UNIQUE(user_id, study_date)`）：`user_id / study_date / activity_count / lessons_done / reviews_done / first_at / last_at`
  - `user_id` 为未来用户系统预留，当前恒为 `DEFAULT_USER_ID = "local"`（无鉴权单用户本地应用）
  - 必须建表的原因：`lesson_mastery.last_quiz_at` 是每课**最后一次**提交时间，重做旧课会让更早的学习日从记录中消失，历史会回溯性损坏
- **Streak 内核**（`services.py`）：`LOCAL_UTC_OFFSET_HOURS` / `local_now()` / `local_today()` / `record_activity()` / `compute_streak()` → 返回 `StreakInfo(current, longest, studied_today, last_study_date)`
- **存量回填** `migrate.backfill_study_days()`：从 `last_quiz_at / last_review_at` 折算本地日期，`INSERT OR IGNORE` 幂等写入 9 天（08-24 / 08-26 / 08-27 / 08-28 / 08-31 / 09-02 / 09-03 / 09-04 / 09-07）
- **前端 `components/StreakBadge.tsx` + `.css`**：三态 `active / at-risk / broken`，状态由纯函数 `streakVariant(days, studiedToday)` 派生
- **验收脚本**：`backend/_p91_e2e_check.py`（28 项，跑临时库）、`backend/_p91_smoke.py`（真 API 冒烟，快照 + 还原）

### Changed
- `GET /api/dashboard`：`streak_days` 由硬编码 `0` 改为真值，并新增 `studied_today` / `longest_streak` / `last_study_date`
- `POST /api/lessons/{id}/quiz/submit` 与 `POST /api/review/{id}/submit`：成功后记一次有效学习行为
- `Home.tsx` hero 新增 `.hero-metrics` 容器（进度环 + Streak 同层），窄屏整组右对齐换行；「最长连续 N 天 · 最近日期」进「进度摘要」次要区
- `types.ts`：`Dashboard` 补 3 个 streak 字段

### Fixed
- **时区切天错误（预防性修复）**：全库存 UTC，若按 UTC 日期切天，UTC+8 用户的"一天"会是本地 08:00→次日 08:00，早上 7 点学完记到"昨天"。改为按 `LOCAL_UTC_OFFSET_HOURS` 折算本地日历日

### Architecture
- **Streak 永不持久化**：任何表都没有 `current_streak` / `longest_streak` 列，一律读时计算，无法与活动日志失同步，规则变更无需迁移
- **同事务埋点**（用户明确要求）：`record_activity()` 只 `flush()` 不 `commit()`，在两个提交接口的 `db.commit()` 之前调用——判分/调度写入与学习日记入同事务，成功同成功、失败同回滚
- **常量通用化**：偏移量命名为 `LOCAL_UTC_OFFSET_HOURS` 而非 Streak 专属，作为全应用业务时区
- **中断语义（Duolingo 式）**：不是"没学立刻清零"，而是"过完一整天没学才断"；今天没学但昨天学了 → streak 保持 N（At Risk），最后学习 ≤ 前天 → 归零（Broken）；`longest` 断链不回退
- **有效学习行为口径**：Quiz 提交 ✅ / Review 提交 ✅（过不过都算，空提交已被既有 422 拦截）；Lesson 阅读 ❌ / Note ❌ / 打开 Dashboard ❌
- **零新增依赖**：不用 `zoneinfo`（Windows 缺 tzdb，需额外装 `tzdata`），不用动画库；火焰呼吸仅 CSS `@keyframes` + `prefers-reduced-motion` 关闭

### RedLines（未抢跑）
- 不做 Streak Freeze（断连保护卡）/ 补签 / Badge 成就 / 每日目标 XP / 学习日历热力图 / 定时与后台任务 / 前端倒计时
- 不做多用户鉴权（`user_id` 只预留列位，不建 user 表）

### 验收
- `_p91_e2e_check.py` 28 项全绿：空库 / 同日幂等 / 连续三天 / 宽限日不断链 / 隔整天断链 / 断链后重来 / 时区边界（UTC 09-06 23:30 → 本地 09-07）/ 未知 kind 报错 / flush 未 commit 不落库 / 真库只读核对
- API 冒烟：提交 lesson 33 测验（score 40 失败）后 `study_days` 09-07 `activity_count` 4→5、`lessons_done` 2→3，证明**失败提交同样计入有效学习日**
- 冒烟前后快照 + 还原并复核：`lesson_mastery=32`、`lesson 33 mastery=0`、`study_days=9`、`09-07=(4,2,2)`、`lessons=66 / quizzes=660` 全部未变（备份 `spark_quest.db.bak_before_streak`）
- `tsc -b && vite build` 零错误

---

## 2026-09-08 — Phase 9.2：🏅 Badge 成就系统

Phase 9.1 Streak 之后，游戏化第二阶段落地 Badge。产品意义：**Content → Learning/Retention Loop → Badge（成就可视化、给正反馈）**。严格按设计稿落地，未扩大范围（无 XP/金币/排行榜/商店/社交/多用户）。

### Added
- **3 张表**：`badge_definitions`（目录，20 枚：`code` 唯一 + `is_secret` 单字段 + `image` 为 `/badges/*.webp` 相对路径）、`user_badges`（`UNIQUE(user_id, badge_id)`，insert-only，幂等基石）、`user_stats`（终身事件计数器：quiz_correct / quiz_submitted / reviews_passed / reviews_submitted / debug_correct）
- **解锁引擎 `badge_service.py`**：`BADGE_RULES` 字典（20 枚全量重算）+ `evaluate_badges()`（读时求值，新解锁 `ON CONFLICT(user_id, badge_id) DO NOTHING`）+ `increment_user_stats()`（同事务加性累加，永不递减）+ `build_context()` 一次聚合
- **20 枚徽章**：8 旅程 `LEVEL_0–7`（由 `course_levels` 自动派生，非硬编码数量）+ 12 特别（QUIZ_100/500/1000、STREAK_7/30/100、REVIEW_50、BUG_HUNTER、BLITZ、LATE_NIGHT、WANMEI、QUANJING）；`LEVEL_NAMES` 手工映射 0–7 中文名
- **种子 `seed_badges.py`**：`ON CONFLICT(code) DO UPDATE` 保留 `id`（规避 `REPLACE` 重排 rowid 破坏 `user_badges.badge_id` 外键）
- **背填 `migrate.backfill_badges()`**：`user_stats` 仅当行不存在时写一次（绝不覆盖线上累加），再 `evaluate_badges` 解锁一切可派生徽章；挂 `init_db` 课程种子之后（LEVEL 定义依赖 `course_levels`）
- **前端**：`pages/BadgesPage.tsx`（`/badges` 路由，按 tier 分两组网格，未解锁灰度、SECRET 未解锁显示「神秘徽章 / ?」）、`Home.tsx`「最近解锁」条 + 页脚入口、`components/BadgeUnlockToast.tsx`（提交后右下角轻量浮动提示，5.2s 自动消失，解锁的 SECRET 正常显示）
- **验收脚本**：`backend/_p92_smoke.py`、`backend/_p92_e2e_check.py`（7 项，均快照 + 还原）

### Changed
- `POST /api/lessons/{id}/quiz/submit` 与 `POST /api/review/{id}/submit`：`record_activity` 之后、`db.commit()` 之前调用 `increment_user_stats` → `evaluate_badges`（同事务；`autoflush=False` 靠两者内部 `flush()` 让刚写状态对引擎可见）；响应新增 `new_badges`
- `GET /api/badges`（新增）：20 枚目录 + 解锁态，SECRET 未解锁时 `name/description/image` 置空
- `GET /api/dashboard`：新增 `recent_badges`（最近 6 枚，解锁的 SECRET 正常显示）
- `QuizPage` 提交带 `started_at`（`new Date().toISOString()`）供 BLITZ；`types.ts` 补 `Badge` / `new_badges` / `recent_badges` / `started_at`

### Fixed
- **BLITZ 时区 bug**：`_parse_started_at` 曾把客户端 UTC 时间戳转成本地时区，与 `datetime.utcnow()`（UTC）对比导致 UTC+8 机器上时长变负、BLITZ 永不触发 → 改为统一转 UTC 朴素时间戳
- `badge_service.evaluate_badges` 误把 `select(UserBadge.badge_id)` 的标量结果当实体取 `.badge_id` → 改为 `set(scalars(...))`
- `is_late_night` 仅在 `event_kind` 非空时判定，背填/只读路径不会因运行时间误判深夜徽章

### 决策与修正（用户拍板）
- Bug 猎手阈值 50→**20**（全库仅 43 道 debug 题，且前 4 Level 已掌握，50 永远够不到）
- 背填 `user_stats` 精度：quiz_submitted=SUM(attempts)=68、reviews_passed=SUM(review_count)=42 为**准确值**；quiz_correct=SUM(correct_count)=160 为**下界**（lesson_mastery 只存每课最近一次）；debug_correct 无历史起点 0
- SECRET 仅单字段 `is_secret`（去掉多余的隐藏开关）；计数器语义跟随既有 submit/attempt；背填按字段区分精度

### Architecture
- **不新增任何学习状态列**：20 枚徽章全由既有表 + `user_stats` 派生
- **幂等**：`user_badges` 唯一约束 + `ON CONFLICT DO NOTHING`；背填 `user_stats` 用 INSERT OR IGNORE 仅写基线一次
- **零新增依赖**：前端纯 CSS 动画，不引动画库；二进制 webp 由 Vite 静态托管
- **背填恰为 6 枚**：LEVEL_0–3（已全掌握）+ QUIZ_100（160≥100）+ WANMEI（34 课全部 100%）；REVIEW_50(42<50) / STREAK_7(最长 3) / QUIZ_500(160<500) / 事件型（无真实事件）均不解锁，符合预期

### RedLines（未抢跑）
- 不做 XP / 金币 / 排行榜 / 商店 / 社交分享 / 每日目标 / 学习日历热力图 / 多用户鉴权 / 后台定时任务 / 前端倒计时

### 验收
- `_p92_e2e_check.py` 7 项全绿：目录形状 20=8+12、SECRET 置空、背填恰 6 枚、背填幂等、BLITZ 快交触发/慢交抑制、BUG_HUNTER/LATE_NIGHT 保持锁定
- 真实 `uvicorn --port 9000` 启动：`/api/health` ok、`/api/badges` 20 枚（6 解锁）、`/api/dashboard` 含 `recent_badges=6`，路由全部挂载正常
- `tsc -b` 与 `vite build` 零错误

---

## 2026-09-08 — Phase 10.1：🧠 薄弱题 / Weak Questions（事实层 + 单题重练）

Phase 9.2 Badge 之后，把核心学习闭环补完整：**学习 → 测试 → 犯错 → 记录 → 再做 → 修复 → 再验证**。此前 Quiz/Review 每次提交的逐题结果（含解析）只回传前端即丢弃，`weak_points` 仅存每课"最近一次"错题 id（覆盖写）；"马马虎虎看一眼解析就过去"的题从此无据可查。本阶段以**专项架构审计**（2026-09-08）定性为 Level B（基础数据够、缺一个很小的事实记录）后实施。设计稿 `Spark_Quest_Phase10_薄弱题_执行计划_设计.md` 经用户验收通过（含 4 点修订）。

### Added
- **事实层 `quiz_answer_log`（append-only）**：`user_id(哨兵) / lesson_id / question_id / source('quiz'|'review'|'practice') / selected_index / correct_index(事件快照) / is_correct / submitted_at`；复合索引 `ix_quiz_answer_log_user_question_time(user_id, question_id, submitted_at)` 替代 3 个单列索引（事实表典型访问路径：一个用户 → 某道题 → 全部历史 → 按时间排序）；**零状态列**（无 wrong_count/status/mastery/is_fixed）
- **写入点**：Quiz submit（source='quiz'）与 Review submit（source='review'）在 `db.commit()` 前同事务逐题追加；新端点 Practice（source='practice'）独立事务追加
- **`routers/weak_questions.py`（3 端点）**：`GET /api/weak-questions`（跨来源派生：wrong_count=COUNT / last_wrong_at=MAX / last_attempt_correct=最近一行，过滤 wrong_count≥1，排序 wrong_count DESC + last_wrong_at DESC）、`GET /api/weak-questions/{id}`（题面**不含 correct_index**）、`POST /api/weak-questions/{id}/practice`（服务端判分 + 返回对错/解析）
- **前端 `/wrong-questions`（最小版）**：`WeakQuestionsPage.tsx`（总数 + 卡片列表：题干/维度·L{n}/错误 N 次·相对时间/「最近一次已做对」标签；「重新练习」弹单题面板 → 独立作答 → 对错高亮 + 解析 → 可重试，**无强制勾选**）+ `Home.tsx` 页脚「🧠 薄弱题 →」入口 + 路由/类型
- **验收脚本**：`backend/_p101_smoke.py`（23 项，快照 → 测 → 还原）

### Changed
- `lesson_mastery.weak_points` 语义保留不动（继续作为 Review 维度提示）；Review 调度、5/5 门槛、Quiz 判分全部不变
- `schemas.py` 新增 `WeakQuestionOut / WeakQuestionDetailOut / WeakQuestionPracticeIn / WeakQuestionPracticeOut`

### 决策与修正（用户验收拍板，4 点）
- **复合索引替代 3 单列索引**：结构设计问题，不是性能优化；`lesson_id` 不单建索引
- **`correct_index` 保留**：是"作答事件当时正确答案的快照"，非状态非聚合——题库日后修订，历史仍准确回答"当时如何判定"
- **Practice 绝不触碰 mastery/SRS/streak/badge stats**（来源 × 副作用矩阵写死）：一次重练就是一条新事实，不能因"答对了"偷偷影响学习状态
- **"薄弱"定义写死**：= "历史上至少出现过一次错误作答"，不代表当前未掌握；`wrong_count=2` 且 `last_attempt_correct=true` 仍在列表是设计语义
- **跨来源统一聚合**：Quiz ❌ + Review ❌ + Practice ✅ → `{wrong_count:2, last_attempt_correct:true}`，`source` 只是事件标签

### Architecture
- **不叫 `wrong_questions`**：命名会诱导塞入 status/mastery/wrong_count/is_fixed，最终造出第二套 Mastery；"事实存库、状态派生"原则的正面落地
- **不做历史 backfill**：Phase 10.1 前的逐题尝试已丢弃不可恢复，强行回填=制造伪历史；日志自实施日起累积，越用越有价值
- **不强制阅读解析**：真正的"懂了没"靠之后重新独立遇到并作答，不是勾选"我看过了"

### RedLines（未抢跑）
- 无错题状态表 / 无错题 Mastery / 无"已修复"状态机 / 无强制阅读解析 / 不重建 Review / 不引入新 SRS / 不一次做全 UX（筛选/归档/薄弱度升级留 Phase 10.2+）

### 验收
- `_p101_smoke.py` 23/23 全绿：quiz 错→入列(wrong_count=1)、practice 错→2、review 错→3（跨来源合并）、practice 对→count 不变+last_attempt_correct=true、practice 对 study_days(行数+行内容)/user_badges/user_stats/lesson_mastery 零污染、log 表无状态列
- 真实 `uvicorn --port 9000`：health ok、新表由 init_db 自动创建、干净库 `/api/weak-questions` 返回 `[]`、不存在题 404
- `tsc -b` 与 `vite build` 零错误；测后 DB 从快照还原（quiz_answer_log=0 行就绪，用户进度零触碰）

---

## 2026-09-09 — Level 4（执行计划）全面技术修复

起因：学员学到 L4-6「WholeStageCodegen 与 Tungsten」时发现 `*(N)` 概念错误。据此先出《Spark Quest Level 4 技术审查报告（2026-09-09）》（四维：技术事实准确性 / 示例真实性 / 概念边界 / 版本敏感性），结论 **P0 1 项、P1 6 项、P2 6 项、P3 5 项**，随后按报告逐项落地。审查对象：Level 4 全部 9 课（lesson id 31–39）+ 90 道 quiz，数据以 `backend/spark_quest.db` 真库为准。

### Fixed — P0：`*(N)` 语义完全说反
- 课文与题库原写「`*(N)` = WholeStageCodegen 融合的算子数」，**实为 codegen stage 编号（codegenStageId）**
- 证据 SPARK-23032（Fix 2.3.0）官方输出：`*(1)` 下有 2 个算子、`*(3)` 下只有 1 个；Exchange 之后编号继续 `(4)(5)(6)`、**不归零**
- 正确读法：数「带相同 N 的行数」= 该 stage 的算子数；数「不同 N 的个数」= 这条查询有几个 codegen stage
- 涉及 L4-4 / L4-6 / L4-9 课文 + **q379 / q397 / q403 / q404 / q433 —— 5 道题原本在考错误答案**

### Fixed — P1（6 项）
- `explain(mode="formatted")` 版本：2.3+ → **3.0+**（SPARK-27395；勿与 SPARK-23032 混为一谈）
- **join 非必然宽依赖**：shuffle-based join（SortMergeJoin / ShuffleHashJoin）才需要 Exchange；**Broadcast Join 不 Shuffle、不切 Stage**（与 Level 6 教学对齐，消除跨 Level 自相矛盾）
- **groupBy 非必然 Shuffle**：上游已按该 key 分区时 `EnsureRequirements` 判定满足，不插 Exchange
- L4-8 `repartition(200)` 示例漏算一次 Shuffle：repartition 自身即 Exchange，实为 **2 个 Shuffle 边界 / 3 个 Stage**
- **Action ≠ 恰好一个 Job**：`show()` 底层是 `take(21)` 逐轮扩大，可能触发多个 Job
- **Job 内 Stage 非必然串行**：有依赖的等父 Stage，无依赖的可并行提交

### Fixed — P2（6 项）
- 3 处 `df.select('city').filter(df.amount>0)` 会抛 AnalysisException → 改为 `select('city','amount')` 或 filter 前置
- **UDF 下推失效的因果讲反了**：不是「优化器看不懂 UDF」，而是含 UDF 的过滤条件依赖 UDF 输出值、顺序上无法前移；且**列裁剪照常发生**，只是 UDF 依赖的列必须保留
- 等价改写补非确定性表达式边界：`rand()` / `current_timestamp()` / `monotonically_increasing_id()`
- 宽依赖容错：「重算整个上游重排」是 RDD 论文（2012）的叙述 → 改为「Shuffle 输出丢失时可能需重新执行相关上游 map task」
- 「Stage 数 = Shuffle 数 + 1」降格为**单条线性链**的快速估算，多分支 DAG 不套用
- 列裁剪：Parquet/ORC 可跳过整列数据；**csv 等行式文本通常仍需读取并解析整行**

### Added — P3（版本敏感性）
- L4-3 补 Spark 3.0+ 五档 explain 模式（simple / extended / codegen / cost / formatted），并说明 `mode="codegen"` 可直接看生成的 Java 代码
- **AQE 版本提示**：Spark 3.2+ 默认开启，`explain()` 只给初始计划（常显示 `AdaptiveSparkPlan isFinalPlan=false`、整棵树看不到 `*(N)`）；教学演示需 `spark.conf.set("spark.sql.adaptive.enabled","false")`，最终计划结合 Spark UI 看
- FileScan parquet 在 Spark 3.x 常不带 `*`（向量化读取后 codegen 从 ColumnarToRow 开始），不代表没优化
- 版本注：WholeStageCodegen 2.0 引入 / `*(N)` 编号 2.3 引入 / formatted 3.0 引入 / AQE 3.2 默认开启
- **Tungsten 重新定义**：紧凑二进制内存表示 + cache-aware 算法与数据结构 + 代码生成；**WholeStageCodegen 属于其中「代码生成」一支，是包含关系而非并列两层**

### Changed
- 措辞统一：「生成一个手写 Java 方法」→「生成 Java 代码并编译执行」；「回退到解释执行」→「回退为逐算子 iterator（Volcano 式）执行，Spark 没有解释器」
- **答案位置重排**：L4 90 题 correct_index 原为 A38/B45/C6/D1（学员凭位置即可猜中约 70%）→ **A22/B24/C22/D22**。只动**无 `quiz_answer_log` 作答记录**的题（38 题）；15 道已作答题 + q427（选项为 0/1/2/3 天然序列）冻结不动
- **`lessons.objective` 补修**：该字段是独立列（前端渲染为「🎯 学完后，你应该能回答」），不在 content JSON 内，首轮修复漏扫 → 9 条中 8 条重写；`description` 同源 2 处一并修
- **三段引导文案重写**（review / problem / preview）：原每段仅 60~110 字、读起来像目录摘要 → 对齐 Level 0/1 调性重写为 review 160~313 字 / problem 98~170 字 / preview 193~249 字（承接已知 → 转折悬念 → 固定「下一课：XXX」）

### Architecture
- 不改表结构、不新增持久化状态；全部改动落在现有 lessons / quizzes 行内
- `app/course_seed.json` / `app/quiz_seed.json` 已用真库回写（否则删库重建会把错误内容重新种回）；`seed_level4.py` 加「已过期、勿执行」警告
- 《心智模型与比喻边界案例库》§5 Level 4 九条目 + L2/L3 四处同源口径一并更正 —— **该文档是写新课时参考的源头，也是本次 Level 4 出错的根因**

### RedLines（未抢跑）
- 不改 Level 4 课程结构与课时数；不顺手重构 UI / DB；不修改用户学习进度（`lesson_mastery` / `study_days` / `user_stats`）

### 遗留技术债（用户决定暂不修）
- **L2 / L3 课文与题库仍是旧口径**（orderBy 必 Shuffle / 聚合必 Shuffle / JOIN 必 Shuffle），与已更正的设计文档存在**已知的不一致**；当前收益低，登记为技术债
- L4 lesson 31 因 5 道冻结题中有 4 道固定在 B，该课答案分布只能做到 A2/B4/C2/D2

### 验收
- 真库核实：Level 4 仍 9 课 / 90 题 / 每课 10 题 / 无重复题干 / 无 orphan quiz
- 关键词扫描剩 11 处命中，逐条人工确认均为合法文本（纠错句、否定句、以及干扰项里故意保留的旧说法）
- 答案重排正确性：与重排前备份逐题比对 —— 正确答案**文本** 0 改动、选项集合 0 异常、已作答题位置 0 移动
- 脚本（均支持 dry-run 与自动备份）：`backend/fix_level4_20260909.py`、`fix_level4_20260909_round2.py`、`fix_level4_objective_20260909.py`、`rebalance_l4_answers_20260909.py`、`rewrite_level4_narrative_20260909.py`、`sync_seed_from_db_20260909.py`、`preview_level4_narrative.py`
- 文档：`spark_quest/docs/Spark_Quest_Level4_技术审查报告_20260909.md`、`Spark_Quest_Level4_修复报告_20260909.md`（含附录 A 重排 / B objective 补修 / C 文案重写 / D 比喻库更正）

---

## 2026-09-10 — Level 5 / Level 6 技术审查与修复

起因：Level 4 修复完成后，对同为「执行与优化」主线的 Level 5（分区与 Shuffle，lesson id 40–48）与 Level 6（JOIN 与 Broadcast，lesson id 49–57）做同口径审查，过程中发现问题顺手修掉。审查维度同 L4：技术事实准确性 / 示例真实性 / 概念边界 / 版本敏感性。结论：**L5 问题明显重于 L6**——L6 的 BHJ / SMJ / SHJ 原理扎实，主要缺口是未提 AQE 会在运行时改写计划；L5 有多处与 L4 已更正口径**直接冲突**。

### Fixed — 明确错误（4 项）
- **`repartition(n)` 不是 hash 重分布，是 round-robin（轮询打散）**，同 key 不保证同分区；只有 `repartition(n, col)` 才是按列哈希。原说法会推出「`repartition(200).groupBy('city')` 已按 city 分好区、只 Shuffle 一次」的错误结论——而这正是 L4-8 三 Stage 例子的立论前提。涉及 L5-6 课文 + q491 / q510 / q511
- **`sortWithinPartitions` 被误列进 Shuffle 触发清单**：它只在各分区内部排序，不跨节点重排，**不 Shuffle**
- **q481 仍用 L4 已废的容错口径**（「上游任何分区丢都要整体重算」）→ 改为「可能需重新执行相关上游 map task」，并在解析中点明整体重算是 RDD 论文（2012）的叙述
- **L6-1 写「0 个 Exchange = 走了广播」**：BroadcastExchange 名字里就带 Exchange，广播路径是 **1 个**不是 0 个。学生照此数必然数漏

### Fixed — 绝对化表述清理
- Shuffle「必然代价、躲不掉」→**通常**（上游已按该 key 分好区时可省；Broadcast Join 不产生 ShuffleExchange）
- 宽依赖「必 Shuffle」→**通常**，并明确 **Broadcast Join 不属于宽依赖**（不满足「子分区依赖所有父分区同 key 数据」的定义）
- join 从「必 Shuffle」清单移出，改为分策略表述（sort-merge / shuffle-hash 需重排，Broadcast 不需）
- 「广播是唯一常见的免 Shuffle 路径」→**两条**：一侧足够小可广播，或两侧已按同一 join key 分好区
- 磁盘 spill「I/O 慢几个数量级」→**1~2 个数量级**
- `repartition` 的「必 Shuffle」保留（它确实一定 Shuffle）

### Added — 版本事实（15 处，均核对官方文档）
- **`spark.sql.adaptive.skewJoin.enabled` 默认 true（自 Spark 3.0）**：AQE 会自动拆分倾斜分区（必要时复制）。因此 **3.x 上手工加盐往往不是第一步**，应先看 AQE 是否生效，没兜住再考虑 salting / 隔离 / 广播
- **AQE 3.2+ 可在运行时把 SMJ 改成 BHJ**：L6-6 原「策略只在规划期决策一次」不再成立，实际是「规划期一次 + 运行期若干次」，且运行期用的是**实测**统计
- `spark.sql.crossJoin.enabled` 3.0 起默认 **true**（2.4 及更早对隐式笛卡尔积直接抛 AnalysisException，现在不拦了）
- Spark 3.x 默认 `spark.sql.join.preferSortMergeJoin=true` → SHJ 相对少见；3.2+ 另有 `spark.sql.adaptive.maxShuffledHashJoinLocalMapThreshold`（默认 0 即关闭）
- 广播阈值 `spark.sql.autoBroadcastJoinThreshold` 默认 **10MB**；广播还有 join 类型限制（如 FULL OUTER JOIN 无法走 BHJ）
- `spark.sql.shuffle.partitions`（默认 200）在 AQE 下只是 shuffle 后的**初始**分区数，运行期会合并 → 200 是上界不是结果
- 读文件初始分区数由**实现**决定：DataFrame 看 `spark.sql.files.maxPartitionBytes`（默认 128MB），RDD 看 InputFormat split；「常常等于 block 数」是巧合不是定义
- `orderBy().limit(n)` 会被优化成 `TakeOrderedAndProject`（内部一次单分区 Shuffle）
- 分区数决定的是**理论**并行度，实际并发上限还受可用 core 数限制
- combine 的准确条件是**可结合**（associative）；「可交换」通常同时成立但非必要条件

### Changed
- 课文 17 课 + `lessons.objective` / `description` 共 5 处（沿用 L4 教训：**objective 是独立列，不在 content 七键 JSON 内**）
- 题库 **26 题**（L5 21 + L6 5）；**correct_index 一个未动**，改的是选项文本与解析
- 《心智模型与比喻边界案例库》**§6 Level 5 九条目 + §7 Level 6 八条目全部按结论更正** —— 该文档是写新课时参考的源头，也是 L4 出错的根因，本次一并堵住

### Architecture
- 不改表结构、不新增持久化状态；全部改动落在现有 lessons / quizzes 行内
- `app/course_seed.json` / `app/quiz_seed.json` 用**全量**同步脚本（`sync_seed_all_20260910.py`，66 课 / 660 题）回写，取代此前只同步 L4 的脚本

### RedLines（未抢跑）
- 不改 Level 5 / 6 课程结构与课时数；不顺手重构 UI / DB；不修改用户学习进度（`lesson_mastery` / `study_days` / `user_stats` / `quiz_answer_log`）

### 验收
- 真库核实：全局 66 课 / 660 题；L5 9 课 90 题、L6 9 课 90 题；每课 10 题；无重复题干；无 orphan quiz
- seed 与真库逐题比对：**0 处不符**
- 关键词扫描剩 17 处命中，逐条人工确认均为合法文本（`repartition` 的准确「必 Shuffle」、否定式告诫句、干扰项、以及 q481 解析中刻意引用的旧说法）
- 脚本：`backend/fix_level56_20260910.py`（支持 dry-run）、`sync_seed_all_20260910.py`
- 文档：`spark_quest/docs/Spark_Quest_Level5_Level6_技术审查与修复报告_20260910.md`

### 遗留技术债与待办
- **L2 / L3 课文与题库仍是旧口径**（orderBy / 聚合 / JOIN 必 Shuffle），与已更正的设计文档存在已知不一致 —— 用户决定暂不修
- **Level 7 尚未审查**：它讲 Tungsten / 内存模型 / 分区调优，且引用的 L5 / L6 结论本次已变更（如 `shuffle.partitions` 默认 200 的口径），建议单独审一轮
- L5 / L6 答案位置分布未核查（L4 曾发现 A38/B45/C6/D1 的严重失衡）

---

## 2026-09-11 — Level 5 / 6 / 7 三段引导文案修缮（对齐 Level 0/1 调性）

起因：Level 4 的三段引导文案（上一课回顾 / 本课要解决的问题 / 下一课伏笔）曾按 Level 0/1 调性重写过；本次审查发现 L5/L6/L7 仍是建课时的「目录摘要」写法——单段无空行、篇幅只有 L0/L1 的三分之一。Level 7 最简陋，`problem` 段平均不到 45 字。用户要求按同一标准修缮，27 课 × 3 段全部重写。

### 改动数据（重构前 → 重构后）

| 字段 | L5 | L6 | L7 | 重写后（L5–L7 统一） |
|---|---|---|---|---|
| 上一课回顾 | 49–115 | 48–146 | 42–117 | **130–320 字（均 170）** |
| 本课要解决的问题 | 45–100 | 41–65 | 36–58 | **94–168 字（均 133）** |
| 下一课伏笔 | 37–120 | 52–127 | 44–96 | **184–284 字（均 220）** |

### Changed — 统一的四条写法（对齐 Level 0/1）

- **回顾**：先承接「上一课我们已经知道了 X」→ 一个转折或较真 → 抛悬念；用空行分段，不再是一整坨
- **本课问题**：连续追问 + 结尾点明「搞懂它你能得到什么」
- **下集伏笔**：本课收获 → 一个自然的追问制造悬念 → 固定收尾「下一课：XXX」
- **全程第二人称、口语化**，允许反问与共情；粗体 / 行内 code / `·` 列表按前端 RichText 规则
- Level 末课（L5-9 / L6-9 / L7-9）preview 改为「收束 + 🏁」，不写「下一课」；L7-9 额外做了跨 Level 的全课程收束（Level 0 → 7 主线）

### 约束（均已遵守）

- **比喻不新造**：全部沿用《心智模型与比喻边界案例库》§0 全局道具表 + §6/§7/§8 已登记道具（托盘 / 空中飞货 / 小册子 / 坐满人的椅子 / 真空压缩袋 / 货车车厢四格 / 车道数与车流 / 秤的刻度 / 会改路的导航 / 交警分流）
- **技术口径与已修复课文一致**：「宽依赖**通常**需 Shuffle」「免 Shuffle 有两条路径」「Broadcast Join 不属于宽依赖」「repartition 是轮询打散」「sortWithinPartitions 不 Shuffle」等
- **扫描复检出 2 处风险表述并修掉**：L5-3 的「需求的**必然**产物」（易读成「Shuffle 必然发生」）→「某类需求逼出来的结果」；L6-3 的「**唯一**能让大表一次货都不飞」（与上一轮拍板的「免 Shuffle 有两条路径」冲突）→「免掉大表那次 Shuffle 的那条路」

### Fixed — 顺手清理

- `key_points` 里上一轮替换脚本留下的 3 处重复词（L5-2 的「（实际并发还受可用 core 数限制）」×2、L5-7 的「（除非上游已按同 key、同分区数分好区）」×2、L5-8 的「repartition(n) 是轮询打散…按列哈希」整句重复）

### Architecture

- 只改 `lessons.content` 的 review / problem / preview 三键，不动 explanation / examples / key_points / common_mistakes，不动 objective / description，不动题库与任何表结构
- `app/course_seed.json` / `app/quiz_seed.json` 已用 `sync_seed_all_20260910.py` 全量回写

### 验收

- 27 课全部落库；`content` 七键完整、无空段；换行分段、粗体与行内 code 标记保留
- 结构校验：L5-9 / L6-9 / L7-9 收束正确（含 🏁、无「下一课」）；其余 24 课 preview 均含「下一课：」
- 危险表述扫描命中 5 处，逐条人工确认：2 处修掉，3 处为正确用法（L5-5 引号内的「宽依赖必切 Stage」口诀并随即破例、L5-6「一定 Shuffle / 可能 Shuffle」是课本既有的教学分类框架）
- 脚本：`backend/rewrite_narrative_l567_20260911.py`（--dry / --apply，幂等）、`backend/preview_narrative_567_20260911.py`
- 预览：`backend/_l567_narrative_preview.html`（渲染规则对齐前端 RichText，已加入 .gitignore）

---

## 2026-09-11 — Level 7（性能调优）技术审查与修复

Level 4 → L5/L6 之后，对执行与优化主线的最后一环 Level 7（lesson id 58–66 + 90 道 quiz）做同口径审查。**结论：L7 无 L4 那种「把定义说反」级别的 P0 错误，整体质量好于 L5**，五段式 explanation 与边界条目写得完整；但存在一个系统性缺口——**版本事实缺失**。

### Fixed — P1（3 项）

- **乱码 2 处（U+FFFD）**：L7-4 / L7-9 的 `examples[].note`（「复用 L5」「真实执行图」）。全库复查后残留 0
- **AQE 默认开启的事实缺失（本次最重要）**：Spark 官方文档明确 **AQE「enabled by default since Apache Spark 3.2.0」**。原课文把 AQE 讲成「需要手动开启的功能」，导致五处表述与 3.x 现实脱节：
  - L7-4「`shuffle.partitions` 就是后续 Task 数」→ AQE 下只是**初始上界**（补 ⑤ 版本提示）
  - L7-5 静态 explain 的 SortMergeJoin 未必是最终策略（补 ⑤）
  - L7-6「前面所有优化都发生在出发之前」/「**开启** AQE」（补 ⓪ 版本提示；example 改为「读取并确认状态」）
  - L7-7「**开**自动倾斜处理，优先试」→ `skewJoin.enabled` 默认 true（3.0），实际是**「先确认它有没有生效」**
  - L7-9 检查单「开 AQE」→「**确认 AQE 效果**」
- **绝对化「慢几个数量级」**：L7-4 note + q646 解析 → **1~2 个数量级**（与 L5 已更正口径对齐）

### Fixed — P2（4 项精度问题）

- **内存借用「反之亦然」不准确**：实为**不对称**——Execution 可直接驱逐 Storage，Storage 不能反向驱逐。已显式写明并解释原因
- **「明明有内存却 OOM」解释不够硬**：补默认划分——Reserved 固定 **300MB**、`spark.memory.fraction` 默认 0.6、`storageFraction` 默认 0.5，剩约 40% 为 **User Memory 且不参与借用**（这正是该现象的来源）
- L7-1「读了 200 列里的 200 列」表述逻辑不通 → 「200 列一列没裁、全读了」
- L7-2「吃掉的 **memory**」中英混用 → 「内存」；「Parquet 读出**直接**组织成紧凑二进制行」→ 补向量化读取（ColumnarBatch → UnsafeRow），与 L4-6 的 P3-2 口径对齐

### Added — P3（版本事实）

- 广播阈值 `autoBroadcastJoinThreshold` 默认 **10MB**（Spark 3.x）
- AQE 子开关 `coalescePartitions.enabled` / `skewJoin.enabled` 默认 true（自 3.0.0）；三大能力自 3.0 引入
- Reserved Memory 固定 300MB、不可配置

### Changed

- 8 课课文（58/59/60/61/62/63/64/66）+ **5 道题解析**（q646 / q650 / q666 / q674 / q684）+ 3 处 `key_points`（61、63 各新增一条；64 修订一条）
- **correct_index 一个未动**，题库结构与课时数未变
- 《心智模型与比喻边界案例库》**§8 Level 7 五个条目**按结论更正并加节首版本提示——该文档是写新课的参考源，也是 L4 出错的根因

### Architecture

- 不改表结构、不新增持久化状态；全部改动落在现有 lessons / quizzes 行内
- `app/course_seed.json` / `app/quiz_seed.json` 已全量回写（66 课 / 660 题）

### RedLines（未抢跑）

- 不改 Level 7 课程结构与课时数；不顺手重构 UI / DB；不修改用户学习进度

### 验收

- 完整性：全局 66 课 / 660 题；每课 10 题；无 orphan quiz；L7 内部无重复题干
- 乱码：全库（lessons 全字段 + quizzes 全字段）U+FFFD 残留 **0**
- 危险词扫描命中 9 处，逐条人工确认为合法（1 处否定式告诫 + 8 处刻意的错误干扰项）
- 幂等性：脚本复跑 19 处全部 SKIP
- 脚本：`backend/fix_level7_20260911.py`（--dry / --apply）
- 文档：`spark_quest/docs/Spark_Quest_Level7_技术审查与修复报告_20260911.md`

### 报告之外发现（未修，待用户决定）

- **全库有 2 道跨 Level 重复题干**：`为什么「计划相同 ≠ 运行时性能相同」？`（q429 L4-8 / q519 L5-8）、`综合读图的第一步是？`（q425 L4-8 / q515 L5-8）。推测为 L5 建课时复用 L4 出题所致；**不在 L7 范围内**（L7 的 90 题内部无重复）。建议改 L5-8 那两题（更贴合 L5 主题）

### 进度

**至此 Level 4–7（执行与优化主线）全部审查完毕。** 剩余：L0/L1 未做技术审查；L2/L3 旧口径技术债（用户决定暂不修）与三段文案未查。

---

## 2026-09-11 — Level 5 答案位置重排（修复「正确项恒为 A」缺陷）

用户实测 Level 5 首个 lesson 抽题时发现正确项恒为 A。核查确认 **Level 5 共 90 题、88 题 correct_index=0（全 A）**，根因是 `seed_level5.py` 写库时正确项永远放位置 0，未套用 L4 之后确立的「写库时就把正确项放目标位置」约定。**Level 6 分布已是 [22,23,22,23]，无需处理。**

### Fixed
- **Level 5 答案位置重排**：套用规范目标序列 `[2,0,3,1,0,3,1,2,3,1]`（A/B/C/D 计数 2/3/2/3），按课序 rotate 错开跨课位置规律，与 L6 既有设计一致。
- **冻结已作答的 5 题**（均在 lesson 40，有 `quiz_answer_log` 记录），保持原位置不动——重排会令历史作答记录语义错位（沿用 L4 rebalance 口径）。
- 仅对 85 道可动题做选项置换 + `correct_index` 重算，**正确项文本零改动**；解析未写死选项字母（扫描 0 处），无需改写。
- 顺带把修正后的分布写回 `seed_level5.py` 的 `LEVEL5_QUIZZES`，使规范源可重生成（仅作用于「清空 L5 quiz 后重跑 seed」场景；运行中 DB 以本脚本为准）。

### 验收
- L5 整体 A/B/C/D = [22,25,18,25]（原 [88,2,0,0]）；lesson 41–48 每课均为 [2,3,2,3]
- lesson 40 因 5 题历史作答冻结为 A，结果 [6,1,2,1]（用户已做过该课，保留历史语义）
- 全库（L5/L6 options+explanation）U+FFFD 残留 **0**；选项纯置换、正确文本逐题校验一致
- 脚本：`backend/rebalance_l5_answers_20260911.py`（--dry / --apply）、`backend/patch_seed_l5_20260911.py`
- 备份：`spark_quest.db.bak_before_l5rebalance_20260911`、`seed_level5.py.bak_before_l5seedfix_20260911`

### 备注（未修，待用户决定）
- 全库扫描仍有 **Level 2 偏 A [63,13,12,12]、Level 3 偏 B [30,57,3,0]** 的同类分布失衡，非全 A 但不均衡；L0/L1/L4/L6/L7 均已均衡。如需一并洗牌可再处理。

---

## 2026-09-11 — Level 5 干扰项重写（修复「正确项总是最长」缺陷）+ Lesson 42 心智模型去重

用户反馈：L5 抽题刚修完全 A，又发现**正确答案总是最长的那个选项**，毫无挑战性。核查确认 L5 90 题有 **88 题（98%）正确项为严格最长**（中位差 +13 字符）——根因是正确项为完整句子、干扰项全为短短语，长度本身成了给分信号。位置重排只解决了「恒为 A」，没解决「恒最长」。

### Fixed
- **L5 全部 90 题干扰项重写**：把每个干扰项从短短语改写为**与正确项长度相当、事实错误但可信**的完整句子（干扰项文本改写、正确项文本与位置 `correct_index` 一律不动）。
- 数据依据：`backend/l5_distractors_20260911.json`（90 × 3 干扰项），由 `backend/rewrite_l5_distractors_20260911.py` 落库。
- **Lesson 42（Shuffle 是什么）心智模型去重**：原 explanation 的「心智模型」段落在段落首尾各重复一遍定义（开头「空中飞货 = Shuffle = 数据离开原车间、按 key 重排」、结尾「Shuffle 就是把货搬出车间这道动作」），且「先用人话理解」段已先抛过同名飞货比喻，造成两端重复。改为：引言只埋钩子不抢定义、把正式命名交给心智模型段落；心智模型段落删去冗余自述、保留与 Stage 的桥接句。
- 同口径写回 `seed_level5.py` 的 `LEVEL5_QUIZZES`（88 题按 prompt 匹配同步，2 题 stale prompt 跳过），脚本：`backend/patch_seed_l5_distractors_20260911.py`。

### 验收
- 「明显最长（>10 字符差）」占比 **53/90 → 20/90**（↓62%）；「有干扰项比正确项更长」占比 **1/90 → 12/90**——「正确项总是最长」模式已打破。
- 逐题校验：正确项文本 0 改动、`correct_index` 0 位移、选项无重复、U+FFFD 乱码 0。
- Lesson 42 explanation 已无重复定义句；未引入「必/必然/一定/唯一」等绝对化词。
- 备份：`spark_quest.db.bak_before_l5distractors_20260911`、`seed_level5.py.bak_before_l5seeddistractors_20260911`、`spark_quest.db.bak_before_l42mentalmodel_20260911`

### 备注（已修，但性质不同）
- 少量「解释型」题（如 q481/q482/q490/q520，正确项是完整机制说明）正确项仍偏长，属「explain why」题型固有特性，非可作弊的长度信号；此类题干扰项已是完整错误句子，长度差已压到可接受范围。

### 补充（同日稍后闭合 seed 缺口）
- 上述 seed 写回当时有 **2 题 stale prompt 被跳过**：q456（`为什么 groupBy / orderBy 通常会触发 Shuffle？（join 要分策略）`）与 q516（`对单条线性依赖链，估算 Stage 数的公式是？`）的 prompt 曾在 2026-09-10 L5/L6 审计中于 DB 改过、却未回写 seed，导致 seed 仍持旧 prompt + 旧短短语干扰项；若清空 L5 quiz 重跑 seed，这 2 题会把「正确项恒最长」的旧缺陷重新引入。
- 现用 `backend/patch_seed_l5_stale_20260911.py` 以「旧 seed prompt → DB qid（456 / 516）」映射，把这 2 题的 prompt + options + correct_index 按 DB 对齐。seed 现 **90/90 与 DB 一致**（matched=90 / mismatched=0 / correct_text_not_found=0）。备份 `seed_level5.py.bak_before_l5stale_20260911`。

---

## 2026-09-11（续）— Lesson「比喻的边界 / 版本提示」段落重复修复

用户反馈 **Level 5 第二个 lesson（41 分区数与并行度）的「⚠️ 比喻的边界」段里有一整句被复制了两遍、字都一摸一样**（实际是 explanation 里 ④ ⚠️ 版本提示 段落被原样粘贴两次）。排查发现这是 2026-09-10 L5/L6 审计新增「版本提示」段落时引入的**系统性复制粘贴重复**：同段落在该 lesson 出现两次，且同时存在于 DB 与 seed。

### Fixed
- 用行级去重（保留空行、删第二次出现的重复非空行）修复 `lessons.content.explanation`，DB 与 `app/course_seed.json`（lesson 内容真源）**两处同改**，否则重跑 seed 会复活。
- 受影响 lesson：
  - **L5**：41（分区数与并行度，④ AQE 默认开启段落重复）、48（综合练习，版本提示段落重复）
  - **L6**：49（JOIN 是什么，⑤ AQE 运行时改 SMJ→BHJ 段落重复）、52（Sort-Merge Join，同）、54（Spark 怎么选 JOIN 策略，同）、57（综合练习，同）
- 各 lesson 修复后：`④/⑤` 计数 2→1、版本提示段落唯一、无残留重复行、DB==SEED、U+FFFD 0。

### 验收
- 全库 lessons 扫描：修复前 6 课有重复行，修复后 **0 课**有重复行（L41/48/49/52/54/57 全清）。
- 脚本：`backend/fix_l41_l48_dup_20260911.py`（L41/48）、`backend/fix_l6_dup_20260911.py`（L49/52/54/57），均 `--apply` 幂等、删前断言 `removed in (0,1)`。
- 备份：`spark_quest.db.bak_before_l41l48dup_20260911`、`app/course_seed.json.bak_before_l41l48dup_20260911`、`spark_quest.db.bak_before_l6dup_20260911`、`app/course_seed.json.bak_before_l6dup_20260911`。

### 备注
- 用户原先误以为重复在 42（Shuffle 是什么），实际 42 无此重复；本轮未动 42（上一轮已修其真实存在的首尾定义重复）。
- 此 bug 与「全库扫 U+FFFD / 扫重复题干」同源：内容审计只看单 lesson 容易漏，必须全库 + DB+seed 双源扫描。

---

## 2026-09-14 — Level 2 / Level 3 题库修复（正确项长度信号 + 答案位置偏置）+ quiz_seed.json 全量校正

### Fixed
- **L2/L3「正确项恒最长」**：
  - 实测 L2 **72/100** 正确项唯一最长（明显最长 >10 字：39/100，中位差 +8）；L3 **82/90（91%）** 唯一最长（明显最长 45/90，中位差 +10，最大差 +70）。根因同 L5：正确项是完整句、干扰项是极短桩（L3 干扰项中位长度仅 8 字）。
  - 重写 **153 题**干扰项（L2 72 + L3 82；q271 为代码 token「global_temp.」无法加长且差值仅 4，跳过）为**与正确项长度相当、事实错误**的干扰项；对「错误说法」类题（98/103/123/138）改填等长**真陈述**，避免唯一假陈述因更长而暴露。代码/语句类题改用**平行错误语句**（如 q254 的 ETL 顺序、q312 的 SQL、q127/q244 的 agg 表达式）。
  - 两轮执行（首轮全量 + 针对 >10 差值的 37 题补丁）。结果：明显最长(>10) **L2 39→9 / L3 45→8**；差值中位 **8→0 / 10→1**；剩余 >10 的题全部落在 11–20（已无「显而易见」级）。
- **L2/L3 答案位置偏置**：L2 分布 `[63,13,12,12]`（63% A）、L3 `[30,57,3,0]`（57% B、**D 从不出现**）。按课序轮转重排选项顺序（仅置换 + 重算 `correct_index`，**正确项文本零改动**）：L2 → `[25,26,25,24]`、L3 → `[23,23,22,22]`。
  - **已作答（冻结）题一并重排**。依据：`routers/weak_questions.py` 派生薄弱题只读 `is_correct` + `question_id`，**从不回读** `quiz_answer_log.selected_index / correct_index`（两列只写不读）；判分 `payload.selected_index == q.correct_index` 用的也是当前值。故重排不破坏任何派生/判分逻辑，脚本**不触碰** `quiz_answer_log`（保持 append-only）。
- **`quiz_seed.json` 历史遗留（重要）**：核实 App `_seed_quizzes()` 只读 **`app/quiz_seed.json`**。此前 2026-09-11 的 L5 干扰项重写 / 答案重排只回写了 DB + `seed_level5.py`，**漏了 `quiz_seed.json`** —— 其中 L5 90 题仍是旧短桩干扰项（8/12/13 字）+ 旧 `correct_index`，**一旦清库重跑 seed 就会复活 L5「全 A + 正确项恒最长」旧缺陷**。已把 `quiz_seed.json` 全量对齐 DB。

### Changed
- **seeding 口径更正**：App 重跑 seed 的**真源**是 `app/quiz_seed.json`（quiz）+ `app/course_seed.json`（lesson content）；`seed_levelN.py` / `seed_quiz_levelN.py` 是**开发期一次性脚本、运行时不读取**。其中 `seed_level3.py`(LEVEL3_QUIZZES)、`seed_quiz_level2.py`(NEW_QUIZZES) 仍持旧快照、未被任何代码引用（建议后续整合或删除，避免多源漂移）。

### 验收
- L2/L3 修复后：`dist` L2 `[25,26,25,24]` / L3 `[23,23,22,22]`；明显最长 L2 9 / L3 8；差值中位 0 / 1；**重复选项 0、U+FFFD 0**。
- `quiz_seed.json` ↔ DB：**L0–L7 共 660 题零漂移**（`mismatched=0 / missing=0`）。
- 全库 lessons + quizzes：U+FFFD 0、重复选项 0。
- 脚本（`backend/`，均 `--apply` 幂等）：`rewrite_l2l3_distractors_20260914.py`、`patch_l2l3_distractors_20260914.py`、`rebalance_l2l3_answers_20260914.py`、`sync_quiz_seed_l2l3_20260914.py`、`sync_quiz_seed_all_20260914.py`；数据 `l2_distractors_20260914.json`、`l3_distractors_20260914.json`、`l2l3_distractors_patch_20260914.json`。
- 备份：`spark_quest.db.bak_before_l2l3distractors_20260914` / `..._l2l3patch_20260914` / `..._l2l3rebalance_20260914`；`app/quiz_seed.json.bak_before_l2l3sync_20260914` / `..._syncall_20260914`。
- 全部**未 commit / 未 push**（用户验收后推送）。

---

## 2026-09-14（续）— 修复：复习失败后课程被从「今日复习」静默移除

### Fixed
- **复习失败 = 课程从待复习消失（死路）**：`POST /api/review/{id}/submit` 在 <5/5 时调用 `defer_review_schedule()`，把 `next_review_at` 推到 **now + 3 天**。而首页「今日复习」的唯一判定是 `status='mastered' AND next_review_at <= now`（`/api/review/due`）—— 于是**提交失败的那一刻，这节课就从它唯一的入口里掉了出去**：用户看不到"还没复习完"，也无法从首页回到它，只能自己翻到课程页点「间隔复习（5 题）」。
  - 现场还原（lesson 24「SELECT 基础」，Level 3）：`quiz_answer_log` 记录 03:11:11 一轮 4/5 失败 → `next_review_at = 09-17 03:11`（被藏起）；03:14:41 用户手动补做 5/5 通过 → `advance` 到 stage 2、`next_review_at = 09-21`。
  - **不是前端锅**：`/lesson/:id?from=review`（失败页「重新阅读本课」）只 `GET /api/lessons/:id` + 笔记，**不写任何 mastery 字段**。
- **修法（用户 2026-09-14 拍板：失败即留在今日复习）**：
  - `defer_review_schedule()` → **`keep_review_due()`**（`services.py`）：失败时 `last_review_at = now`、`next_review_at = now`（保持"未完成"），返回 **0**（不排新间隔，UI 也不再打印误导性的"+N 天"）。`srs_stage` 照旧**不动**（失败是巩固，不是降级）。
  - `routers/review.py`：改调用 + 更新模块 docstring（原「失败延后 3 天、可立即重试」的 decouple 说明作废）。
  - 结果页失败分支文案：删掉「另已安排在 3 天后再次提醒你复习本课」，改为「本课会继续留在首页『今日复习』里，直到 5 题全对为止」。
- **存量数据核查**：`fix_deferred_failed_reviews_20260914.py`（dry-run / `--apply`）扫描"`next_review_at` 在未来、但最近一轮复习是失败"的行 —— **0 条**（27 个"未来到期"的课要么上轮 5/5 通过、要么从未做过复习）。**无需数据修复，未改动生产数据**。

### Changed
- **失败不再排下一次复习**：`REVIEW_FAIL_INTERVAL_DAYS = 3` 常量**删除**。失败后的语义 = 「本课仍未复习完，继续挂在今日复习里（逾期天数会累积），随时可重试；直到一轮 5/5 才升到下一档」。
  - 副作用存档：规格书 `spark_quest/04_WorkBuddy_开发实施指南.md` Phase 6 写的是「复习错误 → 1 天后」，而实现一直是 3 天；本次改动让**两者都不再适用**（失败不再排期）。规格书该行是否同步待用户决定。

### 验收
- 冒烟（在 `backend/_smoketmp/` 的 **DB 副本**上跑，端口 9100，**真库零改动**）：14 项断言**全过**。
  - 失败轮（4/5）：`next_interval_days=0`、课题**仍在** `/api/review/due`、`next_review_at ≈ now`、`srs_stage` / `review_count` 不变、`status` 仍 `mastered`。
  - 通过轮（5/5）回归：`srs_stage` +1、`review_count` +1、`next_interval_days=7`、课题**离开** `/api/review/due`、due 列表 = 基线 − 该课。
- 真库冒烟后核对：due 16 条不变、`quiz_answer_log` 245 行不变、lesson 24 仍 `stage=2 / next=09-21`。
- 前端 `tsc --noEmit` 通过（0 error）。
- 脚本：`backend/fix_deferred_failed_reviews_20260914.py`（存量核查，dry-run 未写入 → 未产生 `.bak`）。
- 全部**未 commit / 未 push**（用户验收后推送，与同日 L2/L3 题库修复一并待推）。

---

## 2026-09-14（续二）— 冷启动（空库重建）修复 + 废弃开发期 seeder 清理

### Fixed
- **空库冷启动崩溃（潜在 P0：全新克隆 / 删库重建后首次启动必崩）**。`database.py::_seed_course_data()` 在 `course_levels` 为空时执行**首次播种**，该路径存在两处缺陷，因历史 DB 一直存在而从未暴露：
  1. `Lesson(**lesson_data)` 把 `course_seed.json` 里的 `content` **对象**直接塞进 `Text` 列 → `sqlite3.ProgrammingError: Error binding parameter 9: type 'dict' is not supported`。已改为先 `json.dumps(..., ensure_ascii=False)`（与 `_backfill_lesson_content` 同口径）。
  2. `n_lessons = sum(len(l["lessons"]) for l in data["levels"])` 读取的键已被上面的 `level_data.pop("lessons", [])` 移除 → `KeyError: 'lessons'`（被缺陷 1 挡住，修完 1 才暴露）。已改为 **pop 前计数**，且不再 pop 共享 dict（改用 `{k: v for k, v in level_data.items() if k != "lessons"}`），`_backfill_lesson_content` 仍能读到 lessons。
  - **影响面**：`spark_quest.db` 被 `.gitignore` 忽略 → 任何**全新克隆 / 手动删库**都会在启动时崩溃；现存运行库不受影响（历史数据由下面被删的一次性 seeder 写入）。老库补内容路径 `_backfill_lesson_content()` 一直正确（本就 `json.dumps`）。
  - **验证**：全新空库 `init_db()` → `levels=8 / lessons=66 / quizzes=660`，`content` 全部为合法 JSON；与生产库**逐题比对 660/660 零差异**（仅重建有 0 / 仅生产有 0 / 内容不同 0）；全库答案位置分布 `[164,172,158,166]`。

### Removed
- **删除 10 个开发期一次性 seeder 脚本**（用户 2026-09-14 拍板）：`backend/seed_level2.py`、`seed_level3.py`、`seed_level4.py`、`seed_level5.py`、`seed_level6.py`、`seed_level7.py`、`seed_quiz_level2.py`、`seed_quiz_level2_v2.py`、`upgrade_level2.py`、`expand_quizzes_to_10.py`。
  - **理由**：运行时**从不读取**它们（唯一运行时 seed 模块是 `app/seed_badges.py`，保留）；这些脚本内嵌**旧快照**并 `upsert()` 同时写 `course_seed.json` + `quiz_seed.json` + DB —— 尤其 `seed_level3.py` 的 `LEVEL3_QUIZZES` 仍是旧短桩干扰项（`"SAVE TABLE"` / `"SQL 不支持分区"`），**误跑一次即回滚本日 L2/L3 题库修复**，是活跃的多源漂移风险。
  - **真源不变**：`app/quiz_seed.json`（quiz）+ `app/course_seed.json`（lesson content）；清库重建已由上面的冷启动修复保证可用。
  - 被删文件均在 `HEAD` 中，可经 git 历史随时找回。

### Docs
- 规格书 `spark_quest/`（不进 git）：00–05 全部加「文档定位」说明（设计意图 vs as-built，**冲突以 `CURRENT_STATE.md` 为准**）；`04` 路线图状态表按现状校正 + Phase 6 复习节按实际 SRS 重写；`01` §9/§10、`03` 偏差清单、`05` Phase 6 Prompt 同步修正。→ 消解了上一条目遗留的「规格书 Phase 6 与实现不一致」问题。

### 状态
- **未 commit / 未 push**（与同日 L2/L3 题库修复、复习失败修复一并待推）。

---

## 2026-09-14（续三）— 清理 30 个开发期一次性脚本 + 新增常驻 seed 同步工具

### Removed
- **删除 `backend/` 根目录 30 个开发期一次性脚本 + 4 个配套数据 JSON**（用户 2026-09-14 拍板「留 1 个 sync 工具，其余全删」）：
  - 验收冒烟/e2e（5）：`_p101_smoke.py`、`_p91_smoke.py`、`_p91_e2e_check.py`、`_p92_smoke.py`、`_p92_e2e_check.py`
  - 内容修复（8）：`fix_deferred_failed_reviews_20260914.py`、`fix_l41_l48_dup_20260911.py`、`fix_l6_dup_20260911.py`、`fix_level4_20260909.py`、`fix_level4_20260909_round2.py`、`fix_level4_objective_20260909.py`、`fix_level56_20260910.py`、`fix_level7_20260911.py`
  - patch（4）/ rebalance（3）/ rewrite（4）/ preview（2）/ sync（4，含 `sync_quiz_seed_all_20260914.py`，能力已迁入新工具）
  - 数据 JSON：`l2_distractors_20260914.json`、`l3_distractors_20260914.json`、`l2l3_distractors_patch_20260914.json`、`l5_distractors_20260911.json`
  - 本地 scratch（未跟踪）：`_quiz_dump.json`、`_p6b_e2e_check.py`、`_l4/_l567_narrative_preview.html`
  - **理由**：逐个 grep 确认**无任何一个被 `app/` 引用** → 删除对运行时零影响。且 `fix_level4_20260909.py` 等**无 `--apply` 保护**、参数一对即 `commit()`，`sync_*` 会重写 seed —— 留着即「误跑改库 / 回退题库」的敞口，与被删的旧 seeder 同类风险。被删文件均在 `HEAD` 中，可经 git 历史找回。

### Added
- **`backend/sync_seed.py`** —— 常驻「真库 → 播种文件」同步 + 漂移检查工具（由 `sync_quiz_seed_all_20260914.py` + `sync_seed_all_20260910.py` 等价能力合并提升）：
  - `python sync_seed.py` → **dry-run**：只报告 `drift / orphan / db_only`，退出码 1 表示检测到漂移
  - `python sync_seed.py --apply` → 写入，先自动备份为 `*.bak_before_sync_<时间戳>`
  - 覆盖 `course_seed.json`（按 slug 对齐 `objective / description / content`）与 `quiz_seed.json`（按 lesson_slug + 归一化 prompt 对齐 `options / correct_index`），幂等

### Fixed
- **`course_seed.json` 的一处 L5 漂移（新工具首次运行即抓到）**：`l5-what-is-shuffle` 的 `content.explanation` 在 seed 中是**旧版**（含绝对化定义「就叫 Shuffle」+ 第 7 行重复定义「空中飞货 = Shuffle = …」），而 DB 已是修复版（不提前定义、用「往往意味着」的去绝对化措辞 + 定义收口到第 7 行）。→ 与当初 `quiz_seed.json` 漏同步**同源**（L5 修复只改了 DB）。已 `--apply` 同步；现 course / quiz 双零漂移。

### Changed
- **`.gitignore` 放宽两条规则**（消除漏网 + 防复发）：
  - `*.bak_before_*` → **`*.bak*`**（原先漏挡 `*.bak_l3review` 这类命名，会让备份出现在 `git status` 里）
  - 逐个列举的 scratch 文件名 → **`backend/_*`**（backend 根目录任何 `_` 前缀临时文件一律不入库）

### 验证
- 冷库重建（临时目录副本 + 空 DB → `init_db()`）：`levels=8 / lessons=66 / quizzes=660`；与生产库**逐课逐题零差异**（lesson content 0 不一致 / quiz 0 不一致 / 仅重建有 0 / 仅生产有 0）。
- `import app.main` 正常（12 routes）；真库未被写入（lessons 66 / quizzes 660 / `quiz_answer_log` 245 不变）。

### 状态
- **未 commit / 未 push**（用户验收后推送）。

---

## 2026-09-14（续四）— Level 3 JOIN 旧口径修复 + 全库叠词清理

用户询问「L2/L3 旧口径技术债影响大不大」，逐条评估后决定：只修其中唯一一处**真事实错误**，其余保留。

### Fixed
- **L3 `l3-joins-intro`「JOIN 必触发 Shuffle」**：JOIN 的实际策略包含 **Broadcast Hash Join（小表广播，大表侧不产生 ShuffleExchange）**，写成「必 Shuffle」是事实错误——学习者会据此错过最常见的维表 join 优化。且《心智模型与比喻边界案例库》§4 早在 **2026-09-09** 就更正为「JOIN 未必 Shuffle」，课文一直未跟进（同源技术债）。共改 **7 处**：
  - `objective`：「并知道 JOIN 必触发 Shuffle…」→「…通常要按连接键重分区（Shuffle）…」
  - `explanation` 边界①：「JOIN 必触发 Shuffle…」→「JOIN 通常要一次 Shuffle…；但若其中一侧是小表，Spark 可走广播连接免掉这次 Shuffle（Level 6 展开）」
  - `key_points[2]`：「JOIN 必触发 Shuffle（按 key 重分区），代价大」→「JOIN 通常要 Shuffle…」
  - `common_mistakes[2].why`：「必 Shuffle，大表 JOIN 是大成本。」→「通常要 Shuffle…」
  - `q307` 解析、`q314` 正确项文本 + 解析
  - **`correct_index` 全部未动**（q307 仍为 3、q314 仍为 2），判分与薄弱题派生零影响。

### Fixed（叠词）
- **全库「同一段文字连续写了两遍」共 6 处**：系 2026-09-09 ~ 09-11 各轮批量替换脚本遗留（当时只扫单课，未做全库复扫）：
  - `l5-repartition-coalesce`（141 字）、`l6-join-strategies-overview`（148 字）、`l6-shuffle-hash-join`（192 字 + 138 字，同课两处）、`l6-how-spark-chooses`（48 字）、`l6-join-data-skew`（231 字）
  - 判定用「周期重复」：仅当 `s[i:i+d] == s[j:j+d]`（d = j−i）时删第二遍；`l5-what-is-partition` 里 `maxPartitionBytes` 的远距离复述等**合法重复被自动跳过**。

### Changed
- **`backend/sync_seed.py` 补齐 `explanation` 同步**：此前只同步 `options` / `correct_index`，而 `_seed_quizzes()` 播种时**会读 `explanation`** → 只改 DB 的解析在清库重建后会丢失（与 L5 `quiz_seed.json` 漏同步同类隐患）。补齐后 dry-run 显示历史 explanation 零漂移，属防御性修复。

### 验证
- 冷库重建（副本 app 目录 + 空 DB → `init_db()`）：`lessons=66 / quizzes=660`，与生产库**逐课逐题零差异**（lesson 0 / quiz 0）。
- 全库扫描：`U+FFFD` 0 处；「必 Shuffle」残留 3 处**均为正确用法**（`repartition` 确实必 Shuffle；另两处在「别背死某算子必 Shuffle」的教育语境）；「唯一」15 处全为术语或限定语境的正确用法。
- 真库改动经 `sync_seed.py --apply` 同步（`course_seed.json` 6 课 + `quiz_seed.json` 2 题）；复跑 dry-run 双零漂移。

### 状态
- 已推送：`811caa5`（fast-forward `c04e956..811caa5`，5 文件 +59 −17）。按发布规则属小改动 → 只 commit + push，**不打 tag**。

---

## 2026-09-16 — 首页 Final UI Refinement（v1.2 基线 · P0 进度环竖排 + 跨文件类名冲突 + 层级压缩）

> 定位：**纯 UI refinement**。首页整体布局、信息架构、视觉方向沿用既有结论，本次只修已确认的缺陷与视觉权重问题。
> **未动**：路由、API、数据派生逻辑、`更多` 折叠交互、淡紫 / 蓝色视觉语言、任何新增功能或新颜色体系。

### Fixed
- **P0 · 顶部进度环 `73%` 竖排**（根因：`index.css` 里 `.progress-ring { transform: rotate(-90deg) }` 把整个 `<svg>` 连同环心的 `<text>` 一起转了 90°，文字于是变成自下而上的竖排）。
  - 改为**只旋转弧**：两个 `<circle>` 各加 `transform="rotate(-90 cx cy)"`，`<svg>` 不再旋转。弧的起算点仍在 12 点方向，视觉与原先完全一致，但文字保持水平。
  - 环心文字由 `y = size/2 + 4` 改为 `y = size/2` + `dominantBaseline="central"`，并用 `textAnchor="middle"` 水平居中 → 实测文字中心与环心偏移 `dx=0px / dy=0px`。
  - 顺带补 `viewBox="0 0 size size"`：此前 420px 以下媒体查询把环 CSS 缩到 48px，而 SVG 无 `viewBox`（用户坐标不缩放）→ 半径 25 的圆在 48×48 视口里会被裁掉右侧和底部。补上后等比缩放，48px 下文字仍为水平（实测盒 23.6×14）。
  - **数据完全没动**：仍读 `progress.percentage`（实测 73%）。
- **P1 · 首页复习卡标题异常过大 + 卡片过高**（根因：**跨文件全局类名冲突**）。`Home.css` 与 `ReviewPage.css` 都定义了裸选择器 `.review-title`；两个文件都是**全局 CSS**（非 CSS Module），Vite 按 import 顺序注入，而 `main.tsx` 里 `ReviewPage` 在 `Home` 之后 → 注入更晚的 `ReviewPage.css` 的 `.review-title { font-size: 26px; margin: 0 0 16px }` 在首页也生效（同特异性、后注入者胜）。结果首页复习卡里的题目标题实际是 **26px + 16px 下边距**，把卡片撑到 **93.8px**。修复：首页侧改名 `.home-review-title` 彻底隔离；标题回到 `--sq-text-h3`（16px / 600）。
  - 同源问题还有一处：`WeakQuestionsPage.css` 末尾残留 `.footer-weak-link`（给首页页脚链接用的），已随页脚删除一并清掉。
- **窄屏闪烁横向滚动条（顺带修）**：`.primary-card.focus-ring::after` 是 `inset:-6px` 的纯装饰层，配合 3s 呼吸动画 `scale(1.0→1.05)`，窄屏时会周期性顶破视口 **1~2px**，导致每 3 秒闪一次横向滚动条（实测 380/400/420px 下 10 次采样中出现 1~2px 溢出，禁用该 `::after` 后 30/30 次均为 0）。修复：`.dashboard-page` 加 `overflow-x: clip`（用 `clip` 而非 `hidden`，不产生滚动容器、不影响纵向滚动），复测三档宽度 30/30 次均为 0，装饰环视觉不受影响。

### Changed
- **P1 · 今日复习卡片轻量压缩**：`.review-item` padding 12px → `10px 12px`，`.review-link` gap 4px → 2px，标题 16px/1.35、`meta` 12px/1.4。
  - 实测卡片高 **93.8px → 62.4px（-33%）**。其中大部分降幅来自**修掉上面那个 26px/16px-margin 的类名泄漏**，不是我硬压 padding；若后续觉得压过头，把标题提到 16→18px 即可，不建议回到 26px。
  - 淡紫色复习视觉语言**完整保留**（`--sq-review-light` #faf5ff 底 + `--sq-review-border` #ddd6fe 描边），信息项一个没减（标题 / Level / 逾期天数 / 去复习）。
  - 视觉层级实测：主课程标题 **28px** > 区块标题 / 题目标题 **16px**，达成「今日学习 ＞ 今日复习」。
- **P1 · 进度摘要：后台表格 → Learning Progress Summary**：
  - 去掉每行 `border-bottom` 的横向分割线（实测三行 `borderTop/Bottom` 全为 `0px`），改为一张**白底摘要卡**（`--sq-card-bg` + 1px `--sq-border` + 16px 圆角 + 极轻阴影）；
  - 每行改为「主指标 + 上下文辅助文字」双行结构（`dt` 内 label / sub，`dd` 为 18px/700 主数值），靠 padding 建立呼吸空间；
  - **数据一增一减都没有**，仍是总进度 / 当前 Level / 最长连续三项。
- **P1 · 「当前 Level」语义歧义修复**：原「当前 Level / `0 / 9` · `0%`」在 hero 已显示「Lesson 1 / 9」的情况下容易被读成自相矛盾（1/9 vs 0/9）或读成整个课程只走完 0/9。现改为：
  - 总进度 → 已完成 48 / 66 课 → **73%**
  - 当前 Level → **Level 6** · 已完成 0 / 9 课 → **0%**（`Level 6` 由 `current_level.title` 前端正则取 `^Level\s*\d+` 短标签，纯展示层派生，**后端零改动**）
  - 最长连续 → 最近学习 2026-09-16 → **5 天**
- **P2 · 删除底部重复快捷入口**：整块 `<footer class="footer-nav">`「查看完整学习路线 → / 🏅 最近解锁 → / 🧠 薄弱题 →」删除。实测 `footer` 元素 0 个、`.footer-*` 0 个；关键入口计数现为 学习路线 `/map` = 1、薄弱题 `/wrong-questions` = 1（`/badges` 出现 7 次 = 1 个「查看全部」+ 6 个徽章磁贴，符合既定行为）。
- **P2 · 薄弱题改为「今日复习」之后的轻量独立入口**：展开区区块顺序实测为
  `review-section → weak-section → progress-section → map-section → badge-section`。
  - 规格：688×60px，白底 + 1px 描边，无大面积彩色背景、无巨大标题、无大按钮、无统计、无游戏化装饰。左 🧠 + 「薄弱题 / 回顾答错的题目，主动强化」，右「复习错题 ›」。
  - 与「今日复习」**保持独立入口不合并**：前者是 SRS 到期任务（系统主动提醒），后者是用户主动强化。
- **P2 · 「更多」按钮**：折叠逻辑与语义**零改动**（仍由 `aria-expanded` + `hidden` 控制，默认收起）；仅做视觉一致性检查，并补一条纯 CSS 的展开态 chevron 旋转（`[aria-expanded="true"] .toggle-icon { transform: rotate(90deg) }`），未改任何 JS 交互。
- **P2 · 最近解锁 Badge**：维持默认 `slice(0, 6)`，实测 6 个，标题栏「🏅 最近解锁 / 查看全部 →」不变。

### 验收（实测，非仅「代码能跑」）
- 用 CDP（headless Chrome 152）在真实页面上做前后对照测量，BEFORE 状态通过注入旧样式在原页面上复现，避免两套环境不可比。
- 进度环：BEFORE `svg.transform = matrix(0,-1,1,0,0,0)`（= rotate(-90deg)）、文字盒 **16×25.9（高＞宽 = 竖排）** → AFTER `svg.transform = none`、`circle.transform = rotate(-90 28 28)`、文字盒 **25.9×16（宽＞高 = 水平）**、偏移 `dx=0 dy=0`。
- 复习卡：**93.8 → 62.4px**；泄漏到首页的 `.review-title` 元素数 0。
- 进度摘要：三行分割线 0px；摘要块 170px；文案见上。
- 窄屏：375 / 400px 横向溢出 0；环 48px 显示下文字仍水平。
- 截图存档：`ux_audit/refine-00-ring-before.png`（竖排证据）、`refine-01-review-before.png`（26px 卡片证据）、`refine-02-expanded-1280.png`、`refine-03-collapsed-firstscreen.png`、`refine-04-narrow-400.png`、`refine-05-narrow-375.png`。

### 参考（后续排查同类问题的两个坑）
- **跨文件全局 CSS 类名冲突 —— 已立为铁律 R1**：本项目所有 `.css` 都是全局注入，裸类名会互相覆盖，且**只在「同名 + 同特异性 + 后注入」时才发生**，单看某个文件完全看不出问题。本次全库复查：裸类名冲突除已修的 2 例（`.review-title`、`.footer-weak-link`）外**另有 0 例**；另发现 **10 处「复合选择器跨文件同名」**（`.para` `.ok` `.correct` `.wrong` `.is-active` `.muted` `.back-link` `.retry` `.btn-ghost` `.btn-primary`）经逐条核查作用域均被父级限定，**判为良性**，清单与理由见 `frontend/src/pages/README.md` 附录。
  - **铁律全文**：`frontend/src/pages/README.md`（含 2 起事故档案、修法、良性清单）
  - **可执行护栏**：`frontend/scripts/check-css-namespace.mjs` → `cd frontend && npm run check:css`（违规 exit 1；`--all` 附观察项）
  - **规则一句话**：选择器**完全等于** `.foo` → 违规；含空格 / 第二个类 / 元素名 → 作用域已限定，通常良性。新写页面样式一律加页面前缀（`.home-` / `.review-` / `.quiz-` / `.practice-`）。
  - 同步落在：`README.md` 醒目警告块、`CURRENT_STATE.md`「关键约定与坑位」首条 + 顶部「版本与必读」、`index.css` 顶部注释横幅、`frontend/src/pages/README.md`。
- **本地 CDP 截图：`/json/new` + page 端点在本机 Chrome 152 下命令无响应**（`Page.navigate` / `Runtime.evaluate` 全部超时，但事件仍能收到）。改用 browser 端点 + `Target.createTarget` + `Target.attachToTarget({flatten:true})` + 每条命令带 `sessionId` 后全部正常，脚本见 `ux_audit/verify_home_refine.mjs`。
- **vite dev server 会「假死」**：本次遇到一个已跑 6 天的 vite 进程，端口仍 `LISTENING` 但任何 HTTP 请求（python / Chrome 均）无响应 → 前端全站不可用且报错像是「网络问题」。**排查顺序应是先直接打一下 6001 根路径**，无响应就重启 vite，不要先怀疑代理或浏览器。（本次已重启，顺带用 `node node_modules/vite/bin/vite.js` 直起，绕开沙箱里 npm 不可用的问题。）

### 状态
- 🟢 **已完成并验收 · 已推送 `main` · 已打 annotated tag `v1.2`** —— **Spark Quest 第一个稳定 UI + 工程规范基线**。`tsc --noEmit` 通过（exit 0）；`npm run check:css` 通过（跨文件裸类名冲突 **0**）。
- 已知但**本次未动**（供用户决定）：hero 的「Lesson 1 / 9」表示「当前在第几课」，与摘要的「已完成 0 / 9 课」是两个量（前者含未完成的当前课）。两者现已各自写明口径，不再互相矛盾，但若想彻底统一，可把 hero 改成「第 1 课 / 共 9 课」。

## 2026-09-17 — 修复：「比喻的边界」被压成一坨 + 加粗跨行内 code 泄漏字面 `**`（RichText 两处渲染缺陷）

**触发**：用户学到 Level 5 第一课（`l5-what-is-partition`）发现「⚠️ 比喻的边界（很重要）：」整块**没有换行**，
①②③ 全部杂糅成一坨加粗橙字，读起来极难受；并注意到 L3 起多个 Level 都用 ①②③ 当编号。

### Fixed

**缺陷① ⚠️ 警示块「标题吞掉正文」（影响 44 课）**

- **根因**：`RichText` 按 `text.split(/\n\n+/)` 切段，「段」是**空行分隔**的块。而数据里 L3–L7 把「⚠️ 标题」与
  「①②③ 条目」写成**同一个段**（彼此只隔一个 `\n`）；`⚠️` 分支却把**整段**（`⚠️ 标题\n① …\n② …\n③ …`）交给
  `renderInline`。`renderInline` 只处理反引号 code 与 `**`，**不认 ①②③**，而 HTML 在 `white-space: normal` 下把
  `\n` **折叠成空格** → 结果是**一个** `<p class="rich-warning-title">` 装着全部内容。
  `renderBlock` 里 ①②③ → `<ol>` 的逻辑一直都在、也一直正确，只是这 44 个块**永远走不到**它。
- **不是数据错**：数据的换行是齐的，是**渲染层**把它吃掉了。L1/L2（及 L3 的 `l3-comprehensive`）正常，
  只是因为它们恰好把 `⚠️ 标题` 单独成段（后接空行）→ 进了原有的 body 收集循环。
- **实测证据**（Chrome CDP 真实 DOM）：修复前 `.rich-warning` 的直接子元素**只有 1 个**（`p.rich-warning-title`，
  高 **134px** / **398 字** / 内含 **3 个 ①**），块内 `<ol>` 条目数 **0**；修复后标题高 **20px**、块内 `<ol>` **3 项**。
  对照 L2 `l2-what-is-dataframe` 一直是 3 个子元素（title 20px + `p.para` + `ol` 3 项）。
- **修法（只动 `frontend/src/components/RichText.tsx`）**：`⚠️` 分支改为「**首行 = 标题**」，其余内容交给新增的
  `renderWarnBody()`（内部复用 `renderBlock`；对「多行纯文本」另补逐行拆段兜底，避免再次被 `\n` 折叠）。
  另加保护：**标题行本身若也混入 ≥2 个 ①②③（标题与条目连写在同一行），从第一个编号处切开** ——
  顺带覆盖「条目与标题同行、连 `\n` 都没有」的写法。
- **覆盖面**：全库 **58 个 ⚠️ 块**（L1×3 / L2×10 / L3×9 / L4×9 / L5×9 / L6×9 / L7×9），修复前 **44 个畸形**
  （L3 8 个 + L4/L5/L6/L7 各 9 个），修复后 **0**。
- **预期内的副作用**：卡片变高（L5 首课 166px → 309.6px）—— 变高是「可读」的代价，且观感与 L1/L2 既有样式一致。
  ①②③ 会被 `<ol>` 渲染成 `1. 2. 3.`（作者当编号用的 ① 被列表标记消费掉），与全库既有 **31 处** ①②③ 段落的
  渲染方式统一；若想保留 ① 外观需另定规则（本次不做）。

**缺陷② 「加粗套行内 code」整对拆散（影响 3 处）**

- **根因**：旧 `renderInline` 先按反引号切出 code 段，再在**每段内部**用 `/\*\*[^*]+\*\*/` 找加粗
  （`[^*]+` 明确排除 `*`）。于是「`**` + 文字 + 行内 code + `**`」被 code 从中间切开，两个 `**` 各自孤立、配不成对
  → **字面 `**` 泄漏进正文 + 加粗失效**。
- **修法**：重写为**单次左→右扫描** —— 遇到反引号吃到下一个反引号（code），遇到 `**` 吃到下一个 `**`
  （加粗内容**递归**再过一遍 `renderInline`）。**谁先出现谁先闭合**，天然支持「加粗套行内 code」嵌套；
  code 内的 `*(N)` 也不会再被误判成定界符。
- **覆盖**：L4 `l4-explain-api`、L4 `l4-wholestage-codegen`、L5 `l5-shuffle-trigger-operators`。
  修复后全库可见文本里未消费的 `**`：**6 → 0**。

### 验证

- **确定性回归（不用浏览器）**：Python 分别复刻「旧 / 新解析器」，对全库 **66 课 × 4 个走 RichText 的字段
  （`explanation`/`review`/`problem`/`preview`，共 264 个）** 逐一比对规范化输出 → **只有 4 处差异且全为预期修复**
  （3 处去掉泄漏的 `**` 并恢复加粗；1 处 `*<b>(N)</b>` → `<b>*(N)</b>`，可见文本不变、只是 `*` 移进加粗内）。
  **无任何非预期副作用**。
- **真实 DOM 全量扫描**：`ux_audit/verify_richtext.mjs` 遍历 66 课、命中 **264 个 `.rich-text` 容器** →
  缺陷① 警告块异常 **0 / 58**；缺陷② 残留未消费 `**` **0 课**；「加粗内含行内 code」正确渲染 **3 处**（原 0）。
  另报 9 个含**合法**裸 `*` 的文本节点（`local[*]` ×2 / `SELECT *` / `age * 2` / `price*0.9` / `*(N)` 等），
  已人工确认非 markdown 残留。
- `tsc --noEmit` 通过（exit 0）。

### 未动

- `course_seed.json` / `spark_quest.db` / `quiz_seed.json` **一行未改**（修复 100% 在渲染层）→
  **无需跑 `sync_seed.py` 对账**；路由 / API / 数据派生 / 交互逻辑均未触碰。

### 状态

- 已推送：`4c1ed99`（修复本体；其后仓库更名 `4ad67e6` / 文档同步 `1878e98`）。按发布规则属小改动 → 只 commit + push，**不打 tag**。

---

## 2026-09-18 — Level 6 题库偏置修复（「正确项恒最长」）+ Sort-Merge Join「两次 Shuffle」表述澄清

用户在学 L6 时提出两个问题：① `l6-sort-merge-join` 反复暗示「两次 shuffle」，容易被读成「搬两遍 / 两轮串行」；② L6 全库 Quiz 的**正确答案就是最长的那个选项**，且正确项尾部带 `（）` 解释，等于把答案标出来。

### Fixed（题库：正确项最长偏置）

- **L6（level_id=7，9 课）90 题全部重排选项**：修复前 **87/90（97%）** 的正确项是 4 个选项里唯一的**最长项**，且大量题目的正确项尾部挂 `（…）` 解释性从句（如 `两侧按 key 分区并排序（两个 Exchange）+ 归并扫描配对`）——「挑最长 + 挑带括号的那句」几乎等于送分。
- 做法：**缩短正确项为精简短语**（细节留给 `explanation`）+ **把干扰项加长到同量级**，去掉正确项的括号解释。参照物是 L6 已有的正确范式（如 q529「不一定：一侧足够小时可广播，大表完全不 Shuffle」）。
- 结果（复检脚本实测）：

  | 指标 | 修复前 | 修复后 |
  |---|---|---|
  | 正确项为**唯一最长** | 87 / 90 | **0 / 91** |
  | 正确项与最长项之差（中位数） | 大 | **3 字符**（肉眼不可辨） |
  | 最长项出现位置分布 | — | 0/1/2/3 = **26 / 27 / 21 / 17**（无位置规律）|
  | 正确项尾部带解释性括号 | 19 | **0**（仅剩 `hint('broadcast')` 这类**代码**括号）|

- **`correct_index` 有调整**：`quiz_answer_log.selected_index / correct_index` 是**只写不读**的历史快照列（判分与薄弱题派生均实时读 `quizzes.correct_index`），因此重排选项 + 改答案下标**不影响既有作答记录、不影响派生结果**。

### Fixed（内容：SMJ 的 Shuffle 表述）

- **先纠正一个技术前提**：Sort-Merge Join **确实是两次 shuffle**（A、B 两侧各插入一个 `Exchange`，各自按 key 重分区 + 分区内排序），这是 Spark 的字面事实（Spark UI 两笔 shuffle 写、DAG 两个 ShuffleMapStage；datadriven.io 直接概括为 *Two Shuffles, Two Sorts, One Merge*）。原文「两边都 Shuffle」**不是事实错误**。
- 但「两次 Shuffle」若被读成「**同一份数据搬两遍**」或「**先搬完 A 再搬 B 的两轮串行**」就是误解——这才是要消除的。改法是把话说准，而不是改成「只有一次」（那反而会写错）：
  - `explanation` 边界①：`① **两边都 Shuffle**：两本簿子都得重排一遍再飞过去，代价是双份的` → `① **两侧都要重分布**：…计划上表现为两侧各有一个 Exchange。贵在「两份数据都在飞」（网络量约 A+B）；注意不是「同一份数据搬两遍」，也不是先 A 后 B 的两轮串行。`
  - `objective` / `description` / `key_points`[0][2] / `preview` / `problem` / `examples[0].note` / 内部步骤 5：统一改为「两侧各（一个 Exchange / 重排一次）」「网络量约 A+B」。
  - `common_mistakes` **新增第 4 条**：「把『两侧都要重排』读成『同一份数据被搬了两遍』。」
  - `l6-join-strategies-overview` 的 `→ **两边都 Shuffle**。` → `→ **两侧都要按 key 重排**。`
- **新增 1 道 Quiz（`q705`）**把该认知做成题目，让学习者自己作答得出结论：

  > **计划里 SMJ 出现两个 Exchange，正确的理解是？**  → 正确项：`两侧各按 key 重排一次，双份数据量`；
  > 干扰项：`同一份数据被原样搬了两遍，纯属重复的劳动` / `两轮串行：先搬完 A 再搬 B` / `其中一个其实是多余的，应该消掉`

  题目本身也按新标准做了长度对齐，不构成新的「最长即正确」信号。

### Fixed（两个「清库重建会丢」的隐患）

- **`_seed_quizzes()` 漏播种 `quizzes.dimension`**：`quiz_seed.json` 里**有** `dimension`，但播种函数没读它，而 `migrate.add_quiz_dimension_column()` 只建列**不回填** → **冷库重建后 661 题维度全部为 `NULL`**，`_sample_quiz_questions` 的「维度多样性」Phase 6.1 逻辑**静默退化为纯随机**（已在副本库上反证：撤掉该行后冷库 `dimension IS NULL = 661/661`）。与 2026-09-14 修掉的 `explanation` 漏同步**同类**，已补齐。
- **`sync_seed.py` 同步字段补 `dimension`**：否则「只改 DB 的维度标签」在清库重建后同样会丢；补上后与播种函数覆盖面一致。

### 验证

- **冷库重建**（副本 `app/` + 空 DB → `init_db()`，真库零改动）：`levels=8 / lessons=66 / quizzes=661 / badges=20`，**lesson 差异 0 / quiz 差异 0**（本轮比对**含 `dimension`**）。临时目录已清理。
- 全库扫描：`U+FFFD` **0**；L6 危险绝对化词 41 处**逐条核对全为正确用法**（否定语境如「不一定：小表可广播」「计划变省也不等于一定更快」，或故意设置的错误干扰项）；L6 课文「叠词」命中 2 处均为**代码块内两行 `spark.read.parquet('big_fact_` 的合法重复**，非缺陷。
- 真库改动经 `sync_seed.py --apply` 同步（`course_seed.json` 2 课 + `quiz_seed.json` 89 题 + 新增 1 题）；复跑 dry-run **双零漂移**（`drift total = 0`）。

### 状态

- 见本文件末尾「状态」区块（本条目写入时未 push）。

---

## 2026-09-23 — Weak Questions UI 派生分组（待重练 / 已恢复）

> **定位：Weak Questions UI 增加「待重练 / 已恢复」派生分组，复用现有 `last_attempt_correct`，不增加持久化状态。**
> 小范围 UX + 展示语义修正，不是新增状态系统：不新增表 / 字段 / 接口，不改 `quiz_answer_log` 的事实层性质，不改 `practice` 端点行为，不引入「连续 N 次正确 / 跨天 / 冷却期」等规则。
> 起因：真实库 17 道历史错题里有 16 道最近一次已答对（94%），却与仍然答错的题在同一个列表里同等呈现 —— 主列表被已恢复的题占满。

### Added
- **`frontend/src/pages/weakGrouping.ts`**：纯函数 `groupWeakQuestions()`，按 `last_attempt_correct` 二分出 `active` / `recovered`。零副作用、不改入参、不丢题、组内保持后端顺序。刻意用 `.ts` 而非 `.tsx`（node type stripping 不支持 JSX），从而能被 node 内置测试运行器直接加载。
- **`frontend/scripts/weak-grouping.test.ts` + `npm run test:weak-grouping`**：项目首个可重复运行的测试入口（`node --test`，**零新依赖**）。放 `scripts/` 而非 `src/`：tsconfig 是 `include:["src"]` + `strict`，测试文件若进 `src/` 会因 `import { test } from "node:test"` 缺 `@types/node` 让 `tsc -b` 直接失败。
- **「待重练」独立空态**：`🎉 待重练已清空 / 历史错题都已恢复，可以继续学习了。` —— 待重练为 0 是正常产品状态（当前数据即 1 道，答对后归 0），不能让用户看到空白区域以为页面坏了。
- **`ux_audit/verify_weak_groups.mjs`**：薄弱题分组的 CDP 验收脚本（真实数据渲染 + 折叠展开 + 视觉权重 + 窄屏 + 只发 GET 核对）。

### Changed
- **薄弱题页由单列表改为两组派生视图**（`WeakQuestionsPage.tsx`）：
  - 「🔴 待重练」= `last_attempt_correct === false`，**默认展开**，页面主要内容
  - 「✓ 已恢复」= `last_attempt_correct === true`，**默认折叠**，但标题栏**数量常显**（`✓ 已恢复 16 道 · 展开`）—— 用户要能看出「这些题不是消失了，而是已恢复」
  - 副标题：`共 N 道 · 待重练 X · 已恢复 Y`
- **卡片文案按组别分化**：待重练卡「最近一次答错 · 相对时间」；已恢复卡「错误 N 次 · 最近一次答对 · 相对时间」。**`wrong_count` 等历史统计照旧显示，恢复不清零、不洗历史。**
- **已恢复卡明显降权**：复合选择器 `.weak-card.is-recovered`（不违反铁律 R1 —— 含第二个类，作用域已限定）→ 灰底 + 题干字重 600→500 + 按钮由实心蓝改描边款。
- **新增 `.weak-group*` 命名空间类**（`.weak-group` / `.weak-group-head` / `.weak-group-toggle` / `.weak-group-mark-*` / `.weak-group-count` / `.weak-group-action` / `.weak-group-empty*` / `.weak-ok`），全部带 `weak-` 前缀、仅本文件定义；新样式走 `--sq-*` 变量（顺带对深色模式友好）。
- **删掉旧「最近一次已做对」绿标**：该标签落在「待重练」组内恒为 false，属死代码；同时**同批删除** `.weak-recovered` 样式规则（铁律 R1 教训：元素删了，样式必须同批删干净）。
- **后端仅补注释，零行为变更**：`routers/weak_questions.py`（module docstring + `list_weak_questions()` docstring）、`schemas.py`（`last_attempt_correct` 字段注释）、`types.ts`（同字段注释）—— 写死该字段**只做 UI 展示分类**，**不是** graduation state，列表成员不变，不得演化为 status 列 / 过滤参数 / 第二套 Mastery。
- 未新增 `total_attempts` 字段（本模块本就没有此字段，本次不引入）。

### Fixed
- **「已经答对的题为什么还霸占主要错题列表」**：`last_attempt_correct` 此前只用来渲染一个绿标、不参与任何归属；现在真正参与 UI 分类（`false → 待重练`，`true → 已恢复`），页面首屏不再被已恢复的题占据。

### Architecture
- **「已恢复」是读时派生 UI 分类，不是状态**：不写库、不新增持久化字段、不与 Mastery / SRS / badge / streak 互相写入；没有「标记为已掌握 / 移出错题本 / 删除 / dismiss」等任何手动操作 —— 唯一让题目进入「已恢复」的方式是**实际把最近一次答对**。
- **准入规则不变**：仍是「历史上至少答错过一次」（ever wrong），列表成员不因答对而改变；服务端**不做**分组，响应形态不变。

### 验证
- **前端纯逻辑**：`node --test scripts/weak-grouping.test.ts` **7/7 通过**（含真实分布 17 = 待重练 1 + 已恢复 16、纯函数不修改入参、全恢复时待重练为空）。
- **后端派生语义 6 用例**（副本库 + 副本 app 目录 → `init_db()`，**真库零改动**，mtime 未变）**10/10 通过**：错→错 = 待重练；错→对 = 已恢复；错→错→对 = 已恢复且 `wrong_count=2`；只答对 = 不入列；`practice` 对 = 已恢复（`last_source=practice`）且**端点零副作用**（`lesson_mastery` / `user_stats` / `study_days` / `user_badges` / `lessons` 全等）；`review` 对 = 已恢复（`last_source=review`）；历史统计保留 + 日志仍 append-only（零删除）；列表 total = 待重练 + 已恢复 对账一致。
- **真实数据渲染**（CDP，`ux_audit/verify_weak_groups.mjs`）：`共 17 道 · 待重练 1 · 已恢复 16`；折叠态已恢复渲染 0 张、展开 16 张、折叠后标题栏仍含数量；待重练卡白底/字重 600/实心按钮 vs 已恢复卡 `rgb(249,250,251)`/字重 500/描边按钮；400 / 375px 无横向溢出；页面全程只发 `GET /api/weak-questions`（真库零写入）。
- `tsc -b` 零错误；`check:css` 通过（11 个 css，无跨文件裸类名冲突），`--all` 观察项与改造前完全一致（未引入新的复合同名）。

### 状态
- 见 `CURRENT_STATE.md`「Phase 10.1 实现记录」的 **UI 派生分组（2026-09-23 增量）** 小节。本条写入时未 commit / push。

---

## 模板（后续阶段直接复制此结构，改日期与内容）

## YYYY-MM-DD — <阶段标题>

### Added
-

### Changed
-

### Fixed
-

### Architecture
-


## 2026-11-06 · 学习体验修理第一步

- L2「DataFrame 是什么」（slug `l2-what-is-dataframe`，当前 ID 12）接入三步互动样板：预测筛选/选列结果 → 查看 Schema → 换条件验证行筛选与重复行保留。
- 针对每个错误选项给出解释，正确后补充概念，完成展示具体学习收获。旧课文折叠为可展开参考，笔记、课后测验、后端掌握和解锁规则保留。
- 互动只在当前浏览器 localStorage 保存步骤，版本键 `spark-quest:df-intro:v1`；不写掌握、错题或打卡记录，不声称运行 Spark 或验证独立编程能力。
- 修复入门 PySpark 关系题（当前题 ID 60）：选项与解析直接回答 Python 官方接口关系。DB/seed 同步，保留题 ID、correct_index=3，保留历史答题记录。既有历史得分不重新评分。
- `backend/repair_intro_question.py` 默认 dry-run，`--apply` 先创建 DB 和 seed 备份，重复执行无变化。历史进度/笔记/打卡/统计/徽章/答题日志的前后摘要一致。
- 验证：TypeScript + Vite 构建、CSS 命名空间；浏览器 fixture 验证错误反馈、重试、三步完成、刷新续学、重置、测验链接及 320/390/768/1440px 无溢出；未做真实 Spark 运行。截图：工作区 `ux_audit/learning-repair/dataframe-390.png`。
- 内容依据：https://spark.apache.org/docs/3.5.6/sql-getting-started.html 。当前为单课样板，未完成全章重构、全库干扰项修理或变式错题调度。


## 2026-11-07 · L2 互动课程扩展（第 2–4 课）

- 新增创建 DataFrame（ID 13）、Schema 与数据类型（14）、检视数据（15）互动课程；每课四个任务，共 12 个。连续订单情境，含单选推理与多空配对补全；每个选项有专门反馈。
- 内容集中在 `frontend/src/content/l2Journeys.ts`，通用渲染器 `components/LessonJourney.tsx`；第一节原有样板保留。
- 按课程 slug/version 独立保存本设备进度和曾用错误反馈的步骤；刷新恢复、重置、回看；完成展示具体收获与辅助记录。未引入后端掌握状态或新的打卡判据。
- 原文完整保留并默认折叠；针对读取惰性边界、CSV Schema/FAILFAST、printSchema/show/列下标在课程中显示醒目勘误。笔记、测验与解锁规则保留。
- 8 道正式测验的错误口径已在 DB/seed 同步纠正。`backend/repair_l2_quizzes.py` 支持 dry-run/--apply，使用 `app/l2_quiz_corrections.json`；修改前 DB 与 seed 备份，保留题 ID、prompt、correct_index；重复执行无变化。历史进度、笔记、打卡、徽章、统计、答题日志摘要一致；历史分数不重算。
- 依据 Spark 3.5.6 官方 API/CSV 文档（source 链接在课程数据内）；不是对所有 Spark 版本的兼容性认证。
- 验证：TypeScript/Vite 构建、CSS 命名检查；运行 `python frontend/scripts/check-l2-journeys.py`（需先在 frontend 启动 4173 端口的 preview；使用本地 Python Playwright）。检查三课 12 个任务的错误/正确分支、补全、刷新续学、重置、测验链接、320/390/768/1440px 布局、存储拒绝降级、第一节回归。浏览器 API 使用数据库派生 fixture，未运行真实 Spark。截图 `ux_audit/learning-repair/l2-*-390.png`。
- 仍待推进：L2 第 5–10 课、真正的异题补救与延迟复习、章末独立挑战。当前错误反馈后调整原题，不声称已实现自适应异题调度。


## 2026-11-07 · L2 互动课程扩展（第 5–8 课）

- 新增 `l2-select-filter`（16）、`l2-withcolumn`（17）、`l2-sort-dedup`（18）、`l2-groupby-agg`（19），每课四步，共 16 个任务。L2 当前 8/10 课已接入互动（首课旧样板 + 七课通用渲染器）。
- 新内容集中在 `frontend/src/content/l2ProcessingJourneys.ts`，订单情境覆盖多条件、NULL 筛选、常量/计算列、when 空值分支、查询不可变性、Top N、按键去重无保留保证、并列排序、count/avg 空值语义及多指标报表。每个选项附专门反馈，保留原文、笔记和原有正式测验流程。
- 对保留原文的技术表述加勘误：Column == 合法；filter 可减输出行而未必减分区；dropDuplicates 不承诺第一条/最大/最新；排序不是所有相同键必须汇聚一处。
- 正式题库修复 4 道排序/去重题，DB/seed 同步，备份在 backend 下。两道改写题干以去掉“保留首次”和排序去重能保证最大值的错误前提；四题均保留题 ID 与正确答案索引。迁移工具增加显式 new_prompt 支持，重复执行 pending=0，历史记录摘要一致，旧分数不重算。
- 验证：构建、CSS 命名空间；`frontend/scripts/check-l2-journeys.py` 扩展为七课共 28 个任务的完整浏览器回归（API fixture），含错误分支、双空补全、续学、重置、测验链接、320/390/768/1440px，以及首课回归与存储拒绝降级。截图在 `ux_audit/learning-repair/`。
- 额外运行 `python backend/check_l2_processing.py`，本机 PySpark 4.2.0 实际执行合成订单查询，筛选、NULL、计算列/常量列、when、不可变查询、排序/去重键、计数/平均值、每用户最大值断言通过，退出码 0。Spark Windows 退出阶段另有 Access denied 输出；不影响已完成断言，未做 Spark 3.5 运行兼容验证。未读取学习数据库。
- 内容口径参考 Spark 3.5.6 官方 filter/withColumn/dropDuplicates/NULL 文档，链接在互动课数据中。
- 后续：第 9 课数据写出、第 10 课独立综合任务，异题补救与延迟复习尚待实现。


## 2026-11-07 · L2 互动课程收尾（第 9–10 课）

- `l2-write-data`（ID 20）新增四步交付练习：输出目录、追加重跑、partitionBy 与小文件、读回验收。
- `l2-comprehensive`（21）新增六步章末挑战，使用新订单 o201–o206，六行原始输入、四行有效订单。预期 south=(1,240,0.24)、north=(2,200,0.20)、east=(1,90,0.09)，总额 530。依次完成类型约定、清洗、聚合、派生列、写入策略和逐地区验收。
- L2 全部十课现在均有互动内容（共 41 步；首课三步，八课各四步，综合课六步）。原文、笔记与正式测验规则保留；互动不自动认证独立编程能力。
- 新数据在 `frontend/src/content/l2DeliveryJourneys.ts`；通用组件支持 project 下载区，综合课首步给任务文件，完成后可展开参考实现下载。
- 可下载任务：`frontend/public/practice/l2/orders.csv`、`starter.py`、`README.txt`、`solution.py`。参考实现每次创建新的隔离输出目录，不覆盖既有文件；包含逐地区 cnt/total/total_k、字段、行数和总额断言；仅对已知三行小报表 collect。参考代码不读取应用数据库，不自动写入学习进度。
- 对旧文补充勘误：目录分区不保证少文件、show 抽样不是全量证明、读取准备可能提前发生、写出不承诺读回顺序、聚合后计算 total_k 避免无效中间列。
- 同步修复 6 道正式题库题目或解析；本轮修改前备份 DB/seed，题 ID/正确索引与历史记录保持。所有累计 18 个 L2 修复项的 DB/seed 一致、选项无重复、迁移重复执行无变化。
- 验证：TypeScript/Vite、CSS；浏览器九课 38 步完整回归加首课样板回归（API fixture），含六步续学、重试、下载资源、参考展开、重置、测验链接、320/390/768/1440px。下载脚本语法检查通过。
- 真实 PySpark 4.2.0：综合任务 CSV 读取、有效行数、聚合、排名、逐地区断言通过；刻意破坏 north cnt 的结果被成功拦截。`backend/check_l2_delivery.py` 完整运行在 Parquet 写出阶段失败：Windows Hadoop native `NativeIO$Windows.access0` 缺失；未通过写出/读回与 mode 实验，不能宣称全程通过。可使用 --query-only 明确跳过文件系统写出验证。尚未完成 Spark 3.5 实机验证。
- 后续不宜直接机械扩展全库：先使用 L2 完整学习路径，评估疲劳、原题重试的记忆效应和章末本地任务完成情况，再设计异题补救/延迟复习与 L3。


## 2026-11-07 · 互动课程骨架整理

- 十课 41 步统一由 `frontend/src/components/LessonJourney.tsx` 渲染，移除首课专用组件与旧 TS 内容副本；首课订单表保留。内容改为 `src/content/lessons/<slug>.json`，通用 `content/journeys.ts` 自动注册。
- 明确 lesson version、task/field/option ID、correctOptionId、knowledgeIds，下载项目资源改为内容配置；播放器不再硬编码 L2 文件路径。现有知识点标签仍为课程级，不等于已实现误区调度。
- 互动进度由步骤下标改为步骤 ID；记录每次作答的选项、正确项快照、结果、时间与轮次。重练开启新轮次并保留旧回答；摘要区分首次答对、反馈后完成和旧版记录缺失。存储失败提供提示。本轮仍为浏览器本地记录，无后端同步，无成绩/解锁/打卡/SRS 改动。
- 旧首课数字进度与其余九课 step/helped 进度通过固定 legacyTaskIds 快照兼容；不编造旧答题事实。不同内容版本独立存储并保留旧版。
- 结束页集中正式测验、已掌握课程的复习/下一课、路线入口和项目参考文件；原文与笔记折叠可展开；互动页移除重复的底部测验区和旧预告。非互动课程保留旧流程。
- 新增 `check-journey-content.mjs`：校验身份唯一性、答案引用、逐项反馈、表格结构、下载文件和内容发布版本。`releases.json` 保存版本摘要，已发布同版本内容变更被阻止。npm build 自动先检查内容。编写/版本迁移规则见 `frontend/src/content/AUTHORING.md`。
- 验证：六组进度测试覆盖旧版部分/完成进度、首课迁移、步骤与选项重排、版本隔离、回答快照/重练、损坏与拒绝存储；TypeScript/Vite、内容与 CSS 检查通过。浏览器十课完整回归通过（API fixture），并额外验证旧完成状态迁入、未知首次记录、稳定 ID 回答存储/刷新、available/mastered/locked 结束页分支。结束页截图 `ux_audit/learning-repair/unified-finish-390.png`。
- 内容保持原有 41 步，未修改后端数据库或正式题库。异题补救/延迟复习、课后测验重新编排、跨设备记录仍待后续。


## 2026-11-07 · 难点互动样板：L5 Shuffle / L7 调优方法论

- 新增 `frontend/src/content/lessons/l5-what-is-shuffle.json`（现有 ID 42，v1，五步）与 `l7-what-is-tuning.json`（58，v1，六步），自动注册到通用播放器；无章节专用组件或分支。原文/笔记仍保留，正式解锁不变。
- L5：局部不等于全局 → 指定路由下同键汇合（明确为教学路由，不假装真实哈希）→ 局部预聚合减量 → 明确哈希 Exchange 线索 → local Shuffle 与热点键风险。数据表新增可选 caption，非订单章节可使用自己的表题。
- L7：证据不足不盲调 → 阶段/任务分布 → 拖尾假设验证 → 针对整数求和试验 groupByKey/mapValues(sum) 与 reduceByKey → 以输出正确性和同条件多次测量验收 → 新症状下重新诊断。所有耗时与字节量明确为教学构造，不是运行监控、性能基准或提速承诺。
- 修正两个样板现有正式测验的 15 道答案/解析，三道同时改写有误前提的题干（Stage 推断、拖尾结论、非瓶颈改动）。保留题目 ID/答案位置与历史记录，DB/seed 备份、对齐、重复执行无变化。使用 `repair_l2_quizzes.py --corrections app/hard_sample_quiz_corrections.json --apply`；默认 L2 修复文件行为保留。
- 内容检查与版本基线更新为 12 课/52 步；构建、CSS、六组记录单测通过。通用浏览器脚本覆盖全部 12 课，含两样板 11 步的错误/正确分支、补全、刷新、结束与重练、测验链接和 320/390/768/1440px。测试 API 使用 fixture，历史学习数据未写入。
- `backend/check_hard_lesson_examples.py` 在本机 PySpark 4.2.0 实跑：两输入分区、明确教学路由、局部和/全局和、local 运行下 ShuffledRDD 依赖、整数求和改写等价性、丢掉 north 被判不等价。断言通过，退出码 0；Windows 退出阶段仍有 Access denied 输出。没有做计时比较、Spark 3.5 运行兼容认证或真实集群倾斜诊断。
- 截图：`ux_audit/learning-repair/l5-what-is-shuffle-390.png`、`l7-what-is-tuning-390.png`。技术依据为各课 source 指向的 Spark 3.5.6 官方 RDD/UI 文档，补充核对性能调优文档。
- 目前仅验证两课内容与通用骨架可承载；用户理解程度、延迟迁移能力与长期学习动力仍需实际使用。未全面改造 L5/L7，其余章节原题库的长度提示等质量问题仍需逐课处理。


## 2026-11-07 · Shuffle 单段融合试验

- 范围仅为 `l5-what-is-shuffle` 的 `route-partial-keys` 步骤：做题前按需借原文理解，错误后给出重读入口，答对后把路由推演连回原理，再可选阅读原心智模型和补充比喻边界。
- 新 `JourneyReading` 直接从 API 返回的本课 explanation 按明确边界提取原段落；互动 JSON 不复制原文。片段下保留“打开本课完整原文”按钮，直接展开并定位现有参考区。后台正文与正式测验未改。
- 泛化内容字段为 task.reading（id/title/startMarker/endMarker/connection/boundary）。构建检查关联的 course_seed 原段落是否存在且起点唯一；运行时 API 文本若漂移，给出查完整原文的降级入口，不显示错段落。
- Shuffle 内容版本升为 v2，步骤与选项 ID 不变。按既定版本隔离规则，v1 本机记录保留，v2 独立记录；不是丢失或覆盖旧记录。
- 验证：构建、CSS、七组单测；浏览器验证原文片段逐字一致、开合不影响答题记录、完整参考区跳转、错/对两种上下文、320/390/768/1440px、原文标记缺失降级；使用 fixture API，无学习数据库写入。截图 `ux_audit/learning-repair/shuffle-reading-390.png`。
- 本轮没有对全课逐段关联、没有重新分配十道旧题、没有引入异题补救。用户先体验一段，再判断推广方式。


## 2026-11-07 · Shuffle 整课原文融合（v3）

- `l5-what-is-shuffle` 五步全部配置 task.reading：局部/全局关联人话理解；按键路由关联心智模型；局部预聚合关联内部执行；Exchange 关联正式定义；local/热点键关联原文中的通常代价与例外。
- 各步均提供题前可选解释、错误后的重读入口、正确后的“把判断连成原理”和可选原文/适用边界。原文直接从 API explanation 提取，五个范围不重叠，不新增正文副本，不修改 DB 或正式题库。
- 通用 reading 增加可选 sectionTitle，按真实引用内容显示人话理解/心智模型/技术定义等标题；边界统一叫“这段解释的适用边界”，不把技术定义误标成比喻。
- 内容版本升 v3，原五步和选项 ID 保留；依既定版本隔离规则 v1/v2 记录留存，v3 使用独立记录。未重算任何正式成绩。
- 内容检查、构建、CSS、七组单测通过；新增 `frontend/scripts/check-shuffle-readings.py` 对五步逐一验证：引用与原文显示内容一致（仅剥除 Markdown 标记）、阅读开合不改学习记录、错误/正确两种辅助入口、回完整原文、320/390/768/1440px、完成页/测验链接/刷新恢复。使用实际 DB 派生只读 API fixture，无用户数据库写入。
- 截图 `ux_audit/learning-repair/shuffle-integrated-1-390.png` 至 `shuffle-integrated-5-390.png`。本轮仅 Shuffle 整课融合，其他课程保持原状，旧十道题用途划分/异题补救尚未开展。


## 2026-11-07 · 项目检查点推送及 L2 打磨第一批

- 仅在 `spark-quest-app` 嵌套仓库提交 `c235dc4` 并经用户指定的一次性代理 127.0.0.1:7890 推送至 `MasonWest/Spark-Quest` 的 origin/main；外层工作区未提交。未改 Git 全局代理。数据库/备份/缓存不推送；PWA 四个 PNG 产品图标增加精确 gitignore 例外并纳入检查点。
- 推送后开始 L2：前三课（DataFrame 是什么、创建、Schema）共 11 步补齐 reading 关联、概念联系与适用边界；内容版本升 v2，保留稳定步骤/选项 ID 和旧版记录。引用仍从原 API 正文提取，没有另一份全文副本。
- 新增 `L2_POLISH_PLAN.md`，明确原文融合、正式题库质量、课末新情境检验、补救/复习、关键示例验证是不同验收项。其余七课阅读融合及整章题库分工未完成，不标记整个 L2 完成。
- 修正进度单测对内容永远停在 v1 的假设：旧迁移测试明确测试 v1；版本隔离使用当前版本+1。构建、CSS、七组单测通过；`frontend/scripts/check-linked-readings.py` 验证前三课所有 11 个阅读入口、原文显示内容（忽略 Markdown 列表版式）、答对后收束/边界、完整参考跳转、四种宽度和刷新完成页，全部通过；使用只读 API fixture，未写学习 DB。
- 这批打磨保留在本地，未混入已经推送的 c235dc4 检查点。


## 2026-11-07 · L2 剩余七课原文融合打磨

- 为检视、筛选、列加工、排序去重、聚合、写出、综合挑战共 30 步补齐 reading：从当前实例结果回到对应原文，再明确概念和适用边界。至此 L2 十课 41 步均已融合，原正文与笔记保留。
- 配文重点：printSchema 与数据求值、show 展示量和上游成本、Column 条件与 NULL、lit/col/when、不可变查询、去重不保证首次/最大、排序并列规则、count/avg 空值语义、分区目录不等于单文件、写入模式与指标验收。综合挑战强调与旧 sales.csv 案例区分，按当前新数据推导，不照搬原文结果。
- reading 增加可选 caution，在引用包含已知错误的原文（本轮为去重“首次出现”）之前先纠正口径；原文仍按原样引用，避免悄悄改写历史讲义。构建检查增加该可选字段的非空校验。
- 七课版本均升 v2，任务与选项 ID 保持，旧 v1 本机记录保留；正式题库、后台成绩、解锁/SRS 与用户数据库均未改。本轮仍是本地工作，未追加推送到检查点之后。
- 验证：内容/原文定位检查、TypeScript/Vite 构建、CSS、七组记录/提取单测通过；扩展 check-linked-readings.py，七课 30 步逐一验证错误分支、重试、阅读不改答题记录、原文显示内容、概念收束、caution、原文跳转、完成与续学、320/390/768/1440px。API 使用现有 DB 的只读 fixture；原文比对忽略 Markdown/列表格式标记。
- 截图 `ux_audit/learning-repair/l2-*-reading-390.png`。L2_POLISH_PLAN.md 已将十课融合标记完成，仍保留正式题库用途、课末新情境检验/延迟复习和 Windows Parquet 写出验证待办；不把本轮标记为整个 L2 所有质量项全部验收。


## 2026-11-07 · L2 正式题库分工与独立检验接入

- 旧 L2 100 题建立逐题用途/结构风险清单 `backend/app/l2_legacy_question_audit.json`，保留审查前原始快照；人读报告 `backend/L2_QUESTION_AUDIT.md`。用途建议为课中解释、误区素材、复习或应用检验候选，不代表原题全部获得技术认证。原题不再进入新的 L2 GET 测验/复习抽题，但 ID 与历史/错题重练入口保留。
- 新增独立题源 `backend/app/l2_reviewed_bank.json` 共 100 题：每课 5 assessment、3 review、2 remediation。来自 50 个目标模板的两套材料，含概念回忆和字段/数值/需求变式，不宣称 100 个独立新概念。每课测验五题、复习另五题；补救题目前进入复习回合，没有实时按错项分支插题。
- 新题用稳定 key 与 knowledge_id；当前存库以 lesson slug + 不变题干定位，修改已安装新题需显式迁移。`app/l2_question_bank.py` 为追加式补齐与用途路由，应用初始化补齐缺失题；其他章节抽样策略保持，L2 两种题组顺序打乱。L2 检验要求五个不同 ID，学习 4/5、复习 5/5、粘性掌握和课程级 SRS 保持。
- `install_l2_reviewed_bank.py` 默认 dry-run，apply 先备份并校验已有题行与历史记录未变。本次开发服务热重载先由初始化追加了 100 题，因此手动安装器运行时 pending/inserted=0，随后备份是追加后的状态，不冒称插入前备份。
- 另经备份修正旧题 6 处事实：创建时的工作、nullable 保证、分组的分布要求、默认聚合列名可引用、write 属性 vs 实际保存动作。使用 `l2_legacy_fact_corrections_v2.json`，保留正确答案位置、ID 与历史作答；历史分数不重算。
- 当前原题源 661 + 新策划题 100 = DB 761；L2 旧 100 题只为兼容与素材保留。sync_seed.py 增加独立策划题检查，漂移时拒绝无意覆盖，原题同步不再把这 100 题误报 db_only；dry-run course/quiz/reviewed 全部 drift=0。
- 新题答案位置 A/B/C/D 各 25，正确项唯一最长 28/100；旧题审查前快照为 51/100。指标只能帮助发现形式线索，不能替代学习效果验证。
- 验证：backend/test_l2_bank.py 七组隔离内存库测试通过，覆盖回滚/幂等、十课 5+5 分离、返回不泄答案、五题约束、4/5 与 5/5、粘性掌握、旧五题在途提交兼容、其他章节未改变、作者源可复现。前端构建/CSS/七组进度测试通过。
- 浏览器检查十课测验/复习共 20 页面，320/390/768px、选答与按钮启用；使用只读 DB 派生的模拟 API，不提交用户成绩。新长代码选项暴露 320px 溢出，已在 QuizPage.css 修正换行/min-width。截图 `ux_audit/learning-repair/l2-new-assessment-390.png`。
- backend/check_l2_assessment_examples.py 在 PySpark 4.2.0 实跑两套材料的 OR/NULL、when、全空聚合、count/avg、带 seq 的 limit/sort、并列排序、清洗分组和 DataFrameWriter 属性，断言通过。未实跑实际文件写入模式，也未认证 Spark 3.5 运行兼容；Windows 退出时仍有 Access denied 输出。真实写出环境与长期教学有效性仍待验证。
- 本批未推送；原文融合之外，正式题库第一轮分工已完成，实时异题补救、扩大每课多套检验、标准原文归档与教学效果评估仍是后续工作。


## 2026-11-08 · 检查点推送与课中补救试点

- 按用户要求先将此前 L2 原文融合、独立题库与用途路由提交为 351535a，经一次性 127.0.0.1:7890 代理推送 origin/main。仅 spark-quest-app，未改全局代理。
- 推送后新增五个课中异题补救：NULL 筛选、when 空值分支、去重保留规则、count 的计数对象、avg 分母。四课升 v3，主任务/选项 ID 不变，旧版本记录保留且不自动迁移。每误区一道变式，可选进入；不是所有 41 步都已有补救。
- 播放器增加通用 remediation 内容协议与组件；答对变式仍返回原题清空选择，不自动完成、不改成绩/解锁/SRS。事件记录 activity、remediationId、knowledgeId，原题作答次数排除补救。刷新回原题，已提交事件保留。与后台 20 道 remediation 用途题分开，未做多套轮换或错误选项路由。
- 验证：内容/版本检查、TypeScript/Vite 构建、CSS 与八组进度单测通过；新浏览器脚本 check-inline-remediation.py 覆盖五个场景的错答重试、补救正确后原题不跳过、事件区分、刷新保留和 320/390/768/1440px。API 使用只读 DB fixture，不提交正式成绩；脚本不作为 Spark 技术结论的独立证据。截图 ux_audit/learning-repair/l2-inline-remediation-390.png。
- 补救试点为推送后的本地工作，未追加推送；细粒度延迟验证、真实教学效果、标准原文整理和写出环境仍需继续。


## 2026-11-08 · 隔天验证试点

- 在五个课中补救知识点之后补一层延迟判断，另编五道新材料，未改变原任务内容/版本。首页与课末可见到期入口，课末说明 24 小时后在原浏览器继续。
- 当前版原步骤已完成且有原题正确记录时，按最近原题/补救作答时间等待满 24 小时。验证先判断后讲解，一次提交后不可现场反复作答；正确材料收起，错误至少再等 24 小时。重复材料存在记忆线索，不能将再次答对当成全新独立能力证据。
- 新增 delayedProgress.ts 纯调度逻辑，独立本机事件记录；不写学习 DB、正式成绩、课程解锁、连续学习天数或课程级 SRS。刷新未答继续，提交时重算队列防陈旧页面/重复提交；读写失败提示且不伪造完成。
- delayedChecks.json 为独立版本题源，纳入构建结构/关联/不同材料/发布摘要检查。没有通知、跨设备记录同步或多套轮换；只覆盖五个试点知识点。
- 验证：内容检查、TypeScript/Vite 构建、CSS、11 项进度/调度单测通过。check-delayed-checks.py 在受控浏览器时钟下覆盖五题、到期首页入口、解释仅提交后显示、刷新续答、24h 重试、原记录不变、陈旧页面拦截、存储拒绝及 320/390/768/1440px；check-inline-remediation.py 五个课中场景回归通过。浏览器仅使用本机 fixture，不提交正式成绩，未执行 Spark。截图 ux_audit/learning-repair/l2-delayed-check-390.png。
- 本轮仍保留本地，未追加推送。下一步宜按实际错误扩充补救/延迟材料、整理标准讲义与原文归档；扩大章节前仍需验证教学效果和文件写出环境。


## 2026-11-08 · L2 标准讲解与历史原文分离

- 新增 standardGuides.json，为 L2 十课 41 个主步骤分别编写标准说明和使用边界；题中阅读与整课讲义共用一份内容，含 Spark 3.5.7 官方来源入口。核对了官方入门、CSV、NULL、dropDuplicates 与文件保存说明；不宣称历史内容或所有运行环境均已认证。
- 默认阅读展示标准讲解；历史片段仍可按旧标记从 API 正文提取对照，完整旧正文/示例/要点进入历史原文折叠区，勘误随历史区显示。未写数据库、未覆盖原始讲义，笔记 API 与独立入口保留。Shuffle/L7 继续原有阅读流程。
- 标准讲义有独立版本/发布摘要与构建覆盖检查，主题目与答案未改，因此不增加课中题目版本、不迁移或清空已有进度。此前四课因补救升级至 v3 的策略保持。
- 验证：内容检查、TypeScript/Vite、CSS、11 项记录/调度单测通过；十课 41 步逐一检查标准节文本、历史片段、两种全文跳转、边界与错误/正确分支、阅读不记作答、320/390/768/1440px；12 课 52 步互动回归、五个补救、五个隔天验证均通过。只读 API/本机 fixture，不提交正式成绩，未运行 Spark 文件写出。
- 本批提交范围包含前两轮未推送的课中补救与隔天验证，以及本轮标准讲解整理；仅 spark-quest-app 嵌套仓库。后续重点为按真实误区扩充材料、实作验收与教学效果验证。


## 2026-11-08 · L2 综合课改为独立毕业任务

- 综合课默认显示独立实作工作台，原六步互动改为折叠的可选准备练习，保留原题目版本、稳定 ID、旧进度与原文/笔记。任务以新订单数据交付可重跑地区日报，不再用已展示过答案的六行材料充当独立检验。
- 工作台四阶段：读交付约定、预测/计划、运行验收、复盘对照；三级提示按需展开，参考下载另行展开。可手动保存独立本机草稿，未将草稿、展开提示或自述结果计作课程通过。原正式测验、掌握/解锁和 SRS 保持；页面实作预计时间改为 45 分钟，后台原课程元数据未迁移。
- capstones.json 独立版本/任务 ID；下载包包含新 CSV、三个职责函数 starter、独立 verify、运行说明和 reference。构建检查锁定配置与下载资产摘要，禁止同版本静默修改。原 practice/l2 材料保持可用。
- verify 用 Python 标准库独立推导期望，检查输出列/类型、逐地区笔数/金额/千元值、变换数值、额外重复/空值/新地区、空输入和全无效输入。默认另实际读 CSV、写 Parquet/读回、同批重跑；只查询模式输出 PARTIAL，失败不伪造完整 PASS。JSON 是本地开发验收证据，不是认证或正式成绩，输出使用一次性临时目录。
- 实跑 PySpark 4.2.0：五组查询通过；七项反向检查拒绝漏去重、总额正确但地区错、单位错、重复报表、类型错、硬编码旧结果及读取阶段提前清洗。默认完整运行已通过 CSV 读取，但 Parquet 提交触发 NativeIO$Windows.access0 缺失，files=ENVIRONMENT_ERROR，未宣称读回/重跑通过。Windows 停止进程仍输出 Access denied。
- 前端构建、内容/资产发布检查、CSS、11 项单测通过。浏览器独立任务检查默认无选题、提示分层、参考隐藏、草稿保存/恢复与保存拒绝、下载、旧笔记、测验入口、320/390/768/1440px；综合课六步阅读与全部 12 课/52 步互动回归通过。使用只读 lesson fixture，不提交正式成绩。截图 ux_audit/learning-repair/l2-graduation-390.png；实跑记录在同目录 l2-graduation-*-result.json。
- 后续仍需补可用文件写出环境与真实学习反馈，不据此标记所有 L2 质量项验收完成。


## 2026-11-08 · L3 整章批量改造

- 新增 SQL 九课 38 个实例推理步骤，含两步双字段补全；每步完整选项反馈、概念收束、标准说明与边界，原文/旧示例/笔记保留历史入口。新课 v1 无虚构的旧互动记录。每课一个关键误区补救与隔天验证，共各 9；全播放器现 21 课/90 步、14 补救与 14 延迟题。
- 标准讲解/延迟题/毕业配置分别升独立 v2，L2 旧条目及任务/答案 ID 保持。加入显式 author-l3-content.py 和 --check，统一验证覆盖 L2/L3。官方 3.5.7 来源核对 SQL 查询/命令、视图应用范围、NULL、JOIN 和数据源等；运行验证使用本机 PySpark 4.2.0，未等同宣称 3.5 实跑。
- L3 综合课默认独立 SQL 实作，另附新订单、三个职责函数的 starter、Python 独立期望验收器、运行说明和 reference；可选六步准备练习、三级提示、草稿与延后对照。澄清至少 200 的组门槛与正金额明细门槛，不强塞 JOIN/UDF。工作台复用 L2，不产生正式成绩认证。
- 定点修正旧 L3 90 题中的 34 项题意/事实/解析，保留题目 ID、正确位置和历史分数；没有重新划分抽题用途。题源与实际数据库同步，初次应用前已备份，history_unchanged=true；实际备份路径 spark_quest.db.bak_l2_20261108_004018_429188（复用原修复器的命名）。
- 新 repair_l3_quizzes.py 支持拉取新题源后升级旧库，识别已知旧/新状态，先锁定并备份，未知漂移拒绝覆盖。旧库配旧/新题源两种迁移实测通过；历史/非目标题/ID/答案位置保持、幂等与拒绝漂移均通过。专用修复 dry-run pending=0，sync_seed 全部漂移=0，数据库仍为 761 题。原始 DB/备份不提交。
- 前端构建/CSS/内容发布摘要/11 项单测通过。全部 21 课90步互动回归，L3九课38步阅读/原文对照/跳转，14补救/14隔天场景，两章毕业工作台，320/390/768/1440px 通过；只读 API/浏览器 fixture，不提交正式成绩。七组现有后端题库测试及两组 L3 迁移脚本验证通过。
- 真 Spark 示例通过视图重绑定/会话范围/DDL、SELECT/标识符/DISTINCT、NULL、HAVING、JOIN 行数、内置/CASE/COALESCE/注册的 NULL 安全 UDF。SQL 毕业任务七组查询通过，六种错误结果被拒绝；完整模式通过 CSV 读取，Parquet 提交仍触发 NativeIO$Windows.access0，files=ENVIRONMENT_ERROR；未认证读回/重跑或所有 Python/Java/Spark 组合。停止 Spark 时仍出现 Access denied。
- README 更正记录位置：正式成绩/笔记在 DB，互动/补救/隔天/草稿在当前浏览器，复制 DB 不包含后者。L3_ROLLOUT_PLAN.md 列本批完成与剩余用途重编、真实教学效果和文件环境待办。


## 2026-11-09 · L3–L6 夜间整章批次

- L4/L5/L6显式编写27课115步（保留原Shuffle5步，净新增26课110步），标准讲解、原文对照、选项反馈、误区补救和隔天目标齐备。L3原38步保留。全应用47课200步，补救/延迟各41；四章36课153步。Shuffle v3→v4保留主ID与原题，旧版本记录未删；新版本独立记录。
- L3–L6新策划题360，180组目标两份材料，每课5assessment与3review+2remediation分池；L2池不变。新增通用路由/初始化/备份安装器，五题提交约束扩展到策划课；旧五题在途提交和历史ID兼容，4/5学习、5/5复习及SRS保持。库1121题；sync_seed漂移0。
- 00:33改动前备份spark_quest.db.bak_l3l6_before_20261109_003351；初次安装backup为spark_quest.db.bak_l3l6_bank_20261109_005054_094922，插入360。发布前对158个新题选项做带备份精简，正确位置保持。最终原761题逐行相同、全部非题目表哈希相同，未提交用户成绩。新题正确位置各90，唯一最长160/360，不当作教学有效性认证。
- 三个新独立毕业包：L4结果/相对实际计划，L5 Pair RDD总量/分区不变性，L6 LEFT补维/唯一键冲突拒绝/实际连接计划。各带JSON数据、starter、独立verify、README、参考；实跑自动检查PASS，诊断文字manual_review=required。它们不是Parquet任务，原L2/L3 NativeIO问题未解决，未混称通过。
- 课程改为按slug动态载入，新增可校验轻量journeyIndex供首页/延迟调度，保留记录键与任务ID。取消过时课程请求防路由竞态。主构建脚本532.28KB→329.15KB（gzip214.38→124.37），只代表构建体积。
- 验证：构建/内容/资产/索引/CSS通过，12项前端单测；47课200步互动、27课115步阅读、41补救/41延迟、3新毕业工作台、懒加载/竞态、92测验/复习页通过，320/390/768/1440px；API使用只读fixture。后端7组旧题库+5组新题库测试通过；真Spark示例与错误报告拒绝通过，三个新lab参考实跑PASS。实跑PySpark4.2.0，不冒充3.5运行认证，退出仍出现Access denied输出。
- README/编写约定和当前事实摘要更新；NIGHTLY_L3_L6_RESULTS.md为早上查看的完整成果与入口清单。按用户要求不发起额外批准请求，保存本地提交，网络推送留待之后。


## 2026-11-09 — L1/L7 补齐与七章统一复核

### Added
- L1 六课 26 步，L7 九课 40 步；调优样板六步保留，净增 14 课/60 步。全 L1–L7 共61课/260步，补救与隔天目标各56个。
- L1 词频、L7 等价内置表达式调优独立任务，下载骨架/参考/自包含验收器，保存真实证据，诊断人工待审。
- L1/L7 150 道分用途正式题与五项内存隔离测试，通用题库安装入口与只读备份对比工具。

### Changed
- 标准讲解、延迟题库与毕业配置升独立 v4；L7 原样板升 v2，只扩展辅助讲解/补救，保留旧版本本机记录。
- L1–L7 正式题池隔离，原1271题中旧1121行逐项未变；学习状态、历史、笔记等非题目表不变。
- 浏览器回归扩大至全部61课、122测验/复习页和七个独立任务入口，报告见 FINAL_CURRICULUM_REVIEW.md。

### Fixed
- 新标准明确列式缓存仍可扫描必要列、AVG拆分需合并sum/count、Driver/JVM/Python容量分开、配置开启不代表AQE具体改写生效。
- L2/L3 Windows NativeIO/Parquet限制保留为未验项，不用其他章节PASS冒充完整通过。本批未推送。

- 统一复核追加：工具包字节摘要存在CRLF/LF跨平台漂移风险，固定下载资产LF并新增构建检查，毕业配置升v5重录摘要；标准讲解/延迟仍v4。


## 2026-11-09 — 概念递进与统一内存教学修补

### Added
- 新增14个明确的铺垫步骤：RDD分份、键值卡片/合并、事实/维度、计划路线、哈希/广播及六步统一内存推演。全61课共274步。
- L7内存课4→10步，新增回收变式与隔天验证，补救/延迟各57个。真实Spark检查空闲借用与存储不逐出活跃执行，容量题另作模型计算。

### Changed
- 修订26课，补首次术语、跨章前置和后续深入提示。三个作者接入显式修补层；标准讲解/延迟库v5，毕业配置不改。
- 旧主步骤的ID、相对顺序、题干、代码、答案身份和56个旧延迟材料逐项保留。互动修订独立计进度，旧本机记录保留；数据库正式题库、掌握和评分未改。
- 全61课、26课讲解关联、57补救/延迟的浏览器回归通过。后续缓存生命周期操作与SQL窗口训练缺口见 CONCEPT_PROGRESSION_REPAIR.md。本轮未推送。


## 2026-11-09 — 接入窗口与缓存生命周期正式课

### Added
- L3聚合后插入窗口/每组Top N/最新整行；L7内存模型后插入缓存物化/复用/观察/释放。各8步，共新增16步与20道分用途正式题，两组补救/延迟。
- 全课程68课，互动63课/290步，题库1291行，补救/延迟各59个。新课进入正常解锁链，相邻五课引导同步修订。
- 已有库备份后事务升级与冷库完整种子，保留旧ID/内容/1271题及学习表，只调整后续顺序。新增五项隔离升级测试与真实Spark窗口/缓存示例验证。

### Changed
- 标准讲解/延迟库v6，毕业配置不变。各作者共用新增课衔接层，保留原延迟材料。已掌握下游课程保留，未开始下游遵循新前置。
- 报告见 EXTENSION_LESSONS.md；未更改七个毕业任务，Windows Parquet限制继续保留。本轮未推送。


## 2026-11-09 — 学习历程成就与展示升级

### Added
- 8枚永久历程成就、4枚独立本机练习成就，8种SVG图标。支持纠错、复习覆盖、允许中断的规律学习与回归。
- 徽章墙分类/筛选/进度/入口、首页单一近期目标、本机达成收录提示；秘密成就保持隐藏。

### Changed
- quiz/review作答日志在同一事务发奖前flush，让本次纠错立即参与判定；practice约定保持。
- 旧徽章与获奖时间保留，其他学习表逐行不变。29项后端回归、12项前端进度单测、构建/CSS及浏览器检查通过。详见ACHIEVEMENTS_UPGRADE.md。本轮未推送。


## 2026-11-10 · L0统一互动与验证体验

### Added
- 五课25步互动、9个填写字段、5组补救/隔天材料、50道分用途正式题。
- 第一个CSV程序的输入、代码骨架、参考实现和四份独立输入验证器。

### Changed
- 复用现有播放器、标准讲解、原文与笔记入口，L0→L1正常衔接。
- 内容守卫覆盖全部68课，标准讲解v9、隔天库v7；L1–L7原内容保持。
- 原1526题及所有非题目表逐行保留，新题追加；当前实库1576题、冷库1341题。
- 38项后端、15项前端、浏览器全链与真实Spark正反验证通过。详见L0_REBUILD.md。


## 2026-11-10 · 长原文阅读返回操作

### Changed
- 历史原文与标准讲解共用ReadingPanel，阅读中固定可见收起/返回操作，文末也提供出口。
- 返回当前题目时收起长文、定位题目标题并恢复焦点，保留填写内容和补救状态；毕业章节可重新展开准备练习。
- 长参数支持折行，避免窄屏WebKit横向溢出；代码块保留内部滚动。

### Validation
- 构建、68课内容守卫、CSS与15项进度/答案单测通过。
- Chromium及WebKit在320/390/768/1440宽度验证普通课、长内存课、毕业课与补救返回，无浏览器错误或真实API写请求。
- 只读核实68课680道当前分用途题均已安装；课末5题与另5题复习池覆盖全课。精修程度仍有章节差别，正式Quiz仍是单选，历史错题保留旧身份。
- 浏览器复现需启动4173预览，运行python frontend/scripts/check-reading-panels.py（WebKit加--webkit）。
