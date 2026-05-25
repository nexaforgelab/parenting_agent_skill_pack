"""Planning engine for 周末亲子活动 Agent.

增强版本：添加数据分析、异常检测、个性化推荐、上下文记忆、数据聚合
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta, date
from collections import defaultdict
try:
    from .models import TrendData, Alert, Recommendation, SessionContext, WeeklyStats
except ImportError:
    from models import TrendData, Alert, Recommendation, SessionContext, WeeklyStats

SKILL_FLOW = ['输入城市、天气、孩子年龄、预算', '推荐室内/户外活动', '生成半日/一日计划', '准备物品清单', '记录活动体验']
SAFETY_NOTES = ['本 Skill 提供家庭教育和生活管理建议，不替代专业人士意见。', '涉及安全、法律、医疗、财务或教育政策时，应提示家长二次核验。', '输出应尊重家庭差异，不用单一标准评价孩子或父母。']
DEFAULT_DELIVERABLES = ['周末活动方案', '准备清单', '照片记录模板']

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


def analyze_activity_trends(records: List[Dict[str, Any]], weeks: int = 4) -> List[TrendData]:
    """分析活动趋势"""
    trends = []
    if not records:
        return trends

    records_by_week = defaultdict(list)
    for record in records:
        try:
            if isinstance(record.get("timestamp"), str):
                record_date = datetime.fromisoformat(record["timestamp"]).date()
            elif isinstance(record.get("timestamp"), datetime):
                record_date = record["timestamp"].date()
            else:
                continue
            week_num = record_date.isocalendar()[1]
            week_key = f"{record_date.year}-W{week_num:02d}"
            records_by_week[week_key].append(record)
        except (ValueError, AttributeError):
            continue

    if not records_by_week:
        return trends

    sorted_weeks = sorted(records_by_week.keys())[-weeks:]
    weekly_counts = []
    weekly_durations = []
    weeks_labels = []

    for week in sorted_weeks:
        week_records = records_by_week[week]
        count = len(week_records)
        total_dur = sum(r.get("duration_hours", 0) or 0 for r in week_records)
        weekly_counts.append(float(count))
        weekly_durations.append(float(total_dur))
        weeks_labels.append(week)

    if weekly_counts:
        count_trend = TrendData(metric_name="每周活动次数", data_points=weekly_counts, dates=weeks_labels)
        count_trend.calculate_trend()
        trends.append(count_trend)

    if weekly_durations:
        duration_trend = TrendData(metric_name="每周活动时长", data_points=weekly_durations, dates=weeks_labels)
        duration_trend.calculate_trend()
        trends.append(duration_trend)

    return trends


def detect_anomalies(records: List[Dict[str, Any]], trends: List[TrendData]) -> List[Alert]:
    """检测异常情况"""
    alerts = []
    if not records:
        return alerts

    activity_types = defaultdict(int)
    for record in records:
        act_type = record.get("activity_type", "other")
        activity_types[act_type] += 1

    total = len(records)
    for act_type, count in activity_types.items():
        ratio = count / total
        if ratio > 0.7 and total > 5:
            alerts.append(Alert(
                alert_type="活动类型单一",
                severity="info",
                message=f"{act_type}类型活动占比超过70%，建议多样化",
                recommendation="尝试不同类型的活动，如户外、社交、艺术等"
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
            category="幼儿活动建议",
            priority=1,
            title="适合幼儿的周末活动",
            description=f"根据孩子月龄（{age_months}个月），建议选择感官刺激和亲子互动活动",
            action_items=[
                "室内游乐场或早教中心",
                "公园草地玩耍",
                "简单的亲子手工"
            ],
            rationale="幼儿需要多样化的感官刺激和亲子陪伴",
            expected_outcome="促进感官发展和亲子关系"
        ))
    elif age_months < 72:
        recommendations.append(Recommendation(
            category="学龄前活动建议",
            priority=1,
            title="适合学龄前的周末活动",
            description=f"根据孩子月龄（{age_months}个月），建议选择探索性和社交性活动",
            action_items=[
                "户外探险和自然探索",
                "图书馆阅读时光",
                "和小朋友一起玩耍"
            ],
            rationale="学龄前儿童好奇心强，需要更多探索机会",
            expected_outcome="培养探索精神和社交能力"
        ))
    else:
        recommendations.append(Recommendation(
            category="学龄儿童活动建议",
            priority=1,
            title="适合学龄儿童的周末活动",
            description=f"根据孩子月龄（{age_months}个月），建议选择益智和体育活动",
            action_items=[
                "体育运动如游泳、骑车",
                "博物馆或科技馆参观",
                "兴趣班或社交活动"
            ],
            rationale="学龄儿童需要全面发展，平衡学习和运动",
            expected_outcome="培养兴趣爱好和健康体魄"
        ))

    if not alerts and not recommendations:
        recommendations.append(Recommendation(
            category="活动规划习惯",
            priority=3,
            title="保持良好的活动规划习惯",
            description="继续丰富周末活动内容",
            action_items=["提前规划周末活动", "准备活动所需物品", "记录活动体验和收获"],
            rationale="合理的规划可以提高活动质量",
            expected_outcome="建立充实的周末活动体系"
        ))

    recommendations.sort(key=lambda x: x.priority)
    return recommendations


def aggregate_weekly_stats(records: List[Dict[str, Any]], week_offset: int = 0) -> Optional[WeeklyStats]:
    """聚合周统计数据"""
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

    activity_types = defaultdict(int)
    for r in week_records:
        act_type = r.get("activity_type", "other")
        activity_types[act_type] += 1

    stats = WeeklyStats(
        week_start=week_start.isoformat(),
        week_end=week_end.isoformat(),
        total_schedules=len(week_records),
        completed_schedules=len(week_records),
        completion_rate=100.0,
        food_category_distribution=dict(activity_types)
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
        trends = analyze_activity_trends(records, payload.get("history_weeks", 4))
        if trends:
            for trend in trends:
                facts.append(f"{trend.metric_name}：平均 {trend.average:.1f}，趋势 {trend.trend_direction}（{trend.trend_percentage:+.1f}%）")
    return facts


def build_analysis(payload: Dict[str, Any]) -> List[str]:
    """构建分析内容"""
    problem = payload.get("current_problem", "")
    history_weeks = payload.get("history_weeks", 4)
    records = payload.get("raw_records") or []
    child_profile = payload.get("child_profile", {})

    analysis = [
        f"当前问题聚焦：{problem}",
        f"建议回顾最近 {history_weeks} 周的活动安排。",
        "本 Skill 会优先输出可执行动作、记录字段和复盘指标。",
    ]
    for step in SKILL_FLOW:
        analysis.append(f"链路节点：{step}")

    if records:
        trends = analyze_activity_trends(records, history_weeks)
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
        "确定本周活动主题和类型",
        "查询天气和场地信息",
        "准备活动所需物品",
        "执行活动计划",
        "记录活动体验和照片"
    ]
    plan: List[Dict[str, str]] = []
    for i, task in enumerate(base_tasks, start=1):
        plan.append({
            "day": f"D{i}",
            "task": task,
            "owner": "家长/主要照护人",
            "evidence_to_record": "活动名称、时长、孩子反应、照片",
            "difficulty": "低" if i <= 3 else "中"
        })
    return plan


def build_deliverables(payload: Dict[str, Any]) -> Dict[str, Any]:
    """构建交付物"""
    deliverables = {
        "required": DEFAULT_DELIVERABLES,
        "tables": {
            "timeline": ["时间", "活动", "地点", "时长", "孩子反应", "备注"],
            "weekly_review": ["指标", "本周", "上周", "变化", "下一步"]
        },
        "templates": {
            "daily_log": "今天做了什么活动？孩子玩得开心吗？有什么收获？",
            "handoff_summary": "给家人的活动摘要：已执行活动、计划调整、注意事项。"
        }
    }
    records = payload.get("raw_records") or []
    if records:
        trends = analyze_activity_trends(records, payload.get("history_weeks", 4))
        if trends:
            deliverables["analysis_charts"] = {"trend_summary": [{"metric": t.metric_name, "average": round(t.average, 2), "trend": t.trend_direction, "change_percent": round(t.trend_percentage, 2)} for t in trends]}
    return deliverables


def next_fields() -> List[str]:
    """获取下次追踪字段"""
    return [
        "孩子年龄/月龄",
        "本周活动计划",
        "实际执行情况",
        "孩子反馈",
        "活动收获",
        "下周改进方向"
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
