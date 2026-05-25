"""Validation helpers for 睡前故事生成 Agent.

提供完整的验证功能，支持字段级别验证、数据范围检查和自定义错误消息。
"""
from typing import Any, Dict, List, Optional, Callable
import re
from datetime import datetime


class ValidationError(Exception):
    """验证错误异常类"""
    def __init__(self, field: str, message: str, error_code: str = "VALIDATION_ERROR"):
        self.field = field
        self.message = message
        self.error_code = error_code
        super().__init__(f"[{error_code}] {field}: {message}")


class FieldValidator:
    """字段验证器类"""

    @staticmethod
    def required(value: Any, field_name: str) -> Optional[str]:
        """验证必填字段"""
        if value is None or (isinstance(value, str) and not value.strip()):
            return f"{field_name} 为必填字段，不能为空"
        return None

    @staticmethod
    def min_length(value: str, min_len: int, field_name: str) -> Optional[str]:
        """验证字符串最小长度"""
        if value and len(str(value)) < min_len:
            return f"{field_name} 长度不能少于 {min_len} 个字符"
        return None

    @staticmethod
    def max_length(value: str, max_len: int, field_name: str) -> Optional[str]:
        """验证字符串最大长度"""
        if value and len(str(value)) > max_len:
            return f"{field_name} 长度不能超过 {max_len} 个字符"
        return None

    @staticmethod
    def range_int(value: int, min_val: int, max_val: int, field_name: str) -> Optional[str]:
        """验证整数范围"""
        if value is not None and (value < min_val or value > max_val):
            return f"{field_name} 必须在 {min_val}-{max_val} 之间"
        return None

    @staticmethod
    def range_float(value: float, min_val: float, max_val: float, field_name: str) -> Optional[str]:
        """验证浮点数范围"""
        if value is not None and (value < min_val or value > max_val):
            return f"{field_name} 必须在 {min_val}-{max_val} 之间"
        return None

    @staticmethod
    def in_choices(value: Any, choices: List[Any], field_name: str) -> Optional[str]:
        """验证值是否在可选列表中"""
        if value is not None and value not in choices:
            return f"{field_name} 必须是以下值之一: {', '.join(str(c) for c in choices)}"
        return None

    @staticmethod
    def is_dict(value: Any, field_name: str) -> Optional[str]:
        """验证是否为字典类型"""
        if value is not None and not isinstance(value, dict):
            return f"{field_name} 必须是字典类型"
        return None

    @staticmethod
    def is_list(value: Any, field_name: str) -> Optional[str]:
        """验证是否为列表类型"""
        if value is not None and not isinstance(value, list):
            return f"{field_name} 必须是列表类型"
        return None

    @staticmethod
    def list_min_length(value: List, min_len: int, field_name: str) -> Optional[str]:
        """验证列表最小长度"""
        if value is not None and len(value) < min_len:
            return f"{field_name} 至少需要 {min_len} 个元素"
        return None

    @staticmethod
    def date_format(value: str, format_str: str, field_name: str) -> Optional[str]:
        """验证日期格式"""
        if value:
            try:
                datetime.strptime(value, format_str)
            except ValueError:
                return f"{field_name} 格式不正确，应为 {format_str}"
        return None

    @staticmethod
    def pattern(value: str, pattern: str, field_name: str) -> Optional[str]:
        """验证正则表达式匹配"""
        if value and not re.match(pattern, value):
            return f"{field_name} 格式不符合要求"
        return None


def require_payload(payload: Dict[str, Any]) -> List[str]:
    """验证主负载数据"""
    errors: List[str] = []
    if not isinstance(payload, dict):
        return ["payload 必须是 dict"]

    error = FieldValidator.required(payload.get("child_profile"), "child_profile")
    if error:
        errors.append(error)

    error = FieldValidator.required(payload.get("current_problem"), "current_problem")
    if error:
        errors.append(error)

    history_days = payload.get("history_days", 7)
    error = FieldValidator.range_int(history_days, 1, 365, "history_days")
    if error:
        errors.append(error)

    privacy_mode = payload.get("privacy_mode", "family_local_first")
    error = FieldValidator.in_choices(privacy_mode, ["anonymous", "family_local_first", "full_shared"], "privacy_mode")
    if error:
        errors.append(error)

    return errors


def validate_child_profile(profile: Dict[str, Any]) -> List[str]:
    """验证孩子画像数据"""
    errors: List[str] = []

    if not isinstance(profile, dict):
        return ["child_profile 必须是字典类型"]

    age = profile.get("age")
    if age:
        age_pattern = r"^\d+\s*岁|^\d+\s*个月|^\d+\s*岁\s*\d+\s*个月"
        error = FieldValidator.pattern(str(age), age_pattern, "age")
        if error:
            errors.append(error)

    return errors


def validate_story_record(record: Dict[str, Any]) -> List[str]:
    """验证故事记录数据"""
    errors: List[str] = []

    if not isinstance(record, dict):
        return ["record 必须是字典类型"]

    error = FieldValidator.required(record.get("story_title"), "story_title")
    if error:
        errors.append(error)

    duration = record.get("duration_minutes", 0)
    error = FieldValidator.range_int(duration, 1, 30, "duration_minutes")
    if error:
        errors.append(error)

    engagement = record.get("child_engagement", 0.0)
    error = FieldValidator.range_float(engagement, 0.0, 10.0, "child_engagement")
    if error:
        errors.append(error)

    return errors


def safe_list(value: Any) -> List[Any]:
    """安全转换为列表"""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def safe_dict(value: Any) -> Dict[str, Any]:
    """安全转换为字典"""
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    return {}


def anonymize_if_needed(text: str, privacy_mode: str) -> str:
    """根据隐私模式匿名化文本"""
    if privacy_mode in {"anonymous", "family_local_first"}:
        return text.replace("孩子姓名", "孩子").replace("学校名称", "学校")
    return text


def validate_and_sanitize_payload(payload: Dict[str, Any]) -> tuple[bool, List[str], Dict[str, Any]]:
    """验证并清理负载数据"""
    errors: List[str] = []

    if not isinstance(payload, dict):
        return False, ["payload 必须是字典类型"], {}

    errors.extend(require_payload(payload))
    errors.extend(validate_child_profile(payload.get("child_profile", {})))

    if errors:
        return False, errors, payload

    sanitized = payload.copy()
    privacy_mode = sanitized.get("privacy_mode", "family_local_first")

    if privacy_mode in {"anonymous", "family_local_first"}:
        if "child_profile" in sanitized and "nickname" in sanitized["child_profile"]:
            sanitized["child_profile"]["nickname"] = "孩子"

    return True, [], sanitized