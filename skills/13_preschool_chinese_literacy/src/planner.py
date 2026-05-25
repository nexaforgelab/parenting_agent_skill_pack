"""Planning engine for 幼儿识字启蒙 Agent."""
from typing import Any, Dict, List
from datetime import datetime
from collections import defaultdict
import uuid

SKILL_FLOW = ['设定识字目标', '每天推送 5 个字', '结合图片、故事、生活场景', '生成小游戏', '定期复习']
SAFETY_NOTES = ['本 Skill 提供家庭教育和生活管理建议，不替代专业人士意见。', '涉及安全、法律、医疗、财务或教育政策时，应提示家长二次核验。', '输出应尊重家庭差异，不用单一标准评价孩子或父母。']
DEFAULT_DELIVERABLES = ['每日识字卡', '复习计划', '掌握度报告', '个性化建议']


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
        "每天学习 5 个新汉字",
        "使用图片和故事辅助记忆",
        "进行认读和书写练习",
        "一周后复习已学汉字",
    ]
    plan: List[Dict[str, str]] = []
    for i, task in enumerate(base_tasks, start=1):
        plan.append({
            "day": f"D{i}",
            "task": task,
            "owner": "家长/主要照护人",
            "evidence_to_record": "学习的汉字、正确率、孩子反应",
            "difficulty": "低" if i <= 3 else "中"
        })
    return plan


def build_deliverables(payload: Dict[str, Any]) -> Dict[str, Any]:
    """构建交付物清单"""
    return {
        "required": DEFAULT_DELIVERABLES,
        "tables": {
            "daily_learning": ["日期", "新字", "拼音", "正确率", "备注"],
            "weekly_review": ["汉字", "拼音", "正确次数", "错误次数", "掌握程度"]
        }
    }


def next_fields() -> List[str]:
    """获取下次追踪字段列表"""
    return ["孩子年龄", "今天学习的汉字", "正确率", "孩子反应", "需要复习的汉字"]


def analyze_learning_progress(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析识字学习进度"""
    if not records:
        return {"total_characters": 0, "mastered_characters": 0, "average_accuracy": 0.0}

    total_chars = len(set(r.get("character", "") for r in records if r.get("character")))
    total_practice = sum(r.get("practice_count", 0) for r in records)
    total_correct = sum(r.get("correct_count", 0) for r in records)
    accuracy = (total_correct / total_practice * 100) if total_practice > 0 else 0.0

    mastered = sum(1 for r in records if r.get("correct_count", 0) >= 5)

    difficult = [r.get("character", "") for r in records if r.get("correct_count", 0) < 2]

    return {
        "total_characters": total_chars,
        "mastered_characters": mastered,
        "learning_characters": total_chars - mastered,
        "total_practice": total_practice,
        "average_accuracy": round(accuracy, 2),
        "difficult_characters": difficult[:10],
        "summary": f"共学习 {total_chars} 个汉字，掌握 {mastered} 个"
    }


def detect_learning_difficulties(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """检测学习困难"""
    difficulties = []
    if len(records) < 3:
        return difficulties

    recent = records[-5:]
    avg_accuracy = sum(r.get("correct_count", 0) / max(r.get("practice_count", 1), 1) for r in recent) / len(recent)

    if avg_accuracy < 0.5:
        difficulties.append({
            "type": "low_accuracy",
            "severity": "high",
            "message": "正确率偏低，需要调整学习方法",
            "suggestion": "减少每日新字数量，加强复习"
        })

    return difficulties


def generate_personalized_recommendations(child_profile: Dict[str, Any], records: List[Dict[str, Any]], progress: Dict[str, Any]) -> List[Dict[str, Any]]:
    """生成个性化推荐"""
    recommendations = []
    age = child_profile.get("age", "未知")
    if "岁" in str(age):
        age_num = int(age.split("岁")[0]) if age.split("岁")[0].isdigit() else 4
    else:
        age_num = 4

    daily_chars = min(3 + age_num // 2, 8)

    recommendations.append({
        "recommendation_id": str(uuid.uuid4())[:8],
        "category": "learning_plan",
        "priority": "high",
        "title": "调整每日学习量",
        "description": f"针对 {age} 孩子，建议每天学习 {daily_chars} 个新字",
        "action_items": [f"每天固定时间学习 {daily_chars} 个字", "使用图片辅助记忆", "配合小游戏增加趣味"]
    })

    difficult = progress.get("difficult_characters", [])
    if difficult:
        recommendations.append({
            "recommendation_id": str(uuid.uuid4())[:8],
            "category": "review",
            "priority": "medium",
            "title": "加强困难字复习",
            "description": f"以下汉字需要加强练习: {', '.join(difficult[:5])}",
            "action_items": ["每天复习困难字", "使用多种方式练习", "关联词汇加强记忆"]
        })

    return recommendations


def analyze_learning_curve(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析学习曲线"""
    if len(records) < 3:
        return {"curve_type": "insufficient_data", "slope": 0.0}

    sorted_records = sorted(records, key=lambda x: x.get("timestamp", ""))
    accuracy_values = [r.get("correct_count", 0) / max(r.get("practice_count", 1), 1) for r in sorted_records]

    n = len(accuracy_values)
    x_mean = sum(range(n)) / n
    y_mean = sum(accuracy_values) / n
    numerator = sum((i - x_mean) * (accuracy_values[i] - y_mean) for i in range(n))
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
    """计算掌握程度"""
    if not records:
        return "NOT_STARTED"
    total = len(records)
    avg_correct = sum(r.get("correct_count", 0) for r in records) / total
    if total >= 20 and avg_correct >= 5:
        return "MASTERED"
    elif total >= 10 and avg_correct >= 3:
        return "FAMILIAR"
    elif total >= 5:
        return "LEARNING"
    return "NOT_STARTED"


def create_session_context(child_profile: Dict[str, Any], records: List[Dict[str, Any]], preferences: Dict[str, Any]) -> Dict[str, Any]:
    """创建会话上下文"""
    return {
        "session_id": str(uuid.uuid4())[:8],
        "child_id": child_profile.get("nickname", "未知孩子"),
        "start_time": datetime.now().isoformat(),
        "current_learning_chars": [r.get("character", "") for r in records[-10:] if r.get("character")],
        "conversation_history": [],
        "preferences": preferences
    }


def run_full_analysis(payload: Dict[str, Any]) -> Dict[str, Any]:
    """运行完整分析"""
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