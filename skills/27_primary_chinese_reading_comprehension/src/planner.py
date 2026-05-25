"""Planning engine for 小学语文阅读理解 Agent.

提供增强的规划功能，包括数据分析、异常检测、个性化推荐、上下文记忆和学习曲线分析。
"""
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import uuid

SKILL_FLOW = ['上传阅读题', '分析文章结构', '判断题型', '提取得分点', '批改孩子答案', '输出改进版']
SAFETY_NOTES = ['本 Skill 以启发式陪练为主，避免直接替孩子完成作业或代写成品。', '输出应包含引导问题、解题路径、错因分析和复习建议，保留孩子自主思考过程。', '涉及教材、地区考试政策或校内要求时，应提示以学校老师最新要求为准。']
DEFAULT_DELIVERABLES = ['得分点拆解', '答题模板', '同类训练']


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
            "total_questions": 0,
            "average_score": 0.0,
            "trend": "insufficient_data",
            "summary": "暂无足够数据进行分析"
        }

    total_sessions = len(records)
    total_questions = sum(r.get("questions_attempted", 0) for r in records)

    scores = [r.get("score", 0.0) for r in records if r.get("score")]
    average_score = sum(scores) / len(scores) if scores else 0.0

    recent_records = records[-7:] if len(records) >= 7 else records
    recent_avg = sum(r.get("score", 0.0) for r in recent_records) / len(recent_records) if recent_records else 0.0

    if len(records) >= 14:
        earlier_records = records[:7]
        earlier_avg = sum(r.get("score", 0.0) for r in earlier_records) / len(earlier_records)
        if recent_avg > earlier_avg * 1.1:
            trend = "improving"
        elif recent_avg < earlier_avg * 0.9:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"

    question_types = defaultdict(int)
    for record in records:
        qtype = record.get("question_type", "未知")
        question_types[qtype] += 1

    most_practiced = sorted(question_types.items(), key=lambda x: x[1], reverse=True)[:3]
    weak_types = [t for t, count in question_types.items() if count < 2]

    return {
        "total_sessions": total_sessions,
        "total_questions": total_questions,
        "average_score": round(average_score, 2),
        "recent_trend": trend,
        "most_practiced_types": [t for t, _ in most_practiced],
        "weak_types": weak_types,
        "summary": f"共完成 {total_sessions} 次练习，答题 {total_questions} 道"
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
    scores = [r.get("score", 0.0) for r in recent_records]

    if scores:
        avg_recent = sum(scores) / len(scores)
        if avg_recent < 60:
            difficulties.append({
                "type": "low_score",
                "severity": "high",
                "message": "阅读理解得分较低，需要加强训练",
                "suggestion": "建议增加阅读量，加强文章分析训练"
            })

    declining_count = 0
    for i in range(1, len(scores)):
        if scores[i] < scores[i-1]:
            declining_count += 1

    if declining_count >= 3:
        difficulties.append({
            "type": "declining_score",
            "severity": "medium",
            "message": "阅读理解得分持续下降，可能出现理解疲劳",
            "suggestion": "建议减少单次练习时长，增加休息间隔"
        })

    accuracy_rates = [r.get("accuracy_rate", 0.0) for r in recent_records]
    if accuracy_rates:
        avg_accuracy = sum(accuracy_rates) / len(accuracy_rates)
        if avg_accuracy < 0.6:
            difficulties.append({
                "type": "low_accuracy",
                "severity": "medium",
                "message": "答题准确率偏低",
                "suggestion": "加强得分点提取训练"
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
        "category": "reading_plan",
        "priority": "high",
        "title": "根据年级调整阅读计划",
        "description": f"针对 {grade} 学生，建议每次阅读练习控制在 {10 + grade_num * 2} 分钟左右",
        "action_items": [
            f"每周安排 {2 + grade_num // 3} 次阅读练习",
            "每次练习包含快速阅读、分析结构、答题三个步骤",
            "完成后进行自我检查"
        ],
        "expected_benefit": "提高阅读效率和理解能力",
        "target_mastery_level": "FAMILIAR",
        "estimated_duration": "2 周"
    })

    if progress.get("trend") == "improving":
        recommendations.append({
            "recommendation_id": str(uuid.uuid4())[:8],
            "category": "progression",
            "priority": "medium",
            "title": "当前阅读状态良好",
            "description": "孩子阅读进步明显，可以适当提升难度",
            "action_items": [
                "尝试更复杂的文章类型",
                "增加阅读速度训练",
                "挑战不同题型的阅读材料"
            ],
            "expected_benefit": "促进阅读能力全面发展",
            "target_mastery_level": "MASTERED",
            "estimated_duration": "1 个月"
        })
    elif progress.get("trend") == "declining":
        recommendations.append({
            "recommendation_id": str(uuid.uuid4())[:8],
            "category": "adjustment",
            "priority": "high",
            "title": "需要调整学习节奏",
            "description": "检测到阅读进步下降，建议降低学习强度",
            "action_items": [
                "减少单次练习时长",
                "选择孩子更感兴趣的阅读材料",
                "增加阅读量和阅读兴趣培养"
            ],
            "expected_benefit": "重新激发阅读兴趣",
            "target_mastery_level": "LEARNING",
            "estimated_duration": "1 周"
        })

    weak_types = progress.get("weak_types", [])
    if weak_types:
        recommendations.append({
            "recommendation_id": str(uuid.uuid4())[:8],
            "category": "weakness_improvement",
            "priority": "high",
            "title": "加强薄弱题型练习",
            "description": f"需要加强练习的题型：{', '.join(weak_types)}",
            "action_items": [
                f"每周安排 1 次 {weak_types[0] if weak_types else '相关'} 题型练习",
                "学习该题型的答题技巧",
                "记录每次练习的进步点"
            ],
            "expected_benefit": "补齐阅读短板",
            "target_mastery_level": "FAMILIAR",
            "estimated_duration": "4 周"
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
    score_values = [r.get("score", 0.0) for r in sorted_records]

    n = len(score_values)
    x_mean = sum(range(n)) / n
    y_mean = sum(score_values) / n

    numerator = sum((i - x_mean) * (score_values[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))

    slope = numerator / denominator if denominator != 0 else 0.0

    if slope > 2:
        curve_type = "improving"
        prediction = "阅读水平呈上升趋势"
    elif slope < -2:
        curve_type = "declining"
        prediction = "阅读水平呈下降趋势，需要关注"
    else:
        curve_type = "stable"
        prediction = "阅读水平保持稳定"

    recent_avg = sum(score_values[-3:]) / 3 if len(score_values) >= 3 else y_mean
    next_trend = "上升" if slope > 0 else "下降"

    return {
        "data_points": score_values,
        "curve_type": curve_type,
        "slope": round(slope, 4),
        "prediction": f"{prediction}，预计下一阶段趋势 {next_trend}",
        "recent_average": round(recent_avg, 2),
        "overall_average": round(y_mean, 2),
        "trend_description": f"平均每次阅读得分变化 {abs(slope):.2f} 分"
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
    avg_score = sum(r.get("score", 0.0) for r in records) / total_sessions

    accuracy_rates = [r.get("accuracy_rate", 0.0) for r in records]
    avg_accuracy = sum(accuracy_rates) / len(accuracy_rates) if accuracy_rates else 0.0

    excellent_count = sum(1 for r in records if r.get("score", 0.0) >= 85)
    excellent_rate = excellent_count / total_sessions if total_sessions > 0 else 0.0

    if total_sessions >= 10 and avg_score >= 75 and avg_accuracy >= 0.7:
        return "MASTERED"
    elif total_sessions >= 5 and avg_score >= 60:
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

    question_types = defaultdict(int)
    for record in records:
        qtype = record.get("question_type", "未知")
        question_types[qtype] += 1

    favorite_types = sorted(question_types.items(), key=lambda x: x[1], reverse=True)[:5]
    context["detected_interests"] = [t for t, _ in favorite_types]

    return context


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

    return {
        "progress": progress,
        "difficulties": difficulties,
        "recommendations": recommendations,
        "learning_curve": learning_curve,
        "mastery_level": mastery_level,
        "session_context": session_context
    }
