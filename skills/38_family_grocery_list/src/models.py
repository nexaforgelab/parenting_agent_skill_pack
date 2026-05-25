"""Data models for 家庭买菜清单 Agent.

增强版本：添加完整类型注解、数据验证、序列化方法
"""
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from enum import Enum
import json


class ValidationError(Exception):
    """自定义验证错误异常"""
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(f"验证错误: {', '.join(errors)}")


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
        if self.data_points:
            self.average = sum(self.data_points) / len(self.data_points)
            self.min_value = min(self.data_points)
            self.max_value = max(self.data_points)

    def calculate_trend(self) -> None:
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
        if isinstance(self.timestamp, str):
            try:
                self.timestamp = datetime.fromisoformat(self.timestamp)
            except ValueError:
                pass

    def to_dict(self) -> Dict[str, Any]:
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
        if isinstance(self.created_at, str):
            try:
                self.created_at = datetime.fromisoformat(self.created_at)
            except ValueError:
                pass
        if isinstance(self.last_updated, str):
            try:
                self.last_updated = datetime.fromisoformat(self.last_updated)
            except ValueError:
                pass

    def add_interaction(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        interaction = {"role": role, "content": content, "timestamp": datetime.now().isoformat(), "metadata": metadata or {}}
        self.conversation_history.append(interaction)
        self.last_updated = datetime.now()

    def update_data(self, key: str, value: Any) -> None:
        self.accumulated_data[key] = value
        self.last_updated = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "last_updated": self.last_updated.isoformat() if isinstance(self.last_updated, datetime) else self.last_updated,
            "conversation_history": self.conversation_history,
            "accumulated_data": self.accumulated_data,
            "user_preferences": self.user_preferences
        }


@dataclass
class WeeklyStats:
    """周统计数据模型"""
    week_start: Union[str, date]
    week_end: Union[str, date]
    total_schedules: int = 0
    completed_schedules: int = 0
    completion_rate: float = 0.0
    schedule_type_distribution: Dict[str, int] = field(default_factory=dict)
    conflict_count: int = 0
    notes: str = ""

    def __post_init__(self):
        if isinstance(self.week_start, str):
            try:
                self.week_start = date.fromisoformat(self.week_start)
            except ValueError:
                pass
        if isinstance(self.week_end, str):
            try:
                self.week_end = date.fromisoformat(self.week_end)
            except ValueError:
                pass

    def to_dict(self) -> Dict[str, Any]:
        return {
            "week_start": self.week_start.isoformat() if isinstance(self.week_start, date) else self.week_start,
            "week_end": self.week_end.isoformat() if isinstance(self.week_end, date) else self.week_end,
            "total_schedules": self.total_schedules,
            "completed_schedules": self.completed_schedules,
            "completion_rate": round(self.completion_rate, 2),
            "schedule_type_distribution": self.schedule_type_distribution,
            "conflict_count": self.conflict_count,
            "notes": self.notes
        }
