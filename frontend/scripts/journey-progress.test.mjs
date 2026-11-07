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
