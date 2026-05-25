"""Planning engine for 小学作文陪练 Agent.

提供增强的规划功能，包括数据分析、异常检测、个性化推荐、上下文记忆和学习曲线分析。
"""
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import uuid

SKILL_FLOW = ['输入作文题目', '生成素材提问', '引导孩子回忆生活经历', '搭建结构', '初稿生成', '批改润色']
SAFETY_NOTES = ['本 Skill 以启发式陪练为主，避免直接替孩子完成作业或代写成品。', '输出应包含引导问题、解题路径、错因分析和复习建议，保留孩子自主思考过程。', '涉及教材、地区考试政策或校内要求时，应提示以学校老师最新要求为准。']
DEFAULT_DELIVERABLES = ['作文大纲', '初稿', '修改稿', '好词好句库']


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
        facts.append(f"孩子画像：年龄 {child.get('age', '未知')}，年级 {child.get('grade', '未知')}")
    if family:
        facts.append(f"家庭上下文：照护人 {family.get('caregiver', '未知')}，学习时间 {family.get('available_time', '未知')}")
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
            "total_words": 0,
            "average_quality_score": 0.0,
            "trend": "insufficient_data",
            "summary": "暂无足够数据进行分析"
        }

    total_sessions = len(records)
    total_words = sum(r.get("word_count", 0) for r in records)

    quality_scores = [r.get("quality_score", 0.0) for r in records if r.get("quality_score")]
    average_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0

    recent_records = records[-7:] if len(records) >= 7 else records
    recent_avg = sum(r.get("quality_score", 0.0) for r in recent_records) / len(recent_records) if recent_records else 0.0

    if len(records) >= 14:
        earlier_records = records[:7]
        earlier_avg = sum(r.get("quality_score", 0.0) for r in earlier_records) / len(earlier_records)
        if recent_avg > earlier_avg * 1.1:
            trend = "improving"
        elif recent_avg < earlier_avg * 0.9:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"

    writing_types = defaultdict(int)
    for record in records:
        writing_type = record.get("writing_type", "未知")
        writing_types[writing_type] += 1

    most_practiced = sorted(writing_types.items(), key=lambda x: x[1], reverse=True)[:3]
    weak_types = [t for t, count in writing_types.items() if count < 2]

    return {
        "total_sessions": total_sessions,
        "total_words": total_words,
        "average_quality_score": round(average_quality, 2),
        "recent_trend": trend,
        "most_practiced_types": [t for t, _ in most_practiced],
        "weak_types": weak_types,
        "summary": f"共完成 {total_sessions} 次练习，累计 {total_words} 字"
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
    quality_scores = [r.get("quality_score", 0.0) for r in recent_records]

    if quality_scores:
        avg_recent = sum(quality_scores) / len(quality_scores)
        if avg_recent < 5.0:
            difficulties.append({
                "type": "low_quality",
                "severity": "high",
                "message": "作文质量评分较低，需要更多指导",
                "suggestion": "建议增加素材积累，加强结构练习"
            })

    declining_count = 0
    for i in range(1, len(quality_scores)):
        if quality_scores[i] < quality_scores[i-1]:
            declining_count += 1

    if declining_count >= 3:
        difficulties.append({
            "type": "declining_quality",
            "severity": "medium",
            "message": "作文质量持续下降，可能出现写作疲劳",
            "suggestion": "建议减少单次写作时长，增加休息间隔"
        })

    structure_scores = [r.get("structure_score", 0.0) for r in recent_records]
    if structure_scores:
        avg_structure = sum(structure_scores) / len(structure_scores)
        if avg_structure < 4.0:
            difficulties.append({
                "type": "weak_structure",
                "severity": "medium",
                "message": "文章结构能力较弱",
                "suggestion": "加强总分总结构的专项训练"
            })

    word_counts = [r.get("word_count", 0) for r in recent_records]
    avg_words = sum(word_counts) / len(word_counts) if word_counts else 0
    grade = records[0].get("grade", "三年级") if records else "三年级"
    grade_num = int(''.join(filter(str.isdigit, grade))) if any(c.isdigit() for c in grade) else 3
    expected_words = grade_num * 50

    if avg_words < expected_words * 0.6:
        difficulties.append({
            "type": "insufficient_length",
            "severity": "medium",
            "message": f"作文字数偏少，平均 {avg_words:.0f} 字，低于年级要求",
            "suggestion": "加强素材积累和细节描写训练"
        })

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

    grade = child_profile.get("grade", "三年级")
    if "年级" in str(grade):
        grade_num = int(''.join(filter(str.isdigit, str(grade)))) if any(c.isdigit() for c in str(grade)) else 3
    else:
        grade_num = 3

    recommendations.append({
        "recommendation_id": str(uuid.uuid4())[:8],
        "category": "writing_plan",
        "priority": "high",
        "title": "根据年级调整写作计划",
        "description": f"针对 {grade} 学生，建议每次写作练习控制在 {grade_num * 5} 分钟左右",
        "action_items": [
            f"每周安排 {2 + grade_num // 3} 次写作练习",
            "每次练习包含审题、列提纲、写初稿三个步骤",
            "完成后进行自我检查"
        ],
        "expected_benefit": "提高写作效率和质量",
        "target_mastery_level": "FAMILIAR",
        "estimated_duration": "2 周"
    })

    if progress.get("trend") == "improving":
        recommendations.append({
            "recommendation_id": str(uuid.uuid4())[:8],
            "category": "progression",
            "priority": "medium",
            "title": "当前写作状态良好",
            "description": "孩子写作进步明显，可以适当提升难度",
            "action_items": [
                "尝试更复杂的叙事结构",
                "增加修辞手法的运用",
                "挑战不同类型的作文题目"
            ],
            "expected_benefit": "促进写作能力全面发展",
            "target_mastery_level": "MASTERED",
            "estimated_duration": "1 个月"
        })
    elif progress.get("trend") == "declining":
        recommendations.append({
            "recommendation_id": str(uuid.uuid4())[:8],
            "category": "adjustment",
            "priority": "high",
            "title": "需要调整学习节奏",
            "description": "检测到写作进步下降，建议降低学习强度",
            "action_items": [
                "减少单次写作时长",
                "选择孩子更感兴趣的写作主题",
                "增加素材积累和阅读时间"
            ],
            "expected_benefit": "重新激发写作兴趣",
            "target_mastery_level": "LEARNING",
            "estimated_duration": "1 周"
        })

    weak_types = progress.get("weak_types", [])
    if weak_types:
        recommendations.append({
            "recommendation_id": str(uuid.uuid4())[:8],
            "category": "weakness_improvement",
            "priority": "high",
            "title": "加强薄弱类型练习",
            "description": f"需要加强练习的作文类型：{', '.join(weak_types)}",
            "action_items": [
                f"每周安排 1 次 {weak_types[0] if weak_types else '相关'} 类型练习",
                "参考优秀范文进行模仿",
                "记录每次练习的进步点"
            ],
            "expected_benefit": "补齐写作短板",
            "target_mastery_level": "FAMILIAR",
            "estimated_duration": "4 周"
        })

    for difficulty in difficulties:
        if difficulty.get("type") == "weak_structure":
            recommendations.append({
                "recommendation_id": str(uuid.uuid4())[:8],
                "category": "support",
                "priority": "high",
                "title": "提升文章结构能力",
                "description": difficulty.get("message", "文章结构能力需要提升"),
                "action_items": [
                    "学习经典作文的结构模式",
                    "练习列提纲的习惯",
                    "使用思维导图整理思路",
                    "对比分析好作文的结构"
                ],
                "expected_benefit": "提高文章组织能力",
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
    quality_values = [r.get("quality_score", 0.0) for r in sorted_records]

    n = len(quality_values)
    x_mean = sum(range(n)) / n
    y_mean = sum(quality_values) / n

    numerator = sum((i - x_mean) * (quality_values[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))

    slope = numerator / denominator if denominator != 0 else 0.0

    if slope > 0.1:
        curve_type = "improving"
        prediction = "写作水平呈上升趋势"
    elif slope < -0.1:
        curve_type = "declining"
        prediction = "写作水平呈下降趋势，需要关注"
    else:
        curve_type = "stable"
        prediction = "写作水平保持稳定"

    recent_avg = sum(quality_values[-3:]) / 3 if len(quality_values) >= 3 else y_mean
    next_trend = "上升" if slope > 0 else "下降"

    return {
        "data_points": quality_values,
        "curve_type": curve_type,
        "slope": round(slope, 4),
        "prediction": f"{prediction}，预计下一阶段趋势 {next_trend}",
        "recent_average": round(recent_avg, 2),
        "overall_average": round(y_mean, 2),
        "trend_description": f"平均每次写作质量变化 {abs(slope):.2f} 分"
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
    avg_quality = sum(r.get("quality_score", 0.0) for r in records) / total_sessions

    structure_scores = [r.get("structure_score", 0.0) for r in records]
    avg_structure = sum(structure_scores) / len(structure_scores) if structure_scores else 0.0

    word_counts = [r.get("word_count", 0) for r in records]
    avg_words = sum(word_counts) / len(word_counts) if word_counts else 0

    excellent_count = sum(1 for r in records if r.get("quality_score", 0.0) >= 8.0)
    excellent_rate = excellent_count / total_sessions if total_sessions > 0 else 0.0

    if total_sessions >= 10 and avg_quality >= 7.0 and avg_structure >= 7.0:
        return "MASTERED"
    elif total_sessions >= 5 and avg_quality >= 6.0:
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
        "writing_goals": [],
        "parent_notes": []
    }

    writing_types = defaultdict(int)
    for record in records:
        writing_type = record.get("writing_type", "未知")
        writing_types[writing_type] += 1

    favorite_types = sorted(writing_types.items(), key=lambda x: x[1], reverse=True)[:5]
    context["detected_interests"] = [t for t, _ in favorite_types]

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

    quality_by_duration = defaultdict(list)
    for r in records:
        duration_bucket = r.get("duration_minutes", 0) // 5
        quality_by_duration[duration_bucket].append(r.get("quality_score", 0.0))

    best_bucket = max(quality_by_duration.items(), key=lambda x: sum(x[1])/len(x[1]) if x[1] else 0)[0]
    optimal_duration = best_bucket * 5 + 2

    writing_types = defaultdict(int)
    for r in records:
        wtype = r.get("writing_type", "记叙文")
        writing_types[wtype] += 1

    most_practiced = max(writing_types.items(), key=lambda x: x[1])[0] if writing_types else "记叙文"

    insights = []
    if avg_duration > 45:
        insights.append("建议减少单次写作时长以保持孩子专注力")
    if quality_by_duration.get(0) and sum(quality_by_duration.get(0, [])) / len(quality_by_duration[0]) > avg_duration:
        insights.append("短时高频练习可能更适合当前阶段")

    return {
        "average_duration": round(avg_duration, 1),
        "optimal_duration": optimal_duration,
        "most_practiced_type": most_practiced,
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
            "total_words": 0,
            "avg_quality": 0.0,
            "improvements": [],
            "areas_for_growth": []
        }

    total_sessions = len(records)
    total_words = sum(r.get("word_count", 0) for r in records)
    avg_quality = sum(r.get("quality_score", 0.0) for r in records) / total_sessions

    improvements = []
    areas_for_growth = []

    if avg_quality >= 7.0:
        improvements.append("写作质量表现优秀")
    elif avg_quality < 5.0:
        areas_for_growth.append("写作质量有待提升")

    structure_scores = [r.get("structure_score", 0.0) for r in records]
    avg_structure = sum(structure_scores) / len(structure_scores) if structure_scores else 0.0
    if avg_structure >= 6.0:
        improvements.append("文章结构能力良好")
    else:
        areas_for_growth.append("文章结构能力需要加强")

    return {
        "sessions": total_sessions,
        "total_words": total_words,
        "avg_quality": round(avg_quality, 1),
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
