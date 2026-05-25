"""Markdown report renderer for 月龄发育里程碑 Agent.

提供美化的Markdown表格、趋势可视化（ASCII art）、摘要生成和多格式导出功能。
"""
from typing import Any, Dict, List, Optional
import json
from datetime import datetime


def format_table(headers: List[str], rows: List[List[str]],
                align: Optional[List[str]] = None) -> str:
    """格式化Markdown表格.

    Args:
        headers: 表头列表
        rows: 行数据列表
        align: 对齐方式列表 (left, center, right)

    Returns:
        格式化的Markdown表格字符串
    """
    if not headers or not rows:
        return ""

    col_widths = [len(h) for h in headers]

    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    if align is None:
        align = ["left"] * len(headers)

    align_map = {"left": ":--", "center": ":--:", "right": "--:"}
    separator = "| " + " | ".join(
        align_map.get(a, ":--").replace("-", "-" * w)
        for a, w in zip(align, col_widths)
    ) + " |"

    header_line = "| " + " | ".join(
        h.ljust(col_widths[i]) for i, h in enumerate(headers)
    ) + " |"

    data_lines = []
    for row in rows:
        line = "| " + " | ".join(
            str(cell).ljust(col_widths[i]) if a == "left"
            else str(cell).rjust(col_widths[i]) if a == "right"
            else str(cell).center(col_widths[i])
            for i, (cell, a) in enumerate(zip(row, align))
        ) + " |"
        data_lines.append(line)

    return "\n".join([header_line, separator] + data_lines)


def create_progress_bar(value: float, max_value: float = 100,
                       width: int = 20, filled_char: str = "█",
                       empty_char: str = "░") -> str:
    """创建ASCII进度条.

    Args:
        value: 当前值
        max_value: 最大值
        width: 进度条宽度
        filled_char: 填充字符
        empty_char: 空字符

    Returns:
        进度条字符串
    """
    percentage = min(value / max_value, 1.0) if max_value > 0 else 0
    filled = int(width * percentage)
    empty = width - filled

    bar = filled_char * filled + empty_char * empty

    percentage_str = f"{percentage * 100:.1f}%"
    return f"[{bar}] {percentage_str}"


def create_trend_chart(values: List[float], labels: Optional[List[str]] = None,
                     height: int = 6, width: int = 40) -> str:
    """创建ASCII趋势图表.

    Args:
        values: 数值列表
        labels: 标签列表
        height: 图表高度
        width: 图表宽度

    Returns:
        ASCII趋势图表字符串
    """
    if not values:
        return "无数据"

    min_val = min(values)
    max_val = max(values)
    value_range = max_val - min_val if max_val != min_val else 1

    rows: List[List[str]] = [[" " for _ in range(width)] for _ in range(height)]

    for i in range(width):
        value_idx = int(i * len(values) / width) if width > 0 else 0
        value_idx = min(value_idx, len(values) - 1)
        value = values[value_idx]

        normalized = (value - min_val) / value_range if value_range > 0 else 0
        y_pos = int((height - 1) * (1 - normalized))
        y_pos = max(0, min(height - 1, y_pos))

        rows[y_pos][i] = "●"

    chart_lines = []
    for row in rows:
        chart_lines.append("│" + "".join(row) + "│")

    chart_lines.append("└" + "─" * width + "┘")

    if labels and len(labels) > 0:
        step = max(1, len(labels) // (width // 8))
        x_labels = labels[::step][:width // 8]
        label_str = " " + "".join(l.ljust(8)[:8] for l in x_labels[:width // 8])
        chart_lines.append(label_str[:width + 1])

    return "\n".join(chart_lines)


def create_comparison_chart(value1: float, value2: float,
                           label1: str = "本周", label2: str = "上周",
                           max_value: Optional[float] = None) -> str:
    """创建对比柱状图.

    Args:
        value1: 第一个值
        value2: 第二个值
        label1: 第一个标签
        label2: 第二个标签
        max_value: 最大值（用于归一化）

    Returns:
        ASCII柱状图字符串
    """
    if max_value is None:
        max_value = max(value1, value2) * 1.2

    height = 8
    bars = []

    for h in range(height, -1, -1):
        threshold = (h / height) * max_value
        bar1 = "███" if value1 >= threshold else "   "
        bar2 = "███" if value2 >= threshold else "   "
        bars.append(f"{bar1}  {bar2}")

    chart = "\n".join(bars)
    chart += f"\n{label1} {value1:.1f}  {label2} {value2:.1f}"

    return chart


def generate_summary(result: Dict[str, Any]) -> str:
    """生成报告摘要.

    Args:
        result: 结果字典

    Returns:
        摘要文本
    """
    summary_points = result.get("summary", [])

    if not summary_points:
        return "暂无摘要信息"

    summary_text = "📋 **报告摘要**\n\n"
    for i, point in enumerate(summary_points[:5], 1):
        summary_text += f"{i}. {point}\n"

    if len(summary_points) > 5:
        summary_text += f"\n... 还有 {len(summary_points) - 5} 项内容\n"

    return summary_text


def render_report(result: Dict[str, Any], include_charts: bool = True) -> str:
    """渲染完整报告.

    Args:
        result: 结果字典
        include_charts: 是否包含图表

    Returns:
        Markdown格式的报告字符串
    """
    lines: List[str] = []

    lines.append("# 月龄发育里程碑报告")
    lines.append("")
    lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    lines.append("## A. 本次结论")
    lines.append("")
    for x in result.get("summary", []):
        lines.append(f"- {x}")
    lines.append("")

    lines.append("## B. 已知信息")
    lines.append("")
    for x in result.get("known_facts", []):
        lines.append(f"- {x}")
    lines.append("")

    lines.append("## C. 分析与判断")
    lines.append("")
    for x in result.get("analysis", []):
        lines.append(f"- {x}")
    lines.append("")

    if include_charts and "statistics" in result.get("deliverables", {}):
        lines.append("### 📊 数据可视化")
        lines.append("")
        stats = result["deliverables"]["statistics"]
        if "achievement_rate" in stats:
            lines.append(f"**达成率**: {create_progress_bar(stats['achievement_rate'], 100)}")
            lines.append("")

        if "category_breakdown" in stats:
            lines.append("**类别分布**:")
            lines.append("")
            breakdown = stats["category_breakdown"]
            for category, data in breakdown.items():
                achieved = data.get("achieved", 0)
                total = achieved + data.get("pending", 0)
                rate = (achieved / total * 100) if total > 0 else 0
                lines.append(f"- {category}: {create_progress_bar(rate, 100, 15)}")
            lines.append("")

    lines.append("## D. 执行方案")
    lines.append("")
    lines.append("| 阶段 | 任务 | 负责人 | 记录要求 | 难度 |")
    lines.append("|:----:|:-----|:------:|:--------|:----:|")

    for item in result.get("action_plan", []):
        day = item.get('day', '')
        task = item.get('task', '')
        owner = item.get('owner', '家长')
        evidence = item.get('evidence_to_record', '')
        difficulty = item.get('difficulty', '低')

        task_short = task[:30] + "..." if len(task) > 30 else task
        evidence_short = evidence[:20] + "..." if len(evidence) > 20 else evidence

        lines.append(f"| {day} | {task_short} | {owner} | {evidence_short} | {difficulty} |")
    lines.append("")

    lines.append("## E. 风险与人工核验")
    lines.append("")
    for x in result.get("risk_notes", []):
        lines.append(f"- ⚠️ {x}")
    lines.append("")

    lines.append("## F. 下次追踪字段")
    lines.append("")
    for x in result.get("next_tracking_fields", []):
        lines.append(f"- [ ] {x}")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("**免责声明**: 本报告仅供参考，不构成医疗建议。如有疑虑，请咨询专业儿科医生。")

    return "\n".join(lines)


def render_compact_report(result: Dict[str, Any]) -> str:
    """渲染精简报告.

    Args:
        result: 结果字典

    Returns:
        精简的Markdown报告
    """
    lines: List[str] = []

    lines.append("## 月龄发育里程碑")
    lines.append("")
    lines.append("### 摘要")
    for x in result.get("summary", [])[:3]:
        lines.append(f"- {x}")
    lines.append("")

    lines.append("### 行动计划")
    for item in result.get("action_plan", [])[:3]:
        lines.append(f"- [{item.get('day', 'D0')}] {item.get('task', '')[:50]}")

    return "\n".join(lines)


def export_to_json(result: Dict[str, Any], indent: int = 2) -> str:
    """导出为JSON格式.

    Args:
        result: 结果字典
        indent: 缩进空格数

    Returns:
        JSON格式字符串
    """
    return json.dumps(result, ensure_ascii=False, indent=indent)


def export_to_csv(result: Dict[str, Any]) -> str:
    """导出为CSV格式.

    Args:
        result: 结果字典

    Returns:
        CSV格式字符串
    """
    lines: List[str] = []

    lines.append("类别,日期,任务,状态,备注")

    for item in result.get("action_plan", []):
        category = "行动计划"
        date = item.get('day', '')
        task = item.get('task', '').replace(',', ';')
        status = item.get('difficulty', '低')
        notes = item.get('evidence_to_record', '').replace(',', ';')
        lines.append(f"{category},{date},{task},{status},{notes}")

    for note in result.get("risk_notes", []):
        lines.append(f"风险提示,,,{note},")

    return "\n".join(lines)


def render_table_view(result: Dict[str, Any], table_type: str = "action_plan") -> str:
    """渲染表格视图.

    Args:
        result: 结果字典
        table_type: 表格类型 (action_plan, timeline, milestone_tracking)

    Returns:
        格式化的表格字符串
    """
    if table_type == "action_plan":
        headers = ["阶段", "任务", "负责人", "难度"]
        rows = [
            [
                item.get('day', ''),
                item.get('task', ''),
                item.get('owner', '家长'),
                item.get('difficulty', '低')
            ]
            for item in result.get("action_plan", [])
        ]
        return format_table(headers, rows, ["center", "left", "center", "center"])

    elif table_type == "timeline":
        headers = ["时间", "事件", "输入", "处理", "结果", "备注"]
        rows = result.get("deliverables", {}).get("tables", {}).get("timeline", [])
        return format_table(headers, rows)

    elif table_type == "milestone_tracking":
        headers = ["里程碑", "类别", "预期月龄", "实际月龄", "状态"]
        rows = result.get("deliverables", {}).get("tables", {}).get("milestone_tracking", [])
        return format_table(headers, rows)

    return "不支持的表格类型"


def generate_statistics_block(statistics: Dict[str, Any]) -> str:
    """生成统计信息块.

    Args:
        statistics: 统计字典

    Returns:
        Markdown格式的统计块
    """
    lines: List[str] = []

    lines.append("### 📈 统计概览")
    lines.append("")

    lines.append(f"| 指标 | 数值 |")
    lines.append("|:-----|:----:|")

    if "total_entries" in statistics:
        lines.append(f"| 记录总数 | {statistics['total_entries']} |")

    if "achievement_rate" in statistics:
        lines.append(f"| 达成率 | {statistics['achievement_rate']}% |")

    if "average_entries_per_day" in statistics:
        lines.append(f"| 日均记录 | {statistics['average_entries_per_day']:.2f} |")

    if "most_active_category" in statistics:
        lines.append(f"| 最活跃类别 | {statistics['most_active_category']} |")

    lines.append("")

    if "category_distribution" in statistics:
        lines.append("**类别分布**:")
        lines.append("")
        for cat, count in statistics["category_distribution"].items():
            lines.append(f"- {cat}: {count} 条")

    return "\n".join(lines)


def add_footer(report: str, disclaimer: str = "") -> str:
    """为报告添加页脚.

    Args:
        report: 报告内容
        disclaimer: 免责声明

    Returns:
        添加页脚后的报告
    """
    if not disclaimer:
        disclaimer = ("**免责声明**: 本报告由 AI 生成，仅供参考。\n"
                    "不构成医疗建议、诊断或治疗方案。\n"
                    "如有健康疑虑，请及时咨询专业儿科医生。")

    return report + "\n\n---\n\n" + disclaimer
