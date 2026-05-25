"""Planning engine for 亲子旅行规划 Agent.

增强版本：添加数据分析、异常检测、个性化推荐、上下文记忆、数据聚合
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta, date
from collections import defaultdict
try:
    from .models import TrendData, Alert, Recommendation, SessionContext, WeeklyStats
except ImportError:
    from models import TrendData, Alert, Recommendation, SessionContext, WeeklyStats

SKILL_FLOW = ['输入目的地、孩子年龄、天数、预算', '规划低强度行程', '安排午睡和用餐', '生成行李清单', '输出应急预案']
SAFETY_NOTES = ['本 Skill 提供家庭教育和生活管理建议，不替代专业人士意见。', '涉及安全、法律、医疗、财务或教育政策时，应提示家长二次核验。', '输出应尊重家庭差异，不用单一标准评价孩子或父母。']
DEFAULT_DELIVERABLES = ['亲子行程', '行李清单', '应急联系人清单']

_context_store: Dict[str, SessionContext] = {}


def get_or_create_context(session_id: str) -> SessionContext:
    """获取或创建会话上下文"""
    if session_id not in _context_store:
        _context_store[session_id] = SessionContext(session_id=session_id)
    return _context_store[session_id]


def update_context(session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
    """更新会话上下文"""
    context = get_or_create_context(session_id)
    context.add_interaction(role, content, metadata)


def analyze_travel_trends(records: List[Dict[str, Any]], days: int = 30) -> List[TrendData]:
    """分析旅行趋势"""
    trends = []
    if not records:
        return trends

    records_by_month = defaultdict(list)
    for record in records:
        try:
            if isinstance(record.get("timestamp"), str):
                record_date = datetime.fromisoformat(record["timestamp"]).date()
            elif isinstance(record.get("timestamp"), datetime):
                record_date = record["timestamp"].date()
            else:
                continue
            month_key = f"{record_date.year}-{record_date.month:02d}"
            records_by_month[month_key].append(record)
        except (ValueError, AttributeError):
            continue

    if not records_by_month:
        return trends

    sorted_months = sorted(records_by_month.keys())
    monthly_counts = []
    monthly_budgets = []
    months = []

    for month in sorted_months[-6:]:
        month_records = records_by_month[month]
        count = len(month_records)
        total_budget = sum(r.get("budget", 0) or 0 for r in month_records)
        monthly_counts.append(float(count))
        monthly_budgets.append(float(total_budget))
        months.append(month)

    if monthly_counts:
        count_trend = TrendData(metric_name="每月出行次数", data_points=monthly_counts, dates=months)
        count_trend.calculate_trend()
        trends.append(count_trend)

    if monthly_budgets:
        budget_trend = TrendData(metric_name="每月预算", data_points=monthly_budgets, dates=months)
        budget_trend.calculate_trend()
        trends.append(budget_trend)

    return trends


def detect_anomalies(records: List[Dict[str, Any]], trends: List[TrendData]) -> List[Alert]:
    """检测异常情况"""
    alerts = []
    if not records:
        return alerts

    child_ages = [r.get("child_age", 0) for r in records if r.get("child_age")]
    if child_ages:
        avg_age = sum(child_ages) / len(child_ages)
        if avg_age < 24:
            alerts.append(Alert(
                alert_type="低龄儿童出行提醒",
                severity="info",
                message=f"出行儿童平均月龄{avg_age:.0f}个月，需特别注意行程强度",
                recommendation="建议选择短途、设施齐全的目的地，频繁安排休息"
            ))

    return alerts


def generate_personalized_recommendations(
    records: List[Dict[str, Any]],
    trends: List[TrendData],
    child_profile: Dict[str, Any],
    alerts: List[Alert]
) -> List[Recommendation]:
    """生成个性化推荐"""
    recommendations = []
    age_months = child_profile.get("age_months", 0)

    if age_months < 24:
        recommendations.append(Recommendation(
            category="低龄出行建议",
            priority=1,
            title="幼儿旅行规划重点",
            description=f"根据孩子月龄（{age_months}个月），建议选择适合幼儿的目的地",
            action_items=[
                "选择室内或短途户外场所",
                "确保有充足的休息时间",
                "携带充足的辅食和尿布"
            ],
            rationale="低龄儿童需要更多休息和照顾",
            expected_outcome="旅行愉快，孩子不累大人轻松"
        ))
    elif age_months < 72:
        recommendations.append(Recommendation(
            category="学龄前出行建议",
            priority=1,
            title="学龄前儿童旅行规划重点",
            description=f"根据孩子月龄（{age_months}个月），建议增加互动体验",
            action_items=[
                "选择有儿童游乐设施的目的地",
                "安排亲子互动活动",
                "教育与娱乐相结合"
            ],
            rationale="学龄前儿童好奇心强，适合探索性旅行",
            expected_outcome="旅行成为生动的课堂"
        ))

    if not alerts and not recommendations:
        recommendations.append(Recommendation(
            category="旅行规划习惯",
            priority=3,
            title="保持良好的旅行规划习惯",
            description="当前规划合理，继续完善细节",
            action_items=["提前制定详细行程", "准备应急物品清单", "记录旅行体验和教训"],
            rationale="充分的规划可以让旅行更加顺利",
            expected_outcome="建立完善的家庭旅行规划体系"
        ))

    recommendations.sort(key=lambda x: x.priority)
    return recommendations


def aggregate_weekly_stats(records: List[Dict[str, Any]], week_offset: int = 0) -> Optional[WeeklyStats]:
    """聚合统计数据"""
    if not records:
        return None

    today = datetime.now().date()
    days_since_monday = today.weekday()
    week_start = today - timedelta(days=days_since_monday + week_offset * 7)
    week_end = week_start + timedelta(days=6)

    week_records = []
    for record in records:
        try:
            if isinstance(record.get("timestamp"), str):
                record_date = datetime.fromisoformat(record["timestamp"]).date()
            elif isinstance(record.get("timestamp"), datetime):
                record_date = record["timestamp"].date()
            else:
                continue
            if week_start <= record_date <= week_end:
                week_records.append(record)
        except (ValueError, AttributeError, TypeError):
            continue

    if not week_records:
        return None

    stats = WeeklyStats(
        week_start=week_start.isoformat(),
        week_end=week_end.isoformat(),
        total_schedules=len(week_records),
        completed_schedules=len(week_records),
        completion_rate=100.0
    )
    return stats


def build_known_facts(payload: Dict[str, Any]) -> List[str]:
    """构建已知事实列表"""
    facts: List[str] = []
    child = payload.get("child_profile", {})
    family = payload.get("family_context", {})
    if child:
        facts.append(f"孩子画像：{child}")
    if family:
        facts.append(f"家庭上下文：{family}")
    if payload.get("goal"):
        facts.append(f"目标：{payload.get('goal')}")
    records = payload.get("raw_records") or []
    facts.append(f"已收到 {len(records)} 条原始记录。")

    if records:
        trends = analyze_travel_trends(records, payload.get("history_days", 30))
        if trends:
            for trend in trends:
                facts.append(f"{trend.metric_name}：平均 {trend.average:.1f}，趋势 {trend.trend_direction}（{trend.trend_percentage:+.1f}%）")
    return facts


def build_analysis(payload: Dict[str, Any]) -> List[str]:
    """构建分析内容"""
    problem = payload.get("current_problem", "")
    history_days = payload.get("history_days", 30)
    records = payload.get("raw_records") or []
    child_profile = payload.get("child_profile", {})

    analysis = [
        f"当前问题聚焦：{problem}",
        f"建议回顾最近 {history_days} 天的旅行规划情况。",
        "本 Skill 会优先输出可执行动作、记录字段和复盘指标。",
    ]
    for step in SKILL_FLOW:
        analysis.append(f"链路节点：{step}")

    if records:
        trends = analyze_travel_trends(records, history_days)
        alerts = detect_anomalies(records, trends)
        if alerts:
            analysis.append("")
            analysis.append("⚠️ 检测到的异常：")
            for alert in alerts:
                analysis.append(f"  - [{alert.severity}] {alert.message}")
        recommendations = generate_personalized_recommendations(records, trends, child_profile, alerts)
        if recommendations:
            analysis.append("")
            analysis.append("📋 个性化建议：")
            for rec in recommendations[:3]:
                analysis.append(f"  - {rec.title}：{rec.description}")
    return analysis


def build_action_plan(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """构建行动计划"""
    base_tasks = [
        "确定旅行目的地和日期",
        "评估孩子的适应能力",
        "制定行程计划表",
        "准备行李清单和应急物品",
        "预订交通和住宿"
    ]
    plan: List[Dict[str, str]] = []
    for i, task in enumerate(base_tasks, start=1):
        plan.append({
            "day": f"D{i}",
            "task": task,
            "owner": "家长/主要照护人",
            "evidence_to_record": "行程安排、注意事项、应急预案",
            "difficulty": "低" if i <= 3 else "中"
        })
    return plan


def build_deliverables(payload: Dict[str, Any]) -> Dict[str, Any]:
    """构建交付物"""
    deliverables = {
        "required": DEFAULT_DELIVERABLES,
        "tables": {
            "timeline": ["时间", "活动", "地点", "注意事项", "备注"],
            "weekly_review": ["指标", "本周", "上周", "变化", "下一步"]
        },
        "templates": {
            "daily_log": "今天旅行去了哪里？孩子玩得开心吗？有什么需要注意的？",
            "handoff_summary": "给家人的旅行摘要：行程安排、注意事项、紧急联系人。"
        }
    }
    records = payload.get("raw_records") or []
    if records:
        trends = analyze_travel_trends(records, payload.get("history_days", 30))
        if trends:
            deliverables["analysis_charts"] = {"trend_summary": [{"metric": t.metric_name, "average": round(t.average, 2), "trend": t.trend_direction, "change_percent": round(t.trend_percentage, 2)} for t in trends]}
    return deliverables


def next_fields() -> List[str]:
    """获取下次追踪字段"""
    return [
        "孩子年龄/月龄",
        "目的地和天数",
        "行程安排",
        "孩子反应",
        "需要调整的事项",
        "下次改进方向"
    ]


def generate_session_summary(session_id: str) -> Optional[Dict[str, Any]]:
    """生成会话摘要"""
    if session_id not in _context_store:
        return None
    context = _context_store[session_id]
    return {
        "session_id": session_id,
        "created_at": context.created_at.isoformat() if isinstance(context.created_at, datetime) else context.created_at,
        "last_updated": context.last_updated.isoformat() if isinstance(context.last_updated, datetime) else context.last_updated,
        "total_interactions": len(context.conversation_history),
        "accumulated_data_keys": list(context.accumulated_data.keys())
    }


def clear_context(session_id: str) -> bool:
    """清除会话上下文"""
    if session_id in _context_store:
        del _context_store[session_id]
        return True
    return False
