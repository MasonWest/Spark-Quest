import { useRef, type ReactNode } from "react";
import "./ReadingPanel.css";

/** Long reading stays in the page; its exit controls stay within reach. */
export default function ReadingPanel({ id, title, collapseLabel, children }: {
  id: string; title: string; collapseLabel: string; children: ReactNode;
}) {
  const panel = useRef<HTMLDetailsElement>(null);
  function leave(backToPractice: boolean) {
    const details = panel.current;
    if (!details) return;
    const summary = details.querySelector<HTMLElement>(":scope > summary");
    const practice = details.closest(".lesson-container")?.querySelector<HTMLElement>("[data-journey-heading]");
    const target = backToPractice ? practice ?? summary : summary;
    details.open = false;
    // The capstone's optional practice may be inside another collapsed panel.
    if (target) {
      let parent = target.parentElement;
      while (parent) {
        if (parent instanceof HTMLDetailsElement && parent !== details) parent.open = true;
        parent = parent.parentElement;
      }
      requestAnimationFrame(() => {
        if (!target.isConnected) return;
        target.focus({ preventScroll: true });
        target.scrollIntoView({ block: "start", behavior: "auto" });
      });
    }
  }
  const actions = <>
    <button type="button" onClick={() => leave(false)}>{collapseLabel}</button>
    <button type="button" className="lrp-return" onClick={() => leave(true)}>返回当前练习 ↑</button>
  </>;
  return <details ref={panel} className="dfj-reference lrp-panel" id={id}>
    <summary>{title}</summary>
    <div className="lrp-toolbar" role="group" aria-label="阅读导航">{actions}</div>
    <div className="lrp-content">{children}</div>
    <div className="lrp-footer" role="group" aria-label="读完后的操作">{actions}</div>
  </details>;
}
