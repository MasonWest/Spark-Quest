import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import type { LessonDetail } from "../types";
import { evidence, freshProgress, loadProgress, progressKey, recordAttempt, recordRemediation, type JourneyProgress } from "./journeyProgress";
import type { JourneyLesson } from "../content/journeys";
import JourneyRemediation from "./JourneyRemediation";
import DelayedCheckLink from "./DelayedCheckLink";
import { standardGuides } from "../content/standardGuides";
import JourneyReading from "./JourneyReading";
import "./Journey.css";
import "./LessonJourney.css";
import { responseOption } from "./journeyAnswer";

export default function LessonJourney({ lesson, detail }: { lesson: JourneyLesson; detail: LessonDetail }) {
  const [progress, setProgress] = useState<JourneyProgress>(() => {
    try { return loadProgress(lesson, localStorage); } catch { return freshProgress(lesson); }
  });
  const [saved, setSaved] = useState(true);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [responses, setResponses] = useState<Record<string, string>>({});
  const [remediationActive, setRemediationActive] = useState(false);
  const [checked, setChecked] = useState(false);
  const heading = useRef<HTMLHeadingElement>(null);
  const step = progress.cursorId === null ? lesson.tasks.length : Math.max(0, lesson.tasks.findIndex(t => t.id === progress.cursorId));
  const task = lesson.tasks[step];
  const done = progress.cursorId === null;
  const allCorrect = !!task && task.fields.every(f => answers[f.id] === f.correctOptionId);
  function save(next: JourneyProgress) {
    setProgress(next);
    try { localStorage.setItem(progressKey(lesson), JSON.stringify(next)); setSaved(true); } catch { setSaved(false); }
  }
  function move(next: number) {
    const completedIds = allCorrect && next === step + 1 ? [...new Set([...progress.completedIds, task.id])] : progress.completedIds;
    save({ ...progress, completedIds, cursorId: lesson.tasks[next]?.id ?? null }); setAnswers({}); setResponses({}); setChecked(false); setRemediationActive(false);
    requestAnimationFrame(() => heading.current?.focus());
  }
  function check() {
    setChecked(true);
    const next = recordAttempt(lesson, progress, task.id, answers);
    if (task.fields.some(f => f.input)) next.attempts[next.attempts.length - 1].responses = { ...responses };
    save(next);
  }
  return <section className="dfj-root" aria-label={lesson.title}>
    <div className="dfj-heading"><span>{lesson.title}</span><strong>{progress.completedIds.length} / {lesson.tasks.length}</strong></div>
    <progress className="dfj-progress" value={progress.completedIds.length} max={lesson.tasks.length} aria-label="本节互动进度" />
    <div className="dfj-body">
      {!saved && <p role="status" className="lj-storage-note">此设备暂时不能保存进度，本次练习仍可继续。</p>}
      {done ? <>
        <p className="dfj-kicker">本节互动完成</p><h2 ref={heading} tabIndex={-1}>这次练会了什么？</h2>
        <ul className="dfj-outcomes">{lesson.tasks.map(t => <li key={t.id}><strong>{t.ability}</strong><small className="lj-evidence">{evidence(progress, t.id)}</small></li>)}</ul>
        <DelayedCheckLink />{lesson.tasks.some(t => t.remediation) && <p>离开这些题目至少 24 小时后，首页会出现「隔天验证」，换个情境看看还记得多少。请在当前浏览器继续，练习记录保存在本机。</p>}<p>{lesson.next}</p><p className="dfj-footnote">这是本设备的练习记录，不是独立编程能力认证。课后测验继续使用原有掌握与解锁规则。</p>
        {lesson.project && <div className="lj-project"><h3>把选择变成自己的代码</h3><p>下载输入和任务骨架，先独立实现，再对照。脚本在本地运行，应用不会自动判定你已掌握。</p><ProjectDownloads lesson={lesson} /><details><summary>展开参考实现下载</summary><p>{lesson.project.solutionNote ?? "参考实现写入每次新建的练习目录，不覆盖已有结果；包含逐地区验收断言。"}</p><a href={lesson.project.solution.href} download>{lesson.project.solution.label}</a></details></div>}
        <div className="lj-finish-actions">
          {detail.status === "locked" ? <p>先掌握前一课，再进入正式测验。</p> : detail.status === "mastered" ? <><p>正式课程已掌握，当前得分 {detail.mastery_score ?? 0}%。</p><Link className="btn-primary" to={`/review/${detail.id}`}>间隔复习（5 题）</Link>{detail.next_lesson && <Link className="btn-ghost" to={`/lesson/${detail.next_lesson.id}`}>下一课：{detail.next_lesson.title} →</Link>}</> : <Link className="btn-primary" to={`/lesson/${detail.id}/quiz`}>开始测验</Link>}
          <Link to="/map" className="btn-ghost">返回学习路线</Link>
        </div>
        <button className="btn-ghost" onClick={() => { save({ ...freshProgress(lesson), attempts: progress.attempts }); setAnswers({}); setResponses({}); setChecked(false); setRemediationActive(false); requestAnimationFrame(() => heading.current?.focus()); }}>重新练一遍</button>
      </> : remediationActive && task.remediation ? <JourneyRemediation key={task.remediation.id} remedy={task.remediation} onAnswer={answer => save(recordRemediation(lesson, progress, task.id, answer))} onReturn={() => { setRemediationActive(false); setAnswers({}); setResponses({}); setChecked(false); requestAnimationFrame(() => heading.current?.focus()); }} /> : <>
        <p className="dfj-kicker">第 {step + 1} 步 / 共 {lesson.tasks.length} 步 · {task.fields.some(f => f.input) ? "自己填写" : task.fields.length > 1 ? "补齐方案" : "推理判断"}</p>
        <h2 ref={heading} tabIndex={-1}>{task.title}</h2>
        {step === 0 && <p className="lj-mission">{lesson.mission}</p>}
        {step === 0 && lesson.project && <div className="lj-project"><strong>先自己动手，也可以边做边核对</strong><ProjectDownloads lesson={lesson} /></div>}
        <p>{task.intro}</p>{task.table && <div className="dfj-table-wrap"><table className="dfj-table"><caption>{task.table.caption ?? "订单样本"}</caption><thead><tr>{task.table.columns.map(c => <th key={c}>{c}</th>)}</tr></thead><tbody>{task.table.rows.map((r, i) => <tr key={i}>{r.map((v, j) => <td key={j}>{v}</td>)}</tr>)}</tbody></table></div>}<pre className="dfj-code"><code>{task.code}</code></pre><p><strong>{task.prompt}</strong></p>
        {task.fields.some(f => f.input) ? <div className="lj-fields">{task.fields.map(field => <label className="lj-field" key={field.id}><span>{field.label}</span><input type="text" inputMode={field.input?.kind === "integer" ? "numeric" : "text"} autoComplete="off" autoCapitalize="off" spellCheck={false} maxLength={160} placeholder={field.input?.placeholder} value={responses[field.id] ?? ""} disabled={checked} onChange={event => {
          const raw = event.target.value;
          setResponses(prev => ({ ...prev, [field.id]: raw }));
          setAnswers(prev => ({ ...prev, [field.id]: responseOption(field, raw) ?? "" }));
        }} /><small>直接填写；前后空格与全角字符会统一处理。{field.input?.kind === "integer" && "请输入整数。"}</small></label>)}</div> : task.fields.length === 1 ? <fieldset className="dfj-options"><legend>{task.fields[0].label}</legend>{task.fields[0].options.map((option) => <label className={`dfj-option${answers[task.fields[0].id] === option.id ? " dfj-selected" : ""}`} key={option.id}><input type="radio" name={`${lesson.slug}-${task.id}`} checked={answers[task.fields[0].id] === option.id} disabled={checked} onChange={() => setAnswers({ [task.fields[0].id]: option.id })} /><span>{option.text}</span></label>)}</fieldset> : <div className="lj-fields">{task.fields.map((field) => <label className="lj-field" key={field.label}><span>{field.label}</span><select value={answers[field.id] ?? ""} disabled={checked} onChange={event => setAnswers(prev => ({ ...prev, [field.id]: event.target.value }))}><option value="" disabled>选择填入的内容</option>{field.options.map(option => <option value={option.id} key={option.id}>{option.text}</option>)}</select></label>)}</div>}
        {checked && <div className={`dfj-feedback${allCorrect ? " dfj-correct" : ""}`} role="status"><strong>{allCorrect ? "方案成立，看看背后的原因" : "有一处需要再想想"}</strong>{task.fields.map((field, i) => <p key={i}>{task.fields.length > 1 && <b>{field.label}：<br /></b>}{field.options.find(o => o.id === answers[field.id])?.feedback}</p>)}{allCorrect && <p>{task.insight}</p>}</div>}
        {task.reading && <JourneyReading standard={standardGuides[lesson.slug]?.sections.find(s => s.id === task.id)} reading={task.reading} explanation={detail.content.explanation} checked={checked} correct={allCorrect} />}
        <div className="dfj-actions">{!checked ? <button className="btn-primary" disabled={task.fields.some(f => !answers[f.id])} onClick={check}>检查判断</button> : allCorrect ? <button className="btn-primary" onClick={() => move(step + 1)}>{step === lesson.tasks.length - 1 ? "看看我的收获" : "继续下一步 →"}</button> : task.remediation ? <><button className="btn-primary" onClick={() => setRemediationActive(true)}>换一道小题验证 →</button><button className="btn-ghost" onClick={() => { setChecked(false); }}>先重试原题</button></> : <button className="btn-primary" onClick={() => { setChecked(false); }}>调整后再试</button>}{step > 0 && <button className="btn-ghost" onClick={() => move(step - 1)}>回看上一步</button>}</div>
        <p className="dfj-footnote">代码用于推演，不会在浏览器中执行。可以重试，不扣分；完成的步骤会在此设备保存。</p>
      </>}
    </div>
  </section>;
}

function ProjectDownloads({ lesson }: { lesson: JourneyLesson }) {
  return <div className="lj-downloads">{lesson.project?.downloads.map(d => <a key={d.href} href={d.href} download>{d.label}</a>)}</div>;
}
