import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import bank from "../content/delayedChecks.json";
import { journeyIndex } from "../content/journeys";
import { delayedQueue, submitDelayed, type DelayedCandidate, type DelayedEvent } from "../components/delayedProgress";
import "../components/Journey.css";
import "../components/LessonJourney.css";
export default function DelayedCheckPage() {
  const [initial] = useState<{ queue: DelayedCandidate[]; error: string }>(() => { try { return { queue: delayedQueue(bank.items, journeyIndex, localStorage), error: "" }; } catch { return { queue: [], error: "暂时无法读取本机练习记录。请检查浏览器存储权限，或回原设备继续；现有记录不会被覆盖。" }; } });
  const queue = initial.queue;
  const [index, setIndex] = useState(0);
  const [answer, setAnswer] = useState("");
  const [result, setResult] = useState<DelayedEvent | null>(null);
  const [error, setError] = useState("");
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => { heading.current?.focus(); }, [index]);
  const candidate = queue[index];
  const item = candidate?.item;
  function submit() {
    try { setResult(submitDelayed(candidate, answer, bank.items, journeyIndex, localStorage)); setError(""); }
    catch { setError("暂时无法保存，或这道题的安排已经更新。请返回首页后重新打开；本次没有记为完成。"); }
  }
  return <main className="container"><Link to="/">← 返回首页</Link><section className="dfj-root"><div className="dfj-body">
    <p className="dfj-kicker">隔天验证 · 本机练习</p>
    {initial.error && <p role="alert">{initial.error}</p>}
    {!item ? <><h1 ref={heading} tabIndex={-1}>{initial.error ? "暂时无法读取验证安排" : queue.length ? "这一轮验证结束了" : "暂时没有到期的验证"}</h1><p>{queue.length ? "答对的情境已收起；答错的知识点至少 24 小时后再试。这一轮结果只用于观察记忆，不代表已掌握。" : "先完成相关互动步骤，离开题目至少 24 小时后再来。目前覆盖 L0–L7 的重点知识点，记录保存在当前浏览器。"}</p><Link className="btn-primary" to="/map">继续学习 →</Link></> : <>
      <p>第 {index + 1} 题 / 共 {queue.length} 题 · {journeyIndex[item.slug].title}</p>
      <h1 ref={heading} tabIndex={-1}>{item.title}</h1><p>先独立判断，提交后再看解释。</p>
      <pre className="dfj-code"><code>{item.code}</code></pre><p><strong>{item.prompt}</strong></p>
      <fieldset className="dfj-options"><legend>你的判断</legend>{item.options.map(o => <label key={o.id} className={`dfj-option${answer === o.id ? " dfj-selected" : ""}`}><input type="radio" name={item.id} checked={answer === o.id} disabled={!!result} onChange={() => setAnswer(o.id)} /><span>{o.text}</span></label>)}</fieldset>
      {error && <p role="alert">{error}</p>}
      {result && <div className={`dfj-feedback${result.correct ? " dfj-correct" : ""}`} role="status"><strong>{result.correct ? "隔了一天，这次独立判断正确" : "这个点还需要巩固"}</strong><p>正确判断：{item.options.find(o => o.id === item.correctOptionId)?.text}</p><p>{item.explanation}</p><p>{result.correct ? "这道材料先收起，不反复用同一道题证明掌握。" : "可以回学习路线找到本课重练。至少 24 小时后再判断；再次出现时可能已记得这道材料的答案。"}</p></div>}
      <div className="dfj-actions">{result ? <button className="btn-primary" onClick={() => { setIndex(i => i + 1); setAnswer(""); setResult(null); setError(""); }}>{index + 1 === queue.length ? "完成这一轮 →" : "验证下一个 →"}</button> : <button className="btn-primary" disabled={!answer} onClick={submit}>提交判断</button>}<Link className="btn-ghost" to="/map">回学习路线</Link></div>
      <p className="dfj-footnote">不计入正式成绩、连续学习天数或课程解锁。离开后，已提交的结果保留，未答的题仍可继续。</p>
    </>}
  </div></section></main>;
}
