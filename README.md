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

本仓库**根目录就是技能内容**（`SKILL.md` 与 `assets/`、`references/` 同级），仓库里并没有 `preloan-industry-dd__skillhub/` 这个子目录——它只是安装时目标文件夹的命名。

### 方式一：git clone（推荐，便于后续升级）

```bash
git clone https://github.com/Crystylyos/Preloan-industry-dd.git \
  ~/.workbuddy/skills/preloan-industry-dd__skillhub
```

升级时进入该目录执行 `git pull` 即可。

### 方式二：下载压缩包

1. 仓库页右上 **Code → Download ZIP**；
2. 解压后把最外层目录重命名为 `preloan-industry-dd__skillhub`；
3. 整体复制到 `~/.workbuddy/skills/`（已存在同名目录则覆盖，即完成升级）；
4. 重开一次 WorkBuddy 会话，技能自动加载。

> 校验是否放对：目标目录下应能直接看到 `SKILL.md`。如果看到的是 `preloan-industry-dd__skillhub/SKILL.md` 之下的再一层同名目录，说明多套了一层，需要上提一层。

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
