"""Planning engine for 幼儿习惯养成 Agent.

增强版本：添加数据分析、异常检测、个性化推荐、上下文记忆、数据聚合
"""
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta, date
from collections import defaultdict

try:
    from .models import (
        TrendData, Alert, Recommendation, SessionContext,
        WeeklyStats, HabitDefinition, HabitRecord, HabitCategory
    )
except ImportError:
    from models import (
        TrendData, Alert, Recommendation, SessionContext,
        WeeklyStats, HabitDefinition, HabitRecord, HabitCategory
    )

SKILL_FLOW = ['选择习惯类型', '设定小目标', '每日打卡', '正负反馈记录', '每周回顾调整']
SAFETY_NOTES = ['本 Skill 提供家庭教育和生活管理建议，不替代专业人士意见。', '涉及安全、法律、医疗、财务或教育政策时，应提示家长二次核验。', '输出应尊重家庭差异，不用单一标准评价孩子或父母。']
DEFAULT_DELIVERABLES = ['习惯养成计划', '打卡表格', '进度报告']

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


def analyze_habit_trends(records: List[Dict[str, Any]], days: int = 7) -> List[TrendData]:
    """分析习惯趋势

    Args:
        records: 习惯记录列表
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

    daily_completion = []
    daily_quality = []
    dates = []

    for d in sorted_dates:
        day_records = records_by_date[d]
        total_completed = sum(1 for r in day_records if r.get("completed", False))
        total_records = len(day_records)

        completion_rate = (total_completed / total_records * 100) if total_records > 0 else 0
        daily_completion.append(completion_rate)

        quality_scores = [r.get("quality_score", 0) for r in day_records if r.get("quality_score") is not None]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        daily_quality.append(avg_quality)

        dates.append(d.isoformat())

    if daily_completion:
        completion_trend = TrendData(
            metric_name="每日完成率",
            data_points=daily_completion,
            dates=dates
        )
        completion_trend.calculate_trend()
        trends.append(completion_trend)

    if daily_quality:
        quality_trend = TrendData(
            metric_name="平均质量评分",
            data_points=daily_quality,
            dates=dates
        )
        quality_trend.calculate_trend()
        trends.append(quality_trend)

    return trends


def detect_habit_anomalies(records: List[Dict[str, Any]], trends: List[TrendData]) -> List[Alert]:
    """检测习惯异常

    Args:
        records: 习惯记录列表
        trends: 趋势数据列表

    Returns:
        告警列表
    """
    alerts = []

    if not records:
        return alerts

    for trend in trends:
        if trend.metric_name == "每日完成率":
            if trend.trend_direction == "decreasing" and trend.trend_percentage < -20:
                alerts.append(Alert(
                    alert_type="完成率下降",
                    severity="warning",
                    message=f"习惯完成率下降了 {abs(trend.trend_percentage):.1f}%，需要关注",
                    recommendation="分析原因：是目标太难、动力下降还是其他因素？适当调整计划"
                ))

            if trend.average > 0 and trend.average < 50:
                alerts.append(Alert(
                    alert_type="完成率偏低",
                    severity="info",
                    message=f"习惯完成率只有 {trend.average:.1f}%，需要加强",
                    recommendation="从简单的目标开始，逐步增加难度，使用正向激励"
                ))

        elif trend.metric_name == "平均质量评分":
            if trend.trend_direction == "decreasing" and trend.trend_percentage < -15:
                alerts.append(Alert(
                    alert_type="质量下降",
                    severity="warning",
                    message=f"习惯执行质量下降了 {abs(trend.trend_percentage):.1f}%",
                    recommendation="可能孩子对习惯失去兴趣，考虑换一种方式或增加趣味性"
                ))

    habit_ids = defaultdict(int)
    for record in records:
        hid = record.get("habit_id", "unknown")
        habit_ids[hid] += 1

    if len(habit_ids) > 3:
        least_progress = min(habit_ids.items(), key=lambda x: x[1])
        if least_progress[1] < 3:
            alerts.append(Alert(
                alert_type="习惯进度不均",
                severity="info",
                message=f"有些习惯的训练次数较少（{least_progress[0]}只有{least_progress[1]}次）",
                recommendation="平衡各习惯的训练，确保每项习惯都有足够练习"
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
        records: 习惯记录列表
        trends: 趋势数据列表
        child_profile: 孩子画像
        alerts: 告警列表

    Returns:
        推荐列表
    """
    recommendations = []

    age_months = child_profile.get("age_months", 0)
    recommended_habits = min(3, max(1, age_months // 24))

    current_habits = len(set(r.get("habit_id", "") for r in records))
    if current_habits < recommended_habits:
        recommendations.append(Recommendation(
            category="习惯选择",
            priority=1,
            title="建议增加习惯数量",
            description=f"根据孩子月龄（{age_months}个月），建议同时培养 {recommended_habits} 个习惯，当前 {current_habits} 个",
            action_items=[
                "选择与日常生活相关的习惯",
                "从简单易行的习惯开始",
                "每个习惯设定明确的目标"
            ],
            rationale="适度的习惯数量可以保证每个习惯都得到足够的练习",
            expected_outcome="建立全面的好习惯体系"
        ))

    for trend in trends:
        if trend.metric_name == "每日完成率" and trend.average < 70:
            recommendations.append(Recommendation(
                category="执行策略",
                priority=1,
                title="提高习惯完成率",
                description=f"当前完成率为 {trend.average:.1f}%，建议使用奖励机制",
                action_items=[
                    "使用贴纸或星星奖励系统",
                    "完成一周后给予小奖励",
                    "与孩子一起庆祝进步"
                ],
                rationale="正向激励可以提高孩子的积极性",
                expected_outcome="完成率达到70%以上"
            ))

    for alert in alerts:
        if alert.alert_type == "完成率下降":
            recommendations.append(Recommendation(
                category="调整计划",
                priority=2,
                title="重新评估习惯目标",
                description="当前习惯可能目标设置过高或方式不够有趣",
                action_items=[
                    "降低目标难度",
                    "增加趣味性元素",
                    "使用游戏化的方式"
                ],
                rationale="合适的难度才能保持孩子的兴趣",
                expected_outcome="重新建立稳定的习惯"
            ))

    if not alerts and len(records) >= 5:
        recommendations.append(Recommendation(
            category="巩固习惯",
            priority=3,
            title="巩固已建立的习惯",
            description="继续保持当前的良好习惯",
            action_items=[
                "坚持每日打卡",
                "定期回顾进步",
                "适度增加挑战"
            ],
            rationale="巩固期是习惯养成的关键阶段",
            expected_outcome="习惯成为自然行为"
        ))

    recommendations.sort(key=lambda x: x.priority)
    return recommendations


def aggregate_weekly_stats(records: List[Dict[str, Any]], week_offset: int = 0) -> Optional[WeeklyStats]:
    """聚合周统计数据

    Args:
        records: 习惯记录列表
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

    total_records = len(week_records)
    completed_records = sum(1 for r in week_records if r.get("completed", False))
    completion_rate = (completed_records / total_records * 100) if total_records > 0 else 0

    quality_scores = [r.get("quality_score", 0) for r in week_records if r.get("quality_score") is not None]
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0

    rewards_count = sum(1 for r in week_records if r.get("reward_received", ""))
    habits_completed = set(r.get("habit_id", "") for r in week_records if r.get("completed", False))

    return WeeklyStats(
        week_start=week_start.isoformat(),
        week_end=week_end.isoformat(),
        total_records=total_records,
        completion_rate=completion_rate,
        average_quality_score=avg_quality,
        streak_days=0,
        rewards_earned=rewards_count,
        habits_established=list(habits_completed)
    )


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
        trends = analyze_habit_trends(records, payload.get("history_days", 7))
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
        f"建议先建立最近 {history_days} 天的习惯基线，再判断趋势。",
        "本 Skill 会优先输出可执行动作、记录字段和复盘指标。",
    ]

    for step in SKILL_FLOW:
        analysis.append(f"链路节点：{step}")

    if records:
        trends = analyze_habit_trends(records, history_days)
        alerts = detect_habit_anomalies(records, trends)

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
        "选择要培养的习惯并设定目标",
        "执行习惯并记录完成情况",
        "晚上复盘当天表现",
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
            "evidence_to_record": "时间、完成情况、质量评分、奖励",
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
            "daily_log": "今天完成了哪些习惯？质量如何？获得什么奖励？",
            "handoff_summary": "给专业人士/老师/家人的沟通摘要：事实、时间线、已尝试方法、待确认问题。"
        }
    }

    records = payload.get("raw_records") or []
    if records:
        trends = analyze_habit_trends(records, payload.get("history_days", 7))
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


def create_habit_definition(habit_name: str, category: str) -> HabitDefinition:
    """创建习惯定义

    Args:
        habit_name: 习惯名称
        category: 习惯类别

    Returns:
        习惯定义对象
    """
    habit_id = f"habit_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    return HabitDefinition(
        habit_id=habit_id,
        habit_name=habit_name,
        category=category,
        description=f"培养{habit_name}的习惯",
        target_frequency=1,
        target_times_per_day=1
    )


def calculate_habit_score(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """计算习惯评分

    Args:
        records: 习惯记录列表

    Returns:
        习惯评分字典
    """
    if not records:
        return {
            "overall_score": 0,
            "completion_score": 0,
            "quality_score": 0,
            "consistency_score": 0,
            "level": "无数据"
        }

    total_records = len(records)
    completed_records = sum(1 for r in records if r.get("completed", False))
    completion_score = (completed_records / total_records * 100) if total_records > 0 else 0

    quality_scores = [r.get("quality_score", 0) for r in records if r.get("quality_score") is not None]
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
    quality_score = avg_quality * 10

    unique_dates = set()
    for record in records:
        try:
            if isinstance(record.get("timestamp"), str):
                unique_dates.add(datetime.fromisoformat(record["timestamp"]).date())
            elif isinstance(record.get("timestamp"), datetime):
                unique_dates.add(record["timestamp"].date())
        except (ValueError, AttributeError):
            continue

    consistency_score = min(100, (len(unique_dates) / 7) * 100)

    overall_score = (completion_score * 0.4 + quality_score * 0.3 + consistency_score * 0.3)

    if overall_score >= 80:
        level = "优秀"
    elif overall_score >= 60:
        level = "良好"
    elif overall_score >= 40:
        level = "一般"
    else:
        level = "需加强"

    return {
        "overall_score": round(overall_score, 1),
        "completion_score": round(completion_score, 1),
        "quality_score": round(quality_score, 1),
        "consistency_score": round(consistency_score, 1),
        "level": level
    }