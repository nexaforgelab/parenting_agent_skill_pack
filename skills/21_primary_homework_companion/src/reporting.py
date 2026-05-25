"""Markdown report renderer for 小学作业陪伴 Agent.

提供图表生成、表格美化、进度可视化和摘要生成功能。
"""
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    from .models import ProgressStats, Recommendation, SessionContext
    from .planner import analyze_learning_progress, detect_learning_anomalies
except ImportError:
    from models import ProgressStats, Recommendation, SessionContext
    from planner import analyze_learning_progress, detect_learning_anomalies


def render_report(result: Dict[str, Any]) -> str:
    """渲染完整报告

    Args:
        result: 结果字典

    Returns:
        Markdown格式的报告
    """
    lines: List[str] = []
    lines.append("# 小学作业陪伴报告")
    lines.append("")
    lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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

    if result.get("progress_stats"):
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(generate_progress_visualization(result["progress_stats"]))

    if result.get("recommendations"):
        lines.append("")
        lines.append(generate_recommendations_table(result["recommendations"]))

    if result.get("session_context"):
        lines.append("")
        lines.append(generate_session_summary(result["session_context"]))

    return "\n".join(lines)


def generate_progress_visualization(progress_stats: Dict[str, Any]) -> str:
    """生成学习进度可视化图表(文本格式)

    Args:
        progress_stats: 进度统计数据

    Returns:
        可视化Markdown文本
    """
    lines = []
    lines.append("### 📊 学习进度概览")
    lines.append("")

    total = progress_stats.get("total_homework_count", 0)
    completed = progress_stats.get("completed_count", 0)
    completion_rate = progress_stats.get("average_completion_rate", 0)
    avg_duration = progress_stats.get("average_duration", 0)
    motivation = progress_stats.get("motivation_score", 0)
    improvement = progress_stats.get("weekly_improvement", 0)

    lines.append("#### 完成情况")
    lines.append("```")
    bar_width = 30
    filled = int((completed / total * bar_width) if total > 0 else 0)
    bar = "█" * filled + "░" * (bar_width - filled)
    lines.append(f"完成进度: [{bar}] {completed}/{total} ({completed/total*100:.1f}%)" if total > 0 else "暂无数据")
    lines.append("```")
    lines.append("")

    lines.append("#### 关键指标")
    lines.append("")
    metrics = [
        ("平均完成率", f"{completion_rate:.1f}%"),
        ("平均用时", f"{avg_duration:.1f}分钟"),
        ("学习动机", f"{motivation:.1f}分"),
        ("本周进步", f"{improvement:+.1f}%")
    ]

    max_label_len = max(len(m[0]) for m in metrics)
    for label, value in metrics:
        padding = " " * (max_label_len - len(label))
        lines.append(f"- {label}{padding} : {value}")
    lines.append("")

    subjects_mastered = progress_stats.get("subjects_mastered", [])
    subjects_needing_work = progress_stats.get("subjects_needing_work", [])

    if subjects_mastered:
        lines.append("#### ✅ 已掌握科目")
        lines.append(f"- {', '.join(subjects_mastered)}")
        lines.append("")

    if subjects_needing_work:
        lines.append("#### ⚠️ 需要加强科目")
        lines.append(f"- {', '.join(subjects_needing_work)}")
        lines.append("")

    return "\n".join(lines)


def generate_text_bar_chart(data: Dict[str, float], title: str = "数据分布", width: int = 20) -> str:
    """生成文本条形图

    Args:
        data: 数据字典 {标签: 数值}
        title: 图表标题
        width: 条形图最大宽度

    Returns:
        文本条形图
    """
    lines = [f"**{title}**", ""]
    lines.append("```")

    if not data:
        lines.append("暂无数据")
    else:
        max_value = max(data.values()) if data else 1
        for label, value in data.items():
            bar_length = int((value / max_value * width)) if max_value > 0 else 0
            bar = "█" * bar_length
            percentage = value / max_value * 100 if max_value > 0 else 0
            lines.append(f"{label:12s} │{bar} {percentage:5.1f}%")

    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def generate_table(headers: List[str], rows: List[List[str]], align: Optional[List[str]] = None) -> str:
    """生成Markdown表格

    Args:
        headers: 表头列表
        rows: 行数据列表
        align: 对齐方式列表 ('l', 'c', 'r')

    Returns:
        Markdown表格
    """
    if not headers or not rows:
        return ""

    lines = []

    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    def format_row(cells: List[str], separator: str) -> str:
        formatted = []
        for i, cell in enumerate(cells):
            width = col_widths[i]
            cell_str = str(cell)
            if align and i < len(align):
                if align[i] == 'r':
                    formatted.append(cell_str.rjust(width))
                elif align[i] == 'c':
                    formatted.append(cell_str.center(width))
                else:
                    formatted.append(cell_str.ljust(width))
            else:
                formatted.append(cell_str.ljust(width))
        return separator.join(formatted)

    lines.append(format_row(headers, " | "))
    lines.append(format_row(["---"] * len(headers), "-|-"))

    for row in rows:
        lines.append(format_row(row, " | "))

    return "\n".join(lines)


def generate_recommendations_table(recommendations: List[Dict[str, Any]]) -> str:
    """生成个性化推荐表格

    Args:
        recommendations: 推荐列表

    Returns:
        Markdown格式推荐表格
    """
    lines = []
    lines.append("### 💡 个性化推荐")
    lines.append("")

    if not recommendations:
        lines.append("暂无推荐")
        return "\n".join(lines)

    headers = ["优先级", "类别", "建议标题", "置信度", "建议时长"]
    rows = []
    for rec in recommendations:
        rows.append([
            rec.get("priority", "未知"),
            rec.get("category", "未知"),
            rec.get("title", ""),
            f"{rec.get('confidence_score', 0) * 100:.0f}%",
            f"{rec.get('suggested_duration', 0)}分钟"
        ])

    priority_order = {"高": 0, "中": 1, "低": 2, "紧急": -1}
    rows.sort(key=lambda x: priority_order.get(x[0], 99))

    lines.append(generate_table(headers, rows, ['c', 'c', 'l', 'c', 'c']))
    lines.append("")

    lines.append("#### 详细建议")
    lines.append("")
    for i, rec in enumerate(recommendations, 1):
        lines.append(f"**{i}. {rec.get('title', '无标题')}**")
        lines.append(f"- 类别: {rec.get('category', '未知')}")
        lines.append(f"- 描述: {rec.get('description', '暂无描述')}")
        if rec.get("suggestion"):
            lines.append(f"- 具体建议: {rec.get('suggestion')}")
        lines.append("")

    return "\n".join(lines)


def generate_session_summary(session_context: Dict[str, Any]) -> str:
    """生成会话摘要

    Args:
        session_context: 会话上下文

    Returns:
        Markdown格式会话摘要
    """
    lines = []
    lines.append("### 📝 会话摘要")
    lines.append("")

    lines.append(f"- **会话ID**: {session_context.get('session_id', '未知')}")
    lines.append(f"- **孩子**: {session_context.get('child_id', '未知')}")
    lines.append(f"- **年级**: {session_context.get('grade_level', 1)}年级")
    lines.append(f"- **当前科目**: {session_context.get('current_subject', '未指定')}")
    lines.append(f"- **对话轮数**: {len(session_context.get('conversation_history', []))}")
    lines.append(f"- **表现记录**: {len(session_context.get('recent_performance', []))}条")
    lines.append("")

    recent = session_context.get('conversation_history', [])[-3:]
    if recent:
        lines.append("#### 最近对话")
        for i, conv in enumerate(recent, 1):
            role = "👤" if conv.get('role') == 'user' else "🤖"
            content = conv.get('content', '')[:50]
            lines.append(f"{i}. {role} {content}...")
        lines.append("")

    return "\n".join(lines)


def generate_summary_section(result: Dict[str, Any]) -> str:
    """生成摘要部分

    Args:
        result: 结果字典

    Returns:
        Markdown格式摘要
    """
    lines = []
    lines.append("### 📋 执行摘要")
    lines.append("")

    key_points = result.get("summary", [])
    if key_points:
        lines.append("**核心发现**:")
        for point in key_points:
            lines.append(f"- {point}")
        lines.append("")

    action_plan = result.get("action_plan", [])
    if action_plan:
        lines.append("**待执行任务**:")
        for item in action_plan[:3]:
            lines.append(f"- [{item.get('day')}] {item.get('task')}")
        lines.append("")

    return "\n".join(lines)


def generate_detailed_analysis(result: Dict[str, Any]) -> str:
    """生成详细分析报告

    Args:
        result: 结果字典

    Returns:
        Markdown格式详细分析
    """
    lines = []
    lines.append("### 🔍 详细分析")
    lines.append("")

    progress_stats = result.get("progress_stats")
    if progress_stats:
        lines.append("#### 学习表现分析")
        lines.append("")
        lines.append(f"- 总作业数: {progress_stats.get('total_homework_count', 0)}")
        lines.append(f"- 已完成: {progress_stats.get('completed_count', 0)}")
        lines.append(f"- 完成率: {progress_stats.get('average_completion_rate', 0):.1f}%")
        lines.append(f"- 平均用时: {progress_stats.get('average_duration', 0):.1f}分钟")
        lines.append(f"- 学习动机: {progress_stats.get('motivation_score', 0):.1f}分")
        lines.append(f"- 本周进步: {progress_stats.get('weekly_improvement', 0):+.1f}%")
        lines.append("")

    known_facts = result.get("known_facts", [])
    if known_facts:
        lines.append("#### 已知信息")
        for fact in known_facts:
            lines.append(f"- {fact}")
        lines.append("")

    analysis = result.get("analysis", [])
    if analysis:
        lines.append("#### 分析判断")
        for item in analysis:
            lines.append(f"- {item}")
        lines.append("")

    return "\n".join(lines)


def export_to_json(result: Dict[str, Any]) -> str:
    """导出为JSON格式

    Args:
        result: 结果字典

    Returns:
        JSON格式字符串
    """
    import json
    return json.dumps(result, ensure_ascii=False, indent=2)


def export_to_csv(result: Dict[str, Any]) -> str:
    """导出为CSV格式

    Args:
        result: 结果字典

    Returns:
        CSV格式字符串
    """
    import csv
    import io

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["字段", "值"])

    if "progress_stats" in result and result["progress_stats"]:
        stats = result["progress_stats"]
        for key, value in stats.items():
            if not isinstance(value, list):
                writer.writerow([f"进度.{key}", value])

    if "action_plan" in result:
        writer.writerow([])
        writer.writerow(["行动计划"])
        writer.writerow(["日期", "任务", "负责人", "记录项", "难度"])
        for item in result["action_plan"]:
            writer.writerow([
                item.get("day", ""),
                item.get("task", ""),
                item.get("owner", ""),
                item.get("evidence_to_record", ""),
                item.get("difficulty", "")
            ])

    if "recommendations" in result:
        writer.writerow([])
        writer.writerow(["个性化推荐"])
        writer.writerow(["ID", "类别", "优先级", "标题", "描述", "置信度"])
        for rec in result["recommendations"]:
            writer.writerow([
                rec.get("recommendation_id", ""),
                rec.get("category", ""),
                rec.get("priority", ""),
                rec.get("title", ""),
                rec.get("description", ""),
                rec.get("confidence_score", 0)
            ])

    return output.getvalue()


def export_to_html(result: Dict[str, Any]) -> str:
    """导出为HTML格式

    Args:
        result: 结果字典

    Returns:
        HTML格式字符串
    """
    import html

    html_parts = []
    html_parts.append("<!DOCTYPE html>")
    html_parts.append("<html><head>")
    html_parts.append("<meta charset='UTF-8'>")
    html_parts.append("<title>小学作业陪伴报告</title>")
    html_parts.append("<style>")
    html_parts.append("body { font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }")
    html_parts.append("h1 { color: #333; border-bottom: 2px solid #007bff; }")
    html_parts.append("h2 { color: #555; }")
    html_parts.append("table { width: 100%; border-collapse: collapse; margin: 20px 0; }")
    html_parts.append("th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
    html_parts.append("th { background-color: #007bff; color: white; }")
    html_parts.append("</style>")
    html_parts.append("</head><body>")

    html_parts.append(f"<h1>小学作业陪伴报告</h1>")
    html_parts.append(f"<p><strong>生成时间</strong>: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")

    html_parts.append("<h2>A. 本次结论</h2>")
    html_parts.append("<ul>")
    for x in result.get("summary", []):
        html_parts.append(f"<li>{html.escape(x)}</li>")
    html_parts.append("</ul>")

    html_parts.append("<h2>B. 已知信息</h2>")
    html_parts.append("<ul>")
    for x in result.get("known_facts", []):
        html_parts.append(f"<li>{html.escape(x)}</li>")
    html_parts.append("</ul>")

    if "progress_stats" in result and result["progress_stats"]:
        stats = result["progress_stats"]
        html_parts.append("<h2>学习进度</h2>")
        html_parts.append("<table>")
        html_parts.append("<tr><th>指标</th><th>数值</th></tr>")
        html_parts.append(f"<tr><td>总作业数</td><td>{stats.get('total_homework_count', 0)}</td></tr>")
        html_parts.append(f"<tr><td>已完成</td><td>{stats.get('completed_count', 0)}</td></tr>")
        html_parts.append(f"<tr><td>平均完成率</td><td>{stats.get('average_completion_rate', 0):.1f}%</td></tr>")
        html_parts.append(f"<tr><td>学习动机</td><td>{stats.get('motivation_score', 0):.1f}分</td></tr>")
        html_parts.append("</table>")

    if "recommendations" in result and result["recommendations"]:
        html_parts.append("<h2>个性化推荐</h2>")
        html_parts.append("<table>")
        html_parts.append("<tr><th>优先级</th><th>标题</th><th>描述</th></tr>")
        for rec in result["recommendations"]:
            html_parts.append(f"<tr><td>{html.escape(rec.get('priority', ''))}</td>")
            html_parts.append(f"<td>{html.escape(rec.get('title', ''))}</td>")
            html_parts.append(f"<td>{html.escape(rec.get('description', ''))}</td></tr>")
        html_parts.append("</table>")

    html_parts.append("</body></html>")

    return "\n".join(html_parts)


def generate_weekly_summary(homework_records: List[Dict[str, Any]]) -> str:
    """生成周报摘要

    Args:
        homework_records: 周作业记录列表

    Returns:
        Markdown格式周报
    """
    lines = []
    lines.append("## 📅 本周作业总结")
    lines.append("")

    if not homework_records:
        lines.append("暂无本周数据")
        return "\n".join(lines)

    progress_stats = analyze_learning_progress(homework_records)
    anomalies = detect_learning_anomalies(homework_records)

    lines.append("### 总体情况")
    lines.append("")
    lines.append(f"- 总作业数: {progress_stats.total_homework_count}")
    lines.append(f"- 已完成: {progress_stats.completed_count}")
    lines.append(f"- 完成率: {progress_stats.get_completion_rate():.1f}%")
    lines.append(f"- 平均用时: {progress_stats.average_duration:.1f}分钟")
    lines.append(f"- 学习动机: {progress_stats.motivation_score:.1f}分")
    lines.append(f"- 本周进步: {progress_stats.weekly_improvement:+.1f}%")
    lines.append("")

    subject_data = {}
    for record in homework_records:
        subject = record.get("subject", "未知")
        if subject not in subject_data:
            subject_data[subject] = {"total": 0, "completed": 0}
        subject_data[subject]["total"] += 1
        if record.get("status") == "已完成":
            subject_data[subject]["completed"] += 1

    if subject_data:
        lines.append("### 学科完成情况")
        lines.append("")
        headers = ["学科", "总作业", "已完成", "完成率"]
        rows = []
        for subject, data in subject_data.items():
            rate = data["completed"] / data["total"] * 100 if data["total"] > 0 else 0
            rows.append([subject, data["total"], data["completed"], f"{rate:.1f}%"])
        lines.append(generate_table(headers, rows, ['l', 'c', 'c', 'c']))
        lines.append("")

    if anomalies:
        lines.append("### 需要关注的问题")
        lines.append("")
        for anomaly in anomalies[:5]:
            severity_icon = "🔴" if anomaly["severity"] == "high" else "🟡"
            lines.append(f"{severity_icon} **{anomaly['subject']}**: {anomaly['message']}")
        lines.append("")

    return "\n".join(lines)
