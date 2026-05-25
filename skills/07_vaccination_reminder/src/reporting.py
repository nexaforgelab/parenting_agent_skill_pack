"""Markdown report renderer for 疫苗接种提醒 Agent.

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
        align: 对齐方式列表

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


def create_calendar_view(year: int, month: int, events: Dict[str, List[str]]) -> str:
    """创建日历视图.

    Args:
        year: 年份
        month: 月份
        events: 日期事件字典

    Returns:
        日历视图字符串
    """
    import calendar

    cal = calendar.Calendar(firstweekday=6)

    lines = []
    lines.append(f"## {year}年{month}月 疫苗接种日历")
    lines.append("")

    week_days = ["日", "一", "二", "三", "四", "五", "六"]
    lines.append("|" + "|".join(["---"] * 7) + "|")
    lines.append("|" + "|".join(week_days) + "|")

    month_days = list(cal.itermonthdays(year, month))

    for week_idx in range(0, len(month_days), 7):
        week = month_days[week_idx:week_idx + 7]
        row = []
        for day in week:
            if day == 0:
                row.append(" ")
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                day_events = events.get(date_str, [])
                if day_events:
                    row.append(f"**{day}**\n" + "\n".join(day_events[:2]))
                else:
                    row.append(str(day))
        lines.append("|" + "|".join(row) + "|")

    return "\n".join(lines)


def create_vaccination_timeline(records: List[Dict[str, Any]]) -> str:
    """创建疫苗接种时间线.

    Args:
        records: 接种记录列表

    Returns:
        时间线视图字符串
    """
    if not records:
        return "暂无接种记录"

    lines = []
    lines.append("### 疫苗接种时间线")
    lines.append("")

    completed = [r for r in records if r.get("actual_date")]
    pending = [r for r in records if not r.get("actual_date")]

    if completed:
        lines.append("✅ **已完成**")
        for record in sorted(completed, key=lambda x: x.get("actual_date", "")):
            lines.append(f"- {record.get('vaccine_name', '未知')} 第{record.get('dose_number', 1)}剂：{record.get('actual_date', '')}")

    if pending:
        lines.append("\n📅 **待接种**")
        for record in sorted(pending, key=lambda x: x.get("scheduled_date", "")):
            lines.append(f"- {record.get('vaccine_name', '未知')} 第{record.get('dose_number', 1)}剂：{record.get('scheduled_date', '')}")

    return "\n".join(lines)


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

    lines.append("# 疫苗接种提醒报告")
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

    if include_charts and "deliverables" in result:
        deliverables = result["deliverables"]

        if "statistics" in deliverables:
            lines.append("### 📊 接种进度")
            lines.append("")
            stats = deliverables["statistics"]
            if "completion_rate" in stats:
                lines.append(f"**完成率**: {create_progress_bar(stats['completion_rate'], 100)}")
                lines.append("")
            if "completed_doses" in stats and "total_doses" in stats:
                lines.append(f"已接种：{stats['completed_doses']} / {stats['total_doses']} 剂")
            lines.append("")

        if "upcoming_vaccines" in deliverables:
            lines.append("### 📅 即将到期")
            lines.append("")
            upcoming = deliverables["upcoming_vaccines"][:5]
            if upcoming:
                headers = ["疫苗", "剂次", "到期日期", "剩余天数"]
                rows = [
                    [
                        v.get("vaccine", ""),
                        str(v.get("dose", 1)),
                        v.get("due_date", ""),
                        str(v.get("days_until", 0))
                    ]
                    for v in upcoming
                ]
                lines.append(format_table(headers, rows))
            else:
                lines.append("暂无即将到期的疫苗")
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
    lines.append("**免责声明**: 本报告仅供参考。疫苗接种时间和方案请以当地卫生部门或儿科医生的建议为准。")

    return "\n".join(lines)


def render_compact_report(result: Dict[str, Any]) -> str:
    """渲染精简报告.

    Args:
        result: 结果字典

    Returns:
        精简的Markdown报告
    """
    lines: List[str] = []

    lines.append("## 疫苗接种提醒")
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

    lines.append("疫苗名称,剂次,应接种日期,实际接种日期,接种机构,批号,孩子反应")

    if "deliverables" in result and "vaccination_records" in result["deliverables"]:
        for record in result["deliverables"]["vaccination_records"]:
            vaccine = record.get("vaccine_name", "").replace(",", ";")
            dose = str(record.get("dose_number", 1))
            scheduled = record.get("scheduled_date", "")
            actual = record.get("actual_date", "")
            location = record.get("location", "").replace(",", ";")
            batch = record.get("batch_number", "")
            side_effects = record.get("side_effects", "").replace(",", ";")
            lines.append(f"{vaccine},{dose},{scheduled},{actual},{location},{batch},{side_effects}")

    return "\n".join(lines)


def render_table_view(result: Dict[str, Any], table_type: str = "vaccination_schedule") -> str:
    """渲染表格视图.

    Args:
        result: 结果字典
        table_type: 表格类型

    Returns:
        格式化的表格字符串
    """
    if table_type == "vaccination_schedule":
        headers = ["疫苗名称", "剂次", "接种月龄", "应接种日期", "实际接种日期", "状态"]
        deliverables = result.get("deliverables", {})
        records = deliverables.get("vaccination_records", [])

        rows = []
        for record in records:
            actual_date = record.get("actual_date", "")
            status = "✅ 已完成" if actual_date else "⏳ 待接种"
            rows.append([
                record.get("vaccine_name", ""),
                str(record.get("dose_number", 1)),
                str(record.get("age_months", "")),
                record.get("scheduled_date", ""),
                actual_date,
                status
            ])

        return format_table(headers, rows, ["left", "center", "center", "center", "center", "center"])

    elif table_type == "action_plan":
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

    return "不支持的表格类型"


def generate_statistics_block(statistics: Dict[str, Any]) -> str:
    """生成统计信息块.

    Args:
        statistics: 统计字典

    Returns:
        Markdown格式的统计块
    """
    lines: List[str] = []

    lines.append("### 📈 接种统计")
    lines.append("")

    lines.append(f"| 指标 | 数值 |")
    lines.append("|:-----|:----:|")

    if "total_doses" in statistics:
        lines.append(f"| 疫苗总数 | {statistics['total_doses']} 剂 |")

    if "completed_doses" in statistics:
        lines.append(f"| 已完成 | {statistics['completed_doses']} 剂 |")

    if "pending_doses" in statistics:
        lines.append(f"| 待接种 | {statistics['pending_doses']} 剂 |")

    if "overdue_doses" in statistics:
        lines.append(f"| 已逾期 | {statistics['overdue_doses']} 剂 |")

    if "completion_rate" in statistics:
        lines.append(f"| 完成率 | {statistics['completion_rate']}% |")

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
                    "疫苗接种时间表请以当地卫生部门的官方指南为准。\n"
                    "如有疑问，请咨询儿科医生或防疫部门。")

    return report + "\n\n---\n\n" + disclaimer
