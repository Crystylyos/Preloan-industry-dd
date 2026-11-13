#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
preloan-industry-dd · 环境就绪检查
只读检查，不联网、不读取凭据、不修改配置。
输出：ready / needs_setup（始终返回 0，仅展示；needs_setup 不阻断核心流程）
"""
import sys
import importlib


def main():
    status = "ready"
    notes = []

    # 必需：python-docx（Word 生成）
    try:
        importlib.import_module("docx")
        notes.append("python-docx：已安装（Word 生成可用）")
    except Exception:
        status = "needs_setup"
        notes.append("python-docx：未安装 -> 运行 pip install python-docx（或交内置 Python 环境满足）；"
                     "缺失时仅能交付 HTML/XML/Markdown，跳过 Word")

    # 可选：金融/工商 MCP 连接器（手动在 WorkBuddy 连接器管理确认）
    optional = ["Wind", "同花顺妙想(mx-ds-mcp)", "企查查(qcc-company)", "北大法宝/法研(PKULaw)"]
    notes.append("可选 MCP：" + "、".join(optional) +
                 " —— 未连接时自动回落网页检索，不影响核心流程；请在 WorkBuddy 连接器管理确认是否已启用")

    print("环境状态：" + status)
    for n in notes:
        print("  - " + n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
