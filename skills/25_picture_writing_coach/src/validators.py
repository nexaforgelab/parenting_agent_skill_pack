"""Validation helpers for 小学看图写话 Agent."""
from typing import Any, Dict, List, Optional, Callable


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


def validate_writing_record(record: Dict[str, Any]) -> ValidationResult:
    """验证写作记录"""
    result = ValidationResult()

    required_fields = ["record_id"]
    for field in required_fields:
        if field not in record:
            result.add_error(f"writing_record.{field}", f"缺少必需字段: {field}")

    if "word_count" in record:
        word_count = record["word_count"]
        if not isinstance(word_count, int) or word_count < 0:
            result.add_error("writing_record.word_count", "word_count 必须是正整数")

    if "overall_score" in record:
        score = record["overall_score"]
        if not isinstance(score, (int, float)) or score < 0 or score > 100:
            result.add_error("writing_record.overall_score", "overall_score 必须在 0-100 之间")

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
