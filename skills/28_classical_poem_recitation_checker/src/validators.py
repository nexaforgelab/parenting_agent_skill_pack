"""Validation helpers for 古诗背诵检查 Agent.

提供增强的验证功能，包括字段级别验证、数据范围检查、格式验证和自定义错误消息。
"""
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import re


class ValidationError:
    """验证错误类"""

    def __init__(self, field: str, message: str, code: str = "INVALID"):
        self.field = field
        self.message = message
        self.code = code

    def __str__(self) -> str:
        return f"[{self.code}] {self.field}: {self.message}"

    def to_dict(self) -> Dict[str, str]:
        return {
            "field": self.field,
            "message": self.message,
            "code": self.code
        }


class Validator:
    """验证器基类"""

    @staticmethod
    def required(value: Any, field_name: str) -> List[ValidationError]:
        errors = []
        if value is None:
            errors.append(ValidationError(field_name, "该字段为必填项", "REQUIRED"))
        elif isinstance(value, str) and not value.strip():
            errors.append(ValidationError(field_name, "该字段不能为空", "EMPTY"))
        elif isinstance(value, (list, dict)) and len(value) == 0:
            errors.append(ValidationError(field_name, "该字段不能为空", "EMPTY"))
        return errors

    @staticmethod
    def range(value: float, min_val: float, max_val: float, field_name: str) -> List[ValidationError]:
        errors = []
        if value is not None:
            if not isinstance(value, (int, float)):
                errors.append(ValidationError(field_name, "必须是数字", "TYPE_ERROR"))
            elif value < min_val or value > max_val:
                errors.append(ValidationError(
                    field_name,
                    f"值必须在 {min_val} 到 {max_val} 之间",
                    "OUT_OF_RANGE"
                ))
        return errors

    @staticmethod
    def is_in(value: Any, allowed_values: List[Any], field_name: str) -> List[ValidationError]:
        errors = []
        if value and value not in allowed_values:
            errors.append(ValidationError(
                field_name,
                f"值必须是以下之一: {', '.join(str(v) for v in allowed_values)}",
                "NOT_IN_ALLOWED"
            ))
        return errors


def require_payload(payload: Dict[str, Any]) -> List[str]:
    """验证输入负载的基本要求"""
    errors = []
    if not isinstance(payload, dict):
        return ["payload 必须是 dict 类型"]

    validator = Validator()

    error_list = validator.required(payload.get("child_profile"), "child_profile")
    for err in error_list:
        errors.append(str(err))

    error_list = validator.required(payload.get("current_problem"), "current_problem")
    for err in error_list:
        errors.append(str(err))

    return errors


def validate_learning_record(record: Dict[str, Any]) -> List[str]:
    """验证学习记录"""
    errors = []
    validator = Validator()

    if not isinstance(record, dict):
        return ["学习记录必须是字典类型"]

    error_list = validator.required(record.get("record_id"), "record_id")
    for err in error_list:
        errors.append(str(err))

    accuracy_rate = record.get("accuracy_rate", 0.0)
    error_list = validator.range(accuracy_rate, 0, 1, "accuracy_rate")
    for err in error_list:
        errors.append(str(err))

    error_count = record.get("error_count", 0)
    error_list = validator.range(error_count, 0, 1000, "error_count")
    for err in error_list:
        errors.append(str(err))

    difficulty_level = record.get("difficulty_level", "")
    if difficulty_level:
        allowed_levels = ["简单", "中等", "困难", "未知"]
        error_list = validator.is_in(difficulty_level, allowed_levels, "difficulty_level")
        for err in error_list:
            errors.append(str(err))

    return errors


def safe_list(value: Any) -> List[Any]:
    """安全地转换为列表"""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def safe_dict(value: Any) -> Dict[str, Any]:
    """安全地转换为字典"""
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    return {}


def anonymize_if_needed(text: str, privacy_mode: str) -> str:
    """根据隐私模式进行匿名化处理"""
    if privacy_mode in {"anonymous", "family_local_first"}:
        replacements = [
            ("孩子姓名", "孩子"),
            ("学校名称", "学校"),
        ]
        for old, new in replacements:
            text = text.replace(old, new)
    return text


def sanitize_input(text: str) -> str:
    """清理输入文本"""
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', text)
    return text


def batch_validate(records: List[Dict[str, Any]], validator_func: callable) -> Dict[int, List[str]]:
    """批量验证记录"""
    results = {}
    for i, record in enumerate(records):
        errors = validator_func(record)
        if errors:
            results[i] = errors
    return results
