"""Data models for 睡前故事生成 Agent.

这些模型保持轻量，方便 OpenClaw / Hermes / 任意 Python Agent Runtime 直接复用。
"""
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
import json


class StoryTheme(Enum):
    """故事主题枚举"""
    ADVENTURE = "冒险"
    FRIENDSHIP = "友谊"
    FAMILY = "家庭"
    NATURE = "自然"
    BRAVERY = "勇敢"
    IMAGINATION = "想象力"
    LEARNING = "学习"
    PEACE = "温馨"


class StoryLength(Enum):
    """故事长度枚举"""
    SHORT = "短篇 (3-5分钟)"
    MEDIUM = "中篇 (5-8分钟)"
    LONG = "长篇 (8-12分钟)"


class StoryTone(Enum):
    """故事语气枚举"""
    GENTLE = "温柔"
    PLAYFUL = "活泼"
    EXCITING = "刺激"
    EDUCATIONAL = "教育性"
    FANTASY = "幻想"


@dataclass
class SkillInput:
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
        """验证输入数据的有效性"""
        errors = []
        if not isinstance(self.child_profile, dict):
            errors.append("child_profile 必须是字典类型")
        if not self.current_problem or not str(self.current_problem).strip():
            errors.append("current_problem 不能为空")
        if self.history_days < 1 or self.history_days > 365:
            errors.append("history_days 必须在 1-365 之间")
        if self.privacy_mode not in {"anonymous", "family_local_first", "full_shared"}:
            errors.append("privacy_mode 值无效")
        return errors

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return asdict(self)


@dataclass
class ActionItem:
    day: str
    task: str
    owner: str = "家长"
    evidence_to_record: str = "一句话记录执行结果"
    difficulty: str = "低"

    def to_dict(self) -> Dict[str, str]:
        """序列化为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "ActionItem":
        """从字典创建实例"""
        return cls(**data)


@dataclass
class StoryRecord:
    """故事记录数据类

    用于记录单次讲故事的详细信息。
    """
    record_id: str = ""
    timestamp: str = ""
    story_title: str = ""
    story_theme: str = StoryTheme.ADVENTURE.value
    story_length: str = StoryLength.SHORT.value
    duration_minutes: int = 0
    child_engagement: float = 0.0
    fall_asleep_time: str = ""
    repeated_story: bool = False
    favorite_character: str = ""
    parent_notes: str = ""
    themes_covered: List[str] = field(default_factory=list)

    def validate(self) -> List[str]:
        """验证故事记录的有效性"""
        errors = []
        if not self.record_id:
            errors.append("record_id 不能为空")
        if self.duration_minutes < 0:
            errors.append("duration_minutes 不能为负数")
        if self.child_engagement < 0.0 or self.child_engagement > 10.0:
            errors.append("child_engagement 必须在 0.0-10.0 之间")
        return errors

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StoryRecord":
        """从字典创建实例"""
        return cls(**data)


@dataclass
class ProgressStats:
    """学习进度统计数据类

    汇总讲故事进度、偏好等统计信息。
    """
    total_stories: int = 0
    total_minutes: int = 0
    average_engagement: float = 0.0
    favorite_themes: List[str] = field(default_factory=list)
    favorite_characters: List[str] = field(default_factory=list)
    repeated_stories: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    stories_by_theme: Dict[str, int] = field(default_factory=dict)
    favorite_time_slots: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProgressStats":
        """从字典创建实例"""
        return cls(**data)

    def calculate_storytelling_skill(self) -> float:
        """计算讲故事技能得分"""
        if self.total_stories == 0:
            return 0.0
        return round(
            (self.total_stories / 50) * 30 +
            (self.average_engagement / 10.0) * 50 +
            (self.repeated_stories / self.total_stories * 10) if self.total_stories > 0 else 0,
            2
        )


@dataclass
class Recommendation:
    """个性化推荐数据类

    基于讲故事数据生成的个性化建议。
    """
    recommendation_id: str = ""
    category: str = ""
    priority: str = "medium"
    title: str = ""
    description: str = ""
    action_items: List[str] = field(default_factory=list)
    expected_benefit: str = ""
    story_suggestions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Recommendation":
        """从字典创建实例"""
        return cls(**data)

    def is_high_priority(self) -> bool:
        """判断是否为高优先级推荐"""
        return self.priority in {"high", "urgent"}


@dataclass
class SessionContext:
    """会话上下文数据类

    支持多轮对话的上下文记忆和管理。
    """
    session_id: str = ""
    child_id: str = ""
    start_time: str = ""
    current_theme: str = ""
    favorite_stories: List[Dict[str, Any]] = field(default_factory=list)
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    detected_interests: List[str] = field(default_factory=list)
    storytelling_goals: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionContext":
        """从字典创建实例"""
        return cls(**data)

    def add_story_to_favorites(self, story: Dict[str, Any]) -> None:
        """添加故事到收藏"""
        self.favorite_stories.append(story)
        if len(self.favorite_stories) > 20:
            self.favorite_stories = self.favorite_stories[-20:]


@dataclass
class SkillOutput:
    skill_id: str
    summary: List[str]
    known_facts: List[str]
    analysis: List[str]
    action_plan: List[ActionItem]
    deliverables: Dict[str, Any]
    risk_notes: List[str]
    next_tracking_fields: List[str]
    markdown_report: str = ""
    progress_stats: Optional[ProgressStats] = None
    recommendations: List[Recommendation] = field(default_factory=list)
    story_records: List[StoryRecord] = field(default_factory=list)
    session_context: Optional[SessionContext] = None

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        data = {
            "skill_id": self.skill_id,
            "summary": self.summary,
            "known_facts": self.known_facts,
            "analysis": self.analysis,
            "action_plan": [a.to_dict() if isinstance(a, ActionItem) else a for a in self.action_plan],
            "deliverables": self.deliverables,
            "risk_notes": self.risk_notes,
            "next_tracking_fields": self.next_tracking_fields,
            "markdown_report": self.markdown_report,
            "progress_stats": self.progress_stats.to_dict() if self.progress_stats else None,
            "recommendations": [r.to_dict() if isinstance(r, Recommendation) else r for r in self.recommendations],
            "story_records": [r.to_dict() if isinstance(r, StoryRecord) else r for r in self.story_records],
            "session_context": self.session_context.to_dict() if self.session_context else None
        }
        return data

    def to_json(self, indent: int = 2) -> str:
        """序列化为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)