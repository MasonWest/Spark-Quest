"""Independent small Spark checks for the new bridges; never touch the app DB.
Memory tests exercise idle borrowing and refusal to evict active execution only.
Cache-block eviction examples are capacity models, not live eviction experiments.
"""
import json
import os
from pathlib import Path
import re
import sys
os.environ.setdefault('PYSPARK_PYTHON',sys.executable)
from pyspark.sql import SparkSession

root=Path(__file__).resolve().parents[1]
memory=json.loads((root/'src/content/lessons/l7-executor-memory.json').read_text(encoding='utf-8'))
tasks={t['id'].split('/')[-1]:t for t in memory['tasks']}
def answer(key):
    f=tasks[key]['fields'][0]
    return next(o['text'] for o in f['options'] if o['id']==f['correctOptionId'])

# Independent capacity arithmetic: free room plus storage above its protected region.
for M,R,S,expected in [(100,50,80,50),(300,120,210,180),(100,50,0,100),(100,50,20,80)]:
    available=(M-S)+max(0,S-R)
    assert available==expected
state=dict((k,int(v)) for k,v in re.findall(r'\b([MRS])=(\d+)',tasks['bridge-protected-limit']['code']))
assert int(answer('bridge-protected-limit'))==state['M']-min(state['S'],state['R'])
heap,reserved,fraction,M,storage_fraction,R=map(float,re.findall(r'\d+(?:\.\d+)?',tasks['bridge-fraction-meaning']['code']))
assert (heap-reserved)*fraction==M and M*storage_fraction==R
delayed=json.loads((root/'src/content/delayedChecks.json').read_text(encoding='utf-8'))
item=next(i for i in delayed['items'] if i['id']=='l7-executor-memory/memory-reclaim-delayed-v1')
state=dict((k,int(v)) for k,v in re.findall(r'\b([MRS])=(\d+)',item['code']))
expected=state['M']-min(state['S'],state['R'])
assert int(next(o['text'] for o in item['options'] if o['id']==item['correctOptionId']))==expected
print('PASS capacity examples and parameter arithmetic (model, not live cache eviction)',flush=True)
if '--model-only' in sys.argv:
    raise SystemExit(0)

spark=(SparkSession.builder.master('local[2]').appName('concept-bridge-check')
       .config('spark.ui.enabled','false').config('spark.ui.showConsoleProgress','false')
       .config('spark.driver.host','127.0.0.1').config('spark.driver.bindAddress','127.0.0.1').getOrCreate())
spark.sparkContext.setLogLevel('ERROR')
try:
    sc=spark.sparkContext
    tokens=sc.parallelize(['Spark','SQL','spark'],2)
    pairs=tokens.map(lambda w:(w.lower(),1))
    assert pairs.collect()==[('spark',1),('sql',1),('spark',1)]
    assert dict(pairs.reduceByKey(lambda a,b:a+b).collect())=={'spark':2,'sql':1}
    assert sc.parallelize(['',' \t '],2).flatMap(lambda line:line.split()).count()==0
    print('PASS actual RDD card shape, reduceByKey counts and whitespace boundary',flush=True)
    jvm=spark._jvm
    manager=jvm.org.apache.spark.memory.UnifiedMemoryManager(spark._jsc.sc().conf(),100,50,1)
    mode=jvm.org.apache.spark.memory.MemoryMode.ON_HEAP
    assert manager.acquireExecutionMemory(80,0,mode)==80
    assert manager.maxOnHeapStorageMemory()==20
    block=jvm.org.apache.spark.storage.RDDBlockId(987654,0)
    assert manager.acquireStorageMemory(block,40,mode)==False
    assert manager.executionMemoryUsed()==80
    manager.releaseExecutionMemory(80,0,mode)
    print('PASS real UnifiedMemoryManager: execution borrows idle storage; new cache cannot evict active execution',flush=True)
    print('Runtime Spark',spark.version,'; does not certify actual block eviction or per-task allocations in the other modeled states',flush=True)
finally:
    spark.stop()
