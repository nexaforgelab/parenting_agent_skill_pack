"""亲子冲突复盘 Agent - 数据模型

增强版本：添加完整类型注解、数据验证方法、序列化支持
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from enum import Enum
import json


class ConflictType(Enum):
    """冲突类型枚举"""
    HOMEWORK = "homework"
    SCREEN_TIME = "screen_time"
    BEDTIME = "bedtime"
    CHORES = "chores"
    SIBLING = "sibling"
    SCHOOL = "school"
    SOCIAL = "social"
    EMOTIONAL = "emotional"
    AUTONOMY = "autonomy"
    OTHER = "other"


class ConflictSeverity(Enum):
    """冲突严重程度枚举"""
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRISIS = "crisis"


class EmotionState(Enum):
    """情绪状态枚举"""
    CALM = "calm"
    FRUSTRATED = "frustrated"
    ANGRY = "angry"
    SAD = "sad"
    ANXIOUS = "anxious"
    RESISTANT = "resistant"
    DEFENSIVE = "defensive"


@dataclass
class ChildProfile:
    """孩子画像数据模型"""
    name: str = ""
    age: int = 0
    grade: str = ""
    personality_traits: List[str] = field(default_factory=list)
    emotional_sensitivity: str = "medium"
    communication_preference: str = "verbal"
    previous_conflicts: List[str] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)
    calming_strategies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)

    def validate(self) -> List[str]:
        """验证数据"""
        errors = []
        if self.age < 3 or self.age > 18:
            errors.append("年龄必须在3-18岁之间")
        valid_sensitivity = {"low", "medium", "high"}
        if self.emotional_sensitivity not in valid_sensitivity:
            errors.append(f"情绪敏感度必须是以下之一: {', '.join(valid_sensitivity)}")
        return errors


@dataclass
class ConflictTrigger:
    """冲突触发点数据模型"""
    trigger_id: str = ""
    description: str = ""
    trigger_type: str = ""
    intensity: int = 1
    frequency: str = "rare"
    warning_signs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)


@dataclass
class ConflictRecord:
    """冲突记录数据模型"""
    id: str = ""
    timestamp: Union[str, datetime] = field(default_factory=lambda: datetime.now())
    conflict_type: Union[str, ConflictType] = ConflictType.OTHER
    severity: Union[str, ConflictSeverity] = ConflictSeverity.MINOR
    trigger: str = ""
    parent_behavior: str = ""
    child_behavior: str = ""
    escalation_factors: List[str] = field(default_factory=list)
    de_escalation_attempts: List[str] = field(default_factory=list)
    outcome: str = "unresolved"
    resolution_quality: int = 0
    child_emotion_before: str = ""
    child_emotion_after: str = ""
    parent_emotion_before: str = ""
    parent_emotion_after: str = ""
    notes: str = ""

    def __post_init__(self):
        """后处理：类型转换"""
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)
        if isinstance(self.conflict_type, str):
            try:
                self.conflict_type = ConflictType(self.conflict_type)
            except ValueError:
                self.conflict_type = ConflictType.OTHER
        if isinstance(self.severity, str):
            try:
                self.severity = ConflictSeverity(self.severity)
            except ValueError:
                self.severity = ConflictSeverity.MINOR

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "conflict_type": self.conflict_type.value if isinstance(self.conflict_type, Enum) else self.conflict_type,
            "severity": self.severity.value if isinstance(self.severity, Enum) else self.severity,
            "trigger": self.trigger,
            "parent_behavior": self.parent_behavior,
            "child_behavior": self.child_behavior,
            "escalation_factors": self.escalation_factors,
            "de_escalation_attempts": self.de_escalation_attempts,
            "outcome": self.outcome,
            "resolution_quality": self.resolution_quality,
            "child_emotion_before": self.child_emotion_before,
            "child_emotion_after": self.child_emotion_after,
            "parent_emotion_before": self.parent_emotion_before,
            "parent_emotion_after": self.parent_emotion_after,
            "notes": self.notes
        }

    def validate(self) -> List[str]:
        """验证数据"""
        errors = []
        if not self.trigger.strip():
            errors.append("冲突触发点描述不能为空")
        if self.resolution_quality < 0 or self.resolution_quality > 10:
            errors.append("解决质量评分必须在0-10之间")
        valid_outcomes = {"resolved", "unresolved", "partially_resolved", "escalated"}
        if self.outcome not in valid_outcomes:
            errors.append(f"结果必须是以下之一: {', '.join(valid_outcomes)}")
        return errors


@dataclass
class ConflictAnalysis:
    """冲突分析数据模型"""
    conflict_id: str
    root_cause: str = ""
    pattern_detected: str = ""
    parent_contributing_factors: List[str] = field(default_factory=list)
    child_contributing_factors: List[str] = field(default_factory=list)
    environmental_factors: List[str] = field(default_factory=list)
    missed_opportunities: List[str] = field(default_factory=list)
    effective_strategies: List[str] = field(default_factory=list)
    risk_indicators: List[str] = field(default_factory=list)
    recommended_approach: str = ""
    follow_up_needed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)


@dataclass
class ResolutionPlan:
    """解决方案数据模型"""
    conflict_id: str
    immediate_actions: List[str] = field(default_factory=list)
    short_term_strategies: List[str] = field(default_factory=list)
    long_term_prevention: List[str] = field(default_factory=list)
    communication_phrase_suggestions: List[str] = field(default_factory=list)
    boundary_adjustments: List[str] = field(default_factory=list)
    support_resources: List[str] = field(default_factory=list)
    follow_up_schedule: str = ""
    success_metrics: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)


@dataclass
class SkillInput:
    """技能输入数据模型"""
    child_profile: Dict[str, Any]
    current_problem: str
    conflict_records: List[Dict[str, Any]] = field(default_factory=list)
    family_context: Dict[str, Any] = field(default_factory=dict)
    history_days: int = 7
    privacy_mode: str = "family_local_first"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)

    def validate(self) -> List[str]:
        """验证输入数据"""
        errors = []
        if not isinstance(self.child_profile, dict):
            errors.append("child_profile 必须是字典类型")
        if not self.current_problem or not str(self.current_problem).strip():
            errors.append("current_problem 不能为空")
        if self.history_days < 1 or self.history_days > 90:
            errors.append("history_days 必须在 1-90 天范围内")
        return errors


@dataclass
class SkillOutput:
    """技能输出数据模型"""
    skill_id: str = "parent_child_conflict_review"
    summary: List[str] = field(default_factory=list)
    known_facts: List[str] = field(default_factory=list)
    analysis: List[str] = field(default_factory=list)
    conflict_analysis: List[Dict[str, Any]] = field(default_factory=list)
    resolution_plans: List[Dict[str, Any]] = field(default_factory=list)
    action_plan: List[Dict[str, str]] = field(default_factory=list)
    deliverables: Dict[str, Any] = field(default_factory=dict)
    risk_notes: List[str] = field(default_factory=list)
    next_tracking_fields: List[str] = field(default_factory=list)
    markdown_report: str = ""
    trend_analysis: Optional[Dict[str, Any]] = None
    communication_tips: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "skill_id": self.skill_id,
            "summary": self.summary,
            "known_facts": self.known_facts,
            "analysis": self.analysis,
            "conflict_analysis": self.conflict_analysis,
            "resolution_plans": self.resolution_plans,
            "action_plan": self.action_plan,
            "deliverables": self.deliverables,
            "risk_notes": self.risk_notes,
            "next_tracking_fields": self.next_tracking_fields,
            "markdown_report": self.markdown_report,
            "trend_analysis": self.trend_analysis,
            "communication_tips": self.communication_tips
        }

    def to_json(self, indent: int = 2) -> str:
        """序列化为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent, default=str)


_context_store: Dict[str, Any] = {}


def get_or_create_context(session_id: str) -> Dict[str, Any]:
    """获取或创建会话上下文"""
    if session_id not in _context_store:
        _context_store[session_id] = {"session_id": session_id, "created_at": datetime.now().isoformat()}
    return _context_store[session_id]
