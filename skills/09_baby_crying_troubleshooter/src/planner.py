"""Planning engine for 宝宝哭闹原因排查 Agent.

提供数据分析、异常检测、个性化推荐、上下文记忆和数据聚合统计功能。
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from collections import Counter

SKILL_FLOW = [
    '输入哭闹时间、持续时长、上次喂奶、睡眠、尿布、环境',
    'Agent 按排查清单引导',
    '记录处理方式和结果',
    '形成宝宝个人规律'
]

SAFETY_NOTES = [
    '本 Skill 只做家庭记录、观察整理、提醒和沟通材料准备，不提供诊断、治疗方案或用药建议。',
    '出现呼吸困难、持续高热、严重过敏反应、精神状态异常、脱水、剧烈呕吐/腹泻、外伤等情况时，必须提示立即联系医生或急救。',
    '所有月龄、疫苗、营养、睡眠建议都应标注为一般性参考，并要求家长以当地儿科医生/公卫机构建议为准。'
]

DEFAULT_DELIVERABLES = [
    '哭闹排查表',
    '原因统计',
    '安抚方式记录'
]

COMMON_CAUSES = [
    "饥饿",
    "困倦",
    "尿布湿了",
    "肠绞痛",
    "太热/太冷",
    "需要安抚",
    "出牙不适",
    "生病不适"
]

SOOTHING_METHODS = [
    "喂奶",
    "轻拍背部",
    "抱起摇晃",
    "白噪音",
    "换个姿势",
    "检查尿布",
    "调整室温",
    "按摩腹部"
]


def analyze_crying_patterns(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析哭闹模式."""
    if not records:
        return {
            "total_episodes": 0,
            "avg_duration": 0.0,
            "most_common_cause": "无数据",
            "most_effective_method": "无数据"
        }

    durations = [r.get("duration_minutes", 0) for r in records]
    all_causes = []
    all_methods = []

    for record in records:
        all_causes.extend(record.get("possible_causes", []))
        all_methods.extend(record.get("soothing_methods", []))

    cause_counts = Counter(all_causes)
    method_counts = Counter(all_methods)

    return {
        "total_episodes": len(records),
        "avg_duration": round(sum(durations) / len(durations), 2) if durations else 0,
        "most_common_cause": cause_counts.most_common(1)[0][0] if cause_counts else "无",
        "most_effective_method": method_counts.most_common(1)[0][0] if method_counts else "无",
        "cause_distribution": dict(cause_counts),
        "method_effectiveness": dict(method_counts)
    }


def detect_emergency_signs(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """检测紧急征象."""
    emergencies = []

    for record in records:
        notes = record.get("notes", "").lower()
        duration = record.get("duration_minutes", 0)

        if duration > 120:
            emergencies.append({
                "type": "长时间哭闹",
                "timestamp": record.get("timestamp", ""),
                "duration": duration,
                "message": f"哭闹持续超过2小时（{duration}分钟），建议立即就医"
            })

        emergency_keywords = ["呼吸困难", "高热", "呕吐", "腹泻", "抽搐", "昏迷"]
        for keyword in emergency_keywords:
            if keyword in notes:
                emergencies.append({
                    "type": "紧急征象",
                    "keyword": keyword,
                    "timestamp": record.get("timestamp", ""),
                    "message": f"检测到紧急关键词 '{keyword}'，请立即联系医生"
                })

    return emergencies


def generate_troubleshooting_checklist() -> List[str]:
    """生成排查清单."""
    checklist = [
        "1. 检查尿布是否湿了",
        "2. 检查是否饿了（距离上次喂奶多久？）",
        "3. 检查是否困了（上次睡眠是什么时候？）",
        "4. 检查体温是否正常",
        "5. 检查是否出牙期",
        "6. 尝试轻拍背部或抱起安抚",
        "7. 检查是否有腹胀或肠绞痛迹象",
        "8. 观察周围环境是否舒适"
    ]
    return checklist


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
    facts.append(f"已收到 {len(records)} 条哭闹记录。")

    if records:
        analysis = analyze_crying_patterns(records)
        facts.append(f"总哭闹次数：{analysis['total_episodes']} 次")
        facts.append(f"平均持续时间：{analysis['avg_duration']} 分钟")
        facts.append(f"最常见原因：{analysis['most_common_cause']}")

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
        analysis.append("\n📊 哭闹模式分析：")
        pattern = analyze_crying_patterns(records)
        analysis.append(f"  - 总哭闹次数：{pattern['total_episodes']} 次")
        analysis.append(f"  - 平均持续时间：{pattern['avg_duration']} 分钟")
        analysis.append(f"  - 最常见原因：{pattern['most_common_cause']}")

        emergencies = detect_emergency_signs(records)
        if emergencies:
            analysis.append("\n🚨 紧急提醒：")
            for em in emergencies[:2]:
                analysis.append(f"  - {em['message']}")

    analysis.append("\n📋 排查清单：")
    for item in generate_troubleshooting_checklist():
        analysis.append(f"  - {item}")

    return analysis


def build_action_plan(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """构建行动计划."""
    base_tasks = [
        "记录本次哭闹的详细信息",
        "按照排查清单逐一排查原因",
        "尝试不同的安抚方法并记录效果",
        "观察并记录宝宝的个人规律",
        "总结有效的安抚策略"
    ]

    plan: List[Dict[str, str]] = []
    for i, task in enumerate(base_tasks, start=1):
        plan.append({
            "day": f"D{i}",
            "task": task,
            "owner": "家长/主要照护人",
            "evidence_to_record": "时间、持续时长、可能原因、安抚方法、效果",
            "difficulty": "低"
        })
    return plan


def build_deliverables(payload: Dict[str, Any]) -> Dict[str, Any]:
    """构建交付物清单."""
    return {
        "required": DEFAULT_DELIVERABLES,
        "tables": {
            "crying_log": ["时间", "持续时长", "可能原因", "安抚方法", "效果"],
            "cause_stats": ["原因", "出现次数", "占比"]
        },
        "templates": {
            "crying_record": "时间：[时间]\n持续时长：[X]分钟\n可能原因：[原因]\n安抚方法：[方法]\n效果：[描述]\n备注：[补充]",
            "daily_summary": "今日哭闹：[X]次\n最常见原因：[原因]\n最有效方法：[方法]"
        },
        "checklists": {
            "troubleshooting": generate_troubleshooting_checklist(),
            "emergency_signs": [
                "持续哭闹超过2小时",
                "高热或体温过低",
                "呼吸困难",
                "呕吐或腹泻",
                "抽搐或精神异常"
            ]
        }
    }


def next_fields() -> List[str]:
    """获取下次追踪字段列表."""
    return [
        "本次哭闹详情",
        "排查过程",
        "有效安抚方法",
        "宝宝规律发现",
        "家长疑问"
    ]
