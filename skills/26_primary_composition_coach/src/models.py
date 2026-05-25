"""Data models for 小学作文陪练 Agent.

这些模型保持轻量，方便 OpenClaw / Hermes / 任意 Python Agent Runtime 直接复用。
提供增强的数据类，包括学习记录、进度统计、推荐、上下文等。
"""
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime
import json


@dataclass
class SkillInput:
    """技能输入数据模型

    属性:
        child_profile: 孩子画像信息
        current_problem: 当前问题描述
        family_context: 家庭上下文信息
        goal: 学习目标
        raw_records: 原始学习记录列表
        preferences: 用户偏好设置
        attachments: 附件列表
        history_days: 历史记录天数
        privacy_mode: 隐私模式
    """
    child_profile: Dict[str, Any]
    current_problem: str
    family_context: Dict[str, Any] = field(default_factory=dict)
    goal: str = ""
    raw_records: List[Dict[str, Any]] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    history_days: int = 7
    privacy_mode: str = "family_local_first"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            字典格式的输入数据
        """
        return asdict(self)

    def validate(self) -> List[str]:
        """验证输入数据

        Returns:
            错误信息列表
        """
        errors = []
        if not self.child_profile:
            errors.append("child_profile 不能为空")
        if not self.current_problem or not str(self.current_problem).strip():
            errors.append("current_problem 不能为空")
        if self.history_days < 1:
            errors.append("history_days 必须大于等于 1")
        return errors


@dataclass
class ActionItem:
    """行动计划项数据模型

    属性:
        day: 计划日期标识
        task: 任务描述
        owner: 负责人
        evidence_to_record: 需要记录的证据
        difficulty: 难度等级
    """
    day: str
    task: str
    owner: str = "家长"
    evidence_to_record: str = "一句话记录执行结果"
    difficulty: str = "低"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            字典格式的行动项
        """
        return asdict(self)


@dataclass
class LearningRecord:
    """学习记录数据模型

    属性:
        record_id: 记录唯一标识
        timestamp: 记录时间戳
        topic: 作文题目
        writing_type: 作文类型
        word_count: 字数
        quality_score: 质量评分 (0-10)
        structure_score: 结构评分 (0-10)
        content_score: 内容评分 (0-10)
        language_score: 语言评分 (0-10)
        feedback: 反馈信息
        strengths: 优点列表
        weaknesses: 不足列表
        improvement_suggestions: 改进建议
        practice_duration_minutes: 练习时长（分钟）
        is_completed: 是否完成
    """
    record_id: str
    timestamp: str
    topic: str = ""
    writing_type: str = "记叙文"
    word_count: int = 0
    quality_score: float = 0.0
    structure_score: float = 0.0
    content_score: float = 0.0
    language_score: float = 0.0
    feedback: str = ""
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    practice_duration_minutes: int = 0
    is_completed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            字典格式的学习记录
        """
        return asdict(self)

    def validate(self) -> List[str]:
        """验证学习记录

        Returns:
            错误信息列表
        """
        errors = []
        if not self.record_id:
            errors.append("record_id 不能为空")
        if self.word_count < 0:
            errors.append("word_count 不能为负数")
        if not 0 <= self.quality_score <= 10:
            errors.append("quality_score 必须在 0-10 之间")
        if not 0 <= self.structure_score <= 10:
            errors.append("structure_score 必须在 0-10 之间")
        return errors

    def get_overall_score(self) -> float:
        """获取综合评分

        Returns:
            综合评分 (0-10)
        """
        return round((self.quality_score + self.structure_score + self.content_score + self.language_score) / 4, 2)

    def is_passed(self, threshold: float = 6.0) -> bool:
        """判断是否达标

        Args:
            threshold: 达标阈值

        Returns:
            是否达标
        """
        return self.get_overall_score() >= threshold


@dataclass
class ProgressStats:
    """进度统计数据模型

    属性:
        total_sessions: 总练习次数
        total_words: 总字数
        average_quality_score: 平均质量评分
        recent_trend: 近期趋势
        most_practiced_types: 最常练习的类型
        weak_types: 薄弱类型
        summary: 总结描述
    """
    total_sessions: int = 0
    total_words: int = 0
    average_quality_score: float = 0.0
    recent_trend: str = "insufficient_data"
    most_practiced_types: List[str] = field(default_factory=list)
    weak_types: List[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            字典格式的进度统计
        """
        return asdict(self)

    def is_improving(self) -> bool:
        """判断是否在进步

        Returns:
            是否在进步
        """
        return self.recent_trend == "improving"

    def get_summary_text(self) -> str:
        """获取摘要文本

        Returns:
            摘要文本
        """
        return f"共完成 {self.total_sessions} 次练习，累计 {self.total_words} 字"


@dataclass
class Recommendation:
    """推荐数据模型

    属性:
        recommendation_id: 推荐唯一标识
        category: 推荐类别
        priority: 优先级
        title: 推荐标题
        description: 推荐描述
        action_items: 行动项列表
        expected_benefit: 预期收益
        target_mastery_level: 目标掌握程度
        estimated_duration: 预计时长
    """
    recommendation_id: str
    category: str
    priority: str
    title: str
    description: str = ""
    action_items: List[str] = field(default_factory=list)
    expected_benefit: str = ""
    target_mastery_level: str = "LEARNING"
    estimated_duration: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            字典格式的推荐
        """
        return asdict(self)

    def is_high_priority(self) -> bool:
        """判断是否高优先级

        Returns:
            是否高优先级
        """
        return self.priority in ["high", "高"]

    def get_action_count(self) -> int:
        """获取行动项数量

        Returns:
            行动项数量
        """
        return len(self.action_items)


@dataclass
class SessionContext:
    """会话上下文数据模型

    属性:
        session_id: 会话唯一标识
        child_id: 孩子标识
        start_time: 开始时间
        current_topic: 当前话题
        recent_records: 最近记录
        conversation_history: 对话历史
        preferences: 偏好设置
        detected_interests: 检测到的兴趣
        detected_difficulties: 检测到的困难
        learning_goals: 学习目标
        parent_notes: 家长备注
    """
    session_id: str
    child_id: str
    start_time: str
    current_topic: str = ""
    recent_records: List[Dict[str, Any]] = field(default_factory=list)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    detected_interests: List[str] = field(default_factory=list)
    detected_difficulties: List[str] = field(default_factory=list)
    learning_goals: List[str] = field(default_factory=list)
    parent_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            字典格式的会话上下文
        """
        return asdict(self)

    def add_conversation(self, role: str, content: str) -> None:
        """添加对话记录

        Args:
            role: 角色
            content: 内容
        """
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def get_conversation_summary(self) -> str:
        """获取对话摘要

        Returns:
            对话摘要
        """
        return f"共 {len(self.conversation_history)} 条对话记录"


@dataclass
class SkillOutput:
    """技能输出数据模型

    属性:
        skill_id: 技能标识
        summary: 摘要列表
        known_facts: 已知事实列表
        analysis: 分析结果列表
        action_plan: 行动计划列表
        deliverables: 交付物字典
        risk_notes: 风险提示列表
        next_tracking_fields: 下次追踪字段列表
        markdown_report: Markdown格式的报告
        progress: 进度统计
        difficulties: 困难列表
        recommendations: 推荐列表
        learning_curve: 学习曲线
        mastery_level: 掌握程度
        session_context: 会话上下文
    """
    skill_id: str
    summary: List[str]
    known_facts: List[str]
    analysis: List[str]
    action_plan: List[ActionItem]
    deliverables: Dict[str, Any]
    risk_notes: List[str]
    next_tracking_fields: List[str]
    markdown_report: str = ""
    progress: Optional[ProgressStats] = None
    difficulties: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[Recommendation] = field(default_factory=list)
    learning_curve: Optional[Dict[str, Any]] = None
    mastery_level: str = "NOT_STARTED"
    session_context: Optional[SessionContext] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            字典格式的输出数据
        """
        result = {
            "skill_id": self.skill_id,
            "summary": self.summary,
            "known_facts": self.known_facts,
            "analysis": self.analysis,
            "action_plan": [item.to_dict() if hasattr(item, 'to_dict') else item for item in self.action_plan],
            "deliverables": self.deliverables,
            "risk_notes": self.risk_notes,
            "next_tracking_fields": self.next_tracking_fields,
            "markdown_report": self.markdown_report,
        }
        if self.progress:
            result["progress"] = self.progress.to_dict() if hasattr(self.progress, 'to_dict') else self.progress
        result["difficulties"] = self.difficulties
        result["recommendations"] = [r.to_dict() if hasattr(r, 'to_dict') else r for r in self.recommendations]
        if self.learning_curve:
            result["learning_curve"] = self.learning_curve
        result["mastery_level"] = self.mastery_level
        if self.session_context:
            result["session_context"] = self.session_context.to_dict() if hasattr(self.session_context, 'to_dict') else self.session_context
        return result

    def to_json(self) -> str:
        """转换为JSON字符串

        Returns:
            JSON字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def get_key_findings(self) -> List[str]:
        """获取关键发现

        Returns:
            关键发现列表
        """
        findings = []
        if self.progress:
            findings.append(f"总练习次数: {self.progress.total_sessions}")
            findings.append(f"累计字数: {self.progress.total_words}")
            findings.append(f"平均质量评分: {self.progress.average_quality_score}")
        if self.mastery_level:
            findings.append(f"掌握程度: {self.mastery_level}")
        return findings
