"""Data models for 小学错题本 Agent.

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


class ErrorType(Enum):
    """错误类型枚举"""
    CARELESS = "粗心大意"
    MISUNDERSTANDING = "理解错误"
    KNOWLEDGE_GAP = "知识盲点"
    CALCULATION = "计算错误"
    APPLICATION = "应用困难"


class MasteryLevel(Enum):
    """掌握程度枚举"""
    NOT_MASTERED = "未掌握"
    PARTIALLY = "部分掌握"
    MOSTLY = "大部分掌握"
    FULLY = "完全掌握"


class ReviewStatus(Enum):
    """复习状态"""
    PENDING = "待复习"
    REVIEWING = "复习中"
    REVIEWED = "已复习"
    MASTERED = "已掌握"


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
class MistakeRecord:
    """错题记录模型

    用于记录单次错题的详细信息
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
    review_count: int = 0
    last_reviewed: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MistakeRecord":
        """从字典创建实例"""
        return cls(**data)

    def get_error_category(self) -> str:
        """获取错误类别"""
        if "计算" in self.error_type:
            return "计算错误"
        elif "理解" in self.error_type:
            return "理解错误"
        elif "粗心" in self.error_type:
            return "粗心大意"
        elif "知识" in self.error_type:
            return "知识盲点"
        return "其他错误"

    def needs_review(self) -> bool:
        """是否需要复习"""
        if self.last_reviewed is None:
            return True
        try:
            last_date = datetime.fromisoformat(self.last_reviewed)
            days_since = (datetime.now() - last_date).days
            return days_since > 3 or self.mastery_level < 0.8
        except (ValueError, TypeError):
            return True

    def should_spaced_repetition(self) -> bool:
        """是否应该使用间隔重复"""
        intervals = [1, 3, 7, 14, 30]
        if self.review_count >= len(intervals):
            return True
        return (datetime.now() - datetime.fromisoformat(self.last_reviewed)).days >= intervals[self.review_count]


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
    wrong_count: int = 0
    last_practiced: Optional[str] = None
    weakness_type: Optional[str] = None
    related_mistakes: List[str] = field(default_factory=list)

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
        try:
            days_since = (datetime.now() - datetime.fromisoformat(self.last_practiced)).days
            return days_since > 3 or self.mastery_level < 0.7
        except (ValueError, TypeError):
            return True

    def update_mastery(self, correct: bool) -> None:
        """更新掌握度"""
        self.practice_count += 1
        if correct:
            self.correct_count += 1
        else:
            self.wrong_count += 1
        self.mastery_level = self.correct_count / self.practice_count if self.practice_count > 0 else 0


@dataclass
class ProgressStats:
    """学习进度统计模型

    用于跟踪和分析学习进度
    """
    total_mistakes: int = 0
    mastered_count: int = 0
    review_pending: int = 0
    average_mastery: float = 0.0
    total_reviews: int = 0
    subjects_with_most_mistakes: List[str] = field(default_factory=list)
    weekly_review_count: int = 0
    improvement_rate: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    def get_mastery_rate(self) -> float:
        """获取掌握率"""
        if self.total_mistakes == 0:
            return 0.0
        return (self.mastered_count / self.total_mistakes) * 100

    def to_summary(self) -> str:
        """生成摘要文本"""
        return f"""
总错题数: {self.total_mistakes}
已掌握: {self.mastered_count}
掌握率: {self.get_mastery_rate():.1f}%
平均掌握度: {self.average_mastery:.1f}%
本周复习: {self.weekly_review_count}次
进步幅度: {self.improvement_rate:.1f}%
""".strip()


@dataclass
class ReviewPlan:
    """复习计划模型

    用于制定和跟踪错题复习计划
    """
    plan_id: str
    start_date: str
    end_date: str
    target_mistakes: List[str] = field(default_factory=list)
    daily_review_count: int = 5
    status: str = "进行中"
    completed_mistakes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    def get_progress(self) -> float:
        """获取完成进度"""
        if not self.target_mistakes:
            return 0.0
        return (len(self.completed_mistakes) / len(self.target_mistakes)) * 100


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
    mistake_records: List[MistakeRecord] = field(default_factory=list)
    knowledge_points: List[KnowledgePoint] = field(default_factory=list)
    review_plan: Optional[ReviewPlan] = None
    recommendations: List[Recommendation] = field(default_factory=list)
    progress_stats: Optional[ProgressStats] = None

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
            "mistake_records": [m.to_dict() for m in self.mistake_records],
            "knowledge_points": [k.to_dict() for k in self.knowledge_points],
            "review_plan": self.review_plan.to_dict() if self.review_plan else None,
            "recommendations": [rec.to_dict() for rec in self.recommendations],
            "progress_stats": self.progress_stats.to_dict() if self.progress_stats else None
        }
        return result

    def to_json(self) -> str:
        """序列化为JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
