import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import ts from 'typescript';
const module = { exports: {} };
const src = fs.readFileSync(new URL('../src/components/journeyProgress.ts', import.meta.url), 'utf8');
new Function('exports', 'module', ts.transpileModule(src, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText)(module.exports, module);
const { loadProgress, progressKey, freshProgress, recordAttempt, evidence } = module.exports;
const lesson = JSON.parse(fs.readFileSync(new URL('../src/content/lessons/l2-create-dataframe.json', import.meta.url), 'utf8'));
function storage() { const m = new Map(); return { getItem: k => m.get(k) ?? null, setItem: (k,v) => m.set(k,v) }; }
test('migrates old partial/completed progress without fabricating attempts', () => {
  for (const step of [0, 2, lesson.tasks.length]) {
    const s=storage(); s.setItem(`spark-quest:journey:${lesson.slug}:v1`,JSON.stringify({step,helped:[0]}));
    const p=loadProgress({...lesson,version:1},s); assert.equal(p.completedIds.length,step); assert.equal(p.attempts.length,0);
    assert.equal(p.cursorId,lesson.legacyTaskIds[step]??null);
    if(step) assert.match(evidence(p,lesson.tasks[0].id),/旧版/);
  }
});
test('intro numeric progress migrates to the unified player', () => {
  const intro=JSON.parse(fs.readFileSync(new URL('../src/content/lessons/l2-what-is-dataframe.json',import.meta.url),'utf8'));
  const s=storage();s.setItem('spark-quest:df-intro:v1','3');assert.equal(loadProgress({...intro,version:1},s).cursorId,null);
});
test('task/option reorder cannot change cursor or correct answer identity', () => {
  const s=storage();const p=freshProgress(lesson);p.cursorId=lesson.tasks[1].id;s.setItem(progressKey(lesson),JSON.stringify(p));
  const reordered=structuredClone(lesson);reordered.tasks.reverse();reordered.tasks.forEach(t=>t.fields.forEach(f=>f.options.reverse()));
  assert.equal(loadProgress(reordered,s).cursorId,p.cursorId);
  const t=reordered.tasks.find(t=>t.id===p.cursorId);const answers=Object.fromEntries(t.fields.map(f=>[f.id,f.correctOptionId]));
  assert.equal(recordAttempt(reordered,p,t.id,answers).attempts[0].correct,true);
});
test('revision change starts a separate record and retains old data', () => {
  const s=storage();s.setItem(progressKey(lesson),JSON.stringify(freshProgress(lesson)));s.setItem(`spark-quest:journey:${lesson.slug}:v1`,JSON.stringify({step:4}));
  const next={...lesson,version:lesson.version+1};assert.equal(loadProgress(next,s).completedIds.length,0);assert.ok(s.getItem(progressKey(lesson)));
});
test('attempts snapshot answers, record first errors and survive a new run', () => {
  const t=lesson.tasks[0];const f=t.fields[0];let p=freshProgress(lesson);const answers={[f.id]:f.options.find(o=>o.id!==f.correctOptionId).id};
  p=recordAttempt(lesson,p,t.id,answers);answers[f.id]=f.correctOptionId;p=recordAttempt(lesson,p,t.id,answers);
  assert.equal(p.attempts[0].correct,false);assert.equal(p.attempts[1].correct,true);assert.notEqual(p.attempts[0].answers[f.id],answers[f.id]);assert.match(evidence(p,t.id),/2 次/);
  const reset={...freshProgress(lesson),attempts:p.attempts};assert.equal(reset.attempts.length,2);assert.equal(evidence(reset,t.id),'尚无作答记录');
});
test('corrupt state or denied storage does not break learning', () => {
  const s=storage();s.setItem(progressKey(lesson),'{bad');assert.equal(loadProgress(lesson,s).completedIds.length,0);
  s.setItem(progressKey(lesson),JSON.stringify({...freshProgress(lesson),cursorId:null}));assert.notEqual(loadProgress(lesson,s).cursorId,null);
  assert.equal(loadProgress(lesson,{getItem(){throw Error('blocked')}}).attempts.length,0);
});

const readingModule={exports:{}};
new Function('exports','module',ts.transpileModule(fs.readFileSync(new URL('../src/components/readingExcerpt.ts',import.meta.url),'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS}}).outputText)(readingModule.exports,readingModule);
test('reading excerpts resolve the original segment and reject missing/ambiguous markers',()=>{
  const {extractReading}=readingModule.exports;
  assert.equal(extractReading('prefix [start] original text [end] next','[start]','[end]'),'original text');
  assert.equal(extractReading('no markers','[start]','[end]'),null);
  assert.equal(extractReading('[start] one [start] two [end]','[start]','[end]'),null);
  assert.equal(extractReading('[start] unfinished','[start]','[end]'),null);
});

test('remediation events never complete the original step or inflate its attempt count',()=>{
 const l=JSON.parse(fs.readFileSync(new URL('../src/content/lessons/l2-groupby-agg.json',import.meta.url),'utf8'));
 const t=l.tasks.find(t=>t.remediation);let p=freshProgress(l);p.cursorId=t.id;
 const wrong=Object.fromEntries(t.fields.map(f=>[f.id,f.options.find(o=>o.id!==f.correctOptionId).id]));
 p=recordAttempt(l,p,t.id,wrong);
 const {recordRemediation}=module.exports;
 p=recordRemediation(l,p,t.id,t.remediation.field.correctOptionId);
 assert.equal(p.cursorId,t.id);assert.equal(p.completedIds.length,0);
 assert.equal(p.attempts[1].activity,'remediation');assert.ok(p.attempts[1].knowledgeId);
 assert.match(evidence(p,t.id),/原题作答 1 次/);assert.match(evidence(p,t.id),/已通过一道变式/);
 assert.equal(p.attempts[1].correctOptions[t.remediation.field.id],t.remediation.field.correctOptionId);
 assert.throws(()=>recordRemediation(l,p,t.id,'not-a-real-option'));
 const s=storage();s.setItem(progressKey(l),JSON.stringify(p));assert.equal(loadProgress(l,s).attempts.length,2);
});


const delayedModule = { exports: {} };
const delayedSrc = fs.readFileSync(new URL('../src/components/delayedProgress.ts', import.meta.url), 'utf8');
new Function('exports', 'module', 'require', ts.transpileModule(delayedSrc, {compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText)(delayedModule.exports, delayedModule, () => module.exports);
const { delayedQueue, submitDelayed, delayedKey, day } = delayedModule.exports;
const bank = JSON.parse(fs.readFileSync(new URL('../src/content/delayedChecks.json', import.meta.url), 'utf8'));
function delayedFixture() {
  const item=bank.items[0]; const l=JSON.parse(fs.readFileSync(new URL(`../src/content/lessons/${item.slug}.json`,import.meta.url),'utf8'));
  const s=storage(); const at=Date.parse('2026-11-01T10:00:00Z'); const t=l.tasks.find(t=>t.id===item.taskId);
  let p=recordAttempt(l,freshProgress(l),t.id,Object.fromEntries(t.fields.map(f=>[f.id,f.correctOptionId])));
  p.attempts[0].at=new Date(at).toISOString();p.completedIds=[t.id];s.setItem(progressKey(l),JSON.stringify(p));
  return {item,l,s,at,p,lessons:{[l.slug]:l}};
}
test('delayed checks require completed original evidence and a full 24 hours, with later exposure restarting the wait',()=>{
  const {item,l,s,at,p,lessons}=delayedFixture();
  assert.equal(delayedQueue([item],lessons,s,at+day-1).length,0);
  assert.equal(delayedQueue([item],lessons,s,at+day).length,1);
  const snapshot=s.getItem(progressKey(l));
  assert.equal(delayedQueue([item],lessons,s,at+2*day).length,1);assert.equal(s.getItem(progressKey(l)),snapshot);
  p.attempts.push({...p.attempts[0],activity:'remediation',at:new Date(at+day).toISOString()});s.setItem(progressKey(l),JSON.stringify(p));
  assert.equal(delayedQueue([item],lessons,s,at+day+1).length,0);
  p.completedIds=[];s.setItem(progressKey(l),JSON.stringify(p));assert.equal(delayedQueue([item],lessons,s,at+4*day).length,0);
});
test('delayed failure waits another day; success retires material; duplicates and stale submissions are rejected',()=>{
  const {item,l,s,at,lessons}=delayedFixture();const original=s.getItem(progressKey(l));
  const c=delayedQueue([item],lessons,s,at+day)[0];const wrong=item.options.find(o=>o.id!==item.correctOptionId).id;
  assert.throws(()=>submitDelayed(c,'invalid',[item],lessons,s,at+day));
  const e=submitDelayed(c,wrong,[item],lessons,s,at+day);assert.equal(e.correct,false);
  assert.throws(()=>submitDelayed(c,item.correctOptionId,[item],lessons,s,at+day));
  assert.equal(delayedQueue([item],lessons,s,at+2*day-1).length,0);
  const again=delayedQueue([item],lessons,s,at+2*day)[0];submitDelayed(again,item.correctOptionId,[item],lessons,s,at+2*day);
  assert.equal(delayedQueue([item],lessons,s,at+20*day).length,0);
  assert.equal(JSON.parse(s.getItem(delayedKey)).length,2);assert.equal(s.getItem(progressKey(l)),original);
});
test('corrupt or denied delayed storage cannot produce a recorded success',()=>{
  const {item,s,at,lessons}=delayedFixture();s.setItem(delayedKey,'{bad');assert.throws(()=>delayedQueue([item],lessons,s,at+day));
  s.setItem(delayedKey,'[]');const c=delayedQueue([item],lessons,s,at+day)[0];
  assert.throws(()=>submitDelayed(c,item.correctOptionId,[item],lessons,{getItem:s.getItem,setItem(){throw Error('denied')}},at+day));
  assert.equal(s.getItem(delayedKey),'[]');
});


test('metadata-only loading preserves progress and delayed scheduling without fetching lesson answers',()=>{
  const index=JSON.parse(fs.readFileSync(new URL('../src/content/journeyIndex.json',import.meta.url),'utf8'));
  for (const [slug,meta] of Object.entries(index)) {
    const full=JSON.parse(fs.readFileSync(new URL(`../src/content/lessons/${slug}.json`,import.meta.url),'utf8'));
    assert.equal(meta.version,full.version);assert.deepEqual(meta.tasks.map(t=>t.id),full.tasks.map(t=>t.id));
    assert.ok(meta.tasks.every(t=>!('fields' in t)));
    const s=storage();const p=freshProgress(full);s.setItem(progressKey(full),JSON.stringify(p));
    assert.deepEqual(loadProgress(meta,s),loadProgress(full,s));
  }
  const {item,l,s,at,lessons}=delayedFixture();
  assert.deepEqual(delayedQueue([item],index,s,at+day),delayedQueue([item],lessons,s,at+day));
});
