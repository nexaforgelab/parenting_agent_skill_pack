"""Data analytics module for 新生儿喂养记录 Agent.

提供高级数据分析和统计功能
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


def analyze_feeding_patterns(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析喂养模式

    Args:
        records: 喂养记录列表

    Returns:
        喂养模式分析结果
    """
    patterns = {
        "average_interval_hours": 0,
        "most_common_interval_range": "",
        "feeding_time_distribution": {},
        "typical_feeding_amount": 0,
        "amount_variability": 0
    }

    if not records:
        return patterns

    timestamps = []
    amounts = []

    for record in records:
        try:
            if isinstance(record.get("timestamp"), str):
                ts = datetime.fromisoformat(record["timestamp"])
            elif isinstance(record.get("timestamp"), datetime):
                ts = record["timestamp"]
            else:
                continue

            timestamps.append(ts)

            amount = record.get("amount_ml")
            if amount is not None:
                amounts.append(float(amount))
        except (ValueError, AttributeError, TypeError):
            continue

    if len(timestamps) >= 2:
        sorted_ts = sorted(timestamps)
        intervals = []
        for i in range(1, len(sorted_ts)):
            diff_hours = (sorted_ts[i] - sorted_ts[i-1]).total_seconds() / 3600
            intervals.append(diff_hours)

        if intervals:
            patterns["average_interval_hours"] = sum(intervals) / len(intervals)

            if patterns["average_interval_hours"] < 2:
                patterns["most_common_interval_range"] = "频繁（<2小时）"
            elif patterns["average_interval_hours"] < 3:
                patterns["most_common_interval_range"] = "正常（2-3小时）"
            elif patterns["average_interval_hours"] < 4:
                patterns["most_common_interval_range"] = "较长（3-4小时）"
            else:
                patterns["most_common_interval_range"] = "很长（>4小时）"

            stats = calculate_statistics(intervals)
            patterns["interval_std"] = stats["std"]

    if amounts:
        stats = calculate_statistics(amounts)
        patterns["typical_feeding_amount"] = stats["mean"]
        patterns["amount_variability"] = stats["std"]

        patterns["amount_distribution"] = {
            "min": stats["min"],
            "max": stats["max"],
            "median": stats["median"]
        }

    hour_counter = Counter()
    for ts in timestamps:
        hour = ts.hour
        if 5 <= hour < 9:
            hour_counter["凌晨"] += 1
        elif 9 <= hour < 12:
            hour_counter["上午"] += 1
        elif 12 <= hour < 14:
            hour_counter["中午"] += 1
        elif 14 <= hour < 18:
            hour_counter["下午"] += 1
        elif 18 <= hour < 22:
            hour_counter["晚上"] += 1
        else:
            hour_counter["深夜"] += 1

    patterns["feeding_time_distribution"] = dict(hour_counter)

    return patterns


def calculate_growth_indicators(records: List[Dict[str, Any]], child_profile: Dict[str, Any]) -> Dict[str, Any]:
    """计算生长指标

    Args:
        records: 喂养记录列表
        child_profile: 孩子画像

    Returns:
        生长指标分析
    """
    indicators = {
        "is_gaining_weight": False,
        "growth_rate": "unknown",
        "feeding_adequacy": "unknown",
        "concerns": []
    }

    if not records or not child_profile:
        return indicators

    weight_kg = child_profile.get("weight_kg", 0)
    age_months = child_profile.get("age_months", 0)

    if weight_kg <= 0 or age_months <= 0:
        return indicators

    total_amount = 0
    count = 0
    for record in records:
        amount = record.get("amount_ml")
        if amount is not None:
            total_amount += float(amount)
            count += 1

    if count == 0:
        return indicators

    avg_daily_amount = total_amount / 7

    recommended_amount = 0
    if age_months <= 1:
        recommended_amount = weight_kg * 150
    elif age_months <= 3:
        recommended_amount = weight_kg * 130
    elif age_months <= 6:
        recommended_amount = weight_kg * 120

    if recommended_amount > 0:
        ratio = avg_daily_amount / recommended_amount
        if ratio >= 0.9:
            indicators["feeding_adequacy"] = "充足"
        elif ratio >= 0.7:
            indicators["feeding_adequacy"] = "基本充足"
        elif ratio >= 0.5:
            indicators["feeding_adequacy"] = "不足"
            indicators["concerns"].append("喂养量低于推荐值的70%")
        else:
            indicators["feeding_adequacy"] = "严重不足"
            indicators["concerns"].append("喂养量严重低于推荐值，建议咨询医生")

    return indicators


def detect_feeding_issues(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """检测喂养问题

    Args:
        records: 喂养记录列表

    Returns:
        检测到的问题列表
    """
    issues = []

    if not records:
        return issues

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
        except (ValueError, AttributeError, TypeError):
            continue

    for date_record, day_records in records_by_date.items():
        count = len(day_records)

        if count > 12:
            issues.append({
                "date": date_record.isoformat(),
                "type": "overfeeding",
                "severity": "warning",
                "description": f"当天喂养次数异常多（{count}次）",
                "recommendation": "注意观察宝宝是否过度喂养"
            })

        if count < 4 and count > 0:
            issues.append({
                "date": date_record.isoformat(),
                "type": "underfeeding",
                "severity": "warning",
                "description": f"当天喂养次数较少（{count}次）",
                "recommendation": "确保宝宝摄入足够营养"
            })

        for record in day_records:
            amount = record.get("amount_ml")
            if amount is not None:
                amount = float(amount)
                if amount > 300:
                    issues.append({
                        "date": date_record.isoformat(),
                        "type": "large_amount",
                        "severity": "info",
                        "description": f"单次喂养量较大（{amount}ml）",
                        "recommendation": "观察宝宝消化情况"
                    })

    return issues


def compare_with_standards(
    records: List[Dict[str, Any]],
    child_profile: Dict[str, Any]
) -> Dict[str, Any]:
    """与标准值比较

    Args:
        records: 喂养记录列表
        child_profile: 孩子画像

    Returns:
        比较结果
    """
    comparison = {
        "feeding_frequency": {"actual": 0, "recommended": 0, "status": "unknown"},
        "feeding_amount": {"actual": 0, "recommended": 0, "status": "unknown"},
        "overall_assessment": "unknown"
    }

    if not records or not child_profile:
        return comparison

    age_months = child_profile.get("age_months", 0)
    weight_kg = child_profile.get("weight_kg", 0)

    recommended_frequency = 0
    if age_months <= 1:
        recommended_frequency = 8
    elif age_months <= 3:
        recommended_frequency = 6
    elif age_months <= 6:
        recommended_frequency = 5

    total_feedings = len(records)
    daily_avg = total_feedings / 7

    comparison["feeding_frequency"]["actual"] = round(daily_avg, 1)
    comparison["feeding_frequency"]["recommended"] = recommended_frequency

    if daily_avg >= recommended_frequency:
        comparison["feeding_frequency"]["status"] = "符合标准"
    elif daily_avg >= recommended_frequency * 0.8:
        comparison["feeding_frequency"]["status"] = "接近标准"
    else:
        comparison["feeding_frequency"]["status"] = "低于标准"

    total_amount = sum(r.get("amount_ml", 0) or 0 for r in records)
    weekly_amount = total_amount
    recommended_weekly = 0

    if weight_kg > 0:
        if age_months <= 1:
            recommended_weekly = weight_kg * 150 * 7
        elif age_months <= 3:
            recommended_weekly = weight_kg * 130 * 7
        elif age_months <= 6:
            recommended_weekly = weight_kg * 120 * 7

    comparison["feeding_amount"]["actual"] = round(weekly_amount, 1)
    comparison["feeding_amount"]["recommended"] = round(recommended_weekly, 1)

    if recommended_weekly > 0:
        ratio = weekly_amount / recommended_weekly
        if ratio >= 0.9:
            comparison["feeding_amount"]["status"] = "符合标准"
        elif ratio >= 0.7:
            comparison["feeding_amount"]["status"] = "接近标准"
        else:
            comparison["feeding_amount"]["status"] = "低于标准"

    frequency_ok = "符合" in comparison["feeding_frequency"]["status"]
    amount_ok = "符合" in comparison["feeding_amount"]["status"]

    if frequency_ok and amount_ok:
        comparison["overall_assessment"] = "优秀"
    elif frequency_ok or amount_ok:
        comparison["overall_assessment"] = "良好"
    else:
        comparison["overall_assessment"] = "需改进"

    return comparison


def generate_insights(
    records: List[Dict[str, Any]],
    trends: List[TrendData],
    child_profile: Dict[str, Any]
) -> List[str]:
    """生成洞察信息

    Args:
        records: 喂养记录列表
        trends: 趋势数据列表
        child_profile: 孩子画像

    Returns:
        洞察信息列表
    """
    insights = []

    if not records:
        return insights

    patterns = analyze_feeding_patterns(records)

    if patterns.get("average_interval_hours"):
        interval = patterns["average_interval_hours"]
        if interval < 2:
            insights.append(f"宝宝喂养间隔较短（平均{interval:.1f}小时），建议观察是否因为摄入量不足")
        elif interval > 4:
            insights.append(f"宝宝喂养间隔较长（平均{interval:.1f}小时），建议确保单次摄入量充足")
        else:
            insights.append(f"宝宝的喂养间隔正常（平均{interval:.1f}小时）")

    if patterns.get("typical_feeding_amount"):
        amount = patterns["typical_feeding_amount"]
        insights.append(f"单次平均喂养量约 {amount:.0f}ml")

    time_dist = patterns.get("feeding_time_distribution", {})
    if time_dist:
        most_common_time = max(time_dist.items(), key=lambda x: x[1])[0] if time_dist else None
        if most_common_time:
            insights.append(f"宝宝在'{most_common_time}'时段喂养最频繁")

    if trends:
        for trend in trends:
            if trend.trend_direction == "increasing":
                insights.append(f"{trend.metric_name}呈上升趋势（+{trend.trend_percentage:.1f}%）")
            elif trend.trend_direction == "decreasing":
                insights.append(f"{trend.metric_name}呈下降趋势（{trend.trend_percentage:.1f}%）")

    indicators = calculate_growth_indicators(records, child_profile)
    if indicators.get("feeding_adequacy"):
        insights.append(f"喂养充足性评估：{indicators['feeding_adequacy']}")

    if indicators.get("concerns"):
        for concern in indicators["concerns"]:
            insights.append(f"⚠️ {concern}")

    return insights


def predict_next_feeding(
    records: List[Dict[str, Any]],
    last_feeding_time: Optional[datetime] = None
) -> Dict[str, Any]:
    """预测下次喂养时间

    Args:
        records: 喂养记录列表
        last_feeding_time: 最后喂养时间

    Returns:
        预测结果
    """
    prediction = {
        "recommended_time": None,
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

    if len(sorted_ts) >= 2:
        intervals = []
        for i in range(min(5, len(sorted_ts) - 1)):
            diff = (sorted_ts[i] - sorted_ts[i+1]).total_seconds() / 3600
            intervals.append(diff)

        avg_interval = sum(intervals) / len(intervals)
        prediction["recommended_time"] = (latest + timedelta(hours=avg_interval)).isoformat()
        prediction["confidence"] = "high" if len(intervals) >= 3 else "medium"
        prediction["reasoning"] = f"基于最近{len(intervals)}次喂养的平均间隔（{avg_interval:.1f}小时）"
    else:
        prediction["reasoning"] = "历史数据不足，使用默认间隔"
        prediction["recommended_time"] = (latest + timedelta(hours=3)).isoformat()

    if last_feeding_time:
        time_since = (datetime.now() - last_feeding_time).total_seconds() / 3600
        prediction["hours_since_last_feeding"] = round(time_since, 1)

        if prediction["recommended_time"]:
            recommended_dt = datetime.fromisoformat(prediction["recommended_time"])
            current_time = datetime.now()
            if current_time >= recommended_dt:
                prediction["suggestion"] = "建议现在喂养"
            else:
                hours_until = (recommended_dt - current_time).total_seconds() / 3600
                prediction["suggestion"] = f"建议{hours_until:.1f}小时后喂养"

    return prediction
