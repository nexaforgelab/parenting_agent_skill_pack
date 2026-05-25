"""Validation helpers for 儿童玩具选购 Agent.

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
        max_length: int = 1000,
        pattern: Optional[str] = None,
        pattern_message: Optional[str] = None
    ):
        super().__init__(field_name, required)
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = pattern
        self.pattern_message = pattern_message

    def validate(self, value: Any) -> List[str]:
        """验证字符串字段"""
        self.errors = []
        if value is None:
            if self.required:
                self.errors.append(f"{self.field_name} 是必填字段")
            return self.errors

        value_str = str(value)
        if not isinstance(value, (str, int, float)):
            self.errors.append(f"{self.field_name} 必须是字符串类型")
            return self.errors

        if len(value_str) < self.min_length:
            self.errors.append(f"{self.field_name} 长度不能少于 {self.min_length} 个字符")
        if len(value_str) > self.max_length:
            self.errors.append(f"{self.field_name} 长度不能超过 {self.max_length} 个字符")

        if self.pattern and not re.match(self.pattern, value_str):
            msg = self.pattern_message or f"{self.field_name} 格式不正确"
            self.errors.append(msg)

        return self.errors


class NumberValidator(FieldValidator):
    """数字字段验证器"""

    def __init__(
        self,
        field_name: str,
        required: bool = True,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        integer_only: bool = False
    ):
        super().__init__(field_name, required)
        self.min_value = min_value
        self.max_value = max_value
        self.integer_only = integer_only

    def validate(self, value: Any) -> List[str]:
        """验证数字字段"""
        self.errors = []
        if value is None:
            if self.required:
                self.errors.append(f"{self.field_name} 是必填字段")
            return self.errors

        try:
            if self.integer_only:
                num_value = int(value)
            else:
                num_value = float(value)
        except (ValueError, TypeError):
            self.errors.append(f"{self.field_name} 必须是数字类型")
            return self.errors

        if self.min_value is not None and num_value < self.min_value:
            self.errors.append(f"{self.field_name} 不能小于 {self.min_value}")
        if self.max_value is not None and num_value > self.max_value:
            self.errors.append(f"{self.field_name} 不能大于 {self.max_value}")

        return self.errors


class AgeValidator(NumberValidator):
    """年龄字段专用验证器"""

    def __init__(self, field_name: str = "年龄", required: bool = True):
        super().__init__(field_name, required, min_value=0, max_value=18, integer_only=True)

    def validate(self, value: Any) -> List[str]:
        """验证年龄字段"""
        self.errors = []
        if value is None:
            if self.required:
                self.errors.append(f"{self.field_name} 是必填字段")
            return self.errors

        try:
            age = int(value)
        except (ValueError, TypeError):
            self.errors.append(f"{self.field_name} 必须是整数")
            return self.errors

        if age < 0:
            self.errors.append(f"{self.field_name} 不能为负数")
        if age > 18:
            self.errors.append(f"{self.field_name} 超出合理范围（0-18岁）")

        return self.errors


class BudgetValidator(NumberValidator):
    """预算字段验证器"""

    def __init__(self, field_name: str = "预算"):
        super().__init__(field_name, required=False, min_value=0, max_value=1000000)


class RatingValidator(NumberValidator):
    """评分字段验证器"""

    def __init__(self, field_name: str = "评分"):
        super().__init__(field_name, required=False, min_value=0, max_value=5)


class DateValidator(FieldValidator):
    """日期字段验证器"""

    def __init__(
        self,
        field_name: str = "日期",
        required: bool = True,
        date_format: str = "%Y-%m-%d",
        min_date: Optional[date] = None,
        max_date: Optional[date] = None
    ):
        super().__init__(field_name, required)
        self.date_format = date_format
        self.min_date = min_date
        self.max_date = max_date

    def validate(self, value: Any) -> List[str]:
        """验证日期字段"""
        self.errors = []
        if value is None:
            if self.required:
                self.errors.append(f"{self.field_name} 是必填字段")
            return self.errors

        if isinstance(value, (datetime, date)):
            parsed_date = value.date() if isinstance(value, datetime) else value
        elif isinstance(value, str):
            try:
                parsed_date = datetime.strptime(value, self.date_format).date()
            except ValueError:
                self.errors.append(f"{self.field_name} 日期格式不正确，应为 {self.date_format}")
                return self.errors
        else:
            self.errors.append(f"{self.field_name} 必须是日期或字符串类型")
            return self.errors

        if self.min_date and parsed_date < self.min_date:
            self.errors.append(f"{self.field_name} 不能早于 {self.min_date.isoformat()}")
        if self.max_date and parsed_date > self.max_date:
            self.errors.append(f"{self.field_name} 不能晚于 {self.max_date.isoformat()}")

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


def validate_toy_recommendation(toy: Dict[str, Any]) -> List[str]:
    """验证玩具推荐

    Args:
        toy: 玩具推荐字典

    Returns:
        错误列表
    """
    errors = []

    if not isinstance(toy, dict):
        return ["toy 必须是字典类型"]

    name_validator = StringValidator("玩具名称", required=True, min_length=1, max_length=200)
    name_errors = name_validator.validate(toy.get("name"))
    errors.extend(name_errors)

    if "educational_value" in toy:
        rating_validator = RatingValidator("教育价值")
        rating_errors = rating_validator.validate(toy.get("educational_value"))
        errors.extend(rating_errors)

    if "durability_score" in toy:
        durability_validator = RatingValidator("耐玩性")
        durability_errors = durability_validator.validate(toy.get("durability_score"))
        errors.extend(durability_errors)

    if "engagement_score" in toy:
        engagement_validator = RatingValidator("趣味性")
        engagement_errors = engagement_validator.validate(toy.get("engagement_score"))
        errors.extend(engagement_errors)

    if "safety_rating" in toy:
        valid_ratings = {
            "age_appropriate", "supervision_required", "small_parts_warning",
            "choking_hazard", "electrical_safety"
        }
        if toy["safety_rating"] not in valid_ratings:
            errors.append(f"safety_rating 必须是以下值之一: {', '.join(valid_ratings)}")

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

    age_validator = AgeValidator("年龄", required=False)
    age_errors = age_validator.validate(profile.get("age_years"))
    errors.extend(age_errors)

    if "interests" in profile and not isinstance(profile["interests"], list):
        errors.append("interests 必须是列表类型")

    if "existing_toys" in profile and not isinstance(profile["existing_toys"], list):
        errors.append("existing_toys 必须是列表类型")

    return errors


def validate_usage_record(record: Dict[str, Any]) -> List[str]:
    """验证使用记录

    Args:
        record: 使用记录字典

    Returns:
        错误列表
    """
    errors = []

    if not isinstance(record, dict):
        return ["record 必须是字典类型"]

    if not record.get("toy_name"):
        errors.append("缺少玩具名称 (toy_name)")

    duration_validator = NumberValidator("使用时长", required=False, min_value=0, max_value=480, integer_only=True)
    duration_errors = duration_validator.validate(record.get("duration_minutes"))
    errors.extend(duration_errors)

    engagement_validator = RatingValidator("参与度")
    engagement_errors = engagement_validator.validate(record.get("child_engagement"))
    errors.extend(engagement_errors)

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
        budget_validator = BudgetValidator("预算")
        budget_errors = budget_validator.validate(preferences["budget"])
        errors.extend(budget_errors)

    return errors


def validate_budget(budget: Union[int, float], max_limit: float = 1000000) -> List[str]:
    """验证预算范围

    Args:
        budget: 预算金额
        max_limit: 最大限制

    Returns:
        错误列表
    """
    errors = []
    try:
        amount = float(budget)
        if amount < 0:
            errors.append("预算不能为负数")
        if amount > max_limit:
            errors.append(f"预算超出限制（最多 {max_limit}）")
    except (ValueError, TypeError):
        errors.append("预算必须是数字")
    return errors


def validate_age_appropriate(child_age: int, toy_age_range: str) -> bool:
    """验证年龄适配性

    Args:
        child_age: 孩子年龄
        toy_age_range: 玩具适玩年龄范围

    Returns:
        是否适配
    """
    if not toy_age_range:
        return True

    if toy_age_range.startswith("0-"):
        try:
            max_age = int(toy_age_range.split("-")[1].replace("岁", ""))
            return child_age <= max_age
        except (ValueError, IndexError):
            pass

    if "-" in toy_age_range:
        parts = toy_age_range.split("-")
        try:
            min_age = int(parts[0].replace("岁", ""))
            max_age = int(parts[1].replace("岁", ""))
            return min_age <= child_age <= max_age
        except (ValueError, IndexError):
            pass

    if "+" in toy_age_range:
        try:
            min_age = int(toy_age_range.replace("+", "").replace("岁", ""))
            return child_age >= min_age
        except ValueError:
            pass

    return True


def safe_list(value: Any) -> List[Any]:
    """安全转换为列表

    Args:
        value: 输入值

    Returns:
        列表
    """
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def anonymize_if_needed(text: str, privacy_mode: str) -> str:
    """根据隐私模式脱敏处理

    Args:
        text: 原始文本
        privacy_mode: 隐私模式

    Returns:
        脱敏后的文本
    """
    if privacy_mode in {"anonymous", "family_local_first"}:
        return text.replace("孩子姓名", "孩子").replace("学校名称", "学校")
    return text


def sanitize_input(text: str, max_length: int = 5000) -> str:
    """清理输入文本

    Args:
        text: 原始文本
        max_length: 最大长度

    Returns:
        清理后的文本
    """
    if not isinstance(text, str):
        text = str(text)
    text = text.strip()
    if len(text) > max_length:
        text = text[:max_length] + "..."
    return text


class PayloadValidator:
    """Payload综合验证器"""

    def __init__(self):
        self.errors: List[str] = []

    def validate(self, payload: Dict[str, Any]) -> List[str]:
        """执行完整验证

        Args:
            payload: 输入payload

        Returns:
            错误列表
        """
        self.errors = []

        base_errors = require_payload(payload)
        self.errors.extend(base_errors)

        if base_errors:
            return self.errors

        if "child_profile" in payload:
            profile_errors = validate_child_profile(payload["child_profile"])
            self.errors.extend(profile_errors)

        if "raw_records" in payload:
            if not isinstance(payload["raw_records"], list):
                self.errors.append("raw_records 必须是列表类型")
            elif len(payload["raw_records"]) > 1000:
                self.errors.append(f"记录数量过多（{len(payload['raw_records'])}），最多支持1000条")

        if "preferences" in payload:
            pref_errors = validate_preferences(payload["preferences"])
            self.errors.extend(pref_errors)

        return self.errors

    def is_valid(self) -> bool:
        """检查是否有效

        Returns:
            是否没有错误
        """
        return len(self.errors) == 0


def validate_safety_certifications(certifications: List[str]) -> List[str]:
    """验证安全认证

    Args:
        certifications: 安全认证列表

    Returns:
        错误列表
    """
    errors = []

    if not isinstance(certifications, list):
        return ["certifications 必须是列表类型"]

    valid_certs = {
        "CCC", "CE", "FCC", "ASTM", "EN71", "ISO",
        "CPC", "KC", "PSE", "JIS"
    }

    for cert in certifications:
        if cert not in valid_certs:
            errors.append(f"未知的安全认证: {cert}，支持的认证: {', '.join(valid_certs)}")

    return errors