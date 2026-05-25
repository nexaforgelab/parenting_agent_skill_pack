"""Validation helpers for 家庭会议主持 Agent."""
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
    def __init__(self, field_name: str, required: bool = True, min_value: Optional[float] = None, max_value: Optional[float] = None):
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


class DateValidator(FieldValidator):
    """日期字段验证器"""
    def __init__(self, field_name: str = "日期", required: bool = True, date_format: str = "%Y-%m-%d"):
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
    """验证payload基础结构"""
    errors: List[str] = []
    if not isinstance(payload, dict):
        return ["payload 必须是 dict"]
    if not payload.get("child_profile"):
        errors.append("缺少 child_profile")
    if not str(payload.get("current_problem", "")).strip():
        errors.append("缺少 current_problem")
    return errors


def validate_meeting_record(record: Dict[str, Any]) -> List[str]:
    """验证会议记录"""
    errors = []
    if not isinstance(record, dict):
        return ["record 必须是字典类型"]
    if "meeting_type" in record:
        valid_types = {"weekly_planning", "monthly_review", "problem_solving", "celebration", "rules_update", "schedule_discussion"}
        if record["meeting_type"] not in valid_types:
            errors.append(f"meeting_type 必须是以下值之一: {', '.join(valid_types)}")
    return errors


def validate_agenda_item(item: Dict[str, Any]) -> List[str]:
    """验证议程项目"""
    errors = []
    if not isinstance(item, dict):
        return ["item 必须是字典类型"]
    if not item.get("topic"):
        errors.append("议程项目缺少 topic")
    if "time_allocation" in item:
        validator = NumberValidator("时间分配", required=False, min_value=1, max_value=60)
        validator.errors = []
        errors.extend(validator.validate(item["time_allocation"]))
    return errors


def validate_decision(decision: Dict[str, Any]) -> List[str]:
    """验证会议决议"""
    errors = []
    if not isinstance(decision, dict):
        return ["decision 必须是字典类型"]
    if not decision.get("topic"):
        errors.append("决议缺少 topic")
    if not decision.get("decision"):
        errors.append("决议缺少 decision")
    if "status" in decision:
        valid_statuses = {"pending", "discussed", "decided", "deferred", "rejected"}
        if decision["status"] not in valid_statuses:
            errors.append(f"status 必须是以下值之一: {', '.join(valid_statuses)}")
    return errors


def validate_child_profile(profile: Dict[str, Any]) -> List[str]:
    """验证孩子画像"""
    errors = []
    if not isinstance(profile, dict):
        return ["child_profile 必须是字典类型"]
    return errors


def validate_preferences(preferences: Dict[str, Any]) -> List[str]:
    """验证偏好设置"""
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
                record_errors = validate_meeting_record(record)
                for err in record_errors:
                    self.errors.append(f"raw_records[{i}]: {err}")
        if "preferences" in payload:
            pref_errors = validate_preferences(payload["preferences"])
            self.errors.extend(pref_errors)
        return self.errors

    def is_valid(self) -> bool:
        """检查是否有效"""
        return len(self.errors) == 0