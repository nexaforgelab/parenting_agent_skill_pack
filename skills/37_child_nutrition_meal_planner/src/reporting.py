"""Markdown report renderer for 儿童营养餐 Agent.

增强版本：添加图表生成、Markdown表格美化、趋势可视化、摘要生成、导出格式支持
"""
from typing import Any, Dict, List
from collections import defaultdict


def render_report(result: Dict[str, Any]) -> str:
    """渲染完整报告"""
    lines: List[str] = []
    lines.append("# 儿童营养餐报告")
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
        lines.append("## F. 营养告警")
        lines.append("")
        lines.extend(render_alerts_list(result.get("alerts", [])))
        lines.append("")

    if result.get("recommendations"):
        lines.append("## G. 个性化推荐")
        lines.append("")
        lines.extend(render_recommendations_list(result.get("recommendations", [])))
        lines.append("")

    if result.get("weekly_stats"):
        lines.append("## H. 周统计")
        lines.append("")
        lines.extend(render_weekly_stats_table(result.get("weekly_stats", {})))
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
        direction_icon = {"increasing": "📈 上升", "decreasing": "📉 下降", "stable": "➡️ 稳定"}.get(direction, direction)
        line = f"| {metric} | {avg:.1f} | {min_val:.1f} | {max_val:.1f} | {direction_icon} | {pct:+.1f}% |"
        lines.append(line)
    return lines


def render_alerts_list(alerts: List[Dict[str, Any]]) -> List[str]:
    """渲染告警列表"""
    lines = []
    severity_icons = {"critical": "🚨 严重", "warning": "⚠️ 警告", "info": "ℹ️ 信息"}

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
    priority_icons = {1: "🔴 高优先级", 2: "🟡 中优先级", 3: "🟢 低优先级"}

    for i, rec in enumerate(recommendations, 1):
        priority = rec.get("priority", 3)
        title = rec.get("title", "")
        description = rec.get("description", "")
        action_items = rec.get("action_items", [])
        priority_icon = priority_icons.get(priority, f"优先级{priority}")

        lines.append(f"### {i}. {priority_icon} {title}")
        lines.append(f"**描述**: {description}")
        if action_items:
            lines.append("**行动项**:")
            for item in action_items:
                lines.append(f"  - {item}")
        lines.append("")
    return lines


def render_weekly_stats_table(stats: Dict[str, Any]) -> List[str]:
    """渲染周统计表格"""
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
        ("总餐次", stats.get("total_meals", 0)),
        ("日均热量(kcal)", stats.get("avg_calories_per_day", 0)),
        ("日均蛋白质(g)", stats.get("avg_protein_g_per_day", 0)),
        ("多样性评分", stats.get("variety_score", 0))
    ]

    for metric, value in metrics:
        if isinstance(value, float):
            lines.append(f"| {metric} | {value:.1f} |")
        else:
            lines.append(f"| {metric} | {value} |")
    lines.append("")
    return lines


def export_to_json(result: Dict[str, Any], indent: int = 2) -> str:
    """导出为JSON格式"""
    import json
    return json.dumps(result, ensure_ascii=False, indent=indent, default=str)


def export_to_csv_summary(result: Dict[str, Any]) -> str:
    """导出为CSV摘要格式"""
    lines = ["类别,项目,数值/内容"]
    if result.get("trends"):
        for trend in result.get("trends", []):
            lines.append(f"趋势,{trend.get('metric_name','')},{trend.get('average',0):.2f}")
    return "\n".join(lines)


def export_to_html(result: Dict[str, Any]) -> str:
    """导出为HTML格式"""
    lines = ["<!DOCTYPE html>", "<html lang='zh-CN'>", "<head>", "    <meta charset='UTF-8'>",
             "    <title>儿童营养餐报告</title>", "    <style>",
             "        body { font-family: 'Microsoft YaHei', Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }",
             "        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }",
             "        .alert { padding: 10px; margin: 10px 0; border-radius: 5px; }",
             "        .alert-warning { background-color: #fff3cd; border: 1px solid #ffc107; }",
             "    </style>", "</head>", "<body>", "    <h1>🍽️ 儿童营养餐报告</h1>"]

    if result.get("summary"):
        lines.append("    <h2>📋 本次结论</h2>")
        lines.append("    <ul>")
        for item in result.get("summary", []):
            lines.append(f"        <li>{item}</li>")
        lines.append("    </ul>")

    lines.append("</body>")
    lines.append("</html>")
    return "\n".join(lines)
