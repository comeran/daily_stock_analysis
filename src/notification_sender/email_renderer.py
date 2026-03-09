# -*- coding: utf-8 -*-
"""
Dedicated HTML renderer for normal email notifications.
"""
from __future__ import annotations

from dataclasses import dataclass
from html import escape
import re
from typing import List, Optional

import markdown2


_TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
_SUMMARY_RE = re.compile(
    r"共分析\s*\*{0,2}(?P<total>\d+)\*{0,2}\s*只股票\s*\|\s*"
    r"🟢买入:(?P<buy>\d+)\s*🟡(?:观望|持有):(?P<hold>\d+)\s*🔴卖出:(?P<sell>\d+)"
)
_SUMMARY_ROW_RE = re.compile(
    r"^[^\n]*\*\*(?P<name>.+?)\((?P<code>\d{6})\)\*\*:\s*"
    r"(?P<advice>[^|]+?)\s*\|\s*评分\s*(?P<score>\d+)\s*\|\s*(?P<trend>.+)$",
    re.MULTILINE,
)


@dataclass
class DashboardStats:
    total: int
    buy: int
    hold: int
    sell: int


@dataclass
class StockSummaryRow:
    name: str
    code: str
    advice: str
    score: str
    trend: str


def _extract_title(markdown_text: str) -> str:
    match = _TITLE_RE.search(markdown_text)
    return match.group(1).strip() if match else "股票分析报告"


def _extract_report_date(title: str) -> str:
    match = _DATE_RE.search(title)
    return match.group(1) if match else ""


def _extract_stats(markdown_text: str) -> Optional[DashboardStats]:
    match = _SUMMARY_RE.search(markdown_text)
    if not match:
        return None
    return DashboardStats(
        total=int(match.group("total")),
        buy=int(match.group("buy")),
        hold=int(match.group("hold")),
        sell=int(match.group("sell")),
    )


def _extract_summary_rows(markdown_text: str) -> List[StockSummaryRow]:
    rows: List[StockSummaryRow] = []
    for match in _SUMMARY_ROW_RE.finditer(markdown_text):
        rows.append(
            StockSummaryRow(
                name=match.group("name").strip(),
                code=match.group("code").strip(),
                advice=match.group("advice").strip(),
                score=match.group("score").strip(),
                trend=match.group("trend").strip(),
            )
        )
    return rows


def _render_stats(stats: Optional[DashboardStats]) -> str:
    if not stats:
        return ""

    metrics = (
        ("分析股票", str(stats.total)),
        ("买入", str(stats.buy)),
        ("观望", str(stats.hold)),
        ("卖出", str(stats.sell)),
    )
    cards = "".join(
        f"""
        <div class="metric-card">
            <div class="metric-label">{escape(label)}</div>
            <div class="metric-value">{escape(value)}</div>
        </div>
        """
        for label, value in metrics
    )
    return f'<div class="metrics">{cards}</div>'


def _render_summary_table(rows: List[StockSummaryRow]) -> str:
    if not rows:
        return ""

    body_rows = "".join(
        f"""
        <tr>
            <td>{escape(row.name)}</td>
            <td>{escape(row.code)}</td>
            <td>{escape(row.score)}</td>
            <td>{escape(row.trend)}</td>
            <td>{escape(row.advice)}</td>
        </tr>
        """
        for row in rows
    )
    return f"""
    <section class="summary-card">
        <h2>股票总结</h2>
        <table>
            <thead>
                <tr>
                    <th>股票</th>
                    <th>代码</th>
                    <th>评分</th>
                    <th>趋势</th>
                    <th>建议</th>
                </tr>
            </thead>
            <tbody>
                {body_rows}
            </tbody>
        </table>
    </section>
    """


def render_email_dashboard(markdown_text: str) -> str:
    """
    Render a dashboard-style HTML document for normal email delivery.
    """
    title = _extract_title(markdown_text)
    report_date = _extract_report_date(title)
    stats = _extract_stats(markdown_text)
    rows = _extract_summary_rows(markdown_text)
    body_html = markdown2.markdown(
        markdown_text,
        extras=["tables", "fenced-code-blocks", "break-on-newline", "cuddled-lists"],
    )

    stats_html = _render_stats(stats)
    summary_table_html = _render_summary_table(rows)
    date_html = f'<p class="hero-subtitle">{escape(report_date)}</p>' if report_date else ""

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0;
                padding: 24px;
                background: #eef2f7;
                color: #162033;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            }}
            .email-shell {{
                max-width: 920px;
                margin: 0 auto;
            }}
            .hero {{
                padding: 28px 32px;
                border-radius: 24px;
                background: linear-gradient(135deg, #0f172a, #1d4ed8);
                color: #f8fafc;
                box-shadow: 0 18px 40px rgba(15, 23, 42, 0.18);
            }}
            .hero h1 {{
                margin: 0;
                font-size: 28px;
                line-height: 1.2;
            }}
            .hero-subtitle {{
                margin: 10px 0 0;
                font-size: 14px;
                color: rgba(248, 250, 252, 0.82);
            }}
            .metrics {{
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 12px;
                margin: 18px 0 0;
            }}
            .metric-card,
            .summary-card,
            .body-card {{
                background: #ffffff;
                border-radius: 20px;
                box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
            }}
            .metric-card {{
                padding: 18px 20px;
            }}
            .metric-label {{
                font-size: 13px;
                color: #64748b;
            }}
            .metric-value {{
                margin-top: 6px;
                font-size: 24px;
                font-weight: 700;
                color: #0f172a;
            }}
            .summary-card,
            .body-card {{
                margin-top: 20px;
                padding: 24px 28px;
            }}
            h2 {{
                margin: 0 0 16px;
                font-size: 20px;
                color: #0f172a;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 14px;
            }}
            th,
            td {{
                padding: 12px 14px;
                border-bottom: 1px solid #e2e8f0;
                text-align: left;
            }}
            th {{
                color: #475569;
                font-size: 12px;
                letter-spacing: 0.04em;
                text-transform: uppercase;
            }}
            .body-card h1,
            .body-card h2,
            .body-card h3 {{
                color: #0f172a;
            }}
            .body-card p,
            .body-card li,
            .body-card blockquote {{
                color: #334155;
                line-height: 1.7;
            }}
            .body-card blockquote {{
                margin: 12px 0;
                padding: 12px 16px;
                border-left: 4px solid #2563eb;
                background: #eff6ff;
                border-radius: 12px;
            }}
            .body-card hr {{
                border: 0;
                border-top: 1px solid #e2e8f0;
                margin: 24px 0;
            }}
        </style>
    </head>
    <body>
        <div class="email-shell">
            <section class="hero">
                <h1>{escape(title)}</h1>
                {date_html}
            </section>
            {stats_html}
            {summary_table_html}
            <section class="body-card">
                {body_html}
            </section>
        </div>
    </body>
    </html>
    """
