"""Markdown report renderer for 儿童玩具选购 Agent.

提供增强的报告功能：Markdown表格美化、可视化、摘要生成和多格式导出支持。
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
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
        align: 列对齐方式
        style: 表格样式

    Returns:
        Markdown表格字符串
    """
    if not headers:
        return ""

    lines = []
    align_map = {"left": ":---", "center": ":---:", "right": "---:"}

    if align is None:
        align = ["left"] * len(headers)

    header_line = "| " + " | ".join(headers) + " |"
    separator_line = "|" + "|".join([align_map.get(a, ":---") for a in align]) + "|"

    lines.append(header_line)
    lines.append(separator_line)

    for row in rows:
        row_line = "| " + " | ".join(str(cell) for cell in row) + " |"
        lines.append(row_line)

    return "\n".join(lines)


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
        stars += "⭐"
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
        if "total_toys" in stats:
            summary.append(f"共推荐 {stats['total_toys']} 件玩具")
        if "avg_educational_value" in stats:
            summary.append(f"平均教育价值: {stats['avg_educational_value']:.1f}/5")
        if "avg_durability" in stats:
            summary.append(f"平均耐玩性: {stats['avg_durability']:.1f}/5")

    return summary


def generate_toy_list_table(toys: List[Dict[str, Any]]) -> str:
    """生成玩具列表表格

    Args:
        toys: 玩具列表

    Returns:
        Markdown表格字符串
    """
    if not toys:
        return "暂无推荐玩具"

    headers = ["优先级", "玩具名称", "品牌", "分类", "适玩年龄", "教育价值", "耐玩性"]
    rows = []

    for toy in toys:
        priority = toy.get("purchase_priority", "-")
        name = toy.get("name", "-")
        brand = toy.get("brand", "-")
        category = toy.get("category", "-")
        age_range = toy.get("age_range", "-")
        edu_value = toy.get("educational_value", "-")
        durability = toy.get("durability_score", "-")

        if isinstance(edu_value, int):
            edu_value = create_rating_stars(edu_value)
        if isinstance(durability, int):
            durability = create_rating_stars(durability)

        rows.append([
            str(priority),
            name[:25],
            brand[:15],
            category,
            age_range,
            str(edu_value),
            str(durability)
        ])

    return create_table(headers, rows, align=["center", "left", "left", "center", "center", "center", "center"])


def generate_safety_table(toys: List[Dict[str, Any]]) -> str:
    """生成安全信息表格

    Args:
        toys: 玩具列表

    Returns:
        Markdown表格字符串
    """
    if not toys:
        return "暂无玩具安全数据"

    headers = ["玩具名称", "安全评级", "认证", "警告"]
    rows = []

    for toy in toys:
        name = toy.get("name", "-")
        safety = toy.get("safety_rating", "-")
        certs = ", ".join(toy.get("safety_certifications", [])) or "无"
        warnings = ", ".join(toy.get("content_warnings", [])) or "无"

        safety_icon = {
            "age_appropriate": "✅",
            "supervision_required": "⚠️",
            "small_parts_warning": "🔶",
            "choking_hazard": "🚨",
            "electrical_safety": "⚡"
        }.get(safety, "❓")

        rows.append([
            name[:25],
            f"{safety_icon} {safety}",
            certs[:30],
            warnings[:30]
        ])

    return create_table(headers, rows)


def generate_budget_comparison(budget: float, recommendations: List[Dict[str, Any]]) -> str:
    """生成预算比较表格

    Args:
        budget: 预算金额
        recommendations: 推荐列表

    Returns:
        Markdown表格字符串
    """
    if not budget or not recommendations:
        return "暂无预算数据"

    headers = ["玩具名称", "价格区间", "是否在预算内"]
    rows = []

    for toy in recommendations:
        name = toy.get("name", "-")
        price_range = toy.get("price_range", "未知")

        rows.append([name[:25], price_range, "✅ 是" if toy.get("in_budget") else "❌ 否"])

    return create_table(headers, rows)


def generate_trend_chart(data_points: List[Dict[str, Any]], metric: str = "值") -> str:
    """生成趋势图表

    Args:
        data_points: 数据点列表
        metric: 指标名称

    Returns:
        ASCII图表字符串
    """
    if not data_points or len(data_points) < 2:
        return "数据点不足，无法生成趋势图"

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


def render_report(result: Dict[str, Any]) -> str:
    """渲染完整报告

    Args:
        result: 结果数据字典

    Returns:
        Markdown报告字符串
    """
    lines: List[str] = []
    lines.append("# 儿童玩具选购报告")
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
        stats = result["statistics"]
        if stats:
            stats_headers = ["指标", "数值"]
            stats_rows = []
            for key, value in stats.items():
                display_key = {
                    "total_toys": "推荐玩具总数",
                    "avg_educational_value": "平均教育价值",
                    "avg_durability": "平均耐玩性",
                    "avg_engagement": "平均趣味性",
                    "total_usage_records": "使用记录总数"
                }.get(key, key)
                if isinstance(value, float):
                    value = f"{value:.2f}"
                stats_rows.append([display_key, str(value)])
            stats_table = create_table(stats_headers, stats_rows)
            lines.append(stats_table)
        lines.append("")

    if "toys" in result:
        lines.append("## E. 推荐玩具")
        toys_table = generate_toy_list_table(result["toys"])
        lines.append(toys_table)
        lines.append("")

    if "safety_concerns" in result and result["safety_concerns"]:
        lines.append("## F. 安全提示")
        for concern in result["safety_concerns"]:
            lines.append(f"- 🚨 {concern}")
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

    return "\n".join(lines)


def render_summary_report(result: Dict[str, Any]) -> str:
    """渲染简洁摘要报告

    Args:
        result: 结果数据字典

    Returns:
        Markdown报告字符串
    """
    lines: List[str] = []
    lines.append("# 儿童玩具选购 - 摘要报告")
    lines.append("")

    summary = generate_summary(result)
    for x in summary:
        lines.append(f"- {x}")
    lines.append("")

    if "statistics" in result:
        stats = result["statistics"]
        if "total_toys" in stats:
            lines.append(f"🧸 推荐总数: {stats['total_toys']}")
        if "avg_educational_value" in stats:
            lines.append(f"📊 平均教育价值: {create_rating_stars(stats['avg_educational_value'])}")

    return "\n".join(lines)