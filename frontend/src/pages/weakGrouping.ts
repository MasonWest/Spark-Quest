import type { WeakQuestion } from "../types";

/**
 * Phase 10.1 UI 派生分组 —— 纯函数，零副作用、零持久化。
 *
 * 「历史错题」由后端 `GET /api/weak-questions` 给出（过滤条件 = 历史上至少答错过
 * 一次，**列表成员不因后来答对而改变**）。这里只在 UI 层把这批历史错题按「最近
 * 一次是否答对」再派生一次分类：
 *
 *   last_attempt_correct === false  ->  active     「待重练」最近一次仍然答错
 *   last_attempt_correct === true   ->  recovered  「已恢复」历史错过、最近一次已答对
 *
 * 明确边界：
 *   * 「已恢复」只是**读时算出来的 UI 分类**，不是 Mastery / SRS / 毕业状态，
 *     不写数据库、不新增字段、不产生第二套状态体系。
 *   * 历史统计（`wrong_count` / `last_wrong_at`）原样保留，恢复不清零、不洗历史。
 *   * 「最近一次」的跨来源聚合（quiz + review + practice）由后端负责，前端不重算。
 */
export interface WeakQuestionGroups {
  /** 待重练：最近一次仍答错 —— 默认展开，页面的主要内容 */
  active: WeakQuestion[];
  /** 已恢复：历史答错过但最近一次已答对 —— 默认折叠，降低视觉权重 */
  recovered: WeakQuestion[];
}

/** 按 `last_attempt_correct` 二分历史错题；组内保持后端给定的顺序（wrong_count DESC）。 */
export function groupWeakQuestions(list: WeakQuestion[]): WeakQuestionGroups {
  const active: WeakQuestion[] = [];
  const recovered: WeakQuestion[] = [];

  for (const q of list) {
    if (q.last_attempt_correct) recovered.push(q);
    else active.push(q);
  }

  return { active, recovered };
}
