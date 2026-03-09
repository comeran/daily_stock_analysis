# -*- coding: utf-8 -*-
"""
Tests for the dedicated HTML email dashboard renderer.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.notification_sender.email_renderer import render_email_dashboard


SAMPLE_DASHBOARD_MARKDOWN = """# 🎯 2026-03-09 决策仪表盘

> 共分析 **2** 只股票 | 🟢买入:1 🟡观望:1 🔴卖出:0

## 📊 分析结果摘要

🟢 **宁德时代(300750)**: 买入 | 评分 88 | 趋势向上
🟡 **贵州茅台(600519)**: 持有 | 评分 61 | 高位震荡

---

## 🟢 宁德时代 (300750)

### 📌 核心结论

**🟢 买入** | 趋势向上

> **一句话决策**: 回踩 MA5 附近可分批布局。
"""

MARKET_REVIEW_MARKDOWN = """# 📈 市场复盘

今日市场延续震荡修复，量能温和放大。

## 核心观察

- 北向资金回流
- 科技成长相对强势
"""


def test_render_email_dashboard_extracts_summary_table():
    html = render_email_dashboard(SAMPLE_DASHBOARD_MARKDOWN)

    assert "股票总结" in html
    assert "宁德时代" in html
    assert "300750" in html
    assert "回踩 MA5 附近可分批布局" in html


def test_render_email_dashboard_without_stock_rows_preserves_body():
    html = render_email_dashboard(MARKET_REVIEW_MARKDOWN)

    assert "市场复盘" in html
    assert "量能温和放大" in html
    assert "股票总结" not in html
