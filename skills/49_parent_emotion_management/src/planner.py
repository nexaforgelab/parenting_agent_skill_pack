"""Planning engine for 父母情绪管理 Agent."""
from typing import Any, Dict, List
from datetime import datetime

try:
    from .analytics import analyze_emotion_patterns, aggregate_statistics, ContextMemory
    from .validators import detect_crisis_signals
except ImportError:
    from analytics import analyze_emotion_patterns, aggregate_statistics, ContextMemory
    from validators import detect_crisis_signals

SKILL_FLOW = ['记录触发事件', '分析情绪来源', '给出暂停话术和替代表达', '生成复盘问题', '每周统计高压场景']
SAFETY_NOTES = ['本 Skill 用于家庭沟通、情绪复盘和非临床自我管理，不提供心理诊断或治疗。', '涉及自伤、伤人、家暴、严重抑郁、持续失控等高风险情境时，应提示寻求专业帮助或紧急支持。', '所有话术应低评判、低羞辱、鼓励共情和边界，不制造亲子对立。']
DEFAULT_DELIVERABLES = ['情绪日志', '亲子沟通建议', '压力场景分析']


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
        if stats.get("avg_intensity"):
            facts.append(f"平均情绪强度：{stats['avg_intensity']:.1f}/10")
        if stats.get("dominant_emotion"):
            facts.append(f"主要情绪：{stats['dominant_emotion']}")
    return facts


def build_analysis(payload: Dict[str, Any]) -> List[str]:
    """构建分析结果列表"""
    problem = payload.get("current_problem", "")
    history_days = payload.get("history_days", 7)
    records = payload.get("raw_records") or []
    analysis: List[str] = [f"当前问题聚焦：{problem}", f"建议先建立最近 {history_days} 天的家庭基线，再判断趋势。", "本 Skill 会优先输出可执行动作、记录字段和复盘指标。"]
    if records:
        patterns = analyze_emotion_patterns(records)
        if patterns.get("emotion_distribution"):
            analysis.append(f"情绪分布：{patterns['emotion_distribution']}")
        if patterns.get("trigger_analysis"):
            analysis.append(f"常见触发因素：{list(patterns['trigger_analysis'].keys())[:3]}")
        if patterns.get("effective_strategies"):
            analysis.append(f"有效策略：{', '.join(patterns['effective_strategies'][:3])}")
        crisis_signals = detect_crisis_signals(records)
        if crisis_signals:
            for signal in crisis_signals:
                analysis.append(f"🚨 {signal}")
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
    return {"required": DEFAULT_DELIVERABLES, "tables": {"timeline": ["时间", "事件", "输入", "处理", "结果", "备注"], "weekly_review": ["指标", "本周", "上周", "变化", "下一步"], "emotion_log": ["日期", "情绪类型", "强度", "触发因素", "应对策略", "效果"]}, "templates": {"daily_log": "今天发生了什么？我做了什么？孩子反应如何？下一次要调整什么？", "handoff_summary": "给专业人士/老师/家人的沟通摘要：事实、时间线、已尝试方法、待确认问题。"}}


def next_fields() -> List[str]:
    """获取下次追踪字段列表"""
    return ["孩子年龄/月龄", "今天新增记录", "执行了哪一步", "孩子反应", "家长感受", "需要调整的限制条件"]


def analyze_data(payload: Dict[str, Any]) -> Dict[str, Any]:
    """执行数据分析"""
    records = payload.get("raw_records") or []
    result = {"statistics": {}, "patterns": {}, "alerts": [], "coping_suggestions": []}
    if records:
        result["statistics"] = aggregate_statistics(records)
        result["patterns"] = analyze_emotion_patterns(records)
        result["alerts"] = generate_alerts(result)
        result["coping_suggestions"] = generate_coping_suggestions_list(records)
    return result


def generate_alerts(analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """生成预警信息"""
    alerts: List[Dict[str, Any]] = []
    stats = analysis_result.get("statistics", {})
    if stats.get("avg_intensity", 0) >= 7:
        alerts.append({"alert_type": "high_intensity", "severity": "warning", "message": "平均情绪强度偏高", "recommendation": "建议关注情绪调节，必要时寻求专业支持", "timestamp": datetime.now().isoformat()})
    patterns = analysis_result.get("patterns", {})
    if patterns.get("emotion_distribution", {}).get("anger") and patterns["emotion_distribution"]["anger"] > 3:
        alerts.append({"alert_type": "frequent_anger", "severity": "info", "message": "愤怒情绪出现较频繁", "recommendation": "尝试使用暂停技巧和替代表达", "timestamp": datetime.now().isoformat()})
    return alerts


def generate_coping_suggestions_list(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """生成应对建议列表"""
    suggestions = []
    if not records:
        return suggestions
    emotion_counter = {}
    for record in records:
        emotion = record.get("emotion_type", "unknown")
        if emotion not in emotion_counter:
            emotion_counter[emotion] = {"count": 0, "total_effectiveness": 0, "strategies": []}
        emotion_counter[emotion]["count"] += 1
        emotion_counter[emotion]["total_effectiveness"] += record.get("effectiveness", 3)
        emotion_counter[emotion]["strategies"].extend(record.get("coping_used", []))
    default_scripts = {
        "anger": ["我现在需要冷静一下", "我需要暂停"],
        "anxiety": ["这种感觉会过去的", "我可以应对"],
        "overwhelm": ["一次做一件事", "我可以请求帮助"],
        "frustration": ["这不是孩子的错", "我理解这是正常的"]
    }
    for emotion, data in emotion_counter.items():
        avg_effectiveness = data["total_effectiveness"] / data["count"] if data["count"] > 0 else 0
        effective_strategies = [s for s in set(data["strategies"]) if s]
        suggestions.append({"emotion_type": emotion, "frequency": data["count"], "avg_effectiveness": avg_effectiveness, "strategies": effective_strategies, "scripts": default_scripts.get(emotion, ["我现在需要冷静"])})
    return suggestions


def calculate_summary_metrics(payload: Dict[str, Any]) -> Dict[str, Any]:
    """计算摘要指标"""
    records = payload.get("raw_records") or []
    metrics = {"total_records": len(records), "avg_intensity": 0, "dominant_emotion": ""}
    if records:
        stats = aggregate_statistics(records)
        metrics["avg_intensity"] = stats.get("avg_intensity", 0)
        metrics["dominant_emotion"] = stats.get("dominant_emotion", "")
    return metrics


def generate_data_report(payload: Dict[str, Any]) -> Dict[str, Any]:
    """生成数据报告"""
    analysis = analyze_data(payload)
    metrics = calculate_summary_metrics(payload)
    report = {"summary": [f"共分析 {len(payload.get('raw_records', []))} 条情绪记录", f"平均强度 {metrics.get('avg_intensity', 0):.1f}/10", f"主要情绪: {metrics.get('dominant_emotion', '未知')}"], "statistics": analysis.get("statistics", {}), "patterns": analysis.get("patterns", {}), "alerts": analysis.get("alerts", []), "coping_suggestions": analysis.get("coping_suggestions", [])}
    return report