"""中考目标拆解 Agent - 报告生成器"""
from __future__ import annotations
from typing import Any, Dict, List
from datetime import datetime
import json


def render_report(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# 🎯 中考目标拆解报告")
    lines.append("")
    lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    lines.append("## A. 本次结论")
    for x in result.get("summary", []):
        lines.append(f"- {x}")
    lines.append("")

    lines.append("## B. 目标概况")
    for x in result.get("known_facts", []):
        lines.append(f"- {x}")
    lines.append("")

    lines.append("## C. 分析与判断")
    for x in result.get("analysis", []):
        lines.append(f"{x}")
    lines.append("")

    if result.get("goal_breakdown"):
        lines.append("## D. 目标拆解")
        lines.append("")
        lines.extend(render_goal_breakdown(result.get("goal_breakdown", {})))
        lines.append("")

    if result.get("study_plan"):
        lines.append("## E. 学习计划")
        lines.append("")
        lines.extend(render_study_plan(result.get("study_plan", [])))
        lines.append("")

    if result.get("recommendations"):
        lines.append("## F. 建议措施")
        lines.append("")
        for rec in result.get("recommendations", []):
            lines.append(f"- {rec}")
        lines.append("")

    lines.append("## G. 执行方案")
    for item in result.get("action_plan", []):
        lines.append(f"- [{item.get('day', '')}] {item.get('task', '')}")
    lines.append("")

    lines.append("## H. 风险与注意事项")
    for x in result.get("risk_notes", []):
        lines.append(f"- {x}")
    lines.append("")

    return "\n".join(lines)


def render_goal_breakdown(breakdown: Dict[str, Any]) -> List[str]:
    lines = []
    lines.append(f"**目标总分**: {breakdown.get('target_total_score', 0)}")
    lines.append(f"**目标学校**: {breakdown.get('target_school', '待定')}")
    lines.append("")

    subjects = breakdown.get("subject_goals", [])
    if subjects:
        header = "| 学科 | 当前成绩 | 目标成绩 | 差距 | 提升空间 |"
        separator = "|------|---------|---------|------|----------|"
        lines.append(header)
        lines.append(separator)
        for s in subjects:
            lines.append(f"| {s.get('subject', '')} | {s.get('current', 0)} | {s.get('target', 0)} | {s.get('gap', 0)} | {s.get('improvement', '')} |")
        lines.append("")

    return lines


def render_study_plan(plans: List[Dict[str, Any]]) -> List[str]:
    lines = []
    for plan in plans:
        lines.append(f"### {plan.get('subject', '')}")
        lines.append(f"**重点**: {plan.get('target_topic', '')}")
        lines.append(f"**每周时间**: {plan.get('weekly_hours', 0)}小时")
        lines.append("")
    return lines


def export_to_json(result: Dict[str, Any], indent: int = 2) -> str:
    return json.dumps(result, ensure_ascii=False, indent=indent, default=str)


def export_to_html(result: Dict[str, Any]) -> str:
    lines = []
    lines.append("<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'><title>中考目标拆解报告</title></head><body><h1>🎯 中考目标拆解报告</h1></body></html>")
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
