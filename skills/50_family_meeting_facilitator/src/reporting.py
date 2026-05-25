"""Markdown report renderer for 家庭会议主持 Agent."""
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


def generate_summary(data: Dict[str, Any]) -> List[str]:
    """生成摘要信息"""
    summary = []
    if "summary" in data and data["summary"]:
        summary.extend(data["summary"])
    else:
        summary.append("本次分析已完成")
    if "statistics" in data:
        stats = data["statistics"]
        if "total_meetings" in stats:
            summary.append(f"会议总数: {stats['total_meetings']}")
        if "total_decisions" in stats:
            summary.append(f"决议总数: {stats['total_decisions']}")
        if "participation_rate" in stats:
            summary.append(f"参与率: {stats['participation_rate']:.0%}")
    return summary


def generate_meeting_history_table(meetings: List[Dict[str, Any]]) -> str:
    """生成会议历史表格"""
    if not meetings:
        return "暂无会议记录"
    headers = ["日期", "类型", "参与者", "决议数", "状态"]
    rows = []
    meeting_type_display = {"weekly_planning": "周计划", "monthly_review": "月复盘", "problem_solving": "问题解决", "celebration": "庆祝", "rules_update": "规则更新", "schedule_discussion": "日程讨论"}
    for meeting in meetings:
        meeting_type = meeting_type_display.get(meeting.get("meeting_type", ""), meeting.get("meeting_type", "-"))
        participants = len(meeting.get("participants", []))
        decisions = len(meeting.get("decisions", []))
        status = "已完成" if meeting.get("decisions") else "待决议"
        rows.append([meeting.get("date", "-"), meeting_type, f"{participants}人", decisions, status])
    return create_table(headers, rows)


def generate_agenda_table(agenda: List[Dict[str, Any]]) -> str:
    """生成议程表格"""
    if not agenda:
        return "暂无议程"
    headers = ["议题", "提出人", "优先级", "时间分配"]
    rows = []
    priority_display = {"urgent": "🔴 紧急", "high": "🟠 高", "normal": "🟡 普通", "low": "🟢 低"}
    for item in agenda:
        topic = item.get("topic", "-")
        presenter = item.get("presenter", "-")
        priority = priority_display.get(item.get("priority", "normal"), item.get("priority", "normal"))
        time = item.get("time_allocation", 10)
        rows.append([topic[:40], presenter, priority, f"{time}分钟"])
    return create_table(headers, rows)


def generate_decision_table(decisions: List[Dict[str, Any]]) -> str:
    """生成决议表格"""
    if not decisions:
        return "暂无决议"
    headers = ["议题", "决议", "决策人", "状态", "截止日期"]
    rows = []
    status_display = {"pending": "⏳ 待处理", "discussed": "💬 讨论中", "decided": "✅ 已决定", "deferred": "⏰ 推迟", "rejected": "❌ 已拒绝"}
    for decision in decisions:
        topic = decision.get("topic", "-")
        decision_text = decision.get("decision", "-")[:30]
        decision_by = decision.get("decision_by", "-")
        status = status_display.get(decision.get("status", ""), decision.get("status", "-"))
        deadline = decision.get("deadline", "-")
        rows.append([topic[:25], decision_text, decision_by, status, deadline])
    return create_table(headers, rows)


def generate_action_items_table(action_items: List[Dict[str, Any]]) -> str:
    """生成行动项目表格"""
    if not action_items:
        return "暂无行动项目"
    headers = ["任务", "负责人", "截止日期", "状态"]
    rows = []
    for item in action_items:
        task = item.get("task", "-")
        owner = item.get("owner", "-")
        deadline = item.get("deadline", "-")
        status = item.get("status", "pending")
        status_icon = {"pending": "⏳", "in_progress": "🔄", "completed": "✅"}.get(status, "⏳")
        rows.append([task[:40], owner, deadline, f"{status_icon} {status}"])
    return create_table(headers, rows)


def export_to_json(data: Dict[str, Any]) -> str:
    """导出为JSON格式"""
    return json.dumps(data, ensure_ascii=False, indent=2)


def render_report(result: Dict[str, Any]) -> str:
    """渲染完整报告"""
    lines: List[str] = []
    lines.append("# 家庭会议主持报告")
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
        lines.append("## D. 会议统计")
        stats = result["statistics"]
        if stats:
            stats_headers = ["指标", "数值"]
            stats_rows = []
            for key, value in stats.items():
                display_key = {"total_meetings": "会议总数", "total_decisions": "决议总数", "pending_decisions": "待处理决议", "participation_rate": "参与率"}.get(key, key)
                if isinstance(value, float):
                    value = f"{value:.2f}"
                else:
                    value = str(value)
                stats_rows.append([display_key, value])
            lines.append(create_table(stats_headers, stats_rows))
        lines.append("")
    if "agenda" in result and result["agenda"]:
        lines.append("## E. 会议议程")
        agenda_table = generate_agenda_table(result["agenda"])
        lines.append(agenda_table)
        lines.append("")
    if "decisions" in result and result["decisions"]:
        lines.append("## F. 会议决议")
        decision_table = generate_decision_table(result["decisions"])
        lines.append(decision_table)
        lines.append("")
    if "action_items" in result and result["action_items"]:
        lines.append("## G. 行动项目")
        action_table = generate_action_items_table(result["action_items"])
        lines.append(action_table)
        lines.append("")
    if "meeting_history" in result:
        lines.append("## H. 会议历史")
        history_table = generate_meeting_history_table(result["meeting_history"])
        lines.append(history_table)
        lines.append("")
    action_plan = result.get("action_plan", [])
    if action_plan:
        lines.append("## I. 执行方案")
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
        lines.append("## J. 风险提示")
        for note in risk_notes:
            lines.append(f"- {note}")
        lines.append("")
    alerts = result.get("alerts", [])
    if alerts:
        lines.append("## K. 预警信息")
        for alert in alerts:
            severity_icon = {"info": "ℹ️", "warning": "⚠️", "critical": "🚨"}.get(alert.get("severity", "info"), "ℹ️")
            lines.append(f"{severity_icon} **{alert.get('alert_type', '通知')}**: {alert.get('message', '')}")
            if alert.get("recommendation"):
                lines.append(f"   - 建议: {alert['recommendation']}")
        lines.append("")
    next_fields = result.get("next_tracking_fields", [])
    if next_fields:
        lines.append("## L. 下次追踪字段")
        for x in next_fields:
            lines.append(f"- [ ] {x}")
        lines.append("")
    return "\n".join(lines)


def render_summary_report(result: Dict[str, Any]) -> str:
    """渲染简洁摘要报告"""
    lines: List[str] = []
    lines.append("# 家庭会议主持 - 摘要报告")
    lines.append("")
    summary = generate_summary(result)
    for x in summary:
        lines.append(f"- {x}")
    lines.append("")
    if "pending_decisions" in result.get("statistics", {}):
        pending = result["statistics"]["pending_decisions"]
        if pending > 0:
            lines.append(f"⚠️ 有 {pending} 项待处理决议")
    return "\n".join(lines)