import { useEffect, useRef, useState } from "react";
import type { JourneyRemedy } from "../content/journeys";

export default function JourneyRemediation({ remedy, onAnswer, onReturn }: {
  remedy: JourneyRemedy; onAnswer: (answer: string) => void; onReturn: () => void;
}) {
  const [answer, setAnswer] = useState("");
  const [checked, setChecked] = useState(false);
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => { heading.current?.focus(); }, []);
  const option = remedy.field.options.find(o => o.id === answer);
  const correct = answer === remedy.field.correctOptionId;
  return <div className="lj-remediation" aria-label="同知识点变式验证">
    <p className="dfj-kicker">换一道小题 · 先把这个点想通</p>
    <h2 ref={heading} tabIndex={-1}>{remedy.title}</h2><p>{remedy.intro}</p>
    <pre className="dfj-code"><code>{remedy.code}</code></pre>
    <p><strong>{remedy.prompt}</strong></p>
    <fieldset className="dfj-options"><legend>{remedy.field.label}</legend>{remedy.field.options.map(o => <label key={o.id} className={`dfj-option${answer === o.id ? " dfj-selected" : ""}`}><input type="radio" name={remedy.id} checked={answer === o.id} disabled={checked} onChange={() => setAnswer(o.id)} /><span>{o.text}</span></label>)}</fieldset>
    {checked && <div className={`dfj-feedback${correct ? " dfj-correct" : ""}`} role="status"><strong>{correct ? "变式判断正确，再回原题确认" : "再分清这一点"}</strong><p>{option?.feedback}</p>{correct && <p>{remedy.insight}</p>}</div>}
    <div className="dfj-actions">{!checked ? <button className="btn-primary" disabled={!answer} onClick={() => { setChecked(true); onAnswer(answer); }}>检查变式</button> : correct ? <button className="btn-primary" onClick={onReturn}>回原题再判断 →</button> : <button className="btn-primary" onClick={() => { setChecked(false); setAnswer(""); }}>再想一次</button>}{!(checked && correct) && <button className="btn-ghost" onClick={onReturn}>先回原题</button>}</div>
    <p className="dfj-footnote">这道小题不增加课程进度，也不改变正式成绩。通过后仍需回到原题完成判断。</p>
  </div>;
}
