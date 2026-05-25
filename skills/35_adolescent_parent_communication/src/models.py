"""青春期亲子沟通 Agent - 数据模型"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum
import json


class CommunicationType(Enum):
    """沟通类型"""
    TOPIC_DISCUSSION = "topic_discussion"
    EMOTION_SHARING = "emotion_sharing"
    RULE_NEGOTIATION = "rule_negotiation"
    CONFLICT_RESOLUTION = "conflict_resolution"
    ROUTINE_CHECK_IN = "routine_check_in"
    PROBLEM_SOLVING = "problem_solving"


class AdolescenceStage(Enum):
    """青春期阶段"""
    EARLY = "early"
    MIDDLE = "middle"
    LATE = "late"


@dataclass
class CommunicationRecord:
    """沟通记录"""
    id: str = ""
    timestamp: Union[str, datetime] = field(default_factory=lambda: datetime.now())
    communication_type: Union[str, CommunicationType] = CommunicationType.ROUTINE_CHECK_IN
    topic: str = ""
    parent_approach: str = ""
    child_response: str = ""
    outcome: str = "unknown"
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "communication_type": self.communication_type.value if isinstance(self.communication_type, Enum) else self.communication_type,
            "topic": self.topic,
            "parent_approach": self.parent_approach,
            "child_response": self.child_response,
            "outcome": self.outcome,
            "notes": self.notes
        }


@dataclass
class SkillInput:
    """技能输入"""
    child_profile: Dict[str, Any]
    current_problem: str
    communication_records: List[Dict[str, Any]] = field(default_factory=list)
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
    skill_id: str = "adolescent_parent_communication"
    summary: List[str] = field(default_factory=list)
    known_facts: List[str] = field(default_factory=list)
    analysis: List[str] = field(default_factory=list)
    action_plan: List[Dict[str, str]] = field(default_factory=list)
    deliverables: Dict[str, Any] = field(default_factory=list)
    risk_notes: List[str] = field(default_factory=list)
    next_tracking_fields: List[str] = field(default_factory=list)
    markdown_report: str = ""
    communication_analysis: Optional[Dict[str, Any]] = None
    communication_tips: List[str] = field(default_factory=list)
    recommended_phrases: List[str] = field(default_factory=list)

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
            "communication_analysis": self.communication_analysis,
            "communication_tips": self.communication_tips,
            "recommended_phrases": self.recommended_phrases
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent, default=str)


_context_store: Dict[str, Any] = {}


def get_or_create_context(session_id: str) -> Dict[str, Any]:
    if session_id not in _context_store:
        _context_store[session_id] = {"session_id": session_id}
    return _context_store[session_id]
