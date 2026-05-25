"""Markdown report renderer for 睡前故事生成 Agent.

提供增强的报告生成功能，包括图表生成、Markdown表格美化、学习进度可视化和导出格式支持。
"""
from typing import Any, Dict, List, Optional
from datetime import datetime


def create_progress_bar(percentage: float, width: int = 20, filled: str = "█", empty: str = "░") -> str:
    """创建文本进度条"""
    filled_width = int(width * percentage / 100)
    empty_width = width - filled_width
    return f"[{filled * filled_width}{empty * empty_width}] {percentage:.1f}%"


def create_line_chart(data: List[float], labels: List[str], width: int = 40, height: int = 10) -> str:
    """创建简单的文本折线图"""
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


def format_markdown_table(headers: List[str], rows: List[List[str]]) -> str:
    """格式化为 Markdown 表格"""
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


def create_story_summary(stories: List[Dict[str, Any]]) -> str:
    """创建故事摘要"""
    if not stories:
        return "暂无故事记录"

    lines = ["📚 最近故事记录"]
    lines.append("")

    for i, story in enumerate(stories[:5], 1):
        title = story.get("story_title", "未知故事")
        theme = story.get("story_theme", "")
        engagement = story.get("child_engagement", 0.0)

        lines.append(f"{i}. {title}")
        if theme:
            lines.append(f"   🎭 主题: {theme}")
        lines.append(f"   ⭐ 投入度: {create_progress_bar(engagement * 10, 10)}")
        lines.append("")

    return "\n".join(lines)


def create_recommendations_section(recommendations: List[Dict[str, Any]]) -> str:
    """创建推荐建议部分"""
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


def create_storytelling_progress(progress_stats: Dict[str, Any]) -> str:
    """创建讲故事进度可视化"""
    lines = ["📖 讲故事进度概览"]
    lines.append("")

    total_stories = progress_stats.get("total_stories", 0)
    total_minutes = progress_stats.get("total_minutes", 0)
    avg_engagement = progress_stats.get("average_engagement", 0.0)

    lines.append(f"累计讲故事 {total_stories} 次，共 {total_minutes} 分钟")
    lines.append("")

    current_streak = progress_stats.get("current_streak", 0)
    longest_streak = progress_stats.get("longest_streak", 0)
    lines.append(f"🔥 当前连续: {current_streak} 天 | 📈 最长连续: {longest_streak} 天")
    lines.append("")

    lines.append(f"⭐ 平均投入度: {create_progress_bar(avg_engagement * 10, 20)}")
    lines.append("")

    favorite_themes = progress_stats.get("favorite_themes", [])
    if favorite_themes:
        lines.append(f"❤️ 喜欢的主题: {', '.join(favorite_themes[:3])}")
        lines.append("")

    favorite_characters = progress_stats.get("favorite_characters", [])
    if favorite_characters:
        lines.append(f"🌟 喜欢的角色: {', '.join(favorite_characters[:3])}")
        lines.append("")

    return "\n".join(lines)


def export_to_json(data: Dict[str, Any], indent: int = 2) -> str:
    """导出为 JSON 格式"""
    import json
    return json.dumps(data, ensure_ascii=False, indent=indent)


def export_to_csv(headers: List[str], rows: List[List[str]]) -> str:
    """导出为 CSV 格式"""
    import csv
    import io

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)

    return output.getvalue()


def render_report(result: Dict[str, Any]) -> str:
    """渲染完整报告"""
    lines: List[str] = []
    lines.append("# 🌙 睡前故事生成报告")
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
        lines.append("## E. 讲故事进度")
        lines.append(create_storytelling_progress(progress_stats))
        lines.append("")

    recommendations = result.get("recommendations", [])
    if recommendations:
        lines.append("## F. 个性化建议")
        lines.append(create_recommendations_section(recommendations))
        lines.append("")

    story_records = result.get("story_records", [])
    if story_records:
        lines.append("## G. 故事记录")
        records_data = []
        for record in story_records:
            records_data.append([
                record.get("story_title", ""),
                record.get("story_theme", ""),
                record.get("duration_minutes", 0),
                record.get("child_engagement", 0.0)
            ])
        lines.append(format_markdown_table(["故事名", "主题", "时长", "投入度"], records_data))
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


def render_simple_report(result: Dict[str, Any]) -> str:
    """渲染简洁报告"""
    lines: List[str] = []
    lines.append("# 睡前故事生成报告")
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