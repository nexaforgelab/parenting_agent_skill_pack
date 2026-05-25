"""Markdown report renderer for 幼儿英语启蒙 Agent."""
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


def create_english_progress(progress_stats: Dict[str, Any]) -> str:
    lines = ["🇬🇧 英语学习进度"]
    lines.append("")
    total = progress_stats.get("total_words", 0)
    mastered = progress_stats.get("mastered_words", 0)
    mastery_rate = progress_stats.get("mastery_rate", 0.0)
    lines.append(f"累计学习 {total} 个单词，已掌握 {mastered} 个")
    lines.append(f"掌握率: {create_progress_bar(mastery_rate, 20)}")
    lines.append("")
    avg_mastery = progress_stats.get("average_mastery", 0.0)
    lines.append(f"⭐ 平均掌握度: {create_progress_bar(avg_mastery * 10, 20)}")
    lines.append("")
    difficult = progress_stats.get("difficult_words", [])
    if difficult:
        lines.append(f"⚠️ 需要加强的单词: {', '.join(difficult[:5])}")
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
    lines.append("# 🇬🇧 幼儿英语启蒙报告")
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
        lines.append("## E. 英语学习进度")
        lines.append(create_english_progress(progress_stats))
        lines.append("")
    recommendations = result.get("recommendations", [])
    if recommendations:
        lines.append("## F. 个性化建议")
        lines.append(create_recommendations_section(recommendations))
        lines.append("")
    vocab_records = result.get("vocab_records", [])
    if vocab_records:
        lines.append("## G. 词汇记录")
        records_data = []
        for record in vocab_records:
            records_data.append([record.get("word", ""), record.get("translation", ""), record.get("category", ""), record.get("mastery_score", 0.0)])
        lines.append(format_markdown_table(["单词", "翻译", "类别", "掌握度"], records_data))
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
    lines.append("# 幼儿英语启蒙报告")
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