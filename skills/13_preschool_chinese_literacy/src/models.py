"""Data models for 幼儿识字启蒙 Agent.

这些模型保持轻量，方便 OpenClaw / Hermes / 任意 Python Agent Runtime 直接复用。
"""
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
import json


class CharacterCategory(Enum):
    """汉字分类枚举"""
    BASIC = "基础汉字"
    INTERMEDIATE = "进阶汉字"
    ADVANCED = "高级汉字"
    Radicals = "偏旁部首"


class LearningStage(Enum):
    """学习阶段枚举"""
    RECOGNITION = "认识"
    READING = "认读"
    WRITING = "书写"
    MASTERY = "掌握"


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


@dataclass
class CharacterRecord:
    """汉字学习记录数据类"""
    record_id: str = ""
    timestamp: str = ""
    character: str = ""
    pinyin: str = ""
    meaning: str = ""
    stroke_count: int = 0
    learning_stage: str = LearningStage.RECOGNITION.value
    practice_count: int = 0
    correct_count: int = 0
    difficulty_rating: float = 0.0
    associated_words: List[str] = field(default_factory=list)

    def validate(self) -> List[str]:
        """验证汉字记录的有效性"""
        errors = []
        if not self.record_id:
            errors.append("record_id 不能为空")
        if not self.character:
            errors.append("character 不能为空")
        if self.correct_count > self.practice_count:
            errors.append("correct_count 不能超过 practice_count")
        return errors

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return asdict(self)


@dataclass
class ProgressStats:
    """学习进度统计数据类"""
    total_characters: int = 0
    mastered_characters: int = 0
    learning_characters: int = 0
    total_practice: int = 0
    average_accuracy: float = 0.0
    current_streak: int = 0
    longest_streak: int = 0
    category_breakdown: Dict[str, int] = field(default_factory=dict)
    difficult_characters: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return asdict(self)

    def calculate_mastery_rate(self) -> float:
        """计算掌握率"""
        if self.total_characters == 0:
            return 0.0
        return round(self.mastered_characters / self.total_characters * 100, 2)


@dataclass
class Recommendation:
    """个性化推荐数据类"""
    recommendation_id: str = ""
    category: str = ""
    priority: str = "medium"
    title: str = ""
    description: str = ""
    action_items: List[str] = field(default_factory=list)
    suggested_characters: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return asdict(self)


@dataclass
class SessionContext:
    """会话上下文数据类"""
    session_id: str = ""
    child_id: str = ""
    start_time: str = ""
    current_learning_chars: List[str] = field(default_factory=list)
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return asdict(self)


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
    character_records: List[CharacterRecord] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
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
            "recommendations": [r.to_dict() for r in self.recommendations],
            "character_records": [r.to_dict() for r in self.character_records]
        }

    def to_json(self, indent: int = 2) -> str:
        """序列化为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)