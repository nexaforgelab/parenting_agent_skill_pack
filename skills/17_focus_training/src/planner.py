"""Planning engine for 专注力训练 Agent.

增强版本：添加数据分析、异常检测、个性化推荐、上下文记忆、数据聚合
"""
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta, date
from collections import defaultdict

try:
    from .models import (
        TrendData, Alert, Recommendation, SessionContext,
        WeeklyStats, FocusTrainingActivity, FocusSessionRecord,
        FocusLevel, TaskType, DifficultyLevel
    )
except ImportError:
    from models import (
        TrendData, Alert, Recommendation, SessionContext,
        WeeklyStats, FocusTrainingActivity, FocusSessionRecord,
        FocusLevel, TaskType, DifficultyLevel
    )

SKILL_FLOW = ['记录孩子年龄和专注场景', '设计 5-15 分钟训练任务', '计时执行', '记录中断次数', '每周生成专注力趋势']
SAFETY_NOTES = ['本 Skill 提供家庭教育和生活管理建议，不替代专业人士意见。', '涉及安全、法律、医疗、财务或教育政策时，应提示家长二次核验。', '输出应尊重家庭差异，不用单一标准评价孩子或父母。']
DEFAULT_DELIVERABLES = ['专注训练计划', '打卡表', '进步报告']

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


def analyze_focus_trends(records: List[Dict[str, Any]], days: int = 7) -> List[TrendData]:
    """分析专注力趋势

    Args:
        records: 专注力训练记录列表
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
            if isinstance(record.get("start_time"), str):
                record_date = datetime.fromisoformat(record["start_time"]).date()
            elif isinstance(record.get("start_time"), datetime):
                record_date = record["start_time"].date()
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

    daily_focus_duration = []
    daily_distraction = []
    daily_completion = []
    dates = []

    for d in sorted_dates:
        day_records = records_by_date[d]
        total_duration = sum(r.get("focus_duration_minutes", 0) or 0 for r in day_records)
        total_distraction = sum(r.get("distraction_count", 0) or 0 for r in day_records)
        avg_completion = sum(r.get("completion_rate", 0) or 0 for r in day_records) / len(day_records) if day_records else 0

        daily_focus_duration.append(total_duration)
        daily_distraction.append(total_distraction)
        daily_completion.append(avg_completion)
        dates.append(d.isoformat())

    if daily_focus_duration:
        duration_trend = TrendData(
            metric_name="每日专注时长",
            data_points=daily_focus_duration,
            dates=dates
        )
        duration_trend.calculate_trend()
        trends.append(duration_trend)

    if daily_distraction:
        distraction_trend = TrendData(
            metric_name="每日分心次数",
            data_points=[float(x) for x in daily_distraction],
            dates=dates
        )
        distraction_trend.calculate_trend()
        trends.append(distraction_trend)

    if daily_completion:
        completion_trend = TrendData(
            metric_name="平均完成率",
            data_points=daily_completion,
            dates=dates
        )
        completion_trend.calculate_trend()
        trends.append(completion_trend)

    return trends


def detect_focus_anomalies(records: List[Dict[str, Any]], trends: List[TrendData]) -> List[Alert]:
    """检测专注力异常

    Args:
        records: 专注力训练记录列表
        trends: 趋势数据列表

    Returns:
        告警列表
    """
    alerts = []

    if not records:
        return alerts

    for trend in trends:
        if trend.metric_name == "每日专注时长":
            if trend.trend_direction == "decreasing" and trend.trend_percentage < -20:
                alerts.append(Alert(
                    alert_type="专注时长下降",
                    severity="warning",
                    message=f"孩子的专注时长下降了 {abs(trend.trend_percentage):.1f}%，需要关注",
                    recommendation="建议降低任务难度或缩短单次训练时间，避免孩子产生抵触情绪"
                ))

            if trend.average > 0 and trend.average < 5:
                alerts.append(Alert(
                    alert_type="专注时长偏短",
                    severity="info",
                    message=f"每次训练平均专注时长只有 {trend.average:.1f} 分钟",
                    recommendation="对于幼儿来说这是正常的，可以逐步延长，重点是保持兴趣"
                ))

        elif trend.metric_name == "每日分心次数":
            if trend.trend_direction == "increasing" and trend.trend_percentage > 30:
                alerts.append(Alert(
                    alert_type="分心次数增加",
                    severity="warning",
                    message=f"孩子的分心次数增加了 {trend.trend_percentage:.1f}%",
                    recommendation="检查训练环境是否过于嘈杂或有过多干扰因素"
                ))

            if trend.average > 10:
                alerts.append(Alert(
                    alert_type="分心频繁",
                    severity="warning",
                    message=f"平均每次训练有 {trend.average:.1f} 次分心",
                    recommendation="考虑将训练拆分成更短的小节，减少每次的注意力要求"
                ))

        elif trend.metric_name == "平均完成率":
            if trend.trend_direction == "decreasing" and trend.trend_percentage < -20:
                alerts.append(Alert(
                    alert_type="完成率下降",
                    severity="info",
                    message=f"任务完成率下降了 {abs(trend.trend_percentage):.1f}%",
                    recommendation="可能是任务难度过高，建议适当降低难度或提供更多支持"
                ))

    task_types = defaultdict(int)
    for record in records:
        tt = record.get("task_type", "mixed")
        task_types[tt] += 1

    if len(task_types) == 1 and len(records) >= 5:
        alerts.append(Alert(
            alert_type="训练类型单一",
            severity="info",
            message="孩子一直只练习同一类型的专注力训练",
            recommendation="建议尝试不同类型的训练（视觉、听觉、运动、认知），全面发展专注力"
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
        records: 专注力训练记录列表
        trends: 趋势数据列表
        child_profile: 孩子画像
        alerts: 告警列表

    Returns:
        推荐列表
    """
    recommendations = []

    age_months = child_profile.get("age_months", 0)
    recommended_duration = max(5, min(15, age_months // 6))

    for trend in trends:
        if trend.metric_name == "每日专注时长" and trend.average < recommended_duration:
            gap = recommended_duration - trend.average
            recommendations.append(Recommendation(
                category="训练时长调整",
                priority=1,
                title="建议逐步延长专注时长",
                description=f"根据孩子月龄（{age_months}个月），建议每次训练 {recommended_duration} 分钟，当前平均 {trend.average:.1f} 分钟",
                action_items=[
                    "从孩子能接受的时长开始，逐步增加1-2分钟",
                    "使用计时器让孩子知道还剩多少时间",
                    "完成后给予积极反馈和适当奖励"
                ],
                rationale="适度的挑战有助于专注力提升，但不要操之过急",
                expected_outcome="逐步提升专注时长，建立稳定的训练习惯"
            ))

    distraction_alert = next((a for a in alerts if a.alert_type == "分心频繁"), None)
    if distraction_alert:
        recommendations.append(Recommendation(
            category="环境优化",
            priority=1,
            title="减少分心因素",
            description="训练环境中的干扰因素可能导致孩子容易分心",
            action_items=[
                "选择安静的房间进行训练",
                "收起可能分散注意力的玩具和电子产品",
                "训练前让孩子上个厕所、喝点水"
            ],
            rationale="减少干扰可以帮助孩子更好地集中注意力",
            expected_outcome="降低分心次数，提高训练效果"
        ))

    task_types = set()
    for record in records:
        tt = record.get("task_type", "")
        if tt:
            task_types.add(tt)

    if len(task_types) < 3 and len(records) >= 3:
        recommendations.append(Recommendation(
            category="训练多样性",
            priority=2,
            title="尝试不同类型的专注力训练",
            description=f"当前练习的类型：{', '.join(list(task_types)[:3])}，建议增加多样性",
            action_items=[
                "视觉训练：找不同、迷宫、舒尔特表格",
                "听觉训练：听指令做动作、复述数字",
                "运动训练：平衡木、球类运动"
            ],
            rationale="不同类型的训练可以全面提升专注力",
            expected_outcome="专注力各项指标均衡发展"
        ))

    if not alerts and len(records) >= 3:
        recommendations.append(Recommendation(
            category="训练习惯",
            priority=3,
            title="保持稳定的训练频率",
            description="专注力训练需要持续练习才能见效",
            action_items=[
                "每天固定时间进行训练",
                "每次训练时间控制在10-15分钟",
                "记录每次训练的表现"
            ],
            rationale="稳定的训练习惯比偶尔的高强度训练更有效",
            expected_outcome="建立长期稳定的专注力训练计划"
        ))

    recommendations.sort(key=lambda x: x.priority)
    return recommendations


def aggregate_weekly_stats(records: List[Dict[str, Any]], week_offset: int = 0) -> Optional[WeeklyStats]:
    """聚合周统计数据

    Args:
        records: 专注力训练记录列表
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
            if isinstance(record.get("start_time"), str):
                record_date = datetime.fromisoformat(record["start_time"]).date()
            elif isinstance(record.get("start_time"), datetime):
                record_date = record["start_time"].date()
            else:
                continue

            if week_start <= record_date <= week_end:
                week_records.append(record)
        except (ValueError, AttributeError, TypeError):
            continue

    if not week_records:
        return None

    total_sessions = len(week_records)
    total_duration = sum(r.get("focus_duration_minutes", 0) or 0 for r in week_records)
    total_distraction = sum(r.get("distraction_count", 0) or 0 for r in week_records)
    total_completion = sum(r.get("completion_rate", 0) or 0 for r in week_records)

    avg_duration = total_duration / total_sessions if total_sessions > 0 else 0
    avg_distraction = total_distraction / total_sessions if total_sessions > 0 else 0
    avg_completion = total_completion / total_sessions if total_sessions > 0 else 0

    focus_level_dist = defaultdict(int)
    task_types = set()

    for r in week_records:
        level = r.get("focus_level", "focused")
        focus_level_dist[level] += 1

        tt = r.get("task_type", "")
        if tt:
            task_types.add(tt)

    return WeeklyStats(
        week_start=week_start.isoformat(),
        week_end=week_end.isoformat(),
        total_sessions=total_sessions,
        average_focus_duration=avg_duration,
        average_distraction_count=avg_distraction,
        completion_rate=avg_completion,
        focus_level_distribution=dict(focus_level_dist),
        task_type_coverage=list(task_types)
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
        trends = analyze_focus_trends(records, payload.get("history_days", 7))
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
        trends = analyze_focus_trends(records, history_days)
        alerts = detect_focus_anomalies(records, trends)

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
        trends = analyze_focus_trends(records, payload.get("history_days", 7))
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


def generate_focus_activity(
    task_type: str,
    age_months: int,
    difficulty: str = "easy"
) -> FocusTrainingActivity:
    """生成专注力训练活动

    Args:
        task_type: 任务类型
        age_months: 月龄
        difficulty: 难度等级

    Returns:
        专注力训练活动对象
    """
    activity_id = f"focus_{task_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    activity_templates = {
        "visual": {
            "name": "视觉专注力训练",
            "description": "通过视觉任务提升专注力",
            "materials": ["图片卡片", "迷宫图", "找不同图"],
            "instructions": [
                "展示图片让孩子观察",
                "问一些关于图片的问题",
                "慢慢延长时间"
            ]
        },
        "auditory": {
            "name": "听觉专注力训练",
            "description": "通过听觉任务提升专注力",
            "materials": ["故事音频", "指令卡"],
            "instructions": [
                "播放故事或指令",
                "让孩子复述或执行",
                "逐渐增加复杂度"
            ]
        },
        "motor": {
            "name": "运动专注力训练",
            "description": "通过运动任务提升专注力",
            "materials": ["皮球", "呼啦圈", "平衡木"],
            "instructions": [
                "做简单的平衡动作",
                "接球或传球游戏",
                "逐渐增加难度"
            ]
        },
        "cognitive": {
            "name": "认知专注力训练",
            "description": "通过认知任务提升专注力",
            "materials": ["拼图", "积木", "益智玩具"],
            "instructions": [
                "选择适龄的拼图",
                "给予适当的提示",
                "完成时给予鼓励"
            ]
        }
    }

    template = activity_templates.get(task_type, activity_templates["cognitive"])

    return FocusTrainingActivity(
        activity_id=activity_id,
        activity_name=template["name"],
        task_type=task_type,
        description=template["description"],
        materials_needed=template["materials"],
        estimated_duration_minutes=15,
        difficulty=difficulty,
        age_recommendation=f"{max(12, age_months - 6)}-{age_months}个月",
        instructions=template["instructions"]
    )


def calculate_focus_score(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """计算专注力评分

    Args:
        records: 专注力训练记录列表

    Returns:
        专注力评分字典
    """
    if not records:
        return {
            "overall_score": 0,
            "duration_score": 0,
            "stability_score": 0,
            "completion_score": 0,
            "level": "无数据"
        }

    total_duration = sum(r.get("focus_duration_minutes", 0) or 0 for r in records)
    total_distraction = sum(r.get("distraction_count", 0) or 0 for r in records)
    total_completion = sum(r.get("completion_rate", 0) or 0 for r in records)

    n = len(records)
    avg_duration = total_duration / n
    avg_distraction = total_distraction / n
    avg_completion = total_completion / n

    duration_score = min(100, (avg_duration / 15) * 100)
    stability_score = max(0, 100 - (avg_distraction * 10))
    completion_score = avg_completion

    overall_score = (duration_score * 0.3 + stability_score * 0.4 + completion_score * 0.3)

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
        "duration_score": round(duration_score, 1),
        "stability_score": round(stability_score, 1),
        "completion_score": round(completion_score, 1),
        "level": level
    }