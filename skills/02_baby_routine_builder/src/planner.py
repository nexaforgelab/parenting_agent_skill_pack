"""Planning engine for 宝宝作息规律培养 Agent.

增强版本：添加数据分析、异常检测、个性化推荐、上下文记忆、数据聚合
"""
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta, date
from collections import defaultdict
try:
    from .models import (
        TrendData, Alert, Recommendation, SessionContext,
        WeeklyStats, RoutineRecord, RoutineType
    )
except ImportError:
    from models import (
        TrendData, Alert, Recommendation, SessionContext,
        WeeklyStats, RoutineRecord, RoutineType
    )

SKILL_FLOW = ['记录 7 天作息', '分析睡眠、喂养、活动规律', '找出夜醒、短睡、晚睡原因', '生成适合月龄的作息建议', '每天提醒执行', '每周复盘']
SAFETY_NOTES = ['本 Skill 只做家庭记录、观察整理、提醒和沟通材料准备，不提供诊断、治疗方案或用药建议。', '出现呼吸困难、持续高热、严重过敏反应、精神状态异常、脱水、剧烈呕吐/腹泻、外伤等情况时，必须提示立即联系医生或急救。', '所有月龄、疫苗、营养、睡眠建议都应标注为一般性参考，并要求家长以当地儿科医生/公卫机构建议为准。']
DEFAULT_DELIVERABLES = ['宝宝作息表', '入睡提醒', '夜醒记录', '调整建议']

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


def analyze_routine_trends(records: List[Dict[str, Any]], days: int = 7) -> List[TrendData]:
    """分析作息趋势"""
    trends = []

    if not records:
        return trends

    records_by_date = defaultdict(list)
    for record in records:
        try:
            if isinstance(record.get("timestamp"), str):
                record_date = datetime.fromisoformat(record["timestamp"]).date()
            elif isinstance(record.get("timestamp"), datetime):
                record_date = record["timestamp"].date()
            else:
                continue
            records_by_date[record_date].append(record)
        except (ValueError, AttributeError):
            continue

    if not records_by_date:
        return trends

    sorted_dates = sorted(records_by_date.keys())
    if len(sorted_dates) > days:
        sorted_dates = sorted_dates[-days:]

    daily_counts = []
    daily_durations = []
    dates = []

    for d in sorted_dates:
        day_records = records_by_date[d]
        count = len(day_records)
        total_duration = sum(r.get("duration_minutes", 0) or 0 for r in day_records)
        daily_counts.append(count)
        daily_durations.append(total_duration)
        dates.append(d.isoformat())

    if daily_counts:
        count_trend = TrendData(
            metric_name="每日作息事件数",
            data_points=daily_counts,
            dates=dates
        )
        count_trend.calculate_trend()
        trends.append(count_trend)

    if daily_durations:
        duration_trend = TrendData(
            metric_name="每日总时长",
            data_points=daily_durations,
            dates=dates
        )
        duration_trend.calculate_trend()
        trends.append(duration_trend)

    return trends


def detect_anomalies(records: List[Dict[str, Any]], trends: List[TrendData]) -> List[Alert]:
    """检测异常情况"""
    alerts = []

    if not records:
        return alerts

    records_by_type = defaultdict(list)
    for record in records:
        routine_type = record.get("routine_type", "").lower()
        records_by_type[routine_type].append(record)

    for routine_type, type_records in records_by_type.items():
        if routine_type == "sleep":
            avg_duration = sum(r.get("duration_minutes", 0) or 0 for r in type_records) / len(type_records)
            if avg_duration < 240:
                alerts.append(Alert(
                    alert_type="睡眠时长不足",
                    severity="warning",
                    message=f"平均睡眠时长较短（{avg_duration/60:.1f}小时）",
                    recommendation="建议调整作息，增加睡眠时间"
                ))

        counts_by_date = defaultdict(int)
        for r in type_records:
            try:
                if isinstance(r.get("timestamp"), str):
                    record_date = datetime.fromisoformat(r["timestamp"]).date()
                elif isinstance(r.get("timestamp"), datetime):
                    record_date = r["timestamp"].date()
                else:
                    continue
                counts_by_date[record_date] += 1
            except (ValueError, AttributeError):
                continue

        for d, count in counts_by_date.items():
            if count > 8:
                alerts.append(Alert(
                    alert_type="作息过于频繁",
                    severity="info",
                    message=f"{d}日{routine_type}事件过多（{count}次）",
                    recommendation="建议适当调整作息节奏"
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

    recommended_sleep_hours = 0
    if age_months <= 1:
        recommended_sleep_hours = 16
    elif age_months <= 3:
        recommended_sleep_hours = 15
    elif age_months <= 6:
        recommended_sleep_hours = 14

    records_by_type = defaultdict(list)
    for record in records:
        routine_type = record.get("routine_type", "").lower()
        records_by_type[routine_type].append(record)

    sleep_records = records_by_type.get("sleep", [])
    if sleep_records:
        total_sleep = sum(r.get("duration_minutes", 0) or 0 for r in sleep_records) / 60
        if total_sleep < recommended_sleep_hours * 0.8:
            recommendations.append(Recommendation(
                category="作息调整",
                priority=1,
                title="增加睡眠时间",
                description=f"宝宝当前睡眠约{total_sleep:.0f}小时，建议{recommended_sleep_hours}小时",
                action_items=[
                    "提前入睡时间",
                    "减少白天小睡对夜间睡眠的影响",
                    "建立固定睡前仪式"
                ],
                rationale="充足的睡眠对生长发育至关重要",
                expected_outcome="达到推荐睡眠时长"
            ))

    routine_types = list(records_by_type.keys())
    if len(routine_types) < 3:
        recommendations.append(Recommendation(
            category="作息丰富",
            priority=2,
            title="多样化作息活动",
            description="建议增加更多类型的作息活动，促进全面发展",
            action_items=[
                "增加户外活动时间",
                "加入互动游戏",
                "规律洗澡时间"
            ],
            rationale="多样化的活动有助于感官和运动发育",
            expected_outcome="建立规律的作息体系"
        ))

    if not alerts:
        recommendations.append(Recommendation(
            category="习惯养成",
            priority=3,
            title="保持良好的作息记录习惯",
            description="继续坚持记录作息情况，有助于及时发现异常",
            action_items=[
                "每天固定时间记录",
                "记录睡眠质量和时长",
                "观察并记录宝宝反应"
            ],
            rationale="持续的记录有助于发现长期趋势",
            expected_outcome="建立完整的作息档案"
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

    total_routines = len(week_records)

    routine_type_dist = defaultdict(int)
    total_sleep_minutes = 0

    for r in week_records:
        rt = r.get("routine_type", "unknown")
        routine_type_dist[rt] += 1

        if rt.lower() == "sleep":
            total_sleep_minutes += r.get("duration_minutes", 0) or 0

    avg_sleep_hours = total_sleep_minutes / 60 / 7 if total_sleep_minutes > 0 else 0

    stats = WeeklyStats(
        week_start=week_start.isoformat(),
        week_end=week_end.isoformat(),
        total_routines=total_routines,
        average_daily_routines=total_routines / 7,
        routine_type_distribution=dict(routine_type_dist),
        average_sleep_hours=avg_sleep_hours
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
        trends = analyze_routine_trends(records, payload.get("history_days", 7))
        if trends:
            for trend in trends:
                facts.append(
                    f"{trend.metric_name}：平均 {trend.average:.1f}，"
                    f"趋势 {trend.trend_direction}（{trend.trend_percentage:+.1f}%）"
                )

    return facts


def build_analysis(payload: Dict[str, Any]) -> List[str]:
    """构建分析内容"""
    problem = payload.get("current_problem", "")
    history_days = payload.get("history_days", 7)
    records = payload.get("raw_records") or []
    child_profile = payload.get("child_profile", {})

    analysis = [
        f"当前问题聚焦：{problem}",
        f"建议先建立最近 {history_days} 天的家庭基线，再判断趋势。",
        "本 Skill 会优先输出可执行动作、记录字段和复盘指标。",
    ]

    for step in SKILL_FLOW:
        analysis.append(f"链路节点：{step}")

    if records:
        trends = analyze_routine_trends(records, history_days)
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
        "补齐孩子画像和家庭限制条件",
        "把今天相关事件按时间线记录",
        "执行一个低压力动作并记录孩子反应",
        "晚上用 3 分钟复盘有效/无效做法",
        "一周后比较趋势并调整计划",
    ]

    records = payload.get("raw_records") or []
    if records:
        base_tasks.insert(0, f"分析最近 {len(records)} 条记录的趋势")

    plan: List[Dict[str, str]] = []
    for i, task in enumerate(base_tasks, start=1):
        plan.append({
            "day": f"D{i}",
            "task": task,
            "owner": "家长/主要照护人",
            "evidence_to_record": "时间、触发点、执行方式、孩子反应",
            "difficulty": "低" if i <= 3 else "中"
        })
    return plan


def build_deliverables(payload: Dict[str, Any]) -> Dict[str, Any]:
    """构建交付物"""
    deliverables = {
        "required": DEFAULT_DELIVERABLES,
        "tables": {
            "timeline": ["时间", "事件", "输入", "处理", "结果", "备注"],
            "weekly_review": ["指标", "本周", "上周", "变化", "下一步"]
        },
        "templates": {
            "daily_log": "今天发生了什么？我做了什么？孩子反应如何？下一次要调整什么？",
            "handoff_summary": "给专业人士/老师/家人的沟通摘要：事实、时间线、已尝试方法、待确认问题。"
        }
    }

    records = payload.get("raw_records") or []
    if records:
        trends = analyze_routine_trends(records, payload.get("history_days", 7))
        if trends:
            deliverables["analysis_charts"] = {
                "trend_summary": [
                    {
                        "metric": t.metric_name,
                        "average": round(t.average, 2),
                        "trend": t.trend_direction,
                        "change_percent": round(t.trend_percentage, 2)
                    }
                    for t in trends
                ]
            }

    return deliverables


def next_fields() -> List[str]:
    """获取下次追踪字段"""
    return [
        "孩子年龄/月龄",
        "今天新增记录",
        "执行了哪一步",
        "孩子反应",
        "家长感受",
        "需要调整的限制条件"
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
