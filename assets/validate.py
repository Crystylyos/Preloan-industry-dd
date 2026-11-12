#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
preloan-industry-dd · 交付前 HTML 静态校验器（V5.3.0 新增）
借鉴 research-report-builder 的「交付前必过校验」原则，但仅做静态检查，
绝不执行页面 JS（避免 eval 外部内容的安全风险）。

检查项：
  1. 零外部依赖：无 <script src=>、<link href=http、@import、url(http)、cdn、chart.js 等
  2. 脚本完整性：<script 开合标签配平，REPORT_DATA 区域无 </script> 跳出
  3. 数据块存在：const REPORT_DATA = 存在
  4. 字段级（尽力）：若 REPORT_DATA 可解析为严格 JSON，校验必备顶层键

用法：
    python validate.py <报告.html>
退出码：0 通过 / 1 发现问题 / 2 用法或读取错误
"""
import sys
import re
import json

REQUIRED_TOP = ["header", "dimensions", "special", "assessment", "notes", "disclaimer"]

# 专项三「盈亏测算模板」四张表的完备性门槛
PC_MIN = {"params": 8, "firstYear": 4, "metrics": 4, "stress": 4}


def _as_list(x):
    return x if isinstance(x, list) else []


def check_project_calc(data):
    """专项三一致性校验。

    完整版的定义是「含企业财务对标与单项目测算」（见 SKILL.md 步骤一「输出模式」），
    因此完整版下专项三必须可渲染。applicable=false 会把整章压成一句「不适用说明」，
    属数据缺陷，必须阻断交付而不是静默放过——旧模板只认该字段，一旦模型误填，
    整章测算数据全部丢失且页面看不出异常。
    """
    out = []
    special = data.get("special") if isinstance(data.get("special"), dict) else {}
    pc = special.get("projectCalc") if isinstance(special.get("projectCalc"), dict) else {}
    if not pc:
        return ["专项三缺失：special.projectCalc 不存在，完整版须输出盈亏测算模板"]

    flag = pc.get("applicable")
    counts = {k: len(_as_list(pc.get(k))) for k in PC_MIN}
    has_data = any(counts.values())
    off = flag is False or flag == "false" or flag == 0 or flag == "0"
    on = flag is True or flag == "true" or flag == 1 or flag == "1"

    header = data.get("header") if isinstance(data.get("header"), dict) else {}
    mode = str(header.get("outputMode") or "完整版")
    is_full = "轻量" not in mode
    company = data.get("company") if isinstance(data.get("company"), dict) else {}
    n_company = len(_as_list(company.get("items")))

    if not (off or on):
        out.append("专项三 applicable 非布尔值（实际 %r）：须显式写 true 或 false" % (flag,))

    if is_full and off:
        if has_data:
            out.append(
                "专项三 applicable=false 但已产出测算数据（%s）：标记与数据矛盾，"
                "整章会被误判为不适用，须改为 true" %
                "、".join("%s %d 项" % (k, counts[k]) for k in PC_MIN if counts[k]))
        else:
            extra = "，且已提供企业财务数据 %d 项" % n_company if n_company else ""
            out.append(
                "专项三 applicable=false 且无测算数据%s：完整版须输出盈亏测算模板"
                "（若确属非项目制行业，请改走轻量速览版，或补充企业整体授信口径的测算）" % extra)

    if on:
        short = ["%s %d<%d" % (k, counts[k], PC_MIN[k]) for k in PC_MIN if counts[k] < PC_MIN[k]]
        if short:
            out.append(
                "专项三 applicable=true 但测算数据不足门槛：%s"
                "（门槛 params>=8 / firstYear>=4 / metrics>=4 / stress>=4）" % "、".join(short))

    return out


def extract_report_data(html):
    """尽力提取 const REPORT_DATA = {...} 的对象文本（括号配平，忽略字符串内括号）。"""
    idx = html.find("const REPORT_DATA")
    if idx < 0:
        return None
    start = html.find("{", idx)
    if start < 0:
        return None
    depth = 0
    in_str = False
    quote = ""
    for j in range(start, len(html)):
        c = html[j]
        if in_str:
            if c == "\\":
                continue
            if c == quote:
                in_str = False
            continue
        if c in ("\"", "'"):
            in_str = True
            quote = c
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return html[start:j + 1]
    return None


def main():
    if len(sys.argv) < 2:
        print("用法：python validate.py <报告.html>")
        return 2
    path = sys.argv[1]
    try:
        with open(path, "r", encoding="utf-8") as fh:
            html = fh.read()
    except Exception as e:
        print("读取失败：" + str(e))
        return 2

    problems = []
    warnings = []

    # 1. 零外部依赖
    ext_patterns = [
        (r'<script[^>]+\bsrc=', "<script src= 外部脚本"),
        (r'<link\b[^>]*\bhref=', "<link href= 外部样式/字体"),
        (r'@import', "@import 外部样式"),
        (r'url\(\s*https?://', "url(http) 外部资源"),
        (r'cdn\.', "cdn 外部依赖"),
        (r'chart\.js', "chart.js 外部库"),
    ]
    for pat, desc in ext_patterns:
        if re.search(pat, html, re.IGNORECASE):
            problems.append("外部依赖：" + desc)

    # 2. 脚本配平
    opens = len(re.findall(r'<script', html, re.IGNORECASE))
    closes = len(re.findall(r'</script', html, re.IGNORECASE))
    if opens != closes:
        problems.append("脚本标签不配平：<script> %d 个 / </script> %d 个" % (opens, closes))

    # 3. 数据块存在
    blob = extract_report_data(html)
    if blob is None:
        if "const REPORT_DATA" not in html:
            problems.append("未找到 const REPORT_DATA 数据块")
        else:
            warnings.append("未能提取 REPORT_DATA 对象边界，跳过字段级校验")

    # 4. 字段级（尽力）
    if blob is not None:
        try:
            data = json.loads(blob)
            missing = [k for k in REQUIRED_TOP if k not in data]
            if missing:
                warnings.append("REPORT_DATA 缺顶层键：" + ", ".join(missing) +
                                "（请核对字段级契约 references/data_contract.md）")
            problems.extend(check_project_calc(data))
        except Exception:
            warnings.append("REPORT_DATA 为非严格 JSON（JS 对象字面量），跳过字段级校验；"
                            "请用浏览器打开模板页脚『校验数据』功能做字段核对")

    if problems:
        print("✗ 校验未通过（%d 项问题）：" % len(problems))
        for p in problems:
            print("  - " + p)
    if warnings:
        print("⚠ 提示（%d 项）：" % len(warnings))
        for w in warnings:
            print("  - " + w)

    if not problems and not warnings:
        print("✓ 校验通过：零外部依赖、脚本完整、数据块存在")
        return 0
    if not problems:
        print("✓ 结构通过（仅提示项，不影响交付）")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
