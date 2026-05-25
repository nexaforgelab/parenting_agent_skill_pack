"""Markdown report renderer for 小学口算训练 Agent."""
from typing import Any, Dict, List, Optional
from datetime import datetime
try:
    from .models import ProgressStats, Recommendation
except ImportError:
    from models import ProgressStats, Recommendation


def render_report(result: Dict[str, Any]) -> str:
    """渲染完整报告"""
    lines: List[str] = []
    lines.append("# 小学口算训练报告")
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
    """生成训练进度可视化"""
    lines = []
    lines.append("### 📊 训练进度概览")
    lines.append("")

    total = progress_stats.get("total_problems_today", 0)
    correct = progress_stats.get("total_correct_today", 0)
    accuracy = progress_stats.get("accuracy_rate", 0)
    avg_speed = progress_stats.get("average_speed", 0)
    total_time = progress_stats.get("total_time_today", 0)

    lines.append("#### 完成情况")
    lines.append("```")
    bar_width = 30
    filled = int((correct / total * bar_width) if total > 0 else 0)
    bar = "█" * filled + "░" * (bar_width - filled)
    lines.append(f"正确率: [{bar}] {correct}/{total} ({accuracy:.1f}%)" if total > 0 else "暂无数据")
    lines.append("```")
    lines.append("")

    lines.append("#### 关键指标")
    lines.append("")
    metrics = [
        ("正确率", f"{accuracy:.1f}%"),
        ("平均速度", f"{avg_speed:.1f}秒/题"),
        ("总用时", f"{total_time:.1f}秒"),
        ("总题数", f"{total}题")
    ]

    max_label_len = max(len(m[0]) for m in metrics)
    for label, value in metrics:
        padding = " " * (max_label_len - len(label))
        lines.append(f"- {label}{padding} : {value}")
    lines.append("")

    weak_ops = progress_stats.get("weak_operations", [])
    strong_ops = progress_stats.get("strong_operations", [])

    if weak_ops:
        lines.append("#### ⚠️ 薄弱运算")
        lines.append(f"- {', '.join(weak_ops)}")
        lines.append("")

    if strong_ops:
        lines.append("#### ✅ 熟练运算")
        lines.append(f"- {', '.join(strong_ops)}")
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

    return output.getvalue()
