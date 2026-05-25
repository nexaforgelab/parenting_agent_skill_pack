"""Planning engine for 小学数学应用题 Agent.

提供数据分析、异常检测、个性化推荐和上下文记忆功能。
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
try:
    from .models import (
        ProblemRecord, ProgressStats, ConceptMastery,
        Recommendation, SessionContext
    )
except ImportError:
    from models import (
        ProblemRecord, ProgressStats, ConceptMastery,
        Recommendation, SessionContext
    )

SKILL_FLOW = ['拍照识别题目', '提取已知条件和问题', '画数量关系', '分步引导孩子思考', '生成同类题']
SAFETY_NOTES = [
    '本 Skill 以启发式陪练为主，避免直接替孩子完成作业或代写成品。',
    '输出应包含引导问题、解题路径、错因分析和复习建议，保留孩子自主思考过程。',
    '涉及教材、地区考试政策或校内要求时，应提示以学校老师最新要求为准。'
]
DEFAULT_DELIVERABLES = ['解题步骤', '数量关系图', '变式题']


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
    records = payload.get("raw_records") or []
    facts.append(f"已收到 {len(records)} 条原始记录。")
    return facts


def build_analysis(payload: Dict[str, Any]) -> List[str]:
    """构建分析内容"""
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
    """构建交付物定义"""
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


def analyze_problem_solving(problem_records: List[Dict[str, Any]]) -> ProgressStats:
    """分析解题表现

    Args:
        problem_records: 应用题记录列表

    Returns:
        学习进度统计对象
    """
    if not problem_records:
        return ProgressStats()

    solved = sum(1 for r in problem_records if r.get("status") == "已解答")
    correct = sum(1 for r in problem_records if r.get("is_correct", False))
    total_time = sum(r.get("time_spent", 0) for r in problem_records)
    total_hints = sum(r.get("hints_used", 0) for r in problem_records)

    concept_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {"total": 0, "correct": 0})
    for record in problem_records:
        for concept in record.get("related_concepts", []):
            concept_stats[concept]["total"] += 1
            if record.get("is_correct", False):
                concept_stats[concept]["correct"] += 1

    mastered = [c for c, stats in concept_stats.items() if stats["total"] > 0 and stats["correct"] / stats["total"] >= 0.8]
    needing_work = [c for c, stats in concept_stats.items() if stats["total"] > 0 and stats["correct"] / stats["total"] < 0.7]

    improvement = calculate_weekly_improvement(problem_records)

    return ProgressStats(
        total_problems=len(problem_records),
        solved_count=solved,
        correct_count=correct,
        average_time=total_time / len(problem_records) if problem_records else 0,
        hints_used=total_hints,
        concepts_mastered=mastered,
        concepts_needing_work=needing_work,
        weekly_improvement=improvement
    )


def calculate_weekly_improvement(problem_records: List[Dict[str, Any]]) -> float:
    """计算本周进步幅度"""
    if len(problem_records) < 2:
        return 0.0

    sorted_records = sorted(problem_records, key=lambda x: x.get("created_at", ""))
    half = len(sorted_records) // 2

    recent = sorted_records[half:]
    older = sorted_records[:half]

    if not recent or not older:
        return 0.0

    recent_rate = sum(1 for r in recent if r.get("is_correct", False)) / len(recent) * 100
    older_rate = sum(1 for r in older if r.get("is_correct", False)) / len(older) * 100

    if older_rate == 0:
        return 100.0 if recent_rate > 0 else 0.0

    return ((recent_rate - older_rate) / older_rate) * 100


def detect_problem_patterns(problem_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """检测解题模式和问题"""
    patterns = []

    if not problem_records:
        return patterns

    for record in problem_records:
        subject = record.get("subject", "数学")

        if record.get("hints_used", 0) > 2:
            patterns.append({
                "type": "hint_dependency",
                "severity": "medium",
                "subject": subject,
                "message": f"使用了 {record.get('hints_used')} 次提示才完成",
                "suggestion": "可能对相关概念理解不深，建议加强基础知识"
            })

        if record.get("time_spent", 0) > 20:
            patterns.append({
                "type": "slow_solution",
                "severity": "low",
                "subject": subject,
                "message": f"解题用时 {record.get('time_spent')} 分钟，超出平均水平",
                "suggestion": "需要提高解题速度，可通过练习提升"
            })

        if not record.get("is_correct", False):
            patterns.append({
                "type": "incorrect",
                "severity": "high",
                "subject": subject,
                "message": f"解答错误: {record.get('content', '')[:30]}...",
                "suggestion": "分析错误原因，理解解题思路"
            })

    return patterns


def analyze_concept_mastery(problem_records: List[Dict[str, Any]]) -> List[ConceptMastery]:
    """分析概念掌握度"""
    concept_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        "practice_count": 0,
        "correct_count": 0
    })

    for record in problem_records:
        for concept in record.get("related_concepts", []):
            concept_stats[concept]["practice_count"] += 1
            if record.get("is_correct", False):
                concept_stats[concept]["correct_count"] += 1

    result = []
    for concept_id, stats in concept_stats.items():
        mastery_level = stats["correct_count"] / stats["practice_count"] if stats["practice_count"] > 0 else 0
        result.append(ConceptMastery(
            concept_id=concept_id,
            concept_name=concept_id,
            mastery_level=mastery_level,
            practice_count=stats["practice_count"],
            correct_count=stats["correct_count"]
        ))

    return result


def generate_recommendations(
    progress_stats: ProgressStats,
    patterns: List[Dict[str, Any]],
    concept_mastery: List[ConceptMastery]
) -> List[Recommendation]:
    """生成个性化推荐"""
    recommendations = []

    weak_concepts = [c for c in concept_mastery if c.mastery_level < 0.7]
    if weak_concepts:
        recommendations.append(Recommendation(
            recommendation_id="rec_weak_concepts",
            category="概念巩固",
            priority="高",
            title="加强薄弱概念",
            description=f"发现 {len(weak_concepts)} 个概念掌握不足",
            target_concepts=[c.concept_id for c in weak_concepts],
            suggested_duration=30,
            confidence_score=0.85
        ))

    high_hint_usage = [p for p in patterns if p["type"] == "hint_dependency"]
    if len(high_hint_usage) > 2:
        recommendations.append(Recommendation(
            recommendation_id="rec_independence",
            category="独立性培养",
            priority="中",
            title="减少提示依赖",
            description="解题过于依赖提示，建议尝试独立思考",
            suggested_duration=20,
            confidence_score=0.8
        ))

    incorrect_problems = [p for p in patterns if p["type"] == "incorrect"]
    if incorrect_problems:
        recommendations.append(Recommendation(
            recommendation_id="rec_error_analysis",
            category="错题分析",
            priority="高",
            title="分析错误原因",
            description=f"有 {len(incorrect_problems)} 道题解答错误，需要深入分析",
            suggested_duration=25,
            confidence_score=0.9
        ))

    if progress_stats.concepts_mastered:
        recommendations.append(Recommendation(
            recommendation_id="rec_advancement",
            category="能力提升",
            priority="低",
            title="挑战更高难度",
            description=f"已掌握 {', '.join(progress_stats.concepts_mastered[:2])}，可以挑战更难题目",
            suggested_duration=20,
            difficulty_adjustment="提高难度",
            confidence_score=0.75
        ))

    return recommendations


def create_session_context(payload: Dict[str, Any], session_id: str) -> SessionContext:
    """创建会话上下文"""
    child_profile = payload.get("child_profile", {})

    return SessionContext(
        session_id=session_id,
        start_time=datetime.now().isoformat(),
        child_id=child_profile.get("name", "未知"),
        grade_level=child_profile.get("grade", 1),
        current_concept=None,
        conversation_history=[],
        recent_performance=payload.get("raw_records", []),
        user_preferences=payload.get("preferences", {})
    )


def update_session_context(
    context: SessionContext,
    role: str,
    content: str,
    performance_data: Optional[Dict[str, Any]] = None
) -> None:
    """更新会话上下文"""
    context.add_interaction(role, content)

    if performance_data:
        context.recent_performance.append(performance_data)
        if len(context.recent_performance) > 20:
            context.recent_performance = context.recent_performance[-20:]
