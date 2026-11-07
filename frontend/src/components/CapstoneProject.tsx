import { useState } from "react";
import { Link } from "react-router-dom";
import type { LessonDetail } from "../types";
import "./CapstoneProject.css";

export interface Capstone {
  id: string; title: string; estimatedMinutes: number; brief: string; contract: string[];
  downloads: { label: string; href: string }[]; solution: { label: string; href: string }; command: string;
  checks: { title: string; body: string }[]; hints: { title: string; body: string }[];
}
type Draft = { prediction: string; plan: string; reflection: string };
const empty: Draft = { prediction: "", plan: "", reflection: "" };

export default function CapstoneProject({ project, detail }: { project: Capstone; detail: LessonDetail }) {
  const key = `spark-quest:capstone:${project.id}:draft`;
  const [draft, setDraft] = useState<Draft>(() => {
    try {
      const raw = localStorage.getItem(key);
      if (!raw) return empty;
      const value = JSON.parse(raw);
      return ["prediction", "plan", "reflection"].every(k => typeof value?.[k] === "string") ? value : empty;
    } catch { return empty; }
  });
  const [notice, setNotice] = useState("");
  const [hints, setHints] = useState(0);
  const [reference, setReference] = useState(false);
  function save() {
    try { localStorage.setItem(key, JSON.stringify(draft)); setNotice("草稿已保存在当前浏览器；这不是实作验收结果。"); }
    catch { setNotice("暂时无法保存，请先复制草稿到本地文件。实作仍可继续。"); }
  }
  return <section className="cp-root" aria-label="L2 独立毕业实作">
    <header className="cp-header"><p>毕业任务 · 约 {project.estimatedMinutes} 分钟</p><h2>{project.title}</h2><p>{project.brief}</p></header>
    <div className="cp-body">
      <section><h3>01 接任务，先读交付约定</h3><ol className="cp-contract">{project.contract.map(rule => <li key={rule}>{rule}</li>)}</ol><p>使用与六步准备练习不同的新数据，先不要打开参考实现。</p>
        <div className="cp-downloads">{project.downloads.map(asset => <a key={asset.href} href={asset.href} download>{asset.label} ↓</a>)}</div>
      </section>
      <section><h3>02 自己推导，再动手写</h3><label className="cp-field">你预测会留下哪些订单？各地区应得到什么？<textarea value={draft.prediction} onChange={e => { setDraft({ ...draft, prediction: e.target.value }); setNotice(""); }} rows={4} placeholder="先算笔数、金额与单位；结果相同的地区也要分别核对。" /></label>
        <label className="cp-field">你的实现计划<textarea value={draft.plan} onChange={e => { setDraft({ ...draft, plan: e.target.value }); setNotice(""); }} rows={3} placeholder="写下每一步负责什么。代码请在下载的 starter.py 中完成。" /></label>
        <details><summary>我卡住了，给一点提示</summary><p>按需逐级展开，先试着继续，再看下一层。</p>{project.hints.slice(0, hints).map((hint, i) => <div className="cp-hint" key={hint.title}><strong>提示 {i + 1} · {hint.title}</strong><p>{hint.body}</p></div>)}{hints < project.hints.length && <button className="btn-ghost" onClick={() => setHints(n => n + 1)}>{hints === 0 ? "给我一个方向" : hints === 1 ? "提示再具体一点" : "看处理顺序骨架"}</button>}</details>
      </section>
      <section><h3>03 让结果接受检查</h3><p>实现 starter.py 中的三个函数，将四个下载文件放在同一目录，在已配置的 PySpark 环境执行：</p><pre className="cp-command"><code>{project.command}</code></pre>
        <ul className="cp-checks">{project.checks.map(check => <li key={check.title}><strong>{check.title}</strong><p>{check.body}</p></li>)}</ul>
        <p>完整验收输出 PASS，且 files=PASS。只运行 --query-only 会输出 PARTIAL；查询通过也要完成文件验收。Windows 若出现 NativeIO / winutils 错误，请先看运行说明排查环境。</p>
        <p className="cp-note">浏览器不执行你的脚本，也不会自动读取本地结果。validation-result.json 是本次本地验收记录，不会改写课程成绩、解锁或连续天数。</p>
      </section>
      <section><h3>04 复盘，再决定是否对照</h3><label className="cp-field">哪项检查失败过？你如何修正？<textarea value={draft.reflection} onChange={e => { setDraft({ ...draft, reflection: e.target.value }); setNotice(""); }} rows={3} placeholder="区分查询错误和环境问题；看过提示或参考实现也可以如实记录。" /></label>
        <button className="btn-ghost" onClick={save}>保存本机草稿</button>{notice && <p role="status">{notice}</p>}
        <details><summary>我已经尝试，想对照参考实现</summary><p>先保留自己的实现和失败记录。对照之后，再换一份输入检查规则；看懂参考实现不等于独立完成。</p>{reference ? <a href={project.solution.href} download>{project.solution.label} ↓</a> : <button className="btn-ghost" onClick={() => setReference(true)}>展开参考实现下载</button>}</details>
      </section>
      <footer className="cp-footer"><p>想先练组合操作？下面保留了六步准备练习和标准讲解。正式测验仍按原有规则判分。</p><div className="cp-actions">{detail.status === "locked" ? <p>先掌握前一课，再进入正式测验。</p> : <Link className="btn-ghost" to={detail.status === "mastered" ? `/review/${detail.id}` : `/lesson/${detail.id}/quiz`}>{detail.status === "mastered" ? "进入正式复习" : "进入课后测验"} →</Link>}<Link className="btn-ghost" to="/map">返回学习路线</Link></div></footer>
    </div>
  </section>;
}
