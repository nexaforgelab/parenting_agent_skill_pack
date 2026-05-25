"""Markdown report renderer for 拼音启蒙 Agent."""
from typing import Any, Dict, List
from datetime import datetime


def create_progress_bar(percentage: float, width: int = 20, filled: str = "█", empty: str = "░") -> str:
    filled_width = int(width * percentage / 100)
    empty_width = width - filled_width
    return f"[{filled * filled_width}{empty * empty_width}] {percentage:.1f}%"


def format_markdown_table(headers: List[str], rows: List[List[str]]) -> str:
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


def create_pinyin_progress(progress_stats: Dict[str, Any]) -> str:
    lines = ["🔤 拼音学习进度"]
    lines.append("")
    total = progress_stats.get("total_pinyin", 0)
    mastered = progress_stats.get("mastered_initial", 0) + progress_stats.get("mastered_final", 0) + progress_stats.get("mastered_compound", 0)
    mastery_rate = progress_stats.get("mastery_rate", 0.0)
    lines.append(f"累计学习 {total} 个拼音，已掌握 {mastered} 个")
    lines.append(f"掌握率: {create_progress_bar(mastery_rate, 20)}")
    lines.append("")
    avg_score = progress_stats.get("average_score", 0.0)
    lines.append(f"⭐ 平均发音得分: {create_progress_bar(avg_score * 10, 20)}")
    lines.append("")
    difficult = progress_stats.get("difficult_pinyin", [])
    if difficult:
        lines.append(f"⚠️ 需要加强的拼音: {', '.join(difficult[:5])}")
    return "\n".join(lines)


def create_recommendations_section(recommendations: List[Dict[str, Any]]) -> str:
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
    lines: List[str] = []
    lines.append("# 🔤 拼音启蒙报告")
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
            plan_rows.append([item.get("day", ""), item.get("task", ""), item.get("owner", ""), item.get("difficulty", "")])
        lines.append(format_markdown_table(plan_headers, plan_rows))
    lines.append("")
    progress_stats = result.get("progress_stats")
    if progress_stats:
        lines.append("## E. 拼音学习进度")
        lines.append(create_pinyin_progress(progress_stats))
        lines.append("")
    recommendations = result.get("recommendations", [])
    if recommendations:
        lines.append("## F. 个性化建议")
        lines.append(create_recommendations_section(recommendations))
        lines.append("")
    pinyin_records = result.get("pinyin_records", [])
    if pinyin_records:
        lines.append("## G. 拼音记录")
        records_data = []
        for record in pinyin_records:
            records_data.append([record.get("pinyin", ""), record.get("pinyin_type", ""), record.get("pronunciation_score", 0.0), record.get("tone_level", 1)])
        lines.append(format_markdown_table(["拼音", "类型", "得分", "声调"], records_data))
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
    lines: List[str] = []
    lines.append("# 拼音启蒙报告")
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