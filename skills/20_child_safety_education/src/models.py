"""Data models for 儿童安全教育 Agent.

这些模型保持轻量，方便 OpenClaw / Hermes / 任意 Python Agent Runtime 直接复用。
增强版本：添加完整类型注解、数据验证、序列化方法、更多数据类
"""
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from enum import Enum
import json


class SafetyCategory(Enum):
    """安全类别枚举"""
    HOME_SAFETY = "home_safety"
    OUTDOOR_SAFETY = "outdoor_safety"
    ROAD_SAFETY = "road_safety"
    FIRE_SAFETY = "fire_safety"
    WATER_SAFETY = "water_safety"
    FOOD_SAFETY = "food_safety"
    Stranger_DANGER = "stranger_danger"
    INTERNET_SAFETY = "internet_safety"


class RiskLevel(Enum):
    """风险等级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TrainingStatus(Enum):
    """培训状态枚举"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    NEEDS_REINFORCEMENT = "needs_reinforcement"


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
        if not isinstance(self.child_profile, dict):
            errors.append("child_profile 必须是字典类型")
        if not self.current_problem or not str(self.current_problem).strip():
            errors.append("current_problem 不能为空")
        if self.history_days < 1 or self.history_days > 90:
            errors.append("history_days 必须在 1-90 天范围内")
        return errors


@dataclass
class SafetyLesson:
    """安全课程数据模型"""
    lesson_id: str
    lesson_name: str
    category: Union[str, SafetyCategory]
    description: str
    age_range: str = ""
    risk_level: Union[str, RiskLevel] = RiskLevel.MEDIUM
    key_points: List[str] = field(default_factory=list)
    materials_needed: List[str] = field(default_factory=list)
    estimated_duration_minutes: int = 15
    difficulty: str = "低"

    def __post_init__(self):
        """后处理：类型转换"""
        if isinstance(self.category, str):
            try:
                self.category = SafetyCategory(self.category)
            except ValueError:
                self.category = SafetyCategory.HOME_SAFETY
        if isinstance(self.risk_level, str):
            try:
                self.risk_level = RiskLevel(self.risk_level)
            except ValueError:
                self.risk_level = RiskLevel.MEDIUM

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "lesson_id": self.lesson_id,
            "lesson_name": self.lesson_name,
            "category": self.category.value if isinstance(self.category, Enum) else self.category,
            "description": self.description,
            "age_range": self.age_range,
            "risk_level": self.risk_level.value if isinstance(self.risk_level, Enum) else self.risk_level,
            "key_points": self.key_points,
            "materials_needed": self.materials_needed,
            "estimated_duration_minutes": self.estimated_duration_minutes,
            "difficulty": self.difficulty
        }

    def validate(self) -> List[str]:
        """验证安全课程数据"""
        errors = []
        if not self.lesson_id:
            errors.append("lesson_id 不能为空")
        if not self.lesson_name:
            errors.append("lesson_name 不能为空")
        if self.estimated_duration_minutes < 1:
            errors.append("estimated_duration_minutes 必须为正数")
        return errors


@dataclass
class SafetyTrainingRecord:
    """安全培训记录数据模型"""
    record_id: str
    child_id: str
    lesson_id: str
    timestamp: Union[str, datetime]
    status: Union[str, TrainingStatus] = TrainingStatus.IN_PROGRESS
    correct_responses: int = 0
    total_questions: int = 0
    role_play_score: float = 0.0
    notes: str = ""
    parent_observation: str = ""
    reinforcement_needed: bool = False

    def __post_init__(self):
        """后处理：类型转换"""
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)
        if isinstance(self.status, str):
            try:
                self.status = TrainingStatus(self.status)
            except ValueError:
                self.status = TrainingStatus.IN_PROGRESS

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "record_id": self.record_id,
            "child_id": self.child_id,
            "lesson_id": self.lesson_id,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "status": self.status.value if isinstance(self.status, Enum) else self.status,
            "correct_responses": self.correct_responses,
            "total_questions": self.total_questions,
            "role_play_score": self.role_play_score,
            "notes": self.notes,
            "parent_observation": self.parent_observation,
            "reinforcement_needed": self.reinforcement_needed
        }

    def validate(self) -> List[str]:
        """验证培训记录数据"""
        errors = []
        if not self.record_id:
            errors.append("record_id 不能为空")
        if not self.child_id:
            errors.append("child_id 不能为空")
        if not self.lesson_id:
            errors.append("lesson_id 不能为空")
        if self.correct_responses < 0:
            errors.append("correct_responses 不能为负数")
        if self.total_questions < 0:
            errors.append("total_questions 不能为负数")
        if self.role_play_score < 0 or self.role_play_score > 10:
            errors.append("role_play_score 必须在 0-10 范围内")
        return errors


@dataclass
class TrendData:
    """趋势分析数据模型"""
    metric_name: str
    data_points: List[float]
    dates: List[Union[str, date]]
    average: float = 0.0
    min_value: float = 0.0
    max_value: float = 0.0
    trend_direction: str = "stable"
    trend_percentage: float = 0.0

    def __post_init__(self):
        """后处理：计算统计值"""
        if self.data_points:
            self.average = sum(self.data_points) / len(self.data_points)
            self.min_value = min(self.data_points)
            self.max_value = max(self.data_points)

    def calculate_trend(self) -> None:
        """计算趋势方向和百分比"""
        if len(self.data_points) < 2:
            return

        first_half = self.data_points[:len(self.data_points)//2]
        second_half = self.data_points[len(self.data_points)//2:]

        avg_first = sum(first_half) / len(first_half) if first_half else 0
        avg_second = sum(second_half) / len(second_half) if second_half else 0

        if avg_first > 0:
            self.trend_percentage = ((avg_second - avg_first) / avg_first) * 100
            if self.trend_percentage > 5:
                self.trend_direction = "increasing"
            elif self.trend_percentage < -5:
                self.trend_direction = "decreasing"
            else:
                self.trend_direction = "stable"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "metric_name": self.metric_name,
            "data_points": self.data_points,
            "dates": [d.isoformat() if isinstance(d, date) else d for d in self.dates],
            "average": round(self.average, 2),
            "min_value": self.min_value,
            "max_value": self.max_value,
            "trend_direction": self.trend_direction,
            "trend_percentage": round(self.trend_percentage, 2)
        }


@dataclass
class Alert:
    """告警信息数据模型"""
    alert_type: str
    severity: str
    message: str
    recommendation: str
    timestamp: Union[str, datetime] = field(default_factory=lambda: datetime.now())
    is_acknowledged: bool = False

    def __post_init__(self):
        """后处理：类型转换"""
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "alert_type": self.alert_type,
            "severity": self.severity,
            "message": self.message,
            "recommendation": self.recommendation,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "is_acknowledged": self.is_acknowledged
        }


@dataclass
class Recommendation:
    """个性化推荐数据模型"""
    category: str
    priority: int
    title: str
    description: str
    action_items: List[str] = field(default_factory=list)
    rationale: str = ""
    expected_outcome: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "category": self.category,
            "priority": self.priority,
            "title": self.title,
            "description": self.description,
            "action_items": self.action_items,
            "rationale": self.rationale,
            "expected_outcome": self.expected_outcome
        }


@dataclass
class SessionContext:
    """会话上下文数据模型"""
    session_id: str
    created_at: Union[str, datetime] = field(default_factory=lambda: datetime.now())
    last_updated: Union[str, datetime] = field(default_factory=lambda: datetime.now())
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    accumulated_data: Dict[str, Any] = field(default_factory=dict)
    user_preferences: Dict[str, Any] = field(default_factory=dict)

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

    def update_data(self, key: str, value: Any) -> None:
        """更新累积数据"""
        self.accumulated_data[key] = value
        self.last_updated = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "last_updated": self.last_updated.isoformat() if isinstance(self.last_updated, datetime) else self.last_updated,
            "conversation_history": self.conversation_history,
            "accumulated_data": self.accumulated_data,
            "user_preferences": self.user_preferences
        }


@dataclass
class ActionItem:
    """行动项数据模型"""
    day: str
    task: str
    owner: str = "家长"
    evidence_to_record: str = "一句话记录执行结果"
    difficulty: str = "低"

    def to_dict(self) -> Dict[str, str]:
        """转换为字典格式"""
        return asdict(self)


@dataclass
class WeeklyStats:
    """周统计数据模型"""
    week_start: Union[str, date]
    week_end: Union[str, date]
    total_sessions: int = 0
    completion_rate: float = 0.0
    average_score: float = 0.0
    lessons_completed: int = 0
    categories_covered: List[str] = field(default_factory=list)
    reinforcement_needed: int = 0
    notes: str = ""

    def __post_init__(self):
        """后处理：类型转换"""
        if isinstance(self.week_start, str):
            self.week_start = date.fromisoformat(self.week_start)
        if isinstance(self.week_end, str):
            self.week_end = date.fromisoformat(self.week_end)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "week_start": self.week_start.isoformat() if isinstance(self.week_start, date) else self.week_start,
            "week_end": self.week_end.isoformat() if isinstance(self.week_end, date) else self.week_end,
            "total_sessions": self.total_sessions,
            "completion_rate": round(self.completion_rate, 2),
            "average_score": round(self.average_score, 2),
            "lessons_completed": self.lessons_completed,
            "categories_covered": self.categories_covered,
            "reinforcement_needed": self.reinforcement_needed,
            "notes": self.notes
        }


@dataclass
class SkillOutput:
    """技能输出数据模型"""
    skill_id: str
    summary: List[str]
    known_facts: List[str]
    analysis: List[str]
    action_plan: List[Union[ActionItem, Dict[str, str]]]
    deliverables: Dict[str, Any]
    risk_notes: List[str]
    next_tracking_fields: List[str]
    markdown_report: str = ""
    trends: List[Dict[str, Any]] = field(default_factory=list)
    alerts: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    weekly_stats: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
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
            "trends": self.trends,
            "alerts": self.alerts,
            "recommendations": self.recommendations,
            "weekly_stats": self.weekly_stats
        }

    def to_json(self, indent: int = 2) -> str:
        """序列化为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent, default=str)