import type { JourneyLesson } from "../content/journeys";

export interface Attempt {
  runId: string; taskId: string; answers: Record<string, string>;
  correctOptions: Record<string, string>; correct: boolean; at: string;
  activity?: "remediation"; remediationId?: string; knowledgeId?: string;
}
export interface JourneyProgress {
  version: number; runId: string; cursorId: string | null;
  completedIds: string[]; migratedIds: string[]; attempts: Attempt[];
}
type Storage = Pick<globalThis.Storage, "getItem" | "setItem">;
export const progressKey = (lesson: JourneyLesson) => `spark-quest:learning:${lesson.slug}:v${lesson.version}`;
export function freshProgress(lesson: JourneyLesson): JourneyProgress {
  return { version: lesson.version, runId: globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(36).slice(2)}`, cursorId: lesson.tasks[0].id, completedIds: [], migratedIds: [], attempts: [] };
}
export function loadProgress(lesson: JourneyLesson, storage: Storage): JourneyProgress {
  const fresh = freshProgress(lesson);
  const ids = new Set(lesson.tasks.map(t => t.id));
  try {
    const raw = storage.getItem(progressKey(lesson));
    if (raw) {
      const p = JSON.parse(raw);
      if (p.version !== lesson.version || typeof p.runId !== "string" || !Array.isArray(p.completedIds) || !p.completedIds.every((id: unknown) => typeof id === "string" && ids.has(id)) || !(p.cursorId === null || ids.has(p.cursorId)) || !Array.isArray(p.attempts) || !Array.isArray(p.migratedIds) || !p.migratedIds.every((id: string) => ids.has(id))) return fresh;
      if (!p.attempts.every((a: Attempt) => a && typeof a.runId === "string" && typeof a.taskId === "string" && typeof a.correct === "boolean" && typeof a.at === "string" && a.answers && a.correctOptions)) return fresh;
      if (p.cursorId === null && !lesson.tasks.every(t => p.completedIds.includes(t.id))) return fresh;
      return p;
    }
    // Only the frozen v1 migration uses old positional progress. Later versions
    // never reinterpret an older cursor against a changed task order.
    if (lesson.version === 1 && lesson.legacyTaskIds) {
      const oldKey = lesson.slug === "l2-what-is-dataframe" ? "spark-quest:df-intro:v1" : `spark-quest:journey:${lesson.slug}:v1`;
      const rawOld = storage.getItem(oldKey);
      const old = rawOld === null ? null : JSON.parse(rawOld);
      const step = typeof old === "number" ? old : old?.step;
      if (Number.isInteger(step) && step >= 0 && step <= lesson.tasks.length) {
        const completedIds = lesson.legacyTaskIds.slice(0, step);
        return { ...fresh, cursorId: lesson.legacyTaskIds[step] ?? null, completedIds, migratedIds: lesson.legacyTaskIds.slice(0, Math.min(step + 1, lesson.tasks.length)) };
      }
    }
  } catch { /* Private browsing and corrupt local data fall back safely. */ }
  return fresh;
}
export function recordAttempt(lesson: JourneyLesson, p: JourneyProgress, taskId: string, answers: Record<string, string>): JourneyProgress {
  const task = lesson.tasks.find(t => t.id === taskId)!;
  const correctOptions = Object.fromEntries(task.fields.map(f => [f.id, f.correctOptionId]));
  const correct = task.fields.every(f => answers[f.id] === f.correctOptionId);
  return { ...p, attempts: [...p.attempts, { runId: p.runId, taskId, answers: { ...answers }, correctOptions, correct, at: new Date().toISOString() }] };
}
export function evidence(p: JourneyProgress, taskId: string): string {
  const attempts = p.attempts.filter(a => a.runId === p.runId && a.taskId === taskId && a.activity !== "remediation");
  const verified = p.attempts.some(a => a.runId === p.runId && a.taskId === taskId && a.activity === "remediation" && a.correct) ? " · 已通过一道变式" : "";
  if (p.migratedIds.includes(taskId)) return attempts.length ? `旧版迁入后作答 ${attempts.length} 次 · 首次记录不完整` : "旧版进度已保留 · 没有首次作答记录";
  if (!attempts.length) return "尚无作答记录";
  return (attempts[0].correct ? "本轮首次答对 · 仍需隔天验证" : `本轮原题作答 ${attempts.length} 次 · 借助反馈后完成`) + verified;
}

export function recordRemediation(lesson: JourneyLesson, p: JourneyProgress, taskId: string, answer: string): JourneyProgress {
  const remedy = lesson.tasks.find(t => t.id === taskId)?.remediation;
  if (!remedy || !remedy.field.options.some(o => o.id === answer)) throw new Error("Invalid remediation answer");
  return { ...p, attempts: [...p.attempts, { runId: p.runId, taskId, activity: "remediation", remediationId: remedy.id, knowledgeId: remedy.knowledgeId, answers: { [remedy.field.id]: answer }, correctOptions: { [remedy.field.id]: remedy.field.correctOptionId }, correct: answer === remedy.field.correctOptionId, at: new Date().toISOString() }] };
}
