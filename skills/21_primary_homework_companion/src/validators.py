"""Validation helpers for 小学作业陪伴 Agent.

提供完善的字段级别验证、数据范围检查、格式验证和自定义错误消息。
"""
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import re


class ValidationError(Exception):
    """验证错误异常"""

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


class ValidationResult:
    """验证结果容器"""

    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[str] = []

    def add_error(self, field: str, message: str) -> None:
        """添加错误"""
        self.errors.append(ValidationError(field, message))

    def add_warning(self, message: str) -> None:
        """添加警告"""
        self.warnings.append(message)

    def is_valid(self) -> bool:
        """是否验证通过"""
        return len(self.errors) == 0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "is_valid": self.is_valid(),
            "errors": [{"field": e.field, "message": e.message} for e in self.errors],
            "warnings": self.warnings
        }

    def __repr__(self) -> str:
        if self.is_valid():
            return "ValidationResult(valid=True)"
        return f"ValidationResult(valid=False, errors={len(self.errors)}, warnings={len(self.warnings)})"


def require_payload(payload: Dict[str, Any]) -> List[str]:
    """验证payload基本结构

    Args:
        payload: 待验证的payload字典

    Returns:
        错误消息列表，如果为空则表示验证通过
    """
    errors: List[str] = []
    if not isinstance(payload, dict):
        return ["payload 必须是 dict"]
    if not payload.get("child_profile"):
        errors.append("缺少 child_profile")
    if not str(payload.get("current_problem", "")).strip():
        errors.append("缺少 current_problem")
    return errors


def validate_field_not_empty(value: Any, field_name: str, custom_message: Optional[str] = None) -> Optional[str]:
    """验证字段非空

    Args:
        value: 字段值
        field_name: 字段名称
        custom_message: 自定义错误消息

    Returns:
        错误消息，如果验证通过则返回None
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        return custom_message or f"{field_name} 不能为空"
    return None


def validate_field_type(value: Any, expected_type: type, field_name: str) -> Optional[str]:
    """验证字段类型

    Args:
        value: 字段值
        expected_type: 期望的类型
        field_name: 字段名称

    Returns:
        错误消息，如果验证通过则返回None
    """
    if not isinstance(value, expected_type):
        return f"{field_name} 类型错误，期望 {expected_type.__name__}，实际 {type(value).__name__}"
    return None


def validate_field_range(
    value: float,
    field_name: str,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    custom_message: Optional[str] = None
) -> Optional[str]:
    """验证数值字段范围

    Args:
        value: 字段值
        field_name: 字段名称
        min_value: 最小值
        max_value: 最大值
        custom_message: 自定义错误消息

    Returns:
        错误消息，如果验证通过则返回None
    """
    if min_value is not None and value < min_value:
        return custom_message or f"{field_name} 小于最小值 {min_value}"
    if max_value is not None and value > max_value:
        return custom_message or f"{field_name} 大于最大值 {max_value}"
    return None


def validate_field_length(
    value: str,
    field_name: str,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    custom_message: Optional[str] = None
) -> Optional[str]:
    """验证字符串字段长度

    Args:
        value: 字段值
        field_name: 字段名称
        min_length: 最小长度
        max_length: 最大长度
        custom_message: 自定义错误消息

    Returns:
        错误消息，如果验证通过则返回None
    """
    length = len(value)
    if min_length is not None and length < min_length:
        return custom_message or f"{field_name} 长度小于最小值 {min_length}"
    if max_length is not None and length > max_length:
        return custom_message or f"{field_name} 长度大于最大值 {max_length}"
    return None


def validate_field_format(
    value: str,
    field_name: str,
    pattern: str,
    custom_message: Optional[str] = None
) -> Optional[str]:
    """验证字符串字段格式

    Args:
        value: 字段值
        field_name: 字段名称
        pattern: 正则表达式模式
        custom_message: 自定义错误消息

    Returns:
        错误消息，如果验证通过则返回None
    """
    if not re.match(pattern, value):
        return custom_message or f"{field_name} 格式不正确"
    return None


def validate_field_in_choices(
    value: Any,
    field_name: str,
    choices: List[Any],
    custom_message: Optional[str] = None
) -> Optional[str]:
    """验证字段值在允许的选择列表中

    Args:
        value: 字段值
        field_name: 字段名称
        choices: 允许的值列表
        custom_message: 自定义错误消息

    Returns:
        错误消息，如果验证通过则返回None
    """
    if value not in choices:
        return custom_message or f"{field_name} 的值不在允许的范围内: {choices}"
    return None


def validate_datetime_format(value: str, field_name: str, format_str: str = "%Y-%m-%d") -> Optional[str]:
    """验证日期时间格式

    Args:
        value: 日期时间字符串
        field_name: 字段名称
        format_str: 日期时间格式

    Returns:
        错误消息，如果验证通过则返回None
    """
    try:
        datetime.strptime(value, format_str)
        return None
    except ValueError:
        return f"{field_name} 日期格式不正确，应为 {format_str}"


def safe_list(value: Any) -> List[Any]:
    """安全转换为列表

    Args:
        value: 任意值

    Returns:
        列表，如果输入为None则返回空列表
    """
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def anonymize_if_needed(text: str, privacy_mode: str) -> str:
    """根据隐私模式匿名化文本

    Args:
        text: 原始文本
        privacy_mode: 隐私模式

    Returns:
        匿名化后的文本
    """
    if privacy_mode in {"anonymous", "family_local_first"}:
        return text.replace("孩子姓名", "孩子").replace("学校名称", "学校")
    return text


def validate_child_profile(profile: Dict[str, Any]) -> ValidationResult:
    """验证孩子画像

    Args:
        profile: 孩子画像字典

    Returns:
        验证结果
    """
    result = ValidationResult()

    if not isinstance(profile, dict):
        result.add_error("child_profile", "孩子画像必须是字典类型")
        return result

    required_fields = ["name", "age", "grade"]
    for field in required_fields:
        if field not in profile:
            result.add_warning(f"孩子画像缺少推荐字段: {field}")

    if "age" in profile:
        age = profile["age"]
        error = validate_field_type(age, int, "age")
        if error:
            result.add_error("child_profile.age", error)
        else:
            error = validate_field_range(age, "age", min_value=5, max_value=15)
            if error:
                result.add_error("child_profile.age", error)

    if "grade" in profile:
        grade = profile["grade"]
        error = validate_field_type(grade, int, "grade")
        if error:
            result.add_error("child_profile.grade", error)
        else:
            error = validate_field_range(grade, "grade", min_value=1, max_value=6)
            if error:
                result.add_error("child_profile.grade", error)

    if "name" in profile:
        name = profile["name"]
        if isinstance(name, str):
            error = validate_field_length(name, "name", min_length=1, max_length=20)
            if error:
                result.add_error("child_profile.name", error)

    return result


def validate_homework_record(record: Dict[str, Any]) -> ValidationResult:
    """验证作业记录

    Args:
        record: 作业记录字典

    Returns:
        验证结果
    """
    result = ValidationResult()

    required_fields = ["subject", "content"]
    for field in required_fields:
        if field not in record:
            result.add_error(f"homework_record.{field}", f"缺少必需字段: {field}")
        elif not record[field]:
            result.add_error(f"homework_record.{field}", f"字段 {field} 不能为空")

    if "duration_minutes" in record:
        duration = record["duration_minutes"]
        error = validate_field_type(duration, (int, float), "duration_minutes")
        if error:
            result.add_error("homework_record.duration_minutes", error)
        else:
            error = validate_field_range(duration, "duration_minutes", min_value=0)
            if error:
                result.add_error("homework_record.duration_minutes", error)

    if "completion_rate" in record:
        rate = record["completion_rate"]
        error = validate_field_type(rate, (int, float), "completion_rate")
        if error:
            result.add_error("homework_record.completion_rate", error)
        else:
            error = validate_field_range(rate, "completion_rate", min_value=0.0, max_value=100.0)
            if error:
                result.add_error("homework_record.completion_rate", error)

    if "difficulty" in record:
        error = validate_field_in_choices(
            record["difficulty"],
            "difficulty",
            ["简单", "中等", "困难", "easy", "medium", "hard"]
        )
        if error:
            result.add_warning("difficulty 字段使用了非标准值")

    if "status" in record:
        error = validate_field_in_choices(
            record["status"],
            "status",
            ["未开始", "进行中", "已完成", "需要帮助", "not_started", "in_progress", "completed", "needs_help"]
        )
        if error:
            result.add_warning("status 字段使用了非标准值")

    return result


def validate_session_context(context: Dict[str, Any]) -> ValidationResult:
    """验证会话上下文

    Args:
        context: 会话上下文字典

    Returns:
        验证结果
    """
    result = ValidationResult()

    if "session_id" not in context:
        result.add_error("session_id", "缺少会话ID")
    else:
        session_id = context["session_id"]
        error = validate_field_not_empty(session_id, "session_id")
        if error:
            result.add_error("session_id", error)

    if "start_time" not in context:
        result.add_warning("缺少 start_time，将使用当前时间")
    elif not isinstance(context["start_time"], str):
        result.add_error("start_time", "start_time 必须是字符串类型")
    else:
        error = validate_datetime_format(context["start_time"], "start_time")
        if error:
            result.add_error("start_time", error)

    if "grade_level" in context:
        grade = context["grade_level"]
        error = validate_field_type(grade, int, "grade_level")
        if error:
            result.add_error("grade_level", error)
        else:
            error = validate_field_range(grade, "grade_level", min_value=1, max_value=6)
            if error:
                result.add_error("grade_level", error)

    return result


def validate_recommendation(recommendation: Dict[str, Any]) -> ValidationResult:
    """验证推荐对象

    Args:
        recommendation: 推荐字典

    Returns:
        验证结果
    """
    result = ValidationResult()

    required_fields = ["recommendation_id", "category", "priority", "title", "description"]
    for field in required_fields:
        if field not in recommendation:
            result.add_error(f"recommendation.{field}", f"缺少必需字段: {field}")

    if "confidence_score" in recommendation:
        score = recommendation["confidence_score"]
        error = validate_field_type(score, (int, float), "confidence_score")
        if error:
            result.add_error("recommendation.confidence_score", error)
        else:
            error = validate_field_range(score, "confidence_score", min_value=0.0, max_value=1.0)
            if error:
                result.add_error("recommendation.confidence_score", error)

    if "priority" in recommendation:
        error = validate_field_in_choices(
            recommendation["priority"],
            "priority",
            ["高", "中", "低", "紧急", "high", "medium", "low", "urgent"]
        )
        if error:
            result.add_warning("priority 字段使用了非标准值")

    return result


def compose_validators(*validators: Callable[[Any], Optional[str]]) -> Callable[[Any], List[str]]:
    """组合多个验证器

    Args:
        validators: 多个验证器函数

    Returns:
        组合后的验证器函数
    """
    def validate(value: Any) -> List[str]:
        errors = []
        for validator in validators:
            error = validator(value)
            if error:
                errors.append(error)
        return errors

    return validate


def batch_validate(records: List[Dict[str, Any]], validator_func: Callable[[Dict[str, Any]], ValidationResult]) -> Dict[int, ValidationResult]:
    """批量验证记录

    Args:
        records: 记录列表
        validator_func: 验证函数

    Returns:
        验证结果字典，键为记录索引
    """
    results = {}
    for i, record in enumerate(records):
        results[i] = validator_func(record)
    return results


def get_validation_summary(results: Dict[int, ValidationResult]) -> Dict[str, Any]:
    """获取验证摘要

    Args:
        results: 验证结果字典

    Returns:
        摘要统计
    """
    total = len(results)
    valid_count = sum(1 for r in results.values() if r.is_valid())
    total_errors = sum(len(r.errors) for r in results.values())
    total_warnings = sum(len(r.warnings) for r in results.values())

    return {
        "total": total,
        "valid": valid_count,
        "invalid": total - valid_count,
        "total_errors": total_errors,
        "total_warnings": total_warnings,
        "pass_rate": (valid_count / total * 100) if total > 0 else 0
    }
