"""Self-contained L4/L5/L6 lab verifier, copied into each download kit.
Only uses small provided teaching fixtures, never the app DB. No Spark file
write is substituted: these labs deliver plan/partition/join evidence, not Parquet.
"""
import argparse
from contextlib import redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
from tempfile import mkdtemp


def grouped(rows):
    expected = {}
    for region, amount in rows:
        if amount is not None and amount > 0:
            n, total = expected.get(region, (0, 0))
            expected[region] = (n+1, total+amount)
    return expected


def check_report(report, expected):
    assert len(report.columns)==3 and set(report.columns)=={'region','cnt','total'}, 'Output columns must be region/cnt/total'
    assert {f.name:f.dataType.simpleString() for f in report.schema.fields} == dict(region='string',cnt='bigint',total='bigint'), 'Output types must be string/long/long'
    actual=report.select('region','cnt','total').limit(len(expected)+1).collect()
    assert len(actual)==len(expected), 'Missing/extra/duplicate report rows'
    assert len({r.region for r in actual})==len(actual), 'Duplicate report keys'
    assert {r.region:(r.cnt,r.total) for r in actual}==expected, 'Wrong grouped counts/totals; check validity, matching and unknown rules'


def plan_text(frame):
    buffer=io.StringIO()
    with redirect_stdout(buffer):
        frame.explain()
    return buffer.getvalue()


def join_expected(orders, dimension):
    dim={}
    for key,region in dimension:
        if key is None:
            continue
        if key in dim:
            raise ValueError('Duplicate non-NULL dimension key')
        dim[key]=region
    projected=[]
    for _,user,amount in orders:
        region=dim.get(user) if user is not None else None
        projected.append(('unknown' if region is None else region,amount))
    return grouped(projected)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--solution',default='starter.py')
    parser.add_argument('--output',help='New non-existing evidence directory')
    args=parser.parse_args()
    base=Path(__file__).resolve().parent
    task=json.loads((base/'task.json').read_text(encoding='utf-8'))
    if args.output:
        output=Path(args.output).resolve();output.mkdir(parents=True,exist_ok=False)
    else:
        practice=base/'practice';practice.mkdir(exist_ok=True)
        output=Path(mkdtemp(prefix='evidence-',dir=practice))
    result=dict(task=task['task'],version=1,status='FAIL',automatic_checks='FAIL',manual_review='required',artifacts='not-ready',checks=[])
    spark=None;stage='load-solution'
    def passed(name):
        result['checks'].append(dict(stage=name,status='PASS'));print('PASS',name,flush=True)
    try:
        spec=importlib.util.spec_from_file_location('student_lab',Path(args.solution).resolve())
        if spec is None or spec.loader is None:raise ValueError('Cannot import selected local solution')
        student=importlib.util.module_from_spec(spec);spec.loader.exec_module(student)
        os.environ.setdefault('PYSPARK_PYTHON',sys.executable)
        stage='spark-environment'
        from pyspark.sql import SparkSession, functions as F
        spark=(SparkSession.builder.master('local[2]').appName('spark-learning-lab')
               .config('spark.ui.enabled','false').config('spark.ui.showConsoleProgress','false')
               .config('spark.driver.host','127.0.0.1').config('spark.driver.bindAddress','127.0.0.1')
               .config('spark.sql.shuffle.partitions','2').config('spark.sql.adaptive.enabled','false').getOrCreate())
        spark.sparkContext.setLogLevel('ERROR');result['spark_version']=spark.version;result['aqe']=False
        if task['task']=='plan':
            cases=[task['orders'],[['x','new',17,'x'],['y','new',23,'y'],['z','other',-1,'x']],[],[['n','none',None,'x'],['z','none',0,'x']]]
            for index,rows in enumerate(cases):
                stage=f'plan-result-{index}'
                frame=spark.createDataFrame([tuple(r) for r in rows],task['schema'])
                report=student.build_report(frame)
                check_report(report,grouped([(r[1],r[2]) for r in rows]));passed(stage)
            stage='relative-plan-evidence'
            frame=spark.createDataFrame([tuple(r) for r in task['orders']],task['schema'])
            baseline=(frame.repartition(7).filter(F.col('amount')>0).groupBy('region')
                      .agg(F.count('*').alias('cnt'),F.sum('amount').alias('total')))
            candidate=student.build_report(frame)
            before,after=plan_text(baseline),plan_text(candidate)
            (output/'plan-before.txt').write_text(before,encoding='utf-8')
            (output/'plan-after.txt').write_text(after,encoding='utf-8')
            count=lambda text:sum('Exchange' in line for line in text.splitlines())
            result['exchange_comparison']={'baseline':count(before),'candidate':count(after)}
            assert count(after)<count(before), 'Controlled baseline has an extra repartition: remove unnecessary exchange; inspect saved plans and version assumptions'
            passed(stage)
        elif task['task']=='partition':
            cases=[task['rows'],[['new',3],['new',-3],['other',9]],[['hot',1]]*12+[['cold',2]],[]]
            evidence=[]
            for index,rows in enumerate(cases):
                expected={}
                for key,qty in rows:expected[key]=expected.get(key,0)+qty
                for partitions in task['partitions']:
                    stage=f'partition-case-{index}-n{partitions}'
                    actual=student.build_totals(spark.sparkContext,rows,partitions)
                    assert actual.getNumPartitions()==partitions,'Output Pair RDD must use requested partitions'
                    pairs=actual.take(len(expected)+1)
                    assert len(pairs)==len(expected) and len({k for k,v in pairs})==len(pairs),'Missing/duplicate keyed output'
                    assert dict(pairs)==expected,'Integer totals must be invariant across partition count'
                    assert all(isinstance(v,int) and not isinstance(v,bool) for k,v in pairs),'Integer quantities required'
                    source=spark.sparkContext.parallelize([tuple(r) for r in rows],partitions)
                    counts=source.mapPartitionsWithIndex(lambda i,it:[(i,sum(1 for _ in it))]).collect()
                    evidence.append(dict(case=index,partitions=partitions,input_partition_rows=counts))
                    passed(stage)
            (output/'partition-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
            result['measurement_limit']='Row counts only; not byte/CPU/network or production benchmark'
        elif task['task']=='join':
            cases=[(task['orders'],task['dimension']),
                   ([['x','new',13],['y','missing',17],['z',None,19]],[['new','new-region'],[None,'must-not-match']]),
                   ([],task['dimension']),
                   ([['x','u1',None],['y','u1',0],['z','u1',-1]],task['dimension']),
                   ([['x','u1',10],['y','u1',20]], [['u1',None]]),
                   ([['x','u1',6]],[['u1','']]),
                   ([['x',None,7]],[[None,'A'],[None,'B']])]
            for index,(orders,dimension) in enumerate(cases):
                stage=f'join-case-{index}'
                o=spark.createDataFrame([tuple(r) for r in orders],task['order_schema'])
                d=spark.createDataFrame([tuple(r) for r in dimension],task['dimension_schema'])
                report=student.build_enriched_report(o,d)
                check_report(report,join_expected(orders,dimension));passed(stage)
                if index==0:(output/'join-plan.txt').write_text(plan_text(report),encoding='utf-8')
            stage='reject-duplicate-dimension'
            o=spark.createDataFrame([('x','u1',10)],task['order_schema'])
            d=spark.createDataFrame([('u1','A'),('u1','B')],task['dimension_schema'])
            try:
                student.build_enriched_report(o,d)
            except ValueError:
                passed(stage)
            else:
                raise AssertionError('Duplicate non-NULL dimension keys must be explicitly rejected with ValueError')
        else:
            raise ValueError('Unknown lab type')
        stage='diagnosis-draft'
        note=student.diagnosis()
        assert isinstance(note,str) and note.strip(),'Write a diagnosis draft; its reasoning still requires human review'
        (output/'diagnosis.txt').write_text(note+'\n',encoding='utf-8');passed(stage)
        result.update(status='PASS',automatic_checks='PASS',artifacts='PASS')
    except Exception as error:
        result['checks'].append(dict(stage=stage,status='FAIL',error=str(error)[:1800]))
        print('NOT PASSED',stage,str(error)[:900],flush=True)
    finally:
        (output/'validation-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(result['status'],'artifacts='+result['artifacts'],'manual_review=required',str(output),flush=True)
        if spark is not None:spark.stop()
    return 0 if result['status']=='PASS' else 1


if __name__=='__main__':
    raise SystemExit(main())
