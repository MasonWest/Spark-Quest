import type { ReactNode } from "react";
import { Fragment } from "react";
import "./RichText.css";

// 行内解析：code（`x`）与 bold（**x**）。数据均为自有种子内容，无 XSS 风险。
//
// 单次左→右扫描，允许两种标记互相嵌套（如 **看不到 `*(N)`**）：
// 旧实现「先按 ` 切分、再在每段里找 **」，会把跨 code 的加粗整对拆散 ——
// 于是字面 ** 泄漏到正文、加粗还失效（L4/L5 共 3 处）。现在谁先出现谁先闭合，
// code 内出现的 * 也不会再被误认成加粗定界符。
function renderInline(text: string): ReactNode[] {
  const nodes: ReactNode[] = [];
  let buf = "";
  let i = 0;
  const flush = () => {
    if (buf) {
      nodes.push(<Fragment key={nodes.length}>{buf}</Fragment>);
      buf = "";
    }
  };
  while (i < text.length) {
    if (text[i] === "`") {
      const end = text.indexOf("`", i + 1);
      if (end > i) {
        flush();
        nodes.push(
          <code key={nodes.length} className="inline-code">
            {text.slice(i + 1, end)}
          </code>
        );
        i = end + 1;
        continue;
      }
    } else if (text[i] === "*" && text[i + 1] === "*") {
      const end = text.indexOf("**", i + 2);
      if (end > i + 2) {
        flush();
        nodes.push(
          <strong key={nodes.length}>{renderInline(text.slice(i + 2, end))}</strong>
        );
        i = end + 2;
        continue;
      }
    }
    buf += text[i];
    i++;
  }
  flush();
  return nodes;
}

const CIRCLED_RE = /[①-⑳]/g;
const CIRCLED_ONE = /[①-⑳]/;
const countCircled = (s: string) => (s.match(CIRCLED_RE) || []).length;
const isDotLine = (l: string) => l.trimStart().startsWith("· ");

// 单个文本块：① ② ③ 有序枚举 / · 项目符号枚举（按行识别，支持与正文混排）/ 普通段落。
// 返回 ReactNode[]（可能含多个元素：正文段 + 列表）。
function renderBlock(text: string, key: string): ReactNode[] {
  const circled = text.match(CIRCLED_RE);
  if (circled && circled.length >= 2) {
    const positions: number[] = [];
    for (const m of text.matchAll(CIRCLED_RE)) positions.push(m.index ?? 0);
    const lead = text.slice(0, positions[0]).trim();
    const items: string[] = [];
    for (let i = 0; i < positions.length; i++) {
      const start = positions[i] + 1;
      const end = i + 1 < positions.length ? positions[i + 1] : text.length;
      let seg = text.slice(start, end).trim();
      seg = seg.replace(/^[；、)\s]+/, "").replace(/[；、]+$/, "");
      if (seg) items.push(seg);
    }
    const out: ReactNode[] = [];
    if (lead) {
      out.push(
        <p key={`${key}-l`} className="para">
          {renderInline(lead)}
        </p>
      );
    }
    out.push(
      <ol key={`${key}-ol`} className="rich-list">
        {items.map((it, i) => (
          <li key={i}>{renderInline(it)}</li>
        ))}
      </ol>
    );
    return out;
  }

  // · 项目符号列举：按行识别（数据常用单个换行分隔，并与正文混排）
  const isDot = isDotLine;
  const lines = text.split("\n").map((l) => l.replace(/\s+$/, ""));
  if (lines.filter(isDot).length >= 2) {
    const out: ReactNode[] = [];
    let prose: string[] = [];
    const flush = () => {
      if (prose.length) {
        out.push(
          <p key={`${key}-p${out.length}`} className="para">
            {renderInline(prose.join(""))}
          </p>
        );
        prose = [];
      }
    };
    let i = 0;
    while (i < lines.length) {
      if (isDot(lines[i])) {
        flush();
        const items: string[] = [];
        while (i < lines.length && isDot(lines[i])) {
          items.push(lines[i].replace(/^\s*·\s*/, ""));
          i++;
        }
        out.push(
          <ul key={`${key}-ul${out.length}`} className="rich-list rich-list-ul">
            {items.map((it, j) => (
              <li key={j}>{renderInline(it)}</li>
            ))}
          </ul>
        );
      } else {
        prose.push(lines[i]);
        i++;
      }
    }
    flush();
    return out;
  }

  return [<p key={key} className="para">{renderInline(text)}</p>];
}

// ⚠️ 块正文：与普通段落共用同一套块渲染，只多一层「多行纯文本」兜底。
// （纯文本若交给 renderBlock 的单段分支，内部的 \n 仍会被 HTML 折叠成空格。）
function renderWarnBody(text: string, key: string): ReactNode[] {
  const t = text.trim();
  if (!t) return [];
  if (countCircled(t) >= 2 || t.split("\n").filter(isDotLine).length >= 2) {
    return renderBlock(t, key);
  }
  const out: ReactNode[] = [];
  t.split("\n").forEach((l, i) => {
    const s = l.trim();
    if (s) out.push(...renderBlock(s, `${key}-${i}`));
  });
  return out;
}

// 判断 s[idx] 处的【...】是否为「小节标题」，而非行内【】强调。
function isHeaderBracket(s: string, idx: number): boolean {
  const m = /【([^】]+)】/.exec(s.slice(idx));
  if (!m) return false;
  const after = s.slice(idx + m[0].length);
  const before = s.slice(0, idx);
  if (before.trim().length === 0) return true;
  if (after.startsWith("\n")) return true;
  const at = after.trim();
  return at.length === 0 || at.startsWith("【");
}

function firstHeaderIndex(s: string): number {
  let idx = s.indexOf("【");
  while (idx >= 0) {
    if (isHeaderBracket(s, idx)) return idx;
    idx = s.indexOf("【", idx + 1);
  }
  return -1;
}

type Seg = { subhead: string } | { body: string };

// 解析一个段落块，支持「【标题】」与正文粘连（部分课程未用空行分隔小节）。
function parseBlock(p: string): Seg[] {
  const m = /^【([^】]+)】\s*([\s\S]*)$/.exec(p);
  if (m) {
    const segs: Seg[] = [{ subhead: m[1] }];
    const rest = m[2].trim();
    if (rest) segs.push(...parseBlock(rest));
    return segs;
  }
  const idx = firstHeaderIndex(p);
  if (idx >= 0) {
    const before = p.slice(0, idx).trim();
    const segs: Seg[] = [];
    if (before) segs.push({ body: before });
    segs.push(...parseBlock(p.slice(idx)));
    return segs;
  }
  return [{ body: p }];
}

export default function RichText({ text }: { text: string }) {
  if (!text || !text.trim()) return null;
  const paras = text
    .split(/\n\n+/)
    .map((s) => s.trim())
    .filter(Boolean);

  const out: ReactNode[] = [];
  let k = 0;
  let i = 0;
  while (i < paras.length) {
    const p = paras[i];

    // ⚠️ 警示块：标题 = 首行，其余（同段内的条目 + 紧随的普通段落）作为正文。
    //
    // 历史数据有两种写法：
    //   A) 标题独占一段，后接空行，条目在下一段        → L1 / L2（健康）
    //   B) 标题后只隔一个换行就跟条目，同属一个「段」  → L3–L7（44 课）
    // 旧实现把整个段塞进 renderInline：它不认 ①②③，HTML 又把 \n 折叠成空格，
    // 于是整块「比喻的边界」被压成一坨加粗橙字。这里统一按「首行 = 标题」切开，
    // 其余交给 renderWarnBody，两种写法渲染结果完全一致。
    if (p.startsWith("⚠️")) {
      let title = p;
      let rest = "";
      const nl = p.indexOf("\n");
      if (nl >= 0) {
        title = p.slice(0, nl).trim();
        rest = p.slice(nl + 1);
      }
      // 兜底：标题行本身也混进了 ≥2 个 ①②③（标题与条目连写在同一行）→ 从第一个编号处切开
      const cut = title.search(CIRCLED_ONE);
      if (cut >= 0 && countCircled(title) >= 2) {
        rest = title.slice(cut) + (rest ? "\n" + rest : "");
        title = title.slice(0, cut).trim();
      }
      const body: ReactNode[] = renderWarnBody(rest, `w${k++}`);
      i++;
      while (
        i < paras.length &&
        !paras[i].startsWith("⚠️") &&
        !/^【/.test(paras[i])
      ) {
        body.push(...renderWarnBody(paras[i], `w${k++}`));
        i++;
      }
      out.push(
        <div key={`warn${k++}`} className="rich-warning">
          <p className="rich-warning-title">{renderInline(title)}</p>
          {body}
        </div>
      );
      continue;
    }

    for (const seg of parseBlock(p)) {
      if ("subhead" in seg) {
        out.push(
          <h4 key={`h${k++}`} className="rich-subhead">
            {seg.subhead}
          </h4>
        );
      } else {
        out.push(renderBlock(seg.body, `b${k++}`));
      }
    }
    i++;
  }

  return <div className="rich-text">{out}</div>;
}
