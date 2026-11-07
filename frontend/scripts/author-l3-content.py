"""Explicit L3 teaching material. Run --check to compare, otherwise write JSON.
No database writes, grades, or positional legacy-progress migration.
"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1] / 'src/content'
GUIDES = json.loads((ROOT / 'standardGuides.json').read_text(encoding='utf-8'))
DELAYED = json.loads((ROOT / 'delayedChecks.json').read_text(encoding='utf-8'))
BASE = 'https://spark.apache.org/docs/3.5.7/'
lessons = {}


def lesson(slug, title, mission, correction, source='sql-getting-started.html'):
    global current
    current = dict(slug=slug, version=1, title=title, mission=mission, correction=correction,
                   source=BASE + source, next='先用自己的话解释本课的判断，再进入下一课。正式测验沿用原有规则。', tasks=[])
    lessons[slug] = current
    GUIDES['lessons'][slug] = dict(title=title, sections=[], sources=[dict(title='Spark 3.5.7 官方说明', url=BASE + source)])


def task(key, title, intro, code, prompt, choices, correct, feedback, insight, concept, body, boundary, extra=None):
    identifier = f"{current['slug']}/{key}"
    field = dict(id='answer', label='你的判断', correctOptionId=f'o{correct}',
                 options=[dict(id=f'o{i}', text=text, feedback=feedback[i]) for i, text in enumerate(choices)])
    t = dict(id=identifier, knowledgeIds=[concept], title=title, intro=intro, code=code, prompt=prompt,
             fields=[field], insight=insight, ability=title,
             reading=dict(id=identifier + '/reading', title=title, sectionTitle='先用人话理解',
                          startMarker='【先用人话理解】', endMarker='【一个直观的心智模型】',
                          connection=insight, boundary=boundary,
                          caution='这是保留的旧讲义，部分简化口径已经修订。请以当前标准讲解为准；旧示例的输入与本题不一定相同。'))
    if extra:
        t['fields'].append(dict(id='detail', label=extra[0], correctOptionId=f'x{extra[2]}',
                                options=[dict(id=f'x{i}', text=text, feedback=extra[3][i]) for i, text in enumerate(extra[1])]))
    current['tasks'].append(t)
    GUIDES['lessons'][current['slug']]['sections'].append(dict(id=identifier, title=title, body=body, boundary=boundary))
    return t


def remedy(t, key, title, code, prompt, choices, correct, feedback, insight):
    t['remediation'] = dict(id=f"{current['slug']}/{key}", knowledgeId=t['knowledgeIds'][0], title=title,
                           intro='换一份材料，只验证刚才这个判断。', code=code, prompt=prompt,
                           field=dict(id='answer', label='变式判断', correctOptionId=f'r{correct}',
                                      options=[dict(id=f'r{i}', text=text, feedback=feedback[i]) for i, text in enumerate(choices)]), insight=insight)


def delayed(t, key, title, code, prompt, choices, correct, explanation):
    DELAYED['items'].append(dict(id=f"{current['slug']}/{key}-delayed-v1", slug=current['slug'], taskId=t['id'],
                                knowledgeId=t['knowledgeIds'][0], title=title, code=code, prompt=prompt,
                                options=[dict(id=f'd{i}', text=text) for i, text in enumerate(choices)],
                                correctOptionId=f'd{correct}', explanation=explanation))


DELAYED['items'] = [i for i in DELAYED['items'] if not i['slug'].startswith('l3-')]
lesson('l3-what-is-spark-sql', '给同一批订单换一种提问方式', '用 SQL 完成已经熟悉的订单分析，分清名字、查询结果与执行命令。',
       'SQL 与 API 共享优化体系，但不能保证任意两种写法计划和耗时相同。SELECT 查询与 INSERT/DDL 命令执行时机不同；SQL 也能访问目录表和文件路径，不只临时视图。')
task('name', 'Python 变量还不是 SQL 表名', 'orders 是一个 DataFrame 变量，当前会话还没有注册同名关系。',
     'orders = spark.createDataFrame([(120,)], "amount long")\nspark.sql("SELECT amount FROM orders")', '要让下面的查询找到这批数据，先补哪一步？',
     ['orders.show()', 'orders.createOrReplaceTempView("orders")', '给变量改名叫 table'], 1,
     ['show 只展示行，不登记 SQL 名称。', '对，把当前 DataFrame 注册为 SQL 可解析的关系名。', 'Python 变量名不会自动加入 SQL 目录。'],
     'SQL 通过关系名找到逻辑计划，而不是查找 Python 局部变量。', 'sql.relation-name',
     'SQL 的 FROM 解析关系名。DataFrame 可以注册为会话临时视图；目录表和支持的文件路径查询也是数据入口。', '名字解析成功不等于数据已计算或持久化。')
t = task('result', '查询结果还能继续加工', '视图 orders 已存在，金额分别是 80 和 150。',
     'result = spark.sql("SELECT amount FROM orders WHERE amount > 100")\nresult.withColumn("amount_k", F.col("amount") / 1000.0)', 'result 是什么？',
     ['已经收集到 Python 的列表', '只能打印的字符串', '可继续调用 DataFrame API 的查询结果'], 2,
     ['需要 collect 等操作才收集到 Python；这里没有。', 'SQL 文本是输入，返回值不是文本。', '对，SELECT 返回 DataFrame，可以与 API 组合。'],
     '同一条查询可以先写 SQL，再接 DataFrame API；需要结果时再执行 show、collect 或写出。', 'sql.result-dataframe',
     'spark.sql 的 SELECT 查询返回 DataFrame，可接 select/filter 等 API。通常在 action 请求结果时计算查询数据。', '不要将 SELECT 的惰性查询规律推广到 INSERT、CREATE TABLE 等 SQL 命令。')
remedy(t, 'result-transfer', '换成库存查询', 'stock = spark.sql("SELECT quantity FROM inventory")\nstock.filter(F.col("quantity") > 0)', '第二行能表达什么？',
       ['继续组成一个筛选查询', '给 SQL 字符串删字符', '把库存写到磁盘'], 0,
       ['对，stock 是 DataFrame。', 'stock 不是查询文本。', '没有任何保存操作。'], '返回 DataFrame 让 SQL 和 API 可以衔接。')
delayed(t, 'result', 'SQL 查询返回什么', 'q = spark.sql("SELECT id FROM customers")\nq.limit(2)', '关于 q，哪个判断成立？', ['Python 字典', '可以继续组合查询的 DataFrame', '已落盘的临时表'], 1,
        'SELECT 返回 DataFrame，limit 可以继续组合查询；既没有收集成字典，也没有写成表。')
task('equivalence', '换写法，先核对业务含义', 'orders 已注册，SQL 与 API 都对同一 DataFrame 工作。',
     'a = orders.filter(F.col("amount") > 100).select("amount")\nb = spark.sql("SELECT amount FROM orders WHERE amount > 100")', '能稳妥地得到哪个结论？',
     ['两者表达同一筛选需求', '所有 SQL 都比 API 快', '所有 SQL 与 API 的物理计划必然逐字相同'], 0,
     ['对，先判断语义是否等价。', '写法本身不能保证更快。', '数据源、表达式和配置不同都可能影响计划。'],
     '共享优化器是理解两套接口的桥梁，性能结论仍要看计划与测量。', 'sql.api-equivalence',
     'SQL 与 DataFrame API 都能表达结构化查询，并使用 Spark SQL 的分析与优化机制。语义等价是对照写法的起点。', '共享优化体系不等于任意写法都同计划、同开销。')
task('commands', '看见 sql()，别一概等待 show', '这里只判断执行约定，不在浏览器运行写入。目标表已存在。',
     'spark.sql("SELECT * FROM orders")\nspark.sql("INSERT INTO target SELECT * FROM orders")', '哪句判断更准确？',
     ['两句都必须接 show 才可能写数据', 'SELECT 组成查询；INSERT 是可能在调用时执行的命令', 'INSERT 返回后也绝不可能写入'], 1,
     ['SELECT 与 INSERT 不能套用同一规则。', '对，应区分查询与命令。', '把所有 sql() 都当惰性查询会漏掉写入副作用。'],
     '排查重复写入时，不要因为没有 show 就认定 INSERT 没有执行。', 'sql.command-execution',
     'SparkSession.sql 接受查询与 SQL 命令。SELECT 的 DataFrame 查询与 DDL/DML 命令需要分开理解，不能把所有调用归为无副作用的转换。', '本课不执行写入；实际操作前核对目标、权限和命令语义。')

lesson('l3-temp-views', '让 SQL 找到正确的那批数据', '给订单挂牌，再检查替换、会话和生命周期。',
       '普通临时视图属于创建它的会话；全局临时视图属于当前 Spark 应用，并非跨独立应用/集群永久共享。注册视图不等于复制、缓存或落盘。')
task('register', '把名字牌挂在正确位置', 'clean 是已经筛选后的 DataFrame，SQL 要查询的名字是 daily。',
     'clean = orders.filter(F.col("amount") > 0)\n# 注册后执行 SELECT * FROM daily', '哪一步能把 daily 对准 clean？',
     ['orders.createOrReplaceTempView("daily")', 'clean.createOrReplaceTempView("daily")', 'clean.show()'], 1,
     ['这挂上的是原始 orders，不是 clean。', '对，视图应对应清洗后的查询。', '展示数据不会注册名字。'],
     '注册哪个 DataFrame，SQL 就从哪个逻辑查询出发。', 'view.target', 'createOrReplaceTempView(name) 把 DataFrame 的查询注册为当前会话的临时视图，同名时替换定义。', '它不自动 materialize、cache 或保存文件。')
task('rebind', '变量改名，视图会跟着变吗', '第一次注册时 df 中只有 10。',
     'df.createOrReplaceTempView("v")\ndf = spark.createDataFrame([(99,)], "amount long")\n# 再查 SELECT amount FROM v', 'v 仍指向哪份定义？',
     ['第一次注册的 10', '自动变为 99', '视图被 Python 赋值删除'], 0,
     ['对，Python 变量重绑定没有重新注册视图。', '需要再次注册替换定义。', 'Python 赋值不删除 SQL 视图。'],
     '要更新 v，请对新 DataFrame 再次调用 createOrReplaceTempView。', 'view.rebind', '视图登记的是注册时的查询定义，Python 名称后来重新绑定不会自动替换它。', '这不意味着物化了源数据；底层外部数据的变化仍需按数据源语义理解。')
t = task('session', '另一个会话为何找不到', '应用中的 s1 注册了普通和全局临时视图，s2=s1.newSession()。',
     'df.createOrReplaceTempView("local_orders")\ndf.createOrReplaceGlobalTempView("shared_orders")\ns2 = spark.newSession()', 's2 中应使用哪个名字访问共享定义？',
     ['local_orders', 'shared_orders', 'global_temp.shared_orders'], 2,
     ['普通临时视图不在另一个会话的临时目录里。', '全局临时视图要带 global_temp 数据库前缀。', '对，同一应用中的新会话可访问这个全局临时视图。'],
     'global_temp 的“全局”范围是当前 Spark 应用，不是任意独立程序。', 'view.global-scope',
     '全局临时视图使用 global_temp 名称空间，可被同一 Spark 应用内的会话访问，其生命周期依附该应用。', '不能用它作为跨独立应用的持久共享表。')
remedy(t, 'scope-transfer', '应用已经退出', '应用 A 创建 global_temp.stock 后退出。\n独立启动应用 B。', '应用 B 能仅凭这个名字继续访问 A 的临时视图吗？',
       ['能，global 表示永久', '不能，需要持久数据与目录安排或重新注册', '只要变量同名就能'], 1,
       ['global 不是永久存储。', '对，两个独立应用不共享这种临时视图。', 'Python 变量名也不会恢复目录。'], '区分会话、应用和持久存储的生命周期。')
delayed(t, 'scope', '全局视图的范围', '一个 Spark 应用里：s1 创建 global_temp.metrics；s2=s1.newSession()。', '哪个判断成立？',
        ['s2 可在同一应用中访问 global_temp.metrics', '独立重启程序后这个临时视图永久存在', 's2 必须写 local.metrics'], 0,
        'global_temp 临时视图可以在同一应用内跨会话访问，不是跨应用的永久目录。')
task('persistence', '登记、缓存、保存是三回事', '需求是让第二天独立启动的程序也能读取这批日报。',
     'report.createOrReplaceTempView("daily")', '仅这一行能满足需求吗？',
     ['能，它已经创建 Parquet', '能，它自动缓存并永久保存', '不能，需要持久化数据及相应访问安排'], 2,
     ['没有任何文件保存调用。', '登记视图不等于缓存，更不等于永久存储。', '对，临时名称会失效。'],
     '临时视图服务当前分析，持久交付需要另行写出并约定位置。', 'view.persistence', '登记视图、cache 查询与写出持久数据分别解决命名、复用计算与交付问题。', '不要把 session 内能查询当作下游隔天可用的保证。')

lesson('l3-select-basics', '写一份字段清楚的订单投影', '从列名、常量与单位出发，产出能被下游理解的结果。', '单引号表示字符串，反引号引用标识符。SELECT 输出的别名决定结果字段；DISTINCT 按完整输出列组合去重。', 'sql-ref-syntax-qry-select.html')
t = task('literal', '同样写 amount，意思不同', 'orders 中 amount=120。',
     "SELECT amount, 'amount' AS label FROM orders", '这一行两列分别是什么？',
     ['120 和字符串 amount', '120 和 120', 'amount 和 amount 两个字段名'], 0,
     ['对，单引号内是固定文本。', '第二个表达式不是列引用。', '查询结果包含值，不只是名称。'],
     '读取列值与给所有行放一个标签，是不同的投影表达式。', 'select.literal', 'SQL 中普通标识符引用字段，单引号字符串表示常量；含空格等特殊字符的标识符使用反引号。', '不要把 Python 字符串的外层引号与 SQL 文本内部的引号混淆。')
remedy(t, 'literal-transfer', '标签也叫 city', "-- city 的值是 north\nSELECT city, 'city' AS tag FROM stores", '输出的 tag 是什么？', ['north', '字符串 city', 'NULL'], 1,
       ['north 是第一列的值。', '对，单引号指定常量。', '常量字符串不因字段内容而变成 NULL。'], '常量的文本可以恰好与列名相同，含义仍不同。')
delayed(t, 'literal', '列引用还是固定标签', "-- product = book\nSELECT product, 'product' AS kind FROM items", 'kind 的值是？', ['book', '字段不存在', '字符串 product'], 2,
        'product 是列引用，单引号内的 product 是固定字符串；kind 得到字符串 product。')
task('units', '把计算和名字同时交代清楚', 'amount 是整数元，运营需要千元字段 amount_k。',
     'SELECT __A__ AS __B__ FROM orders', 'A 应选哪一个？',
     ['amount * 1000.0', 'amount / 1000.0', "'amount'"], 1,
     ['从元到千元应缩小一千倍。', '对，除以 1000.0。', '这是字符串，不是金额表达式。'],
     '表达式负责单位，别名负责把单位变化暴露给下游。', 'select.expression-alias', 'SELECT 可以包含算术表达式和 AS 别名；把单位写进列名有助于避免后续重复换算。', '货币计算应核对精度与类型；本题用 double 演示千元展示，不替代精确财务记账。',
     extra=('B：输出列名', ['amount', 'amount_k', 'cnt'], 1, ['会掩盖单位变化。', '对，明确千元口径。', 'cnt 通常表示数量，不是金额。']))
task('identifier', '含空格的列如何引用', '表里有一个真实字段叫 order amount。',
     'SELECT __A__ AS amount FROM orders', '哪个写法引用这个字段？',
     ["'order amount'", '`order amount`', 'order amount'], 1,
     ['这是固定字符串。', '对，反引号包住完整标识符。', '空格会参与 SQL 语法解析，不是完整列名引用。'],
     '标识符与字符串常量的引号不能互换。', 'select.identifier', '使用反引号引用含特殊字符的列名，再用明确别名简化下游使用。', '名称本身包含反引号时还需要转义；本题只处理空格。')
task('distinct', '只选城市后再去重', '明细有 (north,10)、(north,20)、(south,10)。',
     'SELECT DISTINCT city FROM orders', '结果包含几行？', ['3 行，因为原明细不同', '2 行，因为输出城市只有两个', '1 行，因为金额 10 重复'], 1,
     ['去重依据已经是输出的 city，不是全部原始明细。', '对，north 和 south 各一行。', '本查询没有输出金额。'],
     'DISTINCT 对 SELECT 的整组输出列去重；增加输出列会改变重复定义。', 'select.distinct', 'SELECT DISTINCT 消除完整输出行的重复。只输出 city 时，判断的是城市是否重复。', '不要把 DISTINCT city,amount 理解成“只按 city 保留一条金额”。')

lesson('l3-where-order-limit', '从订单里挑出真正的 Top N', '用正确的空值条件和并列规则，避免只取到碰巧出现的几行。', '与 NULL 的普通比较得到未知，并非恒为 false。WHERE 只保留 true；ORDER BY/LIMIT 的物理实现要看计划，不能断言固定 Shuffle 次数。', 'sql-ref-null-semantics.html')
task('conditions', '业务括号不能靠猜', 'A=north/40，B=south/200，C=north/150。',
     "SELECT id FROM orders\nWHERE city = 'north' AND amount > 100", '会留下哪些订单？', ['只有 C', 'A 和 C', 'B 和 C'], 0,
     ['对，地区与金额条件同时满足。', 'A 的金额没有超过 100。', 'B 不在 north。'],
     'SQL 文本中用 AND/OR/NOT 组合条件，复杂条件应显式加括号。', 'where.conditions', 'WHERE 过滤聚合前的行。SQL 的布尔运算写 AND、OR、NOT，与 Column API 的 &、|、~ 属于不同语法层。', 'OR 与 AND 混合时先核对括号和优先级。')
t = task('null', '空值真的等于空值吗', 'phone 三行分别为 NULL、空字符串、123。',
     'SELECT * FROM people WHERE phone = NULL', '会留下哪行？', ['NULL 那行', '没有行，因为比较结果是未知而非 true', '空字符串那行'], 1,
     ['普通等号不能用来判断 NULL。', '对，WHERE 不保留未知条件。', '空字符串也不是 NULL。'],
     '要查缺失电话，写 phone IS NULL；不要把未知理解成普通 false 值。', 'where.null', '普通比较的任一操作数为 NULL 时，结果通常为 NULL（未知）；WHERE 只保留 true。IS NULL 专门判断缺失。', '空字符串与 NULL 不同；需要把二者都视为缺失时要显式组合条件。')
remedy(t, 'null-transfer', '只找未知库存', 'stock 三行：NULL、0、8。\nSELECT * FROM inventory WHERE __A__', 'A 怎么写才只留下未知库存？', ['stock = NULL', 'stock = 0', 'stock IS NULL'], 2,
       ['比较结果未知，不能筛出 NULL。', '会留下真实零库存。', '对，明确检查缺失。'], 'IS NULL 是缺失判断，零值需要另一条业务规则。')
delayed(t, 'null', '缺失时间的筛选', 'ts 三行：NULL、2026-01-01、2026-01-02。\nSELECT * FROM events WHERE ts IS NULL', '会保留什么？', ['只有未知时间那行', '所有行', '没有行'], 0,
        'IS NULL 对未知时间得到 true，因此只保留那行；它与 ts = NULL 不同。')
task('limit', '取两行不等于最高两行', '表中金额有 10、90、50，没有排序约定。', 'SELECT amount FROM orders LIMIT 2', '能保证什么？',
     ['保证得到 90、50', '保证均匀随机抽样', '最多取两行，但不保证最大或随机'], 2,
     ['Top N 需要明确 ORDER BY。', 'LIMIT 不是随机抽样接口。', '对，数量约束不等于顺序或抽样保证。'],
     '没有排序的 LIMIT 不表达“最好”“最早”或“随机”。', 'where.limit', 'LIMIT 约束输出行数；取最大若干条应与完整 ORDER BY 规则组合。', '即使某次运行碰巧得到最大值，也不能把它当成承诺。')
task('ties', '同分时还要定义谁在前', 'A/200，B/200，C/300，按金额高优先，同额按 id 升序。',
     'SELECT id FROM orders ORDER BY amount DESC, id ASC LIMIT 2', '输出顺序是？', ['C、B', 'A、B', 'C、A'], 2,
     ['同额按 id 升序，应先 A。', 'C 金额最高，应在最前。', '对，第二排序键解决并列。'],
     '先完整定义排序，再截取边界，Top N 才有可解释的取舍。', 'where.tie-break', 'ORDER BY 支持多个排序键和 ASC/DESC。固定 Top N 应定义足够的并列处理规则。', '若业务要保留所有同分项，固定 LIMIT 未必符合需求。')

lesson('l3-groupby-having', '先筛订单，还是筛城市日报', '用一组数值分清 WHERE、GROUP BY 和 HAVING 的职责。', 'WHERE 在聚合前，HAVING 在聚合后。GROUP BY 的物理交换与预聚合依赖计划，不能固定说必然某次数 Shuffle 或某种 Combine。', 'sql-ref-syntax-qry-select-having.html')
t = task('stage', '两笔小单能不能组成大城市', 'A 城有 70、60，B 城有 120。想保留总额大于 100 的城市。',
     'SELECT city, SUM(amount) AS total FROM orders\nGROUP BY city HAVING SUM(amount) > 100', '结果是什么？', ['只有 B/120', 'A/130 和 B/120', '只有 A/130'], 1,
     ['这是把每笔 >100 放在 WHERE 时可能得到的结果。', '对，先汇总再按城市总额筛。', 'B 的总额也满足条件。'],
     'HAVING 不能被逐行金额筛选替代，否则组成总额的小订单会被丢掉。', 'aggregate.having-stage',
     'WHERE 决定哪些明细参与聚合，HAVING 决定哪些聚合组进入结果。把条件移动到另一阶段可能改变结果。', '聚合结果也可以在外层查询用 WHERE 过滤；不能在同层 WHERE 直接放 SUM 条件。')
remedy(t, 'having-transfer', '两次访问组成活跃用户', 'u1 有访问时长 4、7；u2 有 8。\n需求：用户总时长 > 10。', '应如何筛？', ['先 WHERE duration > 10', '先分组，再 HAVING SUM(duration) > 10', 'LIMIT 10'], 1,
       ['会在求和前丢掉所有记录。', '对，u1 总时长 11，应留下。', 'LIMIT 控制行数，不表达时长。'], '筛明细还是筛汇总，决定条件所在阶段。')
delayed(t, 'having', '小额订单能组成达标组吗', 'X 城 40、80；Y 城 90。\nGROUP BY city HAVING SUM(amount) > 100', '会保留哪个城市？', ['X 和 Y', '只有 Y', '只有 X'], 2,
        'X 的合计 120 达标，Y 的 90 不达标。HAVING 看组内合计，不要求每笔都超过 100。')
task('count', '数行与数已知金额', '同一城市的 amount 为 10、NULL、20。', 'SELECT COUNT(*) AS rows, COUNT(amount) AS known FROM orders', '两列分别是？', ['3、2', '2、2', '3、3'], 0,
     ['对，COUNT(*) 包含所有行，COUNT(amount) 忽略 NULL。', 'COUNT(*) 不会排除缺失金额行。', 'COUNT(amount) 不包含 NULL。'],
     'SQL 沿用相同的空值聚合语义，换语言不改变业务分母。', 'aggregate.sql-count', 'COUNT(*) 统计行，COUNT(列) 统计该列的非空值。', '如果一行不是一张订单，COUNT(*) 也不能直接解释为订单数。')
task('grain', '汇总后还想带上哪个订单号', '每城有多张订单，结果约定每城一行。',
     'SELECT city, order_id, SUM(amount) FROM orders GROUP BY city', '这份查询有什么问题？',
     ['必须把 SUM 改为 COUNT 才行', 'order_id 既非分组键也未聚合，组内取值未定义', '没有问题，Spark 总是自动取第一张'], 1,
     ['问题不在选了哪种聚合函数。', '对，需要明确粒度与字段选择规则。', '不能依赖自动取第一张这种不存在的约定。'],
     '先决定一行代表什么，再决定结果能保留哪些字段。', 'aggregate.sql-grain', 'SELECT 中普通输出字段应属于分组键，其他输出应由合法聚合表达式产生。', '任意加 first 可能让语法通过，却未解决业务选择规则。')
task('all-null', '全空城市会通过总额条件吗', 'Z 城两行金额都为 NULL。',
     'SELECT city, SUM(amount) AS total FROM orders\nGROUP BY city HAVING SUM(amount) > 0', 'Z 城的 total 和最终去向是什么？',
     ['total=0，留下', 'total=NULL，条件未知，不留下', 'total=2，留下'], 1,
     ['SUM 全空不自动补成 0。', '对，NULL > 0 不是 true。', 'SUM 不是在数行。'],
     '求和与筛选的空值行为共同决定是否出现某个组。', 'aggregate.sql-null-sum', 'SUM/AVG 对全空输入组返回 NULL；HAVING 与 WHERE 一样只保留条件为 true 的结果。', '业务要展示零额城市时，需要明确补零与是否保留无订单城市。')

lesson('l3-joins-intro', '把订单与用户正确配对', '先理解匹配、丢行和放大，再谈连接性能。', '多笔订单匹配一个唯一用户是正常明细粒度；右侧重复键才会额外放大订单。键类型不一致可能发生隐式转换或错误，不能断言必定全部不匹配。', 'sql-ref-syntax-qry-select-join.html')
task('inner', '找不到用户的订单去哪了', 'orders：o1/u1、o2/u9；users：u1/Ana。',
     'SELECT o.id, u.name FROM orders o\nINNER JOIN users u ON o.user_id = u.user_id', '结果包含什么？', ['o1/Ana 和 o2/NULL', '只有 o1/Ana', '只有 o2/Ana'], 1,
     ['这更像保留左侧未匹配行的 LEFT JOIN。', '对，INNER 只留下匹配对。', 'u9 并不匹配 u1。'],
     '连接类型决定未匹配行的去向，INNER 不保证保留全部订单。', 'join.inner-unmatched', 'INNER JOIN 按 ON 条件产生匹配的行对，任何一边未匹配的行不进入结果。', '本课先掌握 INNER；其他连接类型和执行策略留给后续连接章节。')
t = task('multiplicity', '两边都重复会产生几对', '左表同一个键有 2 行，右表同键有 3 行，全部满足等值条件。',
     'SELECT * FROM left_rows l JOIN right_rows r ON l.k = r.k', '这个键会贡献几行？', ['2 行', '3 行', '6 行'], 2,
     ['每条左行都能匹配三条右行。', '不是只按右侧行数保留。', '对，2×3 个匹配对。'],
     'JOIN 不会自动把同键记录去重。聚合前应先核对维表键是否唯一。', 'join.multiplicity', '对于满足连接条件的同键行，左右每一个可匹配组合都会进入连接结果。', '订单多对唯一用户是正常关系；维表重复会额外放大金额，不能只看连接键名字。')
remedy(t, 'multiplicity-transfer', '一笔金额为何变成两笔', '订单一行：u1/50。\n用户维表两行：u1/A、u1/B。\nINNER JOIN 后 SUM(amount)。', '结果金额是多少？', ['50', '100', '0'], 1,
       ['订单匹配到两行，不会自动去重。', '对，50 被复制到两个匹配结果里。', '两行维表都能匹配。'], '先检查维表唯一性，再解释聚合金额。')
delayed(t, 'multiplicity', 'JOIN 后为什么多了', '左表 k=7 有 3 行，右表 k=7 有 2 行。\nINNER JOIN ON l.k=r.k', '该键产生几行？', ['3', '5', '6'], 2,
        '每条左行匹配两条右行，3×2=6。JOIN 不会自动压缩同键记录。')
task('types', '键的类型不同，先别武断', '左侧 user_id 是字符串，右侧是整数。尚未检查字符串内容。',
     'ON orders.user_id = users.user_id', '排查时哪个做法可靠？',
     ['断言所有行绝不会匹配', '只要字段名相同就一定匹配', '核对类型、值与转换规则，再显式统一约定'], 2,
     ['可能发生隐式转换，也可能遇到无效值或异常。', '名字一致不保证类型和值一致。', '对，不能靠类型名直接猜最终匹配结果。'],
     '显式约定连接键类型，有助于避免隐式转换掩盖质量问题。', 'join.key-types', '键类型、可转换性、NULL 和实际值共同影响匹配。应先核对 Schema 与坏值，再决定转换。', '转换行为受表达式与配置影响，不能用一条口号替代验证。')
task('aliases', '同名字段要说清来自哪边', 'orders 与 users 都包含 user_id。',
     'SELECT __A__, o.amount FROM orders o\nJOIN users u ON o.user_id = u.user_id', 'A 哪个写法明确引用用户表的键？', ['u.user_id', "'u.user_id'", 'user_id'], 0,
     ['对，表别名消除来源歧义。', '这是固定字符串。', 'ON 连接后的同名列可能歧义。'],
     '别名既缩短语句，也让字段来源可审查。', 'join.alias', '给关系起别名后使用别名.字段名限定来源，尤其适用于连接中出现同名列的情况。', 'ON 与 USING 的输出列处理不同；本题明确使用 ON。')

lesson('l3-functions-and-udf', '先找内置工具，再决定是否自定义', '清理文本、处理缺失、写条件标签，最后辨认 UDF 的使用边界。', 'UDF 需要显式处理空值与返回类型。不能笼统说所有 UDF 每行跨语言或 pandas UDF 一定更快；本课只比较需求与表达能力。', 'sql-ref-functions-builtin.html')
task('strings', '清理空格后再统一大小写', 'name 是字符串 " ana "。', 'SELECT UPPER(TRIM(name)) AS normalized FROM people', 'normalized 是什么？', [' ANA ', 'ana', 'ANA'], 2,
     ['TRIM 已经去掉首尾空格。', 'UPPER 会转换为大写。', '对，先去空格再大写。'],
     '内置函数可以组合表达常见清洗，不必先写 Python 循环或 UDF。', 'function.builtin', '优先检查内置字符串、日期、数值与条件函数能否表达需求；这些表达式能直接参与 Spark SQL 计划。', '具体性能仍需测量，不能仅凭“内置”二字保证任意表达式都更快。')
t = task('coalesce', '缺失与空串不是同一个值', 'name 三行：NULL、空字符串、Ana。', "SELECT COALESCE(name, 'unknown') AS name FROM people", '三行依次是什么？',
     ['unknown、unknown、Ana', 'unknown、空字符串、Ana', 'NULL、空字符串、Ana'], 1,
     ['COALESCE 不把空字符串自动当作 NULL。', '对，只替换 NULL。', '第一个 NULL 会选择备用值。'],
     '要处理空字符串，先定义显式的空串清洗规则。', 'function.coalesce-null', 'COALESCE 返回参数中第一个非 NULL 值；空字符串是一个非 NULL 字符串。', '它不是通用的“缺失值自动识别器”；业务缺失口径必须明确。')
remedy(t, 'coalesce-transfer', '零分需要补成默认分吗', 'score 三行：NULL、0、8。\nSELECT COALESCE(score, 5) FROM scores', '结果依次是？', ['5、5、8', 'NULL、0、8', '5、0、8'], 2,
       ['0 不是 NULL。', 'NULL 会使用后备值 5。', '对，真实零分不变。'], '默认值只替换缺失，不替换合法零值。')
delayed(t, 'coalesce', '空字符串会自动补上吗', "code 三行：空字符串、NULL、A。\nSELECT COALESCE(code, 'NA') FROM items", '结果依次是？', ['NA、NA、A', '空字符串、NA、A', '空字符串、NULL、A'], 1,
        '空字符串非 NULL，因此保留；只有 NULL 使用 NA。')
task('case', '标签的第一条规则就漏了谁', 'amount 包含 NULL、50、150。',
     "SELECT CASE WHEN amount IS NULL THEN '待核对'\nWHEN amount > 100 THEN '高额' ELSE '普通' END AS tag FROM orders", '三行标签依次是什么？',
     ['普通、普通、高额', '待核对、普通、高额', '待核对、高额、普通'], 1,
     ['首分支显式接住 NULL。', '对，按条件顺序选择匹配分支。', '50 未超过 100，150 才是高额。'],
     'CASE 能直接表达这类标签，不必为了几个分支写 UDF。', 'function.case', 'CASE WHEN 按匹配条件产生表达式结果；把 NULL 的业务分支明确写出来可以避免遗漏未知值。', '多个条件可能同时成立时，先匹配的分支决定结果；返回类型还需兼容。')
task('udf', 'SQL 调用 Python 函数还缺什么', '函数已经处理 None，返回字符串标签。',
     'def label_score(s):\n    return "missing" if s is None else ("high" if s > 90 else "low")\n# SQL: SELECT label_score(score) FROM scores', '如何让 SQL 解析这个自定义函数？',
     ['只定义 Python 函数就自动可用', 'spark.udf.register("label_score", label_score, "string")', '先把全部数据 collect 到 Python'], 1,
     ['SQL 不会自动查找 Python 局部函数。', '对，注册 SQL 名称并声明返回类型。', '不需要为此收集整表。'],
     '先判断内置 CASE 是否足够；确需 UDF 时处理空值、声明类型并在代表数据上验证。', 'function.udf-registration', '普通 Python UDF 可经 spark.udf.register 注册供 SQL 使用，需约定返回类型与 NULL 行为。', '不同 UDF 类型执行方式不同；跨语言开销与向量化收益应按实际场景测量。')

lesson('l3-tables-and-formats', '名字、文件和写入命令分开看', '找到数据入口，再弄清追加、覆盖与目标表的要求。', '不接外部 Hive Metastore 也可使用数据源目录表；能否跨重启保留取决于 catalog 配置。INSERT INTO 是追加，不能泛指 error/ignore；写命令不需要再接 show 才生效。', 'sql-data-sources-load-save-functions.html')
task('catalog', '不启用 Hive，就不能有目录表吗', '当前 Spark 支持数据源表，准备把已有 Parquet 路径登记到 catalog。',
     "CREATE TABLE daily USING parquet LOCATION '/practice/daily'", '哪个判断准确？',
     ['只有 Hive 才能使用任何 CREATE TABLE', '这是临时视图的另一种名字', '可登记数据源表；元数据持久性取决于 catalog 配置'], 2,
     ['数据源表不要求一定接外部 Hive Metastore。', '目录表与会话临时视图需要区分。', '对，不能仅凭有没有 Hive 下结论。'],
     '文件负责数据，catalog 负责名字与元数据；它们的生命周期要分别约定。', 'table.catalog', '数据源表可以将格式、位置等信息登记到 catalog；临时视图则是另一种命名关系。', '本路线不搭建外部 Hive Metastore；不据此承诺所有默认目录跨重启永久保留。')
task('path', '直接从 Parquet 路径提问', '日报已经写在可信练习路径 /practice/daily。',
     'SELECT city FROM parquet.`/practice/daily`', '这里 parquet 与反引号内的内容分别表示什么？',
     ['数据源格式与文件路径', '目录数据库名与已注册表名', '输出格式与结果别名'], 0,
     ['对，是直接文件查询的一种入口。', '这里访问的是文件路径，并非已登记的表名。', '这是读取入口，不是输出声明。'],
     'SQL 也可访问受支持的数据源路径；“只能查注册视图”不是完整规则。', 'table.direct-path', 'Spark SQL 对支持的文件源提供格式.路径形式的直接查询，路径标识符用反引号包围。', '示例只使用可信固定练习路径；不要把外部输入直接拼成 SQL 路径。')
t = task('append', '同一批日报写两次会怎样', 'daily 是已创建的可写表，每批结果有 3 行，没有额外去重机制。',
     'INSERT INTO daily SELECT * FROM batch;\nINSERT INTO daily SELECT * FROM batch;', '同一批次会新增几行？', ['3 行，自动去重', '6 行，追加了两次', '0 行，因为没接 show'], 1,
     ['INSERT INTO 不自动按批次去重。', '对，相同批次被追加两次。', '写命令不靠 show 才产生副作用。'],
     '设计重跑策略时，要先区分追加与替换，不能只看语句是否执行成功。', 'table.insert-append', 'INSERT INTO 向目标追加查询结果，INSERT OVERWRITE 表达覆盖语义。目标、列映射和分区规则必须先核对。', '这不提供任意文件系统上的完整事务保证；本课不执行这些写命令。')
remedy(t, 'append-transfer', '两行库存又跑了一遍', '一个空的练习表，每次 INSERT INTO 写入相同两行，运行两次。', '没有去重逻辑时最终几行？', ['2', '0', '4'], 2,
       ['追加不会自动幂等。', '已经执行了两次写命令。', '对，2+2=4。'], '相同输入重复追加仍会重复，重跑需要明确策略。')
delayed(t, 'append', '写命令会自动防重复吗', '练习表初始空。相同 4 行结果执行两次 INSERT INTO。', '无其他机制时总行数是？', ['4', '8', '0'], 1,
        'INSERT INTO 追加，两次各 4 行得到 8 行；不自动去重，也不需要再调用 show。')
task('target', '写入前先确认目标存在', 'SQL 准备向 daily 写入结果。当前只创建了 orders 临时视图。',
     'INSERT OVERWRITE TABLE daily SELECT city, SUM(amount) FROM orders GROUP BY city', '应先核对什么？',
     ['只要 orders 存在，daily 自动正确建立', '把 daily 当普通临时视图即可写文件', 'daily 的目录定义、可写性和列对应规则'], 2,
     ['不能假定目标表已存在且结构匹配。', '普通临时视图不是任意可写物理表。', '对，输入可查询与输出可写是两项约定。'],
     '完整交付不只是一段 SELECT，目标格式和位置也要事先约定。', 'table.write-target', '写入命令需要合法的目标关系、Schema 与访问安排，SELECT 成功不能证明目标可写。', '本地练习优先用新的隔离路径，不操作生产表。')

lesson('l3-comprehensive', '准备练习：用 SQL 交付城市日报', '这六步是可选热身；独立毕业任务使用另一份输入，先在任务工作台自己实现。', 'HAVING 与 WHERE 不可按同层条件互换；SQL 命令不能全部视为惰性。输出文件不承诺保留排名，不能只凭 show 的样本或总计验收。')
task('read', '先让字段和名字对上', '准备数据：p1/A/70、p2/A/60、p3/B/140、p4/B/NULL。金额为整数元。',
     'raw = spark.read.option("header", True).schema(__A__).csv("practice.csv")\nraw.createOrReplaceTempView("orders")', 'A 应使用什么结构？',
     ['"id long, city string, amount string"', '"id string, city string, amount long"', '"city long, amount boolean"'], 1,
     ['p1 不是整数，金额也应按约定读取。', '对，按输入约定建立结构。', '字段与类型都不符合输入。'],
     '读入结构与 SQL 关系名都是分析链的输入契约。', 'project.sql-input', '独立 SQL 任务先确认字段名、类型、空值规则和输入关系名。', '这份准备练习不是毕业任务的数据，不能照搬结果。')
task('dedup', '完全相同的导入行怎么办', '同一条 p1/A/70 被重复导入一次，业务要求完全相同行只算一次。',
     'SELECT __A__ id, city, amount FROM orders', 'A 应填什么？', ['DISTINCT', 'LIMIT', 'HAVING'], 0,
     ['对，三列共同定义完整输出行的重复。', 'LIMIT 不是去重。', 'HAVING 不放在这里，也不负责去重。'],
     '去重依据应与业务约定一致，不是随便按一个字段丢行。', 'project.sql-dedup', '完全相同行的重复可用 SELECT DISTINCT 在同一组输出字段上消除。', '同键冲突版本需要另定义保留规则，不能直接套用 DISTINCT。')
t = task('stages', '先保留有效单，再筛达标城市', '使用准备数据，业务只统计正金额，城市总额需严格大于 100。',
     'SELECT city, SUM(amount) AS total FROM orders\nWHERE __A__ GROUP BY city HAVING __B__', 'A 应选什么？',
     ['SUM(amount) > 100', 'amount > 0', 'amount IS NULL'], 1,
     ['同层 WHERE 不是筛聚合结果的位置。', '对，先筛有效明细。', '这会只保留缺失金额。'],
     'WHERE 定义参与指标的订单，HAVING 定义交付哪些城市。', 'project.sql-stages', '多步分析先按业务规则筛明细，再按分组指标筛结果；每一步都应能解释对分母的影响。', '本题 >100 与独立毕业任务的阈值不同，边界要重新读。',
     extra=('B：城市达标条件', ['amount > 100', 'SUM(amount) > 100', 'COUNT(*) > 100'], 1, ['这是单笔金额，不是城市总额。', '对，按城市合计筛选。', '业务比较的是金额，不是笔数。']))
remedy(t, 'stages-transfer', '恰好等于门槛要不要留', '业务：城市合计至少 200 元。\n某城市两笔 90、110。', '正确判断是什么？', ['用 HAVING SUM(amount) >= 200，应该保留', '用 WHERE amount >= 200，会保留两笔', '用 HAVING SUM(amount) > 200，也会保留'], 0,
       ['对，“至少”包含等号。', '两笔都小于 200，会在求和前被排除。', '严格大于不包括刚好 200。'], '不只要选对阶段，还要读对阈值边界。')
delayed(t, 'stages', '至少与超过的区别', '某组金额 120、80，需求是合计至少 200。', '应使用什么条件？', ['WHERE amount > 200', 'HAVING SUM(amount) >= 200', 'HAVING SUM(amount) > 200'], 1,
        '至少包含边界，且筛组内合计应在聚合后使用 HAVING SUM(amount) >= 200。')
task('metric', '缺失金额还应算进有效订单吗', '准备任务先执行 WHERE amount > 0，A 有 70、60，B 有 140、NULL。',
     'SELECT city, COUNT(*) AS cnt, SUM(amount) AS total\nFROM orders WHERE amount > 0 GROUP BY city', '结果是什么？', ['A:2/130，B:2/140', 'A:1/70，B:1/140', 'A:2/130，B:1/140'], 2,
     ['B 的 NULL 行已被 WHERE 排除。', 'A 的两笔正金额都有效。', '对，指标针对筛选后的集合计算。'],
     '计数口径必须与清洗阶段合在一起解释。', 'project.sql-metrics', '定义指标时明确是在原始输入、去重后还是有效明细上计算，避免同名 cnt 表示不同集合。', '只核对总额可能漏掉重复计数或地区分配错误。')
task('rank', '日报预览也要定义并列顺序', '城市 A 与 B 的总额都是 200。希望同额按 city 升序。',
     'SELECT city, total FROM report ORDER BY __A__ LIMIT 1', 'A 应填什么？', ['total DESC, city ASC', 'city DESC', 'total DESC'], 0,
     ['对，完整定义金额优先及并列规则。', '会优先 B，忽略金额排序需求。', '同额时没有定义 A/B 取舍。'],
     '排名规则适用于查询展示；文件读回后若需要排名，应重新排序。', 'project.sql-ranking', '对报表做 Top N 展示时定义完整排序键；保存数据集不等于保存文件中的全局行顺序。', '目录分区与文件数量也不是排名规则。')
task('accept', '看到总额对了，够不够交付', '输出总额与纸上计算一致，但还没核对各城市和写出后结果。',
     'report.show()\n# 总额看起来正确', '下一步应如何验收？',
     ['直接认定毕业成功', '只把 show 行数改大', '核对字段/类型/逐城市指标，写出读回并检查重跑'], 2,
     ['不同城市的错误可能互相抵消，文件也未验证。', '展示更多行仍不等于可运行断言和文件验收。', '对，查询正确与交付可用都要验证。'],
     '毕业任务要求新的输入、独立实现和可复现验收，不靠看懂一道陈述题完成。', 'project.sql-acceptance', '独立验收应检查逐组指标、类型、空结果与阈值边界，并实际验证输出可读和重复执行行为。', '当前开发机的 Windows 文件系统限制仍存在，查询通过不等于文件阶段通过。')

# Vary answer positions without changing stable choice IDs or answer identity.
for index, t in enumerate(t for l in lessons.values() for t in l['tasks']):
    for field_index, field in enumerate(t['fields']):
        answer = next(o for o in field['options'] if o['id'] == field['correctOptionId'])
        wrong = [o for o in field['options'] if o['id'] != field['correctOptionId']]
        wrong.insert((index + field_index) % 3, answer)
        field['options'] = wrong
    if t.get('remediation'):
        field = t['remediation']['field']
        answer = next(o for o in field['options'] if o['id'] == field['correctOptionId'])
        wrong = [o for o in field['options'] if o['id'] != field['correctOptionId']]
        wrong.insert((index + 1) % 3, answer)
        field['options'] = wrong
for index, item in enumerate(i for i in DELAYED['items'] if i['slug'].startswith('l3-')):
    answer = next(o for o in item['options'] if o['id'] == item['correctOptionId'])
    wrong = [o for o in item['options'] if o['id'] != item['correctOptionId']]
    wrong.insert((index + 2) % 3, answer)
    item['options'] = wrong
GUIDES['lessons']['l3-what-is-spark-sql']['sources'].append(dict(title='SQL 查询与命令 API', url=BASE+'api/scala/org/apache/spark/sql/SparkSession.html'))
GUIDES['version'] = 2
DELAYED['version'] = 2
outputs = {ROOT / 'lessons' / f'{slug}.json': data for slug, data in lessons.items()}
outputs[ROOT / 'standardGuides.json'] = GUIDES
outputs[ROOT / 'delayedChecks.json'] = DELAYED
for path, data in outputs.items():
    rendered = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    if '--check' in sys.argv:
        assert path.read_text(encoding='utf-8') == rendered, f'Authoring drift: {path}'
    else:
        path.write_text(rendered, encoding='utf-8')
print('PASS L3 authored:', len(lessons), 'lessons /', sum(len(l['tasks']) for l in lessons.values()), 'steps / 9 remedies / 9 delayed checks')
