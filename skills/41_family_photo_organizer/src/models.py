"""Data models for 家庭照片整理 Agent.

增强版本：添加完整类型注解、数据验证、序列化方法、更多数据类
"""
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from enum import Enum
import json


class PhotoCategory(Enum):
    """照片分类枚举"""
    BIRTHDAY = "birthday"
    TRAVEL = "travel"
    HOLIDAY = "holiday"
    DAILY = "daily"
    MILESTONE = "milestone"
    FAMILY = "family"
    SCHOOL = "school"
    OTHER = "other"


class PhotoQuality(Enum):
    """照片质量枚举"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


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
        """验证输入数据

        Returns:
            错误信息列表
        """
        errors = []
        if not isinstance(self.child_profile, dict):
            errors.append("child_profile 必须是字典类型")
        if not self.current_problem or not str(self.current_problem).strip():
            errors.append("current_problem 不能为空")
        if self.history_days < 1 or self.history_days > 90:
            errors.append("history_days 必须在 1-90 天范围内")
        return errors


@dataclass
class PhotoRecord:
    """单张照片记录数据模型"""
    photo_id: str
    timestamp: Union[str, datetime]
    category: Union[str, PhotoCategory] = PhotoCategory.DAILY
    location: str = ""
    people: List[str] = field(default_factory=list)
    description: str = ""
    tags: List[str] = field(default_factory=list)
    file_path: str = ""
    quality: Union[str, PhotoQuality] = PhotoQuality.GOOD
    is_favorite: bool = False
    is_in_album: bool = False
    album_name: str = ""

    def __post_init__(self):
        """后处理：类型转换"""
        if isinstance(self.timestamp, str):
            try:
                self.timestamp = datetime.fromisoformat(self.timestamp)
            except ValueError:
                self.timestamp = datetime.now()
        if isinstance(self.category, str):
            try:
                self.category = PhotoCategory(self.category)
            except ValueError:
                self.category = PhotoCategory.OTHER
        if isinstance(self.quality, str):
            try:
                self.quality = PhotoQuality(self.quality)
            except ValueError:
                self.quality = PhotoQuality.GOOD

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            字典格式的照片记录
        """
        return {
            "photo_id": self.photo_id,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "category": self.category.value if isinstance(self.category, Enum) else self.category,
            "location": self.location,
            "people": self.people,
            "description": self.description,
            "tags": self.tags,
            "file_path": self.file_path,
            "quality": self.quality.value if isinstance(self.quality, Enum) else self.quality,
            "is_favorite": self.is_favorite,
            "is_in_album": self.is_in_album,
            "album_name": self.album_name
        }

    def validate(self) -> List[str]:
        """验证照片记录数据

        Returns:
            错误信息列表
        """
        errors = []
        if not self.photo_id or not str(self.photo_id).strip():
            errors.append("photo_id 不能为空")
        if not self.timestamp:
            errors.append("timestamp 不能为空")
        if self.file_path and not str(self.file_path).strip():
            errors.append("file_path 不能为空字符串")
        return errors


@dataclass
class AlbumData:
    """相册数据模型"""
    album_id: str
    album_name: str
    description: str = ""
    start_date: Optional[Union[str, date]] = None
    end_date: Optional[Union[str, date]] = None
    photo_count: int = 0
    cover_photo_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    is_annual: bool = False
    year: Optional[int] = None
    created_at: Union[str, datetime] = field(default_factory=lambda: datetime.now())
    updated_at: Union[str, datetime] = field(default_factory=lambda: datetime.now())

    def __post_init__(self):
        """后处理：类型转换"""
        if isinstance(self.start_date, str):
            try:
                self.start_date = date.fromisoformat(self.start_date)
            except ValueError:
                self.start_date = None
        if isinstance(self.end_date, str):
            try:
                self.end_date = date.fromisoformat(self.end_date)
            except ValueError:
                self.end_date = None
        if isinstance(self.created_at, str):
            try:
                self.created_at = datetime.fromisoformat(self.created_at)
            except ValueError:
                self.created_at = datetime.now()
        if isinstance(self.updated_at, str):
            try:
                self.updated_at = datetime.fromisoformat(self.updated_at)
            except ValueError:
                self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            字典格式的相册数据
        """
        return {
            "album_id": self.album_id,
            "album_name": self.album_name,
            "description": self.description,
            "start_date": self.start_date.isoformat() if isinstance(self.start_date, date) else self.start_date,
            "end_date": self.end_date.isoformat() if isinstance(self.end_date, date) else self.end_date,
            "photo_count": self.photo_count,
            "cover_photo_id": self.cover_photo_id,
            "tags": self.tags,
            "is_annual": self.is_annual,
            "year": self.year,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }

    def validate(self) -> List[str]:
        """验证相册数据

        Returns:
            错误信息列表
        """
        errors = []
        if not self.album_id or not str(self.album_id).strip():
            errors.append("album_id 不能为空")
        if not self.album_name or not str(self.album_name).strip():
            errors.append("album_name 不能为空")
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                errors.append("开始日期不能晚于结束日期")
        return errors


@dataclass
class TimelineEvent:
    """成长时间线事件数据模型"""
    event_id: str
    event_date: Union[str, date, datetime]
    event_type: str
    title: str
    description: str = ""
    related_photo_ids: List[str] = field(default_factory=list)
    age_years: Optional[float] = None
    age_months: Optional[float] = None
    importance: str = "normal"
    is_milestone: bool = False

    def __post_init__(self):
        """后处理：类型转换"""
        if isinstance(self.event_date, datetime):
            self.event_date = self.event_date.date()
        elif isinstance(self.event_date, str):
            try:
                self.event_date = date.fromisoformat(self.event_date)
            except ValueError:
                try:
                    self.event_date = datetime.fromisoformat(self.event_date).date()
                except ValueError:
                    self.event_date = date.today()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            字典格式的时间线事件
        """
        return {
            "event_id": self.event_id,
            "event_date": self.event_date.isoformat() if isinstance(self.event_date, date) else self.event_date,
            "event_type": self.event_type,
            "title": self.title,
            "description": self.description,
            "related_photo_ids": self.related_photo_ids,
            "age_years": self.age_years,
            "age_months": self.age_months,
            "importance": self.importance,
            "is_milestone": self.is_milestone
        }

    def validate(self) -> List[str]:
        """验证时间线事件数据

        Returns:
            错误信息列表
        """
        errors = []
        if not self.event_id or not str(self.event_id).strip():
            errors.append("event_id 不能为空")
        if not self.event_date:
            errors.append("event_date 不能为空")
        if not self.title or not str(self.title).strip():
            errors.append("title 不能为空")
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
        """转换为字典格式

        Returns:
            字典格式的趋势数据
        """
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
            try:
                self.timestamp = datetime.fromisoformat(self.timestamp)
            except ValueError:
                self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            字典格式的告警信息
        """
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
        """转换为字典格式

        Returns:
            字典格式的推荐信息
        """
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
            try:
                self.created_at = datetime.fromisoformat(self.created_at)
            except ValueError:
                self.created_at = datetime.now()
        if isinstance(self.last_updated, str):
            try:
                self.last_updated = datetime.fromisoformat(self.last_updated)
            except ValueError:
                self.last_updated = datetime.now()

    def add_interaction(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """添加交互记录

        Args:
            role: 角色（user/assistant）
            content: 内容
            metadata: 额外元数据
        """
        interaction = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.conversation_history.append(interaction)
        self.last_updated = datetime.now()

    def update_data(self, key: str, value: Any) -> None:
        """更新累积数据

        Args:
            key: 数据键
            value: 数据值
        """
        self.accumulated_data[key] = value
        self.last_updated = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            字典格式的会话上下文
        """
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
        """转换为字典格式

        Returns:
            字典格式的行动项
        """
        return asdict(self)


@dataclass
class PhotoStatistics:
    """照片统计数据模型"""
    total_photos: int = 0
    photos_by_category: Dict[str, int] = field(default_factory=dict)
    photos_by_year: Dict[int, int] = field(default_factory=dict)
    photos_by_month: Dict[str, int] = field(default_factory=dict)
    favorite_count: int = 0
    albums_count: int = 0
    average_photos_per_month: float = 0.0
    most_active_month: Optional[str] = None
    least_active_month: Optional[str] = None
    photos_with_location: int = 0
    photos_with_tags: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            字典格式的照片统计
        """
        return {
            "total_photos": self.total_photos,
            "photos_by_category": self.photos_by_category,
            "photos_by_year": self.photos_by_year,
            "photos_by_month": self.photos_by_month,
            "favorite_count": self.favorite_count,
            "albums_count": self.albums_count,
            "average_photos_per_month": round(self.average_photos_per_month, 2),
            "most_active_month": self.most_active_month,
            "least_active_month": self.least_active_month,
            "photos_with_location": self.photos_with_location,
            "photos_with_tags": self.photos_with_tags
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
    photo_statistics: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            字典格式的技能输出
        """
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
            "photo_statistics": self.photo_statistics
        }

    def to_json(self, indent: int = 2) -> str:
        """序列化为JSON字符串

        Args:
            indent: 缩进空格数

        Returns:
            JSON字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent, default=str)
