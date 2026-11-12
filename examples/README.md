# 开箱即用样例

三份可直接运行的 `REPORT_DATA`，覆盖专项三的三个分支，用于**上手试跑**与**交付前返检**。

| 文件 | 场景 | 专项三 | 看点 |
|---|---|---|---|
| `report_data_full.json` | 工程机械（项目制，完整版） | `applicable: true` | 8 参数 / 4 项首年测算 / 4 指标 / 4 压力场景齐全，含 `chart` 覆盖折旧与固定费用 |
| `report_data_light.json` | 光伏（轻量速览版） | `applicable: false` | 无企业数据，维度三自动收起企业值列，专项三收起整章 |
| `report_data_nonproject.json` | 钢材贸易（非项目制，完整版） | `applicable: false` + 原因代码 | 演示「非项目制」合法例外：note 注明`非项目制`/`数据缺失-D` 即可通过校验 |

> 样例中企业名称与财务数字均为**演示用示例数据**，不代表任何真实主体；行业判断仅作结构示范，不可直接用于授信决策。

## 用法一：一键自检（推荐）

```bash
python assets/selftest.py            # 结构 + 契约 + 色阶，秒级
python assets/selftest.py --browser  # 追加真实渲染核验（需本机 Edge/Chrome）
```

校验项包括：模板占位符唯一、章节数 15、样例 JSON 可解析、注入无残留、零外部依赖、专项三契约、Word 与 HTML 风险色同源。

## 用法二：生成一份 HTML

把样例注入模板即可（模板中 `__REPORT_DATA__` 恰好一个）：

```bash
python - <<'PY'
import json, pathlib
tpl = pathlib.Path("assets/report_template.html").read_text(encoding="utf-8")
data = json.loads(pathlib.Path("examples/report_data_full.json").read_text(encoding="utf-8"))
pathlib.Path("示例报告.html").write_text(
    tpl.replace("__REPORT_DATA__", json.dumps(data, ensure_ascii=False)), encoding="utf-8")
print("已生成 示例报告.html")
PY
```

再跑一次交付校验：

```bash
python assets/validate.py 示例报告.html
```

## 用法三：生成 Word

```bash
python assets/generate_docx.py examples/report_data_full.json 示例报告.docx
```

需先 `pip install python-docx`；缺失时只交付 HTML。

## 改造建议

- 换行业时，优先替换 `special.projectCalc.params` 与 `firstYear` 的 `name` / `unit` / `val`，**保留 `unit` 字段**——盈亏图的产量与金额单位直接取自它，缺失会回落为「单位 / 元每单位」。
- 完整版务必保留 `applicable: true` 且满足门槛（`params`≥8、`firstYear`≥4、`metrics`≥4、`stress`≥4），否则校验器会判不合格。
- 确属非项目制行业（纯贸易、纯服务），把 `applicable` 设为 `false` 并在 `note` 写明「非项目制」或「数据缺失-D」。
