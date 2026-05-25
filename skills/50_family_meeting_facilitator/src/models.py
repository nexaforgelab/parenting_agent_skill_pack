"""Data models for 家庭会议主持 Agent.

这些模型保持轻量，方便 OpenClaw / Hermes / 任意 Python Agent Runtime 直接复用。
增强版本：添加更多数据类、类型注解、数据验证和序列化方法。
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from enum import Enum
import json


class MeetingType(Enum):
    """会议类型枚举"""
    WEEKLY_PLANNING = "weekly_planning"
    MONTHLY_REVIEW = "monthly_review"
    PROBLEM_SOLVING = "problem_solving"
    CELEBRATION = "celebration"
    RULES_UPDATE = "rules_update"
    SCHEDULE_DISCUSSION = "schedule_discussion"


class ParticipantRole(Enum):
    """参与者角色枚举"""
    FACILITATOR = "facilitator"
    PARTICIPANT = "participant"
    OBSERVER = "observer"
    CHILD = "child"
    GUEST = "guest"


class IssuePriority(Enum):
    """议题优先级枚举"""
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class DecisionStatus(Enum):
    """决策状态枚举"""
    PENDING = "pending"
    DISCUSSED = "discussed"
    DECIDED = "decided"
    DEFERRED = "deferred"
    REJECTED = "rejected"


@dataclass
class MeetingAgenda:
    """会议议程数据模型

    Attributes:
        topic: 议题
        presenter: 提出人
        priority: 优先级
        time_allocation: 时间分配（分钟）
        notes: 备注
    """
    topic: str
    presenter: str = ""
    priority: str = "normal"
    time_allocation: int = 10
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "topic": self.topic,
            "presenter": self.presenter,
            "priority": self.priority,
            "time_allocation": self.time_allocation,
            "notes": self.notes
        }


@dataclass
class MeetingParticipant:
    """会议参与者数据模型

    Attributes:
        name: 姓名
        role: 角色
        attendance: 是否出席
        contributions: 贡献
    """
    name: str
    role: str = "participant"
    attendance: bool = True
    contributions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "role": self.role,
            "attendance": self.attendance,
            "contributions": self.contributions
        }


@dataclass
class MeetingDecision:
    """会议决议数据模型

    Attributes:
        topic: 议题
        decision: 决议内容
        decision_by: 决策人
        status: 状态
        follow_up: 后续行动
        deadline: 截止日期
    """
    topic: str
    decision: str
    decision_by: str = ""
    status: str = "decided"
    follow_up: List[str] = field(default_factory=list)
    deadline: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "topic": self.topic,
            "decision": self.decision,
            "decision_by": self.decision_by,
            "status": self.status,
            "follow_up": self.follow_up,
            "deadline": self.deadline
        }


@dataclass
class MeetingRecord:
    """会议记录数据模型

    Attributes:
        date: 日期
        meeting_type: 会议类型
        participants: 参与者
        agenda: 议程列表
        decisions: 决议列表
        action_items: 行动项目
        summary: 摘要
        next_meeting: 下次会议
    """
    date: Union[str, date]
    meeting_type: str
    participants: List[Dict[str, Any]] = field(default_factory=list)
    agenda: List[Dict[str, Any]] = field(default_factory=list)
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    action_items: List[Dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    next_meeting: str = ""

    def __post_init__(self):
        if isinstance(self.date, str):
            try:
                self.date = date.fromisoformat(self.date)
            except ValueError:
                self.date = date.today()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "date": self.date.isoformat() if isinstance(self.date, date) else str(self.date),
            "meeting_type": self.meeting_type,
            "participants": self.participants,
            "agenda": self.agenda,
            "decisions": self.decisions,
            "action_items": self.action_items,
            "summary": self.summary,
            "next_meeting": self.next_meeting
        }


@dataclass
class ActionItem:
    """行动项目数据模型"""
    day: str
    task: str
    owner: str = "家长"
    evidence_to_record: str = "一句话记录执行结果"
    difficulty: str = "低"

    def to_dict(self) -> Dict[str, str]:
        """转换为字典"""
        return {
            "day": self.day,
            "task": self.task,
            "owner": self.owner,
            "evidence_to_record": self.evidence_to_record,
            "difficulty": self.difficulty
        }


@dataclass
class SkillInput:
    """Skill输入数据模型"""
    child_profile: Dict[str, Any]
    current_problem: str
    family_context: Dict[str, Any] = field(default_factory=dict)
    goal: str = ""
    raw_records: List[Dict[str, Any]] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    history_days: int = 7
    privacy_mode: str = "family_local_first"

    def validate(self) -> List[str]:
        """验证输入数据"""
        errors = []
        if not isinstance(self.child_profile, dict):
            errors.append("child_profile 必须是字典类型")
        if not str(self.current_problem or "").strip():
            errors.append("current_problem 不能为空")
        return errors

    def to_json(self) -> str:
        """序列化为JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "child_profile": self.child_profile,
            "current_problem": self.current_problem,
            "family_context": self.family_context,
            "goal": self.goal,
            "raw_records": self.raw_records,
            "preferences": self.preferences,
            "attachments": self.attachments,
            "history_days": self.history_days,
            "privacy_mode": self.privacy_mode
        }


@dataclass
class SkillOutput:
    """Skill输出数据模型"""
    skill_id: str
    summary: List[str] = field(default_factory=list)
    known_facts: List[str] = field(default_factory=list)
    analysis: List[str] = field(default_factory=list)
    action_plan: List[ActionItem] = field(default_factory=list)
    deliverables: Dict[str, Any] = field(default_factory=dict)
    risk_notes: List[str] = field(default_factory=list)
    next_tracking_fields: List[str] = field(default_factory=list)
    markdown_report: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "skill_id": self.skill_id,
            "summary": self.summary,
            "known_facts": self.known_facts,
            "analysis": self.analysis,
            "action_plan": [item.to_dict() if hasattr(item, 'to_dict') else item for item in self.action_plan],
            "deliverables": self.deliverables,
            "risk_notes": self.risk_notes,
            "next_tracking_fields": self.next_tracking_fields,
            "markdown_report": self.markdown_report
        }


@dataclass
class TrendData:
    """趋势数据模型"""
    metric_name: str
    current_value: float = 0.0
    previous_value: float = 0.0
    trend_direction: str = "stable"
    trend_percentage: float = 0.0
    data_points: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "metric_name": self.metric_name,
            "current_value": self.current_value,
            "previous_value": self.previous_value,
            "trend_direction": self.trend_direction,
            "trend_percentage": self.trend_percentage,
            "data_points": self.data_points
        }


@dataclass
class Alert:
    """预警数据模型"""
    alert_type: str
    severity: str
    message: str
    timestamp: str = ""
    recommendation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "alert_type": self.alert_type,
            "severity": self.severity,
            "message": self.message,
            "timestamp": self.timestamp,
            "recommendation": self.recommendation
        }