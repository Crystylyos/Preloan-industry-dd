# 数据契约（Data Contract）：REPORT_DATA / report_data.json

本文件定义 HTML 模板 `assets/report_template.html` 中的 `REPORT_DATA` 对象，以及 Word 生成脚本 `assets/generate_docx.py` 读取的 `report_data.json` 必须同构的 JSON 字段结构。XML 报告（`references/output_schema.md`）是同一份事实的标签化表达，三者须保持一致。

> 约定：所有键均为小写驼峰；缺失字段以 `null` 或空字符串表示，不得省略键名（脚本以 `.get()` 兜底，缺键不报错但会留白）。

## 顶层结构

```text
{
  "header":     { ... },      // 报告头部
  "company":    { ... },      // 可选：目标企业财务速览
  "dimensions": { ... },      // 七大基础维度
  "special":    { ... },      // 四大专项模块
  "assessment": { ... },      // 综合评估
  "notes":      { ... },      // 报告核心说明
  "disclaimer": "..."         // 免责声明
}
```

## 字段明细

### header
`industry`(行业名) · `rating`(综合风险评级) · `redAlert`(红色预警触发/无) · `analysisDate`(YYYY-MM-DD) · `dataAsOf`(数据截止) · `dataTimeliness`(时效判断) · `outputMode`(完整版/轻量速览版) · `summary`(一句话结论≤80字)

### company（可选）
`asOf` · `name` · `items`(数组，每项 `{k, v}`) · `note`

### dimensions
- `policy`：conclusion / confidence / certainty / redAlert / steps[] / policies[{name,org,date,summary,impact}] / decisionTip / source / gap
- `cycle`：conclusion / confidence / certainty / redAlert / steps[] / matrix{rev,capex,inventory,price,entrants,pos} / decisionTip / source / gap
- `profit`：conclusion / confidence / certainty / redAlert / srcNote / items[{name,ent,avg,dev,eval}] / reason / decisionTip / gap
- `supply`：conclusion / confidence / certainty / redAlert / steps[] / metrics{util,invDays,priceChg,newCap} / outlook / decisionTip / source / gap
- `financial`：srcNote / sample{n,filter,window} / items[{name,avg,mid,ok,warn,miss}]
- `market`：conclusion / confidence / certainty / redAlert / nationwide / region{cluster,policy,risk} / forecast{overall,drivers[],uncertainty} / decisionTip / source / gap
- `chain`：conclusion / confidence / certainty / redAlert / steps[] / metrics{upstream,downstream,conduction,profitShare} / riskMeaning / decisionTip / source / gap

### special
- `risks[]`：{name, level, desc, path, measures, source}
- `checklist`：region / usage / categories[{name, items[]}] / guarantee{regionNote, items[{name, content}]}
- `projectCalc`：applicable(bool) / note / scenario / assumption / params[{name,unit,val,note}] / firstYear[{name,unit,val,logic}] / metrics[{name,unit,val,eval}] / stress[{name,change,judge}] / thresholds{normal,caution,forbid} / source / chart{qUnit,pUnit,depYears,otherFixed}（可选）。`depYears` 仅用于会计口径折旧；现金平衡点由「年利息支出 + otherFixed」自动推算，不需要额外字段。`qUnit` / `pUnit` 缺省时分别取自「设计产能」与「产品现货单价」的单位。

  > **专项三开关规则（硬约束）**：`applicable` 为布尔值，不得用字符串。**只要输出专项三，无论完整版还是轻量速览版，都必须为 `true`**，且 `params` ≥ 8、`firstYear` ≥ 4、`metrics` ≥ 4、`stress` ≥ 4。轻量速览版同样输出行业基准测算，表头注明「行业基准示例值 · 非目标企业」，不因缺企业数据而省略。仅两种情况可为 `false`：① 确属非项目制行业（纯贸易 / 纯服务），`note` 写明「非项目制」或「数据缺失-D」；② 用户明确要求不出测算。误填 `false` 会让整章只剩「不适用说明」，`assets/validate.py` 判不合格并阻断交付。

  > **单位与盈亏图（重要）**：盈亏平衡图的单位**取自数据、不写在代码里**。`params` 中「设计产能」的 `unit` 决定横轴单位（如 `万吨/年`、`台/年`，显示时去掉「/年」），「产品现货单价」的 `unit` 决定价格单位（如 `元/吨`、`万元/台`）；投资与成本的金额单位按 `亿元 / 万元 / 元` 自动换算到万元。可选 `chart` 用于覆盖折旧年限与其他固定费用（缺省 10 年 / 0）。
  >
  > **单价的分母必须与产能单位一致**，否则单价与单位变动成本不同量级、无法相减，图会退化为「单价 ≤ 单位变动成本、无平衡点」。例：产能写 `MW/年` 时，单价须写 `万元/MW`（0.85 元/W = 85 万元/MW），不能写 `元/W`；产能写 `台/年` 时，单价写 `万元/台`。换行业务必保留 `unit` 字段，否则图表回落为「单位 / 元每单位」。
- `esg`：env{intensity,substitution,carbon} / social{labor,supply} / gov{record,disclosure} / fit{rating,support,constraint} / source

### assessment
`radar`{policy, cycle, profit, supply, finance, score}（各 1–5，score 为五项均值保留一位小数）· `topRisks[]` · `topStrengths[]` · `strategy`{overall, quota, measures, focus} · `compliance`(建议法务专项审查事项/无)

### notes
`boundary`(行业边界界定) · `logic`(核心风险逻辑) · `differentiation`(差异化策略)

### disclaimer
字符串（与 XML 免责声明一致）

## XML → JSON 映射要点

- 维度判定结论、置信度、数据确定性、维度红色预警 → 各 `dimensions.*` 对应字段。
- 综合风险评级、一句话结论、红色预警触发 → `header`。
- 风险雷达五轴 → `assessment.radar`（维度七与专项四不纳入雷达轴，见 output_schema.md）。
- 任一 `<数据来源>` 字段须含 T1–T4 标记（见 `references/source_tiers.md`）。

## 最小可用示例

```json
{
  "header": {
    "industry": "光伏制造（晶硅组件）",
    "rating": "中风险",
    "redAlert": "无",
    "analysisDate": "2026-10-23",
    "dataAsOf": "2026-09-30",
    "dataTimeliness": "近12个月内",
    "outputMode": "完整版",
    "summary": "产能阶段性过剩但技术迭代领先，建议择优介入、严控产能过剩环节新增授信。"
  },
  "dimensions": {
    "policy": {"conclusion":"扶持类","confidence":"高","certainty":"确凿数据","redAlert":"无",
      "steps":["《产业结构调整指导目录》列为鼓励类"],"policies":[],
      "decisionTip":"优先支持","source":"【T1】发改委《产业结构调整指导目录（2024年本）》","gap":"无"},
    "cycle": {"conclusion":"底部震荡","confidence":"中","certainty":"合理推断","redAlert":"无",
      "steps":[],"matrix":{"rev":"↓","capex":"↓","inventory":"偏高","price":"↓","entrants":"减少","pos":"底部区域"},
      "decisionTip":"审慎介入","source":"【T3】CPIA 运行报告","gap":"无"},
    "profit": {"conclusion":"持平行业均值","confidence":"中","certainty":"确凿数据","redAlert":"无",
      "srcNote":"行业均值见 dimensions.financial","items":[],"reason":"数据缺失-D（未提供企业财务）","decisionTip":"按行业均值定价","gap":"数据缺失-D"},
    "supply": {"conclusion":"供给过剩","confidence":"高","certainty":"确凿数据","redAlert":"无",
      "steps":[],"metrics":{"util":"62%","invDays":"90","priceChg":"-18%","newCap":"8%"},
      "outlook":"未来1年供需缓慢修复","decisionTip":"压降产能过剩环节授信","source":"【T1】Wind 行业数据","gap":"无"},
    "financial": {"srcNote":"基于23家A股上市公司2025年报加权平均","sample":{"n":"23","filter":"A股+北交所同行业剔除ST","window":"2025年报"},
      "items":[{"name":"资产负债率","avg":"58%","mid":"56%","ok":"40%-65%","warn":"70%","miss":"有数据"}]},
    "market": {"conclusion":"承压下行","confidence":"中","certainty":"合理推断","redAlert":"无",
      "nationwide":"全球装机增速放缓","region":{"cluster":"江浙皖集群集中","policy":"绿色信贷支持","risk":"互保圈需排查"},
      "forecast":{"overall":"平稳运行","drivers":["海外需求","技术迭代"],"uncertainty":"贸易壁垒"},
      "decisionTip":"区域差异化授信","source":"【T3】券商研报","gap":"无"},
    "chain": {"conclusion":"中性","confidence":"中","certainty":"合理推断","redAlert":"无",
      "steps":[],"metrics":{"upstream":"集中","downstream":"分散","conduction":"部分传导","profitShare":"中游约25%"},
      "riskMeaning":"中游加工环节两头受挤","decisionTip":"偏好具上游绑定主体","source":"【T3】行业研报","gap":"无"}
  },
  "special": {
    "risks":[{"name":"产能过剩价格战","level":"中高风险","desc":"产能利用率低位、价格下行","path":"盈利恶化→还款来源弱化","measures":"严控新增、存量压降","source":"【T1】Wind"}],
    "checklist":{"region":"江苏省","usage":"现场尽调核查","categories":[{"name":"合规资质类","items":["环评批复","安全生产许可证"]}],
      "guarantee":{"regionNote":"江浙沪互保高发","items":[{"name":"互保规模与对手方资质","content":"担保余额/净资产超30%即预警"}]}},
    "projectCalc": {
      "applicable": true,
      "note": "",
      "scenario": "新建组件产能项目，用于判断产能类授信能否由项目自身现金流覆盖",
      "assumption": "区域平均水平与行业通用参数，实际项目须替换真实成本结构",
      "params": [
        {"name": "设计产能", "unit": "MW/年", "val": "200", "note": "组件产线年产能"},
        {"name": "产品现货单价", "unit": "万元/MW", "val": "85", "note": "组件含税均价，由 0.85 元/W 折算（1 元/W = 100 万元/MW）"},
        {"name": "项目总投资", "unit": "亿元", "val": "3.2", "note": "含设备与土建"},
        {"name": "年利息支出", "unit": "万元", "val": "1200", "note": "贷款占比 60%、利率 3.5% 估算"},
        {"name": "基准产能利用率", "unit": "%", "val": "75", "note": "行业景气中枢"},
        {"name": "银行贷款占比", "unit": "%", "val": "60", "note": "项目融资结构"},
        {"name": "贷款年利率", "unit": "%", "val": "3.5", "note": "制造业中长期贷款"},
        {"name": "单位产能投资", "unit": "元/W", "val": "1.6", "note": "行业投资强度"}
      ],
      "firstYear": [
        {"name": "年销售量", "unit": "MW", "val": "150", "logic": "设计产能 × 利用率"},
        {"name": "年营业收入", "unit": "亿元", "val": "1.28", "logic": "销量 × 单价"},
        {"name": "年营业成本", "unit": "亿元", "val": "1.15", "logic": "材料 + 人工 + 制造费用"},
        {"name": "EBIT（未扣期间费用与折旧）", "unit": "亿元", "val": "0.13", "logic": "营业收入 − 营业成本"}
      ],
      "metrics": [
        {"name": "全投资内部收益率 IRR", "unit": "%", "val": "7.8", "eval": "达标"},
        {"name": "静态投资回收期", "unit": "年", "val": "8.1", "eval": "达标"},
        {"name": "利息保障倍数", "unit": "倍", "val": "2.4", "eval": "审慎"},
        {"name": "贷款偿还期", "unit": "年", "val": "9.0", "eval": "达标"}
      ],
      "stress": [
        {"name": "组件价格下跌 10%", "change": "IRR 降至 4.9%", "judge": "不可接受"},
        {"name": "销量下降 20%", "change": "IRR 降至 5.2%", "judge": "审慎"},
        {"name": "硅料成本上涨 15%", "change": "IRR 降至 6.0%", "judge": "审慎"},
        {"name": "融资利率上行 100BP", "change": "IRR 降至 7.2%", "judge": "可控"}
      ],
      "thresholds": {"normal": "IRR ≥ 8%", "caution": "IRR 5%–8%", "forbid": "IRR < 5%"},
      "source": "【T3】行业基准示例值",
      "chart": {"depYears": 10, "otherFixed": 0}
    },
    "esg":{"env":{"intensity":"中","substitution":"高","carbon":"CBAM敞口中等"},"social":{"labor":"正常","supply":"需溯源"},"gov":{"record":"无重大处罚","disclosure":"较好"},"fit":{"rating":"中性","support":"清洁技术","constraint":"环评前置"},"source":"【T1】生态环境部"}
  },
  "assessment":{"radar":{"policy":2,"cycle":3,"profit":3,"supply":4,"finance":3,"score":3.0},
    "topRisks":["产能过剩价格战","贸易壁垒","互保圈风险"],"topStrengths":["技术领先","政策支持","海外需求"],
    "strategy":{"overall":"审慎介入","quota":"单户上限按行业敞口","measures":"抵质押+资金监管","focus":"产能利用率/价格"},
    "compliance":"无"},
  "notes":{"boundary":"覆盖晶硅组件制造环节","logic":"产能+价格+互保三重叠加时压缩授信","differentiation":"偏好技术领先与上游绑定主体"},
  "disclaimer":"本报告基于公开数据和AI分析生成，仅供信贷审批参考，不构成最终信贷决策依据。"
}
```

## 契约维护纪律

- 修改 XML 标签体系时，须同步更新本文件与 `report_template.html` 的 `REPORT_DATA`、否则 HTML/Word 渲染缺字段。
- 交付前运行 `python assets/validate.py <报告.html>` 确认零外部依赖、脚本完整、数据块可解析。
