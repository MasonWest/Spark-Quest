#!/usr/bin/env node
/**
 * check-css-namespace.mjs —— 前端样式「全局注入」护栏  (铁律 R1)
 *
 * 背景：本项目的 .css 全部是**全局 CSS**（非 CSS Module），由 main.tsx 静态 import
 *      后经 Vite 全局注入 <head>。因此两个文件写下**同名裸类选择器**时，
 *      后 import 者胜 —— 且只在「同名 + 同特异性 + 后注入」三者同时成立时才发作，
 *      单看任何一个文件都看不出问题。
 *
 * 历史事故（都属真实 UI 走样）：
 *   - .review-title      Home.css ↔ ReviewPage.css        → 首页复习卡标题被顶到 26px，卡片 93.8px（应为 62.4px）
 *   - .footer-weak-link  Home.css ↔ WeakQuestionsPage.css
 *
 * 铁律 R1：禁止跨文件复用裸类名；页面样式一律加页面前缀（.home- / .review- / .quiz- …）。
 *         需要复用通用视觉时，要么用父级限定（.review-next .para），要么在 index.css 里定义设计系统层。
 * 详见：frontend/src/pages/README.md
 *
 * 用法：
 *   node frontend/scripts/check-css-namespace.mjs          # 只报「裸类名冲突」（有则 exit 1）
 *   node frontend/scripts/check-css-namespace.mjs --all    # 附带列出复合选择器同名观察项
 */
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const SRC = join(HERE, "..", "src");
const SHOW_ALL = process.argv.includes("--all");

/** 有意全局共享的通用类名（设计系统层，允许跨文件出现） */
const ALLOWLIST = new Set([
  "card", "badge", "chip", "tag", "icon", "container", "sr-only", "empty-state",
  "btn-primary", "btn-ghost", "btn-sm", "section-title",
]);

function collectCss(dir, out = []) {
  for (const name of readdirSync(dir)) {
    const full = join(dir, name);
    if (name === "node_modules" || name === "dist") continue;
    if (statSync(full).isDirectory()) collectCss(full, out);
    else if (name.endsWith(".css")) out.push(full);
  }
  return out;
}

/** 拆出所有 { selector { body } } 规则（支持 @media 嵌套） */
function rules(css) {
  const noC = css.replace(/\/\*[\s\S]*?\*\//g, "");
  const out = [];
  const stack = [];
  let lastEnd = 0, i = 0, depth = 0, openAt = -1;
  while (i < noC.length) {
    const ch = noC[i];
    if (ch === "{") {
      if (depth === 0) openAt = i;
      stack.push(i);
      depth++;
    } else if (ch === "}") {
      stack.pop();
      depth--;
      if (depth === 0) {
        out.push({ sel: noC.slice(lastEnd, openAt).trim(), body: noC.slice(openAt + 1, i).trim() });
        lastEnd = i + 1;
      }
    }
    i++;
  }
  return out;
}

const files = collectCss(SRC).sort();
const bare = new Map();   // className -> [{file, line}]  裸类选择器
const scoped = new Map(); // className -> [{file, sel}]    复合选择器（观察项）

for (const file of files) {
  const rel = relative(SRC, file).split("\\").join("/");
  const text = readFileSync(file, "utf8");
  const lines = text.replace(/\/\*[\s\S]*?\*\//g, (m) => m.replace(/[^\n]/g, " ")).split("\n");
  for (const r of rules(text)) {
    for (const part of r.sel.split(",").map((s) => s.trim()).filter(Boolean)) {
      const bareMatch = /^\.(-?[A-Za-z_][A-Za-z0-9_-]*)$/.exec(part);
      if (bareMatch) {
        const cls = bareMatch[1];
        const line = lines.findIndex((l) => l.includes(part)) + 1;
        if (!bare.has(cls)) bare.set(cls, []);
        bare.get(cls).push({ file: rel, line });
      } else {
        const re = /\.(-?[A-Za-z_][A-Za-z0-9_-]*)/g;
        let m;
        while ((m = re.exec(part)) !== null) {
          if (!scoped.has(m[1])) scoped.set(m[1], new Set());
          scoped.get(m[1]).add(rel);
        }
      }
    }
  }
}

const collisions = [];
for (const [cls, hits] of [...bare.entries()].sort()) {
  const distinct = [...new Set(hits.map((h) => h.file))];
  if (distinct.length < 2) continue;
  if (ALLOWLIST.has(cls) || cls.startsWith("--")) continue;
  collisions.push({ cls, hits });
}

if (SHOW_ALL) {
  console.log("\n=== 观察项：复合选择器里跨文件出现的类名（作用域已被父级限定，通常良性）===");
  const obs = [...scoped.entries()].filter(([, s]) => s.size > 1 && !ALLOWLIST.has(...[])).sort();
  for (const [cls, s] of obs) console.log(`  .${cls}  ← ${[...s].join(", ")}`);
  console.log();
}

if (collisions.length === 0) {
  console.log(`\n✅ CSS 命名空间检查通过（铁律 R1）：${files.length} 个 css 文件，无跨文件裸类名冲突。\n`);
  process.exit(0);
}

console.log(`\n❌ 铁律 R1 违规：${collisions.length} 处跨文件裸类名冲突（后 import 者会静默覆盖前者）\n`);
for (const { cls, hits } of collisions) {
  console.log(`  .${cls}`);
  for (const h of hits) console.log(`      ${h.file}:${h.line}`);
  console.log(`      → 修法：本页专用类名加页面前缀，或改用父级限定，或确认有意共享后加入 ALLOWLIST\n`);
}
console.log("  铁律全文：frontend/src/pages/README.md\n");
process.exit(1);
