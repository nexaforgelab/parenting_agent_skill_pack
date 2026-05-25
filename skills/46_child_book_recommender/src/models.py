"""Data models for 儿童图书推荐 Agent.

这些模型保持轻量，方便 OpenClaw / Hermes / 任意 Python Agent Runtime 直接复用。
增强版本：添加更多数据类、类型注解、数据验证和序列化方法。
"""
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from enum import Enum
import json


class ReadingLevel(Enum):
    """阅读水平枚举"""
    PRE_READER = "pre_reader"
    EMERGING = "emerging"
    DEVELOPING = "developing"
    FLUENT = "fluent"
    ADVANCED = "advanced"


class BookCategory(Enum):
    """图书分类枚举"""
    PICTURE_BOOK = "picture_book"
    EARLY_READER = "early_reader"
    CHAPTER_BOOK = "chapter_book"
    MIDDLE_GRADE = "middle_grade"
    YOUNG_ADULT = "young_adult"
    NON_FICTION = "non_fiction"
    POETRY = "poetry"
    GRAPHIC_NOVEL = "graphic_novel"


class AgeGroup(Enum):
    """年龄段枚举"""
    INFANT = "infant"
    TODDLER = "toddler"
    PRESCHOOL = "preschool"
    EARLY_ELEMENTARY = "early_elementary"
    MIDDLE_ELEMENTARY = "middle_elementary"
    UPPER_ELEMENTARY = "upper_elementary"
    MIDDLE_SCHOOL = "middle_school"
    HIGH_SCHOOL = "high_school"


@dataclass
class ChildProfile:
    """孩子画像数据模型

    Attributes:
        name: 孩子姓名（脱敏后）
        age_years: 年龄（岁）
        age_months: 年龄（月）
        reading_level: 阅读水平
        interests: 兴趣爱好列表
        preferred_genres: 喜欢的图书类型
        dislikes: 不喜欢的事物
        attention_span_minutes: 注意力持续时间（分钟）
        reading_history: 阅读历史记录
    """
    name: str = ""
    age_years: int = 0
    age_months: int = 0
    reading_level: ReadingLevel = ReadingLevel.EMERGING
    interests: List[str] = field(default_factory=list)
    preferred_genres: List[str] = field(default_factory=list)
    dislikes: List[str] = field(default_factory=list)
    attention_span_minutes: int = 15
    reading_history: List[str] = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.reading_level, str):
            try:
                self.reading_level = ReadingLevel(self.reading_level)
            except ValueError:
                self.reading_level = ReadingLevel.EMERGING

    def get_age_group(self) -> AgeGroup:
        """根据年龄计算年龄段"""
        total_months = self.age_years * 12 + self.age_months
        if total_months < 12:
            return AgeGroup.INFANT
        elif total_months < 24:
            return AgeGroup.TODDLER
        elif total_months < 60:
            return AgeGroup.PRESCHOOL
        elif total_months < 84:
            return AgeGroup.EARLY_ELEMENTARY
        elif total_months < 108:
            return AgeGroup.MIDDLE_ELEMENTARY
        elif total_months < 144:
            return AgeGroup.UPPER_ELEMENTARY
        elif total_months < 180:
            return AgeGroup.MIDDLE_SCHOOL
        else:
            return AgeGroup.HIGH_SCHOOL

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "age_years": self.age_years,
            "age_months": self.age_months,
            "reading_level": self.reading_level.value if isinstance(self.reading_level, ReadingLevel) else self.reading_level,
            "interests": self.interests,
            "preferred_genres": self.preferred_genres,
            "dislikes": self.dislikes,
            "attention_span_minutes": self.attention_span_minutes,
            "reading_history": self.reading_history
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChildProfile":
        """从字典创建实例"""
        return cls(
            name=data.get("name", ""),
            age_years=data.get("age_years", 0),
            age_months=data.get("age_months", 0),
            reading_level=data.get("reading_level", "emerging"),
            interests=data.get("interests", []),
            preferred_genres=data.get("preferred_genres", []),
            dislikes=data.get("dislikes", []),
            attention_span_minutes=data.get("attention_span_minutes", 15),
            reading_history=data.get("reading_history", [])
        )


@dataclass
class BookRecommendation:
    """图书推荐数据模型

    Attributes:
        title: 书名
        author: 作者
        category: 图书分类
        age_range: 适读年龄范围
        reading_level: 推荐阅读水平
        themes: 主题列表
        educational_value: 教育价值评分 (1-5)
        engagement_score: 趣味性评分 (1-5)
        parent_review_count: 家长评价数量
        average_rating: 平均评分
        price_range: 价格区间
        purchase_priority: 购买优先级
        reason: 推荐理由
        content_warnings: 内容警告
    """
    title: str
    author: str
    category: BookCategory
    age_range: str
    reading_level: ReadingLevel
    themes: List[str] = field(default_factory=list)
    educational_value: int = 3
    engagement_score: int = 3
    parent_review_count: int = 0
    average_rating: float = 0.0
    price_range: str = ""
    purchase_priority: int = 1
    reason: str = ""
    content_warnings: List[str] = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.category, str):
            try:
                self.category = BookCategory(self.category)
            except ValueError:
                self.category = BookCategory.PICTURE_BOOK
        if isinstance(self.reading_level, str):
            try:
                self.reading_level = ReadingLevel(self.reading_level)
            except ValueError:
                self.reading_level = ReadingLevel.EMERGING

    def validate_scores(self) -> List[str]:
        """验证评分数据"""
        errors = []
        if not 1 <= self.educational_value <= 5:
            errors.append(f"教育价值评分必须在1-5之间，当前值: {self.educational_value}")
        if not 1 <= self.engagement_score <= 5:
            errors.append(f"趣味性评分必须在1-5之间，当前值: {self.engagement_score}")
        if self.average_rating < 0 or self.average_rating > 5:
            errors.append(f"平均评分必须在0-5之间，当前值: {self.average_rating}")
        return errors

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "title": self.title,
            "author": self.author,
            "category": self.category.value if isinstance(self.category, BookCategory) else self.category,
            "age_range": self.age_range,
            "reading_level": self.reading_level.value if isinstance(self.reading_level, ReadingLevel) else self.reading_level,
            "themes": self.themes,
            "educational_value": self.educational_value,
            "engagement_score": self.engagement_score,
            "parent_review_count": self.parent_review_count,
            "average_rating": self.average_rating,
            "price_range": self.price_range,
            "purchase_priority": self.purchase_priority,
            "reason": self.reason,
            "content_warnings": self.content_warnings
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BookRecommendation":
        """从字典创建实例"""
        return cls(
            title=data.get("title", ""),
            author=data.get("author", ""),
            category=data.get("category", "picture_book"),
            age_range=data.get("age_range", ""),
            reading_level=data.get("reading_level", "emerging"),
            themes=data.get("themes", []),
            educational_value=data.get("educational_value", 3),
            engagement_score=data.get("engagement_score", 3),
            parent_review_count=data.get("parent_review_count", 0),
            average_rating=data.get("average_rating", 0.0),
            price_range=data.get("price_range", ""),
            purchase_priority=data.get("purchase_priority", 1),
            reason=data.get("reason", ""),
            content_warnings=data.get("content_warnings", [])
        )


@dataclass
class ReadingSession:
    """共读会话数据模型

    Attributes:
        book_title: 书名
        date: 日期
        duration_minutes: 时长（分钟）
        child_engagement: 孩子参与度 (1-5)
        comprehension_questions: 理解问题数量
        child_reaction: 孩子反应
        parent_reflection: 家长反思
    """
    book_title: str
    date: Union[str, date]
    duration_minutes: int = 15
    child_engagement: int = 3
    comprehension_questions: int = 0
    child_reaction: str = ""
    parent_reflection: str = ""

    def __post_init__(self):
        if isinstance(self.date, str):
            try:
                self.date = date.fromisoformat(self.date)
            except ValueError:
                self.date = date.today()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "book_title": self.book_title,
            "date": self.date.isoformat() if isinstance(self.date, date) else str(self.date),
            "duration_minutes": self.duration_minutes,
            "child_engagement": self.child_engagement,
            "comprehension_questions": self.comprehension_questions,
            "child_reaction": self.child_reaction,
            "parent_reflection": self.parent_reflection
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReadingSession":
        """从字典创建实例"""
        return cls(
            book_title=data.get("book_title", ""),
            date=data.get("date", ""),
            duration_minutes=data.get("duration_minutes", 15),
            child_engagement=data.get("child_engagement", 3),
            comprehension_questions=data.get("comprehension_questions", 0),
            child_reaction=data.get("child_reaction", ""),
            parent_reflection=data.get("parent_reflection", "")
        )


@dataclass
class ReadingPlan:
    """阅读计划数据模型

    Attributes:
        title: 计划名称
        duration_weeks: 计划周期（周）
        books: 计划书目列表
        weekly_goals: 每周目标
        progress_tracking: 进度追踪
    """
    title: str
    duration_weeks: int = 4
    books: List[Dict[str, Any]] = field(default_factory=list)
    weekly_goals: List[str] = field(default_factory=list)
    progress_tracking: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "title": self.title,
            "duration_weeks": self.duration_weeks,
            "books": self.books,
            "weekly_goals": self.weekly_goals,
            "progress_tracking": self.progress_tracking
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReadingPlan":
        """从字典创建实例"""
        return cls(
            title=data.get("title", ""),
            duration_weeks=data.get("duration_weeks", 4),
            books=data.get("books", []),
            weekly_goals=data.get("weekly_goals", []),
            progress_tracking=data.get("progress_tracking", {})
        )


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
    """Skill输入数据模型

    Attributes:
        child_profile: 孩子画像
        current_problem: 当前问题
        family_context: 家庭上下文
        goal: 目标
        raw_records: 原始记录
        preferences: 偏好设置
        attachments: 附件列表
        history_days: 历史天数
        privacy_mode: 隐私模式
    """
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
        """验证输入数据"""
        errors = []
        if not isinstance(self.child_profile, dict):
            errors.append("child_profile 必须是字典类型")
        if not str(self.current_problem or "").strip():
            errors.append("current_problem 不能为空")
        if self.history_days < 1 or self.history_days > 365:
            errors.append("history_days 必须在 1-365 之间")
        if self.privacy_mode not in {"anonymous", "family_local_first", "full"}:
            errors.append("privacy_mode 必须是 anonymous/family_local_first/full 之一")
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
            "privacy_mode": self.privacy_mode
        }


@dataclass
class SkillOutput:
    """Skill输出数据模型

    Attributes:
        skill_id: 技能ID
        summary: 摘要列表
        known_facts: 已知事实列表
        analysis: 分析结果列表
        action_plan: 行动计划列表
        deliverables: 交付物
        risk_notes: 风险提示列表
        next_tracking_fields: 下次追踪字段列表
        markdown_report: Markdown报告
    """
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

    def to_json(self) -> str:
        """序列化为JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass
class TrendData:
    """趋势数据模型

    Attributes:
        metric_name: 指标名称
        current_value: 当前值
        previous_value: 上一个周期值
        trend_direction: 趋势方向 (increasing/decreasing/stable)
        trend_percentage: 变化百分比
        data_points: 数据点列表
    """
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
    """预警数据模型

    Attributes:
        alert_type: 预警类型
        severity: 严重程度 (info/warning/critical)
        message: 预警消息
        timestamp: 时间戳
        recommendation: 建议
    """
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