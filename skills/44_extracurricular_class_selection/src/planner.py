"""Planning engine for 兴趣班选择 Agent.

增强版本：添加数据分析、异常检测、个性化推荐、上下文记忆、数据聚合
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
from collections import defaultdict
try:
    from .models import TrendData, Alert, Recommendation, SessionContext
except ImportError:
    from models import TrendData, Alert, Recommendation, SessionContext

SKILL_FLOW = ['收集孩子兴趣信息', '收集兴趣班信息', '匹配孩子特点与兴趣班', '综合评估推荐', '输出选择建议']
SAFETY_NOTES = ['本 Skill 提供家庭教育和生活管理建议，不替代专业人士意见。', '涉及安全、法律、医疗、财务或教育政策时，应提示家长二次核验。', '输出应尊重家庭差异，不用单一标准评价孩子或父母。']
DEFAULT_DELIVERABLES = ['兴趣班对比表', '选择建议报告', '试课评估清单']

_context_store: Dict[str, SessionContext] = {}


def get_or_create_context(session_id: str) -> SessionContext:
    """获取或创建会话上下文"""
    if session_id not in _context_store:
        _context_store[session_id] = SessionContext(session_id=session_id)
    return _context_store[session_id]


def compare_classes(
    classes: List[Dict[str, Any]],
    preferences: Dict[str, Any],
    child_profile: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """比较兴趣班"""
    results = []

    if not classes:
        return results

    child_interests = child_profile.get("interests", [])
    child_personality = child_profile.get("personality", "")

    for cls in classes:
        result = {
            "class_id": cls.get("class_id", ""),
            "class_name": cls.get("name", "未知"),
            "overall_score": 0,
            "pros": [],
            "cons": [],
            "match_score": 0
        }

        tuition = float(cls.get("tuition_per_month", 0) or 0)
        if tuition > 0 and tuition < 3000:
            result["pros"].append("学费相对较低")
        elif tuition > 8000:
            result["cons"].append("学费较高")

        class_interests = cls.get("related_interests", [])
        if class_interests and child_interests:
            match_count = sum(1 for interest in class_interests if interest in child_interests)
            result["match_score"] = (match_count / len(class_interests)) * 100 if class_interests else 0
            if match_count > 0:
                result["pros"].append(f"与孩子兴趣匹配（{match_count}项）")

        hours = float(cls.get("hours_per_week", 0) or 0)
        if hours > 0 and hours <= 3:
            result["pros"].append("时间安排合理")
        elif hours > 5:
            result["cons"].append("课时较多，可能增加孩子负担")

        rating = float(cls.get("rating", 0) or 0)
        if rating >= 4.5:
            result["pros"].append("口碑良好")
        elif rating < 3.5:
            result["cons"].append("口碑一般")

        result["overall_score"] = rating * 20 + result["match_score"] * 0.1
        results.append(result)

    results.sort(key=lambda x: x["overall_score"], reverse=True)
    return results


def detect_class_anomalies(
    classes: List[Dict[str, Any]],
    comparisons: List[Dict[str, Any]]
) -> List[Alert]:
    """检测兴趣班异常情况"""
    alerts = []

    if not classes:
        return alerts

    total_hours = sum(float(cls.get("hours_per_week", 0) or 0) for cls in classes)
    if total_hours > 10:
        alerts.append(Alert(
            alert_type="课时过多",
            severity="warning",
            message=f"兴趣班总课时每周{total_hours}小时，可能给孩子造成过大压力",
            recommendation="建议精简兴趣班数量，确保孩子有足够休息和自由玩耍时间"
        ))

    total_tuition = sum(float(cls.get("tuition_per_month", 0) or 0) for cls in classes)
    if total_tuition > 15000:
        alerts.append(Alert(
            alert_type="学费偏高",
            severity="warning",
            message=f"兴趣班每月总学费约{total_tuition}元，支出较大",
            recommendation="建议综合考虑性价比，优先选择孩子最感兴趣的几项"
        ))

    return alerts


def generate_class_recommendations(
    classes: List[Dict[str, Any]],
    comparisons: List[Dict[str, Any]],
    child_profile: Dict[str, Any],
    alerts: List[Alert]
) -> List[Recommendation]:
    """生成兴趣班推荐"""
    recommendations = []

    # 安全处理 age 字段，支持字符串和数值类型
    age = child_profile.get("age", 0)
    if age is not None:
        if isinstance(age, str):
            import re
            match = re.match(r'^(\d+\.?\d*)', str(age))
            if match:
                age = float(match.group(1))
            else:
                age = 0
        try:
            age = float(age)
        except (ValueError, TypeError):
            age = 0

    if age < 5:
        recommendations.append(Recommendation(
            category="年龄建议",
            priority=1,
            title="适合低龄段",
            description=f"孩子目前{age}岁，建议选择以游戏和体验为主的兴趣班",
            action_items=[
                "优先选择培养兴趣和好奇心的课程",
                "避免过早强调技能训练",
                "关注课程的游戏性和互动性"
            ],
            rationale="低龄段应以培养兴趣为主",
            expected_outcome="找到适合孩子年龄特点的兴趣班"
        ))

    if comparisons:
        top_match = max(comparisons, key=lambda x: x.get("match_score", 0))
        recommendations.append(Recommendation(
            category="首要推荐",
            priority=1,
            title=f"推荐 {top_match['class_name']}",
            description=f"该课程与孩子兴趣匹配度最高（{top_match.get('match_score', 0):.0f}%）",
            action_items=[
                "预约试课体验",
                "观察孩子上课表现",
                "与其他家长交流"
            ],
            rationale="综合评分和兴趣匹配度最高",
            expected_outcome="确定首选兴趣班"
        ))

    recommendations.append(Recommendation(
        category="选择建议",
        priority=2,
        title="精选2-3个兴趣班",
        description="建议选择2-3个孩子真正感兴趣的，避免贪多",
        action_items=[
            "根据孩子意愿选择",
            "考虑家庭经济承受能力",
            "确保孩子有足够自由时间"
        ],
        rationale="兴趣班不在多，而在精",
        expected_outcome="做出明智的兴趣班选择"
    ))

    return recommendations


def build_known_facts(payload: Dict[str, Any]) -> List[str]:
    """构建已知事实列表"""
    facts: List[str] = []
    child = payload.get("child_profile", {})
    family = payload.get("family_context", {})

    if child:
        facts.append(f"孩子画像：{child}")
    if family:
        facts.append(f"家庭上下文：{family}")
    if payload.get("goal"):
        facts.append(f"目标：{payload.get('goal')}")

    classes = payload.get("classes") or []
    facts.append(f"已收到 {len(classes)} 个兴趣班的信息。")

    return facts


def build_analysis(payload: Dict[str, Any]) -> List[str]:
    """构建分析内容"""
    problem = payload.get("current_problem", "")
    classes = payload.get("classes") or []
    child_profile = payload.get("child_profile", {})
    preferences = payload.get("preferences", {})

    analysis = [
        f"当前问题聚焦：{problem}",
        "建议根据孩子的兴趣和特点选择适合的兴趣班。",
        "本 Skill 会优先输出可执行动作、评估维度和复盘指标。",
    ]

    for step in SKILL_FLOW:
        analysis.append(f"链路节点：{step}")

    if classes:
        comparisons = compare_classes(classes, preferences, child_profile)
        alerts = detect_class_anomalies(classes, comparisons)

        if alerts:
            analysis.append("")
            analysis.append("⚠️ 检测到的异常：")
            for alert in alerts:
                analysis.append(f"  - [{alert.severity}] {alert.message}")

        recommendations = generate_class_recommendations(classes, comparisons, child_profile, alerts)
        if recommendations:
            analysis.append("")
            analysis.append("📋 个性化建议：")
            for rec in recommendations[:3]:
                analysis.append(f"  - {rec.title}：{rec.description}")

    return analysis


def build_action_plan(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """构建行动计划"""
    base_tasks = [
        "补齐孩子画像和家庭限制条件",
        "收集目标兴趣班的详细信息",
        "预约试课体验",
        "观察孩子上课表现",
        "综合评估后确定选择",
    ]

    classes = payload.get("classes") or []
    if classes:
        base_tasks.insert(0, f"对比分析 {len(classes)} 个兴趣班")

    plan: List[Dict[str, str]] = []
    for i, task in enumerate(base_tasks, start=1):
        plan.append({
            "day": f"D{i}",
            "task": task,
            "owner": "家长",
            "evidence_to_record": "试课反馈、孩子意愿、评估结果",
            "difficulty": "中"
        })
    return plan


def build_deliverables(payload: Dict[str, Any]) -> Dict[str, Any]:
    """构建交付物"""
    deliverables = {
        "required": DEFAULT_DELIVERABLES,
        "tables": {
            "comparison": ["兴趣班", "类型", "学费/月", "课时/周", "评分", "匹配度", "优缺点"],
            "evaluation": ["评估维度", "权重", "A班得分", "B班得分", "C班得分"]
        },
        "templates": {
            "trial_feedback": "孩子是否喜欢？老师教学如何？环境设施怎么样？与其他孩子相处如何？",
            "selection_checklist": "孩子兴趣、经济承受能力、时间安排、地理位置、师资力量"
        }
    }

    return deliverables


def next_fields() -> List[str]:
    """获取下次追踪字段"""
    return [
        "试课反馈",
        "孩子意愿表达",
        "最终选择决定",
        "课程报名进度",
        "学习效果跟踪"
    ]


def clear_context(session_id: str) -> bool:
    """清除会话上下文"""
    if session_id in _context_store:
        del _context_store[session_id]
        return True
    return False
