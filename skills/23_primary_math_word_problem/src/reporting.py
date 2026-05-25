"""Markdown report renderer for 小学数学应用题 Agent.

提供图表生成、表格美化、进度可视化和摘要生成功能。
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
try:
    from .models import ProgressStats, Recommendation
except ImportError:
    from models import ProgressStats, Recommendation


def render_report(result: Dict[str, Any]) -> str:
    """渲染完整报告"""
    lines: List[str] = []
    lines.append("# 小学数学应用题报告")
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
        lines.append(generate_progress_visualization(result["progress_stats"]))

    if result.get("recommendations"):
        lines.append("")
        lines.append(generate_recommendations_table(result["recommendations"]))

    return "\n".join(lines)


def generate_progress_visualization(progress_stats: Dict[str, Any]) -> str:
    """生成学习进度可视化图表(文本格式)"""
    lines = []
    lines.append("### 📊 解题进度概览")
    lines.append("")

    total = progress_stats.get("total_problems", 0)
    solved = progress_stats.get("solved_count", 0)
    correct = progress_stats.get("correct_count", 0)
    accuracy_rate = progress_stats.get("get_accuracy_rate", lambda: 0)() if callable(progress_stats.get("get_accuracy_rate")) else progress_stats.get("average_time", 0)
    avg_time = progress_stats.get("average_time", 0)
    hints = progress_stats.get("hints_used", 0)
    improvement = progress_stats.get("weekly_improvement", 0)

    lines.append("#### 完成情况")
    lines.append("```")
    bar_width = 30
    filled = int((solved / total * bar_width) if total > 0 else 0)
    bar = "█" * filled + "░" * (bar_width - filled)
    lines.append(f"解题进度: [{bar}] {solved}/{total}")
    lines.append("```")
    lines.append("")

    lines.append("#### 关键指标")
    lines.append("")
    metrics = [
        ("正确率", f"{accuracy_rate:.1f}%"),
        ("平均用时", f"{avg_time:.1f}分钟"),
        ("提示次数", f"{hints}次"),
        ("本周进步", f"{improvement:+.1f}%")
    ]

    max_label_len = max(len(m[0]) for m in metrics)
    for label, value in metrics:
        padding = " " * (max_label_len - len(label))
        lines.append(f"- {label}{padding} : {value}")
    lines.append("")

    concepts_mastered = progress_stats.get("concepts_mastered", [])
    concepts_needing_work = progress_stats.get("concepts_needing_work", [])

    if concepts_mastered:
        lines.append("#### ✅ 已掌握概念")
        lines.append(f"- {', '.join(concepts_mastered)}")
        lines.append("")

    if concepts_needing_work:
        lines.append("#### ⚠️ 需要加强概念")
        lines.append(f"- {', '.join(concepts_needing_work)}")
        lines.append("")

    return "\n".join(lines)


def generate_text_bar_chart(data: Dict[str, float], title: str = "数据分布", width: int = 20) -> str:
    """生成文本条形图"""
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
    """生成Markdown表格"""
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
    """生成个性化推荐表格"""
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


def export_to_json(result: Dict[str, Any]) -> str:
    """导出为JSON格式"""
    import json
    return json.dumps(result, ensure_ascii=False, indent=2)


def export_to_csv(result: Dict[str, Any]) -> str:
    """导出为CSV格式"""
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


def generate_summary_section(result: Dict[str, Any]) -> str:
    """生成摘要部分"""
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
