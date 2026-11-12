# 安装与发布说明（preloan-industry-dd）

适用版本：1.0.5。版本号见 SKILL.md frontmatter，历史变更见 `references/changelog.md`，出错处置见 `references/troubleshooting.md`。

## 一、安装（Install）

### 方式一：目录放置（推荐）

三种来源解压后的顶层结构不同，先按下表确认，再放入技能目录：

| 来源 | 解压/克隆后的顶层 | 处理方式 |
|---|---|---|
| `preloan-industry-dd_vX.Y.Z.zip`（基础版） | `SKILL.md` 等散文件，**无外层文件夹** | 自行放入 `preloan-industry-dd__skillhub/` |
| `preloan-industry-dd_vX.Y.Z_github.zip` | `preloan-industry-dd__skillhub/` 文件夹 | 直接复制 |
| GitHub 仓库 | 根目录即技能内容 | `git clone <仓库地址> ~/.workbuddy/skills/preloan-industry-dd__skillhub` |

1. 按上表确认顶层结构，避免多套一层或直接散落。
2. 确保目标目录名为 `preloan-industry-dd__skillhub`，置于 `~/.workbuddy/skills/`（同名目录被覆盖，即完成升级）。
3. 重开或刷新 WorkBuddy 会话，技能自动加载。

> 自检：目标目录下应能直接看到 `SKILL.md`。

### 方式二：技能市场安装
若已发布到 WorkBuddy 推荐市场，在对话输入 `安装技能 preloan-industry-dd` 由系统自动完成。

### 验证加载
- 输入"对光伏制造做贷前行业尽调"等表述应触发本技能。
- 运行环境检查（只读，不联网、不读凭据）：`python scripts/check_environment.py`。

### 回滚
- 升级前建议备份旧版（独立目录或 zip）。历史备份示例：`preloan-industry-dd__skillhub_v5.2.1_backup`。
- 回滚：用备份文件夹覆盖 `~/.workbuddy/skills/preloan-industry-dd__skillhub/` 即可。

## 二、发布（Publish）

### 分发压缩包
- 直接分享 `preloan-industry-dd_vX.Y.Z.zip`。
- 发布时附 SHA256 校验值，接收方解压后比对完整性（重新打包后以实际 SHA256 为准）。

### 上架技能市场
- 走 WorkBuddy 技能市场提交流程（需平台侧操作，非本技能代为执行）。
- 提交物为本技能文件夹：含 SKILL.md、references/、assets/、scripts/、skill-dependencies.json。

### 依赖声明（skill-dependencies.json）
- **必需**：python-docx（仅 Word/PDF 交付需要；HTML/XML/Markdown 不需要）。
- **可选**：Wind / 同花顺妙想 / 企查查 / 北大法宝 等金融工商 MCP，未连接时自动回落网页检索，不影响核心流程。详见 `references/setup-guide.md`。

### 兼容性
- HTML 报告单文件、无外部依赖，浏览器双击即开；全站微软雅黑，风险雷达为原生 SVG，离线可用；含侧栏目录、暗色主题与 A4 打印样式。
- Word 报告由 `assets/generate_docx.py` 生成，需 python-docx。

## 三、上架 skillhub

上架信息写在 SKILL.md 头部：`slug`、`version`、`displayName` 为必需；`summary`、`description`、`tags` 用于商店展示；`license: MIT` 与 `homepage: https://skillhub.cn/skills/user_63ec19e2/preloan-industry-dd` 已由作者确认补充。

- 本地预检（只校验头部信息，不联网、不发布）：`python ~/.skillhub/skills_store_cli.py --skip-self-upgrade publish --dry-run <技能目录>`。
- 预检通过后由作者本人登录后发布；本技能不代为发布，不保存任何 Token。
- 发布包不含本地安装态元数据 `_meta.json` 与 `_skillhub_meta.json`，避免把本机路径带上架。
- `skill-dependencies.json` 是技能自用的依赖说明，平台发布不校验其结构。
## 三、合规与边界
- 本报告基于公开数据与 AI 分析，仅供信贷审批参考，不构成最终信贷决策。
- 模型不输出"贷或不贷"结论，最终由审批委员会裁定。
- 交付前建议运行 `python assets/validate.py <报告.html>` 校验零外部依赖与数据块完整性。

## 四、来源分级（T1–T4）速览
- 每条数据来源须在字符串前置【T1】–【T4】标记（一手权威 / 官方自述 / 独立第三方 / 个人与存疑）。
- T4 不得单独支撑结论；HTML 报告自动渲染为彩色溯源徽标。规则详见 `references/source_tiers.md`。
