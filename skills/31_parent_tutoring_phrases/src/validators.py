"""家长辅导话术 Agent - 数据验证器

增强版本：添加字段级别验证、数据范围检查、格式验证、自定义错误消息
"""
from __future__ import annotations
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

    if "age" in profile:
        age_errors = validate_age(profile["age"])
        errors.extend([f"年龄: {e}" for e in age_errors])

    if "grade" in profile:
        grade_errors = validate_grade(profile["grade"])
        errors.extend([f"年级: {e}" for e in grade_errors])

    if "attention_span_minutes" in profile:
        span_errors = validate_attention_span(profile["attention_span_minutes"])
        errors.extend([f"专注时长: {e}" for e in span_errors])

    if "learning_style" in profile:
        style_errors = validate_learning_style(profile["learning_style"])
        errors.extend([f"学习风格: {e}" for e in style_errors])

    return errors


def validate_age(value: Any) -> List[str]:
    """验证年龄字段

    Args:
        value: 待验证的值

    Returns:
        错误列表
    """
    errors: List[str] = []

    if value is None:
        return errors

    try:
        age = int(value)
        if age < 3:
            errors.append("年龄不能小于3岁")
        elif age > 18:
            errors.append("年龄不能超过18岁")
    except (ValueError, TypeError):
        errors.append("年龄必须是整数")

    return errors


def validate_grade(value: Any) -> List[str]:
    """验证年级字段

    Args:
        value: 待验证的值

    Returns:
        错误列表
    """
    errors: List[str] = []

    if value is None or str(value).strip() == "":
        return errors

    valid_grades = {
        "幼儿园小班", "幼儿园中班", "幼儿园大班",
        "一年级", "二年级", "三年级", "四年级", "五年级", "六年级",
        "初一", "初二", "初三",
        "高一", "高二", "高三"
    }

    grade = str(value).strip()
    if grade not in valid_grades:
        errors.append(f"年级必须是以下之一: {', '.join(sorted(valid_grades))}")

    return errors


def validate_name(value: Any) -> List[str]:
    """验证姓名格式

    Args:
        value: 待验证的值

    Returns:
        错误列表
    """
    errors: List[str] = []

    if value is None or str(value).strip() == "":
        return errors

    name = str(value).strip()
    if len(name) < 1:
        errors.append("姓名不能为空")
    elif len(name) > 50:
        errors.append("姓名不能超过50个字符")

    if not re.match(r'^[\u4e00-\u9fa5a-zA-Z\s·]+$', name):
        errors.append("姓名只能包含中文、英文字母和空格")

    return errors


def validate_attention_span(value: Any) -> List[str]:
    """验证专注时长

    Args:
        value: 待验证的值

    Returns:
        错误列表
    """
    errors: List[str] = []

    if value is None:
        return errors

    try:
        span = int(value)
        if span < 5:
            errors.append("专注时长不能小于5分钟")
        elif span > 120:
            errors.append("专注时长不建议超过120分钟")
    except (ValueError, TypeError):
        errors.append("专注时长必须是整数")

    return errors


def validate_learning_style(value: Any) -> List[str]:
    """验证学习风格

    Args:
        value: 待验证的值

    Returns:
        错误列表
    """
    errors: List[str] = []
    valid_styles = {"visual", "auditory", "kinesthetic", "reading", "mixed"}

    if value is None or str(value).strip() == "":
        return errors

    normalized = str(value).lower().strip()
    if normalized not in valid_styles:
        errors.append(f"学习风格必须是以下之一: {', '.join(sorted(valid_styles))}")

    return errors


def validate_emotion_state(value: Any) -> List[str]:
    """验证情绪状态

    Args:
        value: 待验证的值

    Returns:
        错误列表
    """
    errors: List[str] = []
    valid_states = {
        "confident", "anxious", "frustrated", "confused",
        "bored", "excited", "resistant", "neutral"
    }

    if value is None or str(value).strip() == "":
        return errors

    normalized = str(value).lower().strip()
    if normalized not in valid_states:
        errors.append(f"情绪状态必须是以下之一: {', '.join(sorted(valid_states))}")

    return errors


def validate_subject(value: Any) -> List[str]:
    """验证学科

    Args:
        value: 待验证的值

    Returns:
        错误列表
    """
    errors: List[str] = []

    if value is None or str(value).strip() == "":
        return errors

    valid_subjects = {
        "语文", "数学", "英语", "物理", "化学", "生物",
        "历史", "地理", "政治", "音乐", "美术", "体育",
        "科学", "信息技术"
    }

    subject = str(value).strip()
    if subject not in valid_subjects:
        errors.append(f"学科必须是以下之一: {', '.join(sorted(valid_subjects))}")

    return errors


def validate_tutoring_phrase(phrase: Dict[str, Any]) -> List[str]:
    """验证辅导话术

    Args:
        phrase: 话术字典

    Returns:
        错误列表
    """
    errors: List[str] = []

    if not isinstance(phrase, dict):
        return ["话术必须是字典类型"]

    if "phrase_text" in phrase:
        text = phrase["phrase_text"]
        if not text or not str(text).strip():
            errors.append("话术文本不能为空")
        if len(str(text)) > 500:
            errors.append("话术文本不能超过500字符")

    if "category" in phrase:
        cat = phrase["category"]
        valid_categories = {
            "encouragement", "guidance", "comfort", "questioning",
            "praise", "limit_setting", "emotion_coaching", "error_handling"
        }
        if cat not in valid_categories:
            errors.append(f"话术类别必须是以下之一: {', '.join(sorted(valid_categories))}")

    if "tone" in phrase:
        tone = phrase["tone"]
        valid_tones = {"warm", "neutral", "firm", "gentle", "enthusiastic"}
        if tone not in valid_tones:
            errors.append(f"语气必须是以下之一: {', '.join(sorted(valid_tones))}")

    if "difficulty_level" in phrase:
        level = phrase["difficulty_level"]
        valid_levels = {"beginner", "intermediate", "advanced"}
        if level not in valid_levels:
            errors.append(f"难度必须是以下之一: {', '.join(sorted(valid_levels))}")

    return errors


def validate_conversation_record(record: Dict[str, Any]) -> List[str]:
    """验证对话记录

    Args:
        record: 记录字典

    Returns:
        错误列表
    """
    errors: List[str] = []

    if not isinstance(record, dict):
        return ["记录必须是字典类型"]

    if "tutor_behavior" in record:
        behavior = record["tutor_behavior"]
        if not str(behavior).strip():
            errors.append("辅导行为描述不能为空")

    if "outcome" in record:
        outcome = record["outcome"]
        valid_outcomes = {"excellent", "good", "neutral", "poor", "failed", "unknown"}
        if outcome not in valid_outcomes:
            errors.append(f"结果必须是以下之一: {', '.join(sorted(valid_outcomes))}")

    return errors


def validate_session_goal(value: Any) -> List[str]:
    """验证辅导目标

    Args:
        value: 待验证的值

    Returns:
        错误列表
    """
    errors: List[str] = []

    if value is None or str(value).strip() == "":
        return errors

    goal = str(value)
    if len(goal) < 5:
        errors.append("辅导目标描述太短，请更具体地说明")
    if len(goal) > 200:
        errors.append("辅导目标描述不能超过200字符")

    return errors


def validate_notes(value: Any, max_length: int = 500) -> List[str]:
    """验证备注字段

    Args:
        value: 待验证的值
        max_length: 最大长度

    Returns:
        错误列表
    """
    errors: List[str] = []

    if value is None or str(value).strip() == "":
        return errors

    notes = str(value)
    if len(notes) > max_length:
        errors.append(f"备注不能超过{max_length}个字符")

    return errors


def validate_history_days(value: Any) -> List[str]:
    """验证历史天数

    Args:
        value: 待验证的值

    Returns:
        错误列表
    """
    errors: List[str] = []

    if value is None:
        return errors

    try:
        days = int(value)
        if days < 1:
            errors.append("历史天数不能小于1")
        elif days > 90:
            errors.append("历史天数不能超过90")
    except (ValueError, TypeError):
        errors.append("历史天数必须是整数")

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
        return text.replace("孩子姓名", "孩子").replace("真实姓名", "孩子")
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

    if "conversation_history" in payload:
        records = safe_list(payload["conversation_history"])
        for i, record in enumerate(records):
            record_errors = validate_conversation_record(record)
            if record_errors:
                result["field_errors"][f"record_{i}"] = record_errors

    if "history_days" in payload:
        days_errors = validate_history_days(payload["history_days"])
        if days_errors:
            result["errors"].extend(days_errors)

    if "session_goal" in payload:
        goal_errors = validate_session_goal(payload["session_goal"])
        if goal_errors:
            result["warnings"].extend(goal_errors)

    return result


def validate_payload(payload: Dict[str, Any]) -> bool:
    """简化的payload验证

    Args:
        payload: 待验证的payload字典

    Returns:
        是否验证通过
    """
    errors = require_payload(payload)
    if errors:
        raise ValidationError(errors)
    return True
