"""Planning engine for 幼儿数学启蒙 Agent.

增强版本：添加数据分析、异常检测、个性化推荐、上下文记忆、数据聚合
"""
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta, date
from collections import defaultdict

try:
    from .models import (
        TrendData, Alert, Recommendation, SessionContext,
        WeeklyStats, MathActivity, ProgressRecord,
        MathSkillLevel, MathTopic, EngagementLevel
    )
except ImportError:
    from models import (
        TrendData, Alert, Recommendation, SessionContext,
        WeeklyStats, MathActivity, ProgressRecord,
        MathSkillLevel, MathTopic, EngagementLevel
    )

SKILL_FLOW = ['输入年龄', '生成生活化数学游戏', '父母记录孩子表现', 'Agent 判断掌握情况', '推荐下一阶段活动']
SAFETY_NOTES = ['本 Skill 提供家庭教育和生活管理建议，不替代专业人士意见。', '涉及安全、法律、医疗、财务或教育政策时，应提示家长二次核验。', '输出应尊重家庭差异，不用单一标准评价孩子或父母。']
DEFAULT_DELIVERABLES = ['数学小游戏', '家庭材料清单', '能力记录']

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


def analyze_progress_trends(records: List[Dict[str, Any]], days: int = 7) -> List[TrendData]:
    """分析进度趋势

    Args:
        records: 进度记录列表
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

    daily_activities = []
    daily_mastery = []
    daily_engagement = []
    dates = []

    for d in sorted_dates:
        day_records = records_by_date[d]
        activity_count = len(day_records)
        daily_activities.append(activity_count)
        dates.append(d.isoformat())

        mastery_scores = []
        engagement_scores = []
        for r in day_records:
            level = r.get("mastery_level", "introductory")
            if level == "advanced":
                mastery_scores.append(4)
            elif level == "intermediate":
                mastery_scores.append(3)
            elif level == "basic":
                mastery_scores.append(2)
            else:
                mastery_scores.append(1)

            engage = r.get("engagement", "medium")
            if engage == "high":
                engagement_scores.append(3)
            elif engage == "medium":
                engagement_scores.append(2)
            else:
                engagement_scores.append(1)

        if mastery_scores:
            daily_mastery.append(sum(mastery_scores) / len(mastery_scores))
        if engagement_scores:
            daily_engagement.append(sum(engagement_scores) / len(engagement_scores))

    if daily_activities:
        activity_trend = TrendData(
            metric_name="每日活动数量",
            data_points=[float(x) for x in daily_activities],
            dates=dates
        )
        activity_trend.calculate_trend()
        trends.append(activity_trend)

    if daily_mastery:
        mastery_trend = TrendData(
            metric_name="平均掌握程度",
            data_points=daily_mastery,
            dates=dates
        )
        mastery_trend.calculate_trend()
        trends.append(mastery_trend)

    if daily_engagement:
        engagement_trend = TrendData(
            metric_name="平均参与度",
            data_points=daily_engagement,
            dates=dates
        )
        engagement_trend.calculate_trend()
        trends.append(engagement_trend)

    return trends


def detect_progress_anomalies(records: List[Dict[str, Any]], trends: List[TrendData]) -> List[Alert]:
    """检测进度异常

    Args:
        records: 进度记录列表
        trends: 趋势数据列表

    Returns:
        告警列表
    """
    alerts = []

    if not records:
        return alerts

    for trend in trends:
        if trend.metric_name == "每日活动数量":
            if trend.trend_direction == "decreasing" and trend.trend_percentage < -30:
                alerts.append(Alert(
                    alert_type="活动减少",
                    severity="warning",
                    message=f"孩子参与数学活动的频率下降了 {abs(trend.trend_percentage):.1f}%",
                    recommendation="建议了解原因，可能是难度过高或兴趣下降，适当降低难度或更换主题"
                ))

            if trend.average > 0 and trend.average < 1:
                alerts.append(Alert(
                    alert_type="活动频率低",
                    severity="info",
                    message=f"每天平均只有 {trend.average:.1f} 个活动，可能需要增加练习机会",
                    recommendation="建议每天安排至少1-2个数学小游戏，保持学习节奏"
                ))

        elif trend.metric_name == "平均掌握程度":
            if trend.trend_direction == "decreasing" and trend.trend_percentage < -15:
                alerts.append(Alert(
                    alert_type="掌握程度下降",
                    severity="warning",
                    message=f"孩子的掌握程度呈下降趋势（{trend.trend_percentage:.1f}%）",
                    recommendation="建议回顾之前的内容，确保基础概念理解后再继续新内容"
                ))

        elif trend.metric_name == "平均参与度":
            if trend.average > 0 and trend.average < 1.5:
                alerts.append(Alert(
                    alert_type="参与度低",
                    severity="warning",
                    message=f"孩子的参与度评分较低（{trend.average:.1f}分）",
                    recommendation="尝试使用更有趣的游戏方式，或增加奖励机制提高积极性"
                ))

    activity_counts = defaultdict(int)
    for record in records:
        topic = record.get("activity_id", "").split("_")[0] if record.get("activity_id") else "unknown"
        activity_counts[topic] += 1

    if len(activity_counts) == 1 and len(records) >= 5:
        alerts.append(Alert(
            alert_type="主题单一",
            severity="info",
            message="孩子一直只练习同一类数学主题",
            recommendation="建议尝试不同的数学主题，如形状、比较、简单加减法等，拓宽数学思维"
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
        records: 进度记录列表
        trends: 趋势数据列表
        child_profile: 孩子画像
        alerts: 告警列表

    Returns:
        推荐列表
    """
    recommendations = []

    age_months = child_profile.get("age_months", 0)
    math_readiness = child_profile.get("math_readiness", "medium")

    readiness_multiplier = 1.0
    if math_readiness == "high":
        readiness_multiplier = 1.2
    elif math_readiness == "low":
        readiness_multiplier = 0.8

    recommended_daily = round(1.5 * readiness_multiplier)

    for trend in trends:
        if trend.metric_name == "每日活动数量" and trend.average < recommended_daily:
            gap = recommended_daily - trend.average
            recommendations.append(Recommendation(
                category="学习节奏",
                priority=1,
                title="建议增加每日数学活动",
                description=f"根据孩子月龄（{age_months}个月）和数学准备度，建议每天进行 {recommended_daily} 个数学活动，当前平均 {trend.average:.1f} 个",
                action_items=[
                    "将数学游戏融入日常生活（如数水果、比较大小）",
                    "每次活动时间控制在10-15分钟",
                    "选择孩子感兴趣的主题开始"
                ],
                rationale="适度的练习有助于巩固数学概念",
                expected_outcome="建立稳定的数学学习习惯"
            ))

    topics_covered = set()
    for record in records:
        topic = record.get("topic", "")
        if topic:
            topics_covered.add(topic)

    all_topics = [t.value for t in MathTopic]
    uncovered = [t for t in all_topics if t not in topics_covered]

    if uncovered and len(topics_covered) >= 2:
        recommendations.append(Recommendation(
            category="主题拓展",
            priority=2,
            title="尝试新的数学主题",
            description=f"孩子已掌握的数学主题：{', '.join(list(topics_covered)[:3])}，建议尝试：{', '.join(uncovered[:2])}",
            action_items=[
                "根据孩子兴趣选择新主题",
                "从简单概念开始逐步深入",
                "使用生活化的例子帮助理解"
            ],
            rationale="多样化的数学主题有助于培养全面的数学思维",
            expected_outcome="扩展数学认知范围"
        ))

    for trend in trends:
        if trend.metric_name == "平均掌握程度" and trend.trend_direction == "increasing":
            recommendations.append(Recommendation(
                category="能力提升",
                priority=3,
                title="可以挑战更高难度",
                description=f"孩子的掌握程度呈上升趋势（{trend.trend_percentage:+.1f}%），可以考虑引入更复杂的数学概念",
                action_items=[
                    "在已掌握的主题上增加变化",
                    "引入简单的数字运算",
                    "使用更抽象的数学语言"
                ],
                rationale="适度的挑战有助于保持学习兴趣",
                expected_outcome="数学能力持续提升"
            ))

    if not alerts and not records:
        recommendations.append(Recommendation(
            category="学习习惯",
            priority=3,
            title="开始记录数学学习进度",
            description="建议开始记录孩子的数学学习活动，帮助追踪进步",
            action_items=[
                "每次活动后记录孩子的表现",
                "观察并记录孩子对不同主题的兴趣",
                "定期回顾学习记录"
            ],
            rationale="持续的记录有助于发现孩子的学习特点",
            expected_outcome="建立完整的数学学习档案"
        ))

    recommendations.sort(key=lambda x: x.priority)
    return recommendations


def aggregate_weekly_stats(records: List[Dict[str, Any]], week_offset: int = 0) -> Optional[WeeklyStats]:
    """聚合周统计数据

    Args:
        records: 进度记录列表
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

    total_activities = len(week_records)

    mastered = sum(1 for r in week_records if r.get("mastery_level") == "advanced")

    topics_covered = list(set(r.get("topic", "") for r in week_records if r.get("topic")))

    engagement_scores = defaultdict(list)
    for r in week_records:
        engage = r.get("engagement", "medium")
        if engage == "high":
            engagement_scores["high"].append(1)
        elif engage == "medium":
            engagement_scores["medium"].append(1)
        else:
            engagement_scores["low"].append(1)

    avg_engagement = {}
    for level, scores in engagement_scores.items():
        avg_engagement[level] = len(scores) / total_activities if total_activities > 0 else 0

    return WeeklyStats(
        week_start=week_start.isoformat(),
        week_end=week_end.isoformat(),
        total_activities=total_activities,
        average_daily_activities=total_activities / 7,
        mastered_activities=mastered,
        topics_covered=topics_covered,
        engagement_scores=avg_engagement
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
        trends = analyze_progress_trends(records, payload.get("history_days", 7))
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
        trends = analyze_progress_trends(records, history_days)
        alerts = detect_progress_anomalies(records, trends)

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
        trends = analyze_progress_trends(records, payload.get("history_days", 7))
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


def generate_math_activity(
    topic: str,
    age_months: int,
    difficulty: str = "低"
) -> MathActivity:
    """生成数学活动

    Args:
        topic: 数学主题
        age_months: 月龄
        difficulty: 难度等级

    Returns:
        数学活动对象
    """
    activity_id = f"math_{topic}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    activity_templates = {
        "counting": {
            "name": "数字认知游戏",
            "description": "通过生活物品学习数数",
            "materials": ["水果", "积木", "手指"],
            "instructions": [
                "先从1-5开始",
                "用实物逐一数数",
                "数完后问'一共有几个？'"
            ]
        },
        "comparison": {
            "name": "大小比较",
            "description": "比较物品的大小和多少",
            "materials": ["玩具", "杯子", "书本"],
            "instructions": [
                "展示两个物品",
                "问'哪个更大/更多？'",
                "让孩子触摸感受"
            ]
        },
        "shapes": {
            "name": "形状识别",
            "description": "认识基本几何形状",
            "materials": ["形状卡片", "积木", "日常用品"],
            "instructions": [
                "展示圆形、方形、三角形",
                "让孩子找出相同形状",
                "在生活中找形状"
            ]
        },
        "patterns": {
            "name": "规律排序",
            "description": "发现和创造简单的规律",
            "materials": ["彩色积木", "珠子", "贴纸"],
            "instructions": [
                "展示 ABAB 规律",
                "让孩子说出下一个",
                "尝试创造新规律"
            ]
        }
    }

    template = activity_templates.get(topic, activity_templates["counting"])

    return MathActivity(
        activity_id=activity_id,
        activity_name=template["name"],
        topic=topic,
        description=template["description"],
        materials_needed=template["materials"],
        estimated_duration_minutes=15,
        difficulty_level=difficulty,
        age_recommendation=f"{max(12, age_months - 6)}-{age_months}个月",
        instructions=template["instructions"]
    )


def calculate_progress_score(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """计算进度评分

    Args:
        records: 进度记录列表

    Returns:
        进度评分字典
    """
    if not records:
        return {
            "overall_score": 0,
            "mastery_score": 0,
            "engagement_score": 0,
            "consistency_score": 0,
            "level": "无数据"
        }

    mastery_sum = 0
    engagement_sum = 0

    for record in records:
        level = record.get("mastery_level", "introductory")
        if level == "advanced":
            mastery_sum += 4
        elif level == "intermediate":
            mastery_sum += 3
        elif level == "basic":
            mastery_sum += 2
        else:
            mastery_sum += 1

        engage = record.get("engagement", "medium")
        if engage == "high":
            engagement_sum += 3
        elif engage == "medium":
            engagement_sum += 2
        else:
            engagement_sum += 1

    n = len(records)
    mastery_score = (mastery_sum / (n * 4)) * 100
    engagement_score = (engagement_sum / (n * 3)) * 100

    dates = set()
    for record in records:
        try:
            if isinstance(record.get("timestamp"), str):
                dates.add(datetime.fromisoformat(record["timestamp"]).date())
            elif isinstance(record.get("timestamp"), datetime):
                dates.add(record["timestamp"].date())
        except (ValueError, AttributeError):
            continue

    consistency_score = min(100, (len(dates) / 7) * 100)

    overall_score = (mastery_score * 0.4 + engagement_score * 0.3 + consistency_score * 0.3)

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
        "mastery_score": round(mastery_score, 1),
        "engagement_score": round(engagement_score, 1),
        "consistency_score": round(consistency_score, 1),
        "level": level
    }