"""亲子冲突复盘 Agent - 数据验证器

增强版本：添加字段级别验证、数据范围检查、格式验证、自定义错误消息
"""
from __future__ import annotations
from typing import Any, Dict, List, Union
import re


class ValidationError(Exception):
    """自定义验证错误异常"""

    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(f"验证错误: {', '.join(errors)}")


def require_payload(payload: Dict[str, Any]) -> List[str]:
    """验证payload基本结构

    Args:
        payload: 待验证的payload字典

    Returns:
        错误列表，如果为空则验证通过
    """
    errors: List[str] = []
    if not isinstance(payload, dict):
        return ["payload 必须是 dict"]
    if not payload.get("child_profile"):
        errors.append("缺少 child_profile")
    if not str(payload.get("current_problem", "")).strip():
        errors.append("缺少 current_problem")
    return errors


def validate_child_profile(profile: Dict[str, Any]) -> List[str]:
    """验证孩子画像字段

    Args:
        profile: 孩子画像字典

    Returns:
        错误列表，如果为空则验证通过
    """
    errors: List[str] = []

    if not isinstance(profile, dict):
        return ["child_profile 必须是字典类型"]

    if "age" in profile:
        age_errors = validate_age(profile["age"])
        errors.extend([f"年龄: {e}" for e in age_errors])

    if "emotional_sensitivity" in profile:
        sensitivity = profile["emotional_sensitivity"]
        valid_values = {"low", "medium", "high"}
        if sensitivity not in valid_values:
            errors.append(f"情绪敏感度必须是以下之一: {', '.join(valid_values)}")

    return errors


def validate_age(value: Any) -> List[str]:
    """验证年龄字段"""
    errors: List[str] = []
    if value is None:
        return errors
    try:
        age = int(value)
        if age < 3 or age > 18:
            errors.append("年龄必须在3-18岁之间")
    except (ValueError, TypeError):
        errors.append("年龄必须是整数")
    return errors


def validate_conflict_type(value: Any) -> List[str]:
    """验证冲突类型"""
    errors: List[str] = []
    valid_types = {
        "homework", "screen_time", "bedtime", "chores",
        "sibling", "school", "social", "emotional", "autonomy", "other"
    }
    if value is None or str(value).strip() == "":
        return errors
    normalized = str(value).lower().strip()
    if normalized not in valid_types:
        errors.append(f"冲突类型必须是以下之一: {', '.join(sorted(valid_types))}")
    return errors


def validate_severity(value: Any) -> List[str]:
    """验证严重程度"""
    errors: List[str] = []
    valid_values = {"minor", "moderate", "severe", "crisis"}
    if value is None or str(value).strip() == "":
        return errors
    normalized = str(value).lower().strip()
    if normalized not in valid_values:
        errors.append(f"严重程度必须是以下之一: {', '.join(sorted(valid_values))}")
    return errors


def validate_resolution_quality(value: Any) -> List[str]:
    """验证解决质量评分"""
    errors: List[str] = []
    if value is None:
        return errors
    try:
        score = int(value)
        if score < 0 or score > 10:
            errors.append("解决质量评分必须在0-10之间")
    except (ValueError, TypeError):
        errors.append("解决质量评分必须是整数")
    return errors


def validate_conflict_record(record: Dict[str, Any]) -> List[str]:
    """验证冲突记录"""
    errors: List[str] = []
    if not isinstance(record, dict):
        return ["记录必须是字典类型"]

    if "conflict_type" in record:
        errors.extend(validate_conflict_type(record["conflict_type"]))

    if "severity" in record:
        errors.extend(validate_severity(record["severity"]))

    if "resolution_quality" in record:
        errors.extend(validate_resolution_quality(record["resolution_quality"]))

    if "outcome" in record:
        outcome = record["outcome"]
        valid_outcomes = {"resolved", "unresolved", "partially_resolved", "escalated"}
        if outcome not in valid_outcomes:
            errors.append(f"结果必须是以下之一: {', '.join(sorted(valid_outcomes))}")

    return errors


def validate_payload_with_details(payload: Dict[str, Any]) -> Dict[str, Any]:
    """完整的payload验证（返回详细信息）"""
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
            result["is_valid"] = False
            result["field_errors"]["child_profile"] = profile_errors
            result["errors"].extend(profile_errors)

    if "conflict_records" in payload:
        records = payload["conflict_records"] if isinstance(payload["conflict_records"], list) else []
        for i, record in enumerate(records):
            record_errors = validate_conflict_record(record)
            if record_errors:
                result["field_errors"][f"record_{i}"] = record_errors

    return result


def validate_payload(payload: Dict[str, Any]) -> bool:
    """简化的payload验证"""
    errors = require_payload(payload)
    if errors:
        raise ValidationError(errors)
    return True
