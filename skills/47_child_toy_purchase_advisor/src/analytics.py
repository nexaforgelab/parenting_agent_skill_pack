"""Data analytics module for 儿童玩具选购 Agent."""
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, date
from collections import Counter, defaultdict


def calculate_statistics(values: List[float]) -> Dict[str, float]:
    """计算统计指标"""
    if not values:
        return {"count": 0, "sum": 0, "mean": 0, "median": 0, "std": 0, "min": 0, "max": 0}
    sorted_values = sorted(values)
    n = len(values)
    mean = sum(values) / n
    median = sorted_values[n // 2] if n % 2 == 1 else (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
    variance = sum((x - mean) ** 2 for x in values) / n
    return {"count": n, "sum": sum(values), "mean": mean, "median": median, "std": variance ** 0.5, "min": min(values), "max": max(values)}


def analyze_toy_preferences(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析玩具偏好"""
    result = {"favorite_toys": [], "most_used_categories": [], "avg_engagement": 0, "engagement_trend": "stable"}
    if not records:
        return result
    toy_counter = Counter()
    category_counter = Counter()
    engagements = []
    for record in records:
        toy_name = record.get("toy_name", "")
        if toy_name:
            toy_counter[toy_name] += 1
        category = record.get("category", "")
        if category:
            category_counter[category] += 1
        engagement = record.get("child_engagement")
        if engagement is not None:
            try:
                engagements.append(float(engagement))
            except (ValueError, TypeError):
                pass
    result["favorite_toys"] = [toy for toy, _ in toy_counter.most_common(5)]
    result["most_used_categories"] = [cat for cat, _ in category_counter.most_common(3)]
    if engagements:
        result["avg_engagement"] = sum(engagements) / len(engagements)
    return result


def detect_toy_issues(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """检测玩具使用问题"""
    issues = []
    if not records:
        return issues
    toy_usage = defaultdict(list)
    for record in records:
        toy_name = record.get("toy_name", "")
        if toy_name:
            toy_usage[toy_name].append(record)
    for toy_name, usages in toy_usage.items():
        if len(usages) > 10:
            low_engagement_count = sum(1 for u in usages if u.get("child_engagement", 5) < 2)
            if low_engagement_count > len(usages) * 0.5:
                issues.append({"type": "low_engagement", "severity": "warning", "description": f"玩具'{toy_name}'使用频率高但参与度低", "recommendation": "考虑更换或增加互动方式"})
        if len(usages) == 1:
            issues.append({"type": "single_use", "severity": "info", "description": f"玩具'{toy_name}'仅使用过一次", "recommendation": "观察孩子兴趣是否已转移"})
    return issues


def aggregate_statistics(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """数据聚合统计"""
    stats = {"total_records": len(records), "unique_toys": 0, "total_usage_minutes": 0, "avg_engagement": 0, "category_distribution": {}}
    if not records:
        return stats
    unique_toys = set()
    total_minutes = 0
    engagements = []
    category_counter = Counter()
    for record in records:
        toy_name = record.get("toy_name", "")
        if toy_name:
            unique_toys.add(toy_name)
        duration = record.get("duration_minutes", 0)
        if duration:
            total_minutes += duration
        engagement = record.get("child_engagement")
        if engagement is not None:
            try:
                engagements.append(float(engagement))
            except (ValueError, TypeError):
                pass
        category = record.get("category", "")
        if category:
            category_counter[category] += 1
    stats["unique_toys"] = len(unique_toys)
    stats["total_usage_minutes"] = total_minutes
    if engagements:
        stats["avg_engagement"] = sum(engagements) / len(engagements)
    stats["category_distribution"] = dict(category_counter)
    return stats


def personalize_recommendations(child_profile: Dict[str, Any], records: List[Dict[str, Any]], all_recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """个性化推荐"""
    if not all_recommendations:
        return []
    existing_toys = set(child_profile.get("existing_toys", []))
    interests = child_profile.get("interests", [])
    scored = []
    for toy in all_recommendations:
        score = 0.0
        if toy.get("name") in existing_toys:
            score -= 2.0
        toy_themes = toy.get("themes", [])
        for interest in interests:
            if any(interest.lower() in str(theme).lower() for theme in toy_themes):
                score += 1.5
                break
        score += (toy.get("educational_value", 3) - 3) * 0.3
        score += (toy.get("engagement_score", 3) - 3) * 0.3
        score += (5 - toy.get("purchase_priority", 1)) * 0.2
        scored.append({"toy": toy, "score": score})
    scored.sort(key=lambda x: x["score"], reverse=True)
    result = []
    for item in scored:
        toy_data = item["toy"].copy() if isinstance(item["toy"], dict) else item["toy"]
        toy_data["personalized_score"] = round(item["score"], 2)
        result.append(toy_data)
    return result


class ContextMemory:
    """上下文记忆类"""
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.toy_history: List[Dict[str, Any]] = []
        self.preferred_categories: List[str] = []
        self.favorite_brands: List[str] = []

    def add_record(self, record: Dict[str, Any]) -> None:
        self.toy_history.append(record)
        if len(self.toy_history) > self.max_history:
            self.toy_history.pop(0)

    def learn_from_history(self) -> Dict[str, Any]:
        if not self.toy_history:
            return {}
        category_counter = Counter()
        brand_counter = Counter()
        for record in self.toy_history:
            category = record.get("category", "")
            if category:
                category_counter[category] += 1
            brand = record.get("brand", "")
            if brand:
                brand_counter[brand] += 1
        self.preferred_categories = [cat for cat, _ in category_counter.most_common(5)]
        self.favorite_brands = [brand for brand, _ in brand_counter.most_common(5)]
        return {"preferred_categories": self.preferred_categories, "favorite_brands": self.favorite_brands, "total_usage": len(self.toy_history)}

    def get_context_summary(self) -> str:
        if not self.toy_history:
            return "暂无玩具使用历史"
        return f"累计使用 {len(self.toy_history)} 次，覆盖 {len(set(r.get('toy_name', '') for r in self.toy_history))} 件玩具"