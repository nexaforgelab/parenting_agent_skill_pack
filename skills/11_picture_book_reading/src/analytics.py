"""Learning analytics module for 绘本共读 Agent.

提供学习数据的深度分析功能，包括趋势分析、模式识别和预测。
"""
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import uuid


def calculate_engagement_trend(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """计算投入度趋势

    Args:
        records: 学习记录列表

    Returns:
        投入度趋势分析结果
    """
    if not records:
        return {
            "trend": "no_data",
            "slope": 0.0,
            "direction": "unknown"
        }

    engagement_scores = [r.get("engagement_score", 0.0) for r in records]

    if len(engagement_scores) < 2:
        return {
            "trend": "insufficient_data",
            "slope": 0.0,
            "direction": "unknown"
        }

    n = len(engagement_scores)
    x_values = list(range(n))
    x_mean = sum(x_values) / n
    y_mean = sum(engagement_scores) / n

    numerator = sum((x_values[i] - x_mean) * (engagement_scores[i] - y_mean) for i in range(n))
    denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))

    slope = numerator / denominator if denominator != 0 else 0.0

    if slope > 0.05:
        direction = "improving"
    elif slope < -0.05:
        direction = "declining"
    else:
        direction = "stable"

    return {
        "trend": direction,
        "slope": round(slope, 4),
        "direction": direction,
        "average": round(y_mean, 2),
        "current": round(engagement_scores[-1], 2) if engagement_scores else 0.0
    }


def identify_learning_patterns(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """识别学习模式

    Args:
        records: 学习记录列表

    Returns:
        学习模式分析结果
    """
    if not records:
        return {"patterns": [], "insights": []}

    patterns = []
    insights = []

    durations = [r.get("duration_minutes", 0) for r in records]
    if durations:
        avg_duration = sum(durations) / len(durations)
        patterns.append(f"平均学习时长: {avg_duration:.1f} 分钟")

        if avg_duration > 20:
            insights.append("建议: 单次学习时间偏长，可能影响专注力")

    engagement_by_duration = defaultdict(list)
    for r in records:
        duration_bucket = r.get("duration_minutes", 0) // 5
        engagement_by_duration[duration_bucket].append(r.get("engagement_score", 0.0))

    if engagement_by_duration:
        best_bucket = max(engagement_by_duration.items(), key=lambda x: sum(x[1]) / len(x[1]) if x[1] else 0)
        optimal_duration = best_bucket[0] * 5 + 2
        patterns.append(f"最佳学习时长: 约 {optimal_duration} 分钟")

    interaction_types = defaultdict(int)
    for r in records:
        itype = r.get("interaction_type", "提问")
        interaction_types[itype] += 1

    if interaction_types:
        most_common = max(interaction_types.items(), key=lambda x: x[1])
        patterns.append(f"最常用互动方式: {most_common[0]}")

    return {
        "patterns": patterns,
        "insights": insights,
        "optimal_duration": optimal_duration if engagement_by_duration else 15
    }


def predict_learning_outcome(records: List[Dict[str, Any]], weeks_ahead: int = 4) -> Dict[str, Any]:
    """预测学习成果

    Args:
        records: 学习记录列表
        weeks_ahead: 预测周数

    Returns:
        学习成果预测结果
    """
    if len(records) < 5:
        return {
            "prediction": "insufficient_data",
            "confidence": "low",
            "estimated_mastery": 0.0
        }

    engagement_trend = calculate_engagement_trend(records)

    current_avg = sum(r.get("engagement_score", 0.0) for r in records) / len(records)

    predicted_score = current_avg + engagement_trend["slope"] * weeks_ahead * 7

    confidence = "medium" if len(records) >= 10 else "low"

    if predicted_score > 9.0:
        predicted_mastery = "MASTERED"
    elif predicted_score > 7.0:
        predicted_mastery = "FAMILIAR"
    elif predicted_score > 5.0:
        predicted_mastery = "LEARNING"
    else:
        predicted_mastery = "NOT_STARTED"

    return {
        "prediction": "预计4周后投入度将达到良好水平",
        "confidence": confidence,
        "estimated_mastery": predicted_mastery,
        "estimated_score": round(max(0, min(10, predicted_score)), 2)
    }


def calculate_learning_efficiency(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """计算学习效率

    Args:
        records: 学习记录列表

    Returns:
        学习效率分析结果
    """
    if not records:
        return {
            "efficiency_score": 0.0,
            "time_per_session": 0.0,
            "engagement_per_minute": 0.0
        }

    total_minutes = sum(r.get("duration_minutes", 0) for r in records)
    total_sessions = len(records)
    total_engagement = sum(r.get("engagement_score", 0.0) for r in records)

    time_per_session = total_minutes / total_sessions if total_sessions > 0 else 0
    engagement_per_minute = total_engagement / total_minutes if total_minutes > 0 else 0

    efficiency_score = (total_engagement / total_minutes * 10) if total_minutes > 0 else 0

    return {
        "efficiency_score": round(efficiency_score, 2),
        "time_per_session": round(time_per_session, 1),
        "engagement_per_minute": round(engagement_per_minute, 2),
        "total_sessions": total_sessions,
        "total_minutes": total_minutes
    }


def analyze_topic_distribution(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析主题分布

    Args:
        records: 学习记录列表

    Returns:
        主题分布分析结果
    """
    topic_counts = defaultdict(int)
    topic_engagement = defaultdict(list)

    for record in records:
        for topic in record.get("topics_covered", []):
            topic_counts[topic] += 1
            topic_engagement[topic].append(record.get("engagement_score", 0.0))

    topic_stats = []
    for topic, count in topic_counts.items():
        avg_engagement = sum(topic_engagement[topic]) / len(topic_engagement[topic]) if topic_engagement[topic] else 0
        topic_stats.append({
            "topic": topic,
            "count": count,
            "average_engagement": round(avg_engagement, 2)
        })

    topic_stats.sort(key=lambda x: x["count"], reverse=True)

    favorite_topics = [t["topic"] for t in topic_stats[:3]]
    difficult_topics = [t["topic"] for t in topic_stats if t["average_engagement"] < 5.0]

    return {
        "topic_distribution": topic_stats,
        "favorite_topics": favorite_topics,
        "difficult_topics": difficult_topics,
        "unique_topics": len(topic_counts)
    }


def calculate_retention_rate(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """计算记忆保持率

    Args:
        records: 学习记录列表

    Returns:
        记忆保持率分析结果
    """
    if len(records) < 2:
        return {
            "retention_rate": 0.0,
            "description": "数据不足，无法计算"
        }

    answered_rates = []
    for r in records:
        asked = r.get("questions_asked", 1)
        answered = r.get("questions_answered", 0)
        if asked > 0:
            answered_rates.append(answered / asked)

    avg_rate = sum(answered_rates) / len(answered_rates) if answered_rates else 0.0

    if avg_rate >= 0.8:
        description = "记忆保持优秀"
    elif avg_rate >= 0.6:
        description = "记忆保持良好"
    elif avg_rate >= 0.4:
        description = "记忆保持一般"
    else:
        description = "需要加强复习"

    return {
        "retention_rate": round(avg_rate * 100, 1),
        "description": description
    }


def generate_learning_insights(records: List[Dict[str, Any]]) -> List[str]:
    """生成学习洞察

    Args:
        records: 学习记录列表

    Returns:
        学习洞察列表
    """
    insights = []

    if not records:
        return ["暂无学习记录，建议开始记录学习数据"]

    trend = calculate_engagement_trend(records)
    if trend["direction"] == "improving":
        insights.append("✅ 学习投入度呈上升趋势，继续保持！")
    elif trend["direction"] == "declining":
        insights.append("⚠️ 学习投入度有所下降，建议调整学习方法")

    efficiency = calculate_learning_efficiency(records)
    if efficiency["time_per_session"] > 25:
        insights.append("💡 单次学习时间偏长，建议分段学习")

    retention = calculate_retention_rate(records)
    if retention["retention_rate"] < 50:
        insights.append("📚 建议增加复习频率，巩固学习内容")

    topic_analysis = analyze_topic_distribution(records)
    if topic_analysis["difficult_topics"]:
        insights.append(f"🎯 需要在以下主题加强: {', '.join(topic_analysis['difficult_topics'][:2])}")

    return insights


def calculate_mastery_metrics(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """计算掌握度指标

    Args:
        records: 学习记录列表

    Returns:
        掌握度指标分析结果
    """
    if not records:
        return {
            "mastery_score": 0.0,
            "mastery_level": "NOT_STARTED"
        }

    total_sessions = len(records)
    avg_engagement = sum(r.get("engagement_score", 0.0) for r in records) / total_sessions

    answer_rates = []
    for r in records:
        asked = r.get("questions_asked", 1)
        answered = r.get("questions_answered", 0)
        if asked > 0:
            answer_rates.append(answered / asked)

    avg_answer_rate = sum(answer_rates) / len(answer_rates) if answer_rates else 0.0

    mastered_count = sum(1 for r in records if r.get("comprehension_level") == "已掌握")
    mastered_rate = mastered_count / total_sessions if total_sessions > 0 else 0.0

    mastery_score = (
        avg_engagement / 10 * 40 +
        avg_answer_rate * 40 +
        mastered_rate * 20
    )

    if mastery_score >= 80:
        mastery_level = "MASTERED"
    elif mastery_score >= 60:
        mastery_level = "FAMILIAR"
    elif mastery_score >= 30:
        mastery_level = "LEARNING"
    else:
        mastery_level = "NOT_STARTED"

    return {
        "mastery_score": round(mastery_score, 2),
        "mastery_level": mastery_level,
        "avg_engagement": round(avg_engagement, 2),
        "avg_answer_rate": round(avg_answer_rate * 100, 1),
        "mastered_rate": round(mastered_rate * 100, 1)
    }


def run_comprehensive_analytics(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """运行综合分析

    Args:
        records: 学习记录列表

    Returns:
        综合分析结果
    """
    return {
        "engagement_trend": calculate_engagement_trend(records),
        "patterns": identify_learning_patterns(records),
        "prediction": predict_learning_outcome(records),
        "efficiency": calculate_learning_efficiency(records),
        "topic_distribution": analyze_topic_distribution(records),
        "retention_rate": calculate_retention_rate(records),
        "insights": generate_learning_insights(records),
        "mastery_metrics": calculate_mastery_metrics(records)
    }