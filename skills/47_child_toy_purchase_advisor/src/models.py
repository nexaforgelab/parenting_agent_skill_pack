"""Data models for 儿童玩具选购 Agent.

这些模型保持轻量，方便 OpenClaw / Hermes / 任意 Python Agent Runtime 直接复用。
增强版本：添加更多数据类、类型注解、数据验证和序列化方法。
"""
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from enum import Enum
import json


class ToyCategory(Enum):
    """玩具分类枚举"""
    CONSTRUCTIVE = "constructive"
    EDUCATIONAL = "educational"
    CREATIVE = "creative"
    SPORTS = "sports"
    MUSICAL = "musical"
    ELECTRONIC = "electronic"
    ROLE_PLAY = "role_play"
    PUZZLE = "puzzle"
    OUTDOOR = "outdoor"
    ART = "art"


class SafetyRating(Enum):
    """安全评级枚举"""
    AGE_APPROPRIATE = "age_appropriate"
    SUPERVISION_REQUIRED = "supervision_required"
    SMALL_PARTS_WARNING = "small_parts_warning"
    CHOKING_HAZARD = "choking_hazard"
    ELECTRICAL_SAFETY = "electrical_safety"


class ToyAgeGroup(Enum):
    """玩具适玩年龄段枚举"""
    UNDER_1 = "under_1"
    AGE_1_2 = "1_2"
    AGE_3_4 = "3_4"
    AGE_5_6 = "5_6"
    AGE_7_8 = "7_8"
    AGE_9_10 = "9_10"
    AGE_11_PLUS = "11_plus"


@dataclass
class ToyRecommendation:
    """玩具推荐数据模型

    Attributes:
        name: 玩具名称
        brand: 品牌
        category: 玩具分类
        age_range: 适玩年龄范围
        price_range: 价格区间
        safety_rating: 安全评级
        educational_value: 教育价值评分 (1-5)
        durability_score: 耐玩性评分 (1-5)
        engagement_score: 趣味性评分 (1-5)
        parent_review_count: 家长评价数量
        average_rating: 平均评分
        purchase_priority: 购买优先级
        reason: 推荐理由
        content_warnings: 内容警告
        safety_certifications: 安全认证列表
    """
    name: str
    brand: str
    category: ToyCategory
    age_range: str
    safety_rating: str = "age_appropriate"
    educational_value: int = 3
    durability_score: int = 3
    engagement_score: int = 3
    parent_review_count: int = 0
    average_rating: float = 0.0
    price_range: str = ""
    purchase_priority: int = 1
    reason: str = ""
    content_warnings: List[str] = field(default_factory=list)
    safety_certifications: List[str] = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.category, str):
            try:
                self.category = ToyCategory(self.category)
            except ValueError:
                self.category = ToyCategory.EDUCATIONAL

    def validate_scores(self) -> List[str]:
        """验证评分数据"""
        errors = []
        for field_name, value in [
            ("教育价值", self.educational_value),
            ("耐玩性", self.durability_score),
            ("趣味性", self.engagement_score)
        ]:
            if not 1 <= value <= 5:
                errors.append(f"{field_name}评分必须在1-5之间，当前值: {value}")
        if self.average_rating < 0 or self.average_rating > 5:
            errors.append(f"平均评分必须在0-5之间，当前值: {self.average_rating}")
        return errors

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "brand": self.brand,
            "category": self.category.value if isinstance(self.category, ToyCategory) else self.category,
            "age_range": self.age_range,
            "safety_rating": self.safety_rating,
            "educational_value": self.educational_value,
            "durability_score": self.durability_score,
            "engagement_score": self.engagement_score,
            "parent_review_count": self.parent_review_count,
            "average_rating": self.average_rating,
            "price_range": self.price_range,
            "purchase_priority": self.purchase_priority,
            "reason": self.reason,
            "content_warnings": self.content_warnings,
            "safety_certifications": self.safety_certifications
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToyRecommendation":
        """从字典创建实例"""
        return cls(
            name=data.get("name", ""),
            brand=data.get("brand", ""),
            category=data.get("category", "educational"),
            age_range=data.get("age_range", ""),
            safety_rating=data.get("safety_rating", "age_appropriate"),
            educational_value=data.get("educational_value", 3),
            durability_score=data.get("durability_score", 3),
            engagement_score=data.get("engagement_score", 3),
            parent_review_count=data.get("parent_review_count", 0),
            average_rating=data.get("average_rating", 0.0),
            price_range=data.get("price_range", ""),
            purchase_priority=data.get("purchase_priority", 1),
            reason=data.get("reason", ""),
            content_warnings=data.get("content_warnings", []),
            safety_certifications=data.get("safety_certifications", [])
        )


@dataclass
class ToyUsageRecord:
    """玩具使用记录数据模型

    Attributes:
        toy_name: 玩具名称
        date: 日期
        duration_minutes: 使用时长（分钟）
        child_engagement: 孩子参与度 (1-5)
        child_reaction: 孩子反应
        parent_notes: 家长备注
    """
    toy_name: str
    date: Union[str, date]
    duration_minutes: int = 0
    child_engagement: int = 3
    child_reaction: str = ""
    parent_notes: str = ""

    def __post_init__(self):
        if isinstance(self.date, str):
            try:
                self.date = date.fromisoformat(self.date)
            except ValueError:
                self.date = date.today()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "toy_name": self.toy_name,
            "date": self.date.isoformat() if isinstance(self.date, date) else str(self.date),
            "duration_minutes": self.duration_minutes,
            "child_engagement": self.child_engagement,
            "child_reaction": self.child_reaction,
            "parent_notes": self.parent_notes
        }


@dataclass
class ChildProfile:
    """孩子画像数据模型"""
    name: str = ""
    age_years: int = 0
    age_months: int = 0
    development_goals: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)
    existing_toys: List[str] = field(default_factory=list)
    safety_sensitivity: List[str] = field(default_factory=list)
    sensory_preferences: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "age_years": self.age_years,
            "age_months": self.age_months,
            "development_goals": self.development_goals,
            "interests": self.interests,
            "existing_toys": self.existing_toys,
            "safety_sensitivity": self.safety_sensitivity,
            "sensory_preferences": self.sensory_preferences
        }


@dataclass
class ActionItem:
    """行动项目数据模型"""
    day: str
    task: str
    owner: str = "家长"
    evidence_to_record: str = "一句话记录执行结果"
    difficulty: str = "低"

    def to_dict(self) -> Dict[str, str]:
        """转换为字典"""
        return {
            "day": self.day,
            "task": self.task,
            "owner": self.owner,
            "evidence_to_record": self.evidence_to_record,
            "difficulty": self.difficulty
        }


@dataclass
class SkillInput:
    """Skill输入数据模型"""
    child_profile: Dict[str, Any]
    current_problem: str
    family_context: Dict[str, Any] = field(default_factory=dict)
    goal: str = ""
    raw_records: List[Dict[str, Any]] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    history_days: int = 7
    privacy_mode: str = "family_local_first"
    budget: float = 0.0

    def validate(self) -> List[str]:
        """验证输入数据"""
        errors = []
        if not isinstance(self.child_profile, dict):
            errors.append("child_profile 必须是字典类型")
        if not str(self.current_problem or "").strip():
            errors.append("current_problem 不能为空")
        if self.budget < 0:
            errors.append("预算不能为负数")
        return errors

    def to_json(self) -> str:
        """序列化为JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "child_profile": self.child_profile,
            "current_problem": self.current_problem,
            "family_context": self.family_context,
            "goal": self.goal,
            "raw_records": self.raw_records,
            "preferences": self.preferences,
            "attachments": self.attachments,
            "history_days": self.history_days,
            "privacy_mode": self.privacy_mode,
            "budget": self.budget
        }


@dataclass
class SkillOutput:
    """Skill输出数据模型"""
    skill_id: str
    summary: List[str] = field(default_factory=list)
    known_facts: List[str] = field(default_factory=list)
    analysis: List[str] = field(default_factory=list)
    action_plan: List[ActionItem] = field(default_factory=list)
    deliverables: Dict[str, Any] = field(default_factory=dict)
    risk_notes: List[str] = field(default_factory=list)
    next_tracking_fields: List[str] = field(default_factory=list)
    markdown_report: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "skill_id": self.skill_id,
            "summary": self.summary,
            "known_facts": self.known_facts,
            "analysis": self.analysis,
            "action_plan": [item.to_dict() if hasattr(item, 'to_dict') else item for item in self.action_plan],
            "deliverables": self.deliverables,
            "risk_notes": self.risk_notes,
            "next_tracking_fields": self.next_tracking_fields,
            "markdown_report": self.markdown_report
        }


@dataclass
class TrendData:
    """趋势数据模型"""
    metric_name: str
    current_value: float = 0.0
    previous_value: float = 0.0
    trend_direction: str = "stable"
    trend_percentage: float = 0.0
    data_points: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "metric_name": self.metric_name,
            "current_value": self.current_value,
            "previous_value": self.previous_value,
            "trend_direction": self.trend_direction,
            "trend_percentage": self.trend_percentage,
            "data_points": self.data_points
        }


@dataclass
class Alert:
    """预警数据模型"""
    alert_type: str
    severity: str
    message: str
    timestamp: str = ""
    recommendation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "alert_type": self.alert_type,
            "severity": self.severity,
            "message": self.message,
            "timestamp": self.timestamp,
            "recommendation": self.recommendation
        }
