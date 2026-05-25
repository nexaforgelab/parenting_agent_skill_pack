"""家长辅导话术 Agent - 数据模型

增强版本：添加完整类型注解、数据验证方法、序列化支持
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from enum import Enum
import json


class PhraseCategory(Enum):
    """话术类别枚举"""
    ENCOURAGEMENT = "encouragement"
    GUIDANCE = "guidance"
    COMFORT = "comfort"
    QUESTIONING = "questioning"
    PRAISE = "praise"
    LIMIT_SETTING = "limit_setting"
    EMOTION_COACHING = "emotion_coaching"
    ERROR_HANDLING = "error_handling"


class CommunicationStyle(Enum):
    """沟通风格枚举"""
    AUTHORITATIVE = "authoritative"
    PERMISSIVE = "permissive"
    AUTHORITARIAN = "authoritarian"
    NEGLECTFUL = "neglectful"


class ChildEmotionState(Enum):
    """孩子情绪状态枚举"""
    CONFIDENT = "confident"
    ANXIOUS = "anxious"
    FRUSTRATED = "frustrated"
    CONFUSED = "confused"
    BORED = "bored"
    EXCITED = "excited"
    RESISTANT = "resistant"


class TutoringPhase(Enum):
    """辅导阶段枚举"""
    PREPARATION = "preparation"
    INTRODUCTION = "introduction"
    GUIDED_PRACTICE = "guided_practice"
    INDEPENDENT_PRACTICE = "independent_practice"
    REVIEW = "review"
    WRAP_UP = "wrap_up"


@dataclass
class ChildProfile:
    """孩子画像数据模型"""
    name: str = ""
    age: int = 0
    grade: str = ""
    subjects: List[str] = field(default_factory=list)
    learning_style: str = "visual"
    attention_span_minutes: int = 30
    emotional_sensitivity: str = "medium"
    previous_difficulties: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)

    def validate(self) -> List[str]:
        """验证数据"""
        errors = []
        if self.age < 3 or self.age > 18:
            errors.append("年龄必须在3-18岁之间")
        if not self.grade:
            errors.append("年级信息不能为空")
        if self.attention_span_minutes < 5 or self.attention_span_minutes > 120:
            errors.append("专注时长建议在5-120分钟范围内")
        return errors


@dataclass
class TutoringPhrase:
    """辅导话术数据模型"""
    id: str = ""
    category: Union[str, PhraseCategory] = PhraseCategory.GUIDANCE
    phrase_text: str = ""
    applicable_ages: List[int] = field(default_factory=list)
    applicable_subjects: List[str] = field(default_factory=list)
    applicable_emotion_states: List[str] = field(default_factory=list)
    example_usage: str = ""
    effect_description: str = ""
    usage_tips: List[str] = field(default_factory=list)
    timing: str = "during_tutoring"
    tone: str = "warm"
    difficulty_level: str = "intermediate"

    def __post_init__(self):
        """后处理：类型转换"""
        if isinstance(self.category, str):
            try:
                self.category = PhraseCategory(self.category)
            except ValueError:
                self.category = PhraseCategory.GUIDANCE

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "category": self.category.value if isinstance(self.category, Enum) else self.category,
            "phrase_text": self.phrase_text,
            "applicable_ages": self.applicable_ages,
            "applicable_subjects": self.applicable_subjects,
            "applicable_emotion_states": self.applicable_emotion_states,
            "example_usage": self.example_usage,
            "effect_description": self.effect_description,
            "usage_tips": self.usage_tips,
            "timing": self.timing,
            "tone": self.tone,
            "difficulty_level": self.difficulty_level
        }

    def validate(self) -> List[str]:
        """验证数据"""
        errors = []
        if not self.phrase_text or not self.phrase_text.strip():
            errors.append("话术文本不能为空")
        if len(self.phrase_text) > 500:
            errors.append("话术文本不能超过500字符")
        valid_tones = {"warm", "neutral", "firm", "gentle", "enthusiastic"}
        if self.tone not in valid_tones:
            errors.append(f"语气必须是以下之一: {', '.join(valid_tones)}")
        valid_levels = {"beginner", "intermediate", "advanced"}
        if self.difficulty_level not in valid_levels:
            errors.append(f"难度必须是以下之一: {', '.join(valid_levels)}")
        return errors


@dataclass
class ConversationRecord:
    """对话记录数据模型"""
    timestamp: Union[str, datetime] = field(default_factory=lambda: datetime.now())
    tutor_behavior: str = ""
    child_response: str = ""
    child_emotion_before: str = ""
    child_emotion_after: str = ""
    subject: str = ""
    topic: str = ""
    outcome: str = "unknown"
    notes: str = ""

    def __post_init__(self):
        """后处理：类型转换"""
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "tutor_behavior": self.tutor_behavior,
            "child_response": self.child_response,
            "child_emotion_before": self.child_emotion_before,
            "child_emotion_after": self.child_emotion_after,
            "subject": self.subject,
            "topic": self.topic,
            "outcome": self.outcome,
            "notes": self.notes
        }

    def validate(self) -> List[str]:
        """验证数据"""
        errors = []
        if not self.tutor_behavior.strip():
            errors.append("辅导行为描述不能为空")
        valid_outcomes = {"excellent", "good", "neutral", "poor", "failed", "unknown"}
        if self.outcome not in valid_outcomes:
            errors.append(f"结果必须是以下之一: {', '.join(valid_outcomes)}")
        return errors


@dataclass
class PhraseRecommendation:
    """话术推荐数据模型"""
    phrase: TutoringPhrase
    match_score: float = 0.0
    match_reasons: List[str] = field(default_factory=list)
    alternative_phrases: List[TutoringPhrase] = field(default_factory=list)
    timing_advice: str = ""
    expected_effect: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "phrase": self.phrase.to_dict(),
            "match_score": round(self.match_score, 2),
            "match_reasons": self.match_reasons,
            "alternative_phrases": [p.to_dict() for p in self.alternative_phrases],
            "timing_advice": self.timing_advice,
            "expected_effect": self.expected_effect
        }


@dataclass
class TutoringAnalysis:
    """辅导分析数据模型"""
    average_session_length: float = 0.0
    effective_phrase_categories: Dict[str, int] = field(default_factory=dict)
    emotion_change_patterns: Dict[str, str] = field(default_factory=dict)
    common_struggle_topics: List[str] = field(default_factory=list)
    improvement_areas: List[str] = field(default_factory=list)
    success_strategies: List[str] = field(default_factory=list)
    recommended_focus: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)


@dataclass
class SkillInput:
    """技能输入数据模型"""
    child_profile: Dict[str, Any]
    current_problem: str
    tutoring_context: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    preferred_style: str = "warm"
    session_goal: str = ""
    subject: str = ""
    topic: str = ""
    child_emotion_state: str = "neutral"
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
    skill_id: str = "parent_tutoring_phrases"
    summary: List[str] = field(default_factory=list)
    known_facts: List[str] = field(default_factory=list)
    analysis: List[str] = field(default_factory=list)
    recommended_phrases: List[Dict[str, Any]] = field(default_factory=list)
    tutoring_tips: List[str] = field(default_factory=list)
    action_plan: List[Dict[str, str]] = field(default_factory=list)
    deliverables: Dict[str, Any] = field(default_factory=dict)
    risk_notes: List[str] = field(default_factory=list)
    next_tracking_fields: List[str] = field(default_factory=list)
    markdown_report: str = ""
    communication_analysis: Optional[Dict[str, Any]] = None
    phrase_library: List[Dict[str, Any]] = field(default_factory=list)
    session_recommendations: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "skill_id": self.skill_id,
            "summary": self.summary,
            "known_facts": self.known_facts,
            "analysis": self.analysis,
            "recommended_phrases": self.recommended_phrases,
            "tutoring_tips": self.tutoring_tips,
            "action_plan": self.action_plan,
            "deliverables": self.deliverables,
            "risk_notes": self.risk_notes,
            "next_tracking_fields": self.next_tracking_fields,
            "markdown_report": self.markdown_report,
            "communication_analysis": self.communication_analysis,
            "phrase_library": self.phrase_library,
            "session_recommendations": self.session_recommendations
        }

    def to_json(self, indent: int = 2) -> str:
        """序列化为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent, default=str)


@dataclass
class SessionContext:
    """会话上下文数据模型"""
    session_id: str
    created_at: Union[str, datetime] = field(default_factory=lambda: datetime.now())
    last_updated: Union[str, datetime] = field(default_factory=lambda: datetime.now())
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    accumulated_data: Dict[str, Any] = field(default_factory=dict)
    child_state_history: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        """后处理：类型转换"""
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.last_updated, str):
            self.last_updated = datetime.fromisoformat(self.last_updated)

    def add_interaction(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """添加交互记录"""
        interaction = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.conversation_history.append(interaction)
        self.last_updated = datetime.now()

    def update_child_state(self, emotion_state: str, context: str) -> None:
        """更新孩子状态"""
        self.child_state_history.append({
            "timestamp": datetime.now().isoformat(),
            "emotion_state": emotion_state,
            "context": context
        })
        self.last_updated = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "last_updated": self.last_updated.isoformat() if isinstance(self.last_updated, datetime) else self.last_updated,
            "conversation_history": self.conversation_history,
            "accumulated_data": self.accumulated_data,
            "child_state_history": self.child_state_history
        }


_context_store: Dict[str, SessionContext] = {}


def get_or_create_context(session_id: str) -> SessionContext:
    """获取或创建会话上下文"""
    if session_id not in _context_store:
        _context_store[session_id] = SessionContext(session_id=session_id)
    return _context_store[session_id]


def clear_context(session_id: str) -> bool:
    """清除会话上下文"""
    if session_id in _context_store:
        del _context_store[session_id]
        return True
    return False
