"""Markdown report renderer for 家庭日程管理 Agent.

增强版本：添加图表生成、Markdown表格美化、趋势可视化、摘要生成、导出格式支持
"""
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from collections import defaultdict


def render_report(result: Dict[str, Any]) -> str:
    """渲染完整报告

    Args:
        result: 结果字典

    Returns:
        Markdown格式的报告字符串
    """
    lines: List[str] = []
    lines.append("# 家庭日程管理报告")
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

    if result.get("conflicts"):
        lines.append("## F. 日程冲突")
        lines.append("")
        lines.extend(render_conflicts_table(result.get("conflicts", [])))
        lines.append("")

    if result.get("alerts"):
        lines.append("## G. 异常告警")
        lines.append("")
        lines.extend(render_alerts_list(result.get("alerts", [])))
        lines.append("")

    if result.get("recommendations"):
        lines.append("## H. 个性化推荐")
        lines.append("")
        lines.extend(render_recommendations_list(result.get("recommendations", [])))
        lines.append("")

    if result.get("weekly_stats"):
        lines.append("## I. 周统计")
        lines.append("")
        lines.extend(render_weekly_stats_table(result.get("weekly_stats", {})))
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
    """渲染趋势表格

    Args:
        trends: 趋势数据列表

    Returns:
        Markdown表格行列表
    """
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


def render_conflicts_table(conflicts: List[Dict[str, Any]]) -> List[str]:
    """渲染冲突表格

    Args:
        conflicts: 冲突数据列表

    Returns:
        Markdown表格行列表
    """
    lines = []

    if not conflicts:
        return ["✅ 暂无日程冲突"]

    header = "| 日程A | 日程B | 冲突时长(分钟) | 严重程度 | 建议 |"
    separator = "|------|------|---------------|---------|------|"
    lines.append(header)
    lines.append(separator)

    severity_icons = {
        "minor": "🟡 轻微",
        "moderate": "🟠 中等",
        "severe": "🔴 严重"
    }

    for conflict in conflicts:
        schedule_a = conflict.get("schedule_a", "未知")
        schedule_b = conflict.get("schedule_b", "未知")
        overlap = conflict.get("overlap_minutes", 0)
        status = conflict.get("status", "minor")
        suggestion = conflict.get("suggestion", "")

        severity_icon = severity_icons.get(status, status)

        line = f"| {schedule_a} | {schedule_b} | {overlap} | {severity_icon} | {suggestion} |"
        lines.append(line)

    return lines


def render_alerts_list(alerts: List[Dict[str, Any]]) -> List[str]:
    """渲染告警列表

    Args:
        alerts: 告警数据列表

    Returns:
        Markdown列表
    """
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
        timestamp = alert.get("timestamp", "")

        severity_icon = severity_icons.get(severity, severity)

        lines.append(f"### {i}. {severity_icon} {alert_type}")
        if timestamp:
            lines.append(f"**时间**: {timestamp}")
        lines.append(f"**问题**: {message}")
        lines.append(f"**建议**: {recommendation}")
        lines.append("")

    return lines


def render_recommendations_list(recommendations: List[Dict[str, Any]]) -> List[str]:
    """渲染推荐列表

    Args:
        recommendations: 推荐数据列表

    Returns:
        Markdown列表
    """
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
        rationale = rec.get("rationale", "")
        expected_outcome = rec.get("expected_outcome", "")

        priority_icon = priority_icons.get(priority, f"优先级{priority}")

        lines.append(f"### {i}. {priority_icon} {title}")
        lines.append(f"**类别**: {category}")
        lines.append(f"**描述**: {description}")
        if rationale:
            lines.append(f"**依据**: {rationale}")
        if expected_outcome:
            lines.append(f"**预期效果**: {expected_outcome}")
        if action_items:
            lines.append("**行动项**:")
            for item in action_items:
                lines.append(f"  - {item}")
        lines.append("")

    return lines


def render_weekly_stats_table(stats: Dict[str, Any]) -> List[str]:
    """渲染周统计表格

    Args:
        stats: 周统计数据字典

    Returns:
        Markdown表格
    """
    lines = []

    if not stats:
        return ["暂无周统计数据"]

    week_start = stats.get("week_start", "")
    week_end = stats.get("week_end", "")
    lines.append(f"**统计周期**: {week_start} 至 {week_end}")
    lines.append("")

    header = "| 指标 | 数值 |"
    separator = "|------|------|"
    lines.append(header)
    lines.append(separator)

    metrics = [
        ("总日程数", stats.get("total_schedules", 0)),
        ("已完成日程", stats.get("completed_schedules", 0)),
        ("完成率(%)", stats.get("completion_rate", 0)),
        ("冲突数量", stats.get("conflict_count", 0))
    ]

    for metric, value in metrics:
        if isinstance(value, float):
            lines.append(f"| {metric} | {value:.1f} |")
        else:
            lines.append(f"| {metric} | {value} |")

    lines.append("")

    schedule_dist = stats.get("schedule_type_distribution", {})
    if schedule_dist:
        lines.append("**日程类型分布**:")
        for st, count in schedule_dist.items():
            lines.append(f"- {st}: {count}个")
        lines.append("")

    return lines


def render_trend_chart_ascii(data_points: List[float], width: int = 40, height: int = 10) -> str:
    """渲染ASCII趋势图表

    Args:
        data_points: 数据点列表
        width: 图表宽度
        height: 图表高度

    Returns:
        ASCII图表字符串
    """
    if not data_points or len(data_points) < 2:
        return "数据点不足，无法生成图表"

    min_val = min(data_points)
    max_val = max(data_points)
    val_range = max_val - min_val

    if val_range == 0:
        val_range = 1

    chart = []
    chart.append("📈 趋势变化:")
    chart.append("")

    rows = []
    for i in range(height):
        row = [" "] * width
        rows.append(row)

    for i, val in enumerate(data_points):
        x = int((i / (len(data_points) - 1)) * (width - 1))
        normalized = (val - min_val) / val_range
        y = height - 1 - int(normalized * (height - 1))
        rows[y][x] = "█"

        if i > 0:
            prev_normalized = (data_points[i-1] - min_val) / val_range
            prev_y = height - 1 - int(prev_normalized * (height - 1))
            if prev_y != y:
                step = 1 if y < prev_y else -1
                for step_y in range(prev_y, y, step):
                    if rows[step_y][x] == " ":
                        rows[step_y][x] = "│"
            else:
                for step_x in range(min(x, int((i-1) / (len(data_points) - 1) * (width - 1))), x):
                    if rows[y][step_x] == " ":
                        rows[y][step_x] = "─"

    for row in rows:
        chart.append("│" + "".join(row) + "│")

    chart.append("└" + "─" * width + "┘")

    chart.append("")
    chart.append(f"最小值: {min_val:.1f}  |  最大值: {max_val:.1f}  |  平均: {sum(data_points)/len(data_points):.1f}")

    return "\n".join(chart)


def render_distribution_bars(distribution: Dict[str, int], width: int = 30) -> str:
    """渲染分布条形图

    Args:
        distribution: 分布字典 {名称: 数量}
        width: 条形图宽度

    Returns:
        ASCII条形图字符串
    """
    if not distribution:
        return "暂无分布数据"

    lines = []
    lines.append("📊 分布统计:")
    lines.append("")

    total = sum(distribution.values())
    if total == 0:
        return "暂无分布数据"

    max_label_len = max(len(str(label)) for label in distribution.keys())
    max_count = max(distribution.values())

    for label, count in distribution.items():
        pct = (count / total) * 100
        bar_len = int((count / max_count) * width) if max_count > 0 else 0
        bar = "█" * bar_len + "░" * (width - bar_len)
        lines.append(f"{str(label):<{max_label_len}} │ {bar} │ {count:>4} ({pct:5.1f}%)")

    return "\n".join(lines)


def generate_summary_text(result: Dict[str, Any]) -> str:
    """生成摘要文本

    Args:
        result: 结果字典

    Returns:
        摘要文本
    """
    lines = []

    summary = result.get("summary", [])
    if summary:
        lines.append("📋 核心结论:")
        for point in summary[:3]:
            lines.append(f"  • {point}")
        lines.append("")

    if result.get("trends"):
        lines.append("📈 趋势洞察:")
        for trend in result.get("trends", [])[:2]:
            metric = trend.get("metric_name", "未知")
            direction = trend.get("trend_direction", "stable")
            pct = trend.get("trend_percentage", 0)
            lines.append(f"  • {metric}: {direction} ({pct:+.1f}%)")
        lines.append("")

    if result.get("conflicts"):
        conflict_count = len(result.get("conflicts", []))
        severe_count = sum(1 for c in result.get("conflicts", []) if c.get("status") in ["severe", "moderate"])
        lines.append(f"⚠️ 日程冲突: 共{conflict_count}个")
        if severe_count > 0:
            lines.append(f"  🚨 其中{severe_count}个需要紧急处理")
        lines.append("")

    if result.get("alerts"):
        alert_count = len(result.get("alerts", []))
        critical_count = sum(1 for a in result.get("alerts", []) if a.get("severity") == "critical")
        lines.append(f"⚠️ 告警提醒: 共{alert_count}项")
        if critical_count > 0:
            lines.append(f"  🚨 其中{critical_count}项需要紧急关注")
        lines.append("")

    if result.get("recommendations"):
        top_rec = result.get("recommendations", [])[0]
        title = top_rec.get("title", "暂无")
        lines.append(f"💡 首要建议: {title}")

    return "\n".join(lines)


def export_to_json(result: Dict[str, Any], indent: int = 2) -> str:
    """导出为JSON格式

    Args:
        result: 结果字典
        indent: 缩进空格数

    Returns:
        JSON字符串
    """
    import json
    return json.dumps(result, ensure_ascii=False, indent=indent, default=str)


def export_to_csv_summary(result: Dict[str, Any]) -> str:
    """导出为CSV摘要格式

    Args:
        result: 结果字典

    Returns:
        CSV字符串
    """
    lines = []
    lines.append("类别,项目,数值/内容")

    if result.get("trends"):
        for trend in result.get("trends", []):
            lines.append(f"趋势,{trend.get('metric_name','')},{trend.get('average',0):.2f}")
            lines.append(f"趋势,{trend.get('metric_name','')}趋势,{trend.get('trend_direction','')}")
            lines.append(f"趋势,{trend.get('metric_name','')}变化,{trend.get('trend_percentage',0):.2f}%")

    if result.get("conflicts"):
        for conflict in result.get("conflicts", []):
            lines.append(f"冲突,{conflict.get('schedule_a','')} vs {conflict.get('schedule_b','')},{conflict.get('overlap_minutes',0)}分钟")

    if result.get("weekly_stats"):
        stats = result.get("weekly_stats", {})
        for key, value in stats.items():
            if not isinstance(value, dict):
                lines.append(f"周统计,{key},{value}")

    return "\n".join(lines)


def export_to_html(result: Dict[str, Any]) -> str:
    """导出为HTML格式

    Args:
        result: 结果字典

    Returns:
        HTML字符串
    """
    lines = []
    lines.append("<!DOCTYPE html>")
    lines.append("<html lang='zh-CN'>")
    lines.append("<head>")
    lines.append("    <meta charset='UTF-8'>")
    lines.append("    <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    lines.append("    <title>家庭日程管理报告</title>")
    lines.append("    <style>")
    lines.append("        body { font-family: 'Microsoft YaHei', Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }")
    lines.append("        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }")
    lines.append("        h2 { color: #34495e; margin-top: 30px; }")
    lines.append("        .alert { padding: 10px; margin: 10px 0; border-radius: 5px; }")
    lines.append("        .alert-warning { background-color: #fff3cd; border: 1px solid #ffc107; }")
    lines.append("        .alert-info { background-color: #d1ecf1; border: 1px solid #17a2b8; }")
    lines.append("        table { width: 100%; border-collapse: collapse; margin: 15px 0; }")
    lines.append("        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
    lines.append("        th { background-color: #3498db; color: white; }")
    lines.append("        .recommendation { background-color: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #28a745; }")
    lines.append("    </style>")
    lines.append("</head>")
    lines.append("<body>")
    lines.append("    <h1>📅 家庭日程管理报告</h1>")

    if result.get("summary"):
        lines.append("    <h2>📋 本次结论</h2>")
        lines.append("    <ul>")
        for item in result.get("summary", []):
            lines.append(f"        <li>{item}</li>")
        lines.append("    </ul>")

    if result.get("conflicts"):
        lines.append("    <h2>⚠️ 日程冲突</h2>")
        lines.append("    <table>")
        lines.append("        <tr><th>日程A</th><th>日程B</th><th>冲突时长</th><th>严重程度</th></tr>")
        for conflict in result.get("conflicts", []):
            lines.append(f"        <tr><td>{conflict.get('schedule_a','')}</td><td>{conflict.get('schedule_b','')}</td><td>{conflict.get('overlap_minutes',0)}分钟</td><td>{conflict.get('status','')}</td></tr>")
        lines.append("    </table>")

    if result.get("alerts"):
        lines.append("    <h2>⚠️ 异常告警</h2>")
        for alert in result.get("alerts", []):
            severity = alert.get("severity", "info")
            alert_class = f"alert-{severity}" if severity in ["warning", "info"] else "alert"
            lines.append(f"    <div class='alert {alert_class}'>")
            lines.append(f"        <strong>{alert.get('alert_type', '')}:</strong> {alert.get('message', '')}")
            lines.append(f"        <br><em>建议:</em> {alert.get('recommendation', '')}")
            lines.append("    </div>")

    if result.get("recommendations"):
        lines.append("    <h2>💡 个性化推荐</h2>")
        for rec in result.get("recommendations", []):
            lines.append("    <div class='recommendation'>")
            lines.append(f"        <h3>{rec.get('title', '')}</h3>")
            lines.append(f"        <p>{rec.get('description', '')}</p>")
            if rec.get("action_items"):
                lines.append("        <strong>行动项:</strong>")
                lines.append("        <ul>")
                for item in rec.get("action_items", []):
                    lines.append(f"            <li>{item}</li>")
                lines.append("        </ul>")
            lines.append("    </div>")

    if result.get("weekly_stats"):
        lines.append("    <h2>📊 周统计</h2>")
        lines.append("    <table>")
        stats = result.get("weekly_stats", {})
        metrics = [
            ("总日程数", stats.get("total_schedules", 0)),
            ("已完成日程", stats.get("completed_schedules", 0)),
            ("完成率(%)", stats.get("completion_rate", 0)),
            ("冲突数量", stats.get("conflict_count", 0))
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


def format_markdown_table(headers: List[str], rows: List[List[Any]]) -> List[str]:
    """格式化Markdown表格

    Args:
        headers: 表头列表
        rows: 行数据列表

    Returns:
        Markdown表格行列表
    """
    lines = []

    header_line = "| " + " | ".join(str(h) for h in headers) + " |"
    separator = "|" + "|".join("---" for _ in headers) + "|"

    lines.append(header_line)
    lines.append(separator)

    for row in rows:
        row_line = "| " + " | ".join(str(cell) for cell in row) + " |"
        lines.append(row_line)

    return lines
