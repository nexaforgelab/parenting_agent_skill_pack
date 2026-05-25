"""Planning engine for 小学口算训练 Agent.

提供数据分析、异常检测、个性化推荐和上下文记忆功能。
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
from collections import defaultdict
try:
    from .models import CalculationRecord, ProgressStats, SessionStats, Recommendation, SessionContext
except ImportError:
    from models import CalculationRecord, ProgressStats, SessionStats, Recommendation, SessionContext


SKILL_FLOW = ['设置年级和题型', '自动生成口算题', '限时答题', '自动批改', '统计正确率和速度', '生成薄弱题型']
SAFETY_NOTES = [
    '本 Skill 以启发式陪练为主，避免直接替孩子完成作业或代写成品。',
    '输出应包含引导问题、解题路径、错因分析和复习建议，保留孩子自主思考过程。',
    '涉及教材、地区考试政策或校内要求时，应提示以学校老师最新要求为准。'
]
DEFAULT_DELIVERABLES = ['每日口算卷', '错题统计', '速度曲线']


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


def analyze_training_progress(calculation_records: List[Dict[str, Any]]) -> ProgressStats:
    """分析训练进度"""
    if not calculation_records:
        return ProgressStats()

    correct = sum(1 for r in calculation_records if r.get("is_correct", False))
    total = len(calculation_records)
    total_time = sum(r.get("time_spent", 0) for r in calculation_records)

    operation_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {"correct": 0, "total": 0})
    for record in calculation_records:
        op = record.get("operation_type", "混合运算")
        operation_stats[op]["total"] += 1
        if record.get("is_correct", False):
            operation_stats[op]["correct"] += 1

    weak = [op for op, stats in operation_stats.items() if stats["total"] > 0 and stats["correct"] / stats["total"] < 0.7]
    strong = [op for op, stats in operation_stats.items() if stats["total"] > 0 and stats["correct"] / stats["total"] >= 0.85]

    return ProgressStats(
        total_problems_today=total,
        total_correct_today=correct,
        total_time_today=total_time,
        accuracy_rate=(correct / total * 100) if total > 0 else 0,
        average_speed=(total_time / total) if total > 0 else 0,
        weak_operations=weak,
        strong_operations=strong
    )


def detect_speed_issues(calculation_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """检测速度问题"""
    issues = []

    if not calculation_records:
        return issues

    avg_time = sum(r.get("time_spent", 0) for r in calculation_records) / len(calculation_records)

    if avg_time > 10:
        issues.append({
            "type": "slow_speed",
            "severity": "medium",
            "message": f"平均答题时间 {avg_time:.1f} 秒，速度偏慢",
            "suggestion": "建议增加限时练习，提高反应速度"
        })

    slow_records = [r for r in calculation_records if r.get("time_spent", 0) > avg_time * 1.5]
    if len(slow_records) > len(calculation_records) * 0.3:
        issues.append({
            "type": "inconsistent_speed",
            "severity": "low",
            "message": f"有 {len(slow_records)} 道题答题时间明显偏长",
            "suggestion": "部分题目需要加强练习"
        })

    return issues


def generate_recommendations(progress_stats: ProgressStats, issues: List[Dict[str, Any]]) -> List[Recommendation]:
    """生成个性化推荐"""
    recommendations = []

    if progress_stats.weak_operations:
        recommendations.append(Recommendation(
            recommendation_id="rec_weak_ops",
            category="薄弱运算",
            priority="高",
            title="加强薄弱运算",
            description=f"需要加强练习: {', '.join(progress_stats.weak_operations)}",
            target_operations=progress_stats.weak_operations,
            suggested_duration=20,
            confidence_score=0.9
        ))

    if progress_stats.accuracy_rate < 80:
        recommendations.append(Recommendation(
            recommendation_id="rec_accuracy",
            category="准确率提升",
            priority="高",
            title="提高准确率",
            description=f"当前准确率 {progress_stats.accuracy_rate:.1f}%，需要加强",
            suggested_duration=15,
            confidence_score=0.85
        ))

    if any(issue["type"] == "slow_speed" for issue in issues):
        recommendations.append(Recommendation(
            recommendation_id="rec_speed",
            category="速度训练",
            priority="中",
            title="提升答题速度",
            description="建议使用计时器进行限时训练",
            suggested_duration=10,
            confidence_score=0.8
        ))

    if progress_stats.strong_operations:
        recommendations.append(Recommendation(
            recommendation_id="rec_mastery",
            category="能力提升",
            priority="低",
            title="挑战更高难度",
            description=f"已掌握 {', '.join(progress_stats.strong_operations)}，可以适当提升难度",
            suggested_duration=15,
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
        current_operation=None,
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
