"""Validation helpers for 儿童图书推荐 Agent.

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


class ListValidator(FieldValidator):
    """列表字段验证器"""

    def __init__(
        self,
        field_name: str,
        required: bool = True,
        min_length: int = 0,
        max_length: int = 100,
        item_validator: Optional[FieldValidator] = None
    ):
        super().__init__(field_name, required)
        self.min_length = min_length
        self.max_length = max_length
        self.item_validator = item_validator

    def validate(self, value: Any) -> List[str]:
        """验证列表字段"""
        self.errors = []
        if value is None:
            if self.required:
                self.errors.append(f"{self.field_name} 是必填字段")
            return self.errors

        if not isinstance(value, list):
            self.errors.append(f"{self.field_name} 必须是列表类型")
            return self.errors

        if len(value) < self.min_length:
            self.errors.append(f"{self.field_name} 至少需要 {self.min_length} 个元素")
        if len(value) > self.max_length:
            self.errors.append(f"{self.field_name} 最多只能有 {self.max_length} 个元素")

        if self.item_validator:
            for i, item in enumerate(value):
                item_errors = self.item_validator.validate(item)
                for err in item_errors:
                    self.errors.append(f"{self.field_name}[{i}]: {err}")

        return self.errors


class DictValidator(FieldValidator):
    """字典字段验证器"""

    def __init__(
        self,
        field_name: str,
        required: bool = True,
        required_keys: Optional[List[str]] = None,
        key_validators: Optional[Dict[str, FieldValidator]] = None
    ):
        super().__init__(field_name, required)
        self.required_keys = required_keys or []
        self.key_validators = key_validators or {}

    def validate(self, value: Any) -> List[str]:
        """验证字典字段"""
        self.errors = []
        if value is None:
            if self.required:
                self.errors.append(f"{self.field_name} 是必填字段")
            return self.errors

        if not isinstance(value, dict):
            self.errors.append(f"{self.field_name} 必须是字典类型")
            return self.errors

        for key in self.required_keys:
            if key not in value:
                self.errors.append(f"{self.field_name} 缺少必填字段: {key}")

        for key, validator in self.key_validators.items():
            if key in value:
                key_errors = validator.validate(value[key])
                for err in key_errors:
                    self.errors.append(f"{self.field_name}.{key}: {err}")

        return self.errors


class AgeValidator(NumberValidator):
    """年龄字段专用验证器"""

    def __init__(self, field_name: str = "年龄", required: bool = True):
        super().__init__(field_name, required, min_value=0, max_value=25, integer_only=True)

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
        if age > 25:
            self.errors.append(f"{self.field_name} 超出合理范围（0-25岁）")

        return self.errors


class RatingValidator(NumberValidator):
    """评分字段专用验证器"""

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
        错误列表，如果有错误则非空
    """
    errors: List[str] = []
    if not isinstance(payload, dict):
        return ["payload 必须是 dict"]
    if not payload.get("child_profile"):
        errors.append("缺少 child_profile")
    if not str(payload.get("current_problem", "")).strip():
        errors.append("缺少 current_problem")
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

    if "reading_level" in profile:
        valid_levels = {"pre_reader", "emerging", "developing", "fluent", "advanced"}
        if profile["reading_level"] not in valid_levels:
            errors.append(f"reading_level 必须是以下值之一: {', '.join(valid_levels)}")

    return errors


def validate_reading_session(session: Dict[str, Any]) -> List[str]:
    """验证共读会话

    Args:
        session: 共读会话字典

    Returns:
        错误列表
    """
    errors = []

    if not isinstance(session, dict):
        return ["session 必须是字典类型"]

    if not session.get("book_title"):
        errors.append("缺少书名 (book_title)")

    date_validator = DateValidator("日期", required=False)
    date_errors = date_validator.validate(session.get("date"))
    errors.extend(date_errors)

    duration_validator = NumberValidator("时长", required=False, min_value=1, max_value=180, integer_only=True)
    duration_errors = duration_validator.validate(session.get("duration_minutes"))
    errors.extend(duration_errors)

    engagement_validator = RatingValidator("参与度")
    engagement_errors = engagement_validator.validate(session.get("child_engagement"))
    errors.extend(engagement_errors)

    return errors


def validate_book_recommendation(book: Dict[str, Any]) -> List[str]:
    """验证图书推荐

    Args:
        book: 图书推荐字典

    Returns:
        错误列表
    """
    errors = []

    if not isinstance(book, dict):
        return ["book 必须是字典类型"]

    title_validator = StringValidator("书名", required=True, min_length=1, max_length=200)
    title_errors = title_validator.validate(book.get("title"))
    errors.extend(title_errors)

    if "educational_value" in book:
        rating_validator = RatingValidator("教育价值")
        rating_errors = rating_validator.validate(book.get("educational_value"))
        errors.extend(rating_errors)

    if "engagement_score" in book:
        score_validator = RatingValidator("趣味性")
        score_errors = score_validator.validate(book.get("engagement_score"))
        errors.extend(score_errors)

    if "purchase_priority" in book:
        priority_validator = NumberValidator("优先级", required=False, min_value=1, max_value=5, integer_only=True)
        priority_errors = priority_validator.validate(book.get("purchase_priority"))
        errors.extend(priority_errors)

    return errors


def validate_records(records: List[Dict[str, Any]], record_type: str = "record") -> List[str]:
    """批量验证记录

    Args:
        records: 记录列表
        record_type: 记录类型标识

    Returns:
        错误列表
    """
    errors = []

    if not isinstance(records, list):
        return [f"{record_type}s 必须是列表类型"]

    if len(records) > 1000:
        errors.append(f"记录数量过多（{len(records)}），最多支持1000条")

    for i, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"{record_type}s[{i}] 必须是字典类型")

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
        budget_validator = NumberValidator("预算", required=False, min_value=0)
        budget_errors = budget_validator.validate(preferences["budget"])
        errors.extend(budget_errors)

    return errors


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
            record_errors = validate_records(payload["raw_records"])
            self.errors.extend(record_errors)

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


def validate_budget_range(budget: Union[int, float], min_amount: float = 0, max_amount: float = 100000) -> List[str]:
    """验证预算范围

    Args:
        budget: 预算金额
        min_amount: 最小金额
        max_amount: 最大金额

    Returns:
        错误列表
    """
    errors = []
    try:
        amount = float(budget)
        if amount < min_amount:
            errors.append(f"预算不能低于 {min_amount}")
        if amount > max_amount:
            errors.append(f"预算不能超过 {max_amount}")
    except (ValueError, TypeError):
        errors.append("预算必须是数字")
    return errors


def validate_age_compatibility(child_age: int, recommended_age_range: str) -> bool:
    """验证年龄兼容性

    Args:
        child_age: 孩子年龄
        recommended_age_range: 推荐年龄范围（如 "3-5岁"）

    Returns:
        是否兼容
    """
    if not recommended_age_range:
        return True

    match = re.search(r"(\d+)-(\d+)", recommended_age_range)
    if match:
        min_age = int(match.group(1))
        max_age = int(match.group(2))
        return min_age <= child_age <= max_age

    match = re.search(r"(\d+)\+", recommended_age_range)
    if match:
        min_age = int(match.group(1))
        return child_age >= min_age

    return True