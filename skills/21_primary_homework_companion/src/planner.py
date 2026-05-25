"""Planning engine for 小学作业陪伴 Agent.

提供学习数据分析、异常检测、个性化推荐和上下文记忆功能。
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta


SKILL_FLOW = ['输入今天作业清单', '估算完成时间', '安排顺序', '专注计时', '中途提醒休息', '完成后总结表现']
SAFETY_NOTES = [
    '本 Skill 提供家庭教育和生活管理建议，不替代专业人士意见。',
    '涉及安全、法律、医疗、财务或教育政策时，应提示家长二次核验。',
    '输出应尊重家庭差异，不用单一标准评价孩子或父母。'
]
DEFAULT_DELIVERABLES = ['作业时间表', '完成记录', '拖延分析']


def _import_models():
    """动态导入models模块,避免sys.path冲突"""
    import sys
    from pathlib import Path
    src_dir = str(Path(__file__).parent)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    from models import (
        SessionContext, ProgressStats, KnowledgePoint,
        MistakeRecord, Recommendation, HomeworkRecord
    )
    return SessionContext, ProgressStats, KnowledgePoint, MistakeRecord, Recommendation, HomeworkRecord


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


def analyze_learning_progress(homework_records: List[Dict[str, Any]]) -> "ProgressStats":
    """分析学习进度"""
    SessionContext, ProgressStats, KnowledgePoint, MistakeRecord, Recommendation, HomeworkRecord = _import_models()

    if not homework_records:
        return ProgressStats()

    completed = sum(1 for r in homework_records if r.get("status") == "已完成")
    total_duration = sum(r.get("duration_minutes", 0) for r in homework_records)
    total_completion = sum(r.get("completion_rate", 0) for r in homework_records)
    total_distractions = sum(len(r.get("distractions", [])) for r in homework_records)

    subject_stats: Dict[str, Dict[str, int]] = {}
    for record in homework_records:
        subject = record.get("subject", "未知")
        if subject not in subject_stats:
            subject_stats[subject] = {"total": 0, "completed": 0}
        subject_stats[subject]["total"] += 1
        if record.get("status") == "已完成":
            subject_stats[subject]["completed"] += 1

    mastered = [s for s, stats in subject_stats.items() if stats["completed"] == stats["total"]]
    needing_work = [s for s, stats in subject_stats.items() if stats["completed"] < stats["total"]]

    motivation = calculate_motivation_score(homework_records)
    improvement = calculate_weekly_improvement(homework_records)

    return ProgressStats(
        total_homework_count=len(homework_records),
        completed_count=completed,
        average_duration=total_duration / len(homework_records) if homework_records else 0,
        average_completion_rate=total_completion / len(homework_records) if homework_records else 0,
        total_distraction_events=total_distractions,
        subjects_mastered=mastered,
        subjects_needing_work=needing_work,
        weekly_improvement=improvement,
        motivation_score=motivation
    )


def calculate_motivation_score(homework_records: List[Dict[str, Any]]) -> float:
    """计算学习动机分数"""
    if not homework_records:
        return 50.0

    score = 100.0
    completed_rate = sum(1 for r in homework_records if r.get("status") == "已完成") / len(homework_records)
    score *= completed_rate
    avg_duration = sum(r.get("duration_minutes", 0) for r in homework_records) / len(homework_records)
    if avg_duration > 60:
        score *= 0.8
    avg_help_requests = sum(r.get("help_requests", 0) for r in homework_records) / len(homework_records)
    if avg_help_requests > 5:
        score *= 0.9

    return max(0, min(100, score))


def calculate_weekly_improvement(homework_records: List[Dict[str, Any]]) -> float:
    """计算本周进步幅度"""
    if len(homework_records) < 2:
        return 0.0

    sorted_records = sorted(homework_records, key=lambda x: x.get("timestamp", ""), reverse=True)
    recent = sorted_records[:len(sorted_records)//2]
    older = sorted_records[len(sorted_records)//2:]

    if not recent or not older:
        return 0.0

    recent_completion = sum(r.get("completion_rate", 0) for r in recent) / len(recent)
    older_completion = sum(r.get("completion_rate", 0) for r in older) / len(older)

    if older_completion == 0:
        return 100.0 if recent_completion > 0 else 0.0

    return ((recent_completion - older_completion) / older_completion) * 100


def detect_learning_anomalies(homework_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """检测学习异常"""
    anomalies = []

    if not homework_records:
        return anomalies

    duration_stats = [r.get("duration_minutes", 0) for r in homework_records]
    avg_duration = sum(duration_stats) / len(duration_stats) if duration_stats else 0

    for record in homework_records:
        subject = record.get("subject", "未知")
        duration = record.get("duration_minutes", 0)

        if duration > avg_duration * 1.5:
            anomalies.append({
                "type": "time_overrun",
                "severity": "warning",
                "subject": subject,
                "message": f"{subject}作业用时异常，超出平均值 {(duration - avg_duration):.0f} 分钟",
                "suggestion": "可能需要针对性练习或重新理解知识点"
            })

        if record.get("help_requests", 0) > 5:
            anomalies.append({
                "type": "frequent_help",
                "severity": "high",
                "subject": subject,
                "message": f"{subject}频繁请求帮助 ({record.get('help_requests')}次)",
                "suggestion": "建议先复习基础知识，分解任务难度"
            })

        if record.get("completion_rate", 0) < 50:
            anomalies.append({
                "type": "low_completion",
                "severity": "medium",
                "subject": subject,
                "message": f"{subject}完成率较低 ({record.get('completion_rate')}%)",
                "suggestion": "分析原因，可能是难度过高或注意力问题"
            })

    help_by_subject: Dict[str, List[int]] = {}
    for record in homework_records:
        subject = record.get("subject", "未知")
        if subject not in help_by_subject:
            help_by_subject[subject] = []
        help_by_subject[subject].append(record.get("help_requests", 0))

    for subject, requests in help_by_subject.items():
        avg_requests = sum(requests) / len(requests) if requests else 0
        if avg_requests > 3:
            anomalies.append({
                "type": "knowledge_gap",
                "severity": "high",
                "subject": subject,
                "message": f"{subject}存在明显知识盲点，平均需要 {avg_requests:.1f} 次帮助",
                "suggestion": "建议系统复习该科目基础知识"
            })

    return anomalies


def analyze_knowledge_mastery(mistake_records: List[Dict[str, Any]]) -> List["KnowledgePoint"]:
    """分析知识点掌握度"""
    SessionContext, ProgressStats, KnowledgePoint, MistakeRecord, Recommendation, HomeworkRecord = _import_models()

    knowledge_points: Dict[str, Dict[str, Any]] = {}

    for mistake in mistake_records:
        for point_id in mistake.get("related_knowledge_points", []):
            if point_id not in knowledge_points:
                knowledge_points[point_id] = {
                    "point_id": point_id,
                    "point_name": point_id,
                    "subject": mistake.get("subject", ""),
                    "practice_count": 0,
                    "correct_count": 0,
                    "mastery_level": 1.0
                }
            knowledge_points[point_id]["practice_count"] += 1

    for point_id, data in knowledge_points.items():
        if data["practice_count"] > 0:
            data["mastery_level"] = data["correct_count"] / data["practice_count"]
            if data["practice_count"] >= 3 and data["mastery_level"] < 0.6:
                data["weakness_type"] = "反复出错"
            elif data["practice_count"] >= 5 and data["mastery_level"] < 0.8:
                data["weakness_type"] = "掌握不牢"

    return [KnowledgePoint(**data) for data in knowledge_points.values()]


def generate_personalized_recommendations(
    progress_stats: "ProgressStats",
    anomalies: List[Dict[str, Any]],
    knowledge_points: List["KnowledgePoint"]
) -> List["Recommendation"]:
    """生成个性化推荐"""
    SessionContext, ProgressStats, KnowledgePoint, MistakeRecord, Recommendation, HomeworkRecord = _import_models()

    recommendations = []

    for anomaly in anomalies:
        if anomaly["severity"] in ["high", "urgent"]:
            recommendations.append(Recommendation(
                recommendation_id=f"rec_{anomaly['type']}_{anomaly['subject']}",
                category="异常处理",
                priority="高",
                title=f"解决{anomaly['subject']}学习问题",
                description=anomaly.get("suggestion", ""),
                target_knowledge_points=[anomaly["subject"]],
                suggested_duration=30,
                confidence_score=0.9
            ))

    weak_points = [kp for kp in knowledge_points if kp.mastery_level < 0.7]
    if weak_points:
        recommendations.append(Recommendation(
            recommendation_id="rec_weak_points",
            category="知识巩固",
            priority="中",
            title="加强薄弱知识点",
            description=f"发现 {len(weak_points)} 个薄弱知识点需要重点练习",
            target_knowledge_points=[kp.point_id for kp in weak_points],
            suggested_duration=20,
            confidence_score=0.85
        ))

    if progress_stats.motivation_score < 60:
        recommendations.append(Recommendation(
            recommendation_id="rec_motivation",
            category="动机提升",
            priority="高",
            title="提升学习动机",
            description="当前学习动机较低，建议调整学习方法，增加正向激励",
            difficulty_adjustment="降低难度",
            confidence_score=0.8
        ))

    if progress_stats.total_distraction_events > 10:
        recommendations.append(Recommendation(
            recommendation_id="rec_focus",
            category="专注力训练",
            priority="中",
            title="减少学习干扰",
            description="检测到较多分心事件，建议使用番茄工作法",
            suggested_duration=15,
            confidence_score=0.75
        ))

    if progress_stats.subjects_mastered:
        recommendations.append(Recommendation(
            recommendation_id="rec_mastery",
            category="能力提升",
            priority="低",
            title="挑战更高难度",
            description=f"已掌握 {', '.join(progress_stats.subjects_mastered)}，可以适当挑战更高难度",
            suggested_duration=25,
            difficulty_adjustment="提高难度",
            confidence_score=0.7
        ))

    return recommendations


def create_session_context(payload: Dict[str, Any], session_id: str) -> "SessionContext":
    """创建会话上下文"""
    SessionContext, ProgressStats, KnowledgePoint, MistakeRecord, Recommendation, HomeworkRecord = _import_models()

    child_profile = payload.get("child_profile", {})

    return SessionContext(
        session_id=session_id,
        start_time=datetime.now().isoformat(),
        child_id=child_profile.get("name", "未知"),
        grade_level=child_profile.get("grade", 1),
        current_subject=payload.get("current_problem", "").split()[0] if payload.get("current_problem") else None,
        conversation_history=[],
        recent_performance=payload.get("raw_records", []),
        user_preferences=payload.get("preferences", {})
    )


def update_session_context(
    context: "SessionContext",
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


def get_context_summary(context: "SessionContext") -> str:
    """获取上下文摘要"""
    recent = context.get_recent_interactions(3)
    recent_summary = "\n".join([f"{i+1}. {r['content'][:50]}..." for i, r in enumerate(recent)]) if recent else "暂无历史对话"

    return f"""
会话ID: {context.session_id}
孩子: {context.child_id}
年级: {context.grade_level}
当前科目: {context.current_subject or '未指定'}
对话轮数: {len(context.conversation_history)}
最近表现: {len(context.recent_performance)} 条记录

最近对话:
{recent_summary}
""".strip()
