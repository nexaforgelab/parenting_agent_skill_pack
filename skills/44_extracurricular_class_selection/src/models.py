"""Data models for 幼儿园择校 Agent.

增强版本：添加完整类型注解、数据验证、序列化方法、更多数据类
"""
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from enum import Enum
import json


class KindergartenType(Enum):
    """幼儿园类型枚举"""
    PUBLIC = "public"
    PRIVATE = "private"
    INTERNATIONAL = "international"
    MONTESSORI = "montessori"
    WALDORF = "waldorf"
    OTHER = "other"


class EvaluationDimension(Enum):
    """评估维度枚举"""
    CURRICULUM = "curriculum"
    TEACHERS = "teachers"
    ENVIRONMENT = "environment"
    SAFETY = "safety"
    FEES = "fees"
    LOCATION = "location"
    REPUTATION = "reputation"


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
class KindergartenInfo:
    """幼儿园信息数据模型"""
    kindergarten_id: str
    name: str
    type: Union[str, KindergartenType] = KindergartenType.PRIVATE
    address: str = ""
    district: str = ""
    phone: str = ""
    website: str = ""
    tuition_per_year: float = 0.0
    enrollment_capacity: int = 0
    current_enrollment: int = 0
    teacher_student_ratio: float = 0.0
    established_year: Optional[int] = None
    accreditation: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    curriculum: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    facilities: List[str] = field(default_factory=list)
    rating: float = 0.0
    review_count: int = 0
    distance_from_home: float = 0.0

    def __post_init__(self):
        """后处理：类型转换"""
        if isinstance(self.type, str):
            try:
                self.type = KindergartenType(self.type)
            except ValueError:
                self.type = KindergartenType.OTHER

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "kindergarten_id": self.kindergarten_id,
            "name": self.name,
            "type": self.type.value if isinstance(self.type, Enum) else self.type,
            "address": self.address,
            "district": self.district,
            "phone": self.phone,
            "website": self.website,
            "tuition_per_year": self.tuition_per_year,
            "enrollment_capacity": self.enrollment_capacity,
            "current_enrollment": self.current_enrollment,
            "teacher_student_ratio": self.teacher_student_ratio,
            "established_year": self.established_year,
            "accreditation": self.accreditation,
            "features": self.features,
            "curriculum": self.curriculum,
            "languages": self.languages,
            "facilities": self.facilities,
            "rating": self.rating,
            "review_count": self.review_count,
            "distance_from_home": self.distance_from_home
        }

    def validate(self) -> List[str]:
        """验证幼儿园数据"""
        errors = []
        if not self.name or not str(self.name).strip():
            errors.append("幼儿园名称不能为空")
        if self.tuition_per_year < 0:
            errors.append("学费不能为负数")
        if self.teacher_student_ratio < 0:
            errors.append("师生比不能为负数")
        return errors


@dataclass
class EvaluationScore:
    """评估评分数据模型"""
    dimension: Union[str, EvaluationDimension]
    score: float
    weight: float = 1.0
    evidence: str = ""
    concerns: List[str] = field(default_factory=list)

    def __post_init__(self):
        """后处理：类型转换"""
        if isinstance(self.dimension, str):
            try:
                self.dimension = EvaluationDimension(self.dimension)
            except ValueError:
                self.dimension = EvaluationDimension.CURRICULUM

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "dimension": self.dimension.value if isinstance(self.dimension, Enum) else self.dimension,
            "score": self.score,
            "weight": self.weight,
            "evidence": self.evidence,
            "concerns": self.concerns
        }


@dataclass
class ComparisonResult:
    """比较结果数据模型"""
    kindergarten_id: str
    kindergarten_name: str
    overall_score: float = 0.0
    dimension_scores: List[EvaluationScore] = field(default_factory=list)
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)
    recommendation: str = ""
    match_percentage: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "kindergarten_id": self.kindergarten_id,
            "kindergarten_name": self.kindergarten_name,
            "overall_score": round(self.overall_score, 2),
            "dimension_scores": [s.to_dict() for s in self.dimension_scores],
            "pros": self.pros,
            "cons": self.cons,
            "recommendation": self.recommendation,
            "match_percentage": round(self.match_percentage, 2)
        }


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

    def __post_init__(self):
        """后处理：类型转换"""
        if isinstance(self.timestamp, str):
            try:
                self.timestamp = datetime.fromisoformat(self.timestamp)
            except ValueError:
                self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "alert_type": self.alert_type,
            "severity": self.severity,
            "message": self.message,
            "recommendation": self.recommendation,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp
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
class SelectionStatistics:
    """择校统计数据模型"""
    total_kindergartens: int = 0
    evaluated_count: int = 0
    average_overall_score: float = 0.0
    top_ranked: Optional[str] = None
    budget_range: Dict[str, float] = field(default_factory=dict)
    distance_range: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "total_kindergartens": self.total_kindergartens,
            "evaluated_count": self.evaluated_count,
            "average_overall_score": round(self.average_overall_score, 2),
            "top_ranked": self.top_ranked,
            "budget_range": self.budget_range,
            "distance_range": self.distance_range
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
    comparison_results: List[Dict[str, Any]] = field(default_factory=list)
    selection_statistics: Optional[Dict[str, Any]] = None

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
            "comparison_results": self.comparison_results,
            "selection_statistics": self.selection_statistics
        }

    def to_json(self, indent: int = 2) -> str:
        """序列化为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent, default=str)
