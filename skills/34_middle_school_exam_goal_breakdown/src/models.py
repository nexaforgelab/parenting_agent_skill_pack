"""中考目标拆解 Agent - 数据模型"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum
import json


class SubjectType(Enum):
    """学科类型"""
    CHINESE = "chinese"
    MATH = "math"
    ENGLISH = "english"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    POLITICS = "politics"
    HISTORY = "history"
    GEOGRAPHY = "geography"


class DifficultyLevel(Enum):
    """难度等级"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class SubjectScore:
    """学科成绩"""
    subject: str
    current_score: float = 0.0
    target_score: float = 0.0
    weight: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StudyPlan:
    """学习计划"""
    subject: str
    target_topic: str
    current_level: str = ""
    target_level: str = ""
    weekly_hours: float = 0.0
    resources_needed: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SkillInput:
    """技能输入"""
    child_profile: Dict[str, Any]
    current_problem: str
    target_school: str = ""
    target_score: float = 0.0
    subject_scores: List[Dict[str, Any]] = field(default_factory=list)
    available_hours_per_week: float = 0.0
    history_days: int = 30
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
    skill_id: str = "middle_school_exam_goal_breakdown"
    summary: List[str] = field(default_factory=list)
    known_facts: List[str] = field(default_factory=list)
    analysis: List[str] = field(default_factory=list)
    action_plan: List[Dict[str, str]] = field(default_factory=list)
    deliverables: Dict[str, Any] = field(default_factory=dict)
    risk_notes: List[str] = field(default_factory=list)
    next_tracking_fields: List[str] = field(default_factory=list)
    markdown_report: str = ""
    goal_breakdown: Optional[Dict[str, Any]] = None
    study_plan: List[Dict[str, Any]] = field(default_factory=list)
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
            "goal_breakdown": self.goal_breakdown,
            "study_plan": self.study_plan,
            "recommendations": self.recommendations
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent, default=str)


_context_store: Dict[str, Any] = {}


def get_or_create_context(session_id: str) -> Dict[str, Any]:
    if session_id not in _context_store:
        _context_store[session_id] = {"session_id": session_id}
    return _context_store[session_id]
