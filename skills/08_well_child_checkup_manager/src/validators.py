"""Validation helpers for 宝宝体检记录管理 skills.

提供完善的字段级验证、数据范围检查和格式验证功能。
"""
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
    """验证器类，提供链式调用验证方法."""
    def __init__(self, field_name: str):
        self.field_name = field_name
        self.errors: List[str] = []

    def required(self, value: Any, message: Optional[str] = None) -> "Validator":
        """验证字段是否必填."""
        if value is None or (isinstance(value, str) and not value.strip()):
            msg = message or f"{self.field_name} 是必填字段"
            self.errors.append(msg)
        return self

    def type_check(self, value: Any, expected_type: type, message: Optional[str] = None) -> "Validator":
        """验证字段类型."""
        if not isinstance(value, expected_type):
            msg = message or f"{self.field_name} 必须是 {expected_type.__name__} 类型"
            self.errors.append(msg)
        return self

    def range_check(self, value: float, min_val: Optional[float] = None,
                   max_val: Optional[float] = None, message: Optional[str] = None) -> "Validator":
        """验证数值范围."""
        if value is not None:
            if min_val is not None and value < min_val:
                msg = message or f"{self.field_name} 必须大于等于 {min_val}"
                self.errors.append(msg)
            if max_val is not None and value > max_val:
                msg = message or f"{self.field_name} 必须小于等于 {max_val}"
                self.errors.append(msg)
        return self

    def length_check(self, value: str, min_len: Optional[int] = None,
                    max_len: Optional[int] = None, message: Optional[str] = None) -> "Validator":
        """验证字符串长度."""
        if value is not None and isinstance(value, str):
            length = len(value)
            if min_len is not None and length < min_len:
                msg = message or f"{self.field_name} 长度必须至少 {min_len} 个字符"
                self.errors.append(msg)
            if max_len is not None and length > max_len:
                msg = message or f"{self.field_name} 长度不能超过 {max_len} 个字符"
                self.errors.append(msg)
        return self

    def pattern_check(self, value: str, pattern: str, message: Optional[str] = None) -> "Validator":
        """验证字符串格式."""
        if value is not None and isinstance(value, str):
            if not re.match(pattern, value):
                msg = message or f"{self.field_name} 格式不正确"
                self.errors.append(msg)
        return self

    def enum_check(self, value: Any, allowed_values: List[Any], message: Optional[str] = None) -> "Validator":
        """验证枚举值."""
        if value is not None and value not in allowed_values:
            msg = message or f"{self.field_name} 必须是以下值之一: {', '.join(map(str, allowed_values))}"
            self.errors.append(msg)
        return self

    def custom(self, value: Any, validator_func: Callable[[Any], bool],
              message: str) -> "Validator":
        """自定义验证函数."""
        if not validator_func(value):
            self.errors.append(message)
        return self

    def get_errors(self) -> List[str]:
        """获取所有验证错误."""
        return self.errors

    def is_valid(self) -> bool:
        """检查是否验证通过."""
        return len(self.errors) == 0


def require_payload(payload: Dict[str, Any]) -> List[str]:
    """验证输入载荷的基本有效性."""
    errors: List[str] = []
    if not isinstance(payload, dict):
        return ["payload 必须是 dict 类型"]

    v = Validator("child_profile")
    v.required(payload.get("child_profile"), "缺少 child_profile")
    v.type_check(payload.get("child_profile"), dict, "child_profile 必须是字典类型")
    if not v.is_valid():
        errors.extend(v.get_errors())

    v2 = Validator("current_problem")
    v2.required(payload.get("current_problem"), "缺少 current_problem")
    v2.type_check(payload.get("current_problem"), str, "current_problem 必须是字符串")
    if not v2.is_valid():
        errors.extend(v2.get_errors())

    return errors


def validate_child_profile(profile: Dict[str, Any]) -> List[str]:
    """验证儿童档案的完整性."""
    errors: List[str] = []

    required_fields = ["name", "birth_date", "gender"]
    for field in required_fields:
        v = Validator(field)
        v.required(profile.get(field), f"儿童档案缺少必填字段: {field}")
        if not v.is_valid():
            errors.extend(v.get_errors())

    if "birth_date" in profile:
        v = Validator("birth_date")
        v.pattern_check(profile["birth_date"], r"^\d{4}-\d{2}-\d{2}$", "出生日期格式必须是 YYYY-MM-DD")
        if not v.is_valid():
            errors.extend(v.get_errors())

    if "gender" in profile:
        v = Validator("gender")
        v.enum_check(profile["gender"], ["男", "女", "其他"], "性别必须是 男、女 或 其他")
        if not v.is_valid():
            errors.extend(v.get_errors())

    return errors


def validate_checkup_record(record: Dict[str, Any]) -> List[str]:
    """验证体检记录."""
    errors: List[str] = []

    if "height_cm" in record and record["height_cm"]:
        v = Validator("height_cm")
        v.range_check(record["height_cm"], min_val=0, max_val=200)
        if not v.is_valid():
            errors.extend(v.get_errors())

    if "weight_kg" in record and record["weight_kg"]:
        v = Validator("weight_kg")
        v.range_check(record["weight_kg"], min_val=0, max_val=50)
        if not v.is_valid():
            errors.extend(v.get_errors())

    return errors


def validate_date_format(date_str: str, field_name: str = "日期") -> List[str]:
    """验证日期格式."""
    errors: List[str] = []
    v = Validator(field_name)
    v.required(date_str, f"{field_name} 不能为空")
    v.pattern_check(date_str, r"^\d{4}-\d{2}-\d{2}$", f"{field_name} 格式必须是 YYYY-MM-DD")
    if v.is_valid():
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            errors.append(f"{field_name} 不是有效的日期: {date_str}")
    else:
        errors.extend(v.get_errors())
    return errors


def safe_list(value: Any) -> List[Any]:
    """安全地将值转换为列表."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def safe_dict(value: Any) -> Dict[str, Any]:
    """安全地将值转换为字典."""
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    return {}


def anonymize_if_needed(text: str, privacy_mode: str) -> str:
    """根据隐私模式对文本进行脱敏处理."""
    if privacy_mode in {"anonymous", "family_local_first"}:
        text = text.replace("孩子姓名", "孩子")
        text = text.replace("医院名称", "医院")
        text = text.replace("医生姓名", "医生")
        text = re.sub(r"\d{3}-\d{4}-\d{4}", "***-****-****", text)
    return text


def sanitize_input(text: str) -> str:
    """对输入文本进行安全清洗."""
    if not isinstance(text, str):
        return ""
    sanitized = text.strip()
    sanitized = re.sub(r'[<>"\';]', '', sanitized)
    if len(sanitized) > 10000:
        sanitized = sanitized[:10000]
    return sanitized


def batch_validate(records: List[Dict[str, Any]],
                   validators: Dict[str, Callable[[Any], List[str]]]) -> Dict[int, List[str]]:
    """批量验证记录列表."""
    all_errors: Dict[int, List[str]] = {}
    for idx, record in enumerate(records):
        record_errors = []
        for field, validator_func in validators.items():
            value = record.get(field)
            errors = validator_func(value)
            record_errors.extend([f"{field}: {err}" for err in errors])
        if record_errors:
            all_errors[idx] = record_errors
    return all_errors
