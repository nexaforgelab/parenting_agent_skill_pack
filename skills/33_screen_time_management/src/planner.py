"""手机使用管理 Agent - 规划引擎"""
from __future__ import annotations
from typing import Any, Dict, List
from datetime import datetime, timedelta
from collections import defaultdict
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

try:
    from .models import (
        ScreenTimeRecord, SkillInput, SkillOutput,
        get_or_create_context
    )
    from .validators import validate_payload, validate_payload_with_details
except ImportError:
    from models import (
        ScreenTimeRecord, SkillInput, SkillOutput,
        get_or_create_context
    )
    from validators import validate_payload, validate_payload_with_details

try:
    from .reporting import render_report
except ImportError:
    from reporting import render_report

SKILL_FLOW = [
    '记录屏幕使用情况',
    '分析使用模式和时长',
    '与推荐标准对比',
    '制定管理策略',
    '建立健康使用习惯'
]

SAFETY_NOTES = [
    '本 Skill 提供屏幕时间管理参考，不替代专业建议',
    '建议根据孩子年龄和发育情况调整具体标准',
    '健康使用习惯需要逐步建立，家长需耐心引导'
]

DEFAULT_DELIVERABLES = [
    '屏幕使用记录表',
    '使用分析报告',
    '管理策略建议',
    '习惯养成计划'
]


def get_recommended_limit(age: int) -> int:
    """获取推荐屏幕时间上限（分钟）"""
    if age < 3:
        return 0
    elif age <= 5:
        return 60
    elif age <= 12:
        return 90
    elif age <= 15:
        return 120
    else:
        return 150


def analyze_screen_time(records: List[Dict[str, Any]], history_days: int) -> Dict[str, Any]:
    """分析屏幕使用数据"""
    if not records:
        return {
            "daily_average_minutes": 0,
            "weekly_total_minutes": 0,
            "recommended_limit": 60,
            "activity_distribution": {},
            "exceeds_limit_days": 0,
            "trend": "unknown"
        }

    total_minutes = sum(r.get("duration_minutes", 0) for r in records)
    daily_avg = total_minutes / history_days if history_days > 0 else 0

    activity_dist = defaultdict(int)
    for r in records:
        activity = r.get("activity_type", "other")
        duration = r.get("duration_minutes", 0)
        activity_dist[activity] += duration

    exceeds_days = sum(1 for r in records if r.get("duration_minutes", 0) > 90)

    return {
        "daily_average_minutes": round(daily_avg, 1),
        "weekly_total_minutes": round(total_minutes, 1),
        "recommended_limit": 60,
        "activity_distribution": dict(activity_dist),
        "exceeds_limit_days": exceeds_days,
        "trend": "increasing" if daily_avg > 90 else "stable" if daily_avg > 60 else "healthy"
    }


def build_known_facts(payload: Dict[str, Any]) -> List[str]:
    """构建已知事实"""
    facts: List[str] = []
    child = payload.get("child_profile", {})

    if child:
        name = child.get("name", "孩子")
        age = child.get("age", 0)
        facts.append(f"孩子信息：{name}，{age}岁")

    records = payload.get("screen_time_records") or []
    facts.append(f"屏幕使用记录：{len(records)}条")

    if records:
        total = sum(r.get("duration_minutes", 0) for r in records)
        facts.append(f"累计屏幕时间：{total}分钟")

    return facts


def build_analysis(payload: Dict[str, Any]) -> List[str]:
    """构建分析"""
    analysis = []
    problem = payload.get("current_problem", "")
    analysis.append(f"当前问题聚焦：{problem}")
    analysis.append("本 Skill 会分析屏幕使用情况并提供管理建议")

    records = payload.get("screen_time_records") or []
    history_days = payload.get("history_days", 7)

    if records:
        screen_analysis = analyze_screen_time(records, history_days)
        child_profile = payload.get("child_profile", {})
        age = child_profile.get("age", 10)
        recommended = get_recommended_limit(age)

        analysis.append("")
        analysis.append("📊 屏幕时间分析：")
        analysis.append(f"  - 日均使用：{screen_analysis['daily_average_minutes']}分钟")
        analysis.append(f"  - 推荐上限：{recommended}分钟/天")

        if screen_analysis["daily_average_minutes"] > recommended:
            analysis.append("")
            analysis.append("⚠️ 使用时间超出推荐标准，需要关注")
        else:
            analysis.append("")
            analysis.append("✅ 使用时间在合理范围内")

    return analysis


def build_action_plan(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """构建行动计划"""
    plan = [
        {"day": "今天", "task": "记录今天的屏幕使用情况", "priority": "高"},
        {"day": "本周", "task": "与孩子讨论并制定使用规则", "priority": "高"},
        {"day": "本周", "task": "设置屏幕时间提醒", "priority": "中"},
        {"day": "2周后", "task": "评估规则执行情况并调整", "priority": "中"}
    ]
    return plan


def build_deliverables(payload: Dict[str, Any]) -> Dict[str, Any]:
    """构建交付物"""
    return {
        "required": DEFAULT_DELIVERABLES,
        "templates": {
            "daily_log": "日期 | 活动类型 | 时长 | 是否监督 | 备注",
            "weekly_review": "周次 | 日均时长 | 超限次数 | 改进措施"
        }
    }


def next_fields() -> List[str]:
    """获取下次追踪字段"""
    return [
        "今日屏幕使用总时长",
        "各类型活动分布",
        "是否遵守约定",
        "孩子的配合度",
        "需要调整的规则"
    ]


def run(payload: Dict[str, Any], session_id: str = "default") -> Dict[str, Any]:
    """主运行函数"""
    validation_result = validate_payload_with_details(payload)

    if not validation_result["is_valid"]:
        return {
            "success": False,
            "errors": validation_result["errors"],
            "validation_details": validation_result
        }

    child_profile = payload.get("child_profile", {})
    age = child_profile.get("age", 10)
    records = payload.get("screen_time_records") or []
    history_days = payload.get("history_days", 7)

    screen_analysis = analyze_screen_time(records, history_days)
    recommended = get_recommended_limit(age)
    screen_analysis["recommended_limit"] = recommended

    known_facts = build_known_facts(payload)
    analysis = build_analysis(payload)
    action_plan = build_action_plan(payload)
    deliverables = build_deliverables(payload)

    recommendations = []
    if screen_analysis["daily_average_minutes"] > recommended * 1.2:
        recommendations.append("建议减少娱乐性屏幕活动，增加教育类内容")
        recommendations.append("考虑使用屏幕时间管理软件")
        recommendations.append("安排更多户外活动替代屏幕时间")
    else:
        recommendations.append("继续保持当前的健康使用习惯")
        recommendations.append("注意内容的适宜性")
        recommendations.append("定期检查孩子的使用体验")

    result = {
        "success": True,
        "skill_id": "screen_time_management",
        "summary": [
            f"分析了{len(records)}条屏幕使用记录",
            f"日均使用{screen_analysis['daily_average_minutes']}分钟",
            f"推荐上限{recommended}分钟/天"
        ],
        "known_facts": known_facts,
        "analysis": analysis,
        "action_plan": action_plan,
        "deliverables": deliverables,
        "risk_notes": SAFETY_NOTES,
        "next_tracking_fields": next_fields(),
        "screen_time_analysis": screen_analysis,
        "recommendations": recommendations,
        "warnings": validation_result.get("warnings", [])
    }

    result["markdown_report"] = render_report(result)

    return result


if __name__ == "__main__":
    sample_payload = {
        "child_profile": {
            "name": "小明",
            "age": 10
        },
        "current_problem": "孩子每天使用手机时间过长",
        "screen_time_records": [
            {"activity_type": "gaming", "duration_minutes": 120},
            {"activity_type": "video", "duration_minutes": 60},
            {"activity_type": "learning", "duration_minutes": 30}
        ]
    }

    result = run(sample_payload)
    print(result["markdown_report"])
