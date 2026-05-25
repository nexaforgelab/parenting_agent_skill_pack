"""Planning engine for 疫苗接种提醒 Agent.

提供数据分析、异常检测、个性化推荐、上下文记忆和数据聚合统计功能。
"""
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta

SKILL_FLOW = [
    '输入出生日期和已接种记录',
    '生成疫苗时间表',
    '到期提醒',
    '记录接种信息',
    '自动生成接种档案'
]

SAFETY_NOTES = [
    '本 Skill 只做家庭记录、观察整理、提醒和沟通材料准备，不提供诊断、治疗方案或用药建议。',
    '出现呼吸困难、持续高热、严重过敏反应、精神状态异常、脱水、剧烈呕吐/腹泻、外伤等情况时，必须提示立即联系医生或急救。',
    '所有月龄、疫苗、营养、睡眠建议都应标注为一般性参考，并要求家长以当地儿科医生/公卫机构建议为准。'
]

DEFAULT_DELIVERABLES = [
    '疫苗日历',
    '接种记录',
    '下次提醒'
]

VACCINE_SCHEDULE = {
    "乙肝疫苗": {"doses": 3, "intervals": [1, 5], "ages": [0, 1, 6]},
    "卡介苗": {"doses": 1, "intervals": [], "ages": [0]},
    "脊灰疫苗": {"doses": 4, "intervals": [2, 2, 3], "ages": [2, 3, 4, 4]},
    "百白破疫苗": {"doses": 4, "intervals": [2, 2, 3], "ages": [3, 4, 5, 18]},
    "麻疹疫苗": {"doses": 2, "intervals": [6], "ages": [8, 18]},
    "乙脑疫苗": {"doses": 2, "intervals": [6], "ages": [8, 18]},
    "流脑疫苗": {"doses": 2, "intervals": [3], "ages": [6, 9]},
    "甲肝疫苗": {"doses": 2, "intervals": [6], "ages": [18, 24]}
}

ALERT_THRESHOLDS = {
    "upcoming_days": 7,
    "overdue_days": 0,
    "reminder_days": 30
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


def calculate_due_date(birth_date: str, target_months: int) -> str:
    """计算目标月龄对应的日期.

    Args:
        birth_date: 出生日期
        target_months: 目标月龄

    Returns:
        目标日期字符串
    """
    try:
        birth = datetime.strptime(birth_date, "%Y-%m-%d")
        target = birth + timedelta(days=target_months * 30)
        return target.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return ""


def generate_vaccine_schedule(birth_date: str) -> List[Dict[str, Any]]:
    """生成疫苗接种时间表.

    Args:
        birth_date: 出生日期

    Returns:
        疫苗接种计划列表
    """
    schedule = []

    for vaccine_name, config in VACCINE_SCHEDULE.items():
        for dose_num, age_months in enumerate(config["ages"], start=1):
            due_date = calculate_due_date(birth_date, age_months)
            schedule.append({
                "vaccine": vaccine_name,
                "dose": dose_num,
                "age_months": age_months,
                "due_date": due_date,
                "status": "pending"
            })

    return sorted(schedule, key=lambda x: x["due_date"])


def analyze_vaccination_status(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析疫苗接种状态.

    Args:
        records: 接种记录列表

    Returns:
        状态分析结果字典
    """
    if not records:
        return {
            "total_doses": 0,
            "completed_doses": 0,
            "pending_doses": 0,
            "overdue_doses": 0,
            "completion_rate": 0.0
        }

    completed = sum(1 for r in records if r.get("actual_date"))
    pending = len(records) - completed
    today = datetime.now()

    overdue = 0
    for record in records:
        if not record.get("actual_date") and record.get("scheduled_date"):
            try:
                scheduled = datetime.strptime(record["scheduled_date"], "%Y-%m-%d")
                if scheduled < today:
                    overdue += 1
            except ValueError:
                pass

    completion_rate = (completed / len(records) * 100) if records else 0.0

    return {
        "total_doses": len(records),
        "completed_doses": completed,
        "pending_doses": pending,
        "overdue_doses": overdue,
        "completion_rate": round(completion_rate, 2)
    }


def detect_upcoming_vaccines(records: List[Dict[str, Any]], days: int = 7) -> List[Dict[str, Any]]:
    """检测即将到期的疫苗.

    Args:
        records: 接种记录列表
        days: 提前提醒天数

    Returns:
        即将到期的疫苗列表
    """
    upcoming = []
    today = datetime.now()
    deadline = today + timedelta(days=days)

    for record in records:
        if not record.get("actual_date") and record.get("scheduled_date"):
            try:
                scheduled = datetime.strptime(record["scheduled_date"], "%Y-%m-%d")
                if today <= scheduled <= deadline:
                    days_until = (scheduled - today).days
                    upcoming.append({
                        "vaccine": record.get("vaccine_name", "未知疫苗"),
                        "dose": record.get("dose_number", 1),
                        "due_date": record["scheduled_date"],
                        "days_until": days_until,
                        "urgency": "high" if days_until <= 3 else "medium"
                    })
            except ValueError:
                pass

    return sorted(upcoming, key=lambda x: x["days_until"])


def detect_overdue_vaccines(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """检测逾期未接种的疫苗.

    Args:
        records: 接种记录列表

    Returns:
        逾期疫苗列表
    """
    overdue = []
    today = datetime.now()

    for record in records:
        if not record.get("actual_date") and record.get("scheduled_date"):
            try:
                scheduled = datetime.strptime(record["scheduled_date"], "%Y-%m-%d")
                if scheduled < today:
                    days_overdue = (today - scheduled).days
                    overdue.append({
                        "vaccine": record.get("vaccine_name", "未知疫苗"),
                        "dose": record.get("dose_number", 1),
                        "scheduled_date": record["scheduled_date"],
                        "days_overdue": days_overdue,
                        "urgency": "high" if days_overdue > 30 else "medium"
                    })
            except ValueError:
                pass

    return sorted(overdue, key=lambda x: x["days_overdue"], reverse=True)


def generate_reminders(vaccination_status: Dict[str, Any],
                      upcoming: List[Dict[str, Any]],
                      overdue: List[Dict[str, Any]]) -> List[str]:
    """生成疫苗提醒消息.

    Args:
        vaccination_status: 接种状态
        upcoming: 即将到期疫苗
        overdue: 逾期疫苗

    Returns:
        提醒消息列表
    """
    reminders = []

    if overdue:
        reminders.append("🚨 **紧急提醒**：以下疫苗已逾期，请尽快安排接种：")
        for item in overdue[:5]:
            reminders.append(
                f"  - {item['vaccine']} 第{item['dose']}剂：已逾期 {item['days_overdue']} 天"
            )

    if upcoming:
        reminders.append("\n📅 **近期提醒**：以下疫苗即将到期：")
        for item in upcoming[:5]:
            if item['days_until'] <= 3:
                reminders.append(
                    f"  - {item['vaccine']} 第{item['dose']}剂：{item['days_until']} 天后 ({item['due_date']}) ⚠️"
                )
            else:
                reminders.append(
                    f"  - {item['vaccine']} 第{item['dose']}剂：{item['days_until']} 天后 ({item['due_date']})"
                )

    reminders.append(f"\n📊 当前接种进度：{vaccination_status['completion_rate']}%")
    reminders.append(f"  - 已完成：{vaccination_status['completed_doses']} 剂")
    reminders.append(f"  - 待接种：{vaccination_status['pending_doses']} 剂")
    if vaccination_status['overdue_doses'] > 0:
        reminders.append(f"  - 已逾期：{vaccination_status['overdue_doses']} 剂")

    return reminders


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
    facts.append(f"已收到 {len(records)} 条疫苗接种记录。")

    if records:
        status = analyze_vaccination_status(records)
        facts.append(f"已完成接种：{status['completed_doses']} 剂")
        facts.append(f"待接种疫苗：{status['pending_doses']} 剂")
        facts.append(f"接种完成率：{status['completion_rate']}%")

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
        analysis.append("\n📊 疫苗接种分析：")
        status = analyze_vaccination_status(records)
        analysis.append(f"  - 总体完成率：{status['completion_rate']}%")
        analysis.append(f"  - 已完成：{status['completed_doses']} 剂")
        analysis.append(f"  - 待完成：{status['pending_doses']} 剂")

        upcoming = detect_upcoming_vaccines(records)
        if upcoming:
            analysis.append(f"\n📅 即将到期（7天内）：{len(upcoming)} 剂")
            for item in upcoming[:3]:
                analysis.append(f"  - {item['vaccine']} 第{item['dose']}剂：{item['days_until']} 天后")

        overdue = detect_overdue_vaccines(records)
        if overdue:
            analysis.append(f"\n⚠️ 已逾期：{len(overdue)} 剂")
            for item in overdue[:3]:
                analysis.append(f"  - {item['vaccine']} 第{item['dose']}剂：逾期 {item['days_overdue']} 天")

    return analysis


def build_action_plan(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """构建行动计划.

    Args:
        payload: 输入载荷

    Returns:
        行动计划列表
    """
    base_tasks = [
        "补齐孩子疫苗接种档案",
        "核对已接种疫苗记录",
        "安排逾期疫苗补种",
        "预约下次疫苗接种时间",
        "记录本次接种反应"
    ]

    records = payload.get("raw_records", [])
    overdue = detect_overdue_vaccines(records)

    if overdue:
        base_tasks[2] = f"立即安排 {overdue[0]['vaccine']} 第{overdue[0]['dose']}剂的补种"

    plan: List[Dict[str, str]] = []
    for i, task in enumerate(base_tasks, start=1):
        plan.append({
            "day": f"D{i}",
            "task": task,
            "owner": "家长/主要照护人",
            "evidence_to_record": "接种日期、疫苗名称、批号、接种机构、孩子反应",
            "difficulty": "高" if i <= 2 else ("中" if i <= 4 else "低")
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

    schedule = generate_vaccine_schedule(birth_date) if birth_date else []

    return {
        "required": DEFAULT_DELIVERABLES,
        "tables": {
            "vaccination_schedule": ["疫苗名称", "剂次", "接种月龄", "应接种日期", "实际接种日期", "状态"],
            "upcoming_vaccines": ["疫苗名称", "剂次", "到期日期", "剩余天数", "紧急程度"]
        },
        "templates": {
            "vaccination_record": "日期：[日期]\n疫苗：[名称]\n剂次：[第X剂]\n批号：[批号]\n接种机构：[机构]\n接种医生：[医生]\n孩子反应：[描述]",
            "reminder_note": "提醒：[疫苗名称]\n剂次：第[X]剂\n预约日期：[日期]\n注意事项：[描述]"
        },
        "schedule": schedule[:10],
        "next_vaccine": schedule[0] if schedule else None
    }


def next_fields() -> List[str]:
    """获取下次追踪字段列表.

    Returns:
        字段列表
    """
    return [
        "孩子年龄/月龄",
        "最新接种记录",
        "接种后反应",
        "下次预约时间",
        "待补种疫苗",
        "家长疑问"
    ]
