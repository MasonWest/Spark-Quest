import RichText from "./RichText";
import type { JourneyTask } from "../content/journeys";

import { extractReading } from "./readingExcerpt";

export default function JourneyReading({ reading, explanation, checked, correct }: {
  reading: NonNullable<JourneyTask["reading"]>; explanation: string; checked: boolean; correct: boolean;
}) {
  const excerpt = extractReading(explanation, reading.startMarker, reading.endMarker);
  function openReference() {
    const full = document.getElementById("lesson-reference");
    if (full instanceof HTMLDetailsElement) {
      full.open = true;
      full.querySelector("summary")?.focus();
      full.scrollIntoView({ block: "start", behavior: "auto" });
    }
  }
  return <aside className="lj-reading" aria-label="原文与本步的联系">
    {checked && correct && <p className="lj-reading-connection"><strong>把这次判断连成原理</strong><br />{reading.connection}</p>}
    <details key={`${reading.id}:${checked}:${correct}`}>
      <summary>{checked ? correct ? `想再深入：回到原文 · ${reading.sectionTitle ?? "心智模型"}` : "这一步没想通？借原文再想一想" : `需要一点解释？${reading.title}`}</summary>
      {excerpt ? <>{reading.caution && <p className="lj-reading-caution"><strong>阅读前先纠正一个口径</strong><br />{reading.caution}</p>}<p className="lj-reading-label">来自本课原文 · {reading.sectionTitle ?? "心智模型"}</p><blockquote className="lj-reading-quote"><RichText text={excerpt} /></blockquote><div className="lj-reading-boundary"><strong>这段解释的适用边界</strong><p>{reading.boundary}</p></div></> : <p>这段原文的位置有变化，可以展开完整讲解查阅。</p>}
      <button type="button" className="lj-reading-source" onClick={openReference}>打开本课完整原文 →</button>
    </details>
  </aside>;
}
