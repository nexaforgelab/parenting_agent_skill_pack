"""Planning engine for 幼儿园择校 Agent.

增强版本：添加数据分析、异常检测、个性化推荐、上下文记忆、数据聚合
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
from collections import defaultdict
try:
    from .models import (
        TrendData, Alert, Recommendation, SessionContext,
        SelectionStatistics, KindergartenInfo, ComparisonResult
    )
except ImportError:
    from models import (
        TrendData, Alert, Recommendation, SessionContext,
        SelectionStatistics, KindergartenInfo, ComparisonResult
    )

SKILL_FLOW = ['收集家庭择校偏好', '收集幼儿园信息', '建立评估维度', '多维度比较分析', '输出择校建议']
SAFETY_NOTES = ['本 Skill 提供家庭教育和生活管理建议，不替代专业人士意见。', '涉及安全、法律、医疗、财务或教育政策时，应提示家长二次核验。', '输出应尊重家庭差异，不用单一标准评价孩子或父母。']
DEFAULT_DELIVERABLES = ['择校对比表', '评估报告', '实地考察清单']

_context_store: Dict[str, SessionContext] = {}


def get_or_create_context(session_id: str) -> SessionContext:
    """获取或创建会话上下文"""
    if session_id not in _context_store:
        _context_store[session_id] = SessionContext(session_id=session_id)
    return _context_store[session_id]


def update_context(session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
    """更新会话上下文"""
    context = get_or_create_context(session_id)
    context.add_interaction(role, content, metadata)


def compare_kindergartens(
    kindergartens: List[Dict[str, Any]],
    preferences: Dict[str, Any]
) -> List[ComparisonResult]:
    """比较幼儿园"""
    results = []

    if not kindergartens:
        return results

    for kg in kindergartens:
        result = ComparisonResult(
            kindergarten_id=kg.get("kindergarten_id", ""),
            kindergarten_name=kg.get("name", "未知"),
            overall_score=float(kg.get("rating", 0) or 0) * 20,
            pros=[],
            cons=[]
        )

        tuition = float(kg.get("tuition_per_year", 0) or 0)
        if tuition > 0:
            if tuition < 50000:
                result.pros.append("学费相对较低")
            else:
                result.cons.append("学费较高")

        rating = float(kg.get("rating", 0) or 0)
        if rating >= 4.5:
            result.pros.append("口碑良好")
        elif rating < 3.5:
            result.cons.append("口碑一般")

        distance = float(kg.get("distance_from_home", 0) or 0)
        if distance < 3:
            result.pros.append("距离近，接送方便")
        elif distance > 10:
            result.cons.append("距离较远")

        teacher_ratio = float(kg.get("teacher_student_ratio", 0) or 0)
        if teacher_ratio > 0 and teacher_ratio <= 0.1:
            result.pros.append("师生比较高")

        result.match_percentage = len(result.pros) / max(len(result.pros) + len(result.cons), 1) * 100
        results.append(result)

    results.sort(key=lambda x: x.overall_score, reverse=True)
    return results


def detect_selection_anomalies(
    kindergartens: List[Dict[str, Any]],
    comparisons: List[ComparisonResult]
) -> List[Alert]:
    """检测择校异常情况"""
    alerts = []

    if not kindergartens:
        return alerts

    tuition_list = [float(kg.get("tuition_per_year", 0) or 0) for kg in kindergartens if float(kg.get("tuition_per_year", 0) or 0) > 0]
    if tuition_list:
        avg_tuition = sum(tuition_list) / len(tuition_list)
        high_tuition_count = sum(1 for t in tuition_list if t > avg_tuition * 1.5)
        if high_tuition_count > len(tuition_list) * 0.3:
            alerts.append(Alert(
                alert_type="学费偏高",
                severity="warning",
                message="部分幼儿园学费明显高于平均水平",
                recommendation="建议综合考虑性价比，不一定最贵的就是最好的"
            ))

    ratings = [float(kg.get("rating", 0) or 0) for kg in kindergartens if float(kg.get("rating", 0) or 0) > 0]
    if ratings:
        low_rating_count = sum(1 for r in ratings if r < 3.5)
        if low_rating_count > len(ratings) * 0.4:
            alerts.append(Alert(
                alert_type="口碑参差",
                severity="info",
                message="所选幼儿园中口碑差异较大",
                recommendation="建议实地考察后再做决定"
            ))

    return alerts


def generate_selection_recommendations(
    kindergartens: List[Dict[str, Any]],
    comparisons: List[ComparisonResult],
    child_profile: Dict[str, Any],
    alerts: List[Alert]
) -> List[Recommendation]:
    """生成择校推荐"""
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

    if age < 2:
        recommendations.append(Recommendation(
            category="择校时机",
            priority=1,
            title="关注托班资源",
            description=f"孩子目前{age}岁，可能需要选择有托班的幼儿园",
            action_items=[
                "了解各幼儿园是否开设托班",
                "关注托班的师生配比",
                "考虑托班的环境和师资"
            ],
            rationale="低龄段孩子需要更多照顾",
            expected_outcome="找到适合低龄段的幼儿园"
        ))

    if comparisons:
        top_match = max(comparisons, key=lambda x: x.match_percentage)
        recommendations.append(Recommendation(
            category="首要推荐",
            priority=1,
            title=f"推荐 {top_match.kindergarten_name}",
            description=f"该园与您的需求匹配度最高（{top_match.match_percentage:.0f}%）",
            action_items=[
                "预约实地考察",
                "了解具体课程设置",
                "咨询入园流程"
            ],
            rationale="综合评分最高",
            expected_outcome="确定首选幼儿园"
        ))

    recommendations.append(Recommendation(
        category="择校建议",
        priority=2,
        title="多维度综合评估",
        description="建议从多个维度综合考虑，不只看某一个因素",
        action_items=[
            "实地考察目标幼儿园",
            "与在园家长交流",
            "了解真实的日常教学"
        ],
        rationale="全面了解才能做出最优选择",
        expected_outcome="做出明智的择校决定"
    ))

    return recommendations


def aggregate_selection_statistics(
    kindergartens: List[Dict[str, Any]],
    comparisons: List[ComparisonResult]
) -> Optional[SelectionStatistics]:
    """聚合择校统计数据"""
    if not kindergartens:
        return None

    stats = SelectionStatistics()
    stats.total_kindergartens = len(kindergartens)
    stats.evaluated_count = len(comparisons)

    tuition_list = [float(kg.get("tuition_per_year", 0) or 0) for kg in kindergartens if float(kg.get("tuition_per_year", 0) or 0) > 0]
    if tuition_list:
        stats.budget_range = {
            "min": min(tuition_list),
            "max": max(tuition_list),
            "average": sum(tuition_list) / len(tuition_list)
        }

    distance_list = [float(kg.get("distance_from_home", 0) or 0) for kg in kindergartens if float(kg.get("distance_from_home", 0) or 0) > 0]
    if distance_list:
        stats.distance_range = {
            "min": min(distance_list),
            "max": max(distance_list),
            "average": sum(distance_list) / len(distance_list)
        }

    if comparisons:
        scores = [c.overall_score for c in comparisons]
        stats.average_overall_score = sum(scores) / len(scores)
        top = max(comparisons, key=lambda x: x.overall_score)
        stats.top_ranked = top.kindergarten_name

    return stats


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

    kindergartens = payload.get("kindergartens") or []
    facts.append(f"已收到 {len(kindergartens)} 所幼儿园的信息。")

    if kindergartens:
        comparisons = compare_kindergartens(kindergartens, payload.get("preferences", {}))
        if comparisons:
            top = comparisons[0]
            facts.append(f"评分最高：{top.kindergarten_name}（{top.overall_score:.1f}分）")

    return facts


def build_analysis(payload: Dict[str, Any]) -> List[str]:
    """构建分析内容"""
    problem = payload.get("current_problem", "")
    kindergartens = payload.get("kindergartens") or []
    child_profile = payload.get("child_profile", {})
    preferences = payload.get("preferences", {})

    analysis = [
        f"当前问题聚焦：{problem}",
        "建议从多个维度综合评估幼儿园：教学质量、环境设施、距离、学费等。",
        "本 Skill 会优先输出可执行动作、评估维度和复盘指标。",
    ]

    for step in SKILL_FLOW:
        analysis.append(f"链路节点：{step}")

    if kindergartens:
        comparisons = compare_kindergartens(kindergartens, preferences)
        alerts = detect_selection_anomalies(kindergartens, comparisons)
        stats = aggregate_selection_statistics(kindergartens, comparisons)

        if alerts:
            analysis.append("")
            analysis.append("⚠️ 检测到的异常：")
            for alert in alerts:
                analysis.append(f"  - [{alert.severity}] {alert.message}")

        recommendations = generate_selection_recommendations(kindergartens, comparisons, child_profile, alerts)
        if recommendations:
            analysis.append("")
            analysis.append("📋 个性化建议：")
            for rec in recommendations[:3]:
                analysis.append(f"  - {rec.title}：{rec.description}")

        if stats:
            analysis.append("")
            analysis.append("📊 择校统计：")
            analysis.append(f"  - 幼儿园总数：{stats.total_kindergartens}")
            analysis.append(f"  - 平均评分：{stats.average_overall_score:.1f}")
            if stats.budget_range:
                analysis.append(f"  - 学费范围：{stats.budget_range['min']:.0f}-{stats.budget_range['max']:.0f}元/年")

    return analysis


def build_action_plan(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """构建行动计划"""
    base_tasks = [
        "补齐孩子画像和家庭限制条件",
        "收集目标幼儿园的详细信息",
        "实地考察候选幼儿园",
        "与在园家长交流获取真实评价",
        "综合评估后确定首选",
    ]

    kindergartens = payload.get("kindergartens") or []
    if kindergartens:
        base_tasks.insert(0, f"对比分析 {len(kindergartens)} 所幼儿园")

    plan: List[Dict[str, str]] = []
    for i, task in enumerate(base_tasks, start=1):
        plan.append({
            "day": f"D{i}",
            "task": task,
            "owner": "家长",
            "evidence_to_record": "考察结果、对比评分、决策依据",
            "difficulty": "中"
        })
    return plan


def build_deliverables(payload: Dict[str, Any]) -> Dict[str, Any]:
    """构建交付物"""
    deliverables = {
        "required": DEFAULT_DELIVERABLES,
        "tables": {
            "comparison": ["幼儿园", "类型", "学费", "评分", "距离", "综合得分", "优缺点"],
            "evaluation": ["评估维度", "权重", "A园得分", "B园得分", "C园得分"]
        },
        "templates": {
            "site_visit_checklist": "园区环境、教学设施、师资力量、安全措施、课程设置、收费明细",
            "parent_feedback_template": "孩子在园表现、老师评价、与同龄人相处、饮食睡眠情况"
        }
    }

    return deliverables


def next_fields() -> List[str]:
    """获取下次追踪字段"""
    return [
        "实地考察结果",
        "在园家长反馈",
        "最终择校决定",
        "入园申请进度",
        "入园准备情况"
    ]


def generate_session_summary(session_id: str) -> Optional[Dict[str, Any]]:
    """生成会话摘要"""
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
    """清除会话上下文"""
    if session_id in _context_store:
        del _context_store[session_id]
        return True
    return False
