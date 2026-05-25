"""中考目标拆解 Agent - 数据验证器"""
from __future__ import annotations
from typing import Any, Dict, List


class ValidationError(Exception):
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(f"验证错误: {', '.join(errors)}")


def require_payload(payload: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if not isinstance(payload, dict):
        return ["payload 必须是 dict"]
    if not payload.get("child_profile"):
        errors.append("缺少 child_profile")
    if not str(payload.get("current_problem", "")).strip():
        errors.append("缺少 current_problem")
    return errors


def validate_score(value: Any) -> List[str]:
    errors = []
    if value is None:
        return errors
    try:
        score = float(value)
        if score < 0 or score > 150:
            errors.append("成绩必须在0-150之间")
    except (ValueError, TypeError):
        errors.append("成绩必须是数字")
    return errors


def validate_payload_with_details(payload: Dict[str, Any]) -> Dict[str, Any]:
    result = {
        "is_valid": True,
        "errors": [],
        "warnings": [],
        "field_errors": {}
    }

    errors = require_payload(payload)
    if errors:
        result["is_valid"] = False
        result["errors"].extend(errors)
        return result

    return result


def validate_payload(payload: Dict[str, Any]) -> bool:
    errors = require_payload(payload)
    if errors:
        raise ValidationError(errors)
    return True
