"""Validation helpers for 儿童安全教育 Agent.

增强版本：添加字段级别验证、数据范围检查、格式验证、自定义错误消息
"""
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
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

    if "name" in profile:
        name_errors = validate_name(profile["name"])
        errors.extend([f"孩子姓名: {e}" for e in name_errors])

    if "birth_date" in profile:
        date_errors = validate_date(profile["birth_date"], "出生日期")
        errors.extend([f"出生日期: {e}" for e in date_errors])

    if "age_months" in profile:
        age_errors = validate_age_months(profile["age_months"])
        errors.extend([f"月龄: {e}" for e in age_errors])

    return errors


def validate_safety_training_record(record: Dict[str, Any]) -> List[str]:
    """验证安全培训记录

    Args:
        record: 记录字典

    Returns:
        错误列表，如果为空则验证通过
    """
    errors: List[str] = []

    if not isinstance(record, dict):
        return ["记录必须是字典类型"]

    timestamp_errors = validate_timestamp(record.get("timestamp"), "培训时间")
    errors.extend([f"培训时间: {e}" for e in timestamp_errors])

    if "correct_responses" in record and record["correct_responses"] is not None:
        if record["correct_responses"] < 0:
            errors.append("correct_responses 不能为负数")

    if "total_questions" in record and record["total_questions"] is not None:
        if record["total_questions"] < 0:
            errors.append("total_questions 不能为负数")

    if "role_play_score" in record and record["role_play_score"] is not None:
        score_errors = validate_role_play_score(record["role_play_score"])
        errors.extend([f"角色扮演评分: {e}" for e in score_errors])

    return errors


def validate_timestamp(value: Any, field_name: str = "时间戳") -> List[str]:
    """验证时间戳格式

    Args:
        value: 待验证的值
        field_name: 字段名称

    Returns:
        错误列表，如果为空则验证通过
    """
    errors: List[str] = []

    if value is None or str(value).strip() == "":
        errors.append(f"{field_name}不能为空")
        return errors

    try:
        if isinstance(value, datetime):
            return errors
        elif isinstance(value, str):
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        else:
            errors.append(f"{field_name}必须是datetime对象或ISO格式字符串")
    except (ValueError, AttributeError) as e:
        errors.append(f"{field_name}格式错误: {str(e)}")

    return errors


def validate_date(value: Any, field_name: str = "日期") -> List[str]:
    """验证日期格式

    Args:
        value: 待验证的值
        field_name: 字段名称

    Returns:
        错误列表，如果为空则验证通过
    """
    errors: List[str] = []

    if value is None or str(value).strip() == "":
        errors.append(f"{field_name}不能为空")
        return errors

    try:
        if isinstance(value, date):
            return errors
        elif isinstance(value, str):
            date.fromisoformat(value)
        elif isinstance(value, datetime):
            return errors
        else:
            errors.append(f"{field_name}必须是date对象或ISO格式字符串")
    except (ValueError, AttributeError) as e:
        errors.append(f"{field_name}格式错误: {str(e)}")

    return errors


def validate_role_play_score(value: Any) -> List[str]:
    """验证角色扮演评分

    Args:
        value: 待验证的值

    Returns:
        错误列表，如果为空则验证通过
    """
    errors: List[str] = []

    if value is None:
        return errors

    try:
        score = float(value)
        if score < 0 or score > 10:
            errors.append("角色扮演评分必须在 0-10 范围内")
    except (ValueError, TypeError):
        errors.append("角色扮演评分必须是数字")

    return errors


def validate_name(value: Any) -> List[str]:
    """验证姓名格式

    Args:
        value: 待验证的值

    Returns:
        错误列表，如果为空则验证通过
    """
    errors: List[str] = []

    if value is None or str(value).strip() == "":
        return errors

    name = str(value).strip()
    if len(name) < 2:
        errors.append("姓名至少需要2个字符")
    elif len(name) > 50:
        errors.append("姓名不能超过50个字符")

    if not re.match(r'^[\u4e00-\u9fa5a-zA-Z\s·]+$', name):
        errors.append("姓名只能包含中文、英文字母和空格")

    return errors


def validate_age_months(value: Any) -> List[str]:
    """验证月龄

    Args:
        value: 待验证的值

    Returns:
        错误列表，如果为空则验证通过
    """
    errors: List[str] = []

    if value is None:
        return errors

    try:
        age = int(value)
        if age < 0:
            errors.append("月龄不能为负数")
        elif age > 180:
            errors.append("月龄不能超过180个月（15岁）")
    except (ValueError, TypeError):
        errors.append("月龄必须是整数")

    return errors


def validate_duration(value: Any, min_val: float = 0, max_val: float = 120) -> List[str]:
    """验证时长

    Args:
        value: 待验证的值
        min_val: 最小值（分钟）
        max_val: 最大值（分钟）

    Returns:
        错误列表，如果为空则验证通过
    """
    errors: List[str] = []

    if value is None:
        return errors

    try:
        duration = float(value)
        if duration < min_val:
            errors.append(f"时长不能小于{min_val}分钟")
        elif duration > max_val:
            errors.append(f"时长不能大于{max_val}分钟")
    except (ValueError, TypeError):
        errors.append("时长必须是数字")

    return errors


def validate_notes(value: Any, max_length: int = 500) -> List[str]:
    """验证备注字段

    Args:
        value: 待验证的值
        max_length: 最大长度

    Returns:
        错误列表，如果为空则验证通过
    """
    errors: List[str] = []

    if value is None or str(value).strip() == "":
        return errors

    notes = str(value)
    if len(notes) > max_length:
        errors.append(f"备注不能超过{max_length}个字符")

    return errors


def safe_list(value: Any) -> List[Any]:
    """安全地转换为列表

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


def anonymize_if_needed(text: str, privacy_mode: str) -> str:
    """根据隐私模式匿名化文本

    Args:
        text: 待处理的文本
        privacy_mode: 隐私模式

    Returns:
        处理后的文本
    """
    if privacy_mode in {"anonymous", "family_local_first"}:
        return text.replace("孩子姓名", "孩子").replace("学校名称", "学校")
    return text


def validate_payload_with_details(payload: Dict[str, Any]) -> Dict[str, Any]:
    """完整的payload验证（返回详细信息）

    Args:
        payload: 待验证的payload字典

    Returns:
        包含验证结果的字典
    """
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

    if "raw_records" in payload:
        records = safe_list(payload["raw_records"])
        for i, record in enumerate(records):
            record_errors = validate_safety_training_record(record)
            if record_errors:
                result["is_valid"] = False
                result["field_errors"][f"record_{i}"] = record_errors

    if "history_days" in payload:
        try:
            days = int(payload["history_days"])
            if days < 1 or days > 90:
                result["warnings"].append("history_days建议在1-90天范围内")
        except (ValueError, TypeError):
            result["errors"].append("history_days必须是整数")

    return result


def batch_validate_records(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """批量验证记录

    Args:
        records: 记录列表

    Returns:
        包含验证结果的字典
    """
    result = {
        "total_records": len(records),
        "valid_records": 0,
        "invalid_records": 0,
        "errors_by_record": []
    }

    for i, record in enumerate(records):
        errors = validate_safety_training_record(record)
        if errors:
            result["invalid_records"] += 1
            result["errors_by_record"].append({
                "index": i,
                "errors": errors,
                "record": record
            })
        else:
            result["valid_records"] += 1

    return result