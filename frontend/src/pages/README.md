# ⚠️ 改这一层之前必读 —— 前端样式铁律 R1

> 这个文件不是说明文档，是**事故档案 + 硬约束**。本项目已经因为违反它吃过两次真实的 UI 走样。
> **写任何新页面、新组件样式前，先读完这一页。**

---

## R1 · 禁止跨文件复用「裸类名」

**规则一句话：本项目的 `.css` 全部是全局作用域，裸类名（`.foo`）属于整个应用，而每个页面都会往同一个 `document` 里注入样式。所以同一个裸类名只能有一个文件定义。**

### 为什么 —— 机制说清楚

- 所有 `.css` 由 `main.tsx` 静态 `import`，Vite 把它们**全局注入** `<head>`，**没有 CSS Module / 没有 scoped / 没有 hash 后缀**。
- 因此样式是**全站累加**的，不是"页面级隔离"。同名的两条规则同时存在于候选集里。
- 冲突触发条件非常苛刻，只有**三条同时成立**才会走样：

  1. **同名**（两个文件都写 `.review-title`）
  2. **同特异性**（都是普通类选择器 `0,1,0`）
  3. **后注入者存在**（`main.tsx` / 组件里的 import 顺序决定谁后注入 → 后者胜）

  三条少一条都不发作。所以它平时静默，一旦爆发就难查：**单看任何一个文件都是对的**，看你正在改的那个文件也永远是对的。

### 症状长什么样

- 某页面元素字号 / 间距 / 颜色"莫名"跟这个文件里写的对不上，DevTools 里显示的规则来自**另一个页面的 css 文件**。
- 常见形态是"这个元素太大 / 间距太多"，且改本文件的数值**毫无效果**（因为你被覆盖了）。
- 只在特定路由出现（那个页面的 css 恰好后注入），换个页面看就正常。

### 怎么修（按推荐顺序）

1. **加页面前缀（首选）** —— 本页专用类名一律带页面前缀，物理上不可能撞车：

   | 页面 | 前缀示例 |
   |------|----------|
   | `Home.tsx` | `.home-review-title`、`.home-weak-entry` |
   | `ReviewPage.tsx` | `.review-banner`、`.review-header .back-link` |
   | `QuizPage.tsx` | `.quiz-result-item` |
   | `WeakQuestionsPage.tsx` | `.practice-option` |
   | `MapPage.tsx` | `.map-*` |

2. **用父级限定作用域** —— 当这个样式本来就只该在小范围内生效时（**这是合法的局部覆盖，不算违规**）：

   ```css
   /* ReviewPage.css —— 良性：只作用于 .review-next 内部，不会碰到别处 */
   .review-next .para { line-height: 1.7; margin: 0 0 14px; }
   ```

3. **提升为设计系统层** —— 确实该全站共享的（按钮 / 徽章 / 卡片），统一定义在 `src/index.css`，**其他文件不要再定义同名裸类名**，只使用它。

   设计系统层当前包含：`.card` `.badge` `.chip` `.tag` `.icon` `.container` `.btn-primary` `.btn-ghost` `.btn-sm` `.section-title`，这些已在护栏脚本的 `ALLOWLIST` 里放行。

### 落地前的自查（一条命令）

```bash
# 在 spark-quest-app/ 下
node frontend/scripts/check-css-namespace.mjs

# 或在 frontend/ 下（等价）
npm run check:css
```

- 通过 → `✅ CSS 命名空间检查通过（铁律 R1）`
- 违规 → 列出**文件名:行号**与修法，退出码 1

加 `--all`（或 `npm run check:css:all`）可另外列出"复合选择器里跨文件同名"的观察项（通常良性，人工确认即可）。

---

## 事故档案（两次真实走样）

### 事故 1 · `.review-title` —— 首页复习卡标题被顶到 26px

| 项 | 内容 |
|----|------|
| 文件 | `Home.css` ↔ `ReviewPage.css` |
| 机制 | 两文件都定义裸 `.review-title`；`main.tsx` 里 `ReviewPage` 在 `Home` **之后** import → ReviewPage 的 `.review-title { font-size: 26px; margin: 0 0 16px }` 在首页也生效 |
| 后果 | 首页复习卡标题 16px → **26px**，卡片高度被撑到 **93.8px**（卡内 padding 只占很小一部分） |
| 修法 | 首页侧改名 `.home-review-title` 隔离 → 卡片 **93.8px → 62.4px（-33%）** |
| 备注 | 这个事故最具欺骗性：需求方以为是"字号设计得太大"，实际是**跨文件泄漏**。修的时候如果只在本文件里调数值，永远不会生效 |

### 事故 2 · `.footer-weak-link` —— 首页页脚残留样式

| 项 | 内容 |
|----|------|
| 文件 | `Home.css` ↔ `WeakQuestionsPage.css` |
| 机制 | 首页页脚删掉后，`WeakQuestionsPage.css` 末尾还留着为首页写的 `.footer-weak-link` |
| 修法 | 随页脚删除一并清掉 —— **组件/元素删了，它的样式必须同批删干净**，否则就是下一轮的幽灵规则 |

---

## 已核查为良性的同名（别重复怀疑）

以下是在 `--all` 模式下会出现的观察项，**已逐条人工确认作用域被父级限定 / 属设计系统层复用，不构成冲突**：

| 类名 | 出现位置 | 为什么安全 |
|------|----------|-----------|
| `.back-link` | LessonPage.css / ReviewPage.css | 后者是 `.review-header .back-link`，父级限定 |
| `.correct` `.wrong` | QuizPage.css / WeakQuestionsPage.css | 均为复合选择器（`.quiz-result-item.correct` / `.practice-option.wrong`） |
| `.is-active` | StreakBadge.css / map.css | 均为复合（`.streak-badge.is-active` / `.view-switch button.is-active`） |
| `.muted` | LessonPage.css / ReviewPage.css | 后者是 `.review-next .muted` |
| `.ok` `.retry` | index.css / QuizPage.css / ReviewPage.css / WeakQuestionsPage.css | 均为复合（`.status.ok` / `.review-banner.ok` / `.result-banner.ok` / `.practice-verdict.ok`） |
| `.para` | RichText.css / LessonPage.css / ReviewPage.css | 后者是 `.rich-warning .para` / `.review-next .para` 父级限定 |
| `.btn-ghost` `.btn-primary` | index.css / Home.css / ReviewPage.css | 设计系统层复用（`ALLOWLIST` 放行） |

> 判断标准很简单：**它是不是裸选择器 `.foo`？是 → 违规。不是（有空格 / 有第二个类 / 有元素名）→ 作用域已限定，通常是良性的。**

---

## 附：本项目前端的其他样式约定

- 所有颜色 / 间距 / 圆角 / 字号一律走 `index.css` 里的 `--sq-*` CSS 变量，**不要在页面文件里写死色值**。
- 页面文件只放"本页布局与页面级组件"样式；能进设计系统层的不重复造。
- 容器不要用 `overflow: hidden` 收横向溢出，用 **`overflow-x: clip`**（不产生滚动容器，不影响纵向滚动，也不破坏 sticky）。
- 装饰性伪元素外扩（如 `inset: -6px` 的呼吸环）在窄屏会顶破视口造成**周期性横向滚动条**，必须由父容器 `clip` 兜住或直接禁用。
