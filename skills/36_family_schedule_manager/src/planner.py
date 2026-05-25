"""Planning engine for 家庭日程管理 Agent.

增强版本：添加数据分析、异常检测、个性化推荐、上下文记忆、数据聚合
"""
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta, date
from collections import defaultdict
try:
    from .models import (
        TrendData, Alert, Recommendation, SessionContext,
        WeeklyStats, ScheduleItem, Conflict
    )
except ImportError:
    from models import (
        TrendData, Alert, Recommendation, SessionContext,
        WeeklyStats, ScheduleItem, Conflict
    )

SKILL_FLOW = ['导入家人日程', '识别接送、课程、会议、体检', '自动排程', '冲突提醒', '每天生成家庭日程卡']
SAFETY_NOTES = ['本 Skill 提供家庭教育和生活管理建议，不替代专业人士意见。', '涉及安全、法律、医疗、财务或教育政策时，应提示家长二次核验。', '输出应尊重家庭差异，不用单一标准评价孩子或父母。']
DEFAULT_DELIVERABLES = ['家庭日历', '接送提醒', '冲突清单']

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


def analyze_schedule_trends(records: List[Dict[str, Any]], days: int = 7) -> List[TrendData]:
    """分析日程趋势

    Args:
        records: 日程记录列表
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

    daily_counts = []
    daily_completions = []
    daily_durations = []
    dates = []

    for d in sorted_dates:
        day_records = records_by_date[d]
        count = len(day_records)
        completed = sum(1 for r in day_records if r.get("is_completed", False))
        total_duration = sum(r.get("duration_minutes", 0) or 0 for r in day_records)

        daily_counts.append(float(count))
        daily_completions.append(float(completed))
        daily_durations.append(float(total_duration))
        dates.append(d.isoformat())

    if daily_counts:
        count_trend = TrendData(
            metric_name="每日日程数量",
            data_points=daily_counts,
            dates=dates
        )
        count_trend.calculate_trend()
        trends.append(count_trend)

    if daily_completions and daily_counts:
        completion_rates = [
            (c / n * 100) if n > 0 else 0
            for c, n in zip(daily_completions, daily_counts)
        ]
        completion_trend = TrendData(
            metric_name="每日完成率(%)",
            data_points=completion_rates,
            dates=dates
        )
        completion_trend.calculate_trend()
        trends.append(completion_trend)

    if daily_durations:
        duration_trend = TrendData(
            metric_name="每日总时长(分钟)",
            data_points=daily_durations,
            dates=dates
        )
        duration_trend.calculate_trend()
        trends.append(duration_trend)

    return trends


def detect_conflicts(records: List[Dict[str, Any]]) -> List[Conflict]:
    """检测日程冲突

    Args:
        records: 日程记录列表

    Returns:
        冲突列表
    """
    conflicts = []

    if not records:
        return conflicts

    schedule_items = []
    for record in records:
        try:
            if isinstance(record.get("timestamp"), str):
                item_time = datetime.fromisoformat(record["timestamp"])
            elif isinstance(record.get("timestamp"), datetime):
                item_time = record["timestamp"]
            else:
                continue

            duration = record.get("duration_minutes", 0) or 0
            schedule_items.append({
                "title": record.get("title", "未命名"),
                "time": item_time,
                "end_time": item_time + timedelta(minutes=duration),
                "type": record.get("schedule_type", "other")
            })
        except (ValueError, AttributeError):
            continue

    schedule_items.sort(key=lambda x: x["time"])

    for i in range(len(schedule_items)):
        for j in range(i + 1, len(schedule_items)):
            item_a = schedule_items[i]
            item_b = schedule_items[j]

            if item_a["end_time"] > item_b["time"]:
                overlap_start = item_b["time"]
                overlap_end = min(item_a["end_time"], item_b["end_time"])
                overlap_minutes = int((overlap_end - overlap_start).total_seconds() / 60)

                if overlap_minutes > 0:
                    status = "severe" if overlap_minutes > 60 else "moderate" if overlap_minutes > 30 else "minor"
                    suggestion = f"建议调整{item_b['title']}的时间，或委托他人协助"

                    conflicts.append(Conflict(
                        schedule_a=item_a["title"],
                        schedule_b=item_b["title"],
                        overlap_minutes=overlap_minutes,
                        status=status,
                        suggestion=suggestion
                    ))

    return conflicts


def detect_anomalies(records: List[Dict[str, Any]], trends: List[TrendData]) -> List[Alert]:
    """检测异常情况

    Args:
        records: 日程记录列表
        trends: 趋势数据列表

    Returns:
        告警列表
    """
    alerts = []

    if not records:
        return alerts

    schedule_type_counts = defaultdict(int)
    for record in records:
        st = record.get("schedule_type", "other")
        schedule_type_counts[st] += 1

    total_records = len(records)
    for st_type, count in schedule_type_counts.items():
        ratio = count / total_records
        if ratio > 0.7 and total_records > 5:
            alerts.append(Alert(
                alert_type="日程类型单一",
                severity="info",
                message=f"{st_type}类型日程占比超过70%，可能需要平衡其他活动",
                recommendation="建议增加多样化的活动，如户外运动、亲子互动等"
            ))

    for trend in trends:
        if trend.metric_name == "每日完成率(%)":
            if trend.trend_direction == "decreasing" and trend.trend_percentage < -20:
                alerts.append(Alert(
                    alert_type="完成率下降",
                    severity="warning",
                    message=f"日程完成率较之前下降了 {abs(trend.trend_percentage):.1f}%",
                    recommendation="建议减少日程数量或调整日程优先级，确保核心任务完成"
                ))

            if trend.average < 50:
                alerts.append(Alert(
                    alert_type="完成率偏低",
                    severity="warning",
                    message=f"平均完成率仅为 {trend.average:.1f}%，可能存在日程过密问题",
                    recommendation="建议评估日程必要性，优化时间分配"
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
        records: 日程记录列表
        trends: 趋势数据列表
        child_profile: 孩子画像
        alerts: 告警列表

    Returns:
        推荐列表
    """
    recommendations = []

    age_months = child_profile.get("age_months", 0)

    if age_months < 36:
        recommendations.append(Recommendation(
            category="日程安排优化",
            priority=1,
            title="幼儿期日程建议",
            description=f"根据孩子月龄（{age_months}个月），建议保持日程简洁，每日不超过3-4个固定活动",
            action_items=[
                "留出充足的自由玩耍时间",
                "避免连续活动超过1小时",
                "保证午睡时间不被压缩"
            ],
            rationale="幼儿需要大量自由探索时间，过密的日程会影响发展",
            expected_outcome="孩子情绪更稳定，亲子关系更和谐"
        ))
    elif age_months < 84:
        recommendations.append(Recommendation(
            category="日程安排优化",
            priority=1,
            title="学龄前日程建议",
            description=f"根据孩子月龄（{age_months}个月），建议兴趣班不超过2个，留出社交和户外时间",
            action_items=[
                "每周至少2次户外活动",
                "保留固定的亲子互动时间",
                "兴趣班选择要符合孩子兴趣"
            ],
            rationale="学龄前儿童需要全面发展，过度安排会影响社交能力和创造力",
            expected_outcome="孩子更自信、社交能力更强"
        ))

    conflicts = detect_conflicts(records)
    if conflicts:
        severe_conflicts = [c for c in conflicts if c.status.value in ["severe", "moderate"]]
        if severe_conflicts:
            recommendations.append(Recommendation(
                category="冲突解决",
                priority=1,
                title="优化日程冲突",
                description=f"检测到 {len(severe_conflicts)} 个需要关注的日程冲突",
                action_items=[
                    "评估各日程的优先级和必要性",
                    "考虑合并或调整时间相近的活动",
                    "寻求家人或朋友协助"
                ],
                rationale="日程冲突会导致压力增加，影响执行效果",
                expected_outcome="减少日程冲突，提高执行效率"
            ))

    for trend in trends:
        if trend.metric_name == "每日完成率(%)" and trend.average < 70:
            recommendations.append(Recommendation(
                category="执行效率提升",
                priority=2,
                title="提高日程执行率",
                description=f"当前完成率为 {trend.average:.1f}%，建议优化日程安排",
                action_items=[
                    "将复杂任务拆分为小步骤",
                    "使用日程提醒工具",
                    "每晚提前规划次日日程"
                ],
                rationale="适当的完成率目标可以提升成就感",
                expected_outcome="完成率提升到80%以上"
            ))

    if not alerts and not recommendations:
        recommendations.append(Recommendation(
            category="日程管理习惯",
            priority=3,
            title="保持良好的日程管理习惯",
            description="当前日程安排合理，继续坚持记录和分析",
            action_items=[
                "每天记录日程执行情况",
                "定期复盘日程安排效果",
                "根据季节调整活动内容"
            ],
            rationale="持续的记录有助于发现长期趋势",
            expected_outcome="建立科学的家庭日程管理体系"
        ))

    recommendations.sort(key=lambda x: x.priority)
    return recommendations


def aggregate_weekly_stats(records: List[Dict[str, Any]], week_offset: int = 0) -> Optional[WeeklyStats]:
    """聚合周统计数据

    Args:
        records: 日程记录列表
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

    total_schedules = len(week_records)
    completed_schedules = sum(1 for r in week_records if r.get("is_completed", False))
    completion_rate = (completed_schedules / total_schedules * 100) if total_schedules > 0 else 0

    schedule_type_dist = defaultdict(int)
    for r in week_records:
        st = r.get("schedule_type", "other")
        schedule_type_dist[st] += 1

    conflicts = detect_conflicts(week_records)

    stats = WeeklyStats(
        week_start=week_start.isoformat(),
        week_end=week_end.isoformat(),
        total_schedules=total_schedules,
        completed_schedules=completed_schedules,
        completion_rate=completion_rate,
        schedule_type_distribution=dict(schedule_type_dist),
        conflict_count=len(conflicts)
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
        trends = analyze_schedule_trends(records, payload.get("history_days", 7))
        if trends:
            for trend in trends:
                facts.append(
                    f"{trend.metric_name}：平均 {trend.average:.1f}，"
                    f"趋势 {trend.trend_direction}（{trend.trend_percentage:+.1f}%）"
                )

        conflicts = detect_conflicts(records)
        if conflicts:
            facts.append(f"检测到 {len(conflicts)} 个日程冲突")

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
        trends = analyze_schedule_trends(records, history_days)
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
        conflicts = detect_conflicts(records)
        if conflicts:
            base_tasks.insert(0, f"解决 {len(conflicts)} 个日程冲突")

        trends = analyze_schedule_trends(records, payload.get("history_days", 7))
        if trends:
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
        trends = analyze_schedule_trends(records, payload.get("history_days", 7))
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

        conflicts = detect_conflicts(records)
        if conflicts:
            deliverables["conflict_list"] = [
                {
                    "schedule_a": c.schedule_a,
                    "schedule_b": c.schedule_b,
                    "overlap_minutes": c.overlap_minutes,
                    "suggestion": c.suggestion
                }
                for c in conflicts
            ]

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
