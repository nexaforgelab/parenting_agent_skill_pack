"""Planning engine for 月龄发育里程碑 Agent.

提供数据分析、异常检测、个性化推荐、上下文记忆和数据聚合统计功能。
"""
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import statistics

SKILL_FLOW = [
    '输入出生日期',
    '匹配月龄',
    '展示大运动、精细动作、语言、社交等发育观察点',
    '家长打卡记录',
    '生成成长趋势'
]

SAFETY_NOTES = [
    '本 Skill 只做家庭记录、观察整理、提醒和沟通材料准备，不提供诊断、治疗方案或用药建议。',
    '出现呼吸困难、持续高热、严重过敏反应、精神状态异常、脱水、剧烈呕吐/腹泻、外伤等情况时，必须提示立即联系医生或急救。',
    '所有月龄、疫苗、营养、睡眠建议都应标注为一般性参考，并要求家长以当地儿科医生/公卫机构建议为准。'
]

DEFAULT_DELIVERABLES = [
    '月龄发展清单',
    '成长记录',
    '观察提醒'
]

MILESTONE_CATEGORIES = {
    "大运动": ["抬头", "翻身", "坐", "爬", "站", "走", "跑", "跳"],
    "精细动作": ["抓握", "伸手", "捏取", "搭积木", "画画", "使用餐具"],
    "语言": ["咿呀", "喊爸妈", "单词", "短句", "长句", "唱歌"],
    "社交": ["微笑", "认人", "怕生", "游戏", "合作", "分享"]
}

ALERT_THRESHOLDS = {
    "milestone_delay_months": 2,
    "weight_gain_concern": 0.5,
    "height_stagnation_days": 90
}


def calculate_child_age(birth_date: str) -> int:
    """计算孩子当前月龄.

    Args:
        birth_date: 出生日期，格式 YYYY-MM-DD

    Returns:
        月龄（整数）
    """
    try:
        birth = datetime.strptime(birth_date, "%Y-%m-%d")
        today = datetime.now()
        months = (today.year - birth.year) * 12 + (today.month - birth.month)
        if today.day < birth.day:
            months -= 1
        return max(0, months)
    except (ValueError, TypeError):
        return 0


def get_age_appropriate_milestones(months: int) -> Dict[str, List[str]]:
    """根据月龄获取适龄的发育里程碑.

    Args:
        months: 月龄

    Returns:
        各类别的里程碑字典
    """
    milestones: Dict[str, List[str]] = {}

    for category, items in MILESTONE_CATEGORIES.items():
        category_milestones = []

        if months < 3:
            category_milestones = items[:1]
        elif months < 6:
            category_milestones = items[:2]
        elif months < 12:
            category_milestones = items[:3]
        elif months < 18:
            category_milestones = items[:4]
        elif months < 24:
            category_milestones = items[:5]
        else:
            category_milestones = items[:6]

        if category_milestones:
            milestones[category] = category_milestones

    return milestones


def analyze_milestone_trends(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析里程碑达成趋势.

    Args:
        records: 历史记录列表

    Returns:
        趋势分析结果字典
    """
    if not records:
        return {
            "total_records": 0,
            "achieved_count": 0,
            "pending_count": 0,
            "achievement_rate": 0.0,
            "category_breakdown": {},
            "trend_summary": "暂无足够数据进行趋势分析"
        }

    achieved = sum(1 for r in records if r.get("achieved", False))
    pending = len(records) - achieved
    achievement_rate = (achieved / len(records) * 100) if records else 0.0

    category_breakdown: Dict[str, Dict[str, int]] = {}
    for record in records:
        category = record.get("category", "未知")
        if category not in category_breakdown:
            category_breakdown[category] = {"achieved": 0, "pending": 0}

        if record.get("achieved", False):
            category_breakdown[category]["achieved"] += 1
        else:
            category_breakdown[category]["pending"] += 1

    trend_summary = generate_trend_summary(achievement_rate, category_breakdown)

    return {
        "total_records": len(records),
        "achieved_count": achieved,
        "pending_count": pending,
        "achievement_rate": round(achievement_rate, 2),
        "category_breakdown": category_breakdown,
        "trend_summary": trend_summary
    }


def generate_trend_summary(achievement_rate: float,
                          category_breakdown: Dict[str, Dict[str, int]]) -> str:
    """生成趋势分析摘要.

    Args:
        achievement_rate: 达成率
        category_breakdown: 各类别达成情况

    Returns:
        趋势摘要文本
    """
    if achievement_rate >= 90:
        base_summary = "发育进度优秀，大部分里程碑已达成"
    elif achievement_rate >= 70:
        base_summary = "发育进度良好，部分里程碑待完成"
    elif achievement_rate >= 50:
        base_summary = "发育进度正常，建议持续观察"
    else:
        base_summary = "发育进度需要关注，建议咨询专业人士"

    weak_categories = [
        cat for cat, stats in category_breakdown.items()
        if stats["pending"] > stats["achieved"]
    ]

    if weak_categories:
        base_summary += f"，{', '.join(weak_categories)}方面需要加强关注"

    return base_summary


def detect_anomalies(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """检测异常情况.

    Args:
        records: 历史记录列表

    Returns:
        异常记录列表
    """
    anomalies: List[Dict[str, Any]] = []

    for record in records:
        expected = record.get("expected_months", 0)
        actual = record.get("actual_months")

        if actual is not None:
            delay = actual - expected
            if delay >= ALERT_THRESHOLDS["milestone_delay_months"]:
                anomalies.append({
                    "type": "里程碑延迟",
                    "severity": "high" if delay >= 3 else "medium",
                    "milestone": record.get("milestone_name", "未知"),
                    "expected_months": expected,
                    "actual_months": actual,
                    "delay_months": delay,
                    "message": f"里程碑 '{record.get('milestone_name')}' 延迟 {delay} 个月，建议咨询医生"
                })

        if record.get("concern_flag"):
            anomalies.append({
                "type": "家长关注",
                "severity": "medium",
                "milestone": record.get("milestone_name", "未知"),
                "notes": record.get("notes", ""),
                "message": f"家长对 '{record.get('milestone_name')}' 表示关注"
            })

    return anomalies


def generate_personalized_recommendations(child_profile: Dict[str, Any],
                                         milestone_analysis: Dict[str, Any],
                                         anomalies: List[Dict[str, Any]]) -> List[str]:
    """生成个性化推荐.

    Args:
        child_profile: 儿童档案
        milestone_analysis: 里程碑分析结果
        anomalies: 异常列表

    Returns:
        推荐列表
    """
    recommendations: List[str] = []

    age_months = calculate_child_age(child_profile.get("birth_date", ""))

    recommendations.append(f"当前月龄 {age_months} 个月，建议关注以下发育重点：")

    appropriate = get_age_appropriate_milestones(age_months)
    for category, items in appropriate.items():
        recommendations.append(f"  - {category}：{'、'.join(items)}")

    if anomalies:
        high_severity = [a for a in anomalies if a.get("severity") == "high"]
        if high_severity:
            recommendations.append("\n⚠️ 高优先级关注事项：")
            for anomaly in high_severity:
                recommendations.append(f"  - {anomaly['message']}")

    pending_count = milestone_analysis.get("pending_count", 0)
    if pending_count > 3:
        recommendations.append(f"\n📋 当前有 {pending_count} 个里程碑待完成，建议按优先级逐步推进")

    recommendations.append("\n💡 建议每日记录孩子的表现，每周进行一次复盘总结")

    return recommendations


def aggregate_statistics(records: List[Dict[str, Any]],
                         days: int = 30) -> Dict[str, Any]:
    """聚合统计数据.

    Args:
        records: 记录列表
        days: 统计周期（天）

    Returns:
        统计汇总字典
    """
    if not records:
        return {
            "period_days": days,
            "total_entries": 0,
            "categories_count": 0,
            "most_active_category": "无",
            "completion_rate": 0.0,
            "average_entries_per_day": 0.0
        }

    category_counts: Dict[str, int] = {}
    for record in records:
        category = record.get("category", "未知")
        category_counts[category] = category_counts.get(category, 0) + 1

    total_entries = len(records)
    categories_count = len(category_counts)
    most_active = max(category_counts.items(), key=lambda x: x[1]) if category_counts else ("无", 0)

    achieved = sum(1 for r in records if r.get("achieved", False))
    completion_rate = (achieved / total_entries * 100) if total_entries > 0 else 0.0

    avg_per_day = total_entries / days if days > 0 else 0.0

    return {
        "period_days": days,
        "total_entries": total_entries,
        "categories_count": categories_count,
        "most_active_category": most_active[0],
        "category_distribution": category_counts,
        "completion_rate": round(completion_rate, 2),
        "average_entries_per_day": round(avg_per_day, 2)
    }


def build_known_facts(payload: Dict[str, Any]) -> List[str]:
    """构建已知事实列表.

    Args:
        payload: 输入载荷

    Returns:
        事实列表
    """
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
    facts.append(f"已收到 {len(records)} 条原始记录。")

    if records:
        analysis = analyze_milestone_trends(records)
        facts.append(f"里程碑达成率：{analysis['achievement_rate']}%")
        facts.append(f"已完成里程碑：{analysis['achieved_count']} 个")
        facts.append(f"待完成里程碑：{analysis['pending_count']} 个")

    return facts


def build_analysis(payload: Dict[str, Any]) -> List[str]:
    """构建分析结果.

    Args:
        payload: 输入载荷

    Returns:
        分析列表
    """
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
        analysis.append("\n📊 数据分析结果：")
        trend_analysis = analyze_milestone_trends(records)
        analysis.append(f"  - 总体达成率：{trend_analysis['achievement_rate']}%")
        analysis.append(f"  - {trend_analysis['trend_summary']}")

        anomalies = detect_anomalies(records)
        if anomalies:
            analysis.append(f"\n⚠️ 检测到 {len(anomalies)} 项异常：")
            for anomaly in anomalies[:3]:
                analysis.append(f"  - {anomaly['message']}")

        stats = aggregate_statistics(records, history_days)
        analysis.append(f"\n📈 统计概览：")
        analysis.append(f"  - 记录总数：{stats['total_entries']} 条")
        analysis.append(f"  - 日均记录：{stats['average_entries_per_day']} 条")
        analysis.append(f"  - 最活跃类别：{stats['most_active_category']}")

    return analysis


def build_action_plan(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """构建行动计划.

    Args:
        payload: 输入载荷

    Returns:
        行动计划列表
    """
    base_tasks = [
        "补齐孩子画像和家庭限制条件",
        "把今天相关事件按时间线记录",
        "执行一个低压力动作并记录孩子反应",
        "晚上用 3 分钟复盘有效/无效做法",
        "一周后比较趋势并调整计划"
    ]

    child = payload.get("child_profile", {})
    birth_date = child.get("birth_date", "")
    if birth_date:
        age = calculate_child_age(birth_date)
        age_appropriate = get_age_appropriate_milestones(age)
        if age_appropriate:
            categories = list(age_appropriate.keys())
            if len(categories) >= 2:
                base_tasks[2] = f"执行一个低压力动作并记录孩子反应（重点关注{categories[0]}和{categories[1]}）"

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
    """构建交付物清单.

    Args:
        payload: 输入载荷

    Returns:
        交付物字典
    """
    child = payload.get("child_profile", {})
    birth_date = child.get("birth_date", "")
    age = calculate_child_age(birth_date) if birth_date else 0

    return {
        "required": DEFAULT_DELIVERABLES,
        "tables": {
            "timeline": ["时间", "事件", "输入", "处理", "结果", "备注"],
            "weekly_review": ["指标", "本周", "上周", "变化", "下一步"],
            "milestone_tracking": ["里程碑", "类别", "预期月龄", "实际月龄", "状态"]
        },
        "templates": {
            "daily_log": "今天发生了什么？我做了什么？孩子反应如何？下一次要调整什么？",
            "handoff_summary": "给专业人士/老师/家人的沟通摘要：事实、时间线、已尝试方法、待确认问题。",
            "milestone_record": "日期：[日期]\n里程碑：[名称]\n类别：[类别]\n孩子表现：[描述]\n是否达成：[是/否/部分]\n备注：[补充说明]"
        },
        "age_specific": {
            "current_months": age,
            "recommended_milestones": get_age_appropriate_milestones(age),
            "checklist": [
                f"{age}个月宝宝发育观察清单",
                "大运动发展情况",
                "精细动作发展情况",
                "语言能力表现",
                "社交互动反应"
            ]
        }
    }


def next_fields() -> List[str]:
    """获取下次追踪字段列表.

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


def generate_context_summary(memory: Dict[str, Any]) -> str:
    """生成上下文记忆摘要.

    Args:
        memory: 上下文记忆字典

    Returns:
        摘要文本
    """
    session_id = memory.get("session_id", "未知")
    child_id = memory.get("child_id", "未知")
    observations = memory.get("previous_observations", [])
    milestones = memory.get("milestone_history", [])

    summary = f"会话 {session_id} | 孩子 {child_id}\n"
    summary += f"历史观察：{len(observations)} 条 | 里程碑记录：{len(milestones)} 条\n"

    if milestones:
        achieved = sum(1 for m in milestones if m.get("achieved", False))
        summary += f"里程碑达成：{achieved}/{len(milestones)}"

    return summary
