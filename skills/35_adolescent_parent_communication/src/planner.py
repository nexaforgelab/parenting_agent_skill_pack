"""青春期亲子沟通 Agent - 规划引擎"""
from __future__ import annotations
from typing import Any, Dict, List
from datetime import datetime
from collections import defaultdict
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

try:
    from .models import SkillInput, SkillOutput, CommunicationRecord, get_or_create_context
    from .validators import validate_payload, validate_payload_with_details
except ImportError:
    from models import SkillInput, SkillOutput, CommunicationRecord, get_or_create_context
    from validators import validate_payload, validate_payload_with_details

try:
    from .reporting import render_report
except ImportError:
    from reporting import render_report

SKILL_FLOW = [
    '了解孩子当前的发展阶段和特点',
    '分析当前沟通问题的根源',
    '提供适合青春期孩子的沟通策略',
    '给出具体的话术建议',
    '帮助建立长期良好的沟通习惯'
]

SAFETY_NOTES = [
    '本 Skill 提供沟通参考，遇到严重心理问题时请寻求专业帮助',
    '青春期的孩子需要更多自主空间，家长要学会适度放手',
    '尊重孩子的隐私，建立互信关系比控制更重要'
]

DEFAULT_DELIVERABLES = [
    '青春期沟通指南',
    '推荐话术清单',
    '沟通场景应对策略',
    '关系改善行动计划'
]

ADOLESCENCE_STAGE_TIPS = {
    "early": [
        "这个阶段的孩子（10-13岁）开始有独立意识",
        "家长应以引导为主，避免过度控制",
        "帮助孩子建立积极的自我认同"
    ],
    "middle": [
        "这个阶段的孩子（14-16岁）独立意识强烈",
        "可能会挑战权威，需要家长有耐心",
        "尊重孩子的隐私，给予适度空间"
    ],
    "late": [
        "这个阶段的孩子（17-19岁）趋于成熟",
        "可以像成人一样沟通，但仍需要支持",
        "帮助孩子做好走向独立的准备"
    ]
}

RECOMMENDED_PHRASES = [
    "我理解你有自己的想法，我们可以谈谈吗？",
    "我想听听你对这件事的看法。",
    "我可能不完全理解你的感受，但我想尝试理解。",
    "你觉得怎么做比较好？",
    "我尊重你的选择，但也想分享我的想法。",
    "如果需要帮助，我随时都在。",
    "我相信你能处理好这件事。",
    "我们可以一起想办法解决这个问题。"
]


def get_adolescence_stage(age: int) -> str:
    """判断青春期阶段"""
    if age <= 13:
        return "early"
    elif age <= 16:
        return "middle"
    else:
        return "late"


def analyze_communication(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析沟通情况"""
    if not records:
        return {
            "total_communications": 0,
            "successful_communications": 0,
            "success_rate": 0,
            "common_topics": [],
            "effective_approaches": []
        }

    total = len(records)
    successful = sum(1 for r in records if r.get("outcome") in ["successful", "good"])

    topics = [r.get("topic", "") for r in records if r.get("topic")]
    topic_counts = defaultdict(int)
    for t in topics:
        topic_counts[t] += 1
    common_topics = [t for t, _ in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:3]]

    return {
        "total_communications": total,
        "successful_communications": successful,
        "success_rate": round(successful / total * 100, 1) if total > 0 else 0,
        "common_topics": common_topics,
        "effective_approaches": ["倾听", "尊重", "给予选择"]
    }


def generate_communication_tips(
    child_profile: Dict[str, Any],
    current_problem: str
) -> List[str]:
    """生成沟通建议"""
    tips = []
    age_raw = child_profile.get("age", 14)
    try:
        age = int(age_raw)
    except (ValueError, TypeError):
        age = 14
    stage = get_adolescence_stage(age)

    stage_tips = ADOLESCENCE_STAGE_TIPS.get(stage, [])
    tips.extend(stage_tips)

    if any(word in current_problem for word in ["不听话", "叛逆", "对抗"]):
        tips.append("避免正面冲突，选择孩子心情好的时候沟通")
        tips.append('用"我感受"代替"你总是"的说法')

    if any(word in current_problem for word in ["不愿交流", "沉默", "封闭"]):
        tips.append("不要强迫孩子开口，给他/她独处的时间")
        tips.append("通过写信、短信等方式尝试沟通")

    tips.append('每周安排一次"特殊时光"，专心陪伴孩子')
    tips.append("关注孩子的兴趣，找到共同话题")

    return tips


def build_known_facts(payload: Dict[str, Any]) -> List[str]:
    """构建已知事实"""
    facts = []
    child = payload.get("child_profile", {})

    if child:
        name = child.get("name", "孩子")
        age_raw = child.get("age", 14)
        try:
            age = int(age_raw)
        except (ValueError, TypeError):
            age = 14
        grade = child.get("grade", "")
        stage = get_adolescence_stage(age)
        stage_name = {"early": "青春期早期", "middle": "青春期中期", "late": "青春期晚期"}.get(stage, "青春期")
        facts.append(f"孩子信息：{name}，{age}岁（{stage_name}），{grade}")

    records = payload.get("communication_records") or []
    facts.append(f"沟通记录：{len(records)}条")

    if records:
        analysis = analyze_communication(records)
        facts.append(f"沟通成功率：{analysis['success_rate']}%")

    return facts


def build_analysis(payload: Dict[str, Any]) -> List[str]:
    """构建分析"""
    analysis = []
    problem = payload.get("current_problem", "")
    analysis.append(f"当前问题聚焦：{problem}")
    analysis.append("本 Skill 会提供适合青春期孩子的沟通策略和建议")

    records = payload.get("communication_records") or []

    if records:
        comm_analysis = analyze_communication(records)
        analysis.append("")
        analysis.append("📊 沟通情况分析：")
        analysis.append(f"  - 总沟通次数：{comm_analysis['total_communications']}")
        analysis.append(f"  - 成功次数：{comm_analysis['successful_communications']}")
        analysis.append(f"  - 成功率：{comm_analysis['success_rate']}%")

    child = payload.get("child_profile", {})
    age_raw = child.get("age", 14)
    try:
        age = int(age_raw)
    except (ValueError, TypeError):
        age = 14
    stage = get_adolescence_stage(age)

    analysis.append("")
    analysis.append(f"📋 当前处于青春期{stage}阶段")
    for tip in ADOLESCENCE_STAGE_TIPS.get(stage, []):
        analysis.append(f"  - {tip}")

    return analysis


def build_action_plan(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """构建行动计划"""
    return [
        {"day": "今天", "task": "选择一个轻松的时刻，主动与孩子聊天", "priority": "高"},
        {"day": "本周", "task": "尝试使用推荐的沟通话术", "priority": "高"},
        {"day": "本周", "task": "记录孩子的反应和感受变化", "priority": "中"},
        {"day": "2周后", "task": "评估沟通效果，调整策略", "priority": "中"}
    ]


def build_deliverables(payload: Dict[str, Any]) -> Dict[str, Any]:
    """构建交付物"""
    return {
        "required": DEFAULT_DELIVERABLES,
        "templates": {
            "communication_log": "日期 | 话题 | 方式 | 孩子反应 | 效果评估",
            "weekly_reflection": "本周沟通次数 | 成功话题 | 困难话题 | 改进计划"
        }
    }


def next_fields() -> List[str]:
    """获取下次追踪字段"""
    return [
        "尝试了哪些沟通方式",
        "孩子的反应如何",
        "哪些话题更容易沟通",
        "遇到的困难",
        "需要调整的策略"
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
    records = payload.get("communication_records") or []

    comm_analysis = analyze_communication(records)
    tips = generate_communication_tips(child_profile, payload.get("current_problem", ""))

    known_facts = build_known_facts(payload)
    analysis = build_analysis(payload)
    action_plan = build_action_plan(payload)
    deliverables = build_deliverables(payload)

    result = {
        "success": True,
        "skill_id": "adolescent_parent_communication",
        "summary": [
            f"针对{child_profile.get('age', 14)}岁青春期孩子提供沟通建议",
            f"分析了{len(records)}条沟通记录",
            f"沟通成功率：{comm_analysis['success_rate']}%"
        ],
        "known_facts": known_facts,
        "analysis": analysis,
        "action_plan": action_plan,
        "deliverables": deliverables,
        "risk_notes": SAFETY_NOTES,
        "next_tracking_fields": next_fields(),
        "communication_analysis": comm_analysis,
        "communication_tips": tips,
        "recommended_phrases": RECOMMENDED_PHRASES,
        "warnings": validation_result.get("warnings", [])
    }

    result["markdown_report"] = render_report(result)

    return result


if __name__ == "__main__":
    sample_payload = {
        "child_profile": {
            "name": "小明",
            "age": 15,
            "grade": "初三"
        },
        "current_problem": "孩子不愿意和家长交流",
        "communication_records": [
            {"topic": "学习", "outcome": "successful"},
            {"topic": "朋友", "outcome": "good"},
            {"topic": "兴趣爱好", "outcome": "successful"}
        ]
    }

    result = run(sample_payload)
    print(result["markdown_report"])
