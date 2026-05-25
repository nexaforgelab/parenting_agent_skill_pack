"""Validation helpers for 幼儿英语启蒙 Agent."""
from typing import Any, Dict, List, Optional


class ValidationError(Exception):
    def __init__(self, field: str, message: str, error_code: str = "VALIDATION_ERROR"):
        self.field = field
        self.message = message
        self.error_code = error_code
        super().__init__(f"[{error_code}] {field}: {message}")


class FieldValidator:
    @staticmethod
    def required(value: Any, field_name: str) -> Optional[str]:
        if value is None or (isinstance(value, str) and not value.strip()):
            return f"{field_name} 为必填字段，不能为空"
        return None

    @staticmethod
    def range_int(value: int, min_val: int, max_val: int, field_name: str) -> Optional[str]:
        if value is not None and (value < min_val or value > max_val):
            return f"{field_name} 必须在 {min_val}-{max_val} 之间"
        return None

    @staticmethod
    def range_float(value: float, min_val: float, max_val: float, field_name: str) -> Optional[str]:
        if value is not None and (value < min_val or value > max_val):
            return f"{field_name} 必须在 {min_val}-{max_val} 之间"
        return None


def require_payload(payload: Dict[str, Any]) -> List[str]:
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


def validate_vocab_record(record: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    if not isinstance(record, dict):
        return ["record 必须是字典类型"]

    error = FieldValidator.required(record.get("word"), "word")
    if error:
        errors.append(error)

    score = record.get("mastery_score", 0.0)
    error = FieldValidator.range_float(score, 0.0, 10.0, "mastery_score")
    if error:
        errors.append(error)

    return errors


def safe_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def anonymize_if_needed(text: str, privacy_mode: str) -> str:
    if privacy_mode in {"anonymous", "family_local_first"}:
        return text.replace("孩子姓名", "孩子").replace("学校名称", "学校")
    return text