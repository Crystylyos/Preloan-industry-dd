#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""preloan-industry-dd · 开箱自检（v5.4.2 新增）

把 examples/ 下的样例注入模板，做「结构 + 契约 + 色阶」三层检查，
用于交付前的快速返检。判据与 assets/validate.py 同源，不另立标准。

用法：
    python assets/selftest.py              # 离线检查（默认，秒级）
    python assets/selftest.py --browser    # 追加无头浏览器渲染核验
    python assets/selftest.py --list       # 仅列出自检项，不执行

退出码：0 全通过 / 1 存在问题
"""
import argparse
import ast
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TPL = HERE / "report_template.html"
EXAMPLES = ROOT / "examples"
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True   # 不生成 __pycache__，避免污染发布包

import validate  # noqa: E402  复用同一套判据

EXPECT_CARDS = 15
PH = "__REPORT_DATA__"
RESULTS = []


def chk(name, ok, detail=""):
    RESULTS.append((name, ok))
    tail = ("  → " + detail) if (detail and not ok) else ""
    print("  %-38s %s%s" % (name, "OK" if ok else "FAIL", tail))
    return ok


def find_browser():
    for c in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              "/usr/bin/google-chrome", "/usr/bin/chromium"):
        if Path(c).exists():
            return c
    return None


def render(html, tag):
    exe = find_browser()
    if not exe:
        return None
    out = Path(tempfile.mkdtemp(prefix="selftest-")) / (tag + ".html")
    out.write_text(html, encoding="utf-8")
    prof = tempfile.mkdtemp(prefix="selftest-prof-")
    r = subprocess.run([exe, "--headless", "--disable-gpu", "--no-first-run",
                        "--user-data-dir=" + prof, "--virtual-time-budget=4000",
                        "--dump-dom", out.as_uri()], capture_output=True)
    return r.stdout.decode("utf-8", "replace")


def check_template(tpl):
    print("\n== 模板结构 ==")
    chk("占位符唯一（%s）" % PH, tpl.count(PH) == 1, "实际 %d 个" % tpl.count(PH))
    n = len(re.findall(r'card\("sec-\d+"', tpl))
    chk("章节数 = %d" % EXPECT_CARDS, n == EXPECT_CARDS, "实际 %d" % n)
    for kw, label in [("@media print", "打印样式"),
                      ('html[data-theme="dark"]', "暗色主题"),
                      ("prefers-reduced-motion", "减弱动效"),
                      ("buildBreakeven", "盈亏平衡图"),
                      ("semanticTone", "信贷语义色阶"),
                      ("Microsoft YaHei", "微软雅黑")]:
        chk("含%s" % label, kw in tpl)


def check_example(path, tpl, browser):
    print("\n== 样例 %s ==" % path.name)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        chk("JSON 可解析", False, str(e))
        return
    chk("JSON 可解析", True)

    miss = [k for k in validate.REQUIRED_TOP if k not in data]
    chk("必备顶层键齐全", not miss, "缺 " + "、".join(miss))

    html = tpl.replace(PH, json.dumps(data, ensure_ascii=False))
    chk("注入后无残留占位符", PH not in html)

    probs = validate.check_html_structure(html)
    chk("零外部依赖 / 脚本配平", not probs, "; ".join(probs))

    chk("数据块可提取", validate.extract_report_data(html) is not None)

    pcs = validate.check_project_calc(data)
    chk("专项三契约", not pcs, "; ".join(pcs))

    if browser:
        dom = render(html, path.stem)
        if dom is None:
            chk("浏览器渲染", False, "未找到 Edge/Chrome")
        else:
            stripped = re.sub(r"<script[\s\S]*?</script>", "", dom, flags=re.I)
            bad = re.findall(r"\bundefined\b|\bNaN\b", stripped)
            chk("渲染无 undefined / NaN", not bad, "残留 %d 处" % len(bad))
            chk("渲染含专项三章节", 'id="sec-10"' in dom)


def check_color(tpl):
    print("\n== 交付物色阶一致性 ==")
    css = {k: v.upper().lstrip("#") for k, v in
           re.findall(r"--risk-(high|midhigh|mid|low):(#[0-9A-Fa-f]{6})", tpl)}
    docx = HERE / "generate_docx.py"
    if not docx.exists():
        chk("Word 生成脚本存在", False)
        return
    src = docx.read_text(encoding="utf-8")
    consts = {"RISK_HIGH", "RISK_MIDHIGH", "RISK_MID", "RISK_LOW", "RISK_UNKNOWN"}
    keep = []
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") in consts for t in node.targets):
            keep.append(node)
        if isinstance(node, ast.FunctionDef) and node.name == "risk_color":
            keep.append(node)
    ns = {}
    exec(compile(ast.Module(body=keep, type_ignores=[]), "<docx>", "exec"), ns)
    rc = ns["risk_color"]
    pairs = [("高风险", "high"), ("中高风险", "midhigh"), ("中风险", "mid"), ("低风险", "low")]
    bad = [lab for lab, key in pairs if rc(lab).upper() != css.get(key)]
    chk("Word 与 HTML 风险色逐值同源", not bad, "不一致：" + "、".join(bad))
    chk("四档互不重复", len({rc(lab) for lab, _ in pairs}) == 4)


def main():
    ap = argparse.ArgumentParser(description="preloan-industry-dd 开箱自检")
    ap.add_argument("--browser", action="store_true", help="追加无头浏览器渲染核验")
    args = ap.parse_args()

    if not TPL.exists():
        print("✗ 未找到模板：%s" % TPL)
        return 1
    tpl = TPL.read_text(encoding="utf-8")

    print("preloan-industry-dd 自检 · 模板 %s" % TPL.name)
    check_template(tpl)

    files = sorted(EXAMPLES.glob("report_data*.json")) if EXAMPLES.exists() else []
    if not files:
        print("\n== 样例 ==")
        chk("examples 下有可用样例", False, "未找到 report_data*.json")
    for f in files:
        check_example(f, tpl, args.browser)

    check_color(tpl)

    total = len(RESULTS)
    failed = [n for n, ok in RESULTS if not ok]
    print("\n" + "-" * 56)
    if failed:
        print("✗ 自检未通过：%d/%d 项失败" % (len(failed), total))
        for n in failed:
            print("  - " + n)
        return 1
    print("✓ 自检通过：%d/%d 项" % (total, total))
    if not args.browser:
        print("  提示：加 --browser 可追加真实渲染核验（需本机 Edge/Chrome）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
