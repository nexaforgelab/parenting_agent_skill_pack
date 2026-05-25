"""Validation helpers for 小学作文陪练 Agent.

提供增强的验证功能，包括字段级别验证、数据范围检查、格式验证和自定义错误消息。
"""
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import re


class ValidationError:
    """验证错误类

    属性:
        field: 字段名
        message: 错误消息
        code: 错误代码
    """

    def __init__(self, field: str, message: str, code: str = "INVALID"):
        """初始化验证错误

        Args:
            field: 字段名
            message: 错误消息
            code: 错误代码
        """
        self.field = field
        self.message = message
        self.code = code

    def __str__(self) -> str:
        """字符串表示

        Returns:
            错误信息字符串
        """
        return f"[{self.code}] {self.field}: {self.message}"

    def to_dict(self) -> Dict[str, str]:
        """转换为字典

        Returns:
            字典格式的错误信息
        """
        return {
            "field": self.field,
            "message": self.message,
            "code": self.code
        }


class Validator:
    """验证器基类

    提供通用的验证功能
    """

    @staticmethod
    def required(value: Any, field_name: str) -> List[ValidationError]:
        """验证必填字段

        Args:
            value: 待验证的值
            field_name: 字段名

        Returns:
            验证错误列表
        """
        errors = []
        if value is None:
            errors.append(ValidationError(field_name, "该字段为必填项", "REQUIRED"))
        elif isinstance(value, str) and not value.strip():
            errors.append(ValidationError(field_name, "该字段不能为空", "EMPTY"))
        elif isinstance(value, (list, dict)) and len(value) == 0:
            errors.append(ValidationError(field_name, "该字段不能为空", "EMPTY"))
        return errors

    @staticmethod
    def min_length(value: str, min_len: int, field_name: str) -> List[ValidationError]:
        """验证最小长度

        Args:
            value: 待验证的值
            min_len: 最小长度
            field_name: 字段名

        Returns:
            验证错误列表
        """
        errors = []
        if value and len(str(value)) < min_len:
            errors.append(ValidationError(
                field_name,
                f"长度不能少于 {min_len} 个字符",
                "MIN_LENGTH"
            ))
        return errors

    @staticmethod
    def max_length(value: str, max_len: int, field_name: str) -> List[ValidationError]:
        """验证最大长度

        Args:
            value: 待验证的值
            max_len: 最大长度
            field_name: 字段名

        Returns:
            验证错误列表
        """
        errors = []
        if value and len(str(value)) > max_len:
            errors.append(ValidationError(
                field_name,
                f"长度不能超过 {max_len} 个字符",
                "MAX_LENGTH"
            ))
        return errors

    @staticmethod
    def range(value: float, min_val: float, max_val: float, field_name: str) -> List[ValidationError]:
        """验证数值范围

        Args:
            value: 待验证的值
            min_val: 最小值
            max_val: 最大值
            field_name: 字段名

        Returns:
            验证错误列表
        """
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
    def pattern(value: str, pattern: str, field_name: str, message: str = "格式不正确") -> List[ValidationError]:
        """验证正则表达式

        Args:
            value: 待验证的值
            pattern: 正则表达式
            field_name: 字段名
            message: 错误消息

        Returns:
            验证错误列表
        """
        errors = []
        if value and not re.match(pattern, str(value)):
            errors.append(ValidationError(field_name, message, "PATTERN_MISMATCH"))
        return errors

    @staticmethod
    def is_in(value: Any, allowed_values: List[Any], field_name: str) -> List[ValidationError]:
        """验证值在允许列表中

        Args:
            value: 待验证的值
            allowed_values: 允许的值列表
            field_name: 字段名

        Returns:
            验证错误列表
        """
        errors = []
        if value and value not in allowed_values:
            errors.append(ValidationError(
                field_name,
                f"值必须是以下之一: {', '.join(str(v) for v in allowed_values)}",
                "NOT_IN_ALLOWED"
            ))
        return errors

    @staticmethod
    def is_dict(value: Any, field_name: str) -> List[ValidationError]:
        """验证是否为字典

        Args:
            value: 待验证的值
            field_name: 字段名

        Returns:
            验证错误列表
        """
        errors = []
        if not isinstance(value, dict):
            errors.append(ValidationError(field_name, "必须是字典类型", "TYPE_ERROR"))
        return errors

    @staticmethod
    def is_list(value: Any, field_name: str) -> List[ValidationError]:
        """验证是否为列表

        Args:
            value: 待验证的值
            field_name: 字段名

        Returns:
            验证错误列表
        """
        errors = []
        if not isinstance(value, list):
            errors.append(ValidationError(field_name, "必须是列表类型", "TYPE_ERROR"))
        return errors

    @staticmethod
    def custom(value: Any, validator_func: Callable[[Any], bool], field_name: str, error_message: str) -> List[ValidationError]:
        """自定义验证函数

        Args:
            value: 待验证的值
            validator_func: 验证函数
            field_name: 字段名
            error_message: 错误消息

        Returns:
            验证错误列表
        """
        errors = []
        if not validator_func(value):
            errors.append(ValidationError(field_name, error_message, "CUSTOM"))
        return errors


def require_payload(payload: Dict[str, Any]) -> List[str]:
    """验证输入负载的基本要求

    Args:
        payload: 输入的负载数据

    Returns:
        错误信息列表
    """
    errors = []
    if not isinstance(payload, dict):
        return ["payload 必须是 dict 类型"]

    validator = Validator()

    error_list = validator.is_dict(payload, "payload")
    for err in error_list:
        errors.append(str(err))

    error_list = validator.required(payload.get("child_profile"), "child_profile")
    for err in error_list:
        errors.append(str(err))

    error_list = validator.is_dict(payload.get("child_profile"), "child_profile")
    for err in error_list:
        errors.append(str(err))

    current_problem = payload.get("current_problem", "")
    error_list = validator.required(current_problem, "current_problem")
    for err in error_list:
        errors.append(str(err))

    error_list = validator.min_length(str(current_problem), 2, "current_problem")
    for err in error_list:
        errors.append(str(err))

    return errors


def validate_child_profile(profile: Dict[str, Any]) -> List[str]:
    """验证孩子画像

    Args:
        profile: 孩子画像数据

    Returns:
        错误信息列表
    """
    errors = []
    validator = Validator()

    if not isinstance(profile, dict):
        return ["child_profile 必须是字典类型"]

    age = profile.get("age", "")
    if age:
        error_list = validator.pattern(str(age), r"^\d{1,2}岁?$", "age", "年龄格式应为数字+岁，如'8岁'或'8'")
        for err in error_list:
            errors.append(str(err))

    grade = profile.get("grade", "")
    if grade:
        error_list = validator.pattern(str(grade), r"^\d{1,2}年级$", "grade", "年级格式应为数字+年级，如'3年级'")
        for err in error_list:
            errors.append(str(err))

    return errors


def validate_learning_record(record: Dict[str, Any]) -> List[str]:
    """验证学习记录

    Args:
        record: 学习记录数据

    Returns:
        错误信息列表
    """
    errors = []
    validator = Validator()

    if not isinstance(record, dict):
        return ["学习记录必须是字典类型"]

    error_list = validator.required(record.get("record_id"), "record_id")
    for err in error_list:
        errors.append(str(err))

    timestamp = record.get("timestamp", "")
    if timestamp:
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            errors.append("timestamp 格式不正确，应为 ISO 格式")

    word_count = record.get("word_count", 0)
    error_list = validator.range(word_count, 0, 100000, "word_count")
    for err in error_list:
        errors.append(str(err))

    quality_score = record.get("quality_score", 0.0)
    error_list = validator.range(quality_score, 0, 10, "quality_score")
    for err in error_list:
        errors.append(str(err))

    structure_score = record.get("structure_score", 0.0)
    error_list = validator.range(structure_score, 0, 10, "structure_score")
    for err in error_list:
        errors.append(str(err))

    writing_type = record.get("writing_type", "")
    if writing_type:
        allowed_types = ["记叙文", "说明文", "议论文", "应用文", "诗歌", "其他"]
        error_list = validator.is_in(writing_type, allowed_types, "writing_type")
        for err in error_list:
            errors.append(str(err))

    return errors


def validate_progress_data(progress: Dict[str, Any]) -> List[str]:
    """验证进度数据

    Args:
        progress: 进度数据

    Returns:
        错误信息列表
    """
    errors = []
    validator = Validator()

    if not isinstance(progress, dict):
        return ["进度数据必须是字典类型"]

    total_sessions = progress.get("total_sessions", 0)
    error_list = validator.range(total_sessions, 0, 10000, "total_sessions")
    for err in error_list:
        errors.append(str(err))

    total_words = progress.get("total_words", 0)
    error_list = validator.range(total_words, 0, 10000000, "total_words")
    for err in error_list:
        errors.append(str(err))

    avg_quality = progress.get("average_quality_score", 0.0)
    error_list = validator.range(avg_quality, 0, 10, "average_quality_score")
    for err in error_list:
        errors.append(str(err))

    trend = progress.get("recent_trend", "")
    if trend:
        allowed_trends = ["improving", "declining", "stable", "insufficient_data"]
        error_list = validator.is_in(trend, allowed_trends, "recent_trend")
        for err in error_list:
            errors.append(str(err))

    return errors


def safe_list(value: Any) -> List[Any]:
    """安全地转换为列表

    Args:
        value: 待转换的值

    Returns:
        列表
    """
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def safe_dict(value: Any) -> Dict[str, Any]:
    """安全地转换为字典

    Args:
        value: 待转换的值

    Returns:
        字典
    """
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    return {}


def anonymize_if_needed(text: str, privacy_mode: str) -> str:
    """根据隐私模式进行匿名化处理

    Args:
        text: 待处理的文本
        privacy_mode: 隐私模式

    Returns:
        处理后的文本
    """
    if privacy_mode in {"anonymous", "family_local_first"}:
        replacements = [
            ("孩子姓名", "孩子"),
            ("学校名称", "学校"),
            ("家庭地址", "地址"),
            ("真实姓名", "姓名"),
            ("电话", "联系方式")
        ]
        for old, new in replacements:
            text = text.replace(old, new)
    return text


def validate_score(value: Any, field_name: str) -> List[str]:
    """验证评分字段

    Args:
        value: 待验证的值
        field_name: 字段名

    Returns:
        错误信息列表
    """
    errors = []
    validator = Validator()

    if value is not None:
        error_list = validator.range(float(value), 0, 10, field_name)
        for err in error_list:
            errors.append(str(err))

    return errors


def validate_duration(value: Any, field_name: str, max_duration: int = 180) -> List[str]:
    """验证时长字段

    Args:
        value: 待验证的值
        field_name: 字段名
        max_duration: 最大时长（分钟）

    Returns:
        错误信息列表
    """
    errors = []
    validator = Validator()

    if value is not None:
        error_list = validator.range(int(value), 0, max_duration, field_name)
        for err in error_list:
            errors.append(str(err))

    return errors


def sanitize_input(text: str) -> str:
    """清理输入文本

    Args:
        text: 待清理的文本

    Returns:
        清理后的文本
    """
    if not text:
        return ""

    text = text.strip()

    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<[^>]+>', '', text)

    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', text)

    return text


def batch_validate(records: List[Dict[str, Any]], validator_func: callable) -> Dict[int, List[str]]:
    """批量验证记录

    Args:
        records: 记录列表
        validator_func: 验证函数

    Returns:
        错误字典，键为记录索引，值为错误信息列表
    """
    results = {}
    for i, record in enumerate(records):
        errors = validator_func(record)
        if errors:
            results[i] = errors
    return results
