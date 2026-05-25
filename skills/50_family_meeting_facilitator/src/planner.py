"""Planning engine for 家庭会议主持 Agent."""
from typing import Any, Dict, List
from datetime import datetime

try:
    from .analytics import analyze_meeting_patterns, aggregate_statistics, ContextMemory
except ImportError:
    from analytics import analyze_meeting_patterns, aggregate_statistics, ContextMemory

SKILL_FLOW = ['收集议题', '排定议程', '主持讨论', '记录决议', '跟踪行动']
SAFETY_NOTES = ['本 Skill 用于家庭会议主持辅助，不替代人工判断和决策。', '涉及法律、财务、重大健康决定时，应建议咨询专业人士。', '所有议题应公平讨论，保护每位家庭成员的发言权。']
DEFAULT_DELIVERABLES = ['会议议程', '决议记录', '行动追踪表']


def build_known_facts(payload: Dict[str, Any]) -> List[str]:
    """构建已知事实列表"""
    facts: List[str] = []
    child = payload.get("child_profile", {})
    family = payload.get("family_context", {})
    if child:
        age = child.get("age_years", 0)
        facts.append(f"孩子画像：年龄{age}岁")
    if family:
        facts.append(f"家庭上下文：{family}")
    if payload.get("goal"):
        facts.append(f"目标：{payload.get('goal')}")
    records = payload.get("raw_records") or []
    facts.append(f"已收到 {len(records)} 条原始记录。")
    if records:
        stats = aggregate_statistics(records)
        if stats.get("total_meetings"):
            facts.append(f"会议总数：{stats['total_meetings']}次")
        if stats.get("pending_decisions"):
            facts.append(f"待处理决议：{stats['pending_decisions']}项")
    return facts


def build_analysis(payload: Dict[str, Any]) -> List[str]:
    """构建分析结果列表"""
    problem = payload.get("current_problem", "")
    history_days = payload.get("history_days", 7)
    records = payload.get("raw_records") or []
    analysis: List[str] = [f"当前问题聚焦：{problem}", f"建议先建立最近 {history_days} 天的家庭基线，再判断趋势。", "本 Skill 会优先输出可执行动作、记录字段和复盘指标。"]
    if records:
        patterns = analyze_meeting_patterns(records)
        if patterns.get("meeting_types"):
            analysis.append(f"会议类型分布：{patterns['meeting_types']}")
        if patterns.get("decision_rate"):
            analysis.append(f"决议达成率：{patterns['decision_rate']:.0%}")
        if patterns.get("action_completion"):
            analysis.append(f"行动完成率：{patterns['action_completion']:.0%}")
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
    return {"required": DEFAULT_DELIVERABLES, "tables": {"timeline": ["时间", "事件", "输入", "处理", "结果", "备注"], "weekly_review": ["指标", "本周", "上周", "变化", "下一步"], "meeting_agenda": ["议题", "提出人", "优先级", "时间分配"], "decisions": ["议题", "决议", "决策人", "状态", "截止日期"]}, "templates": {"daily_log": "今天发生了什么？我做了什么？孩子反应如何？下一次要调整什么？", "handoff_summary": "给专业人士/老师/家人的沟通摘要：事实、时间线、已尝试方法、待确认问题。"}}


def next_fields() -> List[str]:
    """获取下次追踪字段列表"""
    return ["孩子年龄/月龄", "今天新增记录", "执行了哪一步", "孩子反应", "家长感受", "需要调整的限制条件"]


def analyze_data(payload: Dict[str, Any]) -> Dict[str, Any]:
    """执行数据分析"""
    records = payload.get("raw_records") or []
    result = {"statistics": {}, "patterns": {}, "agenda": [], "decisions": [], "action_items": [], "alerts": []}
    if records:
        result["statistics"] = aggregate_statistics(records)
        result["patterns"] = analyze_meeting_patterns(records)
        result["decisions"] = extract_pending_decisions(records)
        result["action_items"] = extract_action_items(records)
        result["agenda"] = generate_next_agenda(payload)
        result["alerts"] = generate_alerts(result)
    return result


def extract_pending_decisions(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """提取待处理决议"""
    pending = []
    for record in records:
        for decision in record.get("decisions", []):
            if decision.get("status") == "pending":
                pending.append(decision)
    return pending


def extract_action_items(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """提取行动项目"""
    action_items = []
    for record in records:
        action_items.extend(record.get("action_items", []))
    return action_items


def generate_next_agenda(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """生成下次议程"""
    agenda = []
    problem = payload.get("current_problem", "")
    if problem:
        agenda.append({"topic": problem, "presenter": "系统", "priority": "normal", "time_allocation": 10})
    pending_decisions = payload.get("pending_decisions", [])
    for item in pending_decisions[:3]:
        agenda.append({"topic": item, "presenter": "待定", "priority": "high", "time_allocation": 5})
    return agenda


def generate_alerts(analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """生成预警信息"""
    alerts: List[Dict[str, Any]] = []
    stats = analysis_result.get("statistics", {})
    if stats.get("pending_decisions", 0) > 5:
        alerts.append({"alert_type": "many_pending", "severity": "warning", "message": "待处理决议过多", "recommendation": "建议召开专题会议处理", "timestamp": datetime.now().isoformat()})
    patterns = analysis_result.get("patterns", {})
    if patterns.get("action_completion", 0) < 0.5:
        alerts.append({"alert_type": "low_completion", "severity": "info", "message": "行动完成率偏低", "recommendation": "简化行动项目，确保可执行性", "timestamp": datetime.now().isoformat()})
    return alerts


def calculate_summary_metrics(payload: Dict[str, Any]) -> Dict[str, Any]:
    """计算摘要指标"""
    records = payload.get("raw_records") or []
    metrics = {"total_meetings": len(records), "total_decisions": 0, "pending_decisions": 0, "participation_rate": 0}
    if records:
        stats = aggregate_statistics(records)
        metrics.update(stats)
    return metrics


def generate_data_report(payload: Dict[str, Any]) -> Dict[str, Any]:
    """生成数据报告"""
    analysis = analyze_data(payload)
    metrics = calculate_summary_metrics(payload)
    report = {"summary": [f"共分析 {len(payload.get('raw_records', []))} 条会议记录", f"总决议 {metrics.get('total_decisions', 0)} 项", f"待处理 {metrics.get('pending_decisions', 0)} 项"], "statistics": analysis.get("statistics", {}), "patterns": analysis.get("patterns", {}), "agenda": analysis.get("agenda", []), "decisions": analysis.get("decisions", []), "action_items": analysis.get("action_items", []), "alerts": analysis.get("alerts", [])}
    return report