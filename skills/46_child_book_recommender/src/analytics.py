"""Data analytics module for 儿童图书推荐 Agent.

提供高级数据分析和统计功能，支持阅读模式分析、个性化推荐、异常检测和上下文记忆。
"""
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta, date
from collections import defaultdict, Counter

try:
    from .models import TrendData, Alert, ReadingSession, BookRecommendation
except ImportError:
    from models import TrendData, Alert, ReadingSession, BookRecommendation


def calculate_statistics(values: List[float]) -> Dict[str, float]:
    """计算统计指标

    Args:
        values: 数值列表

    Returns:
        包含统计指标的字典
    """
    if not values:
        return {
            "count": 0,
            "sum": 0,
            "mean": 0,
            "median": 0,
            "std": 0,
            "min": 0,
            "max": 0
        }

    sorted_values = sorted(values)
    n = len(values)
    mean = sum(values) / n

    median = sorted_values[n // 2] if n % 2 == 1 else (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2

    variance = sum((x - mean) ** 2 for x in values) / n
    std = variance ** 0.5

    return {
        "count": n,
        "sum": sum(values),
        "mean": mean,
        "median": median,
        "std": std,
        "min": min(values),
        "max": max(values)
    }


def analyze_reading_patterns(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析阅读模式

    Args:
        records: 阅读记录列表

    Returns:
        阅读模式分析结果
    """
    patterns = {
        "average_session_duration": 0,
        "most_common_session_time": "",
        "reading_time_distribution": {},
        "typical_engagement_level": 0,
        "engagement_variability": 0,
        "preferred_days": [],
        "reading_streak": 0,
        "total_reading_minutes": 0
    }

    if not records:
        return patterns

    durations = []
    engagement_scores = []
    timestamps = []

    for record in records:
        duration = record.get("duration_minutes")
        if duration is not None:
            try:
                durations.append(float(duration))
            except (ValueError, TypeError):
                pass

        engagement = record.get("child_engagement")
        if engagement is not None:
            try:
                engagement_scores.append(float(engagement))
            except (ValueError, TypeError):
                pass

        try:
            if isinstance(record.get("date"), str):
                ts = datetime.fromisoformat(record["date"])
            elif isinstance(record.get("date"), datetime):
                ts = record["date"]
            else:
                continue
            timestamps.append(ts)
        except (ValueError, AttributeError, TypeError):
            continue

    if durations:
        stats = calculate_statistics(durations)
        patterns["average_session_duration"] = stats["mean"]
        patterns["total_reading_minutes"] = stats["sum"]

    if engagement_scores:
        stats = calculate_statistics(engagement_scores)
        patterns["typical_engagement_level"] = stats["mean"]
        patterns["engagement_variability"] = stats["std"]

    hour_counter = Counter()
    weekday_counter = Counter()
    for ts in timestamps:
        hour = ts.hour
        if 6 <= hour < 9:
            hour_counter["早晨"] += 1
        elif 9 <= hour < 12:
            hour_counter["上午"] += 1
        elif 12 <= hour < 14:
            hour_counter["中午"] += 1
        elif 14 <= hour < 18:
            hour_counter["下午"] += 1
        elif 18 <= hour < 21:
            hour_counter["傍晚"] += 1
        else:
            hour_counter["夜间"] += 1

        weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][ts.weekday()]
        weekday_counter[weekday] += 1

    patterns["reading_time_distribution"] = dict(hour_counter)

    if hour_counter:
        patterns["most_common_session_time"] = hour_counter.most_common(1)[0][0]

    if weekday_counter:
        patterns["preferred_days"] = [day for day, _ in weekday_counter.most_common()]

    if len(timestamps) >= 2:
        sorted_ts = sorted(timestamps, reverse=True)
        streak = 1
        max_streak = 1
        for i in range(len(sorted_ts) - 1):
            days_diff = (sorted_ts[i] - sorted_ts[i + 1]).days
            if days_diff == 1:
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 1
        patterns["reading_streak"] = max_streak

    return patterns


def calculate_engagement_indicators(records: List[Dict[str, Any]], child_profile: Dict[str, Any]) -> Dict[str, Any]:
    """计算参与度指标

    Args:
        records: 阅读记录列表
        child_profile: 孩子画像

    Returns:
        参与度指标分析
    """
    indicators = {
        "average_engagement": 0,
        "engagement_trend": "stable",
        "engagement_level": "unknown",
        "concerns": []
    }

    if not records:
        return indicators

    engagement_scores = []
    for record in records:
        engagement = record.get("child_engagement")
        if engagement is not None:
            try:
                engagement_scores.append(float(engagement))
            except (ValueError, TypeError):
                continue

    if not engagement_scores:
        return indicators

    avg_engagement = sum(engagement_scores) / len(engagement_scores)
    indicators["average_engagement"] = avg_engagement

    if avg_engagement >= 4:
        indicators["engagement_level"] = "非常高"
    elif avg_engagement >= 3:
        indicators["engagement_level"] = "正常"
    elif avg_engagement >= 2:
        indicators["engagement_level"] = "偏低"
        indicators["concerns"].append("阅读参与度偏低，建议增加互动")
    else:
        indicators["engagement_level"] = "很低"
        indicators["concerns"].append("阅读参与度很低，需要选择更有吸引力的图书")

    if len(engagement_scores) >= 3:
        recent_avg = sum(engagement_scores[:3]) / min(3, len(engagement_scores))
        earlier_avg = sum(engagement_scores[-3:]) / min(3, len(engagement_scores))

        if recent_avg > earlier_avg + 0.5:
            indicators["engagement_trend"] = "increasing"
        elif recent_avg < earlier_avg - 0.5:
            indicators["engagement_trend"] = "decreasing"
        else:
            indicators["engagement_trend"] = "stable"

    return indicators


def detect_reading_issues(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """检测阅读问题

    Args:
        records: 阅读记录列表

    Returns:
        检测到的问题列表
    """
    issues = []

    if not records:
        return issues

    records_by_date = defaultdict(list)
    for record in records:
        try:
            if isinstance(record.get("date"), str):
                record_date = datetime.fromisoformat(record["date"]).date()
            elif isinstance(record.get("date"), datetime):
                record_date = record["date"].date()
            else:
                continue
            records_by_date[record_date].append(record)
        except (ValueError, AttributeError, TypeError):
            continue

    for date_record, day_records in records_by_date.items():
        total_duration = sum(r.get("duration_minutes", 0) for r in day_records)

        if total_duration > 60:
            issues.append({
                "date": date_record.isoformat(),
                "type": "excessive_reading",
                "severity": "warning",
                "description": f"当天阅读时间过长（{total_duration}分钟）",
                "recommendation": "注意控制阅读时间，避免疲劳"
            })

        if total_duration > 0 and total_duration < 5:
            issues.append({
                "date": date_record.isoformat(),
                "type": "insufficient_reading",
                "severity": "info",
                "description": f"当天阅读时间很短（{total_duration}分钟）",
                "recommendation": "可以适当增加共读时间"
            })

        avg_engagement = sum(r.get("child_engagement", 0) for r in day_records) / len(day_records)
        if avg_engagement < 2:
            issues.append({
                "date": date_record.isoformat(),
                "type": "low_engagement",
                "severity": "warning",
                "description": f"当天阅读参与度偏低（{avg_engagement:.1f}分）",
                "recommendation": "考虑更换图书或增加互动环节"
            })

    return issues


def compare_with_recommendations(
    records: List[Dict[str, Any]],
    recommendations: List[Dict[str, Any]],
    child_profile: Dict[str, Any]
) -> Dict[str, Any]:
    """与推荐标准比较

    Args:
        records: 阅读记录列表
        recommendations: 推荐书目
        child_profile: 孩子画像

    Returns:
        比较结果
    """
    comparison = {
        "reading_frequency": {"actual": 0, "recommended": 0, "status": "unknown"},
        "reading_variety": {"actual": 0, "recommended": 0, "status": "unknown"},
        "engagement_score": {"actual": 0, "recommended": 0, "status": "unknown"},
        "overall_assessment": "unknown"
    }

    if not child_profile:
        return comparison

    age_years = child_profile.get("age_years", 5)

    recommended_frequency = 3
    if age_years < 3:
        recommended_frequency = 5
    elif age_years < 6:
        recommended_frequency = 4
    elif age_years < 10:
        recommended_frequency = 3
    else:
        recommended_frequency = 2

    unique_dates = set()
    for record in records:
        try:
            if isinstance(record.get("date"), str):
                record_date = datetime.fromisoformat(record["date"]).date()
            elif isinstance(record.get("date"), datetime):
                record_date = record["date"].date()
            else:
                continue
            unique_dates.add(record_date)
        except (ValueError, AttributeError, TypeError):
            continue

    weekly_frequency = len(unique_dates) / max(1, len(records) / 7)
    comparison["reading_frequency"]["actual"] = round(weekly_frequency, 1)
    comparison["reading_frequency"]["recommended"] = recommended_frequency

    if weekly_frequency >= recommended_frequency:
        comparison["reading_frequency"]["status"] = "符合标准"
    elif weekly_frequency >= recommended_frequency * 0.7:
        comparison["reading_frequency"]["status"] = "接近标准"
    else:
        comparison["reading_frequency"]["status"] = "低于标准"

    read_books = set()
    for record in records:
        book_title = record.get("book_title", "")
        if book_title:
            read_books.add(book_title)

    recommended_variety = 4
    comparison["reading_variety"]["actual"] = len(read_books)
    comparison["reading_variety"]["recommended"] = recommended_variety

    if len(read_books) >= recommended_variety:
        comparison["reading_variety"]["status"] = "符合标准"
    elif len(read_books) >= recommended_variety * 0.7:
        comparison["reading_variety"]["status"] = "接近标准"
    else:
        comparison["reading_variety"]["status"] = "低于标准"

    engagement_scores = []
    for record in records:
        engagement = record.get("child_engagement")
        if engagement is not None:
            try:
                engagement_scores.append(float(engagement))
            except (ValueError, TypeError):
                continue

    if engagement_scores:
        actual_engagement = sum(engagement_scores) / len(engagement_scores)
        comparison["engagement_score"]["actual"] = round(actual_engagement, 1)
        comparison["engagement_score"]["recommended"] = 3.5

        if actual_engagement >= 3.5:
            comparison["engagement_score"]["status"] = "符合标准"
        elif actual_engagement >= 2.5:
            comparison["engagement_score"]["status"] = "接近标准"
        else:
            comparison["engagement_score"]["status"] = "低于标准"

    frequency_ok = "符合" in comparison["reading_frequency"]["status"]
    variety_ok = "符合" in comparison["reading_variety"]["status"]
    engagement_ok = "符合" in comparison["engagement_score"]["status"]

    if frequency_ok and variety_ok and engagement_ok:
        comparison["overall_assessment"] = "优秀"
    elif sum([frequency_ok, variety_ok, engagement_ok]) >= 2:
        comparison["overall_assessment"] = "良好"
    elif sum([frequency_ok, variety_ok, engagement_ok]) >= 1:
        comparison["overall_assessment"] = "一般"
    else:
        comparison["overall_assessment"] = "需改进"

    return comparison


def generate_reading_insights(
    records: List[Dict[str, Any]],
    trends: List[TrendData],
    child_profile: Dict[str, Any]
) -> List[str]:
    """生成阅读洞察信息

    Args:
        records: 阅读记录列表
        trends: 趋势数据列表
        child_profile: 孩子画像

    Returns:
        洞察信息列表
    """
    insights = []

    if not records:
        return insights

    patterns = analyze_reading_patterns(records)

    if patterns.get("average_session_duration"):
        duration = patterns["average_session_duration"]
        insights.append(f"平均单次阅读时长约 {duration:.0f} 分钟")

    if patterns.get("most_common_session_time"):
        time = patterns["most_common_session_time"]
        insights.append(f"最常在'{time}'时段进行共读")

    if patterns.get("reading_streak"):
        streak = patterns["reading_streak"]
        if streak >= 7:
            insights.append(f"🏆 已连续阅读 {streak} 天，表现优异！")
        elif streak >= 3:
            insights.append(f"📚 当前连续阅读 {streak} 天，继续保持！")

    if patterns.get("preferred_days"):
        days = patterns["preferred_days"]
        if days:
            insights.append(f"偏好阅读日: {', '.join(days[:3])}")

    indicators = calculate_engagement_indicators(records, child_profile)
    if indicators.get("engagement_level"):
        level = indicators["engagement_level"]
        insights.append(f"阅读参与度评估: {level}")

    if trends:
        for trend in trends:
            if trend.trend_direction == "increasing":
                insights.append(f"📈 {trend.metric_name}呈上升趋势（+{trend.trend_percentage:.1f}%）")
            elif trend.trend_direction == "decreasing":
                insights.append(f"📉 {trend.metric_name}呈下降趋势（{trend.trend_percentage:.1f}%）")

    if indicators.get("concerns"):
        for concern in indicators["concerns"]:
            insights.append(f"⚠️ {concern}")

    return insights


def personalize_recommendations(
    child_profile: Dict[str, Any],
    records: List[Dict[str, Any]],
    all_recommendations: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """个性化推荐算法

    Args:
        child_profile: 孩子画像
        records: 阅读记录列表
        all_recommendations: 全部推荐书目

    Returns:
        个性化排序后的推荐列表
    """
    if not all_recommendations:
        return []

    scored_recommendations = []

    for book in all_recommendations:
        score = 0.0
        reasons = []

        age = child_profile.get("age_years", 5)
        age_range = book.get("age_range", "")
        if age_range:
            if f"{age}-" in age_range or (f"{age-1}-" in age_range and age > 0):
                score += 2.0
                reasons.append("年龄适配")
            elif str(age) in age_range:
                score += 1.5
                reasons.append("年龄匹配")

        interests = child_profile.get("interests", [])
        book_themes = book.get("themes", [])
        for interest in interests:
            if any(interest.lower() in theme.lower() for theme in book_themes):
                score += 1.5
                reasons.append(f"匹配兴趣: {interest}")
                break

        educational_value = book.get("educational_value", 3)
        score += (educational_value - 3) * 0.5

        engagement_score = book.get("engagement_score", 3)
        score += (engagement_score - 3) * 0.5

        avg_rating = book.get("average_rating", 0)
        if avg_rating > 4.5:
            score += 1.0
            reasons.append("高分好评")
        elif avg_rating > 4.0:
            score += 0.5

        content_warnings = book.get("content_warnings", [])
        if content_warnings:
            score -= 0.5 * len(content_warnings)

        read_books = set(r.get("book_title", "") for r in records)
        if book.get("title") in read_books:
            score -= 3.0
            reasons.append("已阅读")

        priority = book.get("purchase_priority", 1)
        score += (5 - priority) * 0.3

        scored_recommendations.append({
            "book": book,
            "score": score,
            "reasons": reasons
        })

    scored_recommendations.sort(key=lambda x: x["score"], reverse=True)

    personalized = []
    for item in scored_recommendations:
        book_data = item["book"].copy() if isinstance(item["book"], dict) else item["book"]
        book_data["personalized_score"] = round(item["score"], 2)
        book_data["recommendation_reasons"] = item["reasons"]
        personalized.append(book_data)

    return personalized


def aggregate_statistics(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """数据聚合统计

    Args:
        records: 阅读记录列表

    Returns:
        聚合统计数据
    """
    stats = {
        "total_records": len(records),
        "unique_books_read": 0,
        "total_reading_minutes": 0,
        "average_session_duration": 0,
        "average_engagement": 0,
        "reading_by_day_of_week": {},
        "reading_by_hour": {},
        "theme_distribution": {},
        "completion_rate": 0
    }

    if not records:
        return stats

    unique_books = set()
    total_minutes = 0
    engagement_scores = []
    day_counter = Counter()
    hour_counter = Counter()

    for record in records:
        book_title = record.get("book_title", "")
        if book_title:
            unique_books.add(book_title)

        duration = record.get("duration_minutes", 0)
        if duration:
            total_minutes += duration

        engagement = record.get("child_engagement")
        if engagement is not None:
            try:
                engagement_scores.append(float(engagement))
            except (ValueError, TypeError):
                pass

        try:
            if isinstance(record.get("date"), str):
                record_date = datetime.fromisoformat(record["date"])
            elif isinstance(record.get("date"), datetime):
                record_date = record["date"]
            else:
                continue

            day_name = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][record_date.weekday()]
            day_counter[day_name] += 1
            hour_counter[record_date.hour] += 1
        except (ValueError, AttributeError, TypeError):
            continue

    stats["unique_books_read"] = len(unique_books)
    stats["total_reading_minutes"] = total_minutes
    stats["average_session_duration"] = total_minutes / len(records) if records else 0

    if engagement_scores:
        stats["average_engagement"] = sum(engagement_scores) / len(engagement_scores)

    stats["reading_by_day_of_week"] = dict(day_counter)
    stats["reading_by_hour"] = dict(hour_counter)

    return stats


def predict_optimal_reading_time(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """预测最佳阅读时间

    Args:
        records: 阅读记录列表

    Returns:
        预测结果
    """
    prediction = {
        "recommended_time": None,
        "recommended_duration": 15,
        "confidence": "low",
        "reasoning": ""
    }

    if not records or len(records) < 5:
        prediction["reasoning"] = "历史数据不足"
        return prediction

    hour_counter = Counter()
    engagement_by_hour = defaultdict(list)

    for record in records:
        try:
            if isinstance(record.get("date"), str):
                record_date = datetime.fromisoformat(record["date"])
            elif isinstance(record.get("date"), datetime):
                record_date = record["date"]
            else:
                continue

            hour = record_date.hour
            hour_counter[hour] += 1

            engagement = record.get("child_engagement")
            if engagement is not None:
                try:
                    engagement_by_hour[hour].append(float(engagement))
                except (ValueError, TypeError):
                    pass
        except (ValueError, AttributeError, TypeError):
            continue

    if not hour_counter:
        prediction["reasoning"] = "无法解析时间数据"
        return prediction

    best_hour = hour_counter.most_common(1)[0][0]
    engagement_scores = engagement_by_hour.get(best_hour, [])

    if engagement_scores:
        avg_engagement = sum(engagement_scores) / len(engagement_scores)
        if avg_engagement >= 4:
            prediction["confidence"] = "high"
        elif avg_engagement >= 3:
            prediction["confidence"] = "medium"

    time_slots = {
        range(6, 9): "早晨（6-8点）",
        range(9, 12): "上午（9-11点）",
        range(12, 14): "中午（12-13点）",
        range(14, 18): "下午（14-17点）",
        range(18, 21): "傍晚（18-20点）",
        range(21, 24): "夜间（21-23点）"
    }

    for hour_range, slot_name in time_slots.items():
        if best_hour in hour_range:
            prediction["recommended_time"] = slot_name
            break

    if len(hour_counter) >= 3:
        prediction["reasoning"] = f"基于 {len(records)} 次阅读记录分析"
    else:
        prediction["reasoning"] = "数据量有限，建议结合实际情况调整"

    return prediction


def generate_trend_data(records: List[Dict[str, Any]], metric: str = "engagement") -> List[Dict[str, Any]]:
    """生成趋势数据

    Args:
        records: 阅读记录列表
        metric: 指标类型

    Returns:
        趋势数据点列表
    """
    if not records:
        return []

    sorted_records = sorted(records, key=lambda x: x.get("date", ""))

    if len(sorted_records) < 4:
        return []

    window_size = max(2, len(sorted_records) // 4)
    data_points = []

    for i in range(0, len(sorted_records), window_size):
        window = sorted_records[i:i + window_size]
        if not window:
            continue

        values = []
        for record in window:
            if metric == "engagement":
                val = record.get("child_engagement")
            elif metric == "duration":
                val = record.get("duration_minutes")
            else:
                val = record.get(metric)

            if val is not None:
                try:
                    values.append(float(val))
                except (ValueError, TypeError):
                    continue

        if values:
            avg_value = sum(values) / len(values)
            data_points.append({
                "label": f"阶段{i // window_size + 1}",
                "value": round(avg_value, 2),
                "count": len(values)
            })

    return data_points


def calculate_trend_percentage(data_points: List[Dict[str, Any]]) -> Tuple[str, float]:
    """计算趋势百分比

    Args:
        data_points: 数据点列表

    Returns:
        (趋势方向, 变化百分比) 元组
    """
    if not data_points or len(data_points) < 2:
        return "stable", 0.0

    first_half = data_points[:len(data_points) // 2]
    second_half = data_points[len(data_points) // 2:]

    first_avg = sum(dp.get("value", 0) for dp in first_half) / len(first_half) if first_half else 0
    second_avg = sum(dp.get("value", 0) for dp in second_half) / len(second_half) if second_half else 0

    if first_avg == 0:
        return "stable", 0.0

    percentage = ((second_avg - first_avg) / first_avg) * 100

    if percentage > 5:
        direction = "increasing"
    elif percentage < -5:
        direction = "decreasing"
    else:
        direction = "stable"

    return direction, round(percentage, 2)


class ContextMemory:
    """上下文记忆类"""

    def __init__(self, max_history: int = 100):
        """初始化上下文记忆

        Args:
            max_history: 最大历史记录数
        """
        self.max_history = max_history
        self.reading_history: List[Dict[str, Any]] = []
        self.preferences: Dict[str, Any] = {}
        self.preferred_authors: List[str] = []
        self.preferred_themes: List[str] = []
        self.avoid_themes: List[str] = []

    def add_record(self, record: Dict[str, Any]) -> None:
        """添加阅读记录

        Args:
            record: 阅读记录字典
        """
        self.reading_history.append(record)
        if len(self.reading_history) > self.max_history:
            self.reading_history.pop(0)

    def update_preferences(self, preferences: Dict[str, Any]) -> None:
        """更新偏好设置

        Args:
            preferences: 偏好设置字典
        """
        self.preferences.update(preferences)

    def learn_from_history(self) -> Dict[str, Any]:
        """从历史记录中学习

        Returns:
            学习到的偏好字典
        """
        if not self.reading_history:
            return {}

        author_counter = Counter()
        theme_counter = Counter()

        for record in self.reading_history:
            author = record.get("author", "")
            if author:
                author_counter[author] += 1

            themes = record.get("themes", [])
            if themes:
                for theme in themes:
                    theme_counter[theme] += 1

        self.preferred_authors = [author for author, _ in author_counter.most_common(5)]
        self.preferred_themes = [theme for theme, _ in theme_counter.most_common(5)]

        return {
            "preferred_authors": self.preferred_authors,
            "preferred_themes": self.preferred_themes,
            "total_books_read": len(self.reading_history),
            "unique_authors": len(author_counter),
            "common_themes": list(theme_counter.most_common(3))
        }

    def get_context_summary(self) -> str:
        """获取上下文摘要

        Returns:
            摘要字符串
        """
        if not self.reading_history:
            return "暂无阅读历史"

        total = len(self.reading_history)
        unique = len(set(r.get("book_title", "") for r in self.reading_history))

        summary = f"累计阅读 {total} 次，覆盖 {unique} 本书"

        if self.preferred_themes:
            summary += f"，偏好主题: {', '.join(self.preferred_themes[:3])}"

        if self.preferred_authors:
            summary += f"，常读作者: {', '.join(self.preferred_authors[:3])}"

        return summary