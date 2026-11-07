import type { JourneyLesson } from "../content/journeys";
import { loadProgress } from "./journeyProgress";
export interface DelayedItem { id: string; slug: string; taskId: string; knowledgeId: string; title: string; prompt: string; code: string; options: {id: string; text: string}[]; correctOptionId: string; explanation: string }
export interface DelayedEvent { itemId: string; sourceAt: string; answer: string; correctOptionId: string; correct: boolean; at: string }
export interface DelayedCandidate { item: DelayedItem; sourceAt: string; dueAt: number }
export const delayedKey = "spark-quest:delayed:v1";
export const day = 24 * 60 * 60 * 1000;
type Store = Pick<Storage, "getItem" | "setItem">;
export function loadDelayed(storage: Store): DelayedEvent[] {
  const raw = storage.getItem(delayedKey);
  if (!raw) return [];
  const events = JSON.parse(raw);
  if (!Array.isArray(events) || !events.every(e => e && typeof e.itemId === "string" && typeof e.answer === "string" && typeof e.correctOptionId === "string" && typeof e.correct === "boolean" && Number.isFinite(Date.parse(e.at)) && Number.isFinite(Date.parse(e.sourceAt)))) throw Error("无法读取验证记录");
  return events;
}
export function delayedQueue(items: DelayedItem[], lessons: Record<string, JourneyLesson>, storage: Store, now = Date.now()): DelayedCandidate[] {
  const events = loadDelayed(storage);
  return items.flatMap(item => {
    const lesson = lessons[item.slug];
    if (!lesson) return [];
    const progress = loadProgress(lesson, storage);
    const attempts = progress.attempts.filter(a => a.taskId === item.taskId && Number.isFinite(Date.parse(a.at)));
    if (!progress.completedIds.includes(item.taskId) || !attempts.some(a => !a.activity && a.correct)) return [];
    const sourceAt = attempts.reduce((latest, a) => Date.parse(a.at) > Date.parse(latest) ? a.at : latest, attempts[0].at);
    const after = events.filter(e => e.itemId === item.id && Date.parse(e.at) >= Date.parse(sourceAt));
    // A single successful delayed check retires this material until the learner
    // encounters the original concept again. Repeated known answers are not new evidence.
    if (after.some(e => e.correct)) return [];
    const dueAt = Math.max(Date.parse(sourceAt), ...after.map(e => Date.parse(e.at))) + day;
    return dueAt <= now ? [{ item, sourceAt, dueAt }] : [];
  }).sort((a,b) => a.dueAt - b.dueAt);
}
export function submitDelayed(candidate: DelayedCandidate, answer: string, items: DelayedItem[], lessons: Record<string, JourneyLesson>, storage: Store, now = Date.now()): DelayedEvent {
  const current = delayedQueue(items, lessons, storage, now).find(c => c.item.id === candidate.item.id && c.sourceAt === candidate.sourceAt);
  if (!current || !current.item.options.some(o => o.id === answer)) throw Error("这道题的安排已更新，请重新打开验证。");
  const event = { itemId: current.item.id, sourceAt: current.sourceAt, answer, correctOptionId: current.item.correctOptionId, correct: answer === current.item.correctOptionId, at: new Date(now).toISOString() };
  storage.setItem(delayedKey, JSON.stringify([...loadDelayed(storage), event]));
  return event;
}
