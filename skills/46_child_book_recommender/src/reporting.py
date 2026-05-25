"""Markdown report renderer for 儿童图书推荐 Agent.

提供增强的报告功能：Markdown表格美化、可视化、摘要生成和多格式导出支持。
"""
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
import json


def create_table(
    headers: List[str],
    rows: List[List[str]],
    align: Optional[List[str]] = None,
    style: str = "default"
) -> str:
    """创建Markdown表格

    Args:
        headers: 表头列表
        rows: 行数据列表
        align: 列对齐方式 (left/center/right)
        style: 表格样式

    Returns:
        Markdown表格字符串
    """
    if not headers:
        return ""

    lines = []

    align_map = {
        "left": ":---",
        "center": ":---:",
        "right": "---:"
    }

    if align is None:
        align = ["left"] * len(headers)

    header_line = "| " + " | ".join(headers) + " |"
    separator_line = "|" + "|".join([
        align_map.get(a, ":---") for a in align
    ]) + "|"

    lines.append(header_line)
    lines.append(separator_line)

    for row in rows:
        row_line = "| " + " | ".join(str(cell) for cell in row) + " |"
        lines.append(row_line)

    return "\n".join(lines)


def create_styled_box(content: str, style: str = "info") -> str:
    """创建样式化文本框

    Args:
        content: 框内容
        style: 样式类型 (info/warning/tip/critical)

    Returns:
        样式化文本框
    """
    style_map = {
        "info": {"icon": "📋", "border": "━"},
        "warning": {"icon": "⚠️", "border": "┅"},
        "tip": {"icon": "💡", "border": "━"},
        "critical": {"icon": "🚨", "border": "┅"}
    }

    style_info = style_map.get(style, style_map["info"])
    lines = content.split("\n")

    result = [
        f"┌{'─' * (len(max(lines, key=len)) + 2)}┐",
    ]

    for line in lines:
        padding = " " * (len(max(lines, key=len)) - len(line))
        result.append(f"│ {line}{padding} │")

    result.append(f"└{'─' * (len(max(lines, key=len)) + 2)}┘")

    return "\n".join(result)


def create_progress_bar(value: float, max_value: float = 100, width: int = 20) -> str:
    """创建进度条可视化

    Args:
        value: 当前值
        max_value: 最大值
        width: 进度条宽度

    Returns:
        进度条字符串
    """
    percentage = min(value / max_value, 1.0)
    filled = int(width * percentage)
    empty = width - filled

    bar = "█" * filled + "░" * empty
    percent_str = f"{percentage * 100:.1f}%"

    return f"[{bar}] {percent_str}"


def create_rating_stars(rating: float, max_rating: float = 5) -> str:
    """创建星级评分可视化

    Args:
        rating: 当前评分
        max_rating: 最大评分

    Returns:
        星级字符串
    """
    full_stars = int(rating)
    half_star = (rating - full_stars) >= 0.5
    empty_stars = int(max_rating - full_stars - (1 if half_star else 0))

    stars = "⭐" * full_stars
    if half_star:
        stars += "⭐" + "☆" * empty_stars
    else:
        stars += "☆" * empty_stars

    return stars


def generate_summary(data: Dict[str, Any]) -> List[str]:
    """生成摘要信息

    Args:
        data: 结果数据字典

    Returns:
        摘要列表
    """
    summary = []

    if "summary" in data and data["summary"]:
        summary.extend(data["summary"])
    else:
        summary.append("本次分析已完成")

    if "statistics" in data:
        stats = data["statistics"]
        if "total_books" in stats:
            summary.append(f"共推荐 {stats['total_books']} 本图书")
        if "avg_educational_value" in stats:
            summary.append(f"平均教育价值: {stats['avg_educational_value']:.1f}/5")
        if "avg_engagement" in stats:
            summary.append(f"平均趣味性: {stats['avg_engagement']:.1f}/5")

    return summary


def generate_statistics_table(data: Dict[str, Any]) -> str:
    """生成统计表格

    Args:
        data: 结果数据字典

    Returns:
        Markdown表格字符串
    """
    stats = data.get("statistics", {})

    if not stats:
        return ""

    headers = ["指标", "数值"]
    rows = []

    for key, value in stats.items():
        display_key = {
            "total_books": "推荐图书总数",
            "avg_educational_value": "平均教育价值",
            "avg_engagement": "平均趣味性",
            "total_reading_sessions": "共读会话总数",
            "avg_session_duration": "平均会话时长(分钟)",
            "most_common_theme": "最常见主题",
            "completion_rate": "阅读完成率"
        }.get(key, key)

        if isinstance(value, float):
            value = f"{value:.2f}"
        rows.append([display_key, str(value)])

    return create_table(headers, rows, align=["left", "right"])


def generate_book_list_table(books: List[Dict[str, Any]]) -> str:
    """生成图书列表表格

    Args:
        books: 图书列表

    Returns:
        Markdown表格字符串
    """
    if not books:
        return "暂无推荐图书"

    headers = ["优先级", "书名", "作者", "分类", "适读年龄", "教育价值", "趣味性"]
    rows = []

    for book in books:
        priority = book.get("purchase_priority", "-")
        title = book.get("title", "-")
        author = book.get("author", "-")
        category = book.get("category", "-")
        age_range = book.get("age_range", "-")
        edu_value = book.get("educational_value", "-")
        engagement = book.get("engagement_score", "-")

        if isinstance(edu_value, int):
            edu_value = create_rating_stars(edu_value)
        if isinstance(engagement, int):
            engagement = create_rating_stars(engagement)

        rows.append([
            str(priority),
            title[:30],
            author[:15],
            category,
            age_range,
            str(edu_value),
            str(engagement)
        ])

    return create_table(headers, rows, align=["center", "left", "left", "center", "center", "center", "center"])


def generate_reading_progress_table(progress: Dict[str, Any]) -> str:
    """生成阅读进度表格

    Args:
        progress: 进度数据字典

    Returns:
        Markdown表格字符串
    """
    if not progress:
        return "暂无阅读进度数据"

    headers = ["阶段", "计划", "实际", "完成率", "状态"]
    rows = []

    for stage, data in progress.items():
        planned = data.get("planned", "-")
        actual = data.get("actual", "-")
        completion = data.get("completion_rate", 0)
        status = data.get("status", "-")

        completion_bar = create_progress_bar(completion, 100, 15)
        status_icon = {"completed": "✅", "in_progress": "🔄", "pending": "⏳"}.get(status, "❓")

        rows.append([
            stage,
            str(planned),
            str(actual),
            completion_bar,
            f"{status_icon} {status}"
        ])

    return create_table(headers, rows)


def generate_trend_chart(data_points: List[Dict[str, Any]], metric: str = "值") -> str:
    """生成简单的趋势图表

    Args:
        data_points: 数据点列表
        metric: 指标名称

    Returns:
        ASCII图表字符串
    """
    if not data_points or len(data_points) < 2:
        return f"数据点不足，无法生成趋势图"

    values = [float(dp.get("value", 0)) for dp in data_points]
    labels = [dp.get("label", "") for dp in data_points]

    if not values:
        return "无有效数据"

    max_val = max(values)
    min_val = min(values)
    value_range = max_val - min_val if max_val != min_val else 1

    chart_height = 5
    chart_lines = []

    for i in range(chart_height, -1, -1):
        threshold = min_val + (value_range * i / chart_height)
        line = ""
        for val in values:
            if val >= threshold:
                line += "█"
            else:
                line += " "
            line += "  "

        if i == 0:
            line = "└" + "──" * len(values)

        chart_lines.append(line)

    chart_lines.append("  " + "  ".join(labels[:len(values)]))

    return "\n".join(chart_lines)


def export_to_json(data: Dict[str, Any]) -> str:
    """导出为JSON格式

    Args:
        data: 结果数据字典

    Returns:
        JSON字符串
    """
    return json.dumps(data, ensure_ascii=False, indent=2)


def export_to_csv_headers(data: Dict[str, Any], table_type: str = "books") -> str:
    """导出为CSV格式的表头

    Args:
        data: 结果数据字典
        table_type: 表格类型

    Returns:
        CSV字符串
    """
    if table_type == "books":
        headers = ["优先级", "书名", "作者", "分类", "年龄范围", "教育价值", "趣味性", "推荐理由"]
    elif table_type == "sessions":
        headers = ["日期", "书名", "时长(分钟)", "参与度", "孩子反应"]
    else:
        headers = ["指标", "数值"]

    return ",".join(headers)


def render_report(result: Dict[str, Any]) -> str:
    """渲染完整报告

    Args:
        result: 结果数据字典

    Returns:
        Markdown报告字符串
    """
    lines: List[str] = []
    lines.append("# 儿童图书推荐报告")
    lines.append("")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines.append(f"> 生成时间: {timestamp}")
    lines.append("")

    summary = generate_summary(result)
    lines.append("## A. 本次结论")
    for x in summary:
        lines.append(f"- {x}")
    lines.append("")

    known_facts = result.get("known_facts", [])
    if known_facts:
        lines.append("## B. 已知信息")
        for x in known_facts:
            lines.append(f"- {x}")
        lines.append("")

    analysis = result.get("analysis", [])
    if analysis:
        lines.append("## C. 分析与判断")
        for x in analysis:
            lines.append(f"- {x}")
        lines.append("")

    if "statistics" in result:
        lines.append("## D. 数据统计")
        stats_table = generate_statistics_table(result)
        if stats_table:
            lines.append(stats_table)
        lines.append("")

    if "books" in result:
        lines.append("## E. 推荐书单")
        books_table = generate_book_list_table(result["books"])
        lines.append(books_table)
        lines.append("")

    if "reading_progress" in result:
        lines.append("## F. 阅读进度")
        progress_table = generate_reading_progress_table(result["reading_progress"])
        lines.append(progress_table)
        lines.append("")

    if "trends" in result and result["trends"]:
        lines.append("## G. 趋势分析")
        for trend in result["trends"]:
            trend_name = trend.get("metric_name", "指标")
            trend_direction = trend.get("trend_direction", "stable")
            trend_percentage = trend.get("trend_percentage", 0)

            direction_icon = {
                "increasing": "📈",
                "decreasing": "📉",
                "stable": "➡️"
            }.get(trend_direction, "➡️")

            lines.append(f"- {direction_icon} {trend_name}: {trend_direction} ({trend_percentage:+.1f}%)")
        lines.append("")

    action_plan = result.get("action_plan", [])
    if action_plan:
        lines.append("## H. 执行方案")
        plan_headers = ["日期", "任务", "负责人", "难度"]
        plan_rows = []

        for item in action_plan:
            if isinstance(item, dict):
                plan_rows.append([
                    item.get("day", "-"),
                    item.get("task", "-"),
                    item.get("owner", "-"),
                    item.get("difficulty", "-")
                ])

        if plan_rows:
            plan_table = create_table(plan_headers, plan_rows)
            lines.append(plan_table)
        lines.append("")

    risk_notes = result.get("risk_notes", [])
    if risk_notes:
        lines.append("## I. 风险提示")
        for note in risk_notes:
            lines.append(f"- {note}")
        lines.append("")

    alerts = result.get("alerts", [])
    if alerts:
        lines.append("## J. 预警信息")
        for alert in alerts:
            severity_icon = {
                "info": "ℹ️",
                "warning": "⚠️",
                "critical": "🚨"
            }.get(alert.get("severity", "info"), "ℹ️")

            lines.append(f"{severity_icon} **{alert.get('alert_type', '通知')}**")
            lines.append(f"   - {alert.get('message', '')}")
            if alert.get("recommendation"):
                lines.append(f"   - 建议: {alert['recommendation']}")
        lines.append("")

    next_fields = result.get("next_tracking_fields", [])
    if next_fields:
        lines.append("## K. 下次追踪字段")
        for x in next_fields:
            lines.append(f"- [ ] {x}")
        lines.append("")

    if "footer" in result:
        lines.append("---")
        lines.append(result["footer"])

    return "\n".join(lines)


def render_summary_report(result: Dict[str, Any]) -> str:
    """渲染简洁摘要报告

    Args:
        result: 结果数据字典

    Returns:
        Markdown报告字符串
    """
    lines: List[str] = []
    lines.append("# 儿童图书推荐 - 摘要报告")
    lines.append("")

    summary = generate_summary(result)
    for x in summary:
        lines.append(f"- {x}")
    lines.append("")

    if "statistics" in result:
        stats = result["statistics"]
        if "total_books" in stats:
            lines.append(f"📚 推荐总数: {stats['total_books']}")
        if "avg_educational_value" in stats:
            lines.append(f"📊 平均教育价值: {create_rating_stars(stats['avg_educational_value'])}")

    return "\n".join(lines)


def render_detailed_report(result: Dict[str, Any]) -> str:
    """渲染详细报告（包含可视化）

    Args:
        result: 结果数据字典

    Returns:
        Markdown报告字符串
    """
    report = render_report(result)

    if "trends" in result and result["trends"]:
        report += "\n\n## 趋势图表\n\n"
        for trend in result["trends"]:
            if "data_points" in trend:
                chart = generate_trend_chart(trend["data_points"], trend.get("metric_name", ""))
                report += f"### {trend.get('metric_name', '指标')}\n\n"
                report += "```\n" + chart + "\n```\n\n"

    return report