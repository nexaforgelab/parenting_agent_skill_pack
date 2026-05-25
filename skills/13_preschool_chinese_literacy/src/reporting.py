"""Markdown report renderer for 幼儿识字启蒙 Agent."""
from typing import Any, Dict, List
from datetime import datetime


def create_progress_bar(percentage: float, width: int = 20, filled: str = "█", empty: str = "░") -> str:
    """创建文本进度条"""
    filled_width = int(width * percentage / 100)
    empty_width = width - filled_width
    return f"[{filled * filled_width}{empty * empty_width}] {percentage:.1f}%"


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


def create_literacy_progress(progress_stats: Dict[str, Any]) -> str:
    """创建识字进度可视化"""
    lines = ["📚 识字进度概览"]
    lines.append("")
    total_chars = progress_stats.get("total_characters", 0)
    mastered_chars = progress_stats.get("mastered_characters", 0)
    mastery_rate = progress_stats.get("mastery_rate", 0.0)
    lines.append(f"累计识字 {total_chars} 个，已掌握 {mastered_chars} 个")
    lines.append(f"掌握率: {create_progress_bar(mastery_rate, 20)}")
    lines.append("")
    current_streak = progress_stats.get("current_streak", 0)
    longest_streak = progress_stats.get("longest_streak", 0)
    lines.append(f"🔥 当前连续: {current_streak} 天 | 📈 最长连续: {longest_streak} 天")
    lines.append("")
    difficult_chars = progress_stats.get("difficult_characters", [])
    if difficult_chars:
        lines.append(f"⚠️ 需要加强的汉字: {', '.join(difficult_chars[:5])}")
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
        lines.append("")
    return "\n".join(lines)


def render_report(result: Dict[str, Any]) -> str:
    """渲染完整报告"""
    lines: List[str] = []
    lines.append("# ✍️ 幼儿识字启蒙报告")
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
        lines.append("## E. 识字进度")
        lines.append(create_literacy_progress(progress_stats))
        lines.append("")
    recommendations = result.get("recommendations", [])
    if recommendations:
        lines.append("## F. 个性化建议")
        lines.append(create_recommendations_section(recommendations))
        lines.append("")
    character_records = result.get("character_records", [])
    if character_records:
        lines.append("## G. 识字记录")
        records_data = []
        for record in character_records:
            records_data.append([
                record.get("character", ""),
                record.get("pinyin", ""),
                record.get("learning_stage", ""),
                record.get("correct_count", 0),
                record.get("practice_count", 0)
            ])
        lines.append(format_markdown_table(["汉字", "拼音", "阶段", "正确", "练习"], records_data))
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
    lines.append("# 幼儿识字启蒙报告")
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