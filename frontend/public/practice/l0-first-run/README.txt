第一个PySpark程序：小CSV地区汇总

把这些文件放在同一目录，在终端进入该目录。
环境：Python、pyspark包和兼容的Java。按实际Spark版本核对官方安装要求：
https://spark.apache.org/docs/3.5.7/api/python/getting_started/install.html
版本不兼容或无法启动属于环境失败，不等于课程知识作答错误。

先填写starter.py里的summarize(spark, csv_path)。
输入CSV带region,amount表头；region是非空地区文本，amount是非负整数。
同一地区每行贡献都必须计入，重复行不会自动去重；空输入应没有分组。
返回DataFrame，列名region和sum(amount)，每地区一行；不要求输出排序。
本任务不处理NULL、坏记录或小数金额；这些在后续课程学习。

运行自己的程序：python starter.py sales.csv
样例应得到north=20、south=5；不能只写死这份答案。
换输入验证：python verify.py --solution starter.py
验证器使用四份独立小CSV，包含重复记录、零金额、空输入与新地区。
它只在临时目录写入并清理测试文件；不访问应用数据库，不提交课程成绩。
本地PASS只说明这些小样例通过，不认证独立编程能力或生产性能。

先独立尝试，再看reference.py；可对照运行：
python verify.py --solution reference.py
参考代码中count数行、groupBy分组、sum求和；show只显示结果，stop释放资源。
网页的推演不会执行Spark，真实运行需要本地环境。
