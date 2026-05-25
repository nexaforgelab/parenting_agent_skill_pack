"""Planning engine for 幼儿情绪识别 Agent.

增强版本：添加数据分析、异常检测、个性化推荐、上下文记忆、数据聚合
"""
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta, date
from collections import defaultdict

try:
    from .models import (
        TrendData, Alert, Recommendation, SessionContext,
        WeeklyStats, EmotionObservation, EmotionLabel,
        EmotionType, EmotionIntensity, ExpressionMethod
    )
except ImportError:
    from models import (
        TrendData, Alert, Recommendation, SessionContext,
        WeeklyStats, EmotionObservation, EmotionLabel,
        EmotionType, EmotionIntensity, ExpressionMethod
    )

SKILL_FLOW = ['观察并记录情绪事件', '识别情绪类型和强度', '分析触发因素', '引导孩子表达情绪', '教会情绪调节策略']
SAFETY_NOTES = ['本 Skill 提供家庭教育和生活管理建议，不替代专业人士意见。', '涉及安全、法律、医疗、财务或教育政策时，应提示家长二次核验。', '输出应尊重家庭差异，不用单一标准评价孩子或父母。']
DEFAULT_DELIVERABLES = ['情绪日历', '情绪识别卡片', '调节策略指南']

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


def analyze_emotion_trends(records: List[Dict[str, Any]], days: int = 7) -> List[TrendData]:
    """分析情绪趋势

    Args:
        records: 情绪观察记录列表
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

    daily_observation_count = []
    daily_positive_ratio = []
    daily_intensity_avg = []
    dates = []

    for d in sorted_dates:
        day_records = records_by_date[d]
        observation_count = len(day_records)
        daily_observation_count.append(observation_count)
        dates.append(d.isoformat())

        positive_count = 0
        intensity_sum = 0
        intensity_count = 0

        for r in day_records:
            emotion = r.get("emotion_type", "neutral")
            if emotion in ["happy", "surprised"]:
                positive_count += 1

            intensity = r.get("intensity", "moderate")
            intensity_map = {"mild": 1, "moderate": 2, "strong": 3, "overwhelming": 4}
            if intensity in intensity_map:
                intensity_sum += intensity_map[intensity]
                intensity_count += 1

        positive_ratio = positive_count / observation_count if observation_count > 0 else 0
        daily_positive_ratio.append(positive_ratio * 100)

        if intensity_count > 0:
            daily_intensity_avg.append(intensity_sum / intensity_count)

    if daily_observation_count:
        count_trend = TrendData(
            metric_name="每日情绪观察次数",
            data_points=[float(x) for x in daily_observation_count],
            dates=dates
        )
        count_trend.calculate_trend()
        trends.append(count_trend)

    if daily_positive_ratio:
        positive_trend = TrendData(
            metric_name="正面情绪比例",
            data_points=daily_positive_ratio,
            dates=dates
        )
        positive_trend.calculate_trend()
        trends.append(positive_trend)

    if daily_intensity_avg:
        intensity_trend = TrendData(
            metric_name="平均情绪强度",
            data_points=daily_intensity_avg,
            dates=dates
        )
        intensity_trend.calculate_trend()
        trends.append(intensity_trend)

    return trends


def detect_emotion_anomalies(records: List[Dict[str, Any]], trends: List[TrendData]) -> List[Alert]:
    """检测情绪异常

    Args:
        records: 情绪观察记录列表
        trends: 趋势数据列表

    Returns:
        告警列表
    """
    alerts = []

    if not records:
        return alerts

    for trend in trends:
        if trend.metric_name == "每日情绪观察次数":
            if trend.trend_direction == "increasing" and trend.trend_percentage > 50:
                alerts.append(Alert(
                    alert_type="情绪事件增加",
                    severity="info",
                    message=f"孩子情绪事件增加了 {trend.trend_percentage:.1f}%，可能需要关注",
                    recommendation="记录更多细节，了解触发因素，是正常成长还是需要干预"
                ))

        elif trend.metric_name == "正面情绪比例":
            if trend.trend_direction == "decreasing" and trend.trend_percentage < -30:
                alerts.append(Alert(
                    alert_type="正面情绪减少",
                    severity="warning",
                    message=f"孩子的正面情绪比例下降了 {abs(trend.trend_percentage):.1f}%",
                    recommendation="关注孩子的情绪状态，增加亲子互动和正向激励"
                ))

        elif trend.metric_name == "平均情绪强度":
            if trend.trend_direction == "increasing" and trend.trend_percentage > 20:
                alerts.append(Alert(
                    alert_type="情绪强度增加",
                    severity="warning",
                    message=f"孩子的情绪强度呈上升趋势（{trend.trend_percentage:.1f}%）",
                    recommendation="教孩子更多情绪调节技巧，帮助他们在激动时冷静下来"
                ))

    emotion_counts = defaultdict(int)
    for record in records:
        emotion = record.get("emotion_type", "neutral")
        emotion_counts[emotion] += 1

    if emotion_counts:
        max_emotion = max(emotion_counts.items(), key=lambda x: x[1])
        if max_emotion[1] > len(records) * 0.6:
            alerts.append(Alert(
                alert_type="情绪类型单一",
                severity="info",
                message=f"孩子的情绪主要表现为{max_emotion[0]}，占比{max_emotion[1]/len(records)*100:.0f}%",
                recommendation="帮助孩子识别和表达更多种情绪，丰富情绪词汇"
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
        records: 情绪观察记录列表
        trends: 趋势数据列表
        child_profile: 孩子画像
        alerts: 告警列表

    Returns:
        推荐列表
    """
    recommendations = []

    age_months = child_profile.get("age_months", 0)

    for trend in trends:
        if trend.metric_name == "正面情绪比例" and trend.average < 50:
            recommendations.append(Recommendation(
                category="情绪引导",
                priority=1,
                title="增加正面情绪体验",
                description=f"当前正面情绪比例为 {trend.average:.1f}%，建议增加积极情绪体验",
                action_items=[
                    "每天安排亲子游戏时间",
                    "使用情绪卡片帮助孩子识别情绪",
                    "给予具体的表扬和鼓励"
                ],
                rationale="正面情绪体验有助于孩子建立积极的情绪调节能力",
                expected_outcome="提高正面情绪比例，改善整体情绪状态"
            ))

    for alert in alerts:
        if alert.alert_type == "情绪强度增加":
            recommendations.append(Recommendation(
                category="情绪调节",
                priority=1,
                title="学习情绪调节策略",
                description="孩子的情绪强度增加，需要学习更多调节技巧",
                action_items=[
                    "教授深呼吸技巧",
                    "使用情绪温度计自我评估",
                    "建立情绪冷静角"
                ],
                rationale="情绪调节是重要的情商技能，需要逐步培养",
                expected_outcome="孩子能够更好地控制情绪反应"
            ))

        if alert.alert_type == "情绪类型单一":
            recommendations.append(Recommendation(
                category="情绪识别",
                priority=2,
                title="丰富情绪词汇",
                description="孩子对某些情绪识别不足，需要扩展情绪认知",
                action_items=[
                    "使用情绪卡片每天认识一种新情绪",
                    "读情绪相关的绘本",
                    "在日常生活中指认情绪"
                ],
                rationale="情绪认知是情绪管理的基础",
                expected_outcome="孩子能够识别和表达更多种情绪"
            ))

    if len(records) >= 5:
        emotion_counts = defaultdict(int)
        for record in records:
            emotion = record.get("emotion_type", "neutral")
            emotion_counts[emotion] += 1

        common_triggers = []
        for record in records[-5:]:
            if record.get("trigger_event"):
                common_triggers.append(record.get("trigger_event", ""))

        if common_triggers:
            recommendations.append(Recommendation(
                category="触发因素分析",
                priority=2,
                title="识别情绪触发因素",
                description=f"最近5次观察中出现了多个触发因素，了解它们有助于预防",
                action_items=[
                    "记录每次情绪事件的触发因素",
                    "分析触发因素的共同特点",
                    "提前准备应对策略"
                ],
                rationale="了解触发因素可以提前干预，减少情绪爆发",
                expected_outcome="减少负面情绪触发的频率"
            ))

    if not alerts and len(records) >= 3:
        recommendations.append(Recommendation(
            category="情绪观察",
            priority=3,
            title="保持情绪观察习惯",
            description="继续记录孩子的情绪变化，及时发现问题",
            action_items=[
                "每天记录1-2次情绪观察",
                "使用情绪卡片辅助识别",
                "关注情绪变化趋势"
            ],
            rationale="持续的观察有助于了解孩子的情绪发展",
            expected_outcome="建立完整的情绪发展档案"
        ))

    recommendations.sort(key=lambda x: x.priority)
    return recommendations


def aggregate_weekly_stats(records: List[Dict[str, Any]], week_offset: int = 0) -> Optional[WeeklyStats]:
    """聚合周统计数据

    Args:
        records: 情绪观察记录列表
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

    total_observations = len(week_records)

    emotion_dist = defaultdict(int)
    intensity_dist = defaultdict(int)
    total_duration = 0
    duration_count = 0
    successfully_regulated = 0

    for r in week_records:
        emotion = r.get("emotion_type", "unknown")
        emotion_dist[emotion] += 1

        intensity = r.get("intensity", "moderate")
        intensity_dist[intensity] += 1

        duration = r.get("duration_minutes")
        if duration is not None:
            total_duration += duration
            duration_count += 1

        outcome = r.get("outcome", "")
        if outcome in ["successfully_regulated", "calmed", "resolved"]:
            successfully_regulated += 1

    avg_duration = total_duration / duration_count if duration_count > 0 else 0
    regulation_rate = successfully_regulated / total_observations if total_observations > 0 else 0

    return WeeklyStats(
        week_start=week_start.isoformat(),
        week_end=week_end.isoformat(),
        total_observations=total_observations,
        emotion_distribution=dict(emotion_dist),
        intensity_distribution=dict(intensity_dist),
        average_duration_minutes=avg_duration,
        successfully_regulated=successfully_regulated,
        regulation_success_rate=regulation_rate * 100
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
        trends = analyze_emotion_trends(records, payload.get("history_days", 7))
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
        f"建议先建立最近 {history_days} 天的情绪基线，再判断趋势。",
        "本 Skill 会优先输出可执行动作、记录字段和复盘指标。",
    ]

    for step in SKILL_FLOW:
        analysis.append(f"链路节点：{step}")

    if records:
        trends = analyze_emotion_trends(records, history_days)
        alerts = detect_emotion_anomalies(records, trends)

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
        "把今天相关情绪事件按时间线记录",
        "执行一个情绪引导动作并记录孩子反应",
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
            "evidence_to_record": "时间、触发点、情绪类型、孩子反应",
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
            "daily_log": "今天发生了什么情绪事件？触发因素是什么？孩子如何表达的？",
            "handoff_summary": "给专业人士/老师/家人的沟通摘要：事实、时间线、已尝试方法、待确认问题。"
        }
    }

    records = payload.get("raw_records") or []
    if records:
        trends = analyze_emotion_trends(records, payload.get("history_days", 7))
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


def create_emotion_label(emotion_type: str, intensity: str = "moderate") -> EmotionLabel:
    """创建情绪标签

    Args:
        emotion_type: 情绪类型
        intensity: 强度

    Returns:
        情绪标签对象
    """
    label_id = f"emotion_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    return EmotionLabel(
        emotion_id=label_id,
        emotion_type=emotion_type,
        intensity=intensity,
        confidence=0.8
    )


def calculate_emotion_score(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """计算情绪评分

    Args:
        records: 情绪观察记录列表

    Returns:
        情绪评分字典
    """
    if not records:
        return {
            "overall_score": 0,
            "positive_ratio_score": 0,
            "regulation_score": 0,
            "diversity_score": 0,
            "level": "无数据"
        }

    positive_count = 0
    intensity_sum = 0
    intensity_count = 0

    emotion_types = set()
    regulation_count = 0

    for record in records:
        emotion = record.get("emotion_type", "neutral")
        emotion_types.add(emotion)

        if emotion in ["happy", "surprised"]:
            positive_count += 1

        intensity = record.get("intensity", "moderate")
        intensity_map = {"mild": 1, "moderate": 2, "strong": 3, "overwhelming": 4}
        if intensity in intensity_map:
            intensity_sum += intensity_map[intensity]
            intensity_count += 1

        outcome = record.get("outcome", "")
        if outcome in ["successfully_regulated", "calmed", "resolved"]:
            regulation_count += 1

    n = len(records)
    positive_ratio = positive_count / n if n > 0 else 0
    positive_ratio_score = positive_ratio * 100

    avg_intensity = intensity_sum / intensity_count if intensity_count > 0 else 2
    regulation_score = (regulation_count / n) * 100 if n > 0 else 0

    diversity_score = min(100, (len(emotion_types) / 8) * 100)

    overall_score = (positive_ratio_score * 0.3 + regulation_score * 0.4 + diversity_score * 0.3)

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
        "positive_ratio_score": round(positive_ratio_score, 1),
        "regulation_score": round(regulation_score, 1),
        "diversity_score": round(diversity_score, 1),
        "level": level
    }