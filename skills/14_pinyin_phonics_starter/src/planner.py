"""Planning engine for 拼音启蒙 Agent."""
from typing import Any, Dict, List
from datetime import datetime
from collections import defaultdict
import uuid

SKILL_FLOW = ['识别孩子当前水平', '生成声母、韵母、整体认读训练', '语音跟读', '自动纠错', '生成练习卡']
SAFETY_NOTES = ['本 Skill 提供家庭教育和生活管理建议，不替代专业人士意见。', '涉及安全、法律、医疗、财务或教育政策时，应提示家长二次核验。', '输出应尊重家庭差异，不用单一标准评价孩子或父母。']
DEFAULT_DELIVERABLES = ['拼音训练表', '发音反馈', '每日练习', '个性化建议']


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
        "评估孩子当前拼音水平",
        "每天学习 3-5 个拼音",
        "使用跟读练习发音",
        "记录发音得分",
        "定期复习已学拼音",
    ]
    plan: List[Dict[str, str]] = []
    for i, task in enumerate(base_tasks, start=1):
        plan.append({
            "day": f"D{i}",
            "task": task,
            "owner": "家长/主要照护人",
            "evidence_to_record": "学习的拼音、发音得分、正确率",
            "difficulty": "低" if i <= 3 else "中"
        })
    return plan


def build_deliverables(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "required": DEFAULT_DELIVERABLES,
        "tables": {
            "daily_learning": ["日期", "拼音", "类型", "得分", "备注"],
            "weekly_review": ["拼音", "类型", "正确次数", "错误次数", "掌握程度"]
        }
    }


def next_fields() -> List[str]:
    return ["孩子年龄", "今天学习的拼音", "发音得分", "正确率", "需要复习的拼音"]


def analyze_learning_progress(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not records:
        return {"total_pinyin": 0, "mastered_initial": 0, "mastered_final": 0, "average_score": 0.0}

    total = len(set(r.get("pinyin", "") for r in records if r.get("pinyin")))
    total_score = sum(r.get("pronunciation_score", 0.0) for r in records)
    avg_score = total_score / len(records) if records else 0.0

    by_type = defaultdict(int)
    mastered_by_type = defaultdict(int)
    for r in records:
        ptype = r.get("pinyin_type", "声母")
        by_type[ptype] += 1
        if r.get("pronunciation_score", 0.0) >= 8.0:
            mastered_by_type[ptype] += 1

    difficult = [r.get("pinyin", "") for r in records if r.get("pronunciation_score", 0.0) < 6.0][:10]

    return {
        "total_pinyin": total,
        "mastered_initial": mastered_by_type.get("声母", 0),
        "mastered_final": mastered_by_type.get("韵母", 0),
        "mastered_compound": mastered_by_type.get("整体认读", 0),
        "average_score": round(avg_score, 2),
        "difficult_pinyin": difficult,
        "summary": f"共学习 {total} 个拼音"
    }


def detect_learning_difficulties(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    difficulties = []
    if len(records) < 3:
        return difficulties

    recent = records[-5:]
    avg_score = sum(r.get("pronunciation_score", 0.0) for r in recent) / len(recent)

    if avg_score < 5.0:
        difficulties.append({
            "type": "low_score",
            "severity": "high",
            "message": "发音得分偏低，需要加强练习",
            "suggestion": "增加跟读练习时间，使用慢速示范"
        })

    return difficulties


def generate_personalized_recommendations(child_profile: Dict[str, Any], records: List[Dict[str, Any]], progress: Dict[str, Any]) -> List[Dict[str, Any]]:
    recommendations = []
    age = child_profile.get("age", "未知")
    if "岁" in str(age):
        age_num = int(age.split("岁")[0]) if age.split("岁")[0].isdigit() else 5
    else:
        age_num = 5

    daily_pinyin = min(2 + age_num // 3, 6)

    recommendations.append({
        "recommendation_id": str(uuid.uuid4())[:8],
        "category": "learning_plan",
        "priority": "high",
        "title": "调整每日学习量",
        "description": f"针对 {age} 孩子，建议每天学习 {daily_pinyin} 个新拼音",
        "action_items": [f"每天固定时间学习 {daily_pinyin} 个拼音", "使用跟读练习", "配合图片记忆"]
    })

    difficult = progress.get("difficult_pinyin", [])
    if difficult:
        recommendations.append({
            "recommendation_id": str(uuid.uuid4())[:8],
            "category": "review",
            "priority": "medium",
            "title": "加强困难拼音练习",
            "description": f"以下拼音需要加强: {', '.join(difficult[:5])}",
            "action_items": ["每天复习困难拼音", "放慢跟读速度", "对比标准发音"]
        })

    return recommendations


def analyze_learning_curve(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    if len(records) < 3:
        return {"curve_type": "insufficient_data", "slope": 0.0}

    sorted_records = sorted(records, key=lambda x: x.get("timestamp", ""))
    score_values = [r.get("pronunciation_score", 0.0) for r in sorted_records]

    n = len(score_values)
    x_mean = sum(range(n)) / n
    y_mean = sum(score_values) / n
    numerator = sum((i - x_mean) * (score_values[i] - y_mean) for i in range(n))
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
    avg_score = sum(r.get("pronunciation_score", 0.0) for r in records) / total
    if total >= 20 and avg_score >= 8.0:
        return "MASTERED"
    elif total >= 10 and avg_score >= 6.0:
        return "FAMILIAR"
    elif total >= 5:
        return "LEARNING"
    return "NOT_STARTED"


def create_session_context(child_profile: Dict[str, Any], records: List[Dict[str, Any]], preferences: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "session_id": str(uuid.uuid4())[:8],
        "child_id": child_profile.get("nickname", "未知孩子"),
        "start_time": datetime.now().isoformat(),
        "current_learning_pinyin": [r.get("pinyin", "") for r in records[-10:] if r.get("pinyin")],
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