"""Data models for 宝宝哭闹原因排查 Agent."""
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime
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
        return errors


@dataclass
class CryingRecord:
    """哭闹记录数据模型."""
    record_id: str
    timestamp: str
    duration_minutes: int
    possible_causes: List[str]
    soothing_methods: List[str]
    effectiveness: str
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式."""
        return asdict(self)


@dataclass
class CausePattern:
    """哭闹原因模式数据模型."""
    cause: str
    frequency: int
    common_times: List[str]
    effective_methods: List[str]
    recommendations: List[str]

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
