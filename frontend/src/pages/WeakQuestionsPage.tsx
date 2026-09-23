import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import type {
  WeakQuestion,
  WeakQuestionDetail,
  WeakQuestionPracticeResult,
} from "../types";
import { groupWeakQuestions } from "./weakGrouping";
import "./WeakQuestionsPage.css";

function relativeTime(iso: string | null): string {
  if (!iso) return "—";
  const then = new Date(iso).getTime();
  const days = Math.floor((Date.now() - then) / 86400000);
  if (days <= 0) return "今天";
  if (days === 1) return "昨天";
  if (days < 30) return `${days} 天前`;
  return iso.slice(0, 10);
}

type PracticeState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "open"; detail: WeakQuestionDetail }
  | {
      status: "result";
      detail: WeakQuestionDetail;
      result: WeakQuestionPracticeResult;
      selected: number;
    };

/** 一张错题卡。`recovered` 只决定视觉权重与文案，不改变任何数据语义。 */
function WeakCard({
  q,
  recovered,
  onPractice,
}: {
  q: WeakQuestion;
  recovered: boolean;
  onPractice: (q: WeakQuestion) => void;
}) {
  return (
    <article className={`weak-card${recovered ? " is-recovered" : ""}`}>
      <div className="weak-card-main">
        <div className="weak-prompt">
          {recovered ? (
            <span className="weak-ok" aria-hidden={true}>
              ✓
            </span>
          ) : (
            <span className="weak-x" aria-hidden={true}>
              ❌
            </span>
          )}
          <span className="weak-prompt-text">{q.prompt}</span>
        </div>
        <div className="weak-meta">
          <span className="weak-dim">
            {q.dimension ?? "未分类"} · L{q.level_order}
          </span>
          {/* 历史统计照旧显示：进入「已恢复」不等于把错误记录抹掉 */}
          <span className="weak-count">错误 {q.wrong_count} 次</span>
          {recovered ? (
            <span className="weak-count">
              最近一次答对 · {relativeTime(q.last_attempt_at)}
            </span>
          ) : (
            <span className="weak-count">
              最近一次答错 · {relativeTime(q.last_attempt_at)}
            </span>
          )}
        </div>
      </div>
      <button className="weak-practice-btn" onClick={() => onPractice(q)}>
        重新练习
      </button>
    </article>
  );
}

export default function WeakQuestionsPage() {
  const [list, setList] = useState<WeakQuestion[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [practice, setPractice] = useState<PracticeState>({ status: "idle" });
  const [practiceError, setPracticeError] = useState<string | null>(null);
  // 「已恢复」默认折叠，但折叠标题始终显示数量 —— 它们不是消失了，是已恢复。
  const [recoveredOpen, setRecoveredOpen] = useState(false);

  useEffect(() => {
    fetch("/api/weak-questions")
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json() as Promise<WeakQuestion[]>;
      })
      .then(setList)
      .catch((e) => setError(String(e)));
  }, []);

  function refreshList() {
    fetch("/api/weak-questions")
      .then((r) => r.json())
      .then((d) => setList(d as WeakQuestion[]))
      .catch(() => {});
  }

  async function openPractice(q: WeakQuestion) {
    setPractice({ status: "loading" });
    setPracticeError(null);
    try {
      const res = await fetch(`/api/weak-questions/${q.question_id}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const detail = (await res.json()) as WeakQuestionDetail;
      setPractice({ status: "open", detail });
    } catch (e) {
      setPracticeError(String(e));
      setPractice({ status: "idle" });
    }
  }

  async function submitPractice(selected: number, detail: WeakQuestionDetail) {
    setPracticeError(null);
    try {
      const res = await fetch(`/api/weak-questions/${detail.id}/practice`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ selected_index: selected }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const result = (await res.json()) as WeakQuestionPracticeResult;
      setPractice({ status: "result", detail, result, selected });
      refreshList(); // 最近一次对错可能已变化 → 该题可能在两组之间移动
    } catch (e) {
      setPracticeError(String(e));
    }
  }

  function closePractice() {
    setPractice({ status: "idle" });
    refreshList();
  }

  const count = list?.length ?? 0;
  const groups = groupWeakQuestions(list ?? []);

  return (
    <div className="container weak-page">
      <header className="weak-header">
        <Link to="/" className="back-link">
          ← 返回首页
        </Link>
        <h1 className="weak-title">🧠 薄弱题</h1>
        <p className="weak-sub">
          {list
            ? `共 ${count} 道 · 待重练 ${groups.active.length} · 已恢复 ${groups.recovered.length}`
            : "加载中…"}
        </p>
      </header>

      {error && (
        <div className="card">
          <span className="status error">加载失败：{error}</span>
        </div>
      )}

      {list && count === 0 && (
        <div className="card weak-empty">
          🎉 暂时没有薄弱题。答错的题会自动出现在这里——过段时间再回来，独立重做它们。
        </div>
      )}

      {list && count > 0 && (
        <>
          {/* 第一组：待重练 —— 最近一次仍然答错的题，页面的主要内容 */}
          <section className="weak-group">
            <h2 className="weak-group-head">
              <span
                className="weak-group-mark weak-group-mark-bad"
                aria-hidden={true}
              >
                🔴
              </span>
              <span className="weak-group-title">待重练</span>
              <span className="weak-group-count">{groups.active.length} 道</span>
            </h2>

            {groups.active.length === 0 ? (
              <div className="card weak-group-empty">
                <div className="weak-group-empty-title">🎉 待重练已清空</div>
                <div className="weak-group-empty-sub">
                  历史错题都已恢复，可以继续学习了。
                </div>
              </div>
            ) : (
              <div className="weak-list">
                {groups.active.map((q) => (
                  <WeakCard
                    key={q.question_id}
                    q={q}
                    recovered={false}
                    onPractice={openPractice}
                  />
                ))}
              </div>
            )}
          </section>

          {/* 第二组：已恢复 —— 默认折叠，数量常显：它们不是消失了，是已恢复 */}
          <section className="weak-group">
            <h2 className="weak-group-head">
              <button
                type="button"
                className="weak-group-toggle"
                onClick={() => setRecoveredOpen((v) => !v)}
                aria-expanded={recoveredOpen}
                aria-controls="weak-recovered-list"
              >
                <span
                  className="weak-group-mark weak-group-mark-ok"
                  aria-hidden={true}
                >
                  ✓
                </span>
                <span className="weak-group-title">已恢复</span>
                <span className="weak-group-count">
                  {groups.recovered.length} 道
                </span>
                <span className="weak-group-action">
                  {recoveredOpen ? "收起" : "展开"}
                </span>
              </button>
            </h2>

            {recoveredOpen && (
              <div className="weak-list" id="weak-recovered-list">
                {groups.recovered.map((q) => (
                  <WeakCard
                    key={q.question_id}
                    q={q}
                    recovered={true}
                    onPractice={openPractice}
                  />
                ))}
              </div>
            )}
          </section>
        </>
      )}

      {practice.status !== "idle" && (
        <div className="practice-overlay" onClick={closePractice}>
          <div className="practice-panel" onClick={(e) => e.stopPropagation()}>
            {practice.status === "loading" && <p>加载中…</p>}

            {practice.status === "open" && (
              <>
                <div className="practice-prompt">{practice.detail.prompt}</div>
                <ul className="practice-options">
                  {practice.detail.options.map((opt, i) => (
                    <li key={i}>
                      <button
                        className="practice-option"
                        onClick={() => submitPractice(i, practice.detail)}
                      >
                        {opt}
                      </button>
                    </li>
                  ))}
                </ul>
                {practiceError && <p className="status error">{practiceError}</p>}
                <button className="practice-close" onClick={closePractice}>
                  取消
                </button>
              </>
            )}

            {practice.status === "result" && (
              <>
                <div className="practice-prompt">{practice.detail.prompt}</div>
                <ul className="practice-options">
                  {practice.detail.options.map((opt, i) => {
                    let cls = "practice-option";
                    if (i === practice.result.correct_index) cls += " correct";
                    else if (
                      i === practice.selected &&
                      !practice.result.is_correct
                    )
                      cls += " wrong";
                    return (
                      <li key={i}>
                        <button className={cls} disabled>
                          {opt}
                          {i === practice.result.correct_index ? " ✓" : ""}
                          {i === practice.selected && !practice.result.is_correct
                            ? " ✗"
                            : ""}
                        </button>
                      </li>
                    );
                  })}
                </ul>
                <div
                  className={`practice-verdict ${
                    practice.result.is_correct ? "ok" : "bad"
                  }`}
                >
                  {practice.result.is_correct
                    ? "✅ 这次答对了！"
                    : "❌ 还是错了，再想想"}
                </div>
                <div className="practice-explanation">
                  <strong>解析：</strong>
                  {practice.result.explanation}
                </div>
                <div className="practice-actions">
                  <button
                    className="practice-retry"
                    onClick={() =>
                      setPractice({ status: "open", detail: practice.detail })
                    }
                  >
                    再试一次
                  </button>
                  <button className="practice-close" onClick={closePractice}>
                    返回列表
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      <p className="phase">Phase 10.1 · Weak Questions</p>
    </div>
  );
}
