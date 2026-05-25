"""中考目标拆解 Agent - 规划引擎"""
from __future__ import annotations
from typing import Any, Dict, List
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

try:
    from .models import SkillInput, SkillOutput, get_or_create_context
    from .validators import validate_payload, validate_payload_with_details
except ImportError:
    from models import SkillInput, SkillOutput, get_or_create_context
    from validators import validate_payload, validate_payload_with_details

try:
    from .reporting import render_report
except ImportError:
    from reporting import render_report

SKILL_FLOW = [
    '分析当前成绩水平',
    '确定目标学校和分数',
    '拆解各科目标差距',
    '制定学科提升计划',
    '建立进度跟踪机制'
]

SAFETY_NOTES = [
    '本 Skill 提供备考规划参考，请结合学校老师建议',
    '目标设定要合理，避免给孩子过大压力',
    '注意劳逸结合，保持身心健康同样重要'
]

DEFAULT_DELIVERABLES = [
    '中考目标分解表',
    '学科提升计划',
    '周学习时间表',
    '进度跟踪记录'
]


def analyze_current_performance(subject_scores: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析当前成绩"""
    if not subject_scores:
        return {"total_score": 0, "average_score": 0, "weak_subjects": [], "strong_subjects": []}

    total = sum(s.get("current_score", 0) for s in subject_scores)
    avg = total / len(subject_scores) if subject_scores else 0

    sorted_scores = sorted(subject_scores, key=lambda x: x.get("current_score", 0))
    weak = sorted_scores[:2] if len(sorted_scores) >= 2 else sorted_scores
    strong = sorted_scores[-2:] if len(sorted_scores) >= 2 else sorted_scores

    return {
        "total_score": total,
        "average_score": round(avg, 1),
        "weak_subjects": [s.get("subject", "") for s in weak],
        "strong_subjects": [s.get("subject", "") for s in strong]
    }


def calculate_goal_breakdown(
    subject_scores: List[Dict[str, Any]],
    target_score: float
) -> Dict[str, Any]:
    """计算目标差距"""
    current_total = sum(s.get("current_score", 0) for s in subject_scores)
    current_avg = current_total / len(subject_scores) if subject_scores else 0

    target_avg = target_score / len(subject_scores) if subject_scores else target_score

    subject_goals = []
    for s in subject_scores:
        current = s.get("current_score", 0)
        subject_avg = target_avg
        gap = subject_avg - current
        improvement = "高" if gap > 15 else "中" if gap > 5 else "低"

        subject_goals.append({
            "subject": s.get("subject", ""),
            "current": current,
            "target": round(subject_avg, 1),
            "gap": round(gap, 1),
            "improvement": improvement
        })

    return {
        "target_total_score": target_score,
        "target_school": "待定",
        "current_total": current_total,
        "total_gap": target_score - current_total,
        "subject_goals": subject_goals
    }


def generate_study_plan(
    subject_scores: List[Dict[str, Any]],
    goal_breakdown: Dict[str, Any],
    available_hours: float
) -> List[Dict[str, Any]]:
    """生成学习计划"""
    plans = []
    subject_goals = goal_breakdown.get("subject_goals", [])

    for goal in subject_goals:
        gap = goal.get("gap", 0)
        weekly_hours = 0

        if gap > 20:
            weekly_hours = available_hours * 0.4
        elif gap > 10:
            weekly_hours = available_hours * 0.3
        elif gap > 5:
            weekly_hours = available_hours * 0.2
        else:
            weekly_hours = available_hours * 0.1

        plans.append({
            "subject": goal.get("subject", ""),
            "target_topic": f"提升至{goal.get('target', 0)}分",
            "current_level": f"当前{goal.get('current', 0)}分",
            "target_level": f"目标{goal.get('target', 0)}分",
            "weekly_hours": round(weekly_hours, 1),
            "resources_needed": ["教材", "练习题", "错题本"]
        })

    return sorted(plans, key=lambda x: x.get("gap", 0), reverse=True) if plans else plans


def build_known_facts(payload: Dict[str, Any]) -> List[str]:
    """构建已知事实"""
    facts = []
    child = payload.get("child_profile", {})

    if child:
        name = child.get("name", "孩子")
        grade = child.get("grade", "")
        facts.append(f"学生信息：{name}，{grade}")

    target = payload.get("target_score", 0)
    if target:
        facts.append(f"目标总分：{target}分")

    target_school = payload.get("target_school", "")
    if target_school:
        facts.append(f"目标学校：{target_school}")

    scores = payload.get("subject_scores", [])
    if scores:
        current = analyze_current_performance(scores)
        facts.append(f"当前总分：{current['total_score']}分")
        facts.append(f"当前平均：{current['average_score']}分")

    return facts


def build_analysis(payload: Dict[str, Any]) -> List[str]:
    """构建分析"""
    analysis = []
    problem = payload.get("current_problem", "")
    analysis.append(f"当前问题聚焦：{problem}")
    analysis.append("本 Skill 会帮助拆解中考目标并制定提升计划")

    scores = payload.get("subject_scores", [])
    target = payload.get("target_score", 0)

    if scores and target:
        breakdown = calculate_goal_breakdown(scores, target)
        analysis.append("")
        analysis.append("📊 成绩分析：")
        analysis.append(f"  - 目标差距：{breakdown['total_gap']}分")

        weak = [s for s in breakdown.get("subject_goals", []) if s.get("improvement") == "高"]
        if weak:
            analysis.append("")
            analysis.append("⚠️ 需要重点关注的学科：")
            for s in weak:
                analysis.append(f"  - {s['subject']}：需提升{s['gap']}分")

    return analysis


def build_action_plan(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """构建行动计划"""
    return [
        {"day": "本周", "task": "确定最终目标学校和分数", "priority": "高"},
        {"day": "本周", "task": "与孩子沟通目标并获得认同", "priority": "高"},
        {"day": "本月", "task": "制定各科详细学习计划", "priority": "高"},
        {"day": "每月", "task": "评估进度并调整计划", "priority": "中"}
    ]


def build_deliverables(payload: Dict[str, Any]) -> Dict[str, Any]:
    """构建交付物"""
    return {
        "required": DEFAULT_DELIVERABLES,
        "templates": {
            "weekly_plan": "日期 | 学科 | 内容 | 时长 | 完成情况",
            "monthly_review": "月份 | 目标 | 实际 | 差距 | 调整措施"
        }
    }


def next_fields() -> List[str]:
    """获取下次追踪字段"""
    return [
        "本次月考各科成绩",
        "计划完成情况",
        "遇到的困难",
        "需要调整的计划"
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

    subject_scores = payload.get("subject_scores", [])
    target_score = payload.get("target_score", 0)
    available_hours = payload.get("available_hours_per_week", 20)

    current_performance = analyze_current_performance(subject_scores)
    goal_breakdown = calculate_goal_breakdown(subject_scores, target_score) if target_score else {}
    study_plan = generate_study_plan(subject_scores, goal_breakdown, available_hours)

    known_facts = build_known_facts(payload)
    analysis = build_analysis(payload)
    action_plan = build_action_plan(payload)
    deliverables = build_deliverables(payload)

    recommendations = [
        "建议将大目标分解为每周、每天的小目标",
        "保持优势学科的同时，重点突破薄弱学科",
        "注意劳逸结合，避免过度疲劳",
        "定期与老师沟通，了解孩子在学校的表现"
    ]

    result = {
        "success": True,
        "skill_id": "middle_school_exam_goal_breakdown",
        "summary": [
            f"分析了{len(subject_scores)}个学科的成绩",
            f"目标总分：{target_score}分",
            f"当前总分：{current_performance['total_score']}分",
            f"差距：{goal_breakdown.get('total_gap', 0)}分"
        ],
        "known_facts": known_facts,
        "analysis": analysis,
        "action_plan": action_plan,
        "deliverables": deliverables,
        "risk_notes": SAFETY_NOTES,
        "next_tracking_fields": next_fields(),
        "goal_breakdown": goal_breakdown,
        "study_plan": study_plan,
        "recommendations": recommendations,
        "warnings": validation_result.get("warnings", [])
    }

    result["markdown_report"] = render_report(result)

    return result


if __name__ == "__main__":
    sample_payload = {
        "child_profile": {
            "name": "小明",
            "grade": "初三"
        },
        "current_problem": "制定中考目标和学习计划",
        "target_score": 600,
        "subject_scores": [
            {"subject": "语文", "current_score": 105},
            {"subject": "数学", "current_score": 98},
            {"subject": "英语", "current_score": 110},
            {"subject": "物理", "current_score": 85},
            {"subject": "化学", "current_score": 90}
        ],
        "available_hours_per_week": 25
    }

    result = run(sample_payload)
    print(result["markdown_report"])
