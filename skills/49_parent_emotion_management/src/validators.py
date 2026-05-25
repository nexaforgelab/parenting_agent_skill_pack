"""Validation helpers for 父母情绪管理 Agent.

提供完整的字段级验证、数据范围检查、格式验证和自定义错误消息。
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, date


class ValidationError(Exception):
    """自定义验证错误异常"""

    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(f"验证错误: {', '.join(errors)}")


class FieldValidator:
    """字段验证器基类"""

    def __init__(self, field_name: str, required: bool = True):
        self.field_name = field_name
        self.required = required
        self.errors: List[str] = []

    def validate(self, value: Any) -> List[str]:
        """验证字段值"""
        self.errors = []
        if value is None or value == "":
            if self.required:
                self.errors.append(f"{self.field_name} 是必填字段")
            return self.errors
        return self.errors


class NumberValidator(FieldValidator):
    """数字字段验证器"""

    def __init__(
        self,
        field_name: str,
        required: bool = True,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ):
        super().__init__(field_name, required)
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: Any) -> List[str]:
        """验证数字字段"""
        self.errors = []
        if value is None:
            if self.required:
                self.errors.append(f"{self.field_name} 是必填字段")
            return self.errors

        try:
            num_value = float(value)
        except (ValueError, TypeError):
            self.errors.append(f"{self.field_name} 必须是数字类型")
            return self.errors

        if self.min_value is not None and num_value < self.min_value:
            self.errors.append(f"{self.field_name} 不能小于 {self.min_value}")
        if self.max_value is not None and num_value > self.max_value:
            self.errors.append(f"{self.field_name} 不能大于 {self.max_value}")

        return self.errors


class IntensityValidator(NumberValidator):
    """情绪强度验证器"""

    def __init__(self, field_name: str = "情绪强度"):
        super().__init__(field_name, required=True, min_value=1, max_value=10)


class EffectivenessValidator(NumberValidator):
    """有效性评分验证器"""

    def __init__(self, field_name: str = "有效性评分"):
        super().__init__(field_name, required=False, min_value=1, max_value=5)


class DateValidator(FieldValidator):
    """日期字段验证器"""

    def __init__(
        self,
        field_name: str = "日期",
        required: bool = True,
        date_format: str = "%Y-%m-%d"
    ):
        super().__init__(field_name, required)
        self.date_format = date_format

    def validate(self, value: Any) -> List[str]:
        """验证日期字段"""
        self.errors = []
        if value is None:
            if self.required:
                self.errors.append(f"{self.field_name} 是必填字段")
            return self.errors

        if isinstance(value, (datetime, date)):
            return self.errors
        elif isinstance(value, str):
            try:
                datetime.strptime(value, self.date_format)
                return self.errors
            except ValueError:
                self.errors.append(f"{self.field_name} 日期格式不正确，应为 {self.date_format}")
                return self.errors
        else:
            self.errors.append(f"{self.field_name} 必须是日期或字符串类型")
            return self.errors


def require_payload(payload: Dict[str, Any]) -> List[str]:
    """验证payload基础结构

    Args:
        payload: 输入的payload字典

    Returns:
        错误列表
    """
    errors: List[str] = []
    if not isinstance(payload, dict):
        return ["payload 必须是 dict"]
    if not payload.get("child_profile"):
        errors.append("缺少 child_profile")
    if not str(payload.get("current_problem", "")).strip():
        errors.append("缺少 current_problem")
    return errors


def validate_emotion_record(record: Dict[str, Any]) -> List[str]:
    """验证情绪记录

    Args:
        record: 情绪记录字典

    Returns:
        错误列表
    """
    errors = []

    if not isinstance(record, dict):
        return ["record 必须是字典类型"]

    if "emotion_type" in record:
        valid_emotions = {
            "anger", "frustration", "anxiety", "sadness", "guilt",
            "overwhelm", "exhaustion", "joy", "calm", "gratitude"
        }
        if record["emotion_type"] not in valid_emotions:
            errors.append(f"emotion_type 必须是以下值之一: {', '.join(valid_emotions)}")

    intensity_validator = IntensityValidator("情绪强度")
    intensity_errors = intensity_validator.validate(record.get("intensity"))
    errors.extend(intensity_errors)

    effectiveness_validator = EffectivenessValidator("有效性评分")
    effectiveness_errors = effectiveness_validator.validate(record.get("effectiveness"))
    errors.extend(effectiveness_errors)

    if "coping_used" in record and not isinstance(record["coping_used"], list):
        errors.append("coping_used 必须是列表类型")

    return errors


def validate_coping_strategy(strategy: str) -> List[str]:
    """验证应对策略

    Args:
        strategy: 应对策略标识

    Returns:
        错误列表
    """
    errors = []
    valid_strategies = {
        "breathing", "pause", "physical_activity", "self_talk",
        "seek_support", "journaling", "professional_help", "mindfulness"
    }
    if strategy not in valid_strategies:
        errors.append(f"strategy 必须是以下值之一: {', '.join(valid_strategies)}")
    return errors


def validate_child_profile(profile: Dict[str, Any]) -> List[str]:
    """验证孩子画像

    Args:
        profile: 孩子画像字典

    Returns:
        错误列表
    """
    errors = []

    if not isinstance(profile, dict):
        return ["child_profile 必须是字典类型"]

    return errors


def validate_preferences(preferences: Dict[str, Any]) -> List[str]:
    """验证偏好设置

    Args:
        preferences: 偏好设置字典

    Returns:
        错误列表
    """
    errors = []

    if not isinstance(preferences, dict):
        return ["preferences 必须是字典类型"]

    if "privacy_mode" in preferences:
        valid_modes = {"anonymous", "family_local_first", "full"}
        if preferences["privacy_mode"] not in valid_modes:
            errors.append(f"privacy_mode 必须是以下值之一: {', '.join(valid_modes)}")

    return errors


def safe_list(value: Any) -> List[Any]:
    """安全转换为列表"""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def anonymize_if_needed(text: str, privacy_mode: str) -> str:
    """根据隐私模式脱敏处理"""
    if privacy_mode in {"anonymous", "family_local_first"}:
        return text.replace("孩子姓名", "孩子").replace("学校名称", "学校")
    return text


class PayloadValidator:
    """Payload综合验证器"""

    def __init__(self):
        self.errors: List[str] = []

    def validate(self, payload: Dict[str, Any]) -> List[str]:
        """执行完整验证"""
        self.errors = []

        base_errors = require_payload(payload)
        self.errors.extend(base_errors)

        if base_errors:
            return self.errors

        if "child_profile" in payload:
            profile_errors = validate_child_profile(payload["child_profile"])
            self.errors.extend(profile_errors)

        if "raw_records" in payload:
            for i, record in enumerate(payload["raw_records"]):
                record_errors = validate_emotion_record(record)
                for err in record_errors:
                    self.errors.append(f"raw_records[{i}]: {err}")

        if "preferences" in payload:
            pref_errors = validate_preferences(payload["preferences"])
            self.errors.extend(pref_errors)

        return self.errors

    def is_valid(self) -> bool:
        """检查是否有效"""
        return len(self.errors) == 0


def detect_crisis_signals(records: List[Dict[str, Any]]) -> List[str]:
    """检测危机信号

    Args:
        records: 情绪记录列表

    Returns:
        危机信号列表
    """
    signals = []

    if not records:
        return signals

    high_intensity_count = sum(1 for r in records if r.get("intensity", 0) >= 8)
    if high_intensity_count > len(records) * 0.5:
        signals.append("高强度情绪频繁出现，建议寻求专业支持")

    self_harm_keywords = ["伤害自己", "自残", "不想活", "放弃"]
    for record in records:
        notes = record.get("notes", "")
        if any(keyword in notes for keyword in self_harm_keywords):
            signals.append("检测到自我伤害相关表达，请寻求专业心理帮助")
            break

    professional_keywords = ["心理咨询", "心理医生", "精神科", "治疗"]
    for record in records:
        if any(keyword in str(record.get("coping_used", [])) for keyword in professional_keywords):
            signals.append("正在接受专业心理帮助，继续保持")
            break

    return signals