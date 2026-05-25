"""Planning engine for 儿童玩具选购 Agent."""
from typing import Any, Dict, List
from datetime import datetime

try:
    from .analytics import analyze_toy_preferences, detect_toy_issues, aggregate_statistics, personalize_recommendations, ContextMemory
except ImportError:
    from analytics import analyze_toy_preferences, detect_toy_issues, aggregate_statistics, personalize_recommendations, ContextMemory

SKILL_FLOW = ['输入年龄、预算、已有玩具、发展目标', '推荐玩具类型', '分析安全性、耐玩性、教育价值', '生成购买建议']
SAFETY_NOTES = ['本 Skill 只做信息整理、对比和风险提示，不替家长做最终消费决定。', '涉及价格、招生名额、合同条款、机构资质、口碑等信息时，应要求人工核验最新资料。', '输出应区分事实、推断、主观偏好和待核验项，避免夸大承诺。']
DEFAULT_DELIVERABLES = ['玩具推荐表', '避坑清单', '年龄适配说明']


def build_known_facts(payload: Dict[str, Any]) -> List[str]:
    """构建已知事实列表"""
    facts: List[str] = []
    child = payload.get("child_profile", {})
    family = payload.get("family_context", {})
    if child:
        age = child.get("age_years", 0)
        interests = child.get("interests", [])
        existing_toys = child.get("existing_toys", [])
        facts.append(f"孩子画像：年龄{age}岁，兴趣{interests}，已有玩具{len(existing_toys)}件")
    if family:
        facts.append(f"家庭上下文：{family}")
    if payload.get("goal"):
        facts.append(f"目标：{payload.get('goal')}")
    records = payload.get("raw_records") or []
    facts.append(f"已收到 {len(records)} 条原始记录。")
    if records:
        stats = aggregate_statistics(records)
        if stats.get("unique_toys"):
            facts.append(f"使用过的玩具：{stats['unique_toys']} 件")
        if stats.get("avg_engagement"):
            facts.append(f"平均参与度：{stats['avg_engagement']:.1f}")
    return facts


def build_analysis(payload: Dict[str, Any]) -> List[str]:
    """构建分析结果列表"""
    problem = payload.get("current_problem", "")
    history_days = payload.get("history_days", 7)
    records = payload.get("raw_records") or []
    child_profile = payload.get("child_profile", {})
    analysis: List[str] = [f"当前问题聚焦：{problem}", f"建议先建立最近 {history_days} 天的家庭基线，再判断趋势。", "本 Skill 会优先输出可执行动作、记录字段和复盘指标。"]
    if records:
        issues = detect_toy_issues(records)
        if issues:
            analysis.append(f"检测到 {len(issues)} 个需要关注的问题")
            for issue in issues[:3]:
                analysis.append(f"  - [{issue['severity']}] {issue['description']}")
        preferences = analyze_toy_preferences(records)
        if preferences.get("favorite_toys"):
            analysis.append(f"孩子喜欢的玩具：{', '.join(preferences['favorite_toys'][:3])}")
        if preferences.get("avg_engagement"):
            analysis.append(f"平均参与度：{preferences['avg_engagement']:.1f}")
    for step in SKILL_FLOW:
        analysis.append(f"链路节点：{step}")
    return analysis


def build_action_plan(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """构建行动计划列表"""
    base_tasks = ["补齐孩子画像和家庭限制条件", "把今天相关事件按时间线记录", "执行一个低压力动作并记录孩子反应", "晚上用 3 分钟复盘有效/无效做法", "一周后比较趋势并调整计划"]
    plan: List[Dict[str, str]] = []
    for i, task in enumerate(base_tasks, start=1):
        plan.append({"day": f"D{i}", "task": task, "owner": "家长/主要照护人", "evidence_to_record": "时间、触发点、执行方式、孩子反应", "difficulty": "低" if i <= 3 else "中"})
    return plan


def build_deliverables(payload: Dict[str, Any]) -> Dict[str, Any]:
    """构建交付物字典"""
    return {"required": DEFAULT_DELIVERABLES, "tables": {"timeline": ["时间", "事件", "输入", "处理", "结果", "备注"], "weekly_review": ["指标", "本周", "上周", "变化", "下一步"], "toy_recommendations": ["优先级", "玩具名称", "品牌", "分类", "适玩年龄", "教育价值", "耐玩性"]}, "templates": {"daily_log": "今天发生了什么？我做了什么？孩子反应如何？下一次要调整什么？", "handoff_summary": "给专业人士/老师/家人的沟通摘要：事实、时间线、已尝试方法、待确认问题。"}}


def next_fields() -> List[str]:
    """获取下次追踪字段列表"""
    return ["孩子年龄/月龄", "今天新增记录", "执行了哪一步", "孩子反应", "家长感受", "需要调整的限制条件"]


def analyze_data(payload: Dict[str, Any]) -> Dict[str, Any]:
    """执行数据分析"""
    records = payload.get("raw_records") or []
    child_profile = payload.get("child_profile", {})
    recommendations = payload.get("recommendations", [])
    result = {"statistics": {}, "preferences": {}, "issues": [], "personalized_recommendations": [], "alerts": []}
    if records:
        result["statistics"] = aggregate_statistics(records)
        result["preferences"] = analyze_toy_preferences(records)
        result["issues"] = detect_toy_issues(records)
        if child_profile and recommendations:
            result["personalized_recommendations"] = personalize_recommendations(child_profile, records, recommendations)
        result["alerts"] = generate_alerts(result)
    return result


def generate_alerts(analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """生成预警信息"""
    alerts: List[Dict[str, Any]] = []
    issues = analysis_result.get("issues", [])
    for issue in issues:
        if issue.get("severity") == "warning":
            alerts.append({"alert_type": "toy_issue", "severity": "warning", "message": issue.get("description", ""), "recommendation": issue.get("recommendation", ""), "timestamp": datetime.now().isoformat()})
    return alerts


def calculate_summary_metrics(payload: Dict[str, Any]) -> Dict[str, Any]:
    """计算摘要指标"""
    records = payload.get("raw_records") or []
    metrics = {"total_records": len(records), "avg_engagement": 0, "unique_toys": 0}
    if records:
        stats = aggregate_statistics(records)
        metrics["avg_engagement"] = stats.get("avg_engagement", 0)
        metrics["unique_toys"] = stats.get("unique_toys", 0)
    return metrics


def generate_data_report(payload: Dict[str, Any]) -> Dict[str, Any]:
    """生成数据报告"""
    analysis = analyze_data(payload)
    metrics = calculate_summary_metrics(payload)
    report = {"summary": [f"共分析 {len(payload.get('raw_records', []))} 条使用记录", f"使用过 {metrics.get('unique_toys', 0)} 件不同玩具", f"平均参与度 {metrics.get('avg_engagement', 0):.1f}"], "statistics": analysis.get("statistics", {}), "preferences": analysis.get("preferences", {}), "issues": analysis.get("issues", []), "alerts": analysis.get("alerts", []), "personalized_recommendations": analysis.get("personalized_recommendations", [])}
    return report