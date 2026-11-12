# 依赖配置与就绪指南

本技能三类能力依赖不同环境，按「必需 / 可选 / 运行时」分别说明。

## 一、必需：python-docx（Word 交付）

仅当需生成 Word/PDF 归档材料时使用。

- 安装：`pip install python-docx`（建议在隔离 venv 中安装，避免污染全局环境）。
- 验证：`python -c "import docx; print(docx.__version__)"` 能输出版本即就绪。
- 降级：未安装时跳过 Word，仅交付 HTML / XML / Markdown；PDF 可由生成的 Word 另存获得。
- 安全：python-docx 仅读取用户提供的 `report_data.json` 并写出 `.docx`，不联网、不读取凭据。

## 二、可选：金融与工商数据 MCP 连接器

以下连接器提供结构化数据，未连接时技能自动回落网页检索（WebSearch），不影响核心流程。

| 连接器 | 用途 | 启用位置 | 最小权限 | 安全存储 |
|---|---|---|---|---|
| Wind / 同花顺妙想(mx-ds-mcp) | 行情、行业、财报 | WorkBuddy 连接器管理 | 只读查询 | 由连接器托管，技能内不保存 Token |
| 企查查(qcc-company) | 工商与司法风险 | WorkBuddy 连接器管理 | 只读查询 | 由连接器托管 |
| 北大法宝/法研(PKULaw) | 法规与监管文本 | WorkBuddy 连接器管理 | 只读查询 | 由连接器托管 |

- 验证：在 WorkBuddy 连接器管理中确认状态为「已连接」；技能运行时优先调用其结构化接口，来源标注「MCP-接口名」。
- 轮换/撤销：在连接器管理中重连或断开即可；技能不缓存任何凭据。
- 注意：上述连接器的具体开通入口与权限以各平台官方文档为准；技能仅消费其输出，不代为授权。

## 三、运行时

- Python >= 3.8（`generate_docx.py`、`validate.py`、`check_environment.py`）。
- WebSearch 工具（网页检索兜底，始终可用）。

## 四、就绪路由

运行 `python scripts/check_environment.py`：

- `ready`：python-docx 已装，可直接生成 Word。
- `needs_setup`：python-docx 缺失，按上文安装；不影响 HTML/XML/Markdown 交付。
- 可选 MCP 缺失：始终 `partial`，核心流程继续并标注受影响功能。
