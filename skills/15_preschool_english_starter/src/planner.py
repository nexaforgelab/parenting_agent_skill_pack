"""Planning engine for 幼儿英语启蒙 Agent."""
from typing import Any, Dict, List
from datetime import datetime
from collections import defaultdict
import uuid

SKILL_FLOW = ['输入年龄和英语基础', '生成每日 10 分钟启蒙计划', '推荐单词、句型、绘本、儿歌', '语音跟读', '记录掌握情况']
SAFETY_NOTES = ['本 Skill 提供家庭教育和生活管理建议，不替代专业人士意见。', '涉及安全、法律、医疗或教育政策时，应提示家长二次核验。', '输出应尊重家庭差异，不用单一标准评价孩子或父母。']
DEFAULT_DELIVERABLES = ['英语启蒙路线', '每日任务', '亲子对话脚本', '个性化建议']


def build_known_facts(payload: Dict[str, Any]) -> List[str]:
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
    base_tasks = [
        "评估孩子当前英语水平",
        "每天学习 5-10 个新单词",
        "使用儿歌和绘本辅助学习",
        "进行简单的英语对话练习",
        "一周后复习已学内容",
    ]
    plan: List[Dict[str, str]] = []
    for i, task in enumerate(base_tasks, start=1):
        plan.append({
            "day": f"D{i}",
            "task": task,
            "owner": "家长/主要照护人",
            "evidence_to_record": "学习的单词、正确率、孩子反应",
            "difficulty": "低" if i <= 3 else "中"
        })
    return plan


def build_deliverables(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "required": DEFAULT_DELIVERABLES,
        "tables": {
            "daily_learning": ["日期", "单词", "翻译", "掌握度", "备注"],
            "weekly_review": ["单词", "翻译", "正确次数", "错误次数", "掌握程度"]
        }
    }


def next_fields() -> List[str]:
    return ["孩子年龄", "今天学习的单词", "正确率", "孩子反应", "需要复习的单词"]


def analyze_learning_progress(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not records:
        return {"total_words": 0, "mastered_words": 0, "average_mastery": 0.0}

    total = len(set(r.get("word", "") for r in records if r.get("word")))
    total_mastery = sum(r.get("mastery_score", 0.0) for r in records)
    avg_mastery = total_mastery / len(records) if records else 0.0

    mastered = sum(1 for r in records if r.get("mastery_score", 0.0) >= 8.0)

    by_category = defaultdict(int)
    for r in records:
        by_category[r.get("category", "")] += 1

    difficult = [r.get("word", "") for r in records if r.get("mastery_score", 0.0) < 5.0][:10]

    return {
        "total_words": total,
        "mastered_words": mastered,
        "learning_words": total - mastered,
        "total_practice": len(records),
        "average_mastery": round(avg_mastery, 2),
        "category_breakdown": dict(by_category),
        "difficult_words": difficult,
        "summary": f"共学习 {total} 个单词，掌握 {mastered} 个"
    }


def detect_learning_difficulties(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    difficulties = []
    if len(records) < 3:
        return difficulties

    recent = records[-5:]
    avg_mastery = sum(r.get("mastery_score", 0.0) for r in recent) / len(recent)

    if avg_mastery < 4.0:
        difficulties.append({
            "type": "low_mastery",
            "severity": "high",
            "message": "单词掌握度偏低，需要调整学习方法",
            "suggestion": "减少每日单词数量，增加复习频率"
        })

    return difficulties


def generate_personalized_recommendations(child_profile: Dict[str, Any], records: List[Dict[str, Any]], progress: Dict[str, Any]) -> List[Dict[str, Any]]:
    recommendations = []
    age = child_profile.get("age", "未知")
    if "岁" in str(age):
        age_num = int(age.split("岁")[0]) if age.split("岁")[0].isdigit() else 4
    else:
        age_num = 4

    daily_words = min(3 + age_num // 2, 10)

    recommendations.append({
        "recommendation_id": str(uuid.uuid4())[:8],
        "category": "learning_plan",
        "priority": "high",
        "title": "调整每日学习量",
        "description": f"针对 {age} 孩子，建议每天学习 {daily_words} 个新单词",
        "action_items": [f"每天固定时间学习 {daily_words} 个单词", "配合图片和动作记忆", "使用儿歌辅助学习"]
    })

    difficult = progress.get("difficult_words", [])
    if difficult:
        recommendations.append({
            "recommendation_id": str(uuid.uuid4())[:8],
            "category": "review",
            "priority": "medium",
            "title": "加强困难单词复习",
            "description": f"以下单词需要加强: {', '.join(difficult[:5])}",
            "action_items": ["每天复习困难单词", "使用多种方式练习", "关联情境加深记忆"]
        })

    return recommendations


def analyze_learning_curve(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    if len(records) < 3:
        return {"curve_type": "insufficient_data", "slope": 0.0}

    sorted_records = sorted(records, key=lambda x: x.get("timestamp", ""))
    mastery_values = [r.get("mastery_score", 0.0) for r in sorted_records]

    n = len(mastery_values)
    x_mean = sum(range(n)) / n
    y_mean = sum(mastery_values) / n
    numerator = sum((i - x_mean) * (mastery_values[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    slope = numerator / denominator if denominator != 0 else 0.0

    if slope > 0.05:
        curve_type = "improving"
    elif slope < -0.05:
        curve_type = "declining"
    else:
        curve_type = "stable"

    return {"curve_type": curve_type, "slope": round(slope, 4)}


def calculate_mastery_level(records: List[Dict[str, Any]]) -> str:
    if not records:
        return "NOT_STARTED"
    total = len(records)
    avg_mastery = sum(r.get("mastery_score", 0.0) for r in records) / total
    if total >= 20 and avg_mastery >= 8.0:
        return "MASTERED"
    elif total >= 10 and avg_mastery >= 6.0:
        return "FAMILIAR"
    elif total >= 5:
        return "LEARNING"
    return "NOT_STARTED"


def create_session_context(child_profile: Dict[str, Any], records: List[Dict[str, Any]], preferences: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "session_id": str(uuid.uuid4())[:8],
        "child_id": child_profile.get("nickname", "未知孩子"),
        "start_time": datetime.now().isoformat(),
        "current_words": [r.get("word", "") for r in records[-10:] if r.get("word")],
        "conversation_history": [],
        "preferences": preferences
    }


def run_full_analysis(payload: Dict[str, Any]) -> Dict[str, Any]:
    records = payload.get("raw_records", [])
    child_profile = payload.get("child_profile", {})
    preferences = payload.get("preferences", {})

    progress = analyze_learning_progress(records)
    difficulties = detect_learning_difficulties(records)
    recommendations = generate_personalized_recommendations(child_profile, records, progress)
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