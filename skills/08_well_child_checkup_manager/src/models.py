"""Data models for 宝宝体检记录管理 Agent.

这些模型保持轻量，方便 OpenClaw / Hermes / 任意 Python Agent Runtime 直接复用。
"""
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime, date
import json


@dataclass
class SkillInput:
    """技能输入数据模型."""
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
        """转换为字典格式."""
        return asdict(self)

    def validate(self) -> List[str]:
        """验证输入数据的有效性."""
        errors = []
        if not isinstance(self.child_profile, dict):
            errors.append("child_profile 必须是字典类型")
        if not str(self.current_problem).strip():
            errors.append("current_problem 不能为空")
        if self.history_days < 0:
            errors.append("history_days 必须是非负整数")
        return errors


@dataclass
class ActionItem:
    """行动项数据模型."""
    day: str
    task: str
    owner: str = "家长"
    evidence_to_record: str = "一句话记录执行结果"
    difficulty: str = "低"

    def to_dict(self) -> Dict[str, str]:
        """转换为字典格式."""
        return asdict(self)

    def validate(self) -> List[str]:
        """验证行动项的有效性."""
        errors = []
        if not self.day:
            errors.append("day 不能为空")
        if not self.task:
            errors.append("task 不能为空")
        if self.difficulty not in {"低", "中", "高"}:
            errors.append("difficulty 必须是 低、中 或 高")
        return errors


@dataclass
class CheckupRecord:
    """体检记录数据模型."""
    checkup_id: str
    checkup_date: str
    age_months: int
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    head_circumference_cm: Optional[float] = None
    doctor_name: str = ""
    institution: str = ""
    diagnosis: str = ""
    recommendations: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式."""
        return asdict(self)

    def is_complete(self) -> bool:
        """判断体检记录是否完整."""
        return all([
            self.height_cm is not None,
            self.weight_kg is not None,
            self.head_circumference_cm is not None
        ])


@dataclass
class GrowthMetrics:
    """生长指标数据模型."""
    date: str
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    head_circumference_cm: Optional[float] = None
    percentile_height: Optional[float] = None
    percentile_weight: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式."""
        return asdict(self)

    def validate(self) -> List[str]:
        """验证生长数据的有效性."""
        errors = []
        if self.height_cm is not None and (self.height_cm <= 0 or self.height_cm > 200):
            errors.append("身高必须在 0-200 cm 之间")
        if self.weight_kg is not None and (self.weight_kg <= 0 or self.weight_kg > 50):
            errors.append("体重必须在 0-50 kg 之间")
        if self.head_circumference_cm is not None and (self.head_circumference_cm <= 0 or self.head_circumference_cm > 100):
            errors.append("头围必须在 0-100 cm 之间")
        return errors


@dataclass
class GrowthTrend:
    """生长趋势分析数据模型."""
    metric_name: str
    values: List[float]
    dates: List[str]
    average_change: float
    trend_direction: str
    percentile_change: float

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式."""
        return asdict(self)


@dataclass
class SkillOutput:
    """技能输出数据模型."""
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
        """转换为字典格式."""
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
        """序列化为JSON格式字符串."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def validate(self) -> List[str]:
        """验证输出数据的有效性."""
        errors = []
        if not self.skill_id:
            errors.append("skill_id 不能为空")
        if not isinstance(self.summary, list):
            errors.append("summary 必须是列表类型")
        return errors
