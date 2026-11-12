#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
preloan-industry-dd · V5.0 Word 交付脚本
---------------------------------------
读取与本技能 assets/report_template.html 中 REPORT_DATA 同构的 JSON 文件，
生成一份格式化的商业银行贷前行业尽调 Word 文档（含章节、表格、风险色卡）。

用法：
    python generate_docx.py report_data.json [输出文件名.docx]

依赖：python-docx
    pip install python-docx
"""

import sys
import json
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ---------- 颜色 ----------
NAVY = RGBColor(0x1A, 0x2C, 0x4E)
SLATE = RGBColor(0x46, 0x56, 0x6E)
INK = RGBColor(0x1F, 0x27, 0x33)
# 风险四档色：与 assets/report_template.html 的 --risk-* 变量逐值一致，
# 保证 HTML 与 Word 两份交付物色阶同源（旧版 Word 只有三档，「中高」被并入红档且色值不同）
RISK_HIGH = "C0392B"
RISK_MIDHIGH = "D2742B"
RISK_MID = "B78A21"
RISK_LOW = "1E7A52"
RISK_UNKNOWN = "46566E"


def shade_cell(cell, hex_color):
    """为单元格设置底纹色"""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)


def set_cell_text(cell, text, bold=False, color=None, size=10, align=None):
    cell.text = ""
    p = cell.paragraphs[0]
    if align:
        p.alignment = align
    run = p.add_run(str(text) if text is not None else "")
    run.bold = bold
    run.font.size = Pt(size)
    run.font.name = "Microsoft YaHei"
    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
    if color:
        run.font.color.rgb = color


def risk_color(level):
    """返回风险四档色（6 位 hex），与 HTML 模板 --risk-* 色阶逐值一致。

    判定顺序即优先级：先「中高」再「高」。旧版按「含高即红」判定，导致
    「中高风险」被染成高风险色，四档塌成三档，与页面不一致。
    """
    s = str(level or "")
    if "中高" in s:
        return RISK_MIDHIGH
    if "高" in s:
        return RISK_HIGH
    if "中" in s:
        return RISK_MID
    if "低" in s:
        return RISK_LOW
    return RISK_UNKNOWN


def hex_rgb(h):
    """6 位 hex 转为 RGBColor。"""
    h = str(h or "")[:6].ljust(6, "0")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def add_heading(doc, text, level=1):
    h = doc.add_heading(level=level)
    run = h.add_run(text)
    run.font.name = "Microsoft YaHei"
    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
    if level == 1:
        run.font.color.rgb = NAVY
        run.font.size = Pt(15)
    else:
        run.font.color.rgb = SLATE
        run.font.size = Pt(12)
    return h


def add_kv_table(doc, pairs, cols=2):
    """pairs: list of (key, value)"""
    n = len(pairs)
    rows = (n + cols - 1) // cols
    table = doc.add_table(rows=rows, cols=cols * 2)
    table.style = "Light Grid Accent 1"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, (k, v) in enumerate(pairs):
        r = idx // cols
        c = (idx % cols) * 2
        set_cell_text(table.cell(r, c), k, bold=True, color=NAVY, size=9)
        shade_cell(table.cell(r, c), "EEF3FB")
        set_cell_text(table.cell(r, c + 1), v, size=10)
    return table


def add_grid_table(doc, headers, rows, widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Light Grid Accent 1"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = table.rows[0].cells
    for i, htext in enumerate(headers):
        set_cell_text(hdr[i], htext, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF), size=9,
                      align=WD_ALIGN_PARAGRAPH.CENTER)
        shade_cell(hdr[i], "243B63")
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            set_cell_text(cells[i], val, size=9)
    return table


def add_para(doc, text, bold_prefix=None, size=10):
    p = doc.add_paragraph()
    if bold_prefix:
        r1 = p.add_run(bold_prefix)
        r1.bold = True
        r1.font.size = Pt(size)
        r1.font.name = "Microsoft YaHei"
        r1._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
    r2 = p.add_run(text or "")
    r2.font.size = Pt(size)
    r2.font.name = "Microsoft YaHei"
    r2._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
    return p


def build(data, out_path):
    doc = Document()
    # 默认正文字体
    style = doc.styles['Normal']
    style.font.name = "Microsoft YaHei"
    style._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
    style.font.size = Pt(10)

    H = data.get("header", {})
    D = data.get("dimensions", {})
    S = data.get("special", {})
    A = data.get("assessment", {})
    N = data.get("notes", {})

    # 标题
    title = doc.add_heading(level=0)
    trun = title.add_run("商业银行贷前行业尽调报告 · " + str(H.get("industry", "")))
    trun.font.name = "Microsoft YaHei"
    trun._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

    # 报告头部
    add_heading(doc, "报告头部", 1)
    if H.get("redAlert") and H.get("redAlert") != "无":
        add_para(doc, "⚠️ 红色预警：" + str(H.get("redAlert")), bold_prefix="", size=11)
    add_kv_table(doc, [
        ("综合风险评级", H.get("rating", "")),
        ("红色预警触发", H.get("redAlert", "无")),
        ("分析日期", H.get("analysisDate", "")),
        ("数据截止", H.get("dataAsOf", "")),
        ("数据时效", H.get("dataTimeliness", "—")),
        ("输出模式", H.get("outputMode", "完整版")),
    ])
    add_para(doc, H.get("summary", ""), bold_prefix="一句话结论：", size=11)

    # 目标企业财务速览（仅当 JSON 含 company 时渲染）
    C = data.get("company")
    if C:
        add_heading(doc, "目标企业财务速览（" + str(C.get("asOf", "")) + "）", 1)
        add_para(doc, C.get("name", ""), bold_prefix="企业名称：", size=11)
        pairs = [(x.get("k", ""), x.get("v", "")) for x in C.get("items", [])]
        add_kv_table(doc, pairs, cols=2)
        if C.get("note"):
            add_para(doc, C.get("note"), bold_prefix="数据说明：", size=9)

    # 维度一 政策导向
    p = D.get("policy", {})
    add_heading(doc, "维度一 政策导向", 1)
    add_kv_table(doc, [("判定结论", p.get("conclusion", "")), ("置信度", p.get("confidence", "")),
                       ("数据确定性", p.get("certainty", ""))])
    if p.get("redAlert") and p.get("redAlert") != "无":
        add_para(doc, "⚠️ 红色预警：" + str(p.get("redAlert")))
    for s in p.get("steps", []):
        add_para(doc, s)
    policies = p.get("policies", [])
    if policies:
        add_grid_table(doc, ["文件名称", "发文机关", "发布日期", "核心条款摘要", "对本行业影响"],
                       [[x.get("name", ""), x.get("org", ""), x.get("date", ""),
                         x.get("summary", ""), x.get("impact", "")] for x in policies])
    add_para(doc, p.get("decisionTip", ""), bold_prefix="信贷决策提示：")
    add_para(doc, "数据来源：" + str(p.get("source", "")) + " ｜ 数据缺口与弥补：" + str(p.get("gap", "")),
             size=9)

    # 维度二 周期阶段
    cy = D.get("cycle", {})
    add_heading(doc, "维度二 周期阶段", 1)
    add_kv_table(doc, [("判定结论", cy.get("conclusion", "")), ("置信度", cy.get("confidence", "")),
                       ("数据确定性", cy.get("certainty", ""))])
    if cy.get("redAlert") and cy.get("redAlert") != "无":
        add_para(doc, "⚠️ 红色预警：" + str(cy.get("redAlert")))
    for s in cy.get("steps", []):
        add_para(doc, s)
    m = cy.get("matrix", {})
    add_kv_table(doc, [("营收增速", m.get("rev", "")), ("资本开支", m.get("capex", "")),
                       ("库存水位", m.get("inventory", "")), ("产品价格", m.get("price", "")),
                       ("新进入者", m.get("entrants", "")), ("综合周期位置", m.get("pos", ""))])
    add_para(doc, cy.get("decisionTip", ""), bold_prefix="信贷决策提示：")
    add_para(doc, "数据来源：" + str(cy.get("source", "")) + " ｜ 数据缺口与弥补：" + str(cy.get("gap", "")), size=9)

    # 维度三 盈利水平对标
    pr = D.get("profit", {})
    add_heading(doc, "维度三 盈利水平对标", 1)
    add_kv_table(doc, [("判定结论", pr.get("conclusion", "")), ("置信度", pr.get("confidence", "")),
                       ("数据确定性", pr.get("certainty", ""))])
    if pr.get("redAlert") and pr.get("redAlert") != "无":
        add_para(doc, "⚠️ 红色预警：" + str(pr.get("redAlert")))
    add_para(doc, "行业均值来源：" + str(pr.get("srcNote", "")), size=9)
    items = pr.get("items", [])
    if items:
        add_grid_table(doc, ["指标", "企业值", "行业均值", "偏离度", "评价"],
                       [[x.get("name", ""), x.get("ent", ""), x.get("avg", ""),
                         x.get("dev", ""), x.get("eval", "")] for x in items])
    add_para(doc, pr.get("reason", ""), bold_prefix="差异原因：")
    add_para(doc, pr.get("decisionTip", ""), bold_prefix="信贷决策提示：")
    add_para(doc, "数据缺口与弥补：" + str(pr.get("gap", "")), size=9)

    # 维度四 产能供需
    sp = D.get("supply", {})
    add_heading(doc, "维度四 产能供需", 1)
    add_kv_table(doc, [("判定结论", sp.get("conclusion", "")), ("置信度", sp.get("confidence", "")),
                       ("数据确定性", sp.get("certainty", ""))])
    if sp.get("redAlert") and sp.get("redAlert") != "无":
        add_para(doc, "⚠️ 红色预警：" + str(sp.get("redAlert")))
    for s in sp.get("steps", []):
        add_para(doc, s)
    sm = sp.get("metrics", {})
    add_kv_table(doc, [("产能利用率", sm.get("util", "")), ("产成品库存天数", sm.get("invDays", "")),
                       ("产品价格同比", sm.get("priceChg", "")), ("未来1年新增产能", sm.get("newCap", ""))])
    add_para(doc, sp.get("outlook", ""), bold_prefix="供需格局展望：")
    add_para(doc, sp.get("decisionTip", ""), bold_prefix="信贷决策提示：")
    add_para(doc, "数据来源：" + str(sp.get("source", "")) + " ｜ 数据缺口与弥补：" + str(sp.get("gap", "")), size=9)

    # 维度五 行业财务指标均值
    f = D.get("financial", {})
    add_heading(doc, "维度五 行业财务指标均值", 1)
    add_para(doc, f.get("srcNote", ""), size=9)
    samp = f.get("sample", {})
    add_kv_table(doc, [("样本企业数量", samp.get("n", "")), ("筛选标准", samp.get("filter", "")),
                       ("数据窗口", samp.get("window", ""))])
    fitems = f.get("items", [])
    if fitems:
        add_grid_table(doc, ["指标", "行业均值", "中位数", "合理区间", "警戒线", "缺失标记"],
                       [[x.get("name", ""), x.get("avg", ""), x.get("mid", ""), x.get("ok", ""),
                         x.get("warn", ""), x.get("miss", "")] for x in fitems])

    # 维度六 行情研判
    mk = D.get("market", {})
    add_heading(doc, "维度六 行情研判", 1)
    add_kv_table(doc, [("判定结论", mk.get("conclusion", "")), ("置信度", mk.get("confidence", "")),
                       ("数据确定性", mk.get("certainty", ""))])
    if mk.get("redAlert") and mk.get("redAlert") != "无":
        add_para(doc, "⚠️ 红色预警：" + str(mk.get("redAlert")))
    add_para(doc, mk.get("nationwide", ""), bold_prefix="全国发展现状：")
    region = mk.get("region", {})
    add_kv_table(doc, [("产能与集群", region.get("cluster", "")), ("政策与监管", region.get("policy", "")),
                       ("区域风险特征", region.get("risk", ""))])
    fc = mk.get("forecast", {})
    add_para(doc, fc.get("overall", ""), bold_prefix="总体研判：")
    add_para(doc, "、".join(fc.get("drivers", [])), bold_prefix="关键驱动：")
    add_para(doc, fc.get("uncertainty", ""), bold_prefix="关键不确定性：")
    add_para(doc, mk.get("decisionTip", ""), bold_prefix="信贷决策提示：")
    add_para(doc, "数据来源：" + str(mk.get("source", "")) + " ｜ 数据缺口与弥补：" + str(mk.get("gap", "")), size=9)

    # 维度七 产业链位势与议价能力
    ch = D.get("chain", {})
    add_heading(doc, "维度七 产业链位势与议价能力", 1)
    add_kv_table(doc, [("判定结论", ch.get("conclusion", "")), ("置信度", ch.get("confidence", "")),
                       ("数据确定性", ch.get("certainty", ""))])
    if ch.get("redAlert") and ch.get("redAlert") != "无":
        add_para(doc, "⚠️ 红色预警：" + str(ch.get("redAlert")))
    for s in ch.get("steps", []):
        add_para(doc, s)
    cm = ch.get("metrics", {})
    add_kv_table(doc, [("上游集中度", cm.get("upstream", "")), ("下游集中度", cm.get("downstream", "")),
                       ("成本传导能力", cm.get("conduction", "")), ("本环节利润占比", cm.get("profitShare", ""))])
    add_para(doc, ch.get("riskMeaning", ""), bold_prefix="信贷风险含义：")
    add_para(doc, ch.get("decisionTip", ""), bold_prefix="信贷决策提示：")
    add_para(doc, "数据来源：" + str(ch.get("source", "")) + " ｜ 数据缺口与弥补：" + str(ch.get("gap", "")), size=9)

    # 专项一 核心风险深度分析
    add_heading(doc, "专项一 核心风险深度分析", 1)
    for r in S.get("risks", []):
        tbl = doc.add_table(rows=1, cols=2)
        tbl.style = "Light Grid Accent 1"
        lv_hex = risk_color(r.get("level", ""))
        set_cell_text(tbl.cell(0, 0), r.get("name", ""), bold=True, color=RGBColor(0xFF, 0xFF, 0xFF), size=10)
        shade_cell(tbl.cell(0, 0), lv_hex)
        set_cell_text(tbl.cell(0, 1), "风险等级：" + str(r.get("level", "")), bold=True,
                      color=hex_rgb(lv_hex), size=10)
        shade_cell(tbl.cell(0, 1), "F1F5FB")
        add_para(doc, r.get("desc", ""), bold_prefix="现状：")
        add_para(doc, r.get("path", ""), bold_prefix="信贷传导路径：")
        add_para(doc, r.get("measures", ""), bold_prefix="全流程风控措施：")
        add_para(doc, "来源：" + str(r.get("source", "")), size=9)

    # 专项二 目标区域实操核查清单
    add_heading(doc, "专项二 目标区域实操核查清单", 1)
    ck = S.get("checklist", {})
    add_para(doc, "适用区域：" + str(ck.get("region", "江苏省")) + " ｜ " + str(ck.get("usage", "")), size=9)
    for cat in ck.get("categories", []):
        add_heading(doc, cat.get("name", ""), 2)
        for it in cat.get("items", []):
            doc.add_paragraph("• " + str(it), style="List Bullet")
    # 担保圈互保标准化排查（如存在）
    if ck.get("guarantee"):
        g = ck.get("guarantee", {})
        add_heading(doc, "担保圈/互保标准化排查", 2)
        add_para(doc, g.get("regionNote", ""), bold_prefix="适用区域特征：")
        for item in g.get("items", []):
            doc.add_paragraph("• " + str(item.get("name", "")) + "：" + str(item.get("content", "")),
                              style="List Bullet")

    # 专项三 单项目收益测算模板
    add_heading(doc, "专项三 单项目收益测算模板", 1)
    pc = S.get("projectCalc", {})
    if pc.get("applicable") is False:
        add_para(doc, pc.get("note", "本行业以企业整体授信为主，不适用单项目测算模板，原因：数据缺失-D"))
    else:
        add_para(doc, "适用场景：" + str(pc.get("scenario", "")) + " ｜ 假设：" + str(pc.get("assumption", "")), size=9)
        if pc.get("params"):
            add_grid_table(doc, ["参数", "单位", "基准示例值", "备注"],
                           [[x.get("name", ""), x.get("unit", ""), x.get("val", ""), x.get("note", "")]
                            for x in pc.get("params", [])])
        if pc.get("firstYear"):
            add_grid_table(doc, ["指标", "单位", "基准测算值", "计算逻辑"],
                           [[x.get("name", ""), x.get("unit", ""), x.get("val", ""), x.get("logic", "")]
                            for x in pc.get("firstYear", [])])
        if pc.get("metrics"):
            add_grid_table(doc, ["指标", "单位", "基准测算值", "信贷评价"],
                           [[x.get("name", ""), x.get("unit", ""), x.get("val", ""), x.get("eval", "")]
                            for x in pc.get("metrics", [])])
        if pc.get("stress"):
            add_grid_table(doc, ["压力场景", "核心指标变动", "风险判定"],
                           [[x.get("name", ""), x.get("change", ""), x.get("judge", "")]
                            for x in pc.get("stress", [])])
        th = pc.get("thresholds", {})
        if th:
            add_para(doc, "正常准入：" + str(th.get("normal", "")) + " ｜ 审慎介入：" +
                     str(th.get("caution", "")) + " ｜ 严禁准入：" + str(th.get("forbid", "")),
                     bold_prefix="信贷准入阈值：")
        add_para(doc, "数据来源：" + str(pc.get("source", "")), size=9)

    # 专项四 ESG与绿色信贷适配度
    add_heading(doc, "专项四 ESG与绿色信贷适配度", 1)
    esg = S.get("esg", {})
    env = esg.get("env", {})
    add_kv_table(doc, [("能耗与排放强度", env.get("intensity", "")), ("绿色工艺替代空间", env.get("substitution", "")),
                       ("碳足迹与碳壁垒风险", env.get("carbon", ""))])
    soc = esg.get("social", {})
    add_kv_table(doc, [("用工与安全生产", soc.get("labor", "")), ("供应链责任", soc.get("supply", ""))])
    gov = esg.get("gov", {})
    add_kv_table(doc, [("环保合规记录", gov.get("record", "")), ("信息披露质量", gov.get("disclosure", ""))])
    fit = esg.get("fit", {})
    add_kv_table(doc, [("绿色信贷适配评级", fit.get("rating", "")), ("重点支持方向", fit.get("support", "")),
                       ("信贷约束条款", fit.get("constraint", ""))])
    add_para(doc, "数据来源：" + str(esg.get("source", "")), size=9)

    # 综合评估
    add_heading(doc, "综合评估", 1)
    radar = A.get("radar", {})
    add_kv_table(doc, [("政策风险", radar.get("policy", "")), ("周期风险", radar.get("cycle", "")),
                       ("盈利风险", radar.get("profit", "")), ("供需风险", radar.get("supply", "")),
                       ("财务风险", radar.get("finance", "")), ("综合风险得分", radar.get("score", ""))])
    add_heading(doc, "核心风险点", 2)
    for r in A.get("topRisks", []):
        doc.add_paragraph("• " + str(r), style="List Bullet")
    add_heading(doc, "核心优势点", 2)
    for r in A.get("topStrengths", []):
        doc.add_paragraph("• " + str(r), style="List Bullet")
    st = A.get("strategy", {})
    add_kv_table(doc, [("总体策略", st.get("overall", "")), ("额度建议", st.get("quota", ""))])
    add_para(doc, st.get("measures", ""), bold_prefix="风控措施建议：")
    add_para(doc, st.get("focus", ""), bold_prefix="重点关注事项：")
    add_para(doc, A.get("compliance", "无"), bold_prefix="合规与制裁风险：")

    # 报告核心说明
    add_heading(doc, "报告核心说明", 1)
    add_para(doc, N.get("boundary", ""), bold_prefix="行业边界界定：")
    add_para(doc, N.get("logic", ""), bold_prefix="核心风险逻辑：")
    add_para(doc, N.get("differentiation", ""), bold_prefix="差异化策略：")

    # 免责声明
    add_heading(doc, "免责声明", 1)
    add_para(doc, data.get("disclaimer", ""), size=9)

    doc.save(out_path)
    print("已生成 Word 文档：" + out_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python generate_docx.py report_data.json [输出文件名.docx]")
        sys.exit(1)
    json_path = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "行业尽调报告.docx"
    with open(json_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    build(data, out)
