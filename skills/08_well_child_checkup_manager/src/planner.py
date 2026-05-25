"""Planning engine for 宝宝体检记录管理 Agent.

提供数据分析、异常检测、个性化推荐、上下文记忆和数据聚合统计功能。
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

SKILL_FLOW = [
    '上传体检单/手动输入身高体重头围',
    '自动归档',
    '生成成长曲线',
    '标记变化趋势',
    '生成下次体检问题清单'
]

SAFETY_NOTES = [
    '本 Skill 只做家庭记录、观察整理、提醒和沟通材料准备，不提供诊断、治疗方案或用药建议。',
    '出现呼吸困难、持续高热、严重过敏反应、精神状态异常、脱水、剧烈呕吐/腹泻、外伤等情况时，必须提示立即联系医生或急救。',
    '所有月龄、疫苗、营养、睡眠建议都应标注为一般性参考，并要求家长以当地儿科医生/公卫机构建议为准。'
]

DEFAULT_DELIVERABLES = [
    '成长曲线',
    '体检档案',
    '医生沟通清单'
]

ALERT_THRESHOLDS = {
    "height_change_concern": 0.5,
    "weight_change_concern": 0.3,
    "percentile_drop": 10
}


def calculate_child_age(birth_date: str) -> int:
    """计算孩子当前月龄."""
    try:
        birth = datetime.strptime(birth_date, "%Y-%m-%d")
        today = datetime.now()
        months = (today.year - birth.year) * 12 + (today.month - birth.month)
        if today.day < birth.day:
            months -= 1
        return max(0, months)
    except (ValueError, TypeError):
        return 0


def analyze_growth_data(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析生长数据."""
    if not records:
        return {
            "total_records": 0,
            "avg_height": 0.0,
            "avg_weight": 0.0,
            "height_trend": "无数据",
            "weight_trend": "无数据"
        }

    heights = [r.get("height_cm") for r in records if r.get("height_cm") is not None]
    weights = [r.get("weight_kg") for r in records if r.get("weight_kg") is not None]

    avg_height = sum(heights) / len(heights) if heights else 0.0
    avg_weight = sum(weights) / len(weights) if weights else 0.0

    height_trend = "稳定"
    weight_trend = "稳定"

    if len(heights) >= 2:
        if heights[-1] - heights[0] > 2:
            height_trend = "上升"
        elif heights[-1] - heights[0] < -2:
            height_trend = "下降"

    if len(weights) >= 2:
        if weights[-1] - weights[0] > 1:
            weight_trend = "上升"
        elif weights[-1] - weights[0] < -1:
            weight_trend = "下降"

    return {
        "total_records": len(records),
        "avg_height": round(avg_height, 2),
        "avg_weight": round(avg_weight, 2),
        "height_trend": height_trend,
        "weight_trend": weight_trend,
        "latest_height": heights[-1] if heights else None,
        "latest_weight": weights[-1] if weights else None
    }


def detect_growth_anomalies(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """检测生长异常."""
    anomalies = []

    for i in range(1, len(records)):
        prev = records[i-1]
        curr = records[i]

        if prev.get("height_cm") and curr.get("height_cm"):
            height_change = abs(curr["height_cm"] - prev["height_cm"])
            if height_change > ALERT_THRESHOLDS["height_change_concern"] * 3:
                anomalies.append({
                    "type": "身高异常变化",
                    "from_date": prev.get("date", ""),
                    "to_date": curr.get("date", ""),
                    "change": height_change,
                    "message": f"身高在短期内变化 {height_change:.1f}cm，可能需要关注"
                })

        if prev.get("weight_kg") and curr.get("weight_kg"):
            weight_change = abs(curr["weight_kg"] - prev["weight_kg"])
            if weight_change > ALERT_THRESHOLDS["weight_change_concern"] * 2:
                anomalies.append({
                    "type": "体重异常变化",
                    "from_date": prev.get("date", ""),
                    "to_date": curr.get("date", ""),
                    "change": weight_change,
                    "message": f"体重在短期内变化 {weight_change:.1f}kg，可能需要关注"
                })

    return anomalies


def generate_growth_recommendations(analysis: Dict[str, Any],
                                  anomalies: List[Dict[str, Any]]) -> List[str]:
    """生成生长建议."""
    recommendations = []

    recommendations.append(f"当前平均身高：{analysis.get('avg_height', 0):.1f} cm")
    recommendations.append(f"当前平均体重：{analysis.get('avg_weight', 0):.1f} kg")
    recommendations.append(f"身高趋势：{analysis.get('height_trend', '未知')}")
    recommendations.append(f"体重趋势：{analysis.get('weight_trend', '未知')}")

    if anomalies:
        recommendations.append("\n⚠️ 需要关注的情况：")
        for anomaly in anomalies[:3]:
            recommendations.append(f"  - {anomaly['message']}")

    recommendations.append("\n建议定期记录体重和身高，观察生长曲线变化")

    return recommendations


def build_known_facts(payload: Dict[str, Any]) -> List[str]:
    """构建已知事实列表."""
    facts: List[str] = []
    child = payload.get("child_profile", {})
    family = payload.get("family_context", {})

    if child:
        facts.append(f"孩子画像：{child.get('name', '未命名')}，")
        birth_date = child.get("birth_date", "")
        if birth_date:
            age = calculate_child_age(birth_date)
            facts.append(f"  - 月龄：{age} 个月")
            facts.append(f"  - 出生日期：{birth_date}")
            facts.append(f"  - 性别：{child.get('gender', '未知')}")

    if family:
        facts.append(f"家庭上下文：")
        for key, value in family.items():
            facts.append(f"  - {key}：{value}")

    if payload.get("goal"):
        facts.append(f"目标：{payload.get('goal')}")

    records = payload.get("raw_records") or []
    facts.append(f"已收到 {len(records)} 条体检记录。")

    if records:
        analysis = analyze_growth_data(records)
        facts.append(f"平均身高：{analysis['avg_height']} cm")
        facts.append(f"平均体重：{analysis['avg_weight']} kg")
        facts.append(f"身高趋势：{analysis['height_trend']}")
        facts.append(f"体重趋势：{analysis['weight_trend']}")

    return facts


def build_analysis(payload: Dict[str, Any]) -> List[str]:
    """构建分析结果."""
    problem = payload.get("current_problem", "")
    history_days = payload.get("history_days", 7)
    records = payload.get("raw_records", [])

    analysis = [
        f"当前问题聚焦：{problem}",
        f"建议先建立最近 {history_days} 天的家庭基线，再判断趋势。",
        "本 Skill 会优先输出可执行动作、记录字段和复盘指标。"
    ]

    for step in SKILL_FLOW:
        analysis.append(f"链路节点：{step}")

    if records:
        analysis.append("\n📊 生长数据分析：")
        growth_analysis = analyze_growth_data(records)
        analysis.append(f"  - 平均身高：{growth_analysis['avg_height']} cm")
        analysis.append(f"  - 平均体重：{growth_analysis['avg_weight']} kg")
        analysis.append(f"  - 身高趋势：{growth_analysis['height_trend']}")
        analysis.append(f"  - 体重趋势：{growth_analysis['weight_trend']}")

        anomalies = detect_growth_anomalies(records)
        if anomalies:
            analysis.append(f"\n⚠️ 检测到 {len(anomalies)} 项异常：")
            for anomaly in anomalies[:3]:
                analysis.append(f"  - {anomaly['message']}")

    return analysis


def build_action_plan(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """构建行动计划."""
    base_tasks = [
        "上传或手动输入最新体检数据",
        "整理历次体检记录",
        "绘制成长曲线图",
        "准备下次体检问题清单",
        "与儿科医生沟通生长情况"
    ]

    plan: List[Dict[str, str]] = []
    for i, task in enumerate(base_tasks, start=1):
        plan.append({
            "day": f"D{i}",
            "task": task,
            "owner": "家长/主要照护人",
            "evidence_to_record": "日期、身高、体重、头围、医生建议",
            "difficulty": "低" if i <= 3 else "中"
        })
    return plan


def build_deliverables(payload: Dict[str, Any]) -> Dict[str, Any]:
    """构建交付物清单."""
    child = payload.get("child_profile", {})
    birth_date = child.get("birth_date", "")
    age = calculate_child_age(birth_date) if birth_date else 0

    return {
        "required": DEFAULT_DELIVERABLES,
        "tables": {
            "growth_records": ["日期", "月龄", "身高(cm)", "体重(kg)", "头围(cm)"],
            "checkup_summary": ["体检日期", "主要发现", "医生建议", "下次复查"]
        },
        "templates": {
            "growth_record": "日期：[日期]\n月龄：[月龄]\n身高：[cm]\n体重：[kg]\n头围：[cm]\n备注：[补充说明]",
            "doctor_question": "问题1：[关于生长的问题]\n问题2：[关于营养的问题]\n问题3：[其他问题]"
        },
        "age_specific": {
            "current_months": age,
            "typical_ranges": {
                "height": f"{age * 0.5 + 50:.1f}-{age * 0.5 + 60:.1f}",
                "weight": f"{age * 0.3 + 5:.1f}-{age * 0.3 + 8:.1f}"
            }
        }
    }


def next_fields() -> List[str]:
    """获取下次追踪字段列表."""
    return [
        "孩子年龄/月龄",
        "最新体检数据",
        "医生建议",
        "下次体检时间",
        "关注的问题",
        "家长疑问"
    ]
