"""Data models for 小学作业陪伴 Agent.

这些模型保持轻量，方便 OpenClaw / Hermes / 任意 Python Agent Runtime 直接复用。
"""
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
import json


class SubjectEnum(Enum):
    """学科枚举"""
    CHINESE = "语文"
    MATH = "数学"
    ENGLISH = "英语"
    SCIENCE = "科学"
    OTHER = "其他"


class DifficultyLevel(Enum):
    """难度等级"""
    EASY = "简单"
    MEDIUM = "中等"
    HARD = "困难"


class CompletionStatus(Enum):
    """完成状态"""
    NOT_STARTED = "未开始"
    IN_PROGRESS = "进行中"
    COMPLETED = "已完成"
    NEEDS_HELP = "需要帮助"


@dataclass
class SkillInput:
    """技能输入模型"""
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
        """转换为字典"""
        return asdict(self)

    def validate(self) -> List[str]:
        """验证输入数据"""
        errors = []
        if not isinstance(self.child_profile, dict):
            errors.append("child_profile 必须是字典类型")
        if not self.current_problem or not str(self.current_problem).strip():
            errors.append("current_problem 不能为空")
        if self.history_days < 1 or self.history_days > 365:
            errors.append("history_days 必须在 1-365 之间")
        if self.privacy_mode not in ["anonymous", "family_local_first", "full_disclosure"]:
            errors.append("privacy_mode 必须是 'anonymous', 'family_local_first' 或 'full_disclosure'")
        return errors


@dataclass
class ActionItem:
    """行动计划项"""
    day: str
    task: str
    owner: str = "家长"
    evidence_to_record: str = "一句话记录执行结果"
    difficulty: str = "低"

    def to_dict(self) -> Dict[str, str]:
        """转换为字典"""
        return asdict(self)


@dataclass
class HomeworkRecord:
    """作业记录模型

    用于记录单次作业的详细信息
    """
    subject: str
    content: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_minutes: int = 0
    status: str = "未开始"
    difficulty: str = "中等"
    distractions: List[str] = field(default_factory=list)
    help_requests: int = 0
    completion_rate: float = 0.0
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HomeworkRecord":
        """从字典创建实例"""
        return cls(**data)

    def is_overdue(self) -> bool:
        """检查是否超时"""
        if self.duration_minutes <= 0:
            return False
        expected_time = self._get_expected_time()
        return self.duration_minutes > expected_time * 1.5

    def _get_expected_time(self) -> int:
        """获取预计时间(分钟)"""
        base_time = 30
        if self.difficulty == "简单":
            return base_time
        elif self.difficulty == "困难":
            return base_time * 2
        return base_time * 1.5


@dataclass
class ProgressStats:
    """学习进度统计模型

    用于跟踪和分析学习进度
    """
    total_homework_count: int = 0
    completed_count: int = 0
    average_duration: float = 0.0
    average_completion_rate: float = 0.0
    total_distraction_events: int = 0
    subjects_mastered: List[str] = field(default_factory=list)
    subjects_needing_work: List[str] = field(default_factory=list)
    weekly_improvement: float = 0.0
    motivation_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    def get_completion_rate(self) -> float:
        """获取完成率"""
        if self.total_homework_count == 0:
            return 0.0
        return (self.completed_count / self.total_homework_count) * 100

    def to_summary(self) -> str:
        """生成摘要文本"""
        return f"""
总作业数: {self.total_homework_count}
已完成: {self.completed_count}
完成率: {self.get_completion_rate():.1f}%
平均用时: {self.average_duration:.1f}分钟
本周进步: {self.weekly_improvement:.1f}%
""".strip()


@dataclass
class KnowledgePoint:
    """知识点掌握度模型

    用于追踪特定知识点的掌握程度
    """
    point_id: str
    point_name: str
    subject: str
    mastery_level: float = 0.0
    practice_count: int = 0
    correct_count: int = 0
    last_practiced: Optional[str] = None
    weakness_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    def get_mastery_percentage(self) -> float:
        """获取掌握百分比"""
        return self.mastery_level * 100

    def needs_review(self) -> bool:
        """是否需要复习"""
        if self.last_practiced is None:
            return True
        days_since = (datetime.now() - datetime.fromisoformat(self.last_practiced)).days
        return days_since > 3 or self.mastery_level < 0.7


@dataclass
class MistakeRecord:
    """错题记录模型

    用于记录和分析作业中的错误
    """
    mistake_id: str
    subject: str
    topic: str
    description: str
    wrong_answer: str
    correct_answer: str
    error_type: str
    root_cause: str = ""
    related_knowledge_points: List[str] = field(default_factory=list)
    practice_history: List[Dict[str, Any]] = field(default_factory=list)
    mastery_level: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    def get_error_category(self) -> str:
        """获取错误类别"""
        if "计算" in self.error_type:
            return "计算错误"
        elif "理解" in self.error_type:
            return "理解错误"
        elif "粗心" in self.error_type:
            return "粗心大意"
        return "其他错误"


@dataclass
class SessionContext:
    """会话上下文模型

    用于维护多轮对话的上下文信息
    """
    session_id: str
    start_time: str
    child_id: str
    grade_level: int = 0
    current_subject: Optional[str] = None
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    recent_performance: List[Dict[str, Any]] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    def add_interaction(self, role: str, content: str) -> None:
        """添加对话交互"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def get_recent_interactions(self, count: int = 5) -> List[Dict[str, str]]:
        """获取最近的交互"""
        return self.conversation_history[-count:]

    def to_json(self) -> str:
        """序列化为JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "SessionContext":
        """从JSON反序列化"""
        data = json.loads(json_str)
        return cls(**data)


@dataclass
class Recommendation:
    """个性化推荐模型

    基于学习数据生成的个性化建议
    """
    recommendation_id: str
    category: str
    priority: str
    title: str
    description: str
    target_knowledge_points: List[str] = field(default_factory=list)
    suggested_duration: int = 0
    difficulty_adjustment: Optional[str] = None
    confidence_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    def is_high_priority(self) -> bool:
        """是否为高优先级"""
        return self.priority in ["高", "紧急", "high", "urgent"]

    def to_action_item(self) -> Dict[str, str]:
        """转换为行动计划项"""
        return {
            "day": "D1",
            "task": f"{self.title}: {self.description}",
            "owner": "家长/孩子",
            "evidence_to_record": f"执行时间、效果反馈",
            "difficulty": self.priority
        }


@dataclass
class SkillOutput:
    """技能输出模型"""
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
    session_context: Optional[SessionContext] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "skill_id": self.skill_id,
            "summary": self.summary,
            "known_facts": self.known_facts,
            "analysis": self.analysis,
            "action_plan": [item.to_dict() if isinstance(item, ActionItem) else item for item in self.action_plan],
            "deliverables": self.deliverables,
            "risk_notes": self.risk_notes,
            "next_tracking_fields": self.next_tracking_fields,
            "markdown_report": self.markdown_report,
            "progress_stats": self.progress_stats.to_dict() if self.progress_stats else None,
            "recommendations": [rec.to_dict() for rec in self.recommendations],
            "session_context": self.session_context.to_dict() if self.session_context else None
        }
        return result

    def to_json(self) -> str:
        """序列化为JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
