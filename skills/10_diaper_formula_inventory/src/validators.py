"""Validation helpers for 尿布奶粉库存 skills."""
from typing import Any, Dict, List, Optional, Callable
import re
from datetime import datetime


class ValidationError(Exception):
    """验证错误异常类."""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"字段 '{field}': {message}")


class Validator:
    """验证器类."""
    def __init__(self, field_name: str):
        self.field_name = field_name
        self.errors: List[str] = []

    def required(self, value: Any, message: Optional[str] = None) -> "Validator":
        if value is None or (isinstance(value, str) and not value.strip()):
            self.errors.append(message or f"{self.field_name} 是必填字段")
        return self

    def type_check(self, value: Any, expected_type: type, message: Optional[str] = None) -> "Validator":
        if not isinstance(value, expected_type):
            self.errors.append(message or f"{self.field_name} 必须是 {expected_type.__name__} 类型")
        return self

    def range_check(self, value: float, min_val: Optional[float] = None,
                   max_val: Optional[float] = None, message: Optional[str] = None) -> "Validator":
        if value is not None:
            if min_val is not None and value < min_val:
                self.errors.append(message or f"{self.field_name} 必须大于等于 {min_val}")
            if max_val is not None and value > max_val:
                self.errors.append(message or f"{self.field_name} 必须小于等于 {max_val}")
        return self

    def get_errors(self) -> List[str]:
        return self.errors

    def is_valid(self) -> bool:
        return len(self.errors) == 0


def require_payload(payload: Dict[str, Any]) -> List[str]:
    """验证输入载荷的基本有效性."""
    errors: List[str] = []
    if not isinstance(payload, dict):
        return ["payload 必须是 dict 类型"]

    v = Validator("child_profile")
    v.required(payload.get("child_profile"), "缺少 child_profile")
    v.type_check(payload.get("child_profile"), dict)
    if not v.is_valid():
        errors.extend(v.get_errors())

    v2 = Validator("current_problem")
    v2.required(payload.get("current_problem"), "缺少 current_problem")
    if not v2.is_valid():
        errors.extend(v2.get_errors())

    return errors


def validate_inventory_record(record: Dict[str, Any]) -> List[str]:
    """验证库存记录."""
    errors: List[str] = []

    if "current_quantity" in record:
        v = Validator("current_quantity")
        v.type_check(record["current_quantity"], (int, float))
        v.range_check(record["current_quantity"], min_val=0)
        if not v.is_valid():
            errors.extend(v.get_errors())

    return errors


def safe_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def anonymize_if_needed(text: str, privacy_mode: str) -> str:
    """根据隐私模式对文本进行脱敏处理."""
    if privacy_mode in {"anonymous", "family_local_first"}:
        text = text.replace("品牌名称", "品牌")
    return text


def sanitize_input(text: str) -> str:
    if not isinstance(text, str):
        return ""
    sanitized = text.strip()
    sanitized = re.sub(r'[<>"\';]', '', sanitized)
    if len(sanitized) > 10000:
        sanitized = sanitized[:10000]
    return sanitized
