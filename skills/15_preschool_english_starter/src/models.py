"""Data models for 幼儿英语启蒙 Agent."""
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
import json


class VocabCategory(Enum):
    """词汇分类枚举"""
    NOUNS = "名词"
    VERBS = "动词"
    ADJECTIVES = "形容词"
    COLORS = "颜色"
    NUMBERS = "数字"
    ANIMALS = "动物"
    FAMILY = "家庭"


class LearningLevel(Enum):
    """学习水平枚举"""
    BEGINNER = "入门"
    INTERMEDIATE = "中级"
    ADVANCED = "高级"


@dataclass
class SkillInput:
    child_profile: Dict[str, Any]
    current_problem: str
    family_context: Dict[str, Any] = field(default_factory=dict)
    goal: str = ""
    raw_records: List[Dict[str, Any]] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    history_days: int = 7
    privacy_mode: str = "family_local_first"

    def validate(self) -> List[str]:
        errors = []
        if not isinstance(self.child_profile, dict):
            errors.append("child_profile 必须是字典类型")
        if not self.current_problem or not str(self.current_problem).strip():
            errors.append("current_problem 不能为空")
        return errors

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ActionItem:
    day: str
    task: str
    owner: str = "家长"
    evidence_to_record: str = "一句话记录执行结果"
    difficulty: str = "低"

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


@dataclass
class VocabRecord:
    """词汇学习记录"""
    record_id: str = ""
    timestamp: str = ""
    word: str = ""
    translation: str = ""
    pronunciation: str = ""
    category: str = VocabCategory.NOUNS.value
    mastery_score: float = 0.0
    practice_count: int = 0
    correct_count: int = 0

    def validate(self) -> List[str]:
        errors = []
        if not self.record_id:
            errors.append("record_id 不能为空")
        if not self.word:
            errors.append("word 不能为空")
        return errors

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProgressStats:
    """进度统计数据"""
    total_words: int = 0
    mastered_words: int = 0
    learning_words: int = 0
    total_practice: int = 0
    average_mastery: float = 0.0
    current_streak: int = 0
    category_breakdown: Dict[str, int] = field(default_factory=dict)
    difficult_words: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def calculate_mastery_rate(self) -> float:
        if self.total_words == 0:
            return 0.0
        return round(self.mastered_words / self.total_words * 100, 2)


@dataclass
class Recommendation:
    recommendation_id: str = ""
    category: str = ""
    priority: str = "medium"
    title: str = ""
    description: str = ""
    action_items: List[str] = field(default_factory=list)
    suggested_words: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SessionContext:
    session_id: str = ""
    child_id: str = ""
    start_time: str = ""
    current_words: List[str] = field(default_factory=list)
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
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
    vocab_records: List[VocabRecord] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
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
            "vocab_records": [r.to_dict() for r in self.vocab_records]
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)