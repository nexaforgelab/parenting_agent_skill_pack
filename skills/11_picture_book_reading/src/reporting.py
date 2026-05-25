"""Markdown report renderer for 绘本共读 Agent.

提供增强的报告生成功能，包括图表生成、Markdown表格美化、学习进度可视化和导出格式支持。
"""
from typing import Any, Dict, List, Optional
from datetime import datetime


def create_progress_bar(percentage: float, width: int = 20, filled: str = "█", empty: str = "░") -> str:
    """创建文本进度条

    Args:
        percentage: 进度百分比 (0-100)
        width: 进度条总宽度
        filled: 填充字符
        empty: 空字符

    Returns:
        进度条字符串
    """
    filled_width = int(width * percentage / 100)
    empty_width = width - filled_width
    return f"[{filled * filled_width}{empty * empty_width}] {percentage:.1f}%"


def create_line_chart(data: List[float], labels: List[str], width: int = 40, height: int = 10) -> str:
    """创建简单的文本折线图

    Args:
        data: 数据点列表
        labels: 标签列表
        width: 图表宽度
        height: 图表高度
        labels: 标签列表

    Returns:
        文本图表字符串
    """
    if not data:
        return "无数据"

    min_val = min(data)
    max_val = max(data)
    value_range = max_val - min_val if max_val != min_val else 1

    grid = [[" " for _ in range(width)] for _ in range(height)]

    for i, value in enumerate(data):
        x = min(int((i / max(len(data) - 1, 1)) * (width - 1)), width - 1)
        y = min(int(((value - min_val) / value_range) * (height - 1)), height - 1)
        grid[height - 1 - y][x] = "●"

    lines = []
    for row in grid:
        lines.append("|" + "".join(row) + "|")

    return "\n".join(lines)


def create_table_row(columns: List[str], widths: List[int], separator: str = "│") -> str:
    """创建美化的表格行

    Args:
        columns: 列内容列表
        widths: 每列宽度列表
        separator: 分隔符

    Returns:
        格式化后的行字符串
    """
    formatted_cols = []
    for col, width in zip(columns, widths):
        col_str = str(col)
        if len(col_str) > width:
            col_str = col_str[:width - 2] + ".."
        formatted_cols.append(col_str.center(width))
    return separator + separator.join(formatted_cols) + separator


def create_table_header(columns: List[str], widths: List[int]) -> str:
    """创建美化的表格表头

    Args:
        columns: 列名列表
        widths: 每列宽度列表

    Returns:
        格式化后的表头字符串
    """
    header = create_table_row(columns, widths)
    separator_parts = []
    for width in widths:
        separator_parts.append("─" * width)
    separator_line = "┼".join(["┼".join(["─" * w]) for w in widths])
    return header + "\n" + create_table_row(separator_parts, widths, "+").replace("+", "┼", 1).replace("+", "┼")


def format_markdown_table(headers: List[str], rows: List[List[str]]) -> str:
    """格式化为 Markdown 表格

    Args:
        headers: 表头列表
        rows: 行数据列表

    Returns:
        Markdown 格式的表格字符串
    """
    if not headers:
        return ""

    lines = []
    col_count = len(headers)
    widths = [len(h) for h in headers]

    for row in rows:
        for i, cell in enumerate(row):
            if i < col_count:
                widths[i] = max(widths[i], len(str(cell)))

    header_line = "| " + " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers)) + " |"
    separator_line = "| " + " | ".join("─" * widths[i] for i in range(col_count)) + " |"

    lines.append(header_line)
    lines.append(separator_line)

    for row in rows:
        row_cells = [str(cell) for cell in row]
        while len(row_cells) < col_count:
            row_cells.append("")
        row_line = "| " + " | ".join(row_cells[i].ljust(widths[i]) for i in range(col_count)) + " |"
        lines.append(row_line)

    return "\n".join(lines)


def format_statistics_box(title: str, stats: Dict[str, Any]) -> str:
    """格式化统计信息框

    Args:
        title: 标题
        stats: 统计信息字典

    Returns:
        格式化的统计信息字符串
    """
    lines = [f"📊 {title}"]
    lines.append("─" * 30)

    for key, value in stats.items():
        if isinstance(value, float):
            lines.append(f"  {key}: {value:.2f}")
        elif isinstance(value, int):
            lines.append(f"  {key}: {value}")
        elif isinstance(value, list):
            lines.append(f"  {key}: {', '.join(str(v) for v in value) if value else '无'}")
        else:
            lines.append(f"  {key}: {value}")

    lines.append("─" * 30)
    return "\n".join(lines)


def create_session_summary(sessions: List[Dict[str, Any]]) -> str:
    """创建学习会话摘要

    Args:
        sessions: 学习会话列表

    Returns:
        格式化的会话摘要字符串
    """
    if not sessions:
        return "暂无学习记录"

    lines = ["📚 最近学习记录"]
    lines.append("")

    for i, session in enumerate(sessions[:5], 1):
        book = session.get("book_title", "未知书籍")
        date = session.get("timestamp", "")
        engagement = session.get("engagement_score", 0.0)

        lines.append(f"{i}. {book}")
        if date:
            lines.append(f"   📅 {date}")
        lines.append(f"   ⭐ 投入度: {create_progress_bar(engagement * 10, 10)}")
        lines.append("")

    return "\n".join(lines)


def create_recommendations_section(recommendations: List[Dict[str, Any]]) -> str:
    """创建推荐建议部分

    Args:
        recommendations: 推荐列表

    Returns:
        格式化的推荐建议字符串
    """
    if not recommendations:
        return "暂无个性化建议"

    lines = ["💡 个性化建议"]
    lines.append("")

    priority_icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}

    for i, rec in enumerate(recommendations, 1):
        priority = rec.get("priority", "medium")
        icon = priority_icons.get(priority, "⚪")
        title = rec.get("title", "建议")
        description = rec.get("description", "")

        lines.append(f"{i}. {icon} {title}")
        if description:
            lines.append(f"   {description}")

        action_items = rec.get("action_items", [])
        if action_items:
            lines.append("   📋 执行建议:")
            for action in action_items:
                lines.append(f"      - {action}")

        lines.append("")

    return "\n".join(lines)


def create_progress_visualization(progress_stats: Dict[str, Any]) -> str:
    """创建进度可视化展示

    Args:
        progress_stats: 进度统计数据

    Returns:
        格式化的进度可视化字符串
    """
    lines = ["📈 学习进度概览"]
    lines.append("")

    total_sessions = progress_stats.get("total_sessions", 0)
    total_minutes = progress_stats.get("total_minutes", 0)
    total_books = progress_stats.get("total_books_read", 0)

    lines.append(f"累计学习 {total_sessions} 次，共 {total_minutes} 分钟，阅读 {total_books} 本绘本")
    lines.append("")

    current_streak = progress_stats.get("current_streak", 0)
    longest_streak = progress_stats.get("longest_streak", 0)
    lines.append(f"🔥 当前连续: {current_streak} 天 | 📈 最长连续: {longest_streak} 天")
    lines.append("")

    average_engagement = progress_stats.get("average_engagement", 0.0)
    lines.append(f"⭐ 平均投入度: {create_progress_bar(average_engagement * 10, 20)}")
    lines.append("")

    overall_mastery = progress_stats.get("overall_mastery", 0.0)
    if overall_mastery > 0:
        lines.append(f"📊 整体掌握度: {create_progress_bar(overall_mastery, 20)}")
        lines.append("")

    favorite_topics = progress_stats.get("favorite_topics", [])
    if favorite_topics:
        lines.append(f"❤️ 最喜欢的主题: {', '.join(favorite_topics[:3])}")
        lines.append("")

    difficult_topics = progress_stats.get("difficult_topics", [])
    if difficult_topics:
        lines.append(f"📚 需要加强的主题: {', '.join(difficult_topics[:3])}")
        lines.append("")

    return "\n".join(lines)


def create_weekly_summary_table(weekly_data: List[Dict[str, Any]]) -> str:
    """创建周报汇总表格

    Args:
        weekly_data: 周报数据列表

    Returns:
        Markdown 格式的周报表格
    """
    if not weekly_data:
        return "暂无周报数据"

    headers = ["周次", "学习次数", "分钟数", "绘本数", "平均投入度", "变化"]
    rows = []

    for week in weekly_data:
        week_num = week.get("week", "-")
        sessions = week.get("sessions", 0)
        minutes = week.get("minutes", 0)
        books = week.get("books", 0)
        engagement = week.get("engagement", 0.0)
        change = week.get("change", "0%")

        engagement_display = f"{engagement:.1f}/10"
        rows.append([week_num, sessions, minutes, books, engagement_display, change])

    return format_markdown_table(headers, rows)


def export_to_json(data: Dict[str, Any], indent: int = 2) -> str:
    """导出为 JSON 格式

    Args:
        data: 要导出的数据
        indent: 缩进空格数

    Returns:
        JSON 格式字符串
    """
    import json
    return json.dumps(data, ensure_ascii=False, indent=indent)


def export_to_csv(headers: List[str], rows: List[List[str]]) -> str:
    """导出为 CSV 格式

    Args:
        headers: 表头列表
        rows: 行数据列表

    Returns:
        CSV 格式字符串
    """
    import csv
    import io

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)

    return output.getvalue()


def render_report(result: Dict[str, Any]) -> str:
    """渲染完整报告

    Args:
        result: 报告数据字典

    Returns:
        Markdown 格式的报告字符串
    """
    lines: List[str] = []
    lines.append("# 📖 绘本共读报告")
    lines.append("")
    lines.append(f"📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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
    action_plan = result.get("action_plan", [])
    if action_plan:
        plan_headers = ["日期", "任务", "负责人", "难度"]
        plan_rows = []
        for item in action_plan:
            plan_rows.append([
                item.get("day", ""),
                item.get("task", ""),
                item.get("owner", ""),
                item.get("difficulty", "")
            ])
        lines.append(format_markdown_table(plan_headers, plan_rows))
    lines.append("")

    progress_stats = result.get("progress_stats")
    if progress_stats:
        lines.append("## E. 学习进度")
        lines.append(create_progress_visualization(progress_stats))
        lines.append("")

    recommendations = result.get("recommendations", [])
    if recommendations:
        lines.append("## F. 个性化建议")
        lines.append(create_recommendations_section(recommendations))
        lines.append("")

    learning_records = result.get("learning_records", [])
    if learning_records:
        lines.append("## G. 学习记录")
        records_data = []
        for record in learning_records:
            records_data.append([
                record.get("book_title", ""),
                record.get("duration_minutes", 0),
                record.get("engagement_score", 0.0),
                record.get("comprehension_level", "")
            ])
        lines.append(format_markdown_table(["绘本", "时长(分钟)", "投入度", "理解程度"], records_data))
        lines.append("")

    lines.append("## H. 风险与人工核验")
    for x in result.get("risk_notes", []):
        lines.append(f"- {x}")
    lines.append("")

    lines.append("## I. 下次追踪字段")
    for x in result.get("next_tracking_fields", []):
        lines.append(f"- {x}")
    lines.append("")

    deliverables = result.get("deliverables", {})
    if deliverables:
        lines.append("## J. 交付物清单")
        required = deliverables.get("required", [])
        if required:
            lines.append("### 必需交付物")
            for item in required:
                lines.append(f"- [ ] {item}")
            lines.append("")
        tables = deliverables.get("tables", {})
        if tables:
            lines.append("### 表格模板")
            for table_name, columns in tables.items():
                lines.append(f"**{table_name}**: {', '.join(columns)}")
            lines.append("")
        templates = deliverables.get("templates", {})
        if templates:
            lines.append("### 记录模板")
            for template_name, template in templates.items():
                lines.append(f"**{template_name}**:")
                lines.append(f"```\n{template}\n```")
                lines.append("")

    return "\n".join(lines)


def render_simple_report(result: Dict[str, Any]) -> str:
    """渲染简洁报告

    Args:
        result: 报告数据字典

    Returns:
        Markdown 格式的简洁报告字符串
    """
    lines: List[str] = []
    lines.append("# 绘本共读报告")
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
    lines.append("## E. 风险与人工核验")
    for x in result.get("risk_notes", []):
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## F. 下次追踪字段")
    for x in result.get("next_tracking_fields", []):
        lines.append(f"- {x}")
    return "\n".join(lines)