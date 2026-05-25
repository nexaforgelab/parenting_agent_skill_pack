"""Markdown report renderer for 父母情绪管理 Agent."""
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


def create_intensity_meter(intensity: int, max_intensity: int = 10) -> str:
    """创建情绪强度仪表"""
    percentage = intensity / max_intensity
    bars = int(percentage * 10)
    return "🔴" * bars + "⚪️" * (10 - bars) + f" {intensity}/10"


def generate_summary(data: Dict[str, Any]) -> List[str]:
    """生成摘要信息"""
    summary = []
    if "summary" in data and data["summary"]:
        summary.extend(data["summary"])
    else:
        summary.append("本次分析已完成")
    if "statistics" in data:
        stats = data["statistics"]
        if "total_records" in stats:
            summary.append(f"情绪记录: {stats['total_records']} 条")
        if "avg_intensity" in stats:
            summary.append(f"平均强度: {stats['avg_intensity']:.1f}/10")
        if "dominant_emotion" in stats:
            summary.append(f"主要情绪: {stats['dominant_emotion']}")
    return summary


def generate_emotion_log_table(records: List[Dict[str, Any]]) -> str:
    """生成情绪日志表格"""
    if not records:
        return "暂无情绪记录"
    headers = ["日期", "情绪类型", "强度", "触发因素", "应对策略", "效果"]
    rows = []
    emotion_display = {"anger": "愤怒", "frustration": "挫败", "anxiety": "焦虑", "sadness": "悲伤", "guilt": "内疚", "overwhelm": "压力", "exhaustion": "疲惫", "joy": "喜悦", "calm": "平静", "gratitude": "感恩"}
    for record in records:
        emotion = emotion_display.get(record.get("emotion_type", ""), record.get("emotion_type", "-"))
        intensity = create_intensity_meter(record.get("intensity", 5))
        trigger = record.get("trigger", "-")[:20]
        coping = ", ".join(record.get("coping_used", [])) or "-"
        effectiveness = record.get("effectiveness", 3)
        rows.append([record.get("date", "-"), emotion, intensity, trigger, coping[:15], f"{effectiveness}/5"])
    return create_table(headers, rows)


def generate_pattern_table(patterns: List[Dict[str, Any]]) -> str:
    """生成情绪模式表格"""
    if not patterns:
        return "暂无模式数据"
    headers = ["情绪类型", "频率", "平均强度", "趋势"]
    rows = []
    for pattern in patterns:
        emotion = pattern.get("emotion_type", "-")
        frequency = pattern.get("frequency", 0)
        avg_intensity = pattern.get("average_intensity", 0)
        trend = pattern.get("trend", "stable")
        trend_icon = {"increasing": "📈", "decreasing": "📉", "stable": "➡️"}.get(trend, "➡️")
        rows.append([emotion, frequency, f"{avg_intensity:.1f}", f"{trend_icon} {trend}"])
    return create_table(headers, rows)


def generate_coping_suggestions(emotion_type: str) -> str:
    """生成应对建议"""
    suggestions = {
        "anger": {"strategies": ["深呼吸", "物理暂停", "数到10"], "scripts": ["我现在需要冷静一下", "我需要暂停"]},
        "anxiety": {"strategies": ["深呼吸", "接地练习", "写日记"], "scripts": ["这种感觉会过去的", "我可以应对"]},
        "overwhelm": {"strategies": ["分解任务", "寻求支持", "休息"], "scripts": ["一次做一件事", "我可以请求帮助"]},
        "frustration": {"strategies": ["暂停", "换个角度", "自我对话"], "scripts": ["这不是孩子的错", "我理解这是正常的"]}
    }
    default_suggestions = {"strategies": ["深呼吸", "暂停", "自我觉察"], "scripts": ["我现在需要冷静"]}
    suggestion = suggestions.get(emotion_type, default_suggestions)
    result = f"### 针对{emotion_type}的建议\n\n"
    result += "**推荐策略:**\n"
    for s in suggestion["strategies"]:
        result += f"- {s}\n"
    result += "\n**推荐话术:**\n"
    for script in suggestion["scripts"]:
        result += f"- \"{script}\"\n"
    return result


def export_to_json(data: Dict[str, Any]) -> str:
    """导出为JSON格式"""
    return json.dumps(data, ensure_ascii=False, indent=2)


def render_report(result: Dict[str, Any]) -> str:
    """渲染完整报告"""
    lines: List[str] = []
    lines.append("# 父母情绪管理报告")
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
        lines.append("## D. 情绪统计")
        stats = result["statistics"]
        if stats:
            stats_headers = ["指标", "数值"]
            stats_rows = []
            for key, value in stats.items():
                display_key = {"total_records": "记录总数", "avg_intensity": "平均强度", "dominant_emotion": "主要情绪", "effective_strategies": "有效策略数"}.get(key, key)
                if isinstance(value, float):
                    value = f"{value:.2f}"
                else:
                    value = str(value)
                stats_rows.append([display_key, value])
            lines.append(create_table(stats_headers, stats_rows))
        lines.append("")
    if "patterns" in result and result["patterns"]:
        lines.append("## E. 情绪模式")
        pattern_table = generate_pattern_table(result["patterns"])
        lines.append(pattern_table)
        lines.append("")
    if "emotion_log" in result:
        lines.append("## F. 情绪日志")
        log_table = generate_emotion_log_table(result["emotion_log"])
        lines.append(log_table)
        lines.append("")
    if "coping_suggestions" in result:
        lines.append("## G. 应对建议")
        for suggestion in result["coping_suggestions"]:
            lines.append(generate_coping_suggestions(suggestion.get("emotion_type", "")))
        lines.append("")
    action_plan = result.get("action_plan", [])
    if action_plan:
        lines.append("## H. 执行方案")
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
        lines.append("## I. 风险提示")
        for note in risk_notes:
            lines.append(f"- {note}")
        lines.append("")
    alerts = result.get("alerts", [])
    if alerts:
        lines.append("## J. 预警信息")
        for alert in alerts:
            severity_icon = {"info": "ℹ️", "warning": "⚠️", "critical": "🚨"}.get(alert.get("severity", "info"), "ℹ️")
            lines.append(f"{severity_icon} **{alert.get('alert_type', '通知')}**: {alert.get('message', '')}")
            if alert.get("recommendation"):
                lines.append(f"   - 建议: {alert['recommendation']}")
        lines.append("")
    next_fields = result.get("next_tracking_fields", [])
    if next_fields:
        lines.append("## K. 下次追踪字段")
        for x in next_fields:
            lines.append(f"- [ ] {x}")
        lines.append("")
    return "\n".join(lines)


def render_summary_report(result: Dict[str, Any]) -> str:
    """渲染简洁摘要报告"""
    lines: List[str] = []
    lines.append("# 父母情绪管理 - 摘要报告")
    lines.append("")
    summary = generate_summary(result)
    for x in summary:
        lines.append(f"- {x}")
    lines.append("")
    if "statistics" in result:
        stats = result["statistics"]
        if "avg_intensity" in stats:
            avg = stats["avg_intensity"]
            status = "🟢 正常" if avg < 5 else "🟡 注意" if avg < 7 else "🔴 需关注"
            lines.append(f"📊 平均情绪强度: {status}")
    return "\n".join(lines)