"""Data models for 绘本共读 Agent.

这些模型保持轻量，方便 OpenClaw / Hermes / 任意 Python Agent Runtime 直接复用。
"""
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
import json


class MasteryLevel(Enum):
    """掌握程度枚举"""
    NOT_STARTED = "未开始"
    LEARNING = "学习中"
    FAMILIAR = "熟悉"
    MASTERED = "已掌握"


class DifficultyLevel(Enum):
    """难度等级枚举"""
    EASY = "简单"
    MEDIUM = "中等"
    HARD = "困难"


class InteractionType(Enum):
    """互动类型枚举"""
    READING = "朗读"
    QUESTIONING = "提问"
    DISCUSSION = "讨论"
    GAME = "游戏"
    CREATIVE = "创意"


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
class LearningRecord:
    """学习记录数据类

    用于记录单次学习活动的详细信息，支持数据分析和进度追踪。
    """
    record_id: str = ""
    timestamp: str = ""
    book_title: str = ""
    interaction_type: str = InteractionType.QUESTIONING.value
    duration_minutes: int = 0
    questions_asked: int = 0
    questions_answered: int = 0
    engagement_score: float = 0.0
    comprehension_level: str = MasteryLevel.LEARNING.value
    child_reaction: str = ""
    parent_observation: str = ""
    topics_covered: List[str] = field(default_factory=list)
    emotions_expressed: List[str] = field(default_factory=list)
    new_words_learned: List[str] = field(default_factory=list)

    def validate(self) -> List[str]:
        """验证学习记录的有效性"""
        errors = []
        if not self.record_id:
            errors.append("record_id 不能为空")
        if self.duration_minutes < 0:
            errors.append("duration_minutes 不能为负数")
        if self.engagement_score < 0.0 or self.engagement_score > 10.0:
            errors.append("engagement_score 必须在 0.0-10.0 之间")
        if self.questions_answered > self.questions_asked:
            errors.append("回答的问题数不能超过提问数")
        return errors

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LearningRecord":
        """从字典创建实例"""
        return cls(**data)

    def calculate_success_rate(self) -> float:
        """计算问题回答成功率"""
        if self.questions_asked == 0:
            return 0.0
        return round(self.questions_answered / self.questions_asked * 100, 2)

    def is_complete(self) -> bool:
        """判断记录是否完整"""
        return (
            bool(self.record_id) and
            bool(self.book_title) and
            self.duration_minutes > 0
        )


@dataclass
class ProgressStats:
    """学习进度统计数据类

    汇总学习进度、掌握程度等统计信息。
    """
    total_sessions: int = 0
    total_minutes: int = 0
    total_books_read: int = 0
    total_questions_asked: int = 0
    total_questions_answered: int = 0
    average_engagement: float = 0.0
    average_comprehension: float = 0.0
    mastered_books: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    most_used_interaction: str = ""
    favorite_topics: List[str] = field(default_factory=list)
    difficult_topics: List[str] = field(default_factory=list)
    weekly_progress: List[Dict[str, Any]] = field(default_factory=list)
    monthly_trend: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProgressStats":
        """从字典创建实例"""
        return cls(**data)

    def calculate_overall_mastery(self) -> float:
        """计算整体掌握度"""
        if self.total_sessions == 0:
            return 0.0
        return round(
            (self.mastered_books / max(self.total_books_read, 1)) * 50 +
            (self.total_questions_answered / max(self.total_questions_asked, 1)) * 30 +
            (self.average_engagement / 10.0) * 20,
            2
        )

    def get_streak_status(self) -> str:
        """获取连续学习状态描述"""
        if self.current_streak == 0:
            return "未开始连续学习"
        elif self.current_streak < 3:
            return f"刚开始连续学习 ({self.current_streak} 天)"
        elif self.current_streak < 7:
            return f"保持学习习惯 ({self.current_streak} 天)"
        else:
            return f"优秀习惯养成 ({self.current_streak} 天)"


@dataclass
class Recommendation:
    """个性化推荐数据类

    基于学习数据生成的个性化学习建议。
    """
    recommendation_id: str = ""
    category: str = ""
    priority: str = "medium"
    title: str = ""
    description: str = ""
    action_items: List[str] = field(default_factory=list)
    expected_benefit: str = ""
    target_mastery_level: str = ""
    estimated_duration: str = ""
    resources_needed: List[str] = field(default_factory=list)

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
    current_topic: str = ""
    recent_records: List[LearningRecord] = field(default_factory=list)
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    detected_interests: List[str] = field(default_factory=list)
    detected_difficulties: List[str] = field(default_factory=list)
    learning_goals: List[str] = field(default_factory=list)
    parent_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        data = asdict(self)
        data["recent_records"] = [r.to_dict() if isinstance(r, LearningRecord) else r for r in self.recent_records]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionContext":
        """从字典创建实例"""
        if "recent_records" in data:
            data["recent_records"] = [
                LearningRecord.from_dict(r) if isinstance(r, dict) else r
                for r in data["recent_records"]
            ]
        return cls(**data)

    def add_conversation(self, role: str, message: str) -> None:
        """添加对话历史"""
        self.conversation_history.append({
            "role": role,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })

    def get_recent_interest(self, limit: int = 5) -> List[str]:
        """获取最近的兴趣点"""
        return self.detected_interests[-limit:] if self.detected_interests else []

    def update_learning_progress(self, record: LearningRecord) -> None:
        """更新学习进度记录"""
        self.recent_records.append(record)
        if len(self.recent_records) > 50:
            self.recent_records = self.recent_records[-50:]


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
    learning_records: List[LearningRecord] = field(default_factory=list)
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
            "learning_records": [r.to_dict() if isinstance(r, LearningRecord) else r for r in self.learning_records],
            "session_context": self.session_context.to_dict() if self.session_context else None
        }
        return data

    def to_json(self, indent: int = 2) -> str:
        """序列化为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)