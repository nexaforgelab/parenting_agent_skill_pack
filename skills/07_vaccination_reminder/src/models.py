"""Data models for 疫苗接种提醒 Agent.

这些模型保持轻量，方便 OpenClaw / Hermes / 任意 Python Agent Runtime 直接复用。
"""
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime, date
import json


@dataclass
class SkillInput:
    """技能输入数据模型.

    包含孩子的基本信息、当前问题、家庭上下文等输入参数。
    支持历史记录、偏好设置和附件信息。
    """
    child_profile: Dict[str, Any]
    current_problem: str
    family_context: Dict[str, Any] = field(default_factory=dict)
    goal: str = ""
    raw_records: List[Dict[str, Any]] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    history_days: int = 7
    privacy_mode: str = "family_local_first"

    def to_dict(self) -> Dict[str, Any]:
        """将对象转换为字典格式.

        Returns:
            包含所有字段的字典对象
        """
        return asdict(self)

    def validate(self) -> List[str]:
        """验证输入数据的有效性.

        Returns:
            错误消息列表，空列表表示验证通过
        """
        errors = []
        if not isinstance(self.child_profile, dict):
            errors.append("child_profile 必须是字典类型")
        if not str(self.current_problem).strip():
            errors.append("current_problem 不能为空")
        if self.history_days < 0:
            errors.append("history_days 必须是非负整数")
        if self.privacy_mode not in {"anonymous", "family_local_first", "full"}:
            errors.append("privacy_mode 必须是 anonymous、family_local_first 或 full")
        return errors


@dataclass
class ActionItem:
    """行动项数据模型.

    描述具体的执行任务，包括时间、负责人和记录要求。
    """
    day: str
    task: str
    owner: str = "家长"
    evidence_to_record: str = "一句话记录执行结果"
    difficulty: str = "低"

    def to_dict(self) -> Dict[str, str]:
        """将行动项转换为字典格式.

        Returns:
            行动项字典
        """
        return asdict(self)

    def validate(self) -> List[str]:
        """验证行动项的有效性.

        Returns:
            错误消息列表
        """
        errors = []
        if not self.day:
            errors.append("day 不能为空")
        if not self.task:
            errors.append("task 不能为空")
        if self.difficulty not in {"低", "中", "高"}:
            errors.append("difficulty 必须是 低、中 或 高")
        return errors


@dataclass
class VaccinationRecord:
    """疫苗接种记录数据模型.

    记录每次疫苗接种的详细信息。
    """
    vaccine_id: str
    vaccine_name: str
    dose_number: int
    scheduled_date: str
    actual_date: Optional[str] = None
    location: str = ""
    batch_number: str = ""
    doctor: str = ""
    side_effects: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式."""
        return asdict(self)

    def is_completed(self) -> bool:
        """判断是否已完成接种.

        Returns:
            True 如果已完成接种
        """
        return self.actual_date is not None and self.actual_date != ""

    def is_overdue(self, reference_date: Optional[str] = None) -> bool:
        """判断是否逾期未接种.

        Args:
            reference_date: 参考日期，默认为今天

        Returns:
            True 如果逾期
        """
        if self.is_completed():
            return False

        ref = datetime.strptime(reference_date or datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d")
        try:
            scheduled = datetime.strptime(self.scheduled_date, "%Y-%m-%d")
            return scheduled < ref
        except ValueError:
            return False


@dataclass
class VaccineSchedule:
    """疫苗接种计划数据模型.

    定义孩子应接种的疫苗时间表。
    """
    vaccine_id: str
    vaccine_name: str
    total_doses: int
    dose_intervals: List[int]
    earliest_age_months: int
    latest_age_months: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式."""
        return asdict(self)

    def get_dose_date(self, birth_date: str, dose_num: int) -> str:
        """计算指定剂次的接种日期.

        Args:
            birth_date: 出生日期
            dose_num: 剂次编号

        Returns:
            接种日期字符串
        """
        try:
            birth = datetime.strptime(birth_date, "%Y-%m-%d")
            total_months = self.earliest_age_months

            for i in range(dose_num - 1):
                total_months += self.dose_intervals[i]

            target_month = birth.month + total_months
            target_year = birth.year + (target_month - 1) // 12
            target_month = (target_month - 1) % 12 + 1

            day = min(birth.day, 28)
            return f"{target_year}-{target_month:02d}-{day:02d}"
        except (ValueError, IndexError):
            return ""


@dataclass
class Reminder:
    """疫苗提醒数据模型.

    存储即将到期或已逾期的疫苗提醒。
    """
    vaccine_name: str
    dose_number: int
    due_date: str
    urgency: str
    message: str

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式."""
        return asdict(self)


@dataclass
class SkillOutput:
    """技能输出数据模型.

    包含分析结果、行动计划和交付物。
    """
    skill_id: str
    summary: List[str]
    known_facts: List[str]
    analysis: List[str]
    action_plan: List[ActionItem]
    deliverables: Dict[str, Any]
    risk_notes: List[str]
    next_tracking_fields: List[str]
    markdown_report: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式.

        Returns:
            完整的输出字典
        """
        return {
            "skill_id": self.skill_id,
            "summary": self.summary,
            "known_facts": self.known_facts,
            "analysis": self.analysis,
            "action_plan": [item.to_dict() if isinstance(item, ActionItem) else item for item in self.action_plan],
            "deliverables": self.deliverables,
            "risk_notes": self.risk_notes,
            "next_tracking_fields": self.next_tracking_fields,
            "markdown_report": self.markdown_report
        }

    def to_json(self, indent: int = 2) -> str:
        """序列化为JSON格式字符串.

        Args:
            indent: JSON缩进空格数

        Returns:
            JSON格式的字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def validate(self) -> List[str]:
        """验证输出数据的有效性.

        Returns:
            错误消息列表
        """
        errors = []
        if not self.skill_id:
            errors.append("skill_id 不能为空")
        if not isinstance(self.summary, list):
            errors.append("summary 必须是列表类型")
        if not isinstance(self.action_plan, list):
            errors.append("action_plan 必须是列表类型")
        return errors


@dataclass
class VaccinationStats:
    """疫苗接种统计数据模型.

    汇总接种统计信息。
    """
    total_vaccines: int
    completed_vaccines: int
    upcoming_vaccines: int
    overdue_vaccines: int
    completion_rate: float

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式."""
        return asdict(self)
