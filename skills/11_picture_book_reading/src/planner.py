"""Planning engine for 绘本共读 Agent.

提供增强的规划功能，包括数据分析、异常检测、个性化推荐、上下文记忆和学习曲线分析。
"""
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import uuid

SKILL_FLOW = ['输入绘本名称/拍照封面', '识别主题', '生成共读提问', '设计互动小游戏', '记录孩子回答', '生成阅读成长档案']
SAFETY_NOTES = ['本 Skill 提供家庭教育和生活管理建议，不替代专业人士意见。', '涉及安全、法律、医疗、财务或教育政策时，应提示家长二次核验。', '输出应尊重家庭差异，不用单一标准评价孩子或父母。']
DEFAULT_DELIVERABLES = ['共读脚本', '提问卡', '阅读记录', '个性化建议', '进度报告']


def build_known_facts(payload: Dict[str, Any]) -> List[str]:
    """构建已知事实列表

    Args:
        payload: 输入的负载数据

    Returns:
        已知事实列表
    """
    facts: List[str] = []
    child = payload.get("child_profile", {})
    family = payload.get("family_context", {})
    if child:
        facts.append(f"孩子画像：年龄 {child.get('age', '未知')}，昵称 {child.get('nickname', '未知')}")
    if family:
        facts.append(f"家庭上下文：照护人 {family.get('caregiver', '未知')}，可用时间 {family.get('available_time', '未知')}")
    if payload.get("goal"):
        facts.append(f"目标：{payload.get('goal')}")
    records = payload.get("raw_records") or []
    facts.append(f"已收到 {len(records)} 条原始记录。")
    return facts


def build_analysis(payload: Dict[str, Any]) -> List[str]:
    """构建分析结果

    Args:
        payload: 输入的负载数据

    Returns:
        分析结果列表
    """
    problem = payload.get("current_problem", "")
    history_days = payload.get("history_days", 7)
    analysis = [
        f"当前问题聚焦：{problem}",
        f"建议先建立最近 {history_days} 天的家庭基线，再判断趋势。",
        "本 Skill 会优先输出可执行动作、记录字段和复盘指标。",
    ]
    for step in SKILL_FLOW:
        analysis.append(f"链路节点：{step}")
    return analysis


def build_action_plan(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """构建行动计划

    Args:
        payload: 输入的负载数据

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
    """构建交付物清单

    Args:
        payload: 输入的负载数据

    Returns:
        交付物字典
    """
    return {
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


def next_fields() -> List[str]:
    """获取下次追踪字段列表

    Returns:
        追踪字段列表
    """
    return [
        "孩子年龄/月龄",
        "今天新增记录",
        "执行了哪一步",
        "孩子反应",
        "家长感受",
        "需要调整的限制条件"
    ]


def analyze_learning_progress(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析学习进度

    Args:
        records: 学习记录列表

    Returns:
        进度分析结果字典
    """
    if not records:
        return {
            "total_sessions": 0,
            "total_minutes": 0,
            "average_engagement": 0.0,
            "trend": "insufficient_data",
            "summary": "暂无足够数据进行分析"
        }

    total_sessions = len(records)
    total_minutes = sum(r.get("duration_minutes", 0) for r in records)

    engagement_scores = [r.get("engagement_score", 0.0) for r in records if r.get("engagement_score")]
    average_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0.0

    recent_records = records[-7:] if len(records) >= 7 else records
    recent_avg = sum(r.get("engagement_score", 0.0) for r in recent_records) / len(recent_records) if recent_records else 0.0

    if len(records) >= 14:
        earlier_records = records[:7]
        earlier_avg = sum(r.get("engagement_score", 0.0) for r in earlier_records) / len(earlier_records)
        if recent_avg > earlier_avg * 1.1:
            trend = "improving"
        elif recent_avg < earlier_avg * 0.9:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"

    topics = defaultdict(int)
    for record in records:
        for topic in record.get("topics_covered", []):
            topics[topic] += 1

    favorite_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:3]
    difficult_topics = [t for t, count in topics.items() if count < 2]

    return {
        "total_sessions": total_sessions,
        "total_minutes": total_minutes,
        "average_engagement": round(average_engagement, 2),
        "recent_trend": trend,
        "favorite_topics": [t for t, _ in favorite_topics],
        "difficult_topics": difficult_topics,
        "summary": f"共完成 {total_sessions} 次学习，累计 {total_minutes} 分钟"
    }


def detect_learning_difficulties(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """检测学习困难

    Args:
        records: 学习记录列表

    Returns:
        检测到的困难列表
    """
    difficulties = []

    if len(records) < 3:
        return difficulties

    recent_records = records[-5:]
    engagement_scores = [r.get("engagement_score", 0.0) for r in recent_records]

    if engagement_scores:
        avg_recent = sum(engagement_scores) / len(engagement_scores)
        if avg_recent < 4.0:
            difficulties.append({
                "type": "low_engagement",
                "severity": "high",
                "message": "孩子近期投入度较低，可能对当前绘本主题不感兴趣",
                "suggestion": "尝试更换绘本主题或增加互动游戏"
            })

    declining_count = 0
    for i in range(1, len(engagement_scores)):
        if engagement_scores[i] < engagement_scores[i-1]:
            declining_count += 1

    if declining_count >= 3:
        difficulties.append({
            "type": "declining_engagement",
            "severity": "medium",
            "message": "投入度持续下降，可能出现学习疲劳",
            "suggestion": "建议减少单次学习时长，增加休息间隔"
        })

    questions_answered = [r.get("questions_answered", 0) for r in recent_records]
    questions_asked = [r.get("questions_asked", 1) for r in recent_records]

    for i in range(len(recent_records)):
        if questions_asked[i] > 0:
            answer_rate = questions_answered[i] / questions_asked[i]
            if answer_rate < 0.3:
                difficulties.append({
                    "type": "low_comprehension",
                    "severity": "medium",
                    "message": f"理解程度较低，问题回答率仅 {answer_rate*100:.0f}%",
                    "suggestion": "降低绘本难度，增加图片解释"
                })
                break

    return difficulties


def generate_personalized_recommendations(
    child_profile: Dict[str, Any],
    records: List[Dict[str, Any]],
    progress: Dict[str, Any],
    difficulties: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """生成个性化推荐

    Args:
        child_profile: 孩子画像
        records: 学习记录
        progress: 进度数据
        difficulties: 检测到的困难

    Returns:
        推荐列表
    """
    recommendations = []

    age = child_profile.get("age", "未知")
    if "岁" in str(age):
        age_num = int(age.split("岁")[0]) if age.split("岁")[0].isdigit() else 3
    else:
        age_num = 3

    recommendations.append({
        "recommendation_id": str(uuid.uuid4())[:8],
        "category": "reading_plan",
        "priority": "high",
        "title": "根据年龄调整阅读计划",
        "description": f"针对 {age} 孩子，建议单次阅读时长控制在 {10 + age_num * 2} 分钟左右",
        "action_items": [
            f"每天固定时间进行 {10 + age_num * 2} 分钟共读",
            "选择适合年龄的绘本难度",
            "中途安排 1-2 次小休息"
        ],
        "expected_benefit": "提高专注力和学习效果",
        "target_mastery_level": "FAMILIAR",
        "estimated_duration": "2 周"
    })

    if progress.get("trend") == "improving":
        recommendations.append({
            "recommendation_id": str(uuid.uuid4())[:8],
            "category": "progression",
            "priority": "medium",
            "title": "当前学习状态良好",
            "description": "孩子学习进度稳步提升，可以适当增加学习内容",
            "action_items": [
                "每周增加 1 本新绘本",
                "尝试更复杂的故事主题",
                "增加开放式问题的提问比例"
            ],
            "expected_benefit": "促进语言能力发展",
            "target_mastery_level": "MASTERED",
            "estimated_duration": "1 个月"
        })
    elif progress.get("trend") == "declining":
        recommendations.append({
            "recommendation_id": str(uuid.uuid4())[:8],
            "category": "adjustment",
            "priority": "high",
            "title": "需要调整学习节奏",
            "description": "检测到学习投入度下降，建议降低学习强度",
            "action_items": [
                "减少单次学习时长",
                "选择孩子更感兴趣的绘本主题",
                "增加互动游戏和奖励机制"
            ],
            "expected_benefit": "重新激发学习兴趣",
            "target_mastery_level": "LEARNING",
            "estimated_duration": "1 周"
        })

    favorite_topics = progress.get("favorite_topics", [])
    if favorite_topics:
        recommendations.append({
            "recommendation_id": str(uuid.uuid4())[:8],
            "category": "interest_boost",
            "priority": "medium",
            "title": "延续兴趣主题",
            "description": f"孩子喜欢 {', '.join(favorite_topics[:2])} 主题的绘本",
            "action_items": [
                f"寻找更多 {favorite_topics[0] if favorite_topics else '相关'} 主题绘本",
                "围绕兴趣主题设计延伸活动",
                "鼓励孩子讲述相关故事"
            ],
            "expected_benefit": "保持学习热情",
            "target_mastery_level": "FAMILIAR",
            "estimated_duration": "持续进行"
        })

    for difficulty in difficulties:
        if difficulty.get("type") == "low_comprehension":
            recommendations.append({
                "recommendation_id": str(uuid.uuid4())[:8],
                "category": "support",
                "priority": "high",
                "title": "提升理解能力",
                "description": difficulty.get("message", "理解能力需要提升"),
                "action_items": [
                    "选择图片更丰富的绘本",
                    "阅读前先带孩子看图讨论",
                    "减少文字量，增加互动提问",
                    "重复阅读同一绘本加深理解"
                ],
                "expected_benefit": "提高理解和表达能力",
                "target_mastery_level": "FAMILIAR",
                "estimated_duration": "2 周"
            })

    return recommendations


def analyze_learning_curve(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析学习曲线

    Args:
        records: 学习记录列表

    Returns:
        学习曲线分析结果
    """
    if len(records) < 3:
        return {
            "data_points": [],
            "curve_type": "insufficient_data",
            "slope": 0.0,
            "prediction": "数据不足，无法预测"
        }

    sorted_records = sorted(records, key=lambda x: x.get("timestamp", ""))
    engagement_values = [r.get("engagement_score", 0.0) for r in sorted_records]

    n = len(engagement_values)
    x_mean = sum(range(n)) / n
    y_mean = sum(engagement_values) / n

    numerator = sum((i - x_mean) * (engagement_values[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))

    slope = numerator / denominator if denominator != 0 else 0.0

    if slope > 0.1:
        curve_type = "improving"
        prediction = "学习投入度呈上升趋势"
    elif slope < -0.1:
        curve_type = "declining"
        prediction = "学习投入度呈下降趋势，需要关注"
    else:
        curve_type = "stable"
        prediction = "学习投入度保持稳定"

    recent_avg = sum(engagement_values[-3:]) / 3 if len(engagement_values) >= 3 else y_mean
    next_trend = "上升" if slope > 0 else "下降"

    return {
        "data_points": engagement_values,
        "curve_type": curve_type,
        "slope": round(slope, 4),
        "prediction": f"{prediction}，预计下一阶段趋势 {next_trend}",
        "recent_average": round(recent_avg, 2),
        "overall_average": round(y_mean, 2),
        "trend_description": f"平均每次学习投入度变化 {abs(slope):.2f} 分"
    }


def calculate_mastery_level(records: List[Dict[str, Any]]) -> str:
    """计算掌握程度

    Args:
        records: 学习记录列表

    Returns:
        掌握程度等级字符串
    """
    if not records:
        return "NOT_STARTED"

    total_sessions = len(records)
    avg_engagement = sum(r.get("engagement_score", 0.0) for r in records) / total_sessions

    answered_rates = []
    for r in records:
        asked = r.get("questions_asked", 1)
        answered = r.get("questions_answered", 0)
        if asked > 0:
            answered_rates.append(answered / asked)

    avg_answer_rate = sum(answered_rates) / len(answered_rates) if answered_rates else 0.0

    mastered_count = sum(1 for r in records if r.get("comprehension_level") == "已掌握")
    mastered_rate = mastered_count / total_sessions if total_sessions > 0 else 0.0

    if total_sessions >= 10 and avg_answer_rate >= 0.7 and mastered_rate >= 0.5:
        return "MASTERED"
    elif total_sessions >= 5 and avg_engagement >= 6.0:
        return "FAMILIAR"
    elif total_sessions >= 2:
        return "LEARNING"
    else:
        return "NOT_STARTED"


def create_session_context(
    child_profile: Dict[str, Any],
    records: List[Dict[str, Any]],
    preferences: Dict[str, Any]
) -> Dict[str, Any]:
    """创建会话上下文

    Args:
        child_profile: 孩子画像
        records: 学习记录
        preferences: 偏好设置

    Returns:
        会话上下文字典
    """
    context = {
        "session_id": str(uuid.uuid4())[:8],
        "child_id": child_profile.get("nickname", "未知孩子"),
        "start_time": datetime.now().isoformat(),
        "current_topic": "",
        "recent_records": records[-10:] if records else [],
        "conversation_history": [],
        "preferences": preferences,
        "detected_interests": [],
        "detected_difficulties": [],
        "learning_goals": [],
        "parent_notes": []
    }

    topics = defaultdict(int)
    for record in records:
        for topic in record.get("topics_covered", []):
            topics[topic] += 1

    favorite_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5]
    context["detected_interests"] = [t for t, _ in favorite_topics]

    return context


def analyze_session_patterns(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析会话模式

    Args:
        records: 学习记录列表

    Returns:
        模式分析结果
    """
    if not records:
        return {"pattern_type": "no_data", "insights": []}

    durations = [r.get("duration_minutes", 0) for r in records]
    avg_duration = sum(durations) / len(durations) if durations else 0

    engagement_by_duration = defaultdict(list)
    for r in records:
        duration_bucket = r.get("duration_minutes", 0) // 5
        engagement_by_duration[duration_bucket].append(r.get("engagement_score", 0.0))

    best_duration_bucket = max(engagement_by_duration.items(), key=lambda x: sum(x[1])/len(x[1]) if x[1] else 0)[0]
    optimal_duration = best_duration_bucket * 5 + 2

    interaction_types = defaultdict(int)
    for r in records:
        itype = r.get("interaction_type", "提问")
        interaction_types[itype] += 1

    most_used_interaction = max(interaction_types.items(), key=lambda x: x[1])[0] if interaction_types else "提问"

    insights = []
    if avg_duration > 20:
        insights.append("建议减少单次学习时长以保持孩子专注力")
    if engagement_by_duration.get(0) and sum(engagement_by_duration.get(0, [])) / len(engagement_by_duration[0]) > avg_duration:
        insights.append("短时高频学习可能更适合当前阶段")

    return {
        "average_duration": round(avg_duration, 1),
        "optimal_duration": optimal_duration,
        "most_used_interaction": most_used_interaction,
        "insights": insights,
        "pattern_type": "stable" if len(records) >= 5 else "developing"
    }


def generate_weekly_review(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """生成周报

    Args:
        records: 学习记录列表

    Returns:
        周报数据
    """
    if not records:
        return {
            "sessions": 0,
            "minutes": 0,
            "books": 0,
            "engagement": 0.0,
            "improvements": [],
            "areas_for_growth": []
        }

    total_sessions = len(records)
    total_minutes = sum(r.get("duration_minutes", 0) for r in records)
    total_books = len(set(r.get("book_title", "") for r in records))
    avg_engagement = sum(r.get("engagement_score", 0.0) for r in records) / total_sessions

    improvements = []
    areas_for_growth = []

    if avg_engagement >= 7.0:
        improvements.append("投入度表现优秀")
    elif avg_engagement < 5.0:
        areas_for_growth.append("投入度有待提升")

    answer_rates = []
    for r in records:
        asked = r.get("questions_asked", 1)
        answered = r.get("questions_answered", 0)
        if asked > 0:
            answer_rates.append(answered / asked)

    avg_answer_rate = sum(answer_rates) / len(answer_rates) if answer_rates else 0.0
    if avg_answer_rate >= 0.6:
        improvements.append("理解能力良好")
    else:
        areas_for_growth.append("理解能力需要加强")

    return {
        "sessions": total_sessions,
        "minutes": total_minutes,
        "books": total_books,
        "engagement": round(avg_engagement, 1),
        "improvements": improvements,
        "areas_for_growth": areas_for_growth
    }


def run_full_analysis(payload: Dict[str, Any]) -> Dict[str, Any]:
    """运行完整分析

    Args:
        payload: 输入的负载数据

    Returns:
        完整分析结果
    """
    records = payload.get("raw_records", [])
    child_profile = payload.get("child_profile", {})
    preferences = payload.get("preferences", {})

    progress = analyze_learning_progress(records)
    difficulties = detect_learning_difficulties(records)
    recommendations = generate_personalized_recommendations(child_profile, records, progress, difficulties)
    learning_curve = analyze_learning_curve(records)
    mastery_level = calculate_mastery_level(records)
    session_context = create_session_context(child_profile, records, preferences)
    patterns = analyze_session_patterns(records)
    weekly_review = generate_weekly_review(records)

    return {
        "progress": progress,
        "difficulties": difficulties,
        "recommendations": recommendations,
        "learning_curve": learning_curve,
        "mastery_level": mastery_level,
        "session_context": session_context,
        "patterns": patterns,
        "weekly_review": weekly_review
    }