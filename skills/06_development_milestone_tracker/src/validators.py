"""Validation helpers for 月龄发育里程碑 skills.

提供完善的字段级验证、数据范围检查和格式验证功能。
支持自定义错误消息和批量验证。
"""
from typing import Any, Dict, List, Optional, Callable
import re
from datetime import datetime


class ValidationError(Exception):
    """验证错误异常类.

    包含字段名和错误消息，用于详细报告验证失败的原因。
    """

    def __init__(self, field: str, message: str):
        """初始化验证错误.

        Args:
            field: 字段名称
            message: 错误消息
        """
        self.field = field
        self.message = message
        super().__init__(f"字段 '{field}': {message}")


class Validator:
    """验证器类.

    提供链式调用验证方法，支持字段级验证和自定义规则。
    """

    def __init__(self, field_name: str):
        """初始化验证器.

        Args:
            field_name: 字段名称
        """
        self.field_name = field_name
        self.errors: List[str] = []

    def required(self, value: Any, message: Optional[str] = None) -> "Validator":
        """验证字段是否必填.

        Args:
            value: 待验证的值
            message: 自定义错误消息

        Returns:
            验证器自身，支持链式调用
        """
        if value is None or (isinstance(value, str) and not value.strip()):
            msg = message or f"{self.field_name} 是必填字段"
            self.errors.append(msg)
        return self

    def type_check(self, value: Any, expected_type: type, message: Optional[str] = None) -> "Validator":
        """验证字段类型.

        Args:
            value: 待验证的值
            expected_type: 期望的类型
            message: 自定义错误消息

        Returns:
            验证器自身
        """
        if not isinstance(value, expected_type):
            msg = message or f"{self.field_name} 必须是 {expected_type.__name__} 类型"
            self.errors.append(msg)
        return self

    def range_check(self, value: float, min_val: Optional[float] = None,
                   max_val: Optional[float] = None, message: Optional[str] = None) -> "Validator":
        """验证数值范围.

        Args:
            value: 待验证的数值
            min_val: 最小值（可选）
            max_val: 最大值（可选）
            message: 自定义错误消息

        Returns:
            验证器自身
        """
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
        """验证字符串长度.

        Args:
            value: 待验证的字符串
            min_len: 最小长度（可选）
            max_len: 最大长度（可选）
            message: 自定义错误消息

        Returns:
            验证器自身
        """
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
        """验证字符串格式.

        Args:
            value: 待验证的字符串
            pattern: 正则表达式模式
            message: 自定义错误消息

        Returns:
            验证器自身
        """
        if value is not None and isinstance(value, str):
            if not re.match(pattern, value):
                msg = message or f"{self.field_name} 格式不正确"
                self.errors.append(msg)
        return self

    def enum_check(self, value: Any, allowed_values: List[Any], message: Optional[str] = None) -> "Validator":
        """验证枚举值.

        Args:
            value: 待验证的值
            allowed_values: 允许的值列表
            message: 自定义错误消息

        Returns:
            验证器自身
        """
        if value is not None and value not in allowed_values:
            msg = message or f"{self.field_name} 必须是以下值之一: {', '.join(map(str, allowed_values))}"
            self.errors.append(msg)
        return self

    def custom(self, value: Any, validator_func: Callable[[Any], bool],
              message: str) -> "Validator":
        """自定义验证函数.

        Args:
            value: 待验证的值
            validator_func: 验证函数，返回 bool
            message: 错误消息

        Returns:
            验证器自身
        """
        if not validator_func(value):
            self.errors.append(message)
        return self

    def get_errors(self) -> List[str]:
        """获取所有验证错误.

        Returns:
            错误消息列表
        """
        return self.errors

    def is_valid(self) -> bool:
        """检查是否验证通过.

        Returns:
            True 如果没有错误
        """
        return len(self.errors) == 0


def require_payload(payload: Dict[str, Any]) -> List[str]:
    """验证输入载荷的基本有效性.

    Args:
        payload: 输入的载荷字典

    Returns:
        错误消息列表，空列表表示验证通过
    """
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
    v2.length_check(str(payload.get("current_problem", "")), min_len=1, max_len=5000)
    if not v2.is_valid():
        errors.extend(v2.get_errors())

    if "history_days" in payload:
        v3 = Validator("history_days")
        v3.type_check(payload.get("history_days"), int, "history_days 必须是整数")
        v3.range_check(payload.get("history_days", 0), min_val=0, max_val=365)
        if not v3.is_valid():
            errors.extend(v3.get_errors())

    return errors


def validate_child_profile(profile: Dict[str, Any]) -> List[str]:
    """验证儿童档案的完整性.

    Args:
        profile: 儿童档案字典

    Returns:
        错误消息列表
    """
    errors: List[str] = []

    required_fields = ["name", "birth_date", "gender"]
    for field in required_fields:
        v = Validator(field)
        v.required(profile.get(field), f"儿童档案缺少必填字段: {field}")
        if not v.is_valid():
            errors.extend(v.get_errors())

    if "birth_date" in profile:
        v = Validator("birth_date")
        v.pattern_check(
            profile["birth_date"],
            r"^\d{4}-\d{2}-\d{2}$",
            "出生日期格式必须是 YYYY-MM-DD"
        )
        if not v.is_valid():
            errors.extend(v.get_errors())

    if "gender" in profile:
        v = Validator("gender")
        v.enum_check(profile["gender"], ["男", "女", "其他"], "性别必须是 男、女 或 其他")
        if not v.is_valid():
            errors.extend(v.get_errors())

    if "birth_date" in profile and "name" in profile:
        try:
            birth = datetime.strptime(profile["birth_date"], "%Y-%m-%d")
            if birth > datetime.now():
                errors.append("出生日期不能是未来时间")
        except ValueError:
            pass

    return errors


def validate_date_format(date_str: str, field_name: str = "日期") -> List[str]:
    """验证日期格式.

    Args:
        date_str: 日期字符串
        field_name: 字段名称

    Returns:
        错误消息列表
    """
    errors: List[str] = []
    v = Validator(field_name)
    v.required(date_str, f"{field_name} 不能为空")
    v.pattern_check(
        date_str,
        r"^\d{4}-\d{2}-\d{2}$",
        f"{field_name} 格式必须是 YYYY-MM-DD"
    )
    if v.is_valid():
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            errors.append(f"{field_name} 不是有效的日期: {date_str}")
    else:
        errors.extend(v.get_errors())
    return errors


def validate_timestamp(timestamp: str) -> List[str]:
    """验证时间戳格式.

    Args:
        timestamp: ISO 格式的时间戳

    Returns:
        错误消息列表
    """
    errors: List[str] = []
    v = Validator("timestamp")
    v.required(timestamp, "时间戳不能为空")
    v.pattern_check(
        timestamp,
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
        "时间戳格式必须是 ISO 格式 (YYYY-MM-DDTHH:MM:SS)"
    )
    if not v.is_valid():
        errors.extend(v.get_errors())
    return errors


def validate_numeric_range(value: Any, field_name: str,
                           min_val: Optional[float] = None,
                           max_val: Optional[float] = None) -> List[str]:
    """验证数值范围.

    Args:
        value: 待验证的数值
        field_name: 字段名称
        min_val: 最小值（可选）
        max_val: 最大值（可选）

    Returns:
        错误消息列表
    """
    errors: List[str] = []
    v = Validator(field_name)
    v.type_check(value, (int, float), f"{field_name} 必须是数值类型")
    v.range_check(float(value) if value is not None else 0, min_val, max_val)
    if not v.is_valid():
        errors.extend(v.get_errors())
    return errors


def validate_enum_value(value: Any, field_name: str,
                        allowed_values: List[Any]) -> List[str]:
    """验证枚举值.

    Args:
        value: 待验证的值
        field_name: 字段名称
        allowed_values: 允许的值列表

    Returns:
        错误消息列表
    """
    errors: List[str] = []
    v = Validator(field_name)
    v.enum_check(value, allowed_values)
    if not v.is_valid():
        errors.extend(v.get_errors())
    return errors


def safe_list(value: Any) -> List[Any]:
    """安全地将值转换为列表.

    如果值是 None，返回空列表；
    如果已经是列表，直接返回；
    否则包装为单元素列表。

    Args:
        value: 待转换的值

    Returns:
        列表对象
    """
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def safe_dict(value: Any) -> Dict[str, Any]:
    """安全地将值转换为字典.

    Args:
        value: 待转换的值

    Returns:
        字典对象，空字典如果值不是字典类型
    """
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    return {}


def anonymize_if_needed(text: str, privacy_mode: str) -> str:
    """根据隐私模式对文本进行脱敏处理.

    Args:
        text: 原始文本
        privacy_mode: 隐私模式 (anonymous, family_local_first, full)

    Returns:
        脱敏后的文本
    """
    if privacy_mode in {"anonymous", "family_local_first"}:
        text = text.replace("孩子姓名", "孩子")
        text = text.replace("学校名称", "学校")
        text = text.replace("家长姓名", "家长")
        text = re.sub(r"\d{3}-\d{4}-\d{4}", "***-****-****", text)
        text = re.sub(r"\d{11}", "***********", text)
    return text


def sanitize_input(text: str) -> str:
    """对输入文本进行安全清洗.

    移除潜在的恶意内容和格式问题。

    Args:
        text: 原始输入文本

    Returns:
        清洗后的文本
    """
    if not isinstance(text, str):
        return ""

    sanitized = text.strip()
    sanitized = re.sub(r'[<>"\';]', '', sanitized)

    if len(sanitized) > 10000:
        sanitized = sanitized[:10000]

    return sanitized


def batch_validate(records: List[Dict[str, Any]],
                   validators: Dict[str, Callable[[Any], List[str]]]) -> Dict[int, List[str]]:
    """批量验证记录列表.

    Args:
        records: 记录列表
        validators: 验证器字典，key 是字段名，value 是验证函数

    Returns:
        错误字典，key 是记录索引，value 是错误列表
    """
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
