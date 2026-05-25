"""Validation helpers for 家庭买菜清单 Agent.

增强版本：添加字段级别验证、数据范围检查、格式验证
"""
from typing import Any, Dict, List
from datetime import datetime, date
import re


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


def validate_child_profile(profile: Dict[str, Any]) -> List[str]:
    """验证孩子画像字段"""
    errors: List[str] = []
    if not isinstance(profile, dict):
        return ["child_profile 必须是字典类型"]
    return errors


def validate_record(record: Dict[str, Any]) -> List[str]:
    """验证单条记录"""
    errors: List[str] = []
    if not isinstance(record, dict):
        return ["记录必须是字典类型"]
    if "item_name" not in record or not str(record.get("item_name", "")).strip():
        errors.append("item_name 不能为空")
    return errors


def validate_amount(value: Any) -> List[str]:
    """验证金额"""
    errors: List[str] = []
    if value is None:
        return errors
    try:
        amount = float(value)
        if amount < 0:
            errors.append("金额不能为负数")
        elif amount > 100000:
            errors.append("金额超出正常范围")
    except (ValueError, TypeError):
        errors.append("金额必须是数字")
    return errors


def validate_category(value: Any) -> List[str]:
    """验证品类"""
    errors: List[str] = []
    valid_categories = {"vegetable", "fruit", "meat", "dairy", "grain", "snack", "beverage", "other"}
    if value is None or str(value).strip() == "":
        return errors
    normalized = str(value).lower().strip()
    if normalized not in valid_categories:
        errors.append(f"品类必须是以下之一: {', '.join(sorted(valid_categories))}")
    return errors


def safe_list(value: Any) -> List[Any]:
    """安全地转换为列表"""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def anonymize_if_needed(text: str, privacy_mode: str) -> str:
    """根据隐私模式匿名化文本"""
    if privacy_mode in {"anonymous", "family_local_first"}:
        return text.replace("孩子姓名", "孩子").replace("家庭地址", "住址")
    return text
