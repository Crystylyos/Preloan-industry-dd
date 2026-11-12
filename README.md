# preloan-industry-dd · 商业银行贷前行业尽调与报告生成

按「七维度 + 四大专项」框架产出银行对公信贷贷前行业风险评估报告，并生成单文件 HTML 可视化页面（UI v2 契约、全站微软雅黑、轻量版/完整版自适应、原生 SVG 雷达图、零外部依赖）及可选的 Word/PDF 文档。

> The skill by Crystylyos

## 功能特性

- **七维度**：政策导向、周期阶段、盈利水平对标、产能供需、行业财务指标均值、行情研判、产业链位势与议价能力。
- **四大专项**：核心风险深度分析、目标区域实操核查清单、盈亏测算模板（含盈亏平衡曲线图）、ESG 与绿色信贷适配度。
- **数据与表现分离**：模型只产出 `REPORT_DATA`，模板保留 `__REPORT_DATA__` 占位符逐字注入。
- **信贷语义色阶**：按风险语义（而非字面「高/中/低」）统一着色警示。
- **固定 15 章节**：侧栏 + 横滑目录、暗色主题、A4 打印；原生 SVG，离线可用。
- **交付前独立返检底线**：数据完整 / 结构完整 / 口径标注 / 版式 / 合规 五项强制校验。

## 安装

### 方式一：技能市场安装（推荐）

在 WorkBuddy 对话中输入「安装技能 preloan-industry-dd」，或到技能市场搜索「贷前行业尽调」，安装后重开会话即可。市场安装会自动处理目录命名与版本升级，无需手动拷贝。

### 方式二：手动安装（离线 / 内网 / 从源码）

先按来源确认顶层结构，避免多套一层：

| 来源 | 解压或克隆后的顶层 | 处理 |
|---|---|---|
| 本仓库（git clone） | 根目录即技能内容（`SKILL.md` 与 `assets/`、`references/` 同级） | 见下方命令 |
| `..._github.zip` | `preloan-industry-dd__skillhub/` 文件夹 | 直接复制 |
| `..._vX.Y.Z.zip`（基础版） | `SKILL.md` 等散文件，无外层文件夹 | 自行放入同名文件夹 |

```bash
git clone https://github.com/Crystylyos/Preloan-industry-dd.git \
  ~/.workbuddy/skills/preloan-industry-dd__skillhub
```

也可下载 ZIP，把最外层目录重命名为 `preloan-industry-dd__skillhub`，整体复制到技能目录（已存在同名目录则覆盖，即完成升级）。

目标目录名统一为 `preloan-industry-dd__skillhub`，三个平台路径一致：

- Windows / macOS / Linux：`~/.workbuddy/skills/preloan-industry-dd__skillhub/`

> 校验：目标目录下应能直接看到 `SKILL.md`；若还隔着一层同名目录，说明多套了一层，需要上提。

## 使用

触发示例：「对工程机械做贷前行业尽调」「生成光伏行业风险报告」「某行业授信前行业研判」。

运行环境自检（只读、不联网、不读凭据）：

```bash
python scripts/check_environment.py
```

## 目录结构

```
SKILL.md                     技能说明与触发条件（含 frontmatter 元数据）
LICENSE                      MIT 许可证
README.md                   本文件
assets/report_template.html HTML 报告 UI v2 模板
assets/generate_docx.py     Word/PDF 生成（需 python-docx）
assets/validate.py          交付前静态校验（零外链 / 脚本完整 / 数据块可解析）
references/                 数据契约、输出结构、UI 规范、发布指南、变更说明 等
scripts/check_environment.py 环境自检
skill-dependencies.json     依赖声明
```

## 许可

[MIT](LICENSE) — Copyright (c) 2026 Crystylyos
