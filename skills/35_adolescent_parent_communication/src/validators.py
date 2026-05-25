"""青春期亲子沟通 Agent - 数据验证器"""
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


def validate_child_profile(profile: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if not isinstance(profile, dict):
        return ["child_profile 必须是字典类型"]
    if "age" in profile:
        try:
            age = int(profile["age"])
            if age < 10 or age > 19:
                errors.append("年龄建议在10-19岁之间（青春期）")
        except (ValueError, TypeError):
            errors.append("年龄必须是整数")
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

    if "child_profile" in payload:
        profile_errors = validate_child_profile(payload["child_profile"])
        if profile_errors:
            result["warnings"].extend(profile_errors)

    return result


def validate_payload(payload: Dict[str, Any]) -> bool:
    errors = require_payload(payload)
    if errors:
        raise ValidationError(errors)
    return True
