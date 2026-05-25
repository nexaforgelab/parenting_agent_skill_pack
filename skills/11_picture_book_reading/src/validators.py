"""Validation helpers for 绘本共读 Agent.

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
    """字段验证器类

    提供各类字段的验证方法，支持链式调用和自定义错误消息。
    """

    @staticmethod
    def required(value: Any, field_name: str) -> Optional[str]:
        """验证必填字段

        Args:
            value: 待验证的值
            field_name: 字段名称

        Returns:
            错误消息，如果验证通过则返回 None
        """
        if value is None or (isinstance(value, str) and not value.strip()):
            return f"{field_name} 为必填字段，不能为空"
        return None

    @staticmethod
    def min_length(value: str, min_len: int, field_name: str) -> Optional[str]:
        """验证字符串最小长度

        Args:
            value: 待验证的字符串
            min_len: 最小长度
            field_name: 字段名称

        Returns:
            错误消息，如果验证通过则返回 None
        """
        if value and len(str(value)) < min_len:
            return f"{field_name} 长度不能少于 {min_len} 个字符"
        return None

    @staticmethod
    def max_length(value: str, max_len: int, field_name: str) -> Optional[str]:
        """验证字符串最大长度

        Args:
            value: 待验证的字符串
            max_len: 最大长度
            field_name: 字段名称

        Returns:
            错误消息，如果验证通过则返回 None
        """
        if value and len(str(value)) > max_len:
            return f"{field_name} 长度不能超过 {max_len} 个字符"
        return None

    @staticmethod
    def range_int(value: int, min_val: int, max_val: int, field_name: str) -> Optional[str]:
        """验证整数范围

        Args:
            value: 待验证的整数
            min_val: 最小值
            max_val: 最大值
            field_name: 字段名称

        Returns:
            错误消息，如果验证通过则返回 None
        """
        if value is not None and (value < min_val or value > max_val):
            return f"{field_name} 必须在 {min_val}-{max_val} 之间"
        return None

    @staticmethod
    def range_float(value: float, min_val: float, max_val: float, field_name: str) -> Optional[str]:
        """验证浮点数范围

        Args:
            value: 待验证的浮点数
            min_val: 最小值
            max_val: 最大值
            field_name: 字段名称

        Returns:
            错误消息，如果验证通过则返回 None
        """
        if value is not None and (value < min_val or value > max_val):
            return f"{field_name} 必须在 {min_val}-{max_val} 之间"
        return None

    @staticmethod
    def in_choices(value: Any, choices: List[Any], field_name: str) -> Optional[str]:
        """验证值是否在可选列表中

        Args:
            value: 待验证的值
            choices: 可选值列表
            field_name: 字段名称

        Returns:
            错误消息，如果验证通过则返回 None
        """
        if value is not None and value not in choices:
            return f"{field_name} 必须是以下值之一: {', '.join(str(c) for c in choices)}"
        return None

    @staticmethod
    def is_dict(value: Any, field_name: str) -> Optional[str]:
        """验证是否为字典类型

        Args:
            value: 待验证的值
            field_name: 字段名称

        Returns:
            错误消息，如果验证通过则返回 None
        """
        if value is not None and not isinstance(value, dict):
            return f"{field_name} 必须是字典类型"
        return None

    @staticmethod
    def is_list(value: Any, field_name: str) -> Optional[str]:
        """验证是否为列表类型

        Args:
            value: 待验证的值
            field_name: 字段名称

        Returns:
            错误消息，如果验证通过则返回 None
        """
        if value is not None and not isinstance(value, list):
            return f"{field_name} 必须是列表类型"
        return None

    @staticmethod
    def list_min_length(value: List, min_len: int, field_name: str) -> Optional[str]:
        """验证列表最小长度

        Args:
            value: 待验证的列表
            min_len: 最小长度
            field_name: 字段名称

        Returns:
            错误消息，如果验证通过则返回 None
        """
        if value is not None and len(value) < min_len:
            return f"{field_name} 至少需要 {min_len} 个元素"
        return None

    @staticmethod
    def date_format(value: str, format_str: str, field_name: str) -> Optional[str]:
        """验证日期格式

        Args:
            value: 待验证的日期字符串
            format_str: 日期格式（如 "%Y-%m-%d"）
            field_name: 字段名称

        Returns:
            错误消息，如果验证通过则返回 None
        """
        if value:
            try:
                datetime.strptime(value, format_str)
            except ValueError:
                return f"{field_name} 格式不正确，应为 {format_str}"
        return None

    @staticmethod
    def pattern(value: str, pattern: str, field_name: str) -> Optional[str]:
        """验证正则表达式匹配

        Args:
            value: 待验证的字符串
            pattern: 正则表达式模式
            field_name: 字段名称

        Returns:
            错误消息，如果验证通过则返回 None
        """
        if value and not re.match(pattern, value):
            return f"{field_name} 格式不符合要求"
        return None

    @staticmethod
    def custom(value: Any, validator: Callable[[Any], bool], message: str, field_name: str) -> Optional[str]:
        """自定义验证器

        Args:
            value: 待验证的值
            validator: 验证函数，返回 True 表示通过
            message: 验证失败时的错误消息
            field_name: 字段名称

        Returns:
            错误消息，如果验证通过则返回 None
        """
        if value is not None and not validator(value):
            return f"{field_name}: {message}"
        return None


def require_payload(payload: Dict[str, Any]) -> List[str]:
    """验证主负载数据

    Args:
        payload: 输入的负载数据字典

    Returns:
        错误消息列表，如果验证通过则为空列表
    """
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
    """验证孩子画像数据

    Args:
        profile: 孩子画像字典

    Returns:
        错误消息列表
    """
    errors: List[str] = []

    if not isinstance(profile, dict):
        return ["child_profile 必须是字典类型"]

    age = profile.get("age")
    if age:
        age_pattern = r"^\d+\s*岁|^\d+\s*个月|^\d+\s*岁\s*\d+\s*个月"
        error = FieldValidator.pattern(str(age), age_pattern, "age")
        if error:
            errors.append(error)

    nickname = profile.get("nickname")
    if nickname:
        error = FieldValidator.max_length(nickname, 50, "nickname")
        if error:
            errors.append(error)

    return errors


def validate_raw_records(records: List[Dict[str, Any]]) -> List[str]:
    """验证原始记录数据

    Args:
        records: 原始记录列表

    Returns:
        错误消息列表
    """
    errors: List[str] = []

    if not isinstance(records, list):
        return ["raw_records 必须是列表类型"]

    for i, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"raw_records[{i}] 必须是字典类型")
            continue

        if record.get("time"):
            error = FieldValidator.max_length(record["time"], 50, f"raw_records[{i}].time")
            if error:
                errors.append(error)

        if record.get("event"):
            error = FieldValidator.max_length(record["event"], 500, f"raw_records[{i}].event")
            if error:
                errors.append(error)

    return errors


def validate_preferences(preferences: Dict[str, Any]) -> List[str]:
    """验证偏好设置数据

    Args:
        preferences: 偏好设置字典

    Returns:
        错误消息列表
    """
    errors: List[str] = []

    if not isinstance(preferences, dict):
        return ["preferences 必须是字典类型"]

    tone = preferences.get("tone")
    if tone:
        error = FieldValidator.in_choices(tone, ["温和", "活泼", "严肃", "幽默"], "tone")
        if error:
            errors.append(error)

    budget = preferences.get("budget")
    if budget:
        error = FieldValidator.in_choices(budget, ["低成本优先", "中等", "高预算"], "budget")
        if error:
            errors.append(error)

    return errors


def validate_learning_record(record: Dict[str, Any]) -> List[str]:
    """验证学习记录数据

    Args:
        record: 学习记录字典

    Returns:
        错误消息列表
    """
    errors: List[str] = []

    if not isinstance(record, dict):
        return ["record 必须是字典类型"]

    error = FieldValidator.required(record.get("record_id"), "record_id")
    if error:
        errors.append(error)

    duration = record.get("duration_minutes", 0)
    error = FieldValidator.range_int(duration, 0, 180, "duration_minutes")
    if error:
        errors.append(error)

    engagement = record.get("engagement_score", 0.0)
    error = FieldValidator.range_float(engagement, 0.0, 10.0, "engagement_score")
    if error:
        errors.append(error)

    questions_asked = record.get("questions_asked", 0)
    questions_answered = record.get("questions_answered", 0)
    if questions_answered > questions_asked:
        errors.append("questions_answered 不能超过 questions_asked")

    return errors


def validate_progress_stats(stats: Dict[str, Any]) -> List[str]:
    """验证进度统计数据

    Args:
        stats: 进度统计字典

    Returns:
        错误消息列表
    """
    errors: List[str] = []

    if not isinstance(stats, dict):
        return ["stats 必须是字典类型"]

    total_sessions = stats.get("total_sessions", 0)
    error = FieldValidator.range_int(total_sessions, 0, 10000, "total_sessions")
    if error:
        errors.append(error)

    total_minutes = stats.get("total_minutes", 0)
    error = FieldValidator.range_int(total_minutes, 0, 100000, "total_minutes")
    if error:
        errors.append(error)

    average_engagement = stats.get("average_engagement", 0.0)
    error = FieldValidator.range_float(average_engagement, 0.0, 10.0, "average_engagement")
    if error:
        errors.append(error)

    return errors


def safe_list(value: Any) -> List[Any]:
    """安全转换为列表

    Args:
        value: 待转换的值

    Returns:
        列表，如果输入为 None 则返回空列表
    """
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def safe_dict(value: Any) -> Dict[str, Any]:
    """安全转换为字典

    Args:
        value: 待转换的值

    Returns:
        字典，如果输入为 None 则返回空字典
    """
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    return {}


def anonymize_if_needed(text: str, privacy_mode: str) -> str:
    """根据隐私模式匿名化文本

    Args:
        text: 待处理的文本
        privacy_mode: 隐私模式

    Returns:
        处理后的文本
    """
    if privacy_mode in {"anonymous", "family_local_first"}:
        return text.replace("孩子姓名", "孩子").replace("学校名称", "学校")
    return text


def validate_and_sanitize_payload(payload: Dict[str, Any]) -> tuple[bool, List[str], Dict[str, Any]]:
    """验证并清理负载数据

    Args:
        payload: 输入的负载数据

    Returns:
        (是否有效, 错误消息列表, 清理后的数据)
    """
    errors: List[str] = []

    if not isinstance(payload, dict):
        return False, ["payload 必须是字典类型"], {}

    errors.extend(require_payload(payload))
    errors.extend(validate_child_profile(payload.get("child_profile", {})))
    errors.extend(validate_raw_records(payload.get("raw_records", [])))
    errors.extend(validate_preferences(payload.get("preferences", {})))

    if errors:
        return False, errors, payload

    sanitized = payload.copy()
    privacy_mode = sanitized.get("privacy_mode", "family_local_first")

    if privacy_mode in {"anonymous", "family_local_first"}:
        if "child_profile" in sanitized and "nickname" in sanitized["child_profile"]:
            sanitized["child_profile"]["nickname"] = "孩子"

    return True, [], sanitized