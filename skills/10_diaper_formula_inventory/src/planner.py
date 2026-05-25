"""Planning engine for 尿布奶粉库存 Agent.

提供数据分析、异常检测、个性化推荐、上下文记忆和数据聚合统计功能。
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

SKILL_FLOW = [
    '输入库存数量',
    '记录每日消耗',
    '预测剩余天数',
    '到阈值提醒购买',
    '生成电商比价清单'
]

SAFETY_NOTES = [
    '本 Skill 提供家庭教育和生活管理建议，不替代专业人士意见。',
    '涉及安全、法律、医疗、财务或教育政策时，应提示家长二次核验。',
    '输出应尊重家庭差异，不用单一标准评价孩子或父母。'
]

DEFAULT_DELIVERABLES = [
    '库存表',
    '购买提醒',
    '月度消耗统计'
]

ALERT_THRESHOLDS = {
    "diaper_low_stock": 20,
    "formula_low_stock": 3,
    "days_until_empty_warning": 7
}


def analyze_inventory(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析库存状态."""
    if not records:
        return {
            "total_items": 0,
            "low_stock_items": [],
            "total_value": 0.0
        }

    low_stock = []
    total_items = 0

    for record in records:
        quantity = record.get("current_quantity", 0)
        threshold = record.get("low_stock_threshold", 10)
        total_items += quantity

        if quantity <= threshold:
            low_stock.append({
                "item": record.get("item_name", "未知"),
                "quantity": quantity,
                "threshold": threshold,
                "urgency": "high" if quantity <= threshold * 0.5 else "medium"
            })

    return {
        "total_items": total_items,
        "low_stock_items": low_stock,
        "low_stock_count": len(low_stock)
    }


def predict_consumption(records: List[Dict[str, Any]], days: int = 30) -> Dict[str, Any]:
    """预测消耗趋势."""
    if not records:
        return {"predictions": {}, "average_daily": {}}

    predictions = {}
    avg_daily = {}

    consumption = {}
    for record in records:
        item = record.get("item_name", "未知")
        quantity = record.get("quantity", 0)
        consumption[item] = consumption.get(item, 0) + quantity

    for item, total in consumption.items():
        avg_per_day = total / max(days, 1)
        avg_daily[item] = round(avg_per_day, 2)

    return {
        "predictions": predictions,
        "average_daily": avg_daily
    }


def generate_purchase_reminders(inventory: Dict[str, Any]) -> List[str]:
    """生成购买提醒."""
    reminders = []

    low_stock = inventory.get("low_stock_items", [])
    if low_stock:
        reminders.append("🚨 **库存不足提醒**：")
        for item in low_stock:
            urgency_icon = "⚠️" if item.get("urgency") == "high" else "📢"
            reminders.append(f"  {urgency_icon} {item['item']}：剩余 {item['quantity']} {item.get('unit', '件')}")

    return reminders


def build_known_facts(payload: Dict[str, Any]) -> List[str]:
    """构建已知事实列表."""
    facts: List[str] = []
    child = payload.get("child_profile", {})
    family = payload.get("family_context", {})

    if child:
        facts.append(f"孩子画像：{child.get('name', '未命名')}，")
        birth_date = child.get("birth_date", "")
        if birth_date:
            try:
                birth = datetime.strptime(birth_date, "%Y-%m-%d")
                today = datetime.now()
                months = (today.year - birth.year) * 12 + (today.month - birth.month)
                facts.append(f"  - 月龄：{months} 个月")
            except ValueError:
                pass

    if family:
        facts.append(f"家庭上下文：")
        for key, value in family.items():
            facts.append(f"  - {key}：{value}")

    if payload.get("goal"):
        facts.append(f"目标：{payload.get('goal')}")

    records = payload.get("raw_records") or []
    facts.append(f"已收到 {len(records)} 条库存记录。")

    if records:
        inventory = analyze_inventory(records)
        facts.append(f"物品总数：{inventory['total_items']}")
        if inventory['low_stock_count'] > 0:
            facts.append(f"库存不足物品：{inventory['low_stock_count']} 种")

    return facts


def build_analysis(payload: Dict[str, Any]) -> List[str]:
    """构建分析结果."""
    problem = payload.get("current_problem", "")
    records = payload.get("raw_records", [])

    analysis = [
        f"当前问题聚焦：{problem}",
        "本 Skill 会优先输出可执行动作、记录字段和复盘指标。"
    ]

    for step in SKILL_FLOW:
        analysis.append(f"链路节点：{step}")

    if records:
        analysis.append("\n📊 库存分析：")
        inventory = analyze_inventory(records)
        analysis.append(f"  - 物品总数：{inventory['total_items']}")

        if inventory['low_stock_items']:
            analysis.append(f"\n⚠️ 库存不足：{inventory['low_stock_count']} 种")
            for item in inventory['low_stock_items'][:3]:
                analysis.append(f"  - {item['item']}：{item['quantity']} {item.get('unit', '件')}")

        predictions = predict_consumption(records)
        if predictions['average_daily']:
            analysis.append(f"\n📈 日均消耗：")
            for item, avg in list(predictions['average_daily'].items())[:3]:
                analysis.append(f"  - {item}：{avg}")

    return analysis


def build_action_plan(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """构建行动计划."""
    base_tasks = [
        "记录当前库存数量",
        "设置库存预警阈值",
        "记录每日消耗",
        "生成购买清单",
        "设置定期提醒"
    ]

    plan: List[Dict[str, str]] = []
    for i, task in enumerate(base_tasks, start=1):
        plan.append({
            "day": f"D{i}",
            "task": task,
            "owner": "家长/主要照护人",
            "evidence_to_record": "日期、物品名称、数量、单位",
            "difficulty": "低"
        })
    return plan


def build_deliverables(payload: Dict[str, Any]) -> Dict[str, Any]:
    """构建交付物清单."""
    return {
        "required": DEFAULT_DELIVERABLES,
        "tables": {
            "inventory": ["物品名称", "当前库存", "单位", "预警阈值", "状态"],
            "consumption": ["日期", "物品名称", "消耗数量", "备注"]
        },
        "templates": {
            "inventory_record": "日期：[日期]\n物品：[名称]\n数量：[X]\n单位：[件/罐/包]\n备注：[补充]",
            "purchase_list": "购买清单：\n1. [物品1] - [数量]\n2. [物品2] - [数量]"
        }
    }


def next_fields() -> List[str]:
    """获取下次追踪字段列表."""
    return [
        "最新库存数量",
        "消耗记录",
        "购买计划",
        "需要补充的物品",
        "其他备注"
    ]
