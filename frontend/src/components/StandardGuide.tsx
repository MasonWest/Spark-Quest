import type { StandardGuide as Guide } from "../content/standardGuides";
import RichText from "./RichText";
export default function StandardGuide({ guide }: { guide: Guide }) {
  return <details className="dfj-reference" id="lesson-reference"><summary>展开本课标准讲解</summary>
    <section className="card"><h2>{guide.title} · 标准讲解</h2><p>与互动步骤配套整理，集中说明概念、使用条件和验收方法。完整旧讲义与示例保留在下方历史原文中。</p>
      {guide.sections.map(section => <section key={section.id} id={`guide-${section.id}`}><h3>{section.title}</h3><RichText text={section.body} /><p><strong>使用边界：</strong>{section.boundary}</p></section>)}
      <h3>核对官方说明</h3><ul>{guide.sources.map(source => <li key={source.url}><a href={source.url} target="_blank" rel="noreferrer">{source.title} ↗</a></li>)}</ul>
    </section>
  </details>;
}
