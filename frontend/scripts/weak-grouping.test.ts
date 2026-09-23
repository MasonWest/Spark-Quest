// Phase 10.1 UI 派生分组的纯逻辑测试。
//
// 运行（node 22 内置测试运行器 + TS type stripping，**零新依赖**）：
//     cd frontend && node --test scripts/weak-grouping.test.ts
// 或：
//     cd frontend && npm run test:weak-grouping
//
// 放在 scripts/ 而不是 src/ 是有原因的：tsconfig 是 include:["src"] + strict，
// 测试文件若放进 src/，`import { test } from "node:test"` 会因缺少 @types/node
// 让 `tsc -b` 直接失败。scripts/ 不在 tsconfig 范围内，`tsc -b` 完全不看它。

import { test } from "node:test";
import assert from "node:assert/strict";
import { groupWeakQuestions } from "../src/pages/weakGrouping.ts";
import type { WeakQuestion } from "../src/types.ts";

function q(over: Partial<WeakQuestion> & { question_id: number }): WeakQuestion {
  return {
    lesson_id: 1,
    lesson_title: "示例课",
    level_order: 1,
    dimension: "分区",
    prompt: "示例题干",
    wrong_count: 1,
    last_wrong_at: "2026-09-01T10:00:00",
    last_attempt_at: "2026-09-01T10:00:00",
    last_attempt_correct: false,
    ...over,
  };
}

test("错 → 错：归入待重练", () => {
  const g = groupWeakQuestions([q({ question_id: 1, last_attempt_correct: false })]);
  assert.equal(g.active.length, 1);
  assert.equal(g.recovered.length, 0);
  assert.equal(g.active[0].question_id, 1);
});

test("错 → 对：归入已恢复", () => {
  const g = groupWeakQuestions([q({ question_id: 2, last_attempt_correct: true })]);
  assert.equal(g.active.length, 0);
  assert.equal(g.recovered.length, 1);
  assert.equal(g.recovered[0].question_id, 2);
});

test("错 → 错 → 对：归入已恢复，且 wrong_count 历史值原样保留", () => {
  const g = groupWeakQuestions([
    q({ question_id: 3, wrong_count: 2, last_attempt_correct: true }),
  ]);
  assert.equal(g.recovered.length, 1);
  assert.equal(g.active.length, 0);
  // 恢复不等于洗历史
  assert.equal(g.recovered[0].wrong_count, 2);
});

test("只答对：本身不在入参里（准入规则由后端负责），分组不得凭空造题", () => {
  const g = groupWeakQuestions([]);
  assert.deepEqual(g, { active: [], recovered: [] });
});

test("分组不修改入参、不丢题：进多少出多少", () => {
  const list = [
    q({ question_id: 10, last_attempt_correct: false, wrong_count: 3 }),
    q({ question_id: 11, last_attempt_correct: true, wrong_count: 1 }),
    q({ question_id: 12, last_attempt_correct: false, wrong_count: 2 }),
  ];
  const snapshot = JSON.parse(JSON.stringify(list));
  const g = groupWeakQuestions(list);

  assert.equal(g.active.length + g.recovered.length, list.length);
  assert.deepEqual(
    list.map((x) => x.question_id),
    snapshot.map((x: WeakQuestion) => x.question_id)
  );
  assert.deepEqual(list, snapshot, "分组必须是纯函数，不得改动入参对象");
  // 组内保持后端顺序（wrong_count DESC）
  assert.deepEqual(
    g.active.map((x) => x.question_id),
    [10, 12]
  );
});

test("真实分布 17 = 待重练 1 + 已恢复 16，且历史统计不被清零", () => {
  const list = [
    q({ question_id: 100, last_attempt_correct: false, wrong_count: 2 }),
    ...Array.from({ length: 16 }, (_, i) =>
      q({
        question_id: 200 + i,
        last_attempt_correct: true,
        wrong_count: i % 3 === 0 ? 3 : 1,
      })
    ),
  ];
  const g = groupWeakQuestions(list);

  assert.equal(g.active.length, 1);
  assert.equal(g.recovered.length, 16);
  assert.equal(
    g.recovered.reduce((sum, x) => sum + x.wrong_count, 0),
    list.slice(1).reduce((sum, x) => sum + x.wrong_count, 0)
  );
  assert.ok(g.recovered.every((x) => x.wrong_count >= 1));
});

test("全部已恢复：待重练为空（页面据此显示独立空态）", () => {
  const g = groupWeakQuestions([
    q({ question_id: 301, last_attempt_correct: true }),
    q({ question_id: 302, last_attempt_correct: true }),
  ]);
  assert.equal(g.active.length, 0);
  assert.equal(g.recovered.length, 2);
});
