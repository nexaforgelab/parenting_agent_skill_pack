"""Markdown report renderer for 幼儿园择校 Agent.

增强版本：添加图表生成、Markdown表格美化、趋势可视化、摘要生成、导出格式支持
"""
from typing import Any, Dict, List
from datetime import datetime


def render_report(result: Dict[str, Any]) -> str:
    """渲染完整报告"""
    lines: List[str] = []
    lines.append("# 幼儿园择校报告")
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

    if result.get("comparison_results"):
        lines.append("## E. 幼儿园对比")
        lines.append("")
        lines.extend(render_comparison_table(result.get("comparison_results", [])))
        lines.append("")

    if result.get("alerts"):
        lines.append("## F. 异常告警")
        lines.append("")
        lines.extend(render_alerts_list(result.get("alerts", [])))
        lines.append("")

    if result.get("recommendations"):
        lines.append("## G. 个性化推荐")
        lines.append("")
        lines.extend(render_recommendations_list(result.get("recommendations", [])))
        lines.append("")

    if result.get("selection_statistics"):
        lines.append("## H. 择校统计")
        lines.append("")
        lines.extend(render_selection_stats_table(result.get("selection_statistics", {})))
        lines.append("")

    lines.append("## I. 风险与人工核验")
    for x in result.get("risk_notes", []):
        lines.append(f"- {x}")
    lines.append("")

    lines.append("## J. 下次追踪字段")
    for x in result.get("next_tracking_fields", []):
        lines.append(f"- {x}")
    lines.append("")

    return "\n".join(lines)


def render_comparison_table(comparisons: List[Dict[str, Any]]) -> List[str]:
    """渲染对比表格"""
    lines = []

    if not comparisons:
        return ["暂无对比数据"]

    header = "| 排名 | 幼儿园 | 综合得分 | 匹配度 | 优势 | 劣势 | 推荐理由 |"
    separator = "|------|--------|---------|-------|------|------|---------|"
    lines.append(header)
    lines.append(separator)

    for i, comp in enumerate(comparisons, 1):
        name = comp.get("kindergarten_name", "未知")
        score = comp.get("overall_score", 0)
        match = comp.get("match_percentage", 0)
        pros = "、".join(comp.get("pros", [])[:2]) if comp.get("pros") else "暂无"
        cons = "、".join(comp.get("cons", [])[:2]) if comp.get("cons") else "暂无"
        rec = comp.get("recommendation", "")[:20]

        line = f"| {i} | {name} | {score:.1f} | {match:.0f}% | {pros} | {cons} | {rec}... |"
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


def render_selection_stats_table(stats: Dict[str, Any]) -> List[str]:
    """渲染择校统计表格"""
    lines = []

    if not stats:
        return ["暂无择校统计数据"]

    header = "| 指标 | 数值 |"
    separator = "|------|------|"
    lines.append(header)
    lines.append(separator)

    metrics = [
        ("幼儿园总数", stats.get("total_kindergartens", 0)),
        ("已评估数", stats.get("evaluated_count", 0)),
        ("平均综合得分", stats.get("average_overall_score", 0)),
        ("推荐首选", stats.get("top_ranked", "暂无"))
    ]

    for metric, value in metrics:
        if isinstance(value, float):
            lines.append(f"| {metric} | {value:.1f} |")
        else:
            lines.append(f"| {metric} | {value} |")

    budget_range = stats.get("budget_range", {})
    if budget_range:
        lines.append(f"| 学费范围 | {budget_range.get('min', 0):.0f}-{budget_range.get('max', 0):.0f}元/年 |")

    distance_range = stats.get("distance_range", {})
    if distance_range:
        lines.append(f"| 距离范围 | {distance_range.get('min', 0):.1f}-{distance_range.get('max', 0):.1f}公里 |")

    return lines


def export_to_json(result: Dict[str, Any], indent: int = 2) -> str:
    """导出为JSON格式"""
    import json
    return json.dumps(result, ensure_ascii=False, indent=indent, default=str)


def export_to_csv_summary(result: Dict[str, Any]) -> str:
    """导出为CSV摘要格式"""
    lines = []
    lines.append("类别,项目,数值/内容")

    if result.get("comparison_results"):
        for comp in result.get("comparison_results", []):
            lines.append(f"对比,{comp.get('kindergarten_name','')},得分{comp.get('overall_score',0):.1f}")

    if result.get("selection_statistics"):
        stats = result.get("selection_statistics", {})
        for key, value in stats.items():
            if not isinstance(value, dict):
                lines.append(f"择校统计,{key},{value}")

    return "\n".join(lines)


def export_to_html(result: Dict[str, Any]) -> str:
    """导出为HTML格式"""
    lines = []
    lines.append("<!DOCTYPE html>")
    lines.append("<html lang='zh-CN'>")
    lines.append("<head>")
    lines.append("    <meta charset='UTF-8'>")
    lines.append("    <title>幼儿园择校报告</title>")
    lines.append("</head>")
    lines.append("<body>")
    lines.append("    <h1>🏫 幼儿园择校报告</h1>")

    if result.get("summary"):
        lines.append("    <h2>📋 本次结论</h2>")
        lines.append("    <ul>")
        for item in result.get("summary", []):
            lines.append(f"        <li>{item}</li>")
        lines.append("    </ul>")

    if result.get("comparison_results"):
        lines.append("    <h2>📊 幼儿园对比</h2>")
        lines.append("    <table>")
        lines.append("        <tr><th>排名</th><th>名称</th><th>得分</th><th>匹配度</th></tr>")
        for i, comp in enumerate(result.get("comparison_results", [])[:5], 1):
            lines.append(f"        <tr><td>{i}</td><td>{comp.get('kindergarten_name','')}</td><td>{comp.get('overall_score',0):.1f}</td><td>{comp.get('match_percentage',0):.0f}%</td></tr>")
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
