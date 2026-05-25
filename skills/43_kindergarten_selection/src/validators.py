"""Validation helpers for 幼儿园择校 Agent.

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
            elif age < 0 or age > 6:
                errors.append("孩子年龄必须在 0-6 岁范围内（幼儿园阶段）")

    name = profile.get("name")
    if name is not None and not isinstance(name, str):
        errors.append("孩子姓名必须是字符串类型")

    return errors


def validate_kindergarten_info(kindergarten: Dict[str, Any]) -> List[str]:
    """验证幼儿园信息"""
    errors: List[str] = []

    if not isinstance(kindergarten, dict):
        return ["幼儿园信息必须是字典类型"]

    name = kindergarten.get("name")
    if not name or not str(name).strip():
        errors.append("幼儿园名称不能为空")

    tuition = kindergarten.get("tuition_per_year")
    if tuition is not None:
        try:
            tuition_val = float(tuition) if tuition != "" else 0
            if tuition_val < 0:
                errors.append("学费不能为负数")
        except (ValueError, TypeError):
            errors.append("学费必须是数字类型")

    ratio = kindergarten.get("teacher_student_ratio")
    if ratio is not None:
        try:
            ratio_val = float(ratio) if ratio != "" else 0
            if ratio_val < 0:
                errors.append("师生比不能为负数")
        except (ValueError, TypeError):
            errors.append("师生比必须是数字类型")

    rating = kindergarten.get("rating")
    if rating is not None:
        try:
            rating_val = float(rating) if rating != "" else 0
            if rating_val < 0 or rating_val > 5:
                errors.append("评分必须在 0-5 范围内")
        except (ValueError, TypeError):
            errors.append("评分必须是数字类型")

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


def validate_string_length(
    value: Any,
    field_name: str,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None
) -> List[str]:
    """验证字符串长度"""
    errors: List[str] = []

    if value is None:
        return errors

    if not isinstance(value, str):
        errors.append(f"{field_name}必须是字符串类型")
        return errors

    length = len(value)

    if min_length is not None and length < min_length:
        errors.append(f"{field_name}长度不能少于{min_length}个字符")

    if max_length is not None and length > max_length:
        errors.append(f"{field_name}长度不能超过{max_length}个字符")

    return errors


def validate_list_items(
    items: Any,
    field_name: str,
    item_type: type = str,
    max_items: Optional[int] = None
) -> List[str]:
    """验证列表项"""
    errors: List[str] = []

    if items is None:
        return errors

    if not isinstance(items, list):
        errors.append(f"{field_name}必须是列表类型")
        return errors

    if max_items is not None and len(items) > max_items:
        errors.append(f"{field_name}最多只能有{max_items}项")

    for i, item in enumerate(items):
        if not isinstance(item, item_type):
            errors.append(f"{field_name}的第{i+1}项类型错误，应为{item_type.__name__}")

    return errors


def validate_phone_number(phone: Optional[str]) -> List[str]:
    """验证电话号码格式"""
    errors: List[str] = []

    if not phone:
        return errors

    if not isinstance(phone, str):
        errors.append("电话号码必须是字符串类型")
        return errors

    phone_pattern = r'^1[3-9]\d{9}$'
    if not re.match(phone_pattern, phone):
        errors.append("电话号码格式不正确")

    return errors


def validate_url(url: Optional[str]) -> List[str]:
    """验证URL格式"""
    errors: List[str] = []

    if not url:
        return errors

    if not isinstance(url, str):
        errors.append("URL必须是字符串类型")
        return errors

    url_pattern = r'^https?://'
    if not re.match(url_pattern, url):
        errors.append("URL格式不正确，应以 http:// 或 https:// 开头")

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


def safe_int(value: Any, default: int = 0) -> int:
    """安全转换为整数"""
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """安全转换为浮点数"""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def anonymize_if_needed(text: str, privacy_mode: str) -> str:
    """根据隐私模式进行脱敏处理"""
    if privacy_mode in {"anonymous", "family_local_first"}:
        text = text.replace("孩子姓名", "孩子")
        text = text.replace("幼儿园名称", "幼儿园")
        text = text.replace("真实姓名", "***")
        text = re.sub(r'\d{3}[-]?\d{4}[-]?\d{4}', '***-****-****', text)
        text = re.sub(r'\d{11}', '***********', text)

    return text


def validate_batch_kindergartens(kindergartens: List[Dict[str, Any]]) -> Dict[str, Any]:
    """批量验证幼儿园信息"""
    result = {
        "valid_kindergartens": [],
        "invalid_kindergartens": [],
        "errors_by_kindergarten": {},
        "total_count": len(kindergartens),
        "valid_count": 0,
        "invalid_count": 0
    }

    for i, kg in enumerate(kindergartens):
        kg_id = kg.get("kindergarten_id") or kg.get("name") or f"kindergarten_{i}"
        errors = validate_kindergarten_info(kg)

        if errors:
            result["invalid_kindergartens"].append(kg)
            result["errors_by_kindergarten"][kg_id] = errors
            result["invalid_count"] += 1
        else:
            result["valid_kindergartens"].append(kg)
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
