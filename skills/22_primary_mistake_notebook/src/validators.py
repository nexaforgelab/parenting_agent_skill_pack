"""Validation helpers for 小学错题本 Agent.

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
    """验证字段非空"""
    if value is None or (isinstance(value, str) and not value.strip()):
        return custom_message or f"{field_name} 不能为空"
    return None


def validate_field_type(value: Any, expected_type: type, field_name: str) -> Optional[str]:
    """验证字段类型"""
    if not isinstance(value, expected_type):
        return f"{field_name} 类型错误，期望 {expected_type.__name__}，实际 {type(value).__name__}"
    return None


def validate_field_range(value: float, field_name: str, min_value: Optional[float] = None, max_value: Optional[float] = None) -> Optional[str]:
    """验证数值字段范围"""
    if min_value is not None and value < min_value:
        return f"{field_name} 小于最小值 {min_value}"
    if max_value is not None and value > max_value:
        return f"{field_name} 大于最大值 {max_value}"
    return None


def validate_field_length(value: str, field_name: str, min_length: Optional[int] = None, max_length: Optional[int] = None) -> Optional[str]:
    """验证字符串字段长度"""
    length = len(value)
    if min_length is not None and length < min_length:
        return f"{field_name} 长度小于最小值 {min_length}"
    if max_length is not None and length > max_length:
        return f"{field_name} 长度大于最大值 {max_length}"
    return None


def validate_field_format(value: str, field_name: str, pattern: str) -> Optional[str]:
    """验证字符串字段格式"""
    if not re.match(pattern, value):
        return f"{field_name} 格式不正确"
    return None


def validate_field_in_choices(value: Any, field_name: str, choices: List[Any]) -> Optional[str]:
    """验证字段值在允许的选择列表中"""
    if value not in choices:
        return f"{field_name} 的值不在允许的范围内: {choices}"
    return None


def validate_datetime_format(value: str, field_name: str, format_str: str = "%Y-%m-%d") -> Optional[str]:
    """验证日期时间格式"""
    try:
        datetime.strptime(value, format_str)
        return None
    except ValueError:
        return f"{field_name} 日期格式不正确，应为 {format_str}"


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


def validate_mistake_record(record: Dict[str, Any]) -> ValidationResult:
    """验证错题记录"""
    result = ValidationResult()

    required_fields = ["mistake_id", "subject", "topic", "description", "wrong_answer", "correct_answer", "error_type"]
    for field in required_fields:
        if field not in record:
            result.add_error(f"mistake_record.{field}", f"缺少必需字段: {field}")
        elif not record[field]:
            result.add_error(f"mistake_record.{field}", f"字段 {field} 不能为空")

    if "mastery_level" in record:
        mastery = record["mastery_level"]
        error = validate_field_type(mastery, (int, float), "mastery_level")
        if error:
            result.add_error("mistake_record.mastery_level", error)
        else:
            error = validate_field_range(mastery, "mastery_level", min_value=0.0, max_value=1.0)
            if error:
                result.add_error("mistake_record.mastery_level", error)

    if "review_count" in record:
        count = record["review_count"]
        error = validate_field_type(count, int, "review_count")
        if error:
            result.add_error("mistake_record.review_count", error)
        else:
            error = validate_field_range(count, "review_count", min_value=0)
            if error:
                result.add_error("mistake_record.review_count", error)

    if "error_type" in record:
        valid_types = ["计算错误", "理解错误", "粗心大意", "知识盲点", "其他"]
        if record["error_type"] not in valid_types:
            result.add_warning(f"error_type 使用了非标准值: {record['error_type']}")

    return result


def validate_knowledge_point(kp: Dict[str, Any]) -> ValidationResult:
    """验证知识点掌握度"""
    result = ValidationResult()

    required_fields = ["point_id", "point_name", "subject"]
    for field in required_fields:
        if field not in kp:
            result.add_error(f"knowledge_point.{field}", f"缺少必需字段: {field}")

    if "mastery_level" in kp:
        mastery = kp["mastery_level"]
        error = validate_field_type(mastery, (int, float), "mastery_level")
        if error:
            result.add_error("knowledge_point.mastery_level", error)
        else:
            error = validate_field_range(mastery, "mastery_level", min_value=0.0, max_value=1.0)
            if error:
                result.add_error("knowledge_point.mastery_level", error)

    return result


def validate_review_plan(plan: Dict[str, Any]) -> ValidationResult:
    """验证复习计划"""
    result = ValidationResult()

    required_fields = ["plan_id", "start_date", "end_date"]
    for field in required_fields:
        if field not in plan:
            result.add_error(f"review_plan.{field}", f"缺少必需字段: {field}")

    if "start_date" in plan and "end_date" in plan:
        try:
            start = datetime.fromisoformat(plan["start_date"])
            end = datetime.fromisoformat(plan["end_date"])
            if end <= start:
                result.add_error("review_plan", "结束日期必须晚于开始日期")
        except ValueError:
            result.add_error("review_plan", "日期格式不正确")

    if "daily_review_count" in plan:
        count = plan["daily_review_count"]
        error = validate_field_range(count, "daily_review_count", min_value=1, max_value=50)
        if error:
            result.add_error("review_plan.daily_review_count", error)

    return result


def batch_validate(records: List[Dict[str, Any]], validator_func: Callable[[Dict[str, Any]], ValidationResult]) -> Dict[int, ValidationResult]:
    """批量验证记录"""
    results = {}
    for i, record in enumerate(records):
        results[i] = validator_func(record)
    return results


def get_validation_summary(results: Dict[int, ValidationResult]) -> Dict[str, Any]:
    """获取验证摘要"""
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
