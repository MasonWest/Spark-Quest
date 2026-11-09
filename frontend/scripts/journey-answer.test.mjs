import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import ts from 'typescript';
const module = { exports: {} };
new Function('exports','module',ts.transpileModule(fs.readFileSync(new URL('../src/components/journeyAnswer.ts',import.meta.url),'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText)(module.exports,module);
const { normalizeResponse, responseOption } = module.exports;
const lesson = slug => JSON.parse(fs.readFileSync(new URL(`../src/content/lessons/${slug}.json`,import.meta.url),'utf8'));
const input = (slug,key) => lesson(slug).tasks.find(t=>t.id.endsWith('/'+key)).fields[0];

test('integer responses accept full-width/whitespace but reject fractions, coercion and unsafe values',()=>{
  const f=input('l1-rdd-exercise','split');
  for(const s of ['3',' ３ ','+03']) assert.equal(responseOption(f,s),f.correctOptionId);
  assert.equal(responseOption(f,'  '),undefined);
  for(const s of ['2','3.0','3e0','0x3','NaN','Infinity','9007199254740993']) assert.equal(responseOption(f,s),f.input.incorrectOptionId);
});
test('text responses normalize formatting without merging distinct values',()=>{
  const f=input('l1-transformation','filter');
  for(const s of ['4,7',' ４，７ ','[4, 7]','4 7','4、7']) assert.equal(responseOption(f,s),f.correctOptionId);
  for(const s of ['47','7,4','0,4,7','4,,7']) assert.equal(responseOption(f,s),f.input.incorrectOptionId);
  const count=input('l1-action','count');
  for(const s of ['ｃｏｕｎｔ',' count() ','count ()']) assert.equal(responseOption(count,s),count.correctOptionId);
  for(const s of ['COUNT','collect()']) assert.equal(responseOption(count,s),count.input.incorrectOptionId);
});
test('word counts support formatting, not incorrect counts or partial answers',()=>{
  const f=input('l1-rdd-exercise','bridge-reduce-key');
  assert.equal(responseOption(f,' spark = 2， sql = 1 '),f.correctOptionId);
  for(const s of ['spark=1,sql=1','spark=2','spark=2sql=1']) assert.equal(responseOption(f,s),f.input.incorrectOptionId);
  assert.equal(normalizeResponse('   ','text'),null);
});
