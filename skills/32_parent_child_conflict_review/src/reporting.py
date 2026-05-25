"""亲子冲突复盘 Agent - 报告生成器

增强版本：添加Markdown表格美化、可视化、摘要生成、多格式导出支持
"""
from __future__ import annotations
from typing import Any, Dict, List, Union
from datetime import datetime
from collections import defaultdict
import json


def render_report(result: Dict[str, Any]) -> str:
    """渲染完整报告"""
    lines: List[str] = []
    lines.append("# 🔄 亲子冲突复盘报告")
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

    if result.get("conflict_analysis"):
        lines.append("## D. 冲突分析详情")
        lines.append("")
        lines.extend(render_conflict_analysis(result.get("conflict_analysis", [])))
        lines.append("")

    if result.get("resolution_plans"):
        lines.append("## E. 解决方案")
        lines.append("")
        lines.extend(render_resolution_plans(result.get("resolution_plans", [])))
        lines.append("")

    if result.get("trend_analysis"):
        lines.append("## F. 趋势分析")
        lines.append("")
        lines.extend(render_trend_analysis(result.get("trend_analysis", {})))
        lines.append("")

    if result.get("communication_tips"):
        lines.append("## G. 沟通建议")
        lines.append("")
        for tip in result.get("communication_tips", []):
            lines.append(f"- {tip}")
        lines.append("")

    lines.append("## H. 执行方案")
    for item in result.get("action_plan", []):
        lines.append(f"- [{item.get('day', '')}] {item.get('task', '')}")
    lines.append("")

    lines.append("## I. 风险与注意事项")
    for x in result.get("risk_notes", []):
        lines.append(f"- {x}")
    lines.append("")

    lines.append("## J. 下次追踪字段")
    for x in result.get("next_tracking_fields", []):
        lines.append(f"- {x}")
    lines.append("")

    return "\n".join(lines)


def render_conflict_analysis(analyses: List[Dict[str, Any]]) -> List[str]:
    """渲染冲突分析"""
    lines = []

    for i, analysis in enumerate(analyses, 1):
        lines.append(f"### 冲突 {i}")
        lines.append(f"**根本原因**: {analysis.get('root_cause', '待分析')}")
        lines.append(f"**检测到的模式**: {analysis.get('pattern_detected', '待观察')}")
        lines.append("")

        if analysis.get("parent_contributing_factors"):
            lines.append("**家长因素**:")
            for factor in analysis["parent_contributing_factors"]:
                lines.append(f"  - {factor}")
            lines.append("")

        if analysis.get("child_contributing_factors"):
            lines.append("**孩子因素**:")
            for factor in analysis["child_contributing_factors"]:
                lines.append(f"  - {factor}")
            lines.append("")

        if analysis.get("effective_strategies"):
            lines.append("**有效策略**:")
            for strategy in analysis["effective_strategies"]:
                lines.append(f"  - {strategy}")
            lines.append("")

        if analysis.get("recommended_approach"):
            lines.append(f"**建议方法**: {analysis['recommended_approach']}")
            lines.append("")

    return lines


def render_resolution_plans(plans: List[Dict[str, Any]]) -> List[str]:
    """渲染解决方案"""
    lines = []

    for i, plan in enumerate(plans, 1):
        lines.append(f"### 方案 {i}")

        if plan.get("immediate_actions"):
            lines.append("**立即行动**:")
            for action in plan["immediate_actions"]:
                lines.append(f"  - {action}")
            lines.append("")

        if plan.get("short_term_strategies"):
            lines.append("**短期策略**:")
            for strategy in plan["short_term_strategies"]:
                lines.append(f"  - {strategy}")
            lines.append("")

        if plan.get("long_term_prevention"):
            lines.append("**长期预防**:")
            for prevention in plan["long_term_prevention"]:
                lines.append(f"  - {prevention}")
            lines.append("")

        if plan.get("communication_phrase_suggestions"):
            lines.append("**建议话术**:")
            for phrase in plan["communication_phrase_suggestions"]:
                lines.append(f"  - \"{phrase}\"")
            lines.append("")

    return lines


def render_trend_analysis(analysis: Dict[str, Any]) -> List[str]:
    """渲染趋势分析"""
    lines = []

    lines.append(f"**冲突频率趋势**: {analysis.get('frequency_trend', 'stable')}")
    lines.append(f"**平均严重程度**: {analysis.get('average_severity', 'N/A')}")
    lines.append(f"**解决质量平均分**: {analysis.get('average_resolution_quality', 'N/A')}")
    lines.append("")

    if analysis.get("common_triggers"):
        lines.append("**常见触发点**:")
        for trigger in analysis["common_triggers"]:
            lines.append(f"  - {trigger}")
        lines.append("")

    if analysis.get("improvement_areas"):
        lines.append("**需要改进的方面**:")
        for area in analysis["improvement_areas"]:
            lines.append(f"  - {area}")
        lines.append("")

    return lines


def generate_summary_text(result: Dict[str, Any]) -> str:
    """生成摘要文本"""
    lines = []

    summary = result.get("summary", [])
    if summary:
        lines.append("📋 核心结论:")
        for point in summary[:3]:
            lines.append(f"  • {point}")
        lines.append("")

    trend = result.get("trend_analysis", {})
    if trend:
        lines.append("📈 趋势洞察:")
        lines.append(f"  • 冲突频率: {trend.get('frequency_trend', 'unknown')}")
        lines.append("")

    return "\n".join(lines)


def export_to_json(result: Dict[str, Any], indent: int = 2) -> str:
    """导出为JSON格式"""
    return json.dumps(result, ensure_ascii=False, indent=indent, default=str)


def export_to_html(result: Dict[str, Any]) -> str:
    """导出为HTML格式"""
    lines = []
    lines.append("<!DOCTYPE html>")
    lines.append("<html lang='zh-CN'>")
    lines.append("<head>")
    lines.append("    <meta charset='UTF-8'>")
    lines.append("    <title>亲子冲突复盘报告</title>")
    lines.append("    <style>")
    lines.append("        body { font-family: 'Microsoft YaHei', Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }")
    lines.append("        h1 { color: #2c3e50; border-bottom: 3px solid #e74c3c; padding-bottom: 10px; }")
    lines.append("        .conflict { background-color: #fdf2f2; padding: 15px; margin: 10px 0; border-left: 4px solid #e74c3c; }")
    lines.append("        .plan { background-color: #f0f9ff; padding: 15px; margin: 10px 0; border-left: 4px solid #3498db; }")
    lines.append("    </style>")
    lines.append("</head>")
    lines.append("<body>")
    lines.append("    <h1>🔄 亲子冲突复盘报告</h1>")

    if result.get("summary"):
        lines.append("    <h2>📋 核心结论</h2>")
        lines.append("    <ul>")
        for item in result.get("summary", []):
            lines.append(f"        <li>{item}</li>")
        lines.append("    </ul>")

    if result.get("conflict_analysis"):
        lines.append("    <h2>📊 冲突分析</h2>")
        for analysis in result.get("conflict_analysis", []):
            lines.append(f"    <div class='conflict'>")
            lines.append(f"        <strong>根本原因:</strong> {analysis.get('root_cause', 'N/A')}")
            lines.append("    </div>")

    lines.append("</body>")
    lines.append("</html>")
    return "\n".join(lines)


def format_markdown_table(headers: List[str], rows: List[List[Any]]) -> List[str]:
    """格式化Markdown表格"""
    lines = []
    header_line = "| " + " | ".join(str(h) for h in headers) + " |"
    separator = "|" + "|".join("---" for _ in headers) + "|"
    lines.append(header_line)
    lines.append(separator)
    for row in rows:
        row_line = "| " + " | ".join(str(cell) for cell in row) + " |"
        lines.append(row_line)
    return lines
