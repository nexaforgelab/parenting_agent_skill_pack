"""手机使用管理 Agent - 数据模型"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from enum import Enum
import json


class ScreenActivity(Enum):
    """屏幕活动类型"""
    VIDEO = "video"
    GAMING = "gaming"
    SOCIAL_MEDIA = "social_media"
    LEARNING = "learning"
    CREATIVE = "creative"
    COMMUNICATION = "communication"
    OTHER = "other"


@dataclass
class ScreenTimeRecord:
    """屏幕使用记录"""
    id: str = ""
    timestamp: Union[str, datetime] = field(default_factory=lambda: datetime.now())
    activity_type: Union[str, ScreenActivity] = ScreenActivity.OTHER
    duration_minutes: int = 0
    content_description: str = ""
    is_supervised: bool = False
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "activity_type": self.activity_type.value if isinstance(self.activity_type, Enum) else self.activity_type,
            "duration_minutes": self.duration_minutes,
            "content_description": self.content_description,
            "is_supervised": self.is_supervised,
            "notes": self.notes
        }

    def validate(self) -> List[str]:
        errors = []
        if self.duration_minutes < 0:
            errors.append("时长不能为负数")
        if self.duration_minutes > 480:
            errors.append("单次时长不建议超过8小时")
        return errors


@dataclass
class SkillInput:
    """技能输入"""
    child_profile: Dict[str, Any]
    current_problem: str
    screen_time_records: List[Dict[str, Any]] = field(default_factory=list)
    history_days: int = 7
    privacy_mode: str = "family_local_first"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def validate(self) -> List[str]:
        errors = []
        if not isinstance(self.child_profile, dict):
            errors.append("child_profile 必须是字典类型")
        if not self.current_problem or not str(self.current_problem).strip():
            errors.append("current_problem 不能为空")
        return errors


@dataclass
class SkillOutput:
    """技能输出"""
    skill_id: str = "screen_time_management"
    summary: List[str] = field(default_factory=list)
    known_facts: List[str] = field(default_factory=list)
    analysis: List[str] = field(default_factory=list)
    action_plan: List[Dict[str, str]] = field(default_factory=list)
    deliverables: Dict[str, Any] = field(default_factory=dict)
    risk_notes: List[str] = field(default_factory=list)
    next_tracking_fields: List[str] = field(default_factory=list)
    markdown_report: str = ""
    screen_time_analysis: Optional[Dict[str, Any]] = None
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "summary": self.summary,
            "known_facts": self.known_facts,
            "analysis": self.analysis,
            "action_plan": self.action_plan,
            "deliverables": self.deliverables,
            "risk_notes": self.risk_notes,
            "next_tracking_fields": self.next_tracking_fields,
            "markdown_report": self.markdown_report,
            "screen_time_analysis": self.screen_time_analysis,
            "recommendations": self.recommendations
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent, default=str)


_context_store: Dict[str, Any] = {}


def get_or_create_context(session_id: str) -> Dict[str, Any]:
    if session_id not in _context_store:
        _context_store[session_id] = {"session_id": session_id}
    return _context_store[session_id]
