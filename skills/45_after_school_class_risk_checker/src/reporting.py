"""Markdown report renderer for 课外班避坑 Agent.

增强版本：添加图表生成、Markdown表格美化、趋势可视化、摘要生成、导出格式支持
"""
from typing import Any, Dict, List
from datetime import datetime


def render_report(result: Dict[str, Any]) -> str:
    """渲染完整报告"""
    lines: List[str] = []
    lines.append("# 课外班避坑报告")
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
        lines.append(f"- {x}")
    lines.append("")

    lines.append("## D. 执行方案")
    for item in result.get("action_plan", []):
        lines.append(f"- {item.get('day')}：{item.get('task')}｜负责人：{item.get('owner')}｜记录：{item.get('evidence_to_record')}")
    lines.append("")

    if result.get("risk_assessments"):
        lines.append("## E. 风险评估")
        lines.append("")
        lines.extend(render_risk_assessment_table(result.get("risk_assessments", [])))
        lines.append("")

    if result.get("alerts"):
        lines.append("## F. 套路检测")
        lines.append("")
        lines.extend(render_alerts_list(result.get("alerts", [])))
        lines.append("")

    if result.get("recommendations"):
        lines.append("## G. 避坑建议")
        lines.append("")
        lines.extend(render_recommendations_list(result.get("recommendations", [])))
        lines.append("")

    lines.append("## H. 风险与人工核验")
    for x in result.get("risk_notes", []):
        lines.append(f"- {x}")
    lines.append("")

    lines.append("## I. 下次追踪字段")
    for x in result.get("next_tracking_fields", []):
        lines.append(f"- {x}")
    lines.append("")

    return "\n".join(lines)


def render_risk_assessment_table(assessments: List[Dict[str, Any]]) -> List[str]:
    """渲染风险评估表格"""
    lines = []

    if not assessments:
        return ["暂无风险评估数据"]

    header = "| 排名 | 课外班 | 机构 | 风险等级 | 主要风险 | 建议 |"
    separator = "|------|--------|------|---------|---------|------|"
    lines.append(header)
    lines.append(separator)

    risk_level_icons = {
        "high": "🔴 高风险",
        "medium": "🟡 中风险",
        "low": "🟢 低风险"
    }

    for i, assessment in enumerate(assessments, 1):
        name = assessment.get("class_name", "未知")
        institution = assessment.get("institution", "未知")
        risk_level = assessment.get("risk_level", "low")
        risk_icon = risk_level_icons.get(risk_level, risk_level)
        risks = "、".join(assessment.get("risks", [])[:2]) if assessment.get("risks") else "暂无"
        recommendations = "谨慎选择" if risk_level == "high" else "建议了解" if risk_level == "medium" else "可考虑"

        line = f"| {i} | {name} | {institution} | {risk_icon} | {risks} | {recommendations} |"
        lines.append(line)

    return lines


def render_alerts_list(alerts: List[Dict[str, Any]]) -> List[str]:
    """渲染告警列表"""
    lines = []

    severity_icons = {
        "critical": "🚨 严重",
        "warning": "⚠️ 警告",
        "info": "ℹ️ 信息"
    }

    for i, alert in enumerate(alerts, 1):
        alert_type = alert.get("alert_type", "未知")
        severity = alert.get("severity", "info")
        message = alert.get("message", "")
        recommendation = alert.get("recommendation", "")

        severity_icon = severity_icons.get(severity, severity)

        lines.append(f"### {i}. {severity_icon} {alert_type}")
        lines.append(f"**问题**: {message}")
        lines.append(f"**建议**: {recommendation}")
        lines.append("")

    return lines


def render_recommendations_list(recommendations: List[Dict[str, Any]]) -> List[str]:
    """渲染推荐列表"""
    lines = []

    priority_icons = {
        1: "🔴 高优先级",
        2: "🟡 中优先级",
        3: "🟢 低优先级"
    }

    for i, rec in enumerate(recommendations, 1):
        category = rec.get("category", "未知")
        priority = rec.get("priority", 3)
        title = rec.get("title", "")
        description = rec.get("description", "")
        action_items = rec.get("action_items", [])

        priority_icon = priority_icons.get(priority, f"优先级{priority}")

        lines.append(f"### {i}. {priority_icon} {title}")
        lines.append(f"**类别**: {category}")
        lines.append(f"**描述**: {description}")
        if action_items:
            lines.append("**行动项**:")
            for item in action_items:
                lines.append(f"  - {item}")
        lines.append("")

    return lines


def export_to_json(result: Dict[str, Any], indent: int = 2) -> str:
    """导出为JSON格式"""
    import json
    return json.dumps(result, ensure_ascii=False, indent=indent, default=str)


def export_to_csv_summary(result: Dict[str, Any]) -> str:
    """导出为CSV摘要格式"""
    lines = []
    lines.append("类别,项目,数值/内容")

    if result.get("risk_assessments"):
        for assessment in result.get("risk_assessments", []):
            lines.append(f"风险评估,{assessment.get('class_name','')},{assessment.get('risk_level','')}")

    if result.get("alerts"):
        for alert in result.get("alerts", []):
            lines.append(f"告警,{alert.get('alert_type','')},{alert.get('severity','')}")

    return "\n".join(lines)


def export_to_html(result: Dict[str, Any]) -> str:
    """导出为HTML格式"""
    lines = []
    lines.append("<!DOCTYPE html>")
    lines.append("<html lang='zh-CN'>")
    lines.append("<head>")
    lines.append("    <meta charset='UTF-8'>")
    lines.append("    <title>课外班避坑报告</title>")
    lines.append("</head>")
    lines.append("<body>")
    lines.append("    <h1>⚠️ 课外班避坑报告</h1>")

    if result.get("summary"):
        lines.append("    <h2>📋 本次结论</h2>")
        lines.append("    <ul>")
        for item in result.get("summary", []):
            lines.append(f"        <li>{item}</li>")
        lines.append("    </ul>")

    if result.get("risk_assessments"):
        lines.append("    <h2>📊 风险评估</h2>")
        lines.append("    <table>")
        lines.append("        <tr><th>名称</th><th>机构</th><th>风险等级</th></tr>")
        for assessment in result.get("risk_assessments", []):
            risk_level = assessment.get('risk_level', 'low')
            risk_color = '#ff4444' if risk_level == 'high' else '#ffaa00' if risk_level == 'medium' else '#44aa44'
            lines.append(f"        <tr><td>{assessment.get('class_name','')}</td><td>{assessment.get('institution','')}</td><td style='color:{risk_color};'>{risk_level.upper()}</td></tr>")
        lines.append("    </table>")

    lines.append("</body>")
    lines.append("</html>")

    return "\n".join(lines)


def format_markdown_table(headers: List[str], rows: List) -> List[str]:
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
