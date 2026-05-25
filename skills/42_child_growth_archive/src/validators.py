"""Validation helpers for 儿童成长档案 Agent.

增强版本：添加字段级别验证、数据范围检查、格式验证、自定义错误消息
"""
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
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

    gender = profile.get("gender")
    if gender is not None and gender not in ["male", "female", "其他"]:
        errors.append("孩子性别必须是 'male'、'female' 或 '其他'")

    return errors


def validate_date_format(date_str: Any, field_name: str = "日期") -> List[str]:
    """验证日期格式"""
    errors: List[str] = []

    if date_str is None:
        errors.append(f"{field_name}不能为空")
        return errors

    if isinstance(date_str, (datetime, date)):
        return errors

    if not isinstance(date_str, str):
        errors.append(f"{field_name}必须是字符串或日期类型")
        return errors

    try:
        datetime.fromisoformat(date_str)
    except ValueError:
        errors.append(f"{field_name}格式不正确，应为 ISO 格式（如：2024-01-01 或 2024-01-01T12:00:00）")

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


def validate_growth_record(record: Dict[str, Any]) -> List[str]:
    """验证成长记录"""
    errors: List[str] = []

    if not isinstance(record, dict):
        return ["成长记录必须是字典类型"]

    record_id = record.get("record_id")
    if not record_id or not str(record_id).strip():
        errors.append("成长记录缺少 record_id 或 record_id 为空")

    date_errors = validate_date_format(record.get("record_date"), "记录日期")
    errors.extend(date_errors)

    title = record.get("title")
    if not title or not str(title).strip():
        errors.append("成长记录缺少 title 或 title 为空")

    title_errors = validate_string_length(title, "标题", max_length=200)
    errors.extend(title_errors)

    category = record.get("category")
    valid_categories = ["health", "learning", "milestone", "family", "social", "interest", "other"]
    if category and category not in valid_categories:
        errors.append(f"记录分类无效，可选值：{', '.join(valid_categories)}")

    record_type = record.get("record_type")
    valid_types = ["physical", "mental", "academic", "social", "emotional"]
    if record_type and record_type not in valid_types:
        errors.append(f"记录类型无效，可选值：{', '.join(valid_types)}")

    tags = record.get("tags")
    tags_errors = validate_list_items(tags, "标签列表", max_items=20)
    errors.extend(tags_errors)

    importance = record.get("importance")
    valid_importance = ["low", "normal", "high", "critical"]
    if importance and importance not in valid_importance:
        errors.append(f"重要性无效，可选值：{', '.join(valid_importance)}")

    return errors


def validate_archive_data(archive: Dict[str, Any]) -> List[str]:
    """验证成长档案"""
    errors: List[str] = []

    if not isinstance(archive, dict):
        return ["成长档案必须是字典类型"]

    archive_id = archive.get("archive_id")
    if not archive_id or not str(archive_id).strip():
        errors.append("成长档案缺少 archive_id 或 archive_id 为空")

    child_id = archive.get("child_id")
    if not child_id or not str(child_id).strip():
        errors.append("成长档案缺少 child_id 或 child_id 为空")

    archive_name = archive.get("archive_name")
    if not archive_name or not str(archive_name).strip():
        errors.append("成长档案缺少 archive_name 或 archive_name 为空")

    name_errors = validate_string_length(archive_name, "档案名称", max_length=100)
    errors.extend(name_errors)

    description = archive.get("description")
    desc_errors = validate_string_length(description, "档案描述", max_length=500)
    errors.extend(desc_errors)

    start_date = archive.get("start_date")
    end_date = archive.get("end_date")

    if start_date:
        start_errors = validate_date_format(start_date, "开始日期")
        errors.extend(start_errors)

    if end_date:
        end_errors = validate_date_format(end_date, "结束日期")
        errors.extend(end_errors)

    if start_date and end_date:
        try:
            start = datetime.fromisoformat(start_date) if isinstance(start_date, str) else start_date
            end = datetime.fromisoformat(end_date) if isinstance(end_date, str) else end_date
            if isinstance(start, datetime) and isinstance(end, datetime):
                if start > end:
                    errors.append("开始日期不能晚于结束日期")
        except (ValueError, AttributeError):
            pass

    record_count = archive.get("record_count")
    count_errors = validate_numeric_range(record_count, "记录数量", min_value=0, allow_none=True)
    errors.extend(count_errors)

    tags = archive.get("tags")
    tags_errors = validate_list_items(tags, "标签列表", max_items=30)
    errors.extend(tags_errors)

    year = archive.get("year")
    if year is not None:
        year_errors = validate_numeric_range(year, "年份", min_value=2000, max_value=2100)
        errors.extend(year_errors)

    return errors


def validate_privacy_mode(mode: Optional[str]) -> List[str]:
    """验证隐私模式"""
    errors: List[str] = []

    valid_modes = ["family_local_first", "anonymous", "public"]
    if mode and mode not in valid_modes:
        errors.append(f"隐私模式无效，可选值：{', '.join(valid_modes)}")

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
        text = text.replace("学校名称", "学校")
        text = text.replace("真实姓名", "***")
        text = re.sub(r'\d{3}[-]?\d{4}[-]?\d{4}', '***-****-****', text)
        text = re.sub(r'\d{11}', '***********', text)

    return text


def validate_batch_records(
    records: List[Dict[str, Any]],
    record_type: str = "记录"
) -> Dict[str, Any]:
    """批量验证记录"""
    result = {
        "valid_records": [],
        "invalid_records": [],
        "errors_by_record": {},
        "total_count": len(records),
        "valid_count": 0,
        "invalid_count": 0
    }

    for i, record in enumerate(records):
        record_id = record.get("record_id") or record.get("archive_id") or f"record_{i}"

        if record_type == "成长记录":
            errors = validate_growth_record(record)
        elif record_type == "档案":
            errors = validate_archive_data(record)
        else:
            errors = []

        if errors:
            result["invalid_records"].append(record)
            result["errors_by_record"][record_id] = errors
            result["invalid_count"] += 1
        else:
            result["valid_records"].append(record)
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
