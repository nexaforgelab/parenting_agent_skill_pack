"""Validation helpers for 小学数学应用题 Agent."""
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
        self.errors.append(ValidationError(field, message))

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid(),
            "errors": [{"field": e.field, "message": e.message} for e in self.errors],
            "warnings": self.warnings
        }


def require_payload(payload: Dict[str, Any]) -> List[str]:
    """验证payload基本结构"""
    errors: List[str] = []
    if not isinstance(payload, dict):
        return ["payload 必须是 dict"]
    if not payload.get("child_profile"):
        errors.append("缺少 child_profile")
    if not str(payload.get("current_problem", "")).strip():
        errors.append("缺少 current_problem")
    return errors


def validate_field_not_empty(value: Any, field_name: str) -> Optional[str]:
    """验证字段非空"""
    if value is None or (isinstance(value, str) and not value.strip()):
        return f"{field_name} 不能为空"
    return None


def validate_field_type(value: Any, expected_type: type, field_name: str) -> Optional[str]:
    """验证字段类型"""
    if not isinstance(value, expected_type):
        return f"{field_name} 类型错误"
    return None


def validate_field_range(value: float, field_name: str, min_value: Optional[float] = None, max_value: Optional[float] = None) -> Optional[str]:
    """验证数值字段范围"""
    if min_value is not None and value < min_value:
        return f"{field_name} 小于最小值 {min_value}"
    if max_value is not None and value > max_value:
        return f"{field_name} 大于最大值 {max_value}"
    return None


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


def validate_problem_record(record: Dict[str, Any]) -> ValidationResult:
    """验证应用题记录"""
    result = ValidationResult()

    required_fields = ["problem_id", "content"]
    for field in required_fields:
        if field not in record:
            result.add_error(f"problem_record.{field}", f"缺少必需字段: {field}")

    if "time_spent" in record:
        time_spent = record["time_spent"]
        error = validate_field_type(time_spent, (int, float), "time_spent")
        if error:
            result.add_error("problem_record.time_spent", error)
        else:
            error = validate_field_range(time_spent, "time_spent", min_value=0)
            if error:
                result.add_error("problem_record.time_spent", error)

    if "hints_used" in record:
        hints = record["hints_used"]
        error = validate_field_type(hints, int, "hints_used")
        if error:
            result.add_error("problem_record.hints_used", error)
        else:
            error = validate_field_range(hints, "hints_used", min_value=0, max_value=10)
            if error:
                result.add_error("problem_record.hints_used", error)

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
