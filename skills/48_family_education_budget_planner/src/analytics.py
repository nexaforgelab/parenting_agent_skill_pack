"""Data analytics module for 家庭教育支出规划 Agent."""
from typing import Any, Dict, List
from collections import defaultdict


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


def analyze_spending_patterns(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析支出模式"""
    result = {"category_breakdown": {}, "payment_methods": {}, "avg_transaction": 0, "total": 0}
    if not records:
        return result
    category_totals = defaultdict(float)
    payment_totals = defaultdict(float)
    amounts = []
    for record in records:
        category = record.get("category", "other")
        amount = record.get("amount", 0)
        category_totals[category] += amount
        payment_method = record.get("payment_method", "cash")
        payment_totals[payment_method] += amount
        amounts.append(amount)
    result["category_breakdown"] = dict(category_totals)
    result["payment_methods"] = dict(payment_totals)
    result["total"] = sum(amounts)
    result["avg_transaction"] = sum(amounts) / len(amounts) if amounts else 0
    return result


def detect_budget_issues(records: List[Dict[str, Any]], budget: float) -> List[Dict[str, Any]]:
    """检测预算问题"""
    issues = []
    if not records:
        return issues
    total = sum(r.get("amount", 0) for r in records)
    if total > budget * 1.2:
        issues.append({"type": "overspend", "severity": "critical", "description": f"支出超出预算20%以上", "recommendation": "建议暂停非必要支出"})
    elif total > budget:
        issues.append({"type": "overspend", "severity": "warning", "description": f"支出已超出预算", "recommendation": "注意控制支出"})
    category_totals = defaultdict(float)
    for record in records:
        category_totals[record.get("category", "other")] += record.get("amount", 0)
    for cat, amount in category_totals.items():
        if amount > budget * 0.5:
            issues.append({"type": "category_high", "severity": "warning", "description": f"分类'{cat}'支出过高", "recommendation": f"关注{cat}类别支出"})
    return issues


def aggregate_statistics(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """数据聚合统计"""
    stats = {"total_records": len(records), "total_spending": 0, "avg_transaction": 0, "category_count": {}}
    if not records:
        return stats
    amounts = []
    category_count = defaultdict(int)
    for record in records:
        amounts.append(record.get("amount", 0))
        category_count[record.get("category", "other")] += 1
    stats["total_spending"] = sum(amounts)
    stats["avg_transaction"] = sum(amounts) / len(amounts) if amounts else 0
    stats["category_count"] = dict(category_count)
    return stats


def predict_annual_spending(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """预测年度支出"""
    prediction = {"estimated_annual": 0, "confidence": "low", "basis": ""}
    if not records:
        return prediction
    amounts = [r.get("amount", 0) for r in records]
    total = sum(amounts)
    daily_avg = total / max(len(records), 1)
    prediction["estimated_annual"] = daily_avg * 365
    prediction["confidence"] = "medium" if len(records) >= 10 else "low"
    prediction["basis"] = f"基于{len(records)}条记录估算"
    return prediction


class ContextMemory:
    """上下文记忆类"""
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.expense_history: List[Dict[str, Any]] = []

    def add_record(self, record: Dict[str, Any]) -> None:
        self.expense_history.append(record)
        if len(self.expense_history) > self.max_history:
            self.expense_history.pop(0)

    def learn_from_history(self) -> Dict[str, Any]:
        if not self.expense_history:
            return {}
        patterns = analyze_spending_patterns(self.expense_history)
        return {"patterns": patterns, "total_expenses": len(self.expense_history), "total_amount": patterns.get("total", 0)}

    def get_context_summary(self) -> str:
        if not self.expense_history:
            return "暂无支出记录"
        total = sum(r.get("amount", 0) for r in self.expense_history)
        return f"累计记录 {len(self.expense_history)} 笔，总支出 ¥{total:.2f}"