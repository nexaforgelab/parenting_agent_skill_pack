"""Data models for 小学生阅读计划 Agent.

这些模型保持轻量，方便 OpenClaw / Hermes / 任意 Python Agent Runtime 直接复用。
提供增强的数据类，包括学习记录、进度统计、推荐、上下文等。
"""
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime
import json


@dataclass
class SkillInput:
    """技能输入数据模型"""
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
        """转换为字典格式"""
        return asdict(self)

    def validate(self) -> List[str]:
        """验证输入数据"""
        errors = []
        if not self.child_profile:
            errors.append("child_profile 不能为空")
        if not self.current_problem or not str(self.current_problem).strip():
            errors.append("current_problem 不能为空")
        if self.history_days < 1:
            errors.append("history_days 必须大于等于 1")
        return errors


@dataclass
class ActionItem:
    """行动计划项数据模型"""
    day: str
    task: str
    owner: str = "家长"
    evidence_to_record: str = "一句话记录执行结果"
    difficulty: str = "低"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)


@dataclass
class LearningRecord:
    """学习记录数据模型"""
    record_id: str
    timestamp: str
    book_title: str = ""
    author: str = ""
    genre: str = "文学"
    pages_read: int = 0
    total_pages: int = 0
    engagement_score: float = 0.0
    reading_duration_minutes: int = 0
    notes: str = ""
    is_completed: bool = False
    feedback: str = ""
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)

    def validate(self) -> List[str]:
        """验证学习记录"""
        errors = []
        if not self.record_id:
            errors.append("record_id 不能为空")
        if self.pages_read < 0:
            errors.append("pages_read 不能为负数")
        if not 0 <= self.engagement_score <= 5:
            errors.append("engagement_score 必须在 0-5 之间")
        return errors

    def get_completion_percentage(self) -> float:
        """获取完成百分比"""
        if self.total_pages == 0:
            return 0.0
        return round(self.pages_read / self.total_pages, 2)

    def is_passed(self, threshold: float = 0.5) -> bool:
        """判断是否达标"""
        return self.get_completion_percentage() >= threshold


@dataclass
class ProgressStats:
    """进度统计数据模型"""
    total_sessions: int = 0
    total_books: int = 0
    total_pages: int = 0
    completion_rate: float = 0.0
    average_engagement: float = 0.0
    recent_trend: str = "insufficient_data"
    favorite_genres: List[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)

    def is_improving(self) -> bool:
        """判断是否在进步"""
        return self.recent_trend == "improving"


@dataclass
class Recommendation:
    """推荐数据模型"""
    recommendation_id: str
    category: str
    priority: str
    title: str
    description: str = ""
    action_items: List[str] = field(default_factory=list)
    expected_benefit: str = ""
    target_mastery_level: str = "LEARNING"
    estimated_duration: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)

    def is_high_priority(self) -> bool:
        """判断是否高优先级"""
        return self.priority in ["high", "高"]


@dataclass
class SessionContext:
    """会话上下文数据模型"""
    session_id: str
    child_id: str
    start_time: str
    current_topic: str = ""
    recent_records: List[Dict[str, Any]] = field(default_factory=list)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    detected_interests: List[str] = field(default_factory=list)
    detected_difficulties: List[str] = field(default_factory=list)
    learning_goals: List[str] = field(default_factory=list)
    parent_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)

    def add_conversation(self, role: str, content: str) -> None:
        """添加对话记录"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })


@dataclass
class SkillOutput:
    """技能输出数据模型"""
    skill_id: str
    summary: List[str]
    known_facts: List[str]
    analysis: List[str]
    action_plan: List[ActionItem]
    deliverables: Dict[str, Any]
    risk_notes: List[str]
    next_tracking_fields: List[str]
    markdown_report: str = ""
    progress: Optional[ProgressStats] = None
    difficulties: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[Recommendation] = field(default_factory=list)
    learning_curve: Optional[Dict[str, Any]] = None
    mastery_level: str = "NOT_STARTED"
    session_context: Optional[SessionContext] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "skill_id": self.skill_id,
            "summary": self.summary,
            "known_facts": self.known_facts,
            "analysis": self.analysis,
            "action_plan": [item.to_dict() if hasattr(item, 'to_dict') else item for item in self.action_plan],
            "deliverables": self.deliverables,
            "risk_notes": self.risk_notes,
            "next_tracking_fields": self.next_tracking_fields,
            "markdown_report": self.markdown_report,
        }
        if self.progress:
            result["progress"] = self.progress.to_dict() if hasattr(self.progress, 'to_dict') else self.progress
        result["difficulties"] = self.difficulties
        result["recommendations"] = [r.to_dict() if hasattr(r, 'to_dict') else r for r in self.recommendations]
        if self.learning_curve:
            result["learning_curve"] = self.learning_curve
        result["mastery_level"] = self.mastery_level
        if self.session_context:
            result["session_context"] = self.session_context.to_dict() if hasattr(self.session_context, 'to_dict') else self.session_context
        return result

    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
