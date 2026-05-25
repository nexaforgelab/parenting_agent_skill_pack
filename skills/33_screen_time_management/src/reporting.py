"""手机使用管理 Agent - 报告生成器"""
from __future__ import annotations
from typing import Any, Dict, List
from datetime import datetime
import json


def render_report(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# 📱 手机使用管理报告")
    lines.append("")
    lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    lines.append("## A. 本次结论")
    for x in result.get("summary", []):
        lines.append(f"- {x}")
    lines.append("")

    lines.append("## B. 已知信息")
    for x in result.get("known_facts", []):
        lines.append(f"- {x}")
    lines.append("")

    lines.append("## C. 分析与判断")
    for x in result.get("analysis", []):
        lines.append(f"{x}")
    lines.append("")

    if result.get("screen_time_analysis"):
        lines.append("## D. 屏幕时间分析")
        lines.append("")
        lines.extend(render_screen_time_analysis(result.get("screen_time_analysis", {})))
        lines.append("")

    if result.get("recommendations"):
        lines.append("## E. 建议措施")
        lines.append("")
        for rec in result.get("recommendations", []):
            lines.append(f"- {rec}")
        lines.append("")

    lines.append("## F. 执行方案")
    for item in result.get("action_plan", []):
        lines.append(f"- [{item.get('day', '')}] {item.get('task', '')}")
    lines.append("")

    lines.append("## G. 风险与注意事项")
    for x in result.get("risk_notes", []):
        lines.append(f"- {x}")
    lines.append("")

    lines.append("## H. 下次追踪字段")
    for x in result.get("next_tracking_fields", []):
        lines.append(f"- {x}")
    lines.append("")

    return "\n".join(lines)


def render_screen_time_analysis(analysis: Dict[str, Any]) -> List[str]:
    lines = []

    lines.append(f"**日均屏幕时间**: {analysis.get('daily_average_minutes', 0)} 分钟")
    lines.append(f"**周总屏幕时间**: {analysis.get('weekly_total_minutes', 0)} 分钟")
    lines.append(f"**推荐上限**: {analysis.get('recommended_limit', 60)} 分钟")
    lines.append("")

    distribution = analysis.get("activity_distribution", {})
    if distribution:
        lines.append("**活动类型分布**:")
        for activity, minutes in distribution.items():
            lines.append(f"  - {activity}: {minutes} 分钟")
        lines.append("")

    return lines


def export_to_json(result: Dict[str, Any], indent: int = 2) -> str:
    return json.dumps(result, ensure_ascii=False, indent=indent, default=str)


def export_to_html(result: Dict[str, Any]) -> str:
    lines = []
    lines.append("<!DOCTYPE html>")
    lines.append("<html lang='zh-CN'>")
    lines.append("<head>")
    lines.append("    <meta charset='UTF-8'>")
    lines.append("    <title>手机使用管理报告</title>")
    lines.append("</head>")
    lines.append("<body>")
    lines.append("    <h1>📱 手机使用管理报告</h1>")
    lines.append("</body>")
    lines.append("</html>")
    return "\n".join(lines)


def format_markdown_table(headers: List[str], rows: List[List[Any]]) -> List[str]:
    lines = []
    header_line = "| " + " | ".join(str(h) for h in headers) + " |"
    separator = "|" + "|".join("---" for _ in headers) + "|"
    lines.append(header_line)
    lines.append(separator)
    for row in rows:
        row_line = "| " + " | ".join(str(cell) for cell in row) + " |"
        lines.append(row_line)
    return lines
