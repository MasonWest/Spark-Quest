import type { StandardSection } from "../content/standardGuides";
import RichText from "./RichText";
import type { JourneyTask } from "../content/journeys";

import { extractReading } from "./readingExcerpt";

export default function JourneyReading({ reading, explanation, checked, correct, standard }: {
  reading: NonNullable<JourneyTask["reading"]>; explanation: string; checked: boolean; correct: boolean; standard?: StandardSection;
}) {
  const excerpt = extractReading(explanation, reading.startMarker, reading.endMarker);
  function openReference(id = "lesson-reference") {
    const full = document.getElementById(id);
    if (full instanceof HTMLDetailsElement) {
      full.open = true;
      full.querySelector("summary")?.focus();
      full.scrollIntoView({ block: "start", behavior: "auto" });
    }
  }
  if (standard) return <aside className="lj-reading" aria-label="标准讲解与本步的联系">
    {checked && correct && <p className="lj-reading-connection"><strong>把这次判断连成原理</strong><br />{reading.connection}</p>}
    <details key={`${reading.id}:${checked}:${correct}`}>
      <summary>{checked ? correct ? `想再深入：${standard.title}` : "这一步没想通？看看标准讲解" : `需要一点解释？${standard.title}`}</summary>
      <p className="lj-reading-label">本课标准讲解 · {standard.title}</p>
      <blockquote className="lj-reading-quote"><RichText text={standard.body} /></blockquote>
      <div className="lj-reading-boundary"><strong>这段解释的适用边界</strong><p>{standard.boundary}</p></div>
      <button type="button" className="lj-reading-source" onClick={() => openReference()}>打开本课标准讲解 →</button>
      <details><summary>对照历史原文</summary>
        {reading.caution && <p className="lj-reading-caution"><strong>历史原文中的口径提醒</strong><br />{reading.caution}</p>}
        {excerpt ? <blockquote className="lj-reading-quote"><RichText text={excerpt} /></blockquote> : <p>这段历史原文的位置有变化，请打开完整历史原文查看。</p>}
        <button type="button" className="lj-reading-source" onClick={() => openReference("lesson-original")}>打开完整历史原文 →</button>
      </details>
    </details>
  </aside>;
  return <aside className="lj-reading" aria-label="原文与本步的联系">
    {checked && correct && <p className="lj-reading-connection"><strong>把这次判断连成原理</strong><br />{reading.connection}</p>}
    <details key={`${reading.id}:${checked}:${correct}`}>
      <summary>{checked ? correct ? `想再深入：回到原文 · ${reading.sectionTitle ?? "心智模型"}` : "这一步没想通？借原文再想一想" : `需要一点解释？${reading.title}`}</summary>
      {excerpt ? <>{reading.caution && <p className="lj-reading-caution"><strong>阅读前先纠正一个口径</strong><br />{reading.caution}</p>}<p className="lj-reading-label">来自本课原文 · {reading.sectionTitle ?? "心智模型"}</p><blockquote className="lj-reading-quote"><RichText text={excerpt} /></blockquote><div className="lj-reading-boundary"><strong>这段解释的适用边界</strong><p>{reading.boundary}</p></div></> : <p>这段原文的位置有变化，可以展开完整讲解查阅。</p>}
      <button type="button" className="lj-reading-source" onClick={() => openReference()}>打开本课完整原文 →</button>
    </details>
  </aside>;
}
