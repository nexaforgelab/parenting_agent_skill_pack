"""Validation helpers for 家庭教育支出规划 Agent.

提供完整的字段级验证、数据范围检查、格式验证和自定义错误消息。
"""
from typing import Any, Dict, List, Optional, Union
import re
from datetime import datetime, date


class ValidationError(Exception):
    """自定义验证错误异常"""

    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(f"验证错误: {', '.join(errors)}")


class FieldValidator:
    """字段验证器基类"""

    def __init__(self, field_name: str, required: bool = True):
        self.field_name = field_name
        self.required = required
        self.errors: List[str] = []

    def validate(self, value: Any) -> List[str]:
        """验证字段值"""
        self.errors = []
        if value is None or value == "":
            if self.required:
                self.errors.append(f"{self.field_name} 是必填字段")
            return self.errors
        return self.errors


class StringValidator(FieldValidator):
    """字符串字段验证器"""

    def __init__(
        self,
        field_name: str,
        required: bool = True,
        min_length: int = 0,
        max_length: int = 1000
    ):
        super().__init__(field_name, required)
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value: Any) -> List[str]:
        """验证字符串字段"""
        self.errors = []
        if value is None:
            if self.required:
                self.errors.append(f"{self.field_name} 是必填字段")
            return self.errors

        value_str = str(value)
        if len(value_str) < self.min_length:
            self.errors.append(f"{self.field_name} 长度不能少于 {self.min_length} 个字符")
        if len(value_str) > self.max_length:
            self.errors.append(f"{self.field_name} 长度不能超过 {self.max_length} 个字符")

        return self.errors


class NumberValidator(FieldValidator):
    """数字字段验证器"""

    def __init__(
        self,
        field_name: str,
        required: bool = True,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ):
        super().__init__(field_name, required)
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: Any) -> List[str]:
        """验证数字字段"""
        self.errors = []
        if value is None:
            if self.required:
                self.errors.append(f"{self.field_name} 是必填字段")
            return self.errors

        try:
            num_value = float(value)
        except (ValueError, TypeError):
            self.errors.append(f"{self.field_name} 必须是数字类型")
            return self.errors

        if self.min_value is not None and num_value < self.min_value:
            self.errors.append(f"{self.field_name} 不能小于 {self.min_value}")
        if self.max_value is not None and num_value > self.max_value:
            self.errors.append(f"{self.field_name} 不能大于 {self.max_value}")

        return self.errors


class AmountValidator(NumberValidator):
    """金额字段验证器"""

    def __init__(self, field_name: str = "金额"):
        super().__init__(field_name, required=True, min_value=0, max_value=10000000)


class DateValidator(FieldValidator):
    """日期字段验证器"""

    def __init__(
        self,
        field_name: str = "日期",
        required: bool = True,
        date_format: str = "%Y-%m-%d"
    ):
        super().__init__(field_name, required)
        self.date_format = date_format

    def validate(self, value: Any) -> List[str]:
        """验证日期字段"""
        self.errors = []
        if value is None:
            if self.required:
                self.errors.append(f"{self.field_name} 是必填字段")
            return self.errors

        if isinstance(value, (datetime, date)):
            return self.errors
        elif isinstance(value, str):
            try:
                datetime.strptime(value, self.date_format)
                return self.errors
            except ValueError:
                self.errors.append(f"{self.field_name} 日期格式不正确，应为 {self.date_format}")
                return self.errors
        else:
            self.errors.append(f"{self.field_name} 必须是日期或字符串类型")
            return self.errors


def require_payload(payload: Dict[str, Any]) -> List[str]:
    """验证payload基础结构

    Args:
        payload: 输入的payload字典

    Returns:
        错误列表
    """
    errors: List[str] = []
    if not isinstance(payload, dict):
        return ["payload 必须是 dict"]
    if not payload.get("child_profile"):
        errors.append("缺少 child_profile")
    if not str(payload.get("current_problem", "")).strip():
        errors.append("缺少 current_problem")
    return errors


def validate_expense_record(record: Dict[str, Any]) -> List[str]:
    """验证支出记录

    Args:
        record: 支出记录字典

    Returns:
        错误列表
    """
    errors = []

    if not isinstance(record, dict):
        return ["record 必须是字典类型"]

    amount_validator = AmountValidator("金额")
    amount_errors = amount_validator.validate(record.get("amount"))
    errors.extend(amount_errors)

    if "category" in record:
        valid_categories = {
            "childcare", "tuition", "books", "toys", "travel",
            "extracurricular", "supplies", "health", "other"
        }
        if record["category"] not in valid_categories:
            errors.append(f"category 必须是以下值之一: {', '.join(valid_categories)}")

    description_validator = StringValidator("描述", required=True, min_length=1, max_length=500)
    desc_errors = description_validator.validate(record.get("description"))
    errors.extend(desc_errors)

    return errors


def validate_budget_plan(plan: Dict[str, Any]) -> List[str]:
    """验证预算计划

    Args:
        plan: 预算计划字典

    Returns:
        错误列表
    """
    errors = []

    if not isinstance(plan, dict):
        return ["plan 必须是字典类型"]

    if "total_budget" in plan:
        budget_validator = AmountValidator("总预算")
        budget_errors = budget_validator.validate(plan["total_budget"])
        errors.extend(budget_errors)

    if "period" in plan:
        valid_periods = {"weekly", "monthly", "quarterly", "yearly"}
        if plan["period"] not in valid_periods:
            errors.append(f"period 必须是以下值之一: {', '.join(valid_periods)}")

    if "categories" in plan:
        if not isinstance(plan["categories"], dict):
            errors.append("categories 必须是字典类型")
        else:
            for cat, amount in plan["categories"].items():
                if not isinstance(amount, (int, float)):
                    errors.append(f"分类 {cat} 的金额必须是数字")
                elif amount < 0:
                    errors.append(f"分类 {cat} 的金额不能为负数")

    return errors


def validate_child_profile(profile: Dict[str, Any]) -> List[str]:
    """验证孩子画像

    Args:
        profile: 孩子画像字典

    Returns:
        错误列表
    """
    errors = []

    if not isinstance(profile, dict):
        return ["child_profile 必须是字典类型"]

    if "age_years" in profile:
        try:
            age = int(profile["age_years"])
            if age < 0 or age > 25:
                errors.append("年龄超出合理范围（0-25岁）")
        except (ValueError, TypeError):
            errors.append("年龄必须是整数")

    return errors


def validate_preferences(preferences: Dict[str, Any]) -> List[str]:
    """验证偏好设置

    Args:
        preferences: 偏好设置字典

    Returns:
        错误列表
    """
    errors = []

    if not isinstance(preferences, dict):
        return ["preferences 必须是字典类型"]

    if "privacy_mode" in preferences:
        valid_modes = {"anonymous", "family_local_first", "full"}
        if preferences["privacy_mode"] not in valid_modes:
            errors.append(f"privacy_mode 必须是以下值之一: {', '.join(valid_modes)}")

    if "budget" in preferences:
        budget_validator = AmountValidator("预算")
        budget_errors = budget_validator.validate(preferences["budget"])
        errors.extend(budget_errors)

    return errors


def safe_list(value: Any) -> List[Any]:
    """安全转换为列表"""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def anonymize_if_needed(text: str, privacy_mode: str) -> str:
    """根据隐私模式脱敏处理"""
    if privacy_mode in {"anonymous", "family_local_first"}:
        return text.replace("孩子姓名", "孩子").replace("学校名称", "学校")
    return text


class PayloadValidator:
    """Payload综合验证器"""

    def __init__(self):
        self.errors: List[str] = []

    def validate(self, payload: Dict[str, Any]) -> List[str]:
        """执行完整验证"""
        self.errors = []

        base_errors = require_payload(payload)
        self.errors.extend(base_errors)

        if base_errors:
            return self.errors

        if "child_profile" in payload:
            profile_errors = validate_child_profile(payload["child_profile"])
            self.errors.extend(profile_errors)

        if "raw_records" in payload:
            for i, record in enumerate(payload["raw_records"]):
                record_errors = validate_expense_record(record)
                for err in record_errors:
                    self.errors.append(f"raw_records[{i}]: {err}")

        if "preferences" in payload:
            pref_errors = validate_preferences(payload["preferences"])
            self.errors.extend(pref_errors)

        return self.errors

    def is_valid(self) -> bool:
        """检查是否有效"""
        return len(self.errors) == 0


def validate_budget_allocation(categories: Dict[str, float], total_budget: float) -> List[str]:
    """验证预算分配

    Args:
        categories: 分类预算字典
        total_budget: 总预算

    Returns:
        错误列表
    """
    errors = []
    category_total = sum(categories.values())
    if abs(category_total - total_budget) > 0.01:
        errors.append(f"分类预算合计({category_total})与总预算({total_budget})不符")
    return errors