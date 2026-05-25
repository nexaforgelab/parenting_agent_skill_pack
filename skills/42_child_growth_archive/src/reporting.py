"""Markdown report renderer for 儿童成长档案 Agent.

增强版本：添加图表生成、Markdown表格美化、趋势可视化、摘要生成、导出格式支持
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, date


def render_report(result: Dict[str, Any]) -> str:
    """渲染完整报告"""
    lines: List[str] = []
    lines.append("# 儿童成长档案报告")
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

    if result.get("trends"):
        lines.append("## E. 趋势分析")
        lines.append("")
        lines.extend(render_trends_table(result.get("trends", [])))
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

    if result.get("archive_statistics"):
        lines.append("## H. 成长统计")
        lines.append("")
        lines.extend(render_archive_stats_table(result.get("archive_statistics", {})))
        lines.append("")

    if result.get("category_distribution"):
        lines.append("## I. 分类分布")
        lines.append("")
        lines.extend(render_category_distribution(result.get("category_distribution", {})))
        lines.append("")

    lines.append("## J. 风险与人工核验")
    for x in result.get("risk_notes", []):
        lines.append(f"- {x}")
    lines.append("")

    lines.append("## K. 下次追踪字段")
    for x in result.get("next_tracking_fields", []):
        lines.append(f"- {x}")
    lines.append("")

    return "\n".join(lines)


def render_trends_table(trends: List[Dict[str, Any]]) -> List[str]:
    """渲染趋势表格"""
    lines = []

    if not trends:
        return ["暂无趋势数据"]

    header = "| 指标 | 平均值 | 最小值 | 最大值 | 趋势方向 | 变化百分比 |"
    separator = "|------|--------|-------|-------|---------|-----------|"
    lines.append(header)
    lines.append(separator)

    for trend in trends:
        metric = trend.get("metric_name", "未知")
        avg = trend.get("average", 0)
        min_val = trend.get("min_value", 0)
        max_val = trend.get("max_value", 0)
        direction = trend.get("trend_direction", "stable")
        pct = trend.get("trend_percentage", 0)

        direction_icon = {
            "increasing": "📈 上升",
            "decreasing": "📉 下降",
            "stable": "➡️ 稳定"
        }.get(direction, direction)

        line = f"| {metric} | {avg:.1f} | {min_val:.1f} | {max_val:.1f} | {direction_icon} | {pct:+.1f}% |"
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


def render_archive_stats_table(stats: Dict[str, Any]) -> List[str]:
    """渲染成长统计表格"""
    lines = []

    if not stats:
        return ["暂无成长统计数据"]

    header = "| 指标 | 数值 |"
    separator = "|------|------|"
    lines.append(header)
    lines.append(separator)

    metrics = [
        ("总记录数", stats.get("total_records", 0)),
        ("里程碑数", stats.get("milestone_count", 0)),
        ("档案数量", stats.get("archive_count", 0)),
        ("有附件记录", stats.get("records_with_attachments", 0)),
        ("有标签记录", stats.get("records_with_tags", 0)),
        ("月均记录", stats.get("average_records_per_month", 0))
    ]

    for metric, value in metrics:
        if isinstance(value, float):
            lines.append(f"| {metric} | {value:.1f} |")
        else:
            lines.append(f"| {metric} | {value} |")

    lines.append("")

    records_by_year = stats.get("records_by_year", {})
    if records_by_year:
        lines.append("**年度分布**:")
        for year, count in sorted(records_by_year.items(), reverse=True):
            lines.append(f"- {year}年: {count}条")
        lines.append("")

    return lines


def render_category_distribution(distribution: Dict[str, int]) -> List[str]:
    """渲染分类分布"""
    lines = []

    if not distribution:
        return ["暂无分类数据"]

    total = sum(distribution.values())
    if total == 0:
        return ["暂无分类数据"]

    header = "| 分类 | 数量 | 占比 |"
    separator = "|------|------|------|"
    lines.append(header)
    lines.append(separator)

    sorted_dist = sorted(distribution.items(), key=lambda x: x[1], reverse=True)

    for category, count in sorted_dist:
        pct = (count / total) * 100
        lines.append(f"| {category} | {count} | {pct:.1f}% |")

    lines.append("")

    if len(sorted_dist) > 0:
        top_category = sorted_dist[0][0]
        top_count = sorted_dist[0][1]
        lines.append(f"📊 最多: {top_category} ({top_count}条)")

    return lines


def export_to_json(result: Dict[str, Any], indent: int = 2) -> str:
    """导出为JSON格式"""
    import json
    return json.dumps(result, ensure_ascii=False, indent=indent, default=str)


def export_to_csv_summary(result: Dict[str, Any]) -> str:
    """导出为CSV摘要格式"""
    lines = []
    lines.append("类别,项目,数值/内容")

    if result.get("trends"):
        for trend in result.get("trends", []):
            lines.append(f"趋势,{trend.get('metric_name','')},{trend.get('average',0):.2f}")
            lines.append(f"趋势,{trend.get('metric_name','')}趋势,{trend.get('trend_direction','')}")
            lines.append(f"趋势,{trend.get('metric_name','')}变化,{trend.get('trend_percentage',0):.2f}%")

    if result.get("archive_statistics"):
        stats = result.get("archive_statistics", {})
        for key, value in stats.items():
            if not isinstance(value, dict):
                lines.append(f"成长统计,{key},{value}")

    if result.get("category_distribution"):
        dist = result.get("category_distribution", {})
        for cat, count in dist.items():
            lines.append(f"分类,{cat},{count}")

    return "\n".join(lines)


def export_to_html(result: Dict[str, Any]) -> str:
    """导出为HTML格式"""
    lines = []
    lines.append("<!DOCTYPE html>")
    lines.append("<html lang='zh-CN'>")
    lines.append("<head>")
    lines.append("    <meta charset='UTF-8'>")
    lines.append("    <title>儿童成长档案报告</title>")
    lines.append("</head>")
    lines.append("<body>")
    lines.append("    <h1>📚 儿童成长档案报告</h1>")

    if result.get("summary"):
        lines.append("    <h2>📋 本次结论</h2>")
        lines.append("    <ul>")
        for item in result.get("summary", []):
            lines.append(f"        <li>{item}</li>")
        lines.append("    </ul>")

    if result.get("archive_statistics"):
        lines.append("    <h2>📊 成长统计</h2>")
        lines.append("    <table>")
        stats = result.get("archive_statistics", {})
        metrics = [
            ("总记录数", stats.get("total_records", 0)),
            ("里程碑数", stats.get("milestone_count", 0)),
            ("月均记录", stats.get("average_records_per_month", 0))
        ]
        for metric, value in metrics:
            if isinstance(value, float):
                lines.append(f"        <tr><td>{metric}</td><td>{value:.1f}</td></tr>")
            else:
                lines.append(f"        <tr><td>{metric}</td><td>{value}</td></tr>")
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
