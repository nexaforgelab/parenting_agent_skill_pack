"""Validation helpers for parenting skills.

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

    if "weight_kg" in profile:
        weight_errors = validate_weight(profile["weight_kg"])
        errors.extend([f"体重: {e}" for e in weight_errors])

    if "height_cm" in profile:
        height_errors = validate_height(profile["height_cm"])
        errors.extend([f"身高: {e}" for e in height_errors])

    return errors


def validate_meal_record(record: Dict[str, Any]) -> List[str]:
    """验证单条餐食记录

    Args:
        record: 餐食记录字典

    Returns:
        错误列表，如果为空则验证通过
    """
    errors: List[str] = []

    if not isinstance(record, dict):
        return ["记录必须是字典类型"]

    meal_name_errors = validate_meal_name(record.get("meal_name"))
    errors.extend([f"餐食名称: {e}" for e in meal_name_errors])

    meal_type_errors = validate_meal_type(record.get("meal_type"))
    errors.extend([f"餐次类型: {e}" for e in meal_type_errors])

    if "calories" in record and record["calories"] is not None:
        calories_errors = validate_calories(record["calories"])
        errors.extend([f"热量: {e}" for e in calories_errors])

    if "protein_g" in record and record["protein_g"] is not None:
        nutrient_errors = validate_nutrient(record["protein_g"], "蛋白质")
        errors.extend([f"蛋白质: {e}" for e in nutrient_errors])

    return errors


def validate_meal_name(value: Any, max_length: int = 100) -> List[str]:
    """验证餐食名称

    Args:
        value: 待验证的值
        max_length: 最大长度

    Returns:
        错误列表，如果为空则验证通过
    """
    errors: List[str] = []

    if value is None or str(value).strip() == "":
        errors.append("餐食名称不能为空")
        return errors

    name = str(value).strip()
    if len(name) < 1:
        errors.append("餐食名称至少需要1个字符")
    elif len(name) > max_length:
        errors.append(f"餐食名称不能超过{max_length}个字符")

    return errors


def validate_meal_type(value: Any) -> List[str]:
    """验证餐次类型

    Args:
        value: 待验证的值

    Returns:
        错误列表，如果为空则验证通过
    """
    errors: List[str] = []
    valid_types = {"breakfast", "lunch", "dinner", "snack", "extra"}

    if value is None or str(value).strip() == "":
        errors.append("餐次类型不能为空")
        return errors

    normalized = str(value).lower().strip()
    if normalized not in valid_types:
        errors.append(f"餐次类型必须是以下之一: {', '.join(sorted(valid_types))}")
    return errors


def validate_calories(value: Any, min_val: int = 0, max_val: int = 2000) -> List[str]:
    """验证热量值

    Args:
        value: 待验证的值
        min_val: 最小值
        max_val: 最大值

    Returns:
        错误列表，如果为空则验证通过
    """
    errors: List[str] = []

    if value is None:
        return errors

    try:
        calories = int(value)
        if calories < min_val:
            errors.append(f"热量不能小于{min_val}kcal")
        elif calories > max_val:
            errors.append(f"热量不能大于{max_val}kcal")
    except (ValueError, TypeError):
        errors.append("热量必须是整数")

    return errors


def validate_nutrient(value: Any, nutrient_name: str = "营养素", min_val: float = 0, max_val: float = 500) -> List[str]:
    """验证营养素含量

    Args:
        value: 待验证的值
        nutrient_name: 营养素名称
        min_val: 最小值
        max_val: 最大值

    Returns:
        错误列表，如果为空则验证通过
    """
    errors: List[str] = []

    if value is None:
        return errors

    try:
        amount = float(value)
        if amount < min_val:
            errors.append(f"{nutrient_name}含量不能小于{min_val}g")
        elif amount > max_val:
            errors.append(f"{nutrient_name}含量不能大于{max_val}g")
    except (ValueError, TypeError):
        errors.append(f"{nutrient_name}含量必须是数字")

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
        elif age > 240:
            errors.append("月龄不能超过240个月（20岁）")
    except (ValueError, TypeError):
        errors.append("月龄必须是整数")

    return errors


def validate_weight(value: Any, min_val: float = 0.5, max_val: float = 150.0) -> List[str]:
    """验证体重

    Args:
        value: 待验证的值
        min_val: 最小值（kg）
        max_val: 最大值（kg）

    Returns:
        错误列表，如果为空则验证通过
    """
    errors: List[str] = []

    if value is None:
        return errors

    try:
        weight = float(value)
        if weight < min_val:
            errors.append(f"体重不能小于{min_val}kg")
        elif weight > max_val:
            errors.append(f"体重不能大于{max_val}kg")
    except (ValueError, TypeError):
        errors.append("体重必须是数字")

    return errors


def validate_height(value: Any, min_val: float = 30.0, max_val: float = 250.0) -> List[str]:
    """验证身高

    Args:
        value: 待验证的值
        min_val: 最小值（cm）
        max_val: 最大值（cm）

    Returns:
        错误列表，如果为空则验证通过
    """
    errors: List[str] = []

    if value is None:
        return errors

    try:
        height = float(value)
        if height < min_val:
            errors.append(f"身高不能小于{min_val}cm")
        elif height > max_val:
            errors.append(f"身高不能大于{max_val}cm")
    except (ValueError, TypeError):
        errors.append("身高必须是数字")

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
        return text.replace("孩子姓名", "孩子").replace("学校名称", "学校").replace("家庭地址", "住址")
    return text
