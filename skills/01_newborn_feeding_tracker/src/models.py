"""Data models for 新生儿喂养记录 Agent.

这些模型保持轻量，方便 OpenClaw / Hermes / 任意 Python Agent Runtime 直接复用。
增强版本：添加完整类型注解、数据验证、序列化方法
"""
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from enum import Enum
import json


class FeedingType(Enum):
    """喂养类型枚举"""
    BREAST = "breast"
    FORMULA = "formula"
    MIXED = "mixed"
    SOLID = "solid"


class BowelMovement(Enum):
    """排便情况枚举"""
    NORMAL = "normal"
    LOOSE = "loose"
    CONSTIPATED = "constipated"
    HARD = "hard"


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
class FeedingRecord:
    """单条喂养记录数据模型"""
    timestamp: Union[str, datetime]
    feeding_type: Union[str, FeedingType]
    amount_ml: Optional[float] = None
    duration_minutes: Optional[float] = None
    side: Optional[str] = None
    bowel_movement: Optional[Union[str, BowelMovement]] = None
    notes: str = ""
    baby_response: str = ""
    caregiver: str = ""

    def __post_init__(self):
        """后处理：类型转换"""
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)
        if isinstance(self.feeding_type, str):
            self.feeding_type = FeedingType(self.feeding_type)
        if self.bowel_movement and isinstance(self.bowel_movement, str):
            self.bowel_movement = BowelMovement(self.bowel_movement)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "feeding_type": self.feeding_type.value if isinstance(self.feeding_type, Enum) else self.feeding_type,
            "amount_ml": self.amount_ml,
            "duration_minutes": self.duration_minutes,
            "side": self.side,
            "bowel_movement": self.bowel_movement.value if isinstance(self.bowel_movement, Enum) else self.bowel_movement,
            "notes": self.notes,
            "baby_response": self.baby_response,
            "caregiver": self.caregiver
        }

    def validate(self) -> List[str]:
        """验证记录数据"""
        errors = []
        if not self.timestamp:
            errors.append("timestamp 不能为空")
        if not self.feeding_type:
            errors.append("feeding_type 不能为空")
        if self.amount_ml is not None and self.amount_ml < 0:
            errors.append("amount_ml 不能为负数")
        if self.amount_ml and self.amount_ml > 500:
            errors.append("amount_ml 超出正常范围(0-500ml)")
        if self.duration_minutes and (self.duration_minutes < 0 or self.duration_minutes > 120):
            errors.append("duration_minutes 超出正常范围(0-120分钟)")
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
    total_feedings: int = 0
    average_daily_feedings: float = 0.0
    total_amount_ml: float = 0.0
    average_amount_ml: float = 0.0
    feeding_type_distribution: Dict[str, int] = field(default_factory=dict)
    bowel_movement_summary: Dict[str, int] = field(default_factory=dict)
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
            "total_feedings": self.total_feedings,
            "average_daily_feedings": round(self.average_daily_feedings, 2),
            "total_amount_ml": round(self.total_amount_ml, 2),
            "average_amount_ml": round(self.average_amount_ml, 2),
            "feeding_type_distribution": self.feeding_type_distribution,
            "bowel_movement_summary": self.bowel_movement_summary,
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
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
