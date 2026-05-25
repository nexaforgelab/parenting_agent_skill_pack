"""Markdown report renderer for 家庭教育支出规划 Agent."""
from typing import Any, Dict, List, Optional
from datetime import datetime
import json


def create_table(headers: List[str], rows: List[List[str]], align: Optional[List[str]] = None) -> str:
    """创建Markdown表格"""
    if not headers:
        return ""
    lines = []
    align_map = {"left": ":---", "center": ":---:", "right": "---:"}
    if align is None:
        align = ["left"] * len(headers)
    header_line = "| " + " | ".join(headers) + " |"
    separator_line = "|" + "|".join([align_map.get(a, ":---") for a in align]) + "|"
    lines.append(header_line)
    lines.append(separator_line)
    for row in rows:
        row_line = "| " + " | ".join(str(cell) for cell in row) + " |"
        lines.append(row_line)
    return "\n".join(lines)


def create_progress_bar(value: float, max_value: float = 100, width: int = 20) -> str:
    """创建进度条可视化"""
    percentage = min(value / max_value, 1.0)
    filled = int(width * percentage)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {percentage * 100:.1f}%"


def generate_summary(data: Dict[str, Any]) -> List[str]:
    """生成摘要信息"""
    summary = []
    if "summary" in data and data["summary"]:
        summary.extend(data["summary"])
    else:
        summary.append("本次分析已完成")
    if "statistics" in data:
        stats = data["statistics"]
        if "total_spending" in stats:
            summary.append(f"总支出: ¥{stats['total_spending']:.2f}")
        if "budget_status" in stats:
            summary.append(f"预算状态: {stats['budget_status']}")
    return summary


def generate_expense_table(expenses: List[Dict[str, Any]]) -> str:
    """生成支出表格"""
    if not expenses:
        return "暂无支出记录"
    headers = ["日期", "分类", "描述", "金额"]
    rows = []
    for expense in expenses:
        rows.append([
            expense.get("date", "-"),
            expense.get("category", "-"),
            expense.get("description", "-")[:40],
            f"¥{expense.get('amount', 0):.2f}"
        ])
    return create_table(headers, rows)


def generate_category_breakdown(category_breakdown: Dict[str, float], total: float) -> str:
    """生成分类明细表格"""
    if not category_breakdown:
        return "暂无分类数据"
    headers = ["分类", "金额", "占比", "预算进度"]
    rows = []
    category_display = {
        "childcare": "托育", "tuition": "学费", "books": "书籍", "toys": "玩具",
        "travel": "旅行", "extracurricular": "课外班", "supplies": "用品", "health": "健康", "other": "其他"
    }
    for cat, amount in sorted(category_breakdown.items(), key=lambda x: x[1], reverse=True):
        percentage = (amount / total * 100) if total > 0 else 0
        progress = create_progress_bar(amount, total, 10)
        display_name = category_display.get(cat, cat)
        rows.append([display_name, f"¥{amount:.2f}", f"{percentage:.1f}%", progress])
    return create_table(headers, rows, align=["left", "right", "center", "left"])


def export_to_json(data: Dict[str, Any]) -> str:
    """导出为JSON格式"""
    return json.dumps(data, ensure_ascii=False, indent=2)


def render_report(result: Dict[str, Any]) -> str:
    """渲染完整报告"""
    lines: List[str] = []
    lines.append("# 家庭教育支出规划报告")
    lines.append("")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines.append(f"> 生成时间: {timestamp}")
    lines.append("")
    summary = generate_summary(result)
    lines.append("## A. 本次结论")
    for x in summary:
        lines.append(f"- {x}")
    lines.append("")
    known_facts = result.get("known_facts", [])
    if known_facts:
        lines.append("## B. 已知信息")
        for x in known_facts:
            lines.append(f"- {x}")
        lines.append("")
    analysis = result.get("analysis", [])
    if analysis:
        lines.append("## C. 分析与判断")
        for x in analysis:
            lines.append(f"- {x}")
        lines.append("")
    if "statistics" in result:
        lines.append("## D. 支出统计")
        stats = result["statistics"]
        if stats:
            stats_headers = ["指标", "数值"]
            stats_rows = []
            for key, value in stats.items():
                display_key = {"total_spending": "总支出", "average_daily": "日均支出", "budget_status": "预算状态"}.get(key, key)
                if isinstance(value, float):
                    value = f"¥{value:.2f}"
                else:
                    value = str(value)
                stats_rows.append([display_key, value])
            lines.append(create_table(stats_headers, stats_rows))
        lines.append("")
    if "category_breakdown" in result:
        lines.append("## E. 分类明细")
        breakdown_table = generate_category_breakdown(result.get("category_breakdown", {}), result.get("statistics", {}).get("total_spending", 1))
        lines.append(breakdown_table)
        lines.append("")
    if "expenses" in result:
        lines.append("## F. 支出记录")
        expense_table = generate_expense_table(result["expenses"])
        lines.append(expense_table)
        lines.append("")
    action_plan = result.get("action_plan", [])
    if action_plan:
        lines.append("## G. 执行方案")
        plan_headers = ["日期", "任务", "负责人"]
        plan_rows = []
        for item in action_plan:
            if isinstance(item, dict):
                plan_rows.append([item.get("day", "-"), item.get("task", "-"), item.get("owner", "-")])
        if plan_rows:
            lines.append(create_table(plan_headers, plan_rows))
        lines.append("")
    risk_notes = result.get("risk_notes", [])
    if risk_notes:
        lines.append("## H. 风险提示")
        for note in risk_notes:
            lines.append(f"- {note}")
        lines.append("")
    alerts = result.get("alerts", [])
    if alerts:
        lines.append("## I. 预警信息")
        for alert in alerts:
            severity_icon = {"info": "ℹ️", "warning": "⚠️", "critical": "🚨"}.get(alert.get("severity", "info"), "ℹ️")
            lines.append(f"{severity_icon} **{alert.get('alert_type', '通知')}**: {alert.get('message', '')}")
            if alert.get("recommendation"):
                lines.append(f"   - 建议: {alert['recommendation']}")
        lines.append("")
    next_fields = result.get("next_tracking_fields", [])
    if next_fields:
        lines.append("## J. 下次追踪字段")
        for x in next_fields:
            lines.append(f"- [ ] {x}")
        lines.append("")
    return "\n".join(lines)


def render_summary_report(result: Dict[str, Any]) -> str:
    """渲染简洁摘要报告"""
    lines: List[str] = []
    lines.append("# 家庭教育支出规划 - 摘要报告")
    lines.append("")
    summary = generate_summary(result)
    for x in summary:
        lines.append(f"- {x}")
    lines.append("")
    if "budget_status" in result.get("statistics", {}):
        status = result["statistics"]["budget_status"]
        status_icon = {"正常": "✅", "超支": "🚨", "接近上限": "⚠️"}.get(status, "❓")
        lines.append(f"📊 预算状态: {status_icon} {status}")
    return "\n".join(lines)