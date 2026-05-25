"""Data models for 小学看图写话 Agent.

这些模型保持轻量，方便 OpenClaw / Hermes / 任意 Python Agent Runtime 直接复用。
"""
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
import json


class WritingStage(Enum):
    """写作阶段"""
    OBSERVATION = "观察图片"
    ORAL_EXPRESSION = "口头表达"
    DRAFTING = "草稿撰写"
    REVISION = "修改润色"


class ExpressionLevel(Enum):
    """表达水平"""
    BEGINNER = "初级"
    INTERMEDIATE = "中级"
    ADVANCED = "高级"


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
class WritingRecord:
    """写作记录模型"""
    record_id: str
    picture_description: str = ""
    draft_content: str = ""
    final_content: str = ""
    observation_points: List[str] = field(default_factory=list)
    guided_questions: List[str] = field(default_factory=list)
    expressions_used: List[str] = field(default_factory=list)
    word_count: int = 0
    expression_score: float = 0.0
    structure_score: float = 0.0
    creativity_score: float = 0.0
    overall_score: float = 0.0
    improvement_suggestions: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class ObservationGuide:
    """观察引导模型"""
    characters: List[str] = field(default_factory=list)
    setting: str = ""
    actions: List[str] = field(default_factory=list)
    emotions: List[str] = field(default_factory=list)
    suggested_elements: List[str] = field(default_factory=list)


@dataclass
class ProgressStats:
    """学习进度统计模型"""
    total_writings: int = 0
    average_word_count: float = 0.0
    average_expression_score: float = 0.0
    average_structure_score: float = 0.0
    average_creativity_score: float = 0.0
    weekly_improvement: float = 0.0
    common_weaknesses: List[str] = field(default_factory=list)
    strong_areas: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    def get_average_overall_score(self) -> float:
        """获取平均总分"""
        scores = [self.average_expression_score, self.average_structure_score, self.average_creativity_score]
        return sum(scores) / len(scores) if scores else 0


@dataclass
class SessionContext:
    """会话上下文模型"""
    session_id: str
    start_time: str
    child_id: str
    grade_level: int = 0
    current_stage: Optional[str] = None
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

    def to_json(self) -> str:
        """序列化为JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass
class Recommendation:
    """个性化推荐模型"""
    recommendation_id: str
    category: str
    priority: str
    title: str
    description: str
    target_areas: List[str] = field(default_factory=list)
    suggested_duration: int = 0
    confidence_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    def is_high_priority(self) -> bool:
        """是否为高优先级"""
        return self.priority in ["高", "紧急"]


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
    writing_records: List[WritingRecord] = field(default_factory=list)
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
            "writing_records": [w.to_dict() for w in self.writing_records],
            "recommendations": [r.to_dict() for r in self.recommendations],
            "progress_stats": self.progress_stats.to_dict() if self.progress_stats else None
        }
        return result

    def to_json(self) -> str:
        """序列化为JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
