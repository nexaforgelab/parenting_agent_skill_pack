"""Planning engine for 小学生阅读计划 Agent.

提供增强的规划功能，包括数据分析、异常检测、个性化推荐、上下文记忆和学习曲线分析。
"""
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import uuid

SKILL_FLOW = ['收集阅读兴趣', '匹配合适书目', '制定阅读计划', '追踪阅读进度', '阅读交流', '效果评估']
SAFETY_NOTES = ['本 Skill 以启发式陪练为主，避免直接替孩子完成作业或代写成品。', '输出应包含引导问题、解题路径、错因分析和复习建议，保留孩子自主思考过程。', '涉及教材、地区考试政策或校内要求时，应提示以学校老师最新要求为准。']
DEFAULT_DELIVERABLES = ['阅读计划表', '书目推荐清单', '阅读记录表']


def build_known_facts(payload: Dict[str, Any]) -> List[str]:
    """构建已知事实列表"""
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
    """构建分析结果"""
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
    """构建行动计划"""
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
    """构建交付物清单"""
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
    """获取下次追踪字段列表"""
    return [
        "孩子年龄/月龄",
        "今天新增记录",
        "执行了哪一步",
        "孩子反应",
        "家长感受",
        "需要调整的限制条件"
    ]


def analyze_learning_progress(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析学习进度"""
    if not records:
        return {
            "total_sessions": 0,
            "total_books": 0,
            "total_pages": 0,
            "completion_rate": 0.0,
            "average_engagement": 0.0,
            "trend": "insufficient_data",
            "summary": "暂无足够数据进行分析"
        }

    total_sessions = len(records)
    total_books = len(set(r.get("book_title", "") for r in records if r.get("book_title")))
    total_pages = sum(r.get("pages_read", 0) for r in records)

    engagement_scores = [r.get("engagement_score", 0.0) for r in records if r.get("engagement_score")]
    average_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0.0

    completed_books = sum(1 for r in records if r.get("is_completed", False))
    completion_rate = completed_books / total_books if total_books > 0 else 0.0

    recent_records = records[-7:] if len(records) >= 7 else records
    recent_avg = sum(r.get("pages_read", 0) for r in recent_records) / len(recent_records) if recent_records else 0.0

    if len(records) >= 14:
        earlier_records = records[:7]
        earlier_avg = sum(r.get("pages_read", 0) for r in earlier_records) / len(earlier_records)
        if recent_avg > earlier_avg * 1.1:
            trend = "improving"
        elif recent_avg < earlier_avg * 0.9:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"

    genres = defaultdict(int)
    for record in records:
        genre = record.get("genre", "未知")
        genres[genre] += 1

    favorite_genres = sorted(genres.items(), key=lambda x: x[1], reverse=True)[:3]

    return {
        "total_sessions": total_sessions,
        "total_books": total_books,
        "total_pages": total_pages,
        "completion_rate": round(completion_rate, 2),
        "average_engagement": round(average_engagement, 2),
        "recent_trend": trend,
        "favorite_genres": [g for g, _ in favorite_genres],
        "summary": f"共完成 {total_sessions} 次阅读，读完 {completed_books} 本书"
    }


def detect_learning_difficulties(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """检测学习困难"""
    difficulties = []

    if len(records) < 3:
        return difficulties

    recent_records = records[-5:]
    pages_read = [r.get("pages_read", 0) for r in recent_records]

    if pages_read:
        avg_pages = sum(pages_read) / len(pages_read)
        if avg_pages < 5:
            difficulties.append({
                "type": "low_engagement",
                "severity": "high",
                "message": "阅读页数偏少，需要增加阅读兴趣",
                "suggestion": "建议选择孩子更感兴趣的书籍"
            })

    declining_count = 0
    for i in range(1, len(pages_read)):
        if pages_read[i] < pages_read[i-1]:
            declining_count += 1

    if declining_count >= 3:
        difficulties.append({
            "type": "declining_interest",
            "severity": "medium",
            "message": "阅读兴趣持续下降",
            "suggestion": "建议更换阅读主题，增加互动讨论"
        })

    engagement_scores = [r.get("engagement_score", 0.0) for r in recent_records]
    if engagement_scores:
        avg_engagement = sum(engagement_scores) / len(engagement_scores)
        if avg_engagement < 3.0:
            difficulties.append({
                "type": "low_engagement_score",
                "severity": "medium",
                "message": "阅读投入度偏低",
                "suggestion": "增加亲子共读时间"
            })

    return difficulties


def generate_personalized_recommendations(
    child_profile: Dict[str, Any],
    records: List[Dict[str, Any]],
    progress: Dict[str, Any],
    difficulties: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """生成个性化推荐"""
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
        "title": "根据年级制定阅读计划",
        "description": f"针对 {grade} 学生，建议每周阅读 {2 + grade_num // 2} 本书",
        "action_items": [
            f"每天安排 {10 + grade_num * 2} 分钟阅读时间",
            "每周至少完成 1 本适龄读物",
            "鼓励写阅读笔记"
        ],
        "expected_benefit": "培养良好阅读习惯",
        "target_mastery_level": "FAMILIAR",
        "estimated_duration": "4 周"
    })

    favorite_genres = progress.get("favorite_genres", [])
    if favorite_genres:
        recommendations.append({
            "recommendation_id": str(uuid.uuid4())[:8],
            "category": "recommendation",
            "priority": "medium",
            "title": "推荐同类型书籍",
            "description": f"孩子喜欢 {', '.join(favorite_genres)} 类书籍",
            "action_items": [
                f"寻找更多 {favorite_genres[0] if favorite_genres else '相关'} 类书籍",
                "设置阅读挑战目标",
                "分享阅读感受"
            ],
            "expected_benefit": "保持阅读兴趣",
            "target_mastery_level": "FAMILIAR",
            "estimated_duration": "2 周"
        })

    if progress.get("trend") == "declining":
        recommendations.append({
            "recommendation_id": str(uuid.uuid4())[:8],
            "category": "adjustment",
            "priority": "high",
            "title": "需要调整阅读计划",
            "description": "检测到阅读兴趣下降，建议调整计划",
            "action_items": [
                "减少单次阅读时长",
                "选择图文并茂的书籍",
                "增加亲子共读时间"
            ],
            "expected_benefit": "重新激发阅读兴趣",
            "target_mastery_level": "LEARNING",
            "estimated_duration": "1 周"
        })

    return recommendations


def analyze_learning_curve(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析学习曲线"""
    if len(records) < 3:
        return {
            "data_points": [],
            "curve_type": "insufficient_data",
            "slope": 0.0,
            "prediction": "数据不足，无法预测"
        }

    sorted_records = sorted(records, key=lambda x: x.get("timestamp", ""))
    page_values = [r.get("pages_read", 0) for r in sorted_records]

    n = len(page_values)
    x_mean = sum(range(n)) / n
    y_mean = sum(page_values) / n

    numerator = sum((i - x_mean) * (page_values[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))

    slope = numerator / denominator if denominator != 0 else 0.0

    if slope > 2:
        curve_type = "improving"
        prediction = "阅读量呈上升趋势"
    elif slope < -2:
        curve_type = "declining"
        prediction = "阅读量呈下降趋势，需要关注"
    else:
        curve_type = "stable"
        prediction = "阅读量保持稳定"

    recent_avg = sum(page_values[-3:]) / 3 if len(page_values) >= 3 else y_mean
    next_trend = "上升" if slope > 0 else "下降"

    return {
        "data_points": page_values,
        "curve_type": curve_type,
        "slope": round(slope, 4),
        "prediction": f"{prediction}，预计下一阶段趋势 {next_trend}",
        "recent_average": round(recent_avg, 2),
        "overall_average": round(y_mean, 2),
        "trend_description": f"平均每次阅读页数变化 {abs(slope):.2f} 页"
    }


def calculate_mastery_level(records: List[Dict[str, Any]]) -> str:
    """计算掌握程度"""
    if not records:
        return "NOT_STARTED"

    total_sessions = len(records)
    avg_engagement = sum(r.get("engagement_score", 0.0) for r in records) / total_sessions

    completed_books = len(set(r.get("book_title", "") for r in records if r.get("is_completed", False)))

    if total_sessions >= 20 and avg_engagement >= 4.0 and completed_books >= 5:
        return "MASTERED"
    elif total_sessions >= 10 and avg_engagement >= 3.0:
        return "FAMILIAR"
    elif total_sessions >= 3:
        return "LEARNING"
    else:
        return "NOT_STARTED"


def create_session_context(
    child_profile: Dict[str, Any],
    records: List[Dict[str, Any]],
    preferences: Dict[str, Any]
) -> Dict[str, Any]:
    """创建会话上下文"""
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

    genres = defaultdict(int)
    for record in records:
        genre = record.get("genre", "未知")
        genres[genre] += 1

    favorite_genres = sorted(genres.items(), key=lambda x: x[1], reverse=True)[:5]
    context["detected_interests"] = [g for g, _ in favorite_genres]

    return context


def run_full_analysis(payload: Dict[str, Any]) -> Dict[str, Any]:
    """运行完整分析"""
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
