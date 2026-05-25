"""Planning engine for 儿童安全教育 Agent.

增强版本：添加数据分析、异常检测、个性化推荐、上下文记忆、数据聚合
"""
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta, date
from collections import defaultdict

try:
    from .models import (
        TrendData, Alert, Recommendation, SessionContext,
        WeeklyStats, SafetyLesson, SafetyTrainingRecord,
        SafetyCategory, RiskLevel, TrainingStatus
    )
except ImportError:
    from models import (
        TrendData, Alert, Recommendation, SessionContext,
        WeeklyStats, SafetyLesson, SafetyTrainingRecord,
        SafetyCategory, RiskLevel, TrainingStatus
    )

SKILL_FLOW = ['识别安全主题', '讲解安全知识', '角色扮演练习', '评估理解程度', '持续强化记忆']
SAFETY_NOTES = ['本 Skill 提供家庭教育和生活管理建议，不替代专业人士意见。', '涉及安全、法律、医疗、财务或教育政策时，应提示家长二次核验。', '输出应尊重家庭差异，不用单一标准评价孩子或父母。']
DEFAULT_DELIVERABLES = ['安全知识卡片', '危险场景题库', '应急反应指南']

_context_store: Dict[str, SessionContext] = {}


def get_or_create_context(session_id: str) -> SessionContext:
    """获取或创建会话上下文

    Args:
        session_id: 会话ID

    Returns:
        会话上下文对象
    """
    if session_id not in _context_store:
        _context_store[session_id] = SessionContext(session_id=session_id)
    return _context_store[session_id]


def update_context(session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
    """更新会话上下文

    Args:
        session_id: 会话ID
        role: 角色（user/assistant）
        content: 内容
        metadata: 额外元数据
    """
    context = get_or_create_context(session_id)
    context.add_interaction(role, content, metadata)


def analyze_safety_trends(records: List[Dict[str, Any]], days: int = 7) -> List[TrendData]:
    """分析安全培训趋势

    Args:
        records: 安全培训记录列表
        days: 分析天数

    Returns:
        趋势数据列表
    """
    trends = []

    if not records:
        return trends

    records_by_date = defaultdict(list)
    for record in records:
        try:
            if isinstance(record.get("timestamp"), str):
                record_date = datetime.fromisoformat(record["timestamp"]).date()
            elif isinstance(record.get("timestamp"), datetime):
                record_date = record["timestamp"].date()
            else:
                continue
            records_by_date[record_date].append(record)
        except (ValueError, AttributeError):
            continue

    if not records_by_date:
        return trends

    sorted_dates = sorted(records_by_date.keys())
    if len(sorted_dates) > days:
        sorted_dates = sorted_dates[-days:]

    daily_completion = []
    daily_score = []
    dates = []

    for d in sorted_dates:
        day_records = records_by_date[d]

        completed_count = sum(1 for r in day_records if r.get("status") == "completed")
        total_count = len(day_records)
        completion_rate = (completed_count / total_count * 100) if total_count > 0 else 0
        daily_completion.append(completion_rate)

        scores = []
        for r in day_records:
            correct = r.get("correct_responses", 0) or 0
            total = r.get("total_questions", 0) or 1
            if total > 0:
                scores.append((correct / total) * 100)
        avg_score = sum(scores) / len(scores) if scores else 0
        daily_score.append(avg_score)

        dates.append(d.isoformat())

    if daily_completion:
        completion_trend = TrendData(
            metric_name="培训完成率",
            data_points=daily_completion,
            dates=dates
        )
        completion_trend.calculate_trend()
        trends.append(completion_trend)

    if daily_score:
        score_trend = TrendData(
            metric_name="平均正确率",
            data_points=daily_score,
            dates=dates
        )
        score_trend.calculate_trend()
        trends.append(score_trend)

    return trends


def detect_safety_anomalies(records: List[Dict[str, Any]], trends: List[TrendData]) -> List[Alert]:
    """检测安全培训异常

    Args:
        records: 安全培训记录列表
        trends: 趋势数据列表

    Returns:
        告警列表
    """
    alerts = []

    if not records:
        return alerts

    for trend in trends:
        if trend.metric_name == "平均正确率":
            if trend.trend_direction == "decreasing" and trend.trend_percentage < -15:
                alerts.append(Alert(
                    alert_type="正确率下降",
                    severity="warning",
                    message=f"孩子的安全知识正确率下降了 {abs(trend.trend_percentage):.1f}%，需要加强",
                    recommendation="重复讲解关键安全点，使用更多角色扮演练习"
                ))

            if trend.average > 0 and trend.average < 60:
                alerts.append(Alert(
                    alert_type="正确率偏低",
                    severity="warning",
                    message=f"安全知识正确率只有 {trend.average:.1f}%，需要重点强化",
                    recommendation="简化概念，使用更具体的例子，增加实践练习"
                ))

    categories_tested = defaultdict(int)
    for record in records:
        cat = record.get("lesson_id", "unknown").split("_")[0] if record.get("lesson_id") else "unknown"
        categories_tested[cat] += 1

    if len(categories_tested) < 3 and len(records) >= 5:
        alerts.append(Alert(
            alert_type="培训覆盖不足",
            severity="info",
            message="安全培训覆盖的主题较少，建议增加多样性",
            recommendation="涵盖更多安全主题，如陌生人、火安全、交通安全等"
        ))

    reinforcement_needed = sum(1 for r in records if r.get("reinforcement_needed", False))
    if reinforcement_needed > len(records) * 0.3:
        alerts.append(Alert(
            alert_type="需要强化",
            severity="info",
            message=f"{reinforcement_needed}项培训需要强化（{reinforcement_needed/len(records)*100:.0f}%）",
            recommendation="对薄弱的安全主题进行强化训练，使用不同方式重复讲解"
        ))

    return alerts


def generate_personalized_recommendations(
    records: List[Dict[str, Any]],
    trends: List[TrendData],
    child_profile: Dict[str, Any],
    alerts: List[Alert]
) -> List[Recommendation]:
    """生成个性化推荐

    Args:
        records: 安全培训记录列表
        trends: 趋势数据列表
        child_profile: 孩子画像
        alerts: 告警列表

    Returns:
        推荐列表
    """
    recommendations = []

    age_months = child_profile.get("age_months", 0)

    critical_categories = ["fire_safety", "water_safety", "stranger_danger"]
    covered_critical = set()

    for record in records:
        lesson = record.get("lesson_id", "")
        for cat in critical_categories:
            if cat in lesson.lower():
                covered_critical.add(cat)

    missing_critical = [c for c in critical_categories if c not in covered_critical]
    if missing_critical:
        recommendations.append(Recommendation(
            category="安全覆盖",
            priority=1,
            title="补充关键安全主题",
            description=f"以下高风险安全主题尚未培训：{', '.join(missing_critical)}",
            action_items=[
                "安排火灾安全教育",
                "进行水上安全培训",
                "教授陌生人应对策略"
            ],
            rationale="这些是儿童最重要的高风险安全技能",
            expected_outcome="覆盖所有关键安全主题"
        ))

    for trend in trends:
        if trend.metric_name == "平均正确率" and trend.average < 80:
            recommendations.append(Recommendation(
                category="培训强化",
                priority=1,
                title="提高安全知识正确率",
                description=f"当前正确率为 {trend.average:.1f}%，建议使用多样化教学方法",
                action_items=[
                    "使用图片和动画讲解",
                    "进行角色扮演练习",
                    "设置安全知识问答游戏"
                ],
                rationale="游戏化学习可以提高孩子的兴趣和记忆效果",
                expected_outcome="正确率达到80%以上"
            ))

    for alert in alerts:
        if alert.alert_type == "正确率下降":
            recommendations.append(Recommendation(
                category="培训调整",
                priority=2,
                title="调整培训策略",
                description="当前培训方式可能不够有效，需要改变教学方法",
                action_items=[
                    "简化安全概念",
                    "使用更多实际例子",
                    "增加互动和实践环节"
                ],
                rationale="根据孩子的学习特点调整教学方式",
                expected_outcome="重新提升安全知识掌握程度"
            ))

    if not alerts and len(records) >= 5:
        recommendations.append(Recommendation(
            category="持续培训",
            priority=3,
            title="保持安全培训频率",
            description="继续定期进行安全培训，巩固已学知识",
            action_items=[
                "每周安排1-2次安全培训",
                "定期复习已学内容",
                "根据年龄增长调整培训内容"
            ],
            rationale="安全意识的培养需要持续强化",
            expected_outcome="建立完整的安全知识体系"
        ))

    recommendations.sort(key=lambda x: x.priority)
    return recommendations


def aggregate_weekly_stats(records: List[Dict[str, Any]], week_offset: int = 0) -> Optional[WeeklyStats]:
    """聚合周统计数据

    Args:
        records: 安全培训记录列表
        week_offset: 周偏移（0=本周，-1=上周）

    Returns:
        周统计数据对象
    """
    if not records:
        return None

    today = datetime.now().date()
    days_since_monday = today.weekday()
    week_start = today - timedelta(days=days_since_monday + week_offset * 7)
    week_end = week_start + timedelta(days=6)

    week_records = []
    for record in records:
        try:
            if isinstance(record.get("timestamp"), str):
                record_date = datetime.fromisoformat(record["timestamp"]).date()
            elif isinstance(record.get("timestamp"), datetime):
                record_date = record["timestamp"].date()
            else:
                continue

            if week_start <= record_date <= week_end:
                week_records.append(record)
        except (ValueError, AttributeError, TypeError):
            continue

    if not week_records:
        return None

    total_sessions = len(week_records)
    completed_sessions = sum(1 for r in week_records if r.get("status") == "completed")
    completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0

    scores = []
    for r in week_records:
        correct = r.get("correct_responses", 0) or 0
        total = r.get("total_questions", 0) or 1
        if total > 0:
            scores.append((correct / total) * 100)

    avg_score = sum(scores) / len(scores) if scores else 0

    reinforcement_needed = sum(1 for r in week_records if r.get("reinforcement_needed", False))

    categories_covered = []
    for r in week_records:
        lesson = r.get("lesson_id", "")
        if lesson and lesson not in categories_covered:
            categories_covered.append(lesson)

    return WeeklyStats(
        week_start=week_start.isoformat(),
        week_end=week_end.isoformat(),
        total_sessions=total_sessions,
        completion_rate=completion_rate,
        average_score=avg_score,
        lessons_completed=completed_sessions,
        categories_covered=categories_covered,
        reinforcement_needed=reinforcement_needed
    )


def build_known_facts(payload: Dict[str, Any]) -> List[str]:
    """构建已知事实列表

    Args:
        payload: 输入数据

    Returns:
        事实列表
    """
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

    if records:
        trends = analyze_safety_trends(records, payload.get("history_days", 7))
        if trends:
            for trend in trends:
                facts.append(
                    f"{trend.metric_name}：平均 {trend.average:.1f}，"
                    f"趋势 {trend.trend_direction}（{trend.trend_percentage:+.1f}%）"
                )

    return facts


def build_analysis(payload: Dict[str, Any]) -> List[str]:
    """构建分析内容

    Args:
        payload: 输入数据

    Returns:
        分析内容列表
    """
    problem = payload.get("current_problem", "")
    history_days = payload.get("history_days", 7)
    records = payload.get("raw_records") or []
    child_profile = payload.get("child_profile", {})

    analysis = [
        f"当前问题聚焦：{problem}",
        f"建议先建立最近 {history_days} 天的安全培训基线，再判断趋势。",
        "本 Skill 会优先输出可执行动作、记录字段和复盘指标。",
    ]

    for step in SKILL_FLOW:
        analysis.append(f"链路节点：{step}")

    if records:
        trends = analyze_safety_trends(records, history_days)
        alerts = detect_safety_anomalies(records, trends)

        if alerts:
            analysis.append("")
            analysis.append("⚠️ 检测到的异常：")
            for alert in alerts:
                analysis.append(f"  - [{alert.severity}] {alert.message}")

        recommendations = generate_personalized_recommendations(records, trends, child_profile, alerts)
        if recommendations:
            analysis.append("")
            analysis.append("📋 个性化建议：")
            for rec in recommendations[:3]:
                analysis.append(f"  - {rec.title}：{rec.description}")

    return analysis


def build_action_plan(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """构建行动计划

    Args:
        payload: 输入数据

    Returns:
        行动计划列表
    """
    base_tasks = [
        "补齐孩子画像和家庭限制条件",
        "选择安全主题进行培训",
        "执行安全培训并记录结果",
        "进行角色扮演练习",
        "一周后比较趋势并调整计划",
    ]

    records = payload.get("raw_records") or []
    if records:
        base_tasks.insert(0, f"分析最近 {len(records)} 条记录的趋势")

    plan: List[Dict[str, str]] = []
    for i, task in enumerate(base_tasks, start=1):
        plan.append({
            "day": f"D{i}",
            "task": task,
            "owner": "家长/主要照护人",
            "evidence_to_record": "主题、完成情况、正确率、角色扮演表现",
            "difficulty": "低" if i <= 3 else "中"
        })
    return plan


def build_deliverables(payload: Dict[str, Any]) -> Dict[str, Any]:
    """构建交付物

    Args:
        payload: 输入数据

    Returns:
        交付物字典
    """
    deliverables = {
        "required": DEFAULT_DELIVERABLES,
        "tables": {
            "timeline": ["时间", "事件", "输入", "处理", "结果", "备注"],
            "weekly_review": ["指标", "本周", "上周", "变化", "下一步"]
        },
        "templates": {
            "daily_log": "今天进行了哪些安全培训？孩子的表现如何？需要强化什么？",
            "handoff_summary": "给专业人士/老师/家人的沟通摘要：事实、时间线、已尝试方法、待确认问题。"
        }
    }

    records = payload.get("raw_records") or []
    if records:
        trends = analyze_safety_trends(records, payload.get("history_days", 7))
        if trends:
            deliverables["analysis_charts"] = {
                "trend_summary": [
                    {
                        "metric": t.metric_name,
                        "average": round(t.average, 2),
                        "trend": t.trend_direction,
                        "change_percent": round(t.trend_percentage, 2)
                    }
                    for t in trends
                ]
            }

    return deliverables


def next_fields() -> List[str]:
    """获取下次追踪字段

    Returns:
        字段列表
    """
    return [
        "孩子年龄/月龄",
        "今天新增记录",
        "执行了哪一步",
        "孩子反应",
        "家长感受",
        "需要调整的限制条件"
    ]


def generate_session_summary(session_id: str) -> Optional[Dict[str, Any]]:
    """生成会话摘要

    Args:
        session_id: 会话ID

    Returns:
        会话摘要字典
    """
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
    """清除会话上下文

    Args:
        session_id: 会话ID

    Returns:
        是否成功清除
    """
    if session_id in _context_store:
        del _context_store[session_id]
        return True
    return False


def create_safety_lesson(lesson_name: str, category: str) -> SafetyLesson:
    """创建安全课程

    Args:
        lesson_name: 课程名称
        category: 安全类别

    Returns:
        安全课程对象
    """
    lesson_id = f"safety_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    return SafetyLesson(
        lesson_id=lesson_id,
        lesson_name=lesson_name,
        category=category,
        description=f"安全课程: {lesson_name}",
        key_points=["识别危险", "正确求助", "自我保护"],
        estimated_duration_minutes=15
    )


def calculate_safety_score(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """计算安全培训评分

    Args:
        records: 安全培训记录列表

    Returns:
        安全培训评分字典
    """
    if not records:
        return {
            "overall_score": 0,
            "knowledge_score": 0,
            "practice_score": 0,
            "coverage_score": 0,
            "level": "无数据"
        }

    scores = []
    for r in records:
        correct = r.get("correct_responses", 0) or 0
        total = r.get("total_questions", 0) or 1
        if total > 0:
            scores.append((correct / total) * 100)

    knowledge_score = sum(scores) / len(scores) if scores else 0

    practice_scores = [r.get("role_play_score", 0) or 0 for r in records]
    practice_score = sum(practice_scores) / len(practice_scores) * 10 if practice_scores else 0

    covered_categories = set()
    for r in records:
        lesson = r.get("lesson_id", "")
        if lesson:
            cat = lesson.split("_")[1] if "_" in lesson else "unknown"
            covered_categories.add(cat)

    coverage_score = min(100, (len(covered_categories) / 8) * 100)

    overall_score = (knowledge_score * 0.5 + practice_score * 0.3 + coverage_score * 0.2)

    if overall_score >= 80:
        level = "优秀"
    elif overall_score >= 60:
        level = "良好"
    elif overall_score >= 40:
        level = "一般"
    else:
        level = "需加强"

    return {
        "overall_score": round(overall_score, 1),
        "knowledge_score": round(knowledge_score, 1),
        "practice_score": round(practice_score, 1),
        "coverage_score": round(coverage_score, 1),
        "level": level
    }