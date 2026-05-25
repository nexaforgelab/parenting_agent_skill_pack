"""Data models for 父母情绪管理 Agent.

这些模型保持轻量，方便 OpenClaw / Hermes / 任意 Python Agent Runtime 直接复用。
增强版本：添加更多数据类、类型注解、数据验证和序列化方法。
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from enum import Enum
import json


class EmotionType(Enum):
    """情绪类型枚举"""
    ANGER = "anger"
    FRUSTRATION = "frustration"
    ANXIETY = "anxiety"
    SADNESS = "sadness"
    GUILT = "guilt"
    OVERWHELM = "overwhelm"
    EXHAUSTION = "exhaustion"
    JOY = "joy"
    CALM = "calm"
    GRATITUDE = "gratitude"


class TriggerType(Enum):
    """触发类型枚举"""
    CHILD_BEHAVIOR = "child_behavior"
    WORK_STRESS = "work_stress"
    TIME_PRESSURE = "time_pressure"
    FINANCE = "finance"
    RELATIONSHIP = "relationship"
    HEALTH = "health"
    SLEEP_DEPRIVATION = "sleep_deprivation"
    EXPECTATIONS = "expectations"


class CopingStrategy(Enum):
    """应对策略枚举"""
    BREATHING = "breathing"
    PAUSE = "pause"
    PHYSICAL_ACTIVITY = "physical_activity"
    SELF_TALK = "self_talk"
    SEEK_SUPPORT = "seek_support"
    JOURNALING = "journaling"
    PROFESSIONAL_HELP = "professional_help"
    MINDFULNESS = "mindfulness"


@dataclass
class EmotionRecord:
    """情绪记录数据模型

    Attributes:
        date: 日期
        emotion_type: 情绪类型
        intensity: 强度 (1-10)
        trigger: 触发因素
        situation: 情境描述
        physical_sensation: 身体感受
        thoughts: 思维
        response: 反应
        coping_used: 使用的应对策略
        effectiveness: 有效性 (1-5)
        outcome: 结果
        notes: 备注
    """
    date: Union[str, date]
    emotion_type: str
    intensity: int = 5
    trigger: str = ""
    situation: str = ""
    physical_sensation: str = ""
    thoughts: str = ""
    response: str = ""
    coping_used: List[str] = field(default_factory=list)
    effectiveness: int = 3
    outcome: str = ""
    notes: str = ""

    def __post_init__(self):
        if isinstance(self.date, str):
            try:
                self.date = date.fromisoformat(self.date)
            except ValueError:
                self.date = date.today()

    def validate(self) -> List[str]:
        """验证情绪记录"""
        errors = []
        if not 1 <= self.intensity <= 10:
            errors.append("情绪强度必须在1-10之间")
        if not 1 <= self.effectiveness <= 5:
            errors.append("有效性评分必须在1-5之间")
        return errors

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "date": self.date.isoformat() if isinstance(self.date, date) else str(self.date),
            "emotion_type": self.emotion_type,
            "intensity": self.intensity,
            "trigger": self.trigger,
            "situation": self.situation,
            "physical_sensation": self.physical_sensation,
            "thoughts": self.thoughts,
            "response": self.response,
            "coping_used": self.coping_used,
            "effectiveness": self.effectiveness,
            "outcome": self.outcome,
            "notes": self.notes
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EmotionRecord":
        """从字典创建实例"""
        return cls(
            date=data.get("date", ""),
            emotion_type=data.get("emotion_type", ""),
            intensity=data.get("intensity", 5),
            trigger=data.get("trigger", ""),
            situation=data.get("situation", ""),
            physical_sensation=data.get("physical_sensation", ""),
            thoughts=data.get("thoughts", ""),
            response=data.get("response", ""),
            coping_used=data.get("coping_used", []),
            effectiveness=data.get("effectiveness", 3),
            outcome=data.get("outcome", ""),
            notes=data.get("notes", "")
        )


@dataclass
class EmotionPattern:
    """情绪模式数据模型

    Attributes:
        emotion_type: 情绪类型
        frequency: 频率
        average_intensity: 平均强度
        common_triggers: 常见触发因素
        effective_strategies: 有效策略
        trend: 趋势
    """
    emotion_type: str = ""
    frequency: int = 0
    average_intensity: float = 0.0
    common_triggers: List[str] = field(default_factory=list)
    effective_strategies: List[str] = field(default_factory=list)
    trend: str = "stable"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "emotion_type": self.emotion_type,
            "frequency": self.frequency,
            "average_intensity": self.average_intensity,
            "common_triggers": self.common_triggers,
            "effective_strategies": self.effective_strategies,
            "trend": self.trend
        }


@dataclass
class CopingSuggestion:
    """应对建议数据模型

    Attributes:
        emotion_type: 情绪类型
        strategies: 策略列表
        scripts: 话术脚本
        resources: 资源推荐
    """
    emotion_type: str
    strategies: List[str] = field(default_factory=list)
    scripts: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "emotion_type": self.emotion_type,
            "strategies": self.strategies,
            "scripts": self.scripts,
            "resources": self.resources
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

    def validate(self) -> List[str]:
        """验证输入数据"""
        errors = []
        if not isinstance(self.child_profile, dict):
            errors.append("child_profile 必须是字典类型")
        if not str(self.current_problem or "").strip():
            errors.append("current_problem 不能为空")
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