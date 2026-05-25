"""Planning engine for 睡前故事生成 Agent.

提供增强的规划功能，包括数据分析、异常检测、个性化推荐、上下文记忆和学习曲线分析。
"""
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import uuid

SKILL_FLOW = ['输入孩子年龄、兴趣、教育主题', '生成睡前故事', '控制时长和语气', '加入安抚结尾', '保存孩子喜欢的角色']
SAFETY_NOTES = ['本 Skill 提供家庭教育和生活管理建议，不替代专业人士意见。', '涉及安全、法律、医疗、财务或教育政策时，应提示家长二次核验。', '输出应尊重家庭差异，不用单一标准评价孩子或父母。']
DEFAULT_DELIVERABLES = ['睡前故事', '连续故事系列', '音频版脚本', '个性化建议', '进度报告']


def build_known_facts(payload: Dict[str, Any]) -> List[str]:
    """构建已知事实列表"""
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


def analyze_storytelling_progress(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析讲故事进度"""
    if not records:
        return {
            "total_stories": 0,
            "total_minutes": 0,
            "average_engagement": 0.0,
            "trend": "insufficient_data"
        }

    total_stories = len(records)
    total_minutes = sum(r.get("duration_minutes", 0) for r in records)

    engagement_scores = [r.get("child_engagement", 0.0) for r in records if r.get("child_engagement")]
    average_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0.0

    themes = defaultdict(int)
    for record in records:
        themes[record.get("story_theme", "")] += 1

    favorite_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)[:3]

    characters = [r.get("favorite_character", "") for r in records if r.get("favorite_character")]
    favorite_characters = list(set(characters))[:3]

    return {
        "total_stories": total_stories,
        "total_minutes": total_minutes,
        "average_engagement": round(average_engagement, 2),
        "favorite_themes": [t for t, _ in favorite_themes],
        "favorite_characters": favorite_characters,
        "summary": f"共讲了 {total_stories} 个故事，累计 {total_minutes} 分钟"
    }


def detect_storytelling_difficulties(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """检测讲故事困难"""
    difficulties = []

    if len(records) < 3:
        return difficulties

    recent_records = records[-5:]
    engagement_scores = [r.get("child_engagement", 0.0) for r in recent_records]

    if engagement_scores:
        avg_recent = sum(engagement_scores) / len(engagement_scores)
        if avg_recent < 4.0:
            difficulties.append({
                "type": "low_engagement",
                "severity": "high",
                "message": "孩子近期听故事投入度较低",
                "suggestion": "尝试更换故事主题或增加互动"
            })

    return difficulties


def generate_personalized_recommendations(
    child_profile: Dict[str, Any],
    records: List[Dict[str, Any]],
    progress: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """生成个性化推荐"""
    recommendations = []

    age = child_profile.get("age", "未知")
    if "岁" in str(age):
        age_num = int(age.split("岁")[0]) if age.split("岁")[0].isdigit() else 3
    else:
        age_num = 3

    recommendations.append({
        "recommendation_id": str(uuid.uuid4())[:8],
        "category": "story_planning",
        "priority": "high",
        "title": "根据年龄调整故事时长",
        "description": f"针对 {age} 孩子，建议故事时长控制在 {5 + age_num} 分钟左右",
        "action_items": [
            f"每天固定睡前时间讲故事 {5 + age_num} 分钟",
            "选择适合年龄的故事主题",
            "结尾加入舒缓的安抚语"
        ],
        "expected_benefit": "帮助孩子更好地入睡"
    })

    favorite_themes = progress.get("favorite_themes", [])
    if favorite_themes:
        recommendations.append({
            "recommendation_id": str(uuid.uuid4())[:8],
            "category": "interest",
            "priority": "medium",
            "title": "延续兴趣主题",
            "description": f"孩子喜欢 {', '.join(favorite_themes[:2])} 主题的故事",
            "action_items": [
                f"寻找更多 {favorite_themes[0] if favorite_themes else '相关'} 主题故事",
                "围绕兴趣主题创作连续故事"
            ],
            "expected_benefit": "保持孩子的故事兴趣"
        })

    return recommendations


def analyze_storytelling_curve(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析讲故事曲线"""
    if len(records) < 3:
        return {
            "curve_type": "insufficient_data",
            "slope": 0.0
        }

    sorted_records = sorted(records, key=lambda x: x.get("timestamp", ""))
    engagement_values = [r.get("child_engagement", 0.0) for r in sorted_records]

    n = len(engagement_values)
    x_mean = sum(range(n)) / n
    y_mean = sum(engagement_values) / n

    numerator = sum((i - x_mean) * (engagement_values[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))

    slope = numerator / denominator if denominator != 0 else 0.0

    if slope > 0.1:
        curve_type = "improving"
    elif slope < -0.1:
        curve_type = "declining"
    else:
        curve_type = "stable"

    return {
        "curve_type": curve_type,
        "slope": round(slope, 4),
        "prediction": f"投入度趋势 {curve_type}"
    }


def calculate_mastery_level(records: List[Dict[str, Any]]) -> str:
    """计算掌握程度"""
    if not records:
        return "NOT_STARTED"

    total_stories = len(records)
    avg_engagement = sum(r.get("child_engagement", 0.0) for r in records) / total_stories

    if total_stories >= 10 and avg_engagement >= 7.0:
        return "MASTERED"
    elif total_stories >= 5 and avg_engagement >= 5.0:
        return "FAMILIAR"
    elif total_stories >= 2:
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
        "favorite_stories": records[-10:] if records else [],
        "conversation_history": [],
        "preferences": preferences,
        "detected_interests": [],
        "storytelling_goals": []
    }

    themes = defaultdict(int)
    for record in records:
        themes[record.get("story_theme", "")] += 1

    favorite_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)[:5]
    context["detected_interests"] = [t for t, _ in favorite_themes]

    return context


def run_full_analysis(payload: Dict[str, Any]) -> Dict[str, Any]:
    """运行完整分析"""
    records = payload.get("raw_records", [])
    child_profile = payload.get("child_profile", {})
    preferences = payload.get("preferences", {})

    progress = analyze_storytelling_progress(records)
    difficulties = detect_storytelling_difficulties(records)
    recommendations = generate_personalized_recommendations(child_profile, records, progress)
    storytelling_curve = analyze_storytelling_curve(records)
    mastery_level = calculate_mastery_level(records)
    session_context = create_session_context(child_profile, records, preferences)

    return {
        "progress": progress,
        "difficulties": difficulties,
        "recommendations": recommendations,
        "storytelling_curve": storytelling_curve,
        "mastery_level": mastery_level,
        "session_context": session_context
    }