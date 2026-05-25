"""Planning engine for 儿童图书推荐 Agent.

增强版本：添加数据分析、异常检测、个性化推荐、上下文记忆支持和数据聚合统计。
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta, date
from collections import Counter

try:
    from .analytics import (
        calculate_statistics,
        analyze_reading_patterns,
        calculate_engagement_indicators,
        detect_reading_issues,
        compare_with_recommendations,
        generate_reading_insights,
        personalize_recommendations,
        aggregate_statistics,
        predict_optimal_reading_time,
        generate_trend_data,
        calculate_trend_percentage,
        ContextMemory
    )
except ImportError:
    from analytics import (
        calculate_statistics,
        analyze_reading_patterns,
        calculate_engagement_indicators,
        detect_reading_issues,
        compare_with_recommendations,
        generate_reading_insights,
        personalize_recommendations,
        aggregate_statistics,
        predict_optimal_reading_time,
        generate_trend_data,
        calculate_trend_percentage,
        ContextMemory
    )

try:
    from .models import TrendData, Alert, ActionItem
except ImportError:
    from models import TrendData, Alert, ActionItem

SKILL_FLOW = ['输入年龄、兴趣、阅读水平', '推荐分级书单', '生成共读方法', '记录孩子反馈', '动态调整书单']
SAFETY_NOTES = [
    '本 Skill 只做信息整理、对比和风险提示，不替家长做最终消费决定。',
    '涉及价格、招生名额、合同条款、机构资质、口碑等信息时，应要求人工核验最新资料。',
    '输出应区分事实、推断、主观偏好和待核验项，避免夸大承诺。'
]
DEFAULT_DELIVERABLES = ['个性化书单', '阅读路线', '购买优先级']


def build_known_facts(payload: Dict[str, Any]) -> List[str]:
    """构建已知事实列表

    Args:
        payload: 输入负载字典

    Returns:
        已知事实列表
    """
    facts: List[str] = []
    child = payload.get("child_profile", {})
    family = payload.get("family_context", {})
    if child:
        age = child.get("age_years", 0)
        interests = child.get("interests", [])
        reading_level = child.get("reading_level", "unknown")
        facts.append(f"孩子画像：年龄{age}岁，兴趣{interests}，阅读水平{reading_level}")
    if family:
        facts.append(f"家庭上下文：{family}")
    if payload.get("goal"):
        facts.append(f"目标：{payload.get('goal')}")
    records = payload.get("raw_records") or []
    facts.append(f"已收到 {len(records)} 条原始记录。")

    if records:
        patterns = analyze_reading_patterns(records)
        if patterns.get("average_session_duration"):
            facts.append(f"平均阅读时长：{patterns['average_session_duration']:.0f}分钟")
        if patterns.get("reading_streak"):
            facts.append(f"连续阅读天数：{patterns['reading_streak']}天")

    return facts


def build_analysis(payload: Dict[str, Any]) -> List[str]:
    """构建分析结果列表

    Args:
        payload: 输入负载字典

    Returns:
        分析结果列表
    """
    problem = payload.get("current_problem", "")
    history_days = payload.get("history_days", 7)
    records = payload.get("raw_records") or []
    child_profile = payload.get("child_profile", {})
    recommendations = payload.get("recommendations", [])

    analysis: List[str] = [
        f"当前问题聚焦：{problem}",
        f"建议先建立最近 {history_days} 天的家庭基线，再判断趋势。",
        "本 Skill 会优先输出可执行动作、记录字段和复盘指标。",
    ]

    if records:
        issues = detect_reading_issues(records)
        if issues:
            analysis.append(f"检测到 {len(issues)} 个需要关注的问题")
            for issue in issues[:3]:
                analysis.append(f"  - [{issue['severity']}] {issue['description']}")

        patterns = analyze_reading_patterns(records)
        if patterns.get("most_common_session_time"):
            analysis.append(f"最佳阅读时段：{patterns['most_common_session_time']}")
        if patterns.get("preferred_days"):
            analysis.append(f"偏好阅读日：{', '.join(patterns['preferred_days'])}")

        engagement = calculate_engagement_indicators(records, child_profile)
        if engagement.get("engagement_level"):
            analysis.append(f"参与度评估：{engagement['engagement_level']}")
        if engagement.get("engagement_trend"):
            trend_icon = {"increasing": "📈", "decreasing": "📉", "stable": "➡️"}.get(
                engagement["engagement_trend"], ""
            )
            analysis.append(f"参与度趋势：{trend_icon}{engagement['engagement_trend']}")

    for step in SKILL_FLOW:
        analysis.append(f"链路节点：{step}")
    return analysis


def build_action_plan(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """构建行动计划列表

    Args:
        payload: 输入负载字典

    Returns:
        行动计划列表
    """
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
    """构建交付物字典

    Args:
        payload: 输入负载字典

    Returns:
        交付物字典
    """
    return {
        "required": DEFAULT_DELIVERABLES,
        "tables": {
            "timeline": ["时间", "事件", "输入", "处理", "结果", "备注"],
            "weekly_review": ["指标", "本周", "上周", "变化", "下一步"],
            "book_recommendations": ["优先级", "书名", "作者", "分类", "适读年龄", "教育价值", "趣味性"]
        },
        "templates": {
            "daily_log": "今天发生了什么？我做了什么？孩子反应如何？下一次要调整什么？",
            "handoff_summary": "给专业人士/老师/家人的沟通摘要：事实、时间线、已尝试方法、待确认问题。"
        }
    }


def next_fields() -> List[str]:
    """获取下次追踪字段列表

    Returns:
        追踪字段列表
    """
    return [
        "孩子年龄/月龄",
        "今天新增记录",
        "执行了哪一步",
        "孩子反应",
        "家长感受",
        "需要调整的限制条件"
    ]


def analyze_data(payload: Dict[str, Any]) -> Dict[str, Any]:
    """执行数据分析

    Args:
        payload: 输入负载字典

    Returns:
        分析结果字典
    """
    records = payload.get("raw_records") or []
    child_profile = payload.get("child_profile", {})
    recommendations = payload.get("recommendations", [])

    result = {
        "statistics": {},
        "patterns": {},
        "engagement": {},
        "issues": [],
        "comparison": {},
        "insights": [],
        "personalized_recommendations": [],
        "alerts": [],
        "trends": []
    }

    if records:
        result["statistics"] = aggregate_statistics(records)
        result["patterns"] = analyze_reading_patterns(records)
        result["engagement"] = calculate_engagement_indicators(records, child_profile)
        result["issues"] = detect_reading_issues(records)
        result["comparison"] = compare_with_recommendations(records, recommendations, child_profile)

        trends = []
        for metric in ["engagement", "duration"]:
            data_points = generate_trend_data(records, metric)
            if data_points and len(data_points) >= 2:
                direction, percentage = calculate_trend_percentage(data_points)
                trends.append({
                    "metric_name": f"阅读{metric}",
                    "current_value": data_points[-1].get("value", 0),
                    "previous_value": data_points[0].get("value", 0),
                    "trend_direction": direction,
                    "trend_percentage": percentage,
                    "data_points": data_points
                })
        result["trends"] = trends

    if child_profile and recommendations:
        result["personalized_recommendations"] = personalize_recommendations(
            child_profile, records, recommendations
        )

    result["insights"] = generate_reading_insights(
        records,
        [TrendData(**t) for t in result.get("trends", [])],
        child_profile
    )

    result["alerts"] = generate_alerts(result)

    return result


def generate_alerts(analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """生成预警信息

    Args:
        analysis_result: 分析结果字典

    Returns:
        预警列表
    """
    alerts: List[Dict[str, Any]] = []

    issues = analysis_result.get("issues", [])
    for issue in issues:
        if issue.get("severity") == "warning":
            alerts.append({
                "alert_type": "reading_issue",
                "severity": "warning",
                "message": issue.get("description", ""),
                "recommendation": issue.get("recommendation", ""),
                "timestamp": datetime.now().isoformat()
            })

    engagement = analysis_result.get("engagement", {})
    if engagement.get("engagement_level") in ["很低", "偏低"]:
        alerts.append({
            "alert_type": "engagement_low",
            "severity": "info",
            "message": f"阅读参与度{engagement['engagement_level']}",
            "recommendation": "考虑选择更有吸引力的图书或增加互动环节",
            "timestamp": datetime.now().isoformat()
        })

    comparison = analysis_result.get("comparison", {})
    if comparison.get("overall_assessment") == "需改进":
        alerts.append({
            "alert_type": "recommendation_deviation",
            "severity": "warning",
            "message": "阅读习惯偏离推荐标准",
            "recommendation": "建议增加阅读频率或尝试新类型图书",
            "timestamp": datetime.now().isoformat()
        })

    return alerts


def build_personalized_plan(
    payload: Dict[str, Any],
    context_memory: Optional[ContextMemory] = None
) -> Dict[str, Any]:
    """构建个性化计划

    Args:
        payload: 输入负载字典
        context_memory: 上下文记忆对象

    Returns:
        个性化计划字典
    """
    child_profile = payload.get("child_profile", {})
    records = payload.get("raw_records") or []

    plan = {
        "recommended_reading_time": None,
        "recommended_duration": 15,
        "priority_books": [],
        "weekly_goals": [],
        "tips": []
    }

    if records:
        prediction = predict_optimal_reading_time(records)
        plan["recommended_reading_time"] = prediction.get("recommended_time")
        plan["recommended_duration"] = prediction.get("recommended_duration")

    age = child_profile.get("age_years", 5)
    if age < 3:
        plan["recommended_duration"] = 10
        plan["weekly_goals"] = ["每天阅读1-2本绘本", "培养阅读习惯", "增加亲子互动"]
        plan["tips"] = ["选择颜色鲜艳的绘本", "简短有趣的故事", "多使用拟声词"]
    elif age < 6:
        plan["recommended_duration"] = 15
        plan["weekly_goals"] = ["每周阅读3-4本绘本", "开始认字启蒙", "培养专注力"]
        plan["tips"] = ["选择有重复句式的绘本", "鼓励孩子复述故事", "关联生活场景"]
    elif age < 10:
        plan["recommended_duration"] = 20
        plan["weekly_goals"] = ["每周阅读2-3本书", "培养独立阅读", "写读后感"]
        plan["tips"] = ["选择图文并茂的桥梁书", "讨论书中人物", "鼓励提问"]
    else:
        plan["recommended_duration"] = 30
        plan["weekly_goals"] = ["每周阅读1-2本章节书", "培养深度阅读", "批判性思考"]
        plan["tips"] = ["选择多元题材", "鼓励写读书笔记", "讨论主题思想"]

    if context_memory:
        context_summary = context_memory.get_context_summary()
        plan["context_summary"] = context_summary

    return plan


def calculate_summary_metrics(payload: Dict[str, Any]) -> Dict[str, Any]:
    """计算摘要指标

    Args:
        payload: 输入负载字典

    Returns:
        摘要指标字典
    """
    records = payload.get("raw_records") or []
    recommendations = payload.get("recommendations", [])

    metrics = {
        "total_records": len(records),
        "total_recommendations": len(recommendations),
        "reading_consistency_score": 0,
        "engagement_score": 0,
        "diversity_score": 0,
        "overall_progress": 0
    }

    if records:
        patterns = analyze_reading_patterns(records)
        metrics["reading_consistency_score"] = min(100, patterns.get("reading_streak", 0) * 10)

        engagement = calculate_engagement_indicators(records, {})
        if engagement.get("average_engagement"):
            metrics["engagement_score"] = (engagement["average_engagement"] / 5) * 100

        unique_books = len(set(r.get("book_title", "") for r in records))
        metrics["diversity_score"] = min(100, unique_books * 20)

        total_progress = metrics["reading_consistency_score"] + metrics["engagement_score"] + metrics["diversity_score"]
        metrics["overall_progress"] = total_progress / 3

    return metrics


def update_context_memory(
    payload: Dict[str, Any],
    context_memory: ContextMemory
) -> ContextMemory:
    """更新上下文记忆

    Args:
        payload: 输入负载字典
        context_memory: 上下文记忆对象

    Returns:
        更新后的上下文记忆对象
    """
    records = payload.get("raw_records") or []
    preferences = payload.get("preferences", {})

    for record in records:
        context_memory.add_record(record)

    if preferences:
        context_memory.update_preferences(preferences)

    context_memory.learn_from_history()

    return context_memory


def generate_data_report(payload: Dict[str, Any]) -> Dict[str, Any]:
    """生成数据报告

    Args:
        payload: 输入负载字典

    Returns:
        数据报告字典
    """
    analysis = analyze_data(payload)
    metrics = calculate_summary_metrics(payload)
    child_profile = payload.get("child_profile", {})
    recommendations = payload.get("recommendations", [])

    report = {
        "summary": [
            f"共分析 {len(payload.get('raw_records', []))} 条阅读记录",
            f"推荐书目 {len(recommendations)} 本",
            f"整体进度 {metrics['overall_progress']:.0f}%"
        ],
        "statistics": analysis.get("statistics", {}),
        "patterns": analysis.get("patterns", {}),
        "engagement": analysis.get("engagement", {}),
        "metrics": metrics,
        "insights": analysis.get("insights", []),
        "alerts": analysis.get("alerts", []),
        "trends": analysis.get("trends", []),
        "personalized_recommendations": analysis.get("personalized_recommendations", []),
        "comparison": analysis.get("comparison", {})
    }

    return report