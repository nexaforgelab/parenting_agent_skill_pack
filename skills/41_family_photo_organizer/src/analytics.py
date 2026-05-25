"""Data analytics module for 家庭照片整理 Agent.

提供高级数据分析和统计功能，作为planner.py的补充模块
"""
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta, date
from collections import defaultdict, Counter
from .models import TrendData, Alert


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


def analyze_photo_patterns(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析照片模式

    Args:
        records: 照片记录列表

    Returns:
        照片模式分析结果
    """
    patterns = {
        "average_interval_days": 0,
        "most_common_interval_range": "",
        "shooting_time_distribution": {},
        "typical_photos_per_day": 0,
        "variability": 0
    }

    if not records:
        return patterns

    timestamps = []

    for record in records:
        try:
            if isinstance(record.get("timestamp"), str):
                ts = datetime.fromisoformat(record["timestamp"])
            elif isinstance(record.get("timestamp"), datetime):
                ts = record["timestamp"]
            else:
                continue

            timestamps.append(ts)
        except (ValueError, AttributeError, TypeError):
            continue

    if len(timestamps) >= 2:
        sorted_ts = sorted(timestamps)
        intervals = []
        for i in range(1, len(sorted_ts)):
            diff_days = (sorted_ts[i] - sorted_ts[i-1]).days
            intervals.append(diff_days)

        if intervals:
            patterns["average_interval_days"] = sum(intervals) / len(intervals)

            if patterns["average_interval_days"] < 1:
                patterns["most_common_interval_range"] = "非常频繁（<1天）"
            elif patterns["average_interval_days"] < 3:
                patterns["most_common_interval_range"] = "频繁（1-3天）"
            elif patterns["average_interval_days"] < 7:
                patterns["most_common_interval_range"] = "正常（3-7天）"
            else:
                patterns["most_common_interval_range"] = "较少（>7天）"

            stats = calculate_statistics([float(x) for x in intervals])
            patterns["variability"] = stats["std"]

    records_by_date = defaultdict(int)
    for ts in timestamps:
        records_by_date[ts.date()] += 1

    if records_by_date:
        daily_counts = list(records_by_date.values())
        patterns["typical_photos_per_day"] = sum(daily_counts) / len(daily_counts)

    hour_counter = Counter()
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
            hour_counter["晚上"] += 1
        else:
            hour_counter["深夜"] += 1

    patterns["shooting_time_distribution"] = dict(hour_counter)

    return patterns


def calculate_growth_indicators(records: List[Dict[str, Any]], child_profile: Dict[str, Any]) -> Dict[str, Any]:
    """计算成长指标

    Args:
        records: 照片记录列表
        child_profile: 孩子画像

    Returns:
        成长指标分析
    """
    indicators = {
        "photo_coverage": "unknown",
        "milestone_capture_rate": 0,
        "growth_completeness": 0,
        "concerns": []
    }

    if not records or not child_profile:
        return indicators

    age_months = child_profile.get("age_months", 0)
    age_years = child_profile.get("age", 0)

    if age_months <= 0 and age_years <= 0:
        return indicators

    milestone_events = ["生日", "上学", "毕业", "旅行", "第一次"]
    milestone_count = 0

    for record in records:
        description = record.get("description", "").lower()
        tags = [tag.lower() for tag in record.get("tags", [])]

        for milestone in milestone_events:
            if milestone.lower() in description or any(milestone.lower() in tag for tag in tags):
                milestone_count += 1
                break

    expected_milestones = max(1, age_months // 6)
    indicators["milestone_capture_rate"] = min(100, (milestone_count / expected_milestones) * 100)

    photos_with_location = sum(1 for r in records if r.get("location"))
    location_coverage = (photos_with_location / len(records)) * 100 if records else 0

    photos_with_tags = sum(1 for r in records if r.get("tags"))
    tags_coverage = (photos_with_tags / len(records)) * 100 if records else 0

    indicators["photo_coverage"] = "优秀" if location_coverage > 80 else "良好" if location_coverage > 50 else "一般"

    indicators["growth_completeness"] = (location_coverage + tags_coverage + indicators["milestone_capture_rate"]) / 3

    return indicators


def detect_photo_quality_issues(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """检测照片质量问题

    Args:
        records: 照片记录列表

    Returns:
        检测到的问题列表
    """
    issues = []

    if not records:
        return issues

    quality_counts = Counter()
    for record in records:
        quality = record.get("quality", "good")
        quality_counts[quality] += 1

    total = len(records)

    if quality_counts.get("poor", 0) > total * 0.3:
        issues.append({
            "type": "quality",
            "severity": "warning",
            "description": f"约 {quality_counts['poor'] / total * 100:.0f}% 的照片质量较低",
            "recommendation": "建议提高拍摄技巧或检查设备设置"
        })

    photos_without_tags = sum(1 for r in records if not r.get("tags"))
    if photos_without_tags > total * 0.5:
        issues.append({
            "type": "organization",
            "severity": "info",
            "description": f"约 {photos_without_tags / total * 100:.0f}% 的照片没有标签",
            "recommendation": "建议为照片添加标签以便于分类和检索"
        })

    photos_without_location = sum(1 for r in records if not r.get("location"))
    if photos_without_location > total * 0.7:
        issues.append({
            "type": "metadata",
            "severity": "info",
            "description": f"约 {photos_without_location / total * 100:.0f}% 的照片没有位置信息",
            "recommendation": "建议开启地理位置标记功能"
        })

    photos_without_desc = sum(1 for r in records if not r.get("description"))
    if photos_without_desc > total * 0.8:
        issues.append({
            "type": "documentation",
            "severity": "info",
            "description": f"约 {photos_without_desc / total * 100:.0f}% 的照片没有描述",
            "recommendation": "建议为重要照片添加简短描述"
        })

    return issues


def compare_photo_years(
    records: List[Dict[str, Any]],
    child_profile: Dict[str, Any]
) -> Dict[str, Any]:
    """按年比较照片

    Args:
        records: 照片记录列表
        child_profile: 孩子画像

    Returns:
        年度比较结果
    """
    comparison = {
        "photos_by_year": {},
        "growth_trend": {},
        "overall_assessment": "unknown"
    }

    if not records:
        return comparison

    photos_by_year = defaultdict(int)
    favorites_by_year = defaultdict(int)

    for record in records:
        try:
            if isinstance(record.get("timestamp"), str):
                ts = datetime.fromisoformat(record["timestamp"])
            elif isinstance(record.get("timestamp"), datetime):
                ts = record["timestamp"]
            else:
                continue

            year = ts.year
            photos_by_year[year] += 1

            if record.get("is_favorite", False):
                favorites_by_year[year] += 1
        except (ValueError, AttributeError):
            continue

    comparison["photos_by_year"] = dict(photos_by_year)

    sorted_years = sorted(photos_by_year.keys())
    if len(sorted_years) >= 2:
        year_counts = [(year, photos_by_year[year]) for year in sorted_years]
        first_year = year_counts[0]
        last_year = year_counts[-1]

        if last_year[1] > first_year[1]:
            growth_rate = ((last_year[1] - first_year[1]) / first_year[1]) * 100
            comparison["growth_trend"] = {
                "direction": "increasing",
                "rate": growth_rate,
                "first_year": first_year[0],
                "last_year": last_year[0]
            }
        elif last_year[1] < first_year[1]:
            growth_rate = ((first_year[1] - last_year[1]) / first_year[1]) * 100
            comparison["growth_trend"] = {
                "direction": "decreasing",
                "rate": growth_rate,
                "first_year": first_year[0],
                "last_year": last_year[0]
            }
        else:
            comparison["growth_trend"] = {
                "direction": "stable",
                "rate": 0,
                "first_year": first_year[0],
                "last_year": last_year[0]
            }

    comparison["overall_assessment"] = "记录丰富" if len(photos_by_year) >= 3 else "记录一般"

    return comparison


def generate_photo_insights(
    records: List[Dict[str, Any]],
    trends: List[TrendData],
    child_profile: Dict[str, Any]
) -> List[str]:
    """生成照片洞察信息

    Args:
        records: 照片记录列表
        trends: 趋势数据列表
        child_profile: 孩子画像

    Returns:
        洞察信息列表
    """
    insights = []

    if not records:
        return insights

    patterns = analyze_photo_patterns(records)

    if patterns.get("average_interval_days"):
        interval = patterns["average_interval_days"]
        if interval < 1:
            insights.append(f"照片拍摄非常频繁（平均间隔{interval:.1f}天），建议关注拍摄质量而非数量")
        elif interval > 7:
            insights.append(f"照片拍摄间隔较长（平均{interval:.1f}天），建议更频繁地记录精彩时刻")
        else:
            insights.append(f"照片拍摄节奏适中（平均{interval:.1f}天）")

    time_dist = patterns.get("shooting_time_distribution", {})
    if time_dist:
        most_common_time = max(time_dist.items(), key=lambda x: x[1])[0] if time_dist else None
        if most_common_time:
            insights.append(f"您最常在'{most_common_time}'时段拍摄照片")

    if trends:
        for trend in trends:
            if trend.trend_direction == "increasing":
                insights.append(f"{trend.metric_name}呈上升趋势（+{trend.trend_percentage:.1f}%）")
            elif trend.trend_direction == "decreasing":
                insights.append(f"{trend.metric_name}呈下降趋势（{trend.trend_percentage:.1f}%）")

    indicators = calculate_growth_indicators(records, child_profile)
    if indicators.get("photo_coverage"):
        insights.append(f"照片覆盖率评估：{indicators['photo_coverage']}")

    if indicators.get("concerns"):
        for concern in indicators["concerns"]:
            insights.append(f"⚠️ {concern}")

    return insights


def predict_photo_activity(
    records: List[Dict[str, Any]],
    last_activity_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """预测照片活动趋势

    Args:
        records: 照片记录列表
        last_activity_date: 最后活动日期

    Returns:
        预测结果
    """
    prediction = {
        "recommended_activity": None,
        "confidence": "low",
        "reasoning": ""
    }

    if not records:
        prediction["reasoning"] = "没有足够的历史数据"
        return prediction

    timestamps = []
    for record in records:
        try:
            if isinstance(record.get("timestamp"), str):
                ts = datetime.fromisoformat(record["timestamp"])
            elif isinstance(record.get("timestamp"), datetime):
                ts = record["timestamp"]
            else:
                continue
            timestamps.append(ts)
        except (ValueError, AttributeError):
            continue

    if not timestamps:
        prediction["reasoning"] = "无法解析时间戳"
        return prediction

    sorted_ts = sorted(timestamps, reverse=True)
    latest = sorted_ts[0]

    days_since_last = (datetime.now() - latest).days

    if days_since_last > 7:
        prediction["recommended_activity"] = "整理照片"
        prediction["confidence"] = "high"
        prediction["reasoning"] = f"已经{days_since_last}天没有拍摄新照片，建议整理现有照片或拍摄新照片"
    elif days_since_last > 3:
        prediction["recommended_activity"] = "继续记录"
        prediction["confidence"] = "medium"
        prediction["reasoning"] = f"已经{days_since_last}天没有拍摄新照片"
    else:
        prediction["recommended_activity"] = "保持节奏"
        prediction["confidence"] = "high"
        prediction["reasoning"] = "照片拍摄节奏良好，继续保持"

    prediction["days_since_last_activity"] = days_since_last
    prediction["latest_activity_date"] = latest.isoformat()

    return prediction
