# HTML 报告 UI 设计规范

> **用途**：供报告生成类 Skill 复用的 HTML 页面产出契约（设计令牌 + 骨架 + 组件状态 + 渲染契约 + 验收清单）。
> **适用技能**：`preloan-industry-dd`（商业银行贷前行业尽调）
> **实现模板**：`assets/report_template.html`（完整 CSS/JS 以此文件为准；页面只留 `__REPORT_DATA__` 占位符）
> **适用**：单文件 HTML、内联 CSS/JS、零外部依赖、JS 数据驱动的长篇报告；全站字体统一微软雅黑

---

## 0. 给 Skill 的接入建议

把这份规范拆成三块固化进 Skill，改生成逻辑时不要重新"设计"，只按契约填空：

| 固化位置 | 内容 | 本规范对应章节 |
|---|---|---|
| Skill 的**模板文件** | 整段 `<style>` + 页面骨架 + 组件构造函数 | §2、§4、§5、附录 A/B/C |
| Skill 的**生成指令** | 只要求产出 `REPORT_DATA` 对象，字段与枚举严格按 schema；禁止生成样式代码 | §1 硬约束、§10 渲染契约 |
| Skill 的**生成后自检** | 脚本化验收，失败即回炉 | §12 验收清单 |

**核心原则：数据与表现分离。** Skill 只负责写数据，模板负责渲染。任何"在生成数据时顺手改 CSS"的做法都会让同一套报告在不同行业间漂移。

---

## 1. 设计目标与硬约束

| 目标 | 可验证标准 |
|---|---|
| 10 秒抓结论 | 首屏同时可见：综合评级与分值、总体策略、核心结论、章节目录 |
| 长文可定位 | 任意章节 ≤1 次点击可达；滚动时目录高亮当前章节 |
| 可打印归档 | A4 打印不丢表格、表头跨页重复、卡片不被拦腰切断 |
| 可信而非炫技 | 无装饰性渐变、无阴影堆叠、无动效入场；强调色只用于决策信息 |

**硬约束（违反即判不合格）**

1. 单文件，`<style>` / `<script>` 全部内联，不引 CDN、Web 字体、外链图片、外部 JS 库。
2. `REPORT_DATA` 由 Skill 原样产出，**模板不得改写、补值、四舍五入或补全缺失字段**；缺失一律沿用数据里已有的标记（如「数据缺失-A」「建议复核」）。
3. 不编造任何数字、日期、机构名、来源；页面新增的统计值只能来自对 `REPORT_DATA` 的计数/取值（如 `risks.length`）。
4. 枚举值严格按 Skill 的 schema 取值，模板只做展示映射，不新增枚举。
5. 所有不确定性表述沿用原文，不因排版需要删减、概括。
6. 页面不得因缺少某字段而抛 `undefined` / `NaN`；缺字段时走 `|| "—"` 兜底，但不改变语义。

---

## 2. 设计令牌（Design Tokens）

### 2.1 浅色（默认）

| 类别 | 变量 | 值 | 用途 |
|---|---|---|---|
| 文字 | `--ink` / `--ink-2` / `--muted` / `--faint` | `#16233A` / `#3B4A61` / `#6B7A90` / `#9AA7B8` | 正文 / 次级 / 辅助 / 页脚 |
| 品牌 | `--navy` / `--navy-2` / `--gold` / `--gold-soft` | `#122C4A` / `#1E4E79` / `#B8863B` / `#F7F0E2` | 标题、表头 / 链接、图表 / 强调、编号、结论 / 强调底 |
| 表面 | `--bg` / `--card` / `--soft` / `--blue-soft` | `#F4F6F9` / `#FFFFFF` / `#F7F9FC` / `#EDF3FA` | 页面 / 卡片 / 内块 / 表头 |
| 描边 | `--line` / `--line-2` | `#E3E8EF` / `#EEF2F7` | 卡片、分隔 / 内块、表格行线 |
| 语义 | `--risk-high` / `--risk-midhigh` / `--risk-mid` / `--risk-low` | `#C0392B` / `#D2742B` / `#B78A21` / `#1E7A52` | 四档风险等级 |
| 语义底 | `--risk-*-bg` | `#FBEAE8` / `#FDF0E4` / `#FBF4DF` / `#E8F5EE` | 徽标底、风险卡左侧渐变起点 |

> **配色规则**：深蓝为基线、降饱和加深度；铜金只承载"决策信息"，避免主色泛滥。风险四档必须独立呈现，「中高风险」与「高风险」不得同色。

### 2.2 暗色覆盖（`html[data-theme="dark"]`）

| 变量 | 值 |
|---|---|
| `--ink` / `--ink-2` / `--muted` | `#E8EDF5` / `#B9C5D6` / `#8A99AE` |
| `--navy` / `--navy-2` / `--gold` / `--gold-soft` | `#8FB6DC` / `#A9C8E8` / `#D8AC68` / `#33291A` |
| `--bg` / `--card` / `--soft` / `--line` | `#0E1622` / `#151F2E` / `#1A2637` / `#28374B` |
| 风险四档 | `#F0796C` / `#E9A05A` / `#DDBA55` / `#5DC194` |

暗色只覆盖变量，**不重写组件规则**；Hero 保持深蓝渐变不动。主题值存 `localStorage`，读取失败用 `try/catch` 静默降级。

### 2.3 尺度系统

| 维度 | 取值 | 说明 |
|---|---|---|
| 字号阶梯 | 10.5 / 11.5 / 12.5 / 13 / 14 / 14.5 / 18.5 / 27px | 徽标·图例 / 标签·来源 / 表格·清单 / 提示 / 正文 / 核心结论 / 章节标题 / Hero 标题 |
| 行高 | 正文 1.75；长段落 1.85；表格 1.7；标签 1.5 | 中文长段落需更宽松的行距 |
| 间距 | 4px 基准：4 / 8 / 12 / 16 / 24 / 32 / 48 | 卡片内边距 26px、卡间距 20px、网格 gap 12px |
| 圆角 | `--r-l:14px` 卡片 / `--r:10px` 内块·表格·风险卡 / `--r-s:6px` 标签·按钮 | 只允许三级，禁止 4/6/8 混用 |
| 阴影 | 常规 `0 1px 2px rgba(18,44,74,.04), 0 10px 28px rgba(18,44,74,.055)`；hover 加深 | 双层弱阴影，保证卡片边界可辨 |
| 字体 | `--font: "Microsoft YaHei","微软雅黑",sans-serif`；`--mono: var(--font)` | 全站单一字体，含 SVG、按钮、表格、徽标与大数字 |
| 数字 | `font-variant-numeric:tabular-nums` 全局；不做独立等宽栈 | 数字列对齐须在验收时目视确认 |

---

## 3. 禁止的反模式

| 问题 | 规则 |
|---|---|
| 15 个章节同款白卡，无权重 | 七大维度用「维度一…维度七」、四大专项用「专项一…专项四」文字编号，概览与结论四章不编号；配合副标题与结论徽标建立层级；概览/综合评估用 `card--accent` 金色顶边，风险章节用 `card--alert` 红顶边 |
| 浅蓝 `.note` 复用几十次，提示与正文等权 | 提示块必须分 4 态，不同类型不同底色与左边框 |
| 长段落塞进小指标格 | 指标块分 `default / long / metric` 三态，长文本降到 12.5px / 1.85 |
| 表格无斑马纹、无滚动容器 | 表格必须有 `.table-scroll` 外包裹 + 斑马纹 + hover |
| 无目录，长文无法定位 | 侧栏 + 横滑目录，IntersectionObserver 高亮 |
| 无打印样式 | 必须内置 A4 规则 |
| 圆角/阴影混乱、风险等级色阶不足 | 见 §2.3、§5.4 |

---

## 4. 页面骨架契约

```html
<body>
<a class="skip" href="#report">跳到报告正文</a>
<div class="topbar no-print">…品牌 / 元信息 / 主题·打印按钮…<nav class="toc-strip" id="toc-strip"></nav></div>
<header class="hero">…标题 / 元信息 / 标签 / 决策速览 + 评级仪表…</header>
<div class="layout">
  <aside class="sidenav no-print" id="sidenav"><nav id="toc-list"></nav></aside>
  <main class="wrap" id="report"></main>
</div>
<footer class="pagefoot">…</footer>
<button class="to-top no-print" id="to-top">↑</button>
<div class="tooltip" id="tip"></div>
<script>const REPORT_DATA = {…}; /* 渲染层 + 交互层 */</script>
</body>
```

**ID 契约（渲染函数依赖，不可改名）**

| ID | 用途 | ID | 用途 |
|---|---|---|---|
| `report` | 章节挂载点 | `toc-list` / `toc-strip` | 侧栏 / 横滑目录 |
| `t-industry` / `t-meta` / `hero-tags` / `hero-quick` | Hero 内容 | `tb-industry` / `tb-meta` | 工具条内容 |
| `score-value` / `score-badge` / `score-bars` | 评级仪表 | `side-foot` / `pagefoot` | 页脚元信息 |
| `btn-print` / `btn-theme` / `to-top` / `tip` | 交互 | `sec-00` … `sec-14` | 章节锚点 |

**Hero 填充规则**：决策速览四项只能取自真实字段——`assessment.strategy.overall`、`special.esg.fit.rating`、`special.risks.length`、`special.checklist.categories.length`。禁止写死行业结论。

**章节契约**：每个章节是 `<section class="card" id="sec-NN" data-toc="编号 + 标题" data-group="分组">`，含 `.sec-head`（编号 / 标题 / 副标题 / 结论徽标）+ `.sec-body`。`num` 为空时不渲染 `.sec-num`，`data-toc` 只取标题；维度与专项章节的 `num` 为文字编号，概览与结论章节为空。分组固定为 `概览 / 维度分析 / 专项研究 / 结论与说明`。综合评估章节须含「五维评分口径说明」。

---

## 5. 组件规范（状态齐全是硬要求）

### 5.1 卡片 `.card`
状态：`default` / `card--accent`（金色 3px 顶边）/ `card--alert`（红色 3px 顶边）；hover 阴影加深。
数值：圆角 14px、间距 20px、`scroll-margin-top:132px`（避开粘性工具条）。

### 5.2 指标块 `.kv`
| 状态 | 类名 | 数值 |
|---|---|---|
| 默认 | `.kv` | 底 `--soft`、边框 `--line-2`、内边距 12/14px、值 14px/650 |
| 长文本 | `.kv--long` | 值 12.5px/500、行高 1.85、色 `--ink-2` |
| 关键数值 | `.kv--metric` | 值 20px 等宽、色 `--navy-2` |

### 5.3 徽标 `.enum` / `.pill`（统一信贷语义色阶）

全站判定徽标共用 `semanticTone(v)` → `enumPill()` / `enumClass()`，规则顺序即优先级。风险评级按高低着色，业绩与策略判定按利好利空着色。**不得按字面「高 / 中 / 低」着色**——否则「显著高于行业均值」会被染红、「显著低于行业均值」会被染绿，「低风险」也会被负面词误伤。

| 档位 | 类 | 典型取值 |
|---|---|---|
| 红 · 强负面 | `e-high` / `p-red` | 红色预警、高风险、显著低于行业均值、不达标、不可接受、无法覆盖 / 无法测算、严禁 / 严禁新增、压缩退出、淘汰类、供给过剩、承压下行、下行期、倒挂、亏损、禁止（红线） |
| 橙 · 偏负面 | `e-midhigh` / `p-orange` | 中高风险、略低于行业均值、低于 / 弱于、弱势、限制类、结构性过剩、底部震荡、偏高 / 偏低、差 / 较差 / 偏弱 / 不足 / 恶化 / 下滑 / 走弱 / 承压、审慎 / 审慎介入 |
| 黄 · 中性偏谨慎 | `e-mid` / `p-yellow` | 中风险、结构性分化、前景不明、拐点不明、待复核、建议复核、口径不一致 |
| 绿 · 正面 | `e-low` / `p-green` | 低风险、低于警戒线、优先支持、扶持类、显著 / 略高于行业均值、上行期、供需平衡、供给紧缺、优势、优秀、良好、达标、可控、正常介入 |
| 灰 · 中性 / 无法判断 | `e-default` / `p-default` | 持平行业均值、中性、无法对标、平稳期、未明确但无限制 |

规则先排除「低于警戒线」等正面例外，再判风险评级，最后判负面业绩词。Hero 深色底的评级徽标用 `.enum.on-dark` 浅金描边，不套用上述色阶（可读性优先）；同一评级在「报告概览」中以普通徽标按色阶呈现。风险卡左侧色条 `l-high / l-midhigh / l-mid / l-low` 只按风险等级渲染，与业绩判定无关。

统一 20px 圆角、11px 内边距、`::before` 圆点。

### 5.4 提示块 `.note`（4 态）
| 状态 | 类 | 底色 / 左边框 | 用途 |
|---|---|---|---|
| 普通 | `note--base` | `--soft` / `--line` | 分析步骤、一般说明 |
| 信贷决策提示 | `note--tip` | `--gold-soft` / `--gold` | **只读决策提示，最高权重** |
| 关键信息 | `note--key` | `--blue-soft` / `--navy-2` | 研判、均值说明、风控措施 |
| 警示 | `note--warn` | `--risk-high-bg` / `--risk-high` | 不确定性、风险含义 |

结构固定 `<div class="note"><span class="note-label">标签</span><div class="note-text">正文</div></div>`，标签列最小宽 76px，窄屏改为上下排列。

### 5.5 表格
外层 `.table-scroll`（`overflow-x:auto`、圆角 10px）；`table` 最小宽 560px；表头 `--blue-soft` 底 + 2px 主色下边框；偶数行 65% `--soft` 底；hover `--blue-soft`；首列加粗；`min-width:0` 长文本必须 `overflow-wrap:anywhere`。

### 5.6 风险卡 `.risk-card`（4 档）
`l-high` / `l-midhigh` / `l-mid` / `l-low`，左边框 4px 对应语义色，背景为 `linear-gradient(90deg, 语义浅底, --card 22%)`。
结构：`.risk-head`（`NN · 名称` + 等级徽标）+ 三段 `.risk-field`（`现状` / `传导路径` / `风控措施`，84px 标签列）+ `.src` 来源行。

### 5.7 其他组件
| 组件 | 规则 |
|---|---|
| `.tier` T1–T4 | 四级独立配色；`title` 属性写全等级释义（如 T1 一手权威：监管/结构化/原始披露） |
| `.source-line` | 76px 标签列 + 虚线上边框；来源与缺口分行，不混排 |
| `.col-check` | 5 类核查清单，2 列网格，`break-inside:avoid`，`::marker` 用金色 |
| `.summary-box` | 核心结论：金色左 4px + 浅金渐变底 + `::before` "核心结论" 眉标 |
| `.legend` | 风险四档色块 + T1–T4 文字释义，仅风险章节末尾出现一次 |
| 雷达图 | 内联 SVG，5 轴 / 5 环 / 轴标签 + 分值双行标注；颜色用 CSS 变量，不用硬编码色值；圆点带 `data-tip` |
| `.redalert` | 仅当 `redAlert !== "无"` 时渲染，红色描边警示条 |

---

## 6. 状态矩阵（每个交互组件必须覆盖）

| 状态 | 要求 |
|---|---|
| 默认 / hover | 按钮底色变化；卡片、表格行、风险卡有 hover 反馈 |
| focus-visible | 全局 `outline:2px solid var(--navy-2); outline-offset:3px` |
| active | 目录项高亮：浅蓝底 + 金色左 2px；按钮 `translateY(1px)` |
| 打印 | 隐藏 `.no-print`，强制浅色变量，去阴影、去圆角、去外链 |
| 暗色 | 仅变量覆盖，`<html data-theme="dark">` |
| 窄屏 | 目录切横滑、网格单列、表格横向滚动 |
| 减弱动效 | `@media(prefers-reduced-motion:reduce)` 关闭 transition / smooth scroll |

---

## 7. 响应式断点

| 断点 | 变化 |
|---|---|
| `≥1181px` | 216px 侧栏 + 正文双列；Hero 左右双列（1fr / 306px） |
| `≤1180px` | 隐藏侧栏，启用 `.toc-strip` 横滑目录；布局单列 |
| `≤820px` | 网格全部单列；Hero 单列、标题 21px；章节头/体内边距降到 16px；`.note`、`.risk-field`、`.source-line` 改上下排列；`scroll-padding-top:110px` |
| `≤520px` | 按钮收起文字只留图标；评分数字 38px；正文 13.5px |

---

## 8. 打印规则（A4）

```
@page{size:A4;margin:14mm 12mm;}
```

- 隐藏：`.topbar / .sidenav / .toc-strip / .to-top / .tooltip / .skip / .no-print / .hero-quick`。
- 强制浅色：在 `@media print` 内重刷一遍 `[data-theme="dark"]` 的变量，保证暗色模式下打印也不发黑。
- `thead{display:table-header-group}` 表头跨页重复；`tr`、`.kv`、`.risk-card`、`.col-check`、`.note`、`.summary-box` 设 `break-inside:avoid`。
- 卡片去阴影、圆角降 6px；表格 `min-width:0`、字号 8.5pt；Hero 背景 `print-color-adjust:exact`。
- 导航类 `a` 去下划线、颜色继承。

---

## 9. 可访问性清单

- `lang="zh-CN"`；`<main>` / `<aside>` / `<nav>` / `<header>` 语义标签齐全。
- 首个可聚焦元素为 skip link；表格 `<th scope="col">`；SVG `role="img" + aria-label`。
- 图标按钮带 `aria-label`；主题按钮维护 `aria-pressed`。
- 正文对比度 ≥4.5:1（`#16233A` on `#FFFFFF`）；辅助文字 `#6B7A90` 仅用于非关键标签。
- tooltip 为 `pointer-events:none`，不阻挡焦点；`prefers-reduced-motion` 生效。

---

## 10. 渲染层契约（Skill 生成数据时必须对齐）

**数据/表现分离**：Skill 只产出 `REPORT_DATA`；模板里的 `render()` 不得写入业务数据。

| 函数 | 签名 / 职责 |
|---|---|
| `card(id,num,title,opt)` | 建章节；`num` 为文字编号或空串，`opt:{group,sub,conclusion,accent,alert}` |
| `grid(items,cols)` | `items:[{k,v,long,metric}]` → 指标块网格 |
| `kvRow(items,cols)` | 章节顶部"判定结论 / 置信度 / 数据确定性"三件套 |
| `table(headers,rows,cls)` | 统一表格外包裹与表头 |
| `note(label,text,kind)` | `kind: base / tip / key / warn` |
| `src(label,text)` | 来源 / 缺口行 |
| `h3(t)` / `bullets(arr,kind)` / `legend()` | 小节标题 / 项目列表 / 图例 |
| `enumPill(v,dark)` / `enumClass(v)` / `tierBadge(src)` | 枚举与来源分级展示映射 |
| `buildRadar(d)` | 五维评分 SVG |
| `render()` / `buildToc()` / `initUI()` | 渲染 → 目录 → 交互，末尾按序调用 |

**字段映射（不得改名）**：`header` → Hero + 概览；`dimensions.{policy,cycle,profit,supply,financial,market,chain}` → 7 个维度章节；`special.{risks,checklist,projectCalc,esg}` → 4 个专项章节；`assessment` → 综合评估 + Hero 评分仪表；`notes` / `disclaimer` → 说明与免责。

**分支规则**：专项三按数据优先判定——有测算数据或 `applicable` 为真即渲染四表，仅在「明确标记不适用且四张表全空」时收起整章；`redAlert !== "无"` 才出红色警示条。所有长文本字段一律经 `note()` / `.kv--long`，禁止直接塞进默认指标块。

---

## 11. 禁止模式

- 禁止等权卡片堆叠、禁止用同一个 `.note` 样式承载所有段落。
- 禁止装饰性渐变、玻璃拟态、入场动画、大圆角、彩色阴影；Hero 渐变是唯一例外（深蓝→深蓝）。
- 禁止把 `float` 用于布局（对齐不稳）；一律 flex / grid。
- 禁止硬编码颜色到组件里（一律走变量）；SVG 也用 `var(--…)`。
- 禁止 `!important` 滥用（仅打印态强制覆盖允许）。
- 禁止为了排版概括、删减或"优化"原文结论与不确定性表述。
- 禁止外链资源；禁止生成第二个 CSS/JS 文件。

---

## 12. 验收清单

**脚本化（可直接做成 Skill 生成后的自检）**

| 检查 | 判据 |
|---|---|
| 数据零改动 | 新旧文件 `REPORT_DATA` 字符串完全相等 |
| JS 语法 | `node --check`（提取 `<script>`）通过 |
| 占位符 | 模板占位符已全部替换 |
| 章节完整 | `card("sec-` 计数 = 预期章节数（本例 15） |
| 章节编号 | 依次为 空 / 维度一…维度七 / 专项一…专项四 / 空×3，且含「五维评分口径说明」 |
| 状态齐全 | 含 `@media print` / `html[data-theme="dark"]` / `@page{size:A4` / `@media(prefers-reduced-motion` |
| DOM 无异常 | 无头浏览器 `--dump-dom` 后 `undefined` / `NaN` 计数为 0 |
| 目录生成 | `data-target=` 链接数 ≈ 章节数 × 2（侧栏 + 横滑） |

**目视（无头浏览器截图，四屏）**：首屏 Hero + 概览 + 目录；风险卡区（四档色阶）；表格区（长文本换行）；综合评估区（雷达图 + 提示块）。逐屏确认无溢出、重叠、错位、空白异常。

> 环境备忘：DOM 校验可用本机无头浏览器 `--dump-dom`；经 PowerShell 管道会丢中文，需用托管 Python `subprocess` 取二进制结果。hash 锚点在 headless 下滚动不生效，截图时改为「隐藏其他章节、只留目标章节」的注入脚本。截图工具为可选，缺失时标记「未完成目视验证」并保留脚本化验收结论。

---

## 13. 复用流程（换行业报告时）

1. 按 `references/output_schema.md` 与 `references/data_contract.md` 产出 `REPORT_DATA`：字段、枚举、缺失标记照写，不补全、不四舍五入。
2. 复制 `assets/report_template.html`，把其中唯一的 `__REPORT_DATA__` 占位符逐字换成该对象字面量，另存为交付 HTML；**数据块零改动**，不得改写 CSS/HTML/JS。
3. 运行 `python assets/validate.py <报告.html>` 完成静态验收；轻量版与完整版各验一份。无头浏览器截图目视（首屏 / 风险卡 / 表格 / 综合评估）为可选增强。

包内相关文件：`assets/report_template.html`（模板）、`assets/validate.py`（验收）、`references/data_contract.md`（数据契约）、`references/html_ui_spec.md`（本规范）。

---

## 附录 A · 最小可复制 Token 块

```css
:root{
  --ink:#16233A; --ink-2:#3B4A61; --muted:#6B7A90; --faint:#9AA7B8;
  --navy:#122C4A; --navy-2:#1E4E79; --gold:#B8863B; --gold-soft:#F7F0E2;
  --bg:#F4F6F9; --card:#FFFFFF; --soft:#F7F9FC; --blue-soft:#EDF3FA;
  --line:#E3E8EF; --line-2:#EEF2F7;
  --risk-high:#C0392B; --risk-midhigh:#D2742B; --risk-mid:#B78A21; --risk-low:#1E7A52;
  --risk-high-bg:#FBEAE8; --risk-midhigh-bg:#FDF0E4; --risk-mid-bg:#FBF4DF; --risk-low-bg:#E8F5EE;
  --r-l:14px; --r:10px; --r-s:6px;
  --sp-1:4px; --sp-2:8px; --sp-3:12px; --sp-4:16px; --sp-5:24px; --sp-6:32px; --sp-7:48px;
  --shadow:0 1px 2px rgba(18,44,74,.04), 0 10px 28px rgba(18,44,74,.055);
  --font:"Microsoft YaHei","微软雅黑",sans-serif;
  --mono:var(--font);
}
body{font-family:var(--font);font-size:14px;line-height:1.75;font-variant-numeric:tabular-nums;}
```

完整 CSS（含暗色覆盖、组件规则、三档断点、A4 打印）见 `report_template.html` 的 `<style>` 段，建议整段复用而非重写。

## 附录 B · 组件构造函数签名（最小契约）

```js
function card(id,num,title,opt){}      // section.card + sec-head + sec-body
function grid(items,cols){}            // items:[{k,v,long,metric}]
function table(headers,rows,cls){}     // 外包裹 .table-scroll
function note(label,text,kind){}       // base|tip|key|warn
function src(label,text){}             // .source-line
function semanticTone(v){}             // 信贷语义色阶（TONE_RULES 优先级表）
function enumPill(v,dark){}            // 5 态展示映射，调用 semanticTone
function enumClass(v){}                // 同源映射
function tierBadge(src){}              // T1–T4
function buildRadar(d){}               // 内联 SVG
function render(){}; function buildToc(){}; function initUI(){}
render(); buildToc(); initUI();
```

## 附录 C · Skill 生成指令建议措辞

> 生成 HTML 报告时，**只输出 `REPORT_DATA` 对象**，字段与枚举严格遵循 schema；不得输出或修改任何 CSS/HTML/JS 模板代码，不得补全缺失数据、不得编造数值与来源。页面样式由固定模板渲染，规范见 `references/html_ui_spec.md`。生成完成后执行验收清单 §12，未通过则回炉。
