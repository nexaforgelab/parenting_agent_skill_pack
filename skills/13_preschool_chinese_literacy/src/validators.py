"""Validation helpers for 幼儿识字启蒙 Agent."""
from typing import Any, Dict, List, Optional
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
    def is_dict(value: Any, field_name: str) -> Optional[str]:
        """验证是否为字典类型"""
        if value is not None and not isinstance(value, dict):
            return f"{field_name} 必须是字典类型"
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

    return errors


def validate_character_record(record: Dict[str, Any]) -> List[str]:
    """验证汉字记录数据"""
    errors: List[str] = []

    if not isinstance(record, dict):
        return ["record 必须是字典类型"]

    error = FieldValidator.required(record.get("character"), "character")
    if error:
        errors.append(error)

    practice_count = record.get("practice_count", 0)
    correct_count = record.get("correct_count", 0)
    if correct_count > practice_count:
        errors.append("correct_count 不能超过 practice_count")

    difficulty = record.get("difficulty_rating", 0.0)
    error = FieldValidator.range_float(difficulty, 0.0, 10.0, "difficulty_rating")
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


def anonymize_if_needed(text: str, privacy_mode: str) -> str:
    """根据隐私模式匿名化文本"""
    if privacy_mode in {"anonymous", "family_local_first"}:
        return text.replace("孩子姓名", "孩子").replace("学校名称", "学校")
    return text