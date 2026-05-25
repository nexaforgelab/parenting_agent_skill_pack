"""Data models for 月龄发育里程碑 Agent.

这些模型保持轻量，方便 OpenClaw / Hermes / 任意 Python Agent Runtime 直接复用。
"""
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime, date
import json


@dataclass
class SkillInput:
    """技能输入数据模型.

    包含孩子的基本信息、当前问题、家庭上下文等输入参数。
    支持历史记录、偏好设置和附件信息。
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

    def to_dict(self) -> Dict[str, Any]:
        """将对象转换为字典格式.

        Returns:
            包含所有字段的字典对象
        """
        return asdict(self)

    def validate(self) -> List[str]:
        """验证输入数据的有效性.

        Returns:
            错误消息列表，空列表表示验证通过
        """
        errors = []
        if not isinstance(self.child_profile, dict):
            errors.append("child_profile 必须是字典类型")
        if not str(self.current_problem).strip():
            errors.append("current_problem 不能为空")
        if self.history_days < 0:
            errors.append("history_days 必须是非负整数")
        if self.privacy_mode not in {"anonymous", "family_local_first", "full"}:
            errors.append("privacy_mode 必须是 anonymous、family_local_first 或 full")
        return errors


@dataclass
class ActionItem:
    """行动项数据模型.

    描述具体的执行任务，包括时间、负责人和记录要求。
    """
    day: str
    task: str
    owner: str = "家长"
    evidence_to_record: str = "一句话记录执行结果"
    difficulty: str = "低"

    def to_dict(self) -> Dict[str, str]:
        """将行动项转换为字典格式.

        Returns:
            行动项字典
        """
        return asdict(self)

    def validate(self) -> List[str]:
        """验证行动项的有效性.

        Returns:
            错误消息列表
        """
        errors = []
        if not self.day:
            errors.append("day 不能为空")
        if not self.task:
            errors.append("task 不能为空")
        if self.difficulty not in {"低", "中", "高"}:
            errors.append("difficulty 必须是 低、中 或 高")
        return errors


@dataclass
class MilestoneRecord:
    """发育里程碑记录数据模型.

    记录孩子在各个月龄段的发育里程碑达成情况。
    """
    milestone_id: str
    milestone_name: str
    category: str
    expected_months: int
    actual_months: Optional[int] = None
    achieved: bool = False
    notes: str = ""
    record_date: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式.

        Returns:
            里程碑记录字典
        """
        return asdict(self)

    def is_delayed(self) -> bool:
        """判断是否发育迟缓.

        Returns:
            True 如果实际月龄超过预期月龄
        """
        if self.actual_months is not None:
            return self.actual_months > self.expected_months
        return False


@dataclass
class GrowthData:
    """生长数据模型.

    记录孩子的身高、体重、头围等生长指标。
    """
    date: str
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    head_circumference_cm: Optional[float] = None
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式."""
        return asdict(self)

    def validate(self) -> List[str]:
        """验证生长数据的有效性.

        Returns:
            错误消息列表
        """
        errors = []
        if self.height_cm is not None and (self.height_cm <= 0 or self.height_cm > 200):
            errors.append("身高必须在 0-200 cm 之间")
        if self.weight_kg is not None and (self.weight_kg <= 0 or self.weight_kg > 50):
            errors.append("体重必须在 0-50 kg 之间")
        if self.head_circumference_cm is not None and (self.head_circumference_cm <= 0 or self.head_circumference_cm > 100):
            errors.append("头围必须在 0-100 cm 之间")
        return errors


@dataclass
class ObservationEntry:
    """观察记录条目数据模型.

    记录家长对孩子的日常观察。
    """
    timestamp: str
    category: str
    description: str
    duration_minutes: Optional[int] = None
    intensity: str = "中等"
    response: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式."""
        return asdict(self)


@dataclass
class TrendAnalysis:
    """趋势分析结果数据模型.

    存储发育趋势分析的结果。
    """
    metric_name: str
    period_start: str
    period_end: str
    values: List[float]
    trend_direction: str
    change_percentage: float
    confidence: str

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式."""
        return asdict(self)


@dataclass
class SkillOutput:
    """技能输出数据模型.

    包含分析结果、行动计划和交付物。
    """
    skill_id: str
    summary: List[str]
    known_facts: List[str]
    analysis: List[str]
    action_plan: List[ActionItem]
    deliverables: Dict[str, Any]
    risk_notes: List[str]
    next_tracking_fields: List[str]
    markdown_report: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式.

        Returns:
            完整的输出字典
        """
        return {
            "skill_id": self.skill_id,
            "summary": self.summary,
            "known_facts": self.known_facts,
            "analysis": self.analysis,
            "action_plan": [item.to_dict() if isinstance(item, ActionItem) else item for item in self.action_plan],
            "deliverables": self.deliverables,
            "risk_notes": self.risk_notes,
            "next_tracking_fields": self.next_tracking_fields,
            "markdown_report": self.markdown_report
        }

    def to_json(self, indent: int = 2) -> str:
        """序列化为JSON格式字符串.

        Args:
            indent: JSON缩进空格数

        Returns:
            JSON格式的字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def validate(self) -> List[str]:
        """验证输出数据的有效性.

        Returns:
            错误消息列表
        """
        errors = []
        if not self.skill_id:
            errors.append("skill_id 不能为空")
        if not isinstance(self.summary, list):
            errors.append("summary 必须是列表类型")
        if not isinstance(self.action_plan, list):
            errors.append("action_plan 必须是列表类型")
        return errors


@dataclass
class ContextMemory:
    """上下文记忆数据模型.

    用于存储和管理跨会话的上下文信息。
    """
    session_id: str
    child_id: str
    previous_observations: List[ObservationEntry] = field(default_factory=list)
    milestone_history: List[MilestoneRecord] = field(default_factory=list)
    growth_history: List[GrowthData] = field(default_factory=list)
    last_updated: str = ""

    def add_observation(self, observation: ObservationEntry) -> None:
        """添加观察记录.

        Args:
            observation: 观察记录条目
        """
        self.previous_observations.append(observation)

    def add_milestone(self, milestone: MilestoneRecord) -> None:
        """添加里程碑记录.

        Args:
            milestone: 里程碑记录
        """
        self.milestone_history.append(milestone)

    def get_recent_observations(self, days: int = 7) -> List[ObservationEntry]:
        """获取最近的观察记录.

        Args:
            days: 获取最近的天数

        Returns:
            观察记录列表
        """
        return self.previous_observations[-days:] if len(self.previous_observations) > days else self.previous_observations

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式."""
        return {
            "session_id": self.session_id,
            "child_id": self.child_id,
            "previous_observations": [obs.to_dict() for obs in self.previous_observations],
            "milestone_history": [m.to_dict() for m in self.milestone_history],
            "growth_history": [g.to_dict() for g in self.growth_history],
            "last_updated": self.last_updated
        }
