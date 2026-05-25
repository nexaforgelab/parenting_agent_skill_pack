"""Planning engine for 新生儿喂养记录 Agent.

增强版本：添加数据分析、异常检测、个性化推荐、上下文记忆、数据聚合
"""
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta, date
from collections import defaultdict
try:
    from .models import (
        TrendData, Alert, Recommendation, SessionContext,
        WeeklyStats, FeedingRecord, FeedingType
    )
except ImportError:
    from models import (
        TrendData, Alert, Recommendation, SessionContext,
        WeeklyStats, FeedingRecord, FeedingType
    )

SKILL_FLOW = ['语音/文字记录喂奶时间', '自动区分母乳、奶粉、混合喂养', '记录奶量、间隔、排便情况', '生成每日喂养曲线', '发现异常波动后提醒家长关注']
SAFETY_NOTES = ['本 Skill 只做家庭记录、观察整理、提醒和沟通材料准备，不提供诊断、治疗方案或用药建议。', '出现呼吸困难、持续高热、严重过敏反应、精神状态异常、脱水、剧烈呕吐/腹泻、外伤等情况时，必须提示立即联系医生或急救。', '所有月龄、疫苗、营养、睡眠建议都应标注为一般性参考，并要求家长以当地儿科医生/公卫机构建议为准。']
DEFAULT_DELIVERABLES = ['每日喂养表', '睡眠表', '排便记录', '宝宝作息趋势图']

_context_store: Dict[str, SessionContext] = {}


def get_or_create_context(session_id: str) -> SessionContext:
    """获取或创建会话上下文

    Args:
        session_id: 会话ID

    Returns:
        会话上下文对象
    """
    if session_id not in _context_store:
        _context_store[session_id] = SessionContext(session_id=session_id)
    return _context_store[session_id]


def update_context(session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
    """更新会话上下文

    Args:
        session_id: 会话ID
        role: 角色（user/assistant）
        content: 内容
        metadata: 额外元数据
    """
    context = get_or_create_context(session_id)
    context.add_interaction(role, content, metadata)


def analyze_feeding_trends(records: List[Dict[str, Any]], days: int = 7) -> List[TrendData]:
    """分析喂养趋势

    Args:
        records: 喂养记录列表
        days: 分析天数

    Returns:
        趋势数据列表
    """
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

    daily_amounts = []
    daily_counts = []
    daily_intervals = []
    dates = []

    for d in sorted_dates:
        day_records = records_by_date[d]
        total_amount = sum(r.get("amount_ml", 0) or 0 for r in day_records)
        count = len(day_records)
        daily_amounts.append(total_amount)
        daily_counts.append(count)
        dates.append(d.isoformat())

        if len(day_records) > 1:
            timestamps = []
            for r in day_records:
                try:
                    if isinstance(r.get("timestamp"), str):
                        timestamps.append(datetime.fromisoformat(r["timestamp"]))
                    elif isinstance(r.get("timestamp"), datetime):
                        timestamps.append(r["timestamp"])
                except (ValueError, AttributeError):
                    continue
            if len(timestamps) >= 2:
                intervals = []
                sorted_ts = sorted(timestamps)
                for i in range(1, len(sorted_ts)):
                    diff = (sorted_ts[i] - sorted_ts[i-1]).total_seconds() / 3600
                    intervals.append(diff)
                if intervals:
                    daily_intervals.append(sum(intervals) / len(intervals))

    if daily_amounts:
        amount_trend = TrendData(
            metric_name="每日喂养总量",
            data_points=daily_amounts,
            dates=dates
        )
        amount_trend.calculate_trend()
        trends.append(amount_trend)

    if daily_counts:
        count_trend = TrendData(
            metric_name="每日喂养次数",
            data_points=[float(c) for c in daily_counts],
            dates=dates
        )
        count_trend.calculate_trend()
        trends.append(count_trend)

    if daily_intervals:
        interval_trend = TrendData(
            metric_name="平均喂养间隔",
            data_points=daily_intervals,
            dates=dates
        )
        interval_trend.calculate_trend()
        trends.append(interval_trend)

    return trends


def detect_anomalies(records: List[Dict[str, Any]], trends: List[TrendData]) -> List[Alert]:
    """检测异常情况

    Args:
        records: 喂养记录列表
        trends: 趋势数据列表

    Returns:
        告警列表
    """
    alerts = []

    if not records:
        return alerts

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

    for trend in trends:
        if trend.metric_name == "每日喂养总量":
            if trend.trend_direction == "decreasing" and trend.trend_percentage < -20:
                alerts.append(Alert(
                    alert_type="喂养量下降",
                    severity="warning",
                    message=f"宝宝的喂养量较之前下降了 {abs(trend.trend_percentage):.1f}%，需要关注",
                    recommendation="建议观察宝宝是否有不适或其他异常表现，如持续下降建议咨询儿科医生"
                ))

            if trend.average > 0:
                for i, val in enumerate(trend.data_points):
                    if val < trend.average * 0.5:
                        alerts.append(Alert(
                            alert_type="喂养量异常低",
                            severity="warning",
                            message=f"在 {trend.dates[i]} 喂养量异常偏低（{val}ml）",
                            recommendation="检查宝宝是否有食欲不振、腹胀或其他不适症状"
                        ))

        elif trend.metric_name == "每日喂养次数":
            if trend.trend_direction == "decreasing" and trend.trend_percentage < -30:
                alerts.append(Alert(
                    alert_type="喂养次数下降",
                    severity="info",
                    message=f"宝宝的喂养次数较之前下降了 {abs(trend.trend_percentage):.1f}%",
                    recommendation="这可能是正常的生长曲线变化，继续观察食欲和精神状态"
                ))

    bowel_movements = defaultdict(int)
    for record in records:
        bm = record.get("bowel_movement", "").lower()
        if bm in ["loose", "constipated", "hard", "diarrhea"]:
            bowel_movements[bm] += 1

    total_bowel = sum(bowel_movements.values())
    if total_bowel > 0:
        for bm_type, count in bowel_movements.items():
            ratio = count / total_bowel
            if ratio > 0.5:
                alerts.append(Alert(
                    alert_type="排便异常",
                    severity="warning",
                    message=f"超过 {ratio*100:.0f}% 的记录显示排便{bm_type}",
                    recommendation="建议记录饮食，观察是否与特定食物相关，必要时咨询医生"
                ))

    return alerts


def generate_personalized_recommendations(
    records: List[Dict[str, Any]],
    trends: List[TrendData],
    child_profile: Dict[str, Any],
    alerts: List[Alert]
) -> List[Recommendation]:
    """生成个性化推荐

    Args:
        records: 喂养记录列表
        trends: 趋势数据列表
        child_profile: 孩子画像
        alerts: 告警列表

    Returns:
        推荐列表
    """
    recommendations = []

    age_months = child_profile.get("age_months", 0)
    weight_kg = child_profile.get("weight_kg", 0)

    recommended_daily_amount = 0
    if 0 < age_months <= 1:
        recommended_daily_amount = weight_kg * 150 if weight_kg > 0 else 450
    elif 1 < age_months <= 3:
        recommended_daily_amount = weight_kg * 130 if weight_kg > 0 else 600
    elif 3 < age_months <= 6:
        recommended_daily_amount = weight_kg * 120 if weight_kg > 0 else 750

    for trend in trends:
        if trend.metric_name == "每日喂养总量" and trend.average > 0:
            gap = recommended_daily_amount - trend.average
            if gap > recommended_daily_amount * 0.2:
                recommendations.append(Recommendation(
                    category="喂养量调整",
                    priority=1,
                    title="适当增加喂养量",
                    description=f"根据宝宝月龄（{age_months}个月）和体重（{weight_kg}kg），建议每日喂养量约 {recommended_daily_amount:.0f}ml，当前平均 {trend.average:.0f}ml",
                    action_items=[
                        "尝试少量多次喂养",
                        "观察宝宝饥饿信号",
                        "不要强迫喂养"
                    ],
                    rationale="合理的喂养量对宝宝生长发育至关重要",
                    expected_outcome="达到推荐喂养量，促进健康成长"
                ))

    feeding_type_counts = defaultdict(int)
    for record in records:
        ft = record.get("feeding_type", "")
        feeding_type_counts[ft] += 1

    if "breast" in feeding_type_counts or "formula" in feeding_type_counts:
        if feeding_type_counts.get("breast", 0) > feeding_type_counts.get("formula", 0) * 3:
            recommendations.append(Recommendation(
                category="喂养方式优化",
                priority=2,
                title="考虑补充配方奶",
                description="母乳喂养占比过高，可能需要适当补充配方奶以满足营养需求",
                action_items=[
                    "咨询医生是否需要补充配方奶",
                    "观察宝宝生长发育曲线",
                    "记录母乳喂养时长"
                ],
                rationale="混合喂养可以更好地满足营养需求",
                expected_outcome="营养摄入更加均衡"
            ))

    if not alerts:
        recommendations.append(Recommendation(
            category="喂养习惯",
            priority=3,
            title="保持良好的喂养记录习惯",
            description="继续坚持记录喂养情况，有助于及时发现异常",
            action_items=[
                "每天记录至少3-5次喂养",
                "记录喂养间隔和奶量",
                "观察并记录宝宝反应"
            ],
            rationale="持续的记录有助于发现长期趋势",
            expected_outcome="建立完整的喂养档案"
        ))

    recommendations.sort(key=lambda x: x.priority)
    return recommendations


def aggregate_weekly_stats(records: List[Dict[str, Any]], week_offset: int = 0) -> Optional[WeeklyStats]:
    """聚合周统计数据

    Args:
        records: 喂养记录列表
        week_offset: 周偏移（0=本周，-1=上周）

    Returns:
        周统计数据对象
    """
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

    total_feedings = len(week_records)
    total_amount = sum(r.get("amount_ml", 0) or 0 for r in week_records)
    days_with_records = len(set(
        datetime.fromisoformat(r["timestamp"]).date() if isinstance(r.get("timestamp"), str)
        else r["timestamp"].date()
        for r in week_records
        if r.get("timestamp")
    ))

    feeding_type_dist = defaultdict(int)
    bowel_movement_dist = defaultdict(int)

    for r in week_records:
        ft = r.get("feeding_type", "unknown")
        feeding_type_dist[ft] += 1

        bm = r.get("bowel_movement", "")
        if bm:
            bowel_movement_dist[bm] += 1

    stats = WeeklyStats(
        week_start=week_start.isoformat(),
        week_end=week_end.isoformat(),
        total_feedings=total_feedings,
        average_daily_feedings=total_feedings / 7 if days_with_records == 0 else total_feedings / days_with_records,
        total_amount_ml=total_amount,
        average_amount_ml=total_amount / 7 if days_with_records == 0 else total_amount / days_with_records,
        feeding_type_distribution=dict(feeding_type_dist),
        bowel_movement_summary=dict(bowel_movement_dist)
    )

    return stats


def build_known_facts(payload: Dict[str, Any]) -> List[str]:
    """构建已知事实列表

    Args:
        payload: 输入数据

    Returns:
        事实列表
    """
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
        trends = analyze_feeding_trends(records, payload.get("history_days", 7))
        if trends:
            for trend in trends:
                facts.append(
                    f"{trend.metric_name}：平均 {trend.average:.1f}，"
                    f"趋势 {trend.trend_direction}（{trend.trend_percentage:+.1f}%）"
                )

    return facts


def build_analysis(payload: Dict[str, Any]) -> List[str]:
    """构建分析内容

    Args:
        payload: 输入数据

    Returns:
        分析内容列表
    """
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
        trends = analyze_feeding_trends(records, history_days)
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
    """构建行动计划

    Args:
        payload: 输入数据

    Returns:
        行动计划列表
    """
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
    """构建交付物

    Args:
        payload: 输入数据

    Returns:
        交付物字典
    """
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
        trends = analyze_feeding_trends(records, payload.get("history_days", 7))
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
    """获取下次追踪字段

    Returns:
        字段列表
    """
    return [
        "孩子年龄/月龄",
        "今天新增记录",
        "执行了哪一步",
        "孩子反应",
        "家长感受",
        "需要调整的限制条件"
    ]


def generate_session_summary(session_id: str) -> Optional[Dict[str, Any]]:
    """生成会话摘要

    Args:
        session_id: 会话ID

    Returns:
        会话摘要字典
    """
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
    """清除会话上下文

    Args:
        session_id: 会话ID

    Returns:
        是否成功清除
    """
    if session_id in _context_store:
        del _context_store[session_id]
        return True
    return False
