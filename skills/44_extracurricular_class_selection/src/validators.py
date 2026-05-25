"""Validation helpers for 兴趣班选择 Agent.

增强版本：添加字段级别验证、数据范围检查、格式验证、自定义错误消息
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
import re


def require_payload(payload: Dict[str, Any]) -> List[str]:
    """验证必填字段"""
    errors: List[str] = []
    if not isinstance(payload, dict):
        return ["payload 必须是 dict 类型"]

    if not payload.get("child_profile"):
        errors.append("缺少必填字段：child_profile")
    elif not isinstance(payload.get("child_profile"), dict):
        errors.append("child_profile 必须是字典类型")

    if not str(payload.get("current_problem", "")).strip():
        errors.append("缺少必填字段：current_problem")

    history_days = payload.get("history_days")
    if history_days is not None:
        if not isinstance(history_days, int):
            errors.append("history_days 必须是整数类型")
        elif history_days < 1 or history_days > 3650:
            errors.append("history_days 必须在 1-3650 天范围内")

    return errors


def validate_child_profile(profile: Optional[Dict[str, Any]]) -> List[str]:
    """验证孩子画像字段"""
    errors: List[str] = []

    if profile is None:
        return ["child_profile 不能为空"]

    if not isinstance(profile, dict):
        return ["child_profile 必须是字典类型"]

    age = profile.get("age")
    if age is not None:
        # 处理字符串格式年龄
        if isinstance(age, str):
            match = re.match(r'^(\d+\.?\d*)', age)
            if match:
                age = float(match.group(1))
            else:
                errors.append("孩子年龄格式不正确，应为数字或 'X岁' 格式")
                age = None
        
        if age is not None:
            if not isinstance(age, (int, float)):
                errors.append("孩子年龄必须是数字类型")
            elif age < 0 or age > 18:
                errors.append("孩子年龄必须在 0-18 岁范围内")

    name = profile.get("name")
    if name is not None and not isinstance(name, str):
        errors.append("孩子姓名必须是字符串类型")

    return errors


def validate_class_info(class_info: Dict[str, Any]) -> List[str]:
    """验证兴趣班信息"""
    errors: List[str] = []

    if not isinstance(class_info, dict):
        return ["兴趣班信息必须是字典类型"]

    name = class_info.get("name")
    if not name or not str(name).strip():
        errors.append("兴趣班名称不能为空")

    tuition = class_info.get("tuition_per_month")
    if tuition is not None:
        try:
            tuition_val = float(tuition) if tuition != "" else 0
            if tuition_val < 0:
                errors.append("学费不能为负数")
        except (ValueError, TypeError):
            errors.append("学费必须是数字类型")

    hours_per_week = class_info.get("hours_per_week")
    if hours_per_week is not None:
        try:
            hours_val = float(hours_per_week) if hours_per_week != "" else 0
            if hours_val < 0:
                errors.append("每周课时不能为负数")
        except (ValueError, TypeError):
            errors.append("每周课时必须是数字类型")

    return errors


def validate_numeric_range(
    value: Any,
    field_name: str,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    allow_none: bool = True
) -> List[str]:
    """验证数值范围"""
    errors: List[str] = []

    if value is None:
        if not allow_none:
            errors.append(f"{field_name}不能为空")
        return errors

    if not isinstance(value, (int, float)):
        errors.append(f"{field_name}必须是数值类型")
        return errors

    if min_value is not None and value < min_value:
        errors.append(f"{field_name}不能小于{min_value}")

    if max_value is not None and value > max_value:
        errors.append(f"{field_name}不能大于{max_value}")

    return errors


def safe_list(value: Any) -> List[Any]:
    """安全转换为列表"""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def safe_dict(value: Any) -> Dict[str, Any]:
    """安全转换为字典"""
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    return {}


def safe_string(value: Any, default: str = "") -> str:
    """安全转换为字符串"""
    if value is None:
        return default
    return str(value)


def anonymize_if_needed(text: str, privacy_mode: str) -> str:
    """根据隐私模式进行脱敏处理"""
    if privacy_mode in {"anonymous", "family_local_first"}:
        text = text.replace("孩子姓名", "孩子")
        text = text.replace("机构名称", "机构")
        text = text.replace("真实姓名", "***")
        text = re.sub(r'\d{3}[-]?\d{4}[-]?\d{4}', '***-****-****', text)

    return text


def validate_batch_classes(classes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """批量验证兴趣班信息"""
    result = {
        "valid_classes": [],
        "invalid_classes": [],
        "errors_by_class": {},
        "total_count": len(classes),
        "valid_count": 0,
        "invalid_count": 0
    }

    for i, cls in enumerate(classes):
        cls_id = cls.get("class_id") or cls.get("name") or f"class_{i}"
        errors = validate_class_info(cls)

        if errors:
            result["invalid_classes"].append(cls)
            result["errors_by_class"][cls_id] = errors
            result["invalid_count"] += 1
        else:
            result["valid_classes"].append(cls)
            result["valid_count"] += 1

    return result


def format_validation_errors(errors: List[str], prefix: str = "错误") -> str:
    """格式化验证错误信息"""
    if not errors:
        return ""

    if len(errors) == 1:
        return f"{prefix}：{errors[0]}"

    error_lines = [f"{prefix}：" + errors[0]]
    for error in errors[1:]:
        error_lines.append(f"  - {error}")

    return "\n".join(error_lines)
