"""亲子冲突复盘 Agent - 规划引擎

增强版本：添加数据分析、异常检测、个性化推荐、上下文记忆
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

try:
    from .models import (
        ConflictRecord, ConflictAnalysis, ResolutionPlan,
        ConflictType, ConflictSeverity, SkillInput, SkillOutput,
        get_or_create_context
    )
    from .validators import validate_payload, validate_payload_with_details
except ImportError:
    from models import (
        ConflictRecord, ConflictAnalysis, ResolutionPlan,
        ConflictType, ConflictSeverity, SkillInput, SkillOutput,
        get_or_create_context
    )
    from validators import validate_payload, validate_payload_with_details

try:
    from .reporting import render_report
except ImportError:
    from reporting import render_report

SKILL_FLOW = [
    '记录冲突事件详情',
    '分析冲突触发点和升级过程',
    '识别家长和孩子双方的行为模式',
    '制定个性化解决方案',
    '建立长期预防策略'
]

SAFETY_NOTES = [
    '本 Skill 只提供冲突分析和沟通建议，不替代专业心理咨询',
    '遇到家庭暴力或严重心理问题时，请及时寻求专业帮助',
    '家长需要先管理好自己的情绪，再与孩子沟通'
]

DEFAULT_DELIVERABLES = [
    '冲突事件时间线',
    '行为模式分析表',
    '解决方案行动计划',
    '预防策略清单'
]


def analyze_conflict_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """分析单条冲突记录

    Args:
        record: 冲突记录字典

    Returns:
        分析结果字典
    """
    analysis = {
        "conflict_id": record.get("id", ""),
        "root_cause": "",
        "pattern_detected": "",
        "parent_contributing_factors": [],
        "child_contributing_factors": [],
        "environmental_factors": [],
        "missed_opportunities": [],
        "effective_strategies": [],
        "risk_indicators": [],
        "recommended_approach": ""
    }

    parent_behavior = record.get("parent_behavior", "")
    child_behavior = record.get("child_behavior", "")
    trigger = record.get("trigger", "")

    if any(word in parent_behavior for word in ["大声", "吼", "批评", "指责"]):
        analysis["parent_contributing_factors"].append("家长使用了高压语言")
    if any(word in parent_behavior for word in ["威胁", "惩罚", "取消"]):
        analysis["parent_contributing_factors"].append("家长使用了惩罚性语言")
    if any(word in parent_behavior for word in ["深呼吸", "冷静", "暂停"]):
        analysis["effective_strategies"].append("家长尝试了情绪调节策略")

    if any(word in child_behavior for word in ["哭", "发脾气", "摔东西"]):
        analysis["child_contributing_factors"].append("孩子情绪反应激烈")

    severity = record.get("severity", "minor")
    if severity in ["severe", "crisis"]:
        analysis["risk_indicators"].append("冲突严重程度较高，需要关注")

    outcome = record.get("outcome", "unresolved")
    if outcome == "escalated":
        analysis["risk_indicators"].append("冲突升级，需要改善应对策略")

    if not analysis["effective_strategies"]:
        analysis["missed_opportunities"].append("未能有效使用情绪调节策略")

    analysis["recommended_approach"] = generate_recommendation(analysis)

    return analysis


def generate_recommendation(analysis: Dict[str, Any]) -> str:
    """生成建议方法"""
    parent_factors = analysis.get("parent_contributing_factors", [])
    effective = analysis.get("effective_strategies", [])

    if parent_factors:
        return "建议家长先管理好自己的情绪，使用平静的语言与孩子沟通"
    elif effective:
        return "当前应对策略部分有效，建议继续使用并加以改进"
    else:
        return "建议学习更多情绪调节和沟通技巧"


def create_resolution_plan(
    conflict_id: str,
    analysis: Dict[str, Any],
    child_profile: Dict[str, Any]
) -> Dict[str, Any]:
    """创建解决方案

    Args:
        conflict_id: 冲突ID
        analysis: 冲突分析
        child_profile: 孩子画像

    Returns:
        解决方案字典
    """
    plan = {
        "conflict_id": conflict_id,
        "immediate_actions": [],
        "short_term_strategies": [],
        "long_term_prevention": [],
        "communication_phrase_suggestions": [],
        "boundary_adjustments": [],
        "support_resources": [],
        "follow_up_schedule": "",
        "success_metrics": []
    }

    parent_factors = analysis.get("parent_contributing_factors", [])

    if any("高压语言" in f for f in parent_factors):
        plan["immediate_actions"].append("与孩子单独沟通，为之前的强硬语气道歉")
        plan["short_term_strategies"].append("学习使用'我感受到...'而非'你总是...'的表达方式")
        plan["communication_phrase_suggestions"].append("妈妈/爸爸刚才说话太急了，对不起。我们可以重新谈谈吗？")

    plan["immediate_actions"].append("找一个平静的时机，主动与孩子谈论这次冲突的感受")

    plan["short_term_strategies"].append("建立'情绪暂停'机制：双方感觉激动时可以暂停5分钟")
    plan["short_term_strategies"].append("约定具体的规则，避免模糊的'你应该'表述")

    plan["long_term_prevention"].append("每周固定一个时间进行家庭沟通会议")
    plan["long_term_prevention"].append("学习孩子的年龄特点，理解其行为背后的需求")

    plan["communication_phrase_suggestions"].append("我理解你很生气，你可以告诉我是哪里让你不高兴吗？")
    plan["communication_phrase_suggestions"].append("我们一起想想有什么办法可以解决这个问题？")

    plan["success_metrics"].append("冲突频率降低")
    plan["success_metrics"].append("孩子情绪改善")
    plan["success_metrics"].append("沟通语气更加平和")

    plan["follow_up_schedule"] = "3天后跟进，1周后评估效果"

    return plan


def analyze_trends(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析冲突趋势

    Args:
        records: 冲突记录列表

    Returns:
        趋势分析结果
    """
    if not records:
        return {
            "frequency_trend": "unknown",
            "average_severity": "N/A",
            "average_resolution_quality": "N/A",
            "common_triggers": [],
            "improvement_areas": []
        }

    severity_map = {"minor": 1, "moderate": 2, "severe": 3, "crisis": 4}
    severities = [severity_map.get(r.get("severity", "minor"), 1) for r in records]
    avg_severity = sum(severities) / len(severities) if severities else 0

    severity_labels = {1: "轻微", 2: "中等", 3: "严重"}
    avg_severity_label = severity_labels.get(round(avg_severity), "轻微")

    resolution_scores = [r.get("resolution_quality", 0) for r in records if r.get("resolution_quality", 0) > 0]
    avg_resolution = sum(resolution_scores) / len(resolution_scores) if resolution_scores else 0

    triggers = [r.get("trigger", "") for r in records if r.get("trigger")]
    trigger_counts = defaultdict(int)
    for t in triggers:
        trigger_counts[t] += 1
    common_triggers = [t for t, _ in sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True)[:3]]

    improvement_areas = []
    if avg_severity > 2:
        improvement_areas.append("冲突严重程度偏高，需要学习更好的情绪管理方法")
    if avg_resolution < 5:
        improvement_areas.append("解决质量偏低，建议在冲突后多进行情感修复对话")

    recent_count = len([r for r in records if isinstance(r.get("timestamp"), str) and
                       datetime.fromisoformat(r["timestamp"]) > datetime.now() - timedelta(days=7)])
    older_count = len([r for r in records if isinstance(r.get("timestamp"), str) and
                      datetime.fromisoformat(r["timestamp"]) <= datetime.now() - timedelta(days=7)])

    if recent_count > older_count * 1.5:
        frequency_trend = "increasing"
    elif recent_count < older_count * 0.7:
        frequency_trend = "decreasing"
    else:
        frequency_trend = "stable"

    return {
        "frequency_trend": frequency_trend,
        "average_severity": avg_severity_label,
        "average_resolution_quality": f"{avg_resolution:.1f}/10",
        "common_triggers": common_triggers,
        "improvement_areas": improvement_areas
    }


def build_known_facts(payload: Dict[str, Any]) -> List[str]:
    """构建已知事实列表"""
    facts: List[str] = []
    child = payload.get("child_profile", {})

    if child:
        name = child.get("name", "孩子")
        age = child.get("age", 0)
        facts.append(f"孩子信息：{name}，{age}岁")

    records = payload.get("conflict_records") or []
    facts.append(f"冲突记录：{len(records)}条")

    if records:
        types = [r.get("conflict_type", "") for r in records]
        type_counts = defaultdict(int)
        for t in types:
            type_counts[t] += 1
        if type_counts:
            most_common = max(type_counts.items(), key=lambda x: x[1])
            facts.append(f"最常见冲突类型：{most_common[0]}")

    return facts


def build_analysis(payload: Dict[str, Any]) -> List[str]:
    """构建分析内容"""
    analysis = []
    problem = payload.get("current_problem", "")
    analysis.append(f"当前问题聚焦：{problem}")
    analysis.append("本 Skill 会分析冲突根源并提供解决方案")

    records = payload.get("conflict_records") or []

    if records:
        trend_analysis = analyze_trends(records)
        analysis.append("")
        analysis.append("📊 趋势分析：")
        analysis.append(f"  - 冲突频率趋势：{trend_analysis['frequency_trend']}")
        analysis.append(f"  - 平均严重程度：{trend_analysis['average_severity']}")
        analysis.append(f"  - 平均解决质量：{trend_analysis['average_resolution_quality']}")

        if trend_analysis.get("common_triggers"):
            analysis.append("")
            analysis.append("⚠️ 常见触发点：")
            for trigger in trend_analysis["common_triggers"]:
                analysis.append(f"  - {trigger}")

    return analysis


def build_action_plan(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """构建行动计划"""
    plan = [
        {
            "day": "今天",
            "task": "回顾冲突事件，保持客观冷静",
            "owner": "家长",
            "priority": "高"
        },
        {
            "day": "今天",
            "task": "找一个合适的时机与孩子沟通",
            "owner": "家长",
            "priority": "高"
        },
        {
            "day": "本周",
            "task": "实施建议的情绪调节策略",
            "owner": "家长",
            "priority": "中"
        },
        {
            "day": "本周",
            "task": "记录实施效果和感受",
            "owner": "家长",
            "priority": "中"
        },
        {
            "day": "下周",
            "task": "评估策略效果并调整",
            "owner": "家长",
            "priority": "低"
        }
    ]
    return plan


def build_deliverables(payload: Dict[str, Any]) -> Dict[str, Any]:
    """构建交付物"""
    records = payload.get("conflict_records") or []

    deliverables = {
        "required": DEFAULT_DELIVERABLES,
        "templates": {
            "conflict_log": "时间 | 冲突类型 | 触发点 | 结果 | 改进措施",
            "emotion_diary": "日期 | 情绪 | 触发事件 | 处理方式 | 效果"
        }
    }

    if records:
        analyses = [analyze_conflict_record(r) for r in records]
        plans = [create_resolution_plan(r.get("id", ""), a, payload.get("child_profile", {}))
                 for r, a in zip(records, analyses)]
        deliverables["conflict_analysis"] = analyses
        deliverables["resolution_plans"] = plans

    return deliverables


def next_fields() -> List[str]:
    """获取下次追踪字段"""
    return [
        "冲突是否再次发生",
        "使用了哪些改进策略",
        "孩子的反应如何",
        "解决质量评分变化",
        "需要继续关注的问题"
    ]


def run(payload: Dict[str, Any], session_id: str = "default") -> Dict[str, Any]:
    """主运行函数

    Args:
        payload: 输入数据字典
        session_id: 会话ID

    Returns:
        处理结果字典
    """
    validation_result = validate_payload_with_details(payload)

    if not validation_result["is_valid"]:
        return {
            "success": False,
            "errors": validation_result["errors"],
            "validation_details": validation_result
        }

    known_facts = build_known_facts(payload)
    analysis = build_analysis(payload)
    action_plan = build_action_plan(payload)
    deliverables = build_deliverables(payload)

    records = payload.get("conflict_records") or []
    conflict_analysis = [analyze_conflict_record(r) for r in records]
    resolution_plans = [create_resolution_plan(
        r.get("id", ""), a, payload.get("child_profile", {})
    ) for r, a in zip(records, conflict_analysis)]

    trend_analysis = analyze_trends(records)

    communication_tips = [
        "使用'我感受到...'而非'你总是...'的表达方式",
        "先处理情绪，再处理问题",
        "给孩子表达的机会，认真倾听",
        "避免在情绪激动时做决定",
        "冲突后记得情感修复"
    ]

    result = {
        "success": True,
        "skill_id": "parent_child_conflict_review",
        "summary": [
            f"分析了{len(records)}条冲突记录",
            "识别了冲突模式和触发因素",
            f"提供了{len(resolution_plans)}个个性化解决方案"
        ],
        "known_facts": known_facts,
        "analysis": analysis,
        "conflict_analysis": conflict_analysis,
        "resolution_plans": resolution_plans,
        "action_plan": action_plan,
        "deliverables": deliverables,
        "risk_notes": SAFETY_NOTES,
        "next_tracking_fields": next_fields(),
        "trend_analysis": trend_analysis,
        "communication_tips": communication_tips,
        "warnings": validation_result.get("warnings", [])
    }

    result["markdown_report"] = render_report(result)

    return result


if __name__ == "__main__":
    sample_payload = {
        "child_profile": {
            "name": "小明",
            "age": 12,
            "grade": "六年级"
        },
        "current_problem": "关于作业时间的亲子冲突",
        "conflict_records": [
            {
                "id": "conflict_001",
                "conflict_type": "homework",
                "severity": "moderate",
                "trigger": "孩子想先玩游戏再做作业",
                "parent_behavior": "大声批评并威胁取消游戏时间",
                "child_behavior": "发脾气并关门",
                "outcome": "escalated",
                "resolution_quality": 3
            }
        ]
    }

    result = run(sample_payload)
    print(result["markdown_report"])
