"""Data models for 家庭教育支出规划 Agent.

这些模型保持轻量，方便 OpenClaw / Hermes / 任意 Python Agent Runtime 直接复用。
增强版本：添加更多数据类、类型注解、数据验证和序列化方法。
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from enum import Enum
import json


class ExpenseCategory(Enum):
    """支出分类枚举"""
    CHILDCARE = "childcare"
    TUITION = "tuition"
    BOOKS = "books"
    TOYS = "toys"
    TRAVEL = "travel"
    EXTRACURRICULAR = "extracurricular"
    SUPPLIES = "supplies"
    HEALTH = "health"
    OTHER = "other"


class BudgetPeriod(Enum):
    """预算周期枚举"""
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class PaymentMethod(Enum):
    """支付方式枚举"""
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    PARENT_PAY = "parent_pay"
    OTHER = "other"


@dataclass
class ExpenseRecord:
    """支出记录数据模型

    Attributes:
        date: 日期
        category: 支出分类
        description: 描述
        amount: 金额
        payment_method: 支付方式
        receipt: 是否有收据
        notes: 备注
    """
    date: Union[str, date]
    category: str
    description: str
    amount: float
    payment_method: str = "cash"
    receipt: bool = False
    notes: str = ""

    def __post_init__(self):
        if isinstance(self.date, str):
            try:
                self.date = date.fromisoformat(self.date)
            except ValueError:
                self.date = date.today()

    def validate(self) -> List[str]:
        """验证支出记录"""
        errors = []
        if self.amount < 0:
            errors.append("金额不能为负数")
        if not self.description:
            errors.append("描述不能为空")
        return errors

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "date": self.date.isoformat() if isinstance(self.date, date) else str(self.date),
            "category": self.category,
            "description": self.description,
            "amount": self.amount,
            "payment_method": self.payment_method,
            "receipt": self.receipt,
            "notes": self.notes
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExpenseRecord":
        """从字典创建实例"""
        return cls(
            date=data.get("date", ""),
            category=data.get("category", "other"),
            description=data.get("description", ""),
            amount=data.get("amount", 0.0),
            payment_method=data.get("payment_method", "cash"),
            receipt=data.get("receipt", False),
            notes=data.get("notes", "")
        )


@dataclass
class BudgetPlan:
    """预算计划数据模型

    Attributes:
        period: 预算周期
        total_budget: 总预算
        categories: 分类预算字典
        start_date: 开始日期
        end_date: 结束日期
    """
    period: str = "monthly"
    total_budget: float = 0.0
    categories: Dict[str, float] = field(default_factory=dict)
    start_date: Union[str, date] = ""
    end_date: Union[str, date] = ""

    def validate(self) -> List[str]:
        """验证预算计划"""
        errors = []
        if self.total_budget < 0:
            errors.append("总预算不能为负数")
        category_total = sum(self.categories.values())
        if abs(category_total - self.total_budget) > 0.01:
            errors.append("分类预算合计与总预算不符")
        return errors

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "period": self.period,
            "total_budget": self.total_budget,
            "categories": self.categories,
            "start_date": self.start_date.isoformat() if isinstance(self.start_date, date) else str(self.start_date),
            "end_date": self.end_date.isoformat() if isinstance(self.end_date, date) else str(self.end_date)
        }


@dataclass
class SpendingAnalysis:
    """支出分析数据模型

    Attributes:
        total_spending: 总支出
        category_breakdown: 分类明细
        average_daily: 日均支出
        budget_status: 预算状态
        recommendations: 优化建议
    """
    total_spending: float = 0.0
    category_breakdown: Dict[str, float] = field(default_factory=dict)
    average_daily: float = 0.0
    budget_status: str = "unknown"
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "total_spending": self.total_spending,
            "category_breakdown": self.category_breakdown,
            "average_daily": self.average_daily,
            "budget_status": self.budget_status,
            "recommendations": self.recommendations
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