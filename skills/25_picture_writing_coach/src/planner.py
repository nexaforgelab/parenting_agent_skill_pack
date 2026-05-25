"""Planning engine for 小学看图写话 Agent.

提供数据分析、异常检测、个性化推荐和上下文记忆功能。
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
from collections import defaultdict
try:
    from .models import WritingRecord, ProgressStats, ObservationGuide, Recommendation, SessionContext
except ImportError:
    from models import WritingRecord, ProgressStats, ObservationGuide, Recommendation, SessionContext


SKILL_FLOW = ['上传图片', '引导观察人物、地点、动作、心情', '生成提问', '孩子口述', 'Agent 整理成作文', '给出修改建议']
SAFETY_NOTES = [
    '本 Skill 以启发式陪练为主，避免直接替孩子完成作业或代写成品。',
    '输出应包含引导问题、解题路径、错因分析和复习建议，保留孩子自主思考过程。',
    '涉及教材、地区考试政策或校内要求时，应提示以学校老师最新要求为准。'
]
DEFAULT_DELIVERABLES = ['看图写话稿', '观察清单', '表达提升建议']


def build_known_facts(payload: Dict[str, Any]) -> List[str]:
    """构建已知事实列表"""
    facts: List[str] = []
    child = payload.get("child_profile", {})
    family = payload.get("family_context", {})
    if child:
        facts.append(f"孩子画像：{child}")
    if family:
        facts.append(f"家庭上下文：{family}")
    if payload.get("goal"):
        facts.append(f"目标：{payload.get('goal')}")
    records = payload.get("raw_records") or []
    facts.append(f"已收到 {len(records)} 条原始记录。")
    return facts


def build_analysis(payload: Dict[str, Any]) -> List[str]:
    """构建分析内容"""
    problem = payload.get("current_problem", "")
    history_days = payload.get("history_days", 7)
    analysis = [
        f"当前问题聚焦：{problem}",
        f"建议先建立最近 {history_days} 天的家庭基线，再判断趋势。",
        "本 Skill 会优先输出可执行动作、记录字段和复盘指标。",
    ]
    for step in SKILL_FLOW:
        analysis.append(f"链路节点：{step}")
    return analysis


def build_action_plan(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """构建行动计划"""
    base_tasks = [
        "补齐孩子画像和家庭限制条件",
        "把今天相关事件按时间线记录",
        "执行一个低压力动作并记录孩子反应",
        "晚上用 3 分钟复盘有效/无效做法",
        "一周后比较趋势并调整计划",
    ]
    plan: List[Dict[str, str]] = []
    for i, task in enumerate(base_tasks, start=1):
        plan.append({
            "day": f"D{i}",
            "task": task,
            "owner": "家长/主要照护人",
            "evidence_to_record": "时间、触发点、执行方式、孩子反应",
            "difficulty": "低" if i <= 3 else "中"
        })
    return plan


def build_deliverables(payload: Dict[str, Any]) -> Dict[str, Any]:
    """构建交付物定义"""
    return {
        "required": DEFAULT_DELIVERABLES,
        "tables": {
            "timeline": ["时间", "事件", "输入", "处理", "结果", "备注"],
            "weekly_review": ["指标", "本周", "上周", "变化", "下一步"]
        },
        "templates": {
            "daily_log": "今天发生了什么？我做了什么？孩子反应如何？下一次要调整什么？",
            "handoff_summary": "给专业人士/老师/家人的沟通摘要：事实、时间线、已尝试方法、待确认问题。"
        }
    }


def next_fields() -> List[str]:
    """获取下次追踪字段列表"""
    return [
        "孩子年龄/月龄",
        "今天新增记录",
        "执行了哪一步",
        "孩子反应",
        "家长感受",
        "需要调整的限制条件"
    ]


def analyze_writing_progress(writing_records: List[Dict[str, Any]]) -> ProgressStats:
    """分析写作进度"""
    if not writing_records:
        return ProgressStats()

    total = len(writing_records)
    total_word_count = sum(r.get("word_count", 0) for r in writing_records)
    total_expression = sum(r.get("expression_score", 0) for r in writing_records)
    total_structure = sum(r.get("structure_score", 0) for r in writing_records)
    total_creativity = sum(r.get("creativity_score", 0) for r in writing_records)

    weakness_stats = defaultdict(int)
    strength_stats = defaultdict(int)

    for record in writing_records:
        if record.get("expression_score", 0) < 70:
            weakness_stats["表达能力"] += 1
        else:
            strength_stats["表达能力"] += 1

        if record.get("structure_score", 0) < 70:
            weakness_stats["结构组织"] += 1
        else:
            strength_stats["结构组织"] += 1

        if record.get("creativity_score", 0) < 70:
            weakness_stats["创意表达"] += 1
        else:
            strength_stats["创意表达"] += 1

    common_weaknesses = [k for k, v in weakness_stats.items() if v > total * 0.3]
    strong_areas = [k for k, v in strength_stats.items() if v > total * 0.5]

    return ProgressStats(
        total_writings=total,
        average_word_count=total_word_count / total if total > 0 else 0,
        average_expression_score=total_expression / total if total > 0 else 0,
        average_structure_score=total_structure / total if total > 0 else 0,
        average_creativity_score=total_creativity / total if total > 0 else 0,
        common_weaknesses=common_weaknesses,
        strong_areas=strong_areas
    )


def generate_observation_guide(picture_description: str) -> ObservationGuide:
    """生成观察引导"""
    return ObservationGuide(
        characters=["图中有哪些人物？", "他们的外貌特征是什么？"],
        setting="这是在什么地方？什么时间？",
        actions=["人物在做什么？", "发生了什么故事？"],
        emotions=["人物的心情是怎样的？", "你是怎么知道的？"],
        suggested_elements=["人物", "环境", "动作", "表情", "时间"]
    )


def generate_recommendations(progress_stats: ProgressStats) -> List[Recommendation]:
    """生成个性化推荐"""
    recommendations = []

    if progress_stats.common_weaknesses:
        recommendations.append(Recommendation(
            recommendation_id="rec_weakness",
            category="薄弱提升",
            priority="高",
            title=f"加强{', '.join(progress_stats.common_weaknesses)}",
            description=f"需要在 {', '.join(progress_stats.common_weaknesses)} 方面加强练习",
            target_areas=progress_stats.common_weaknesses,
            suggested_duration=30,
            confidence_score=0.85
        ))

    if progress_stats.average_word_count < 100:
        recommendations.append(Recommendation(
            recommendation_id="rec_word_count",
            category="写作长度",
            priority="中",
            title="增加写作字数",
            description=f"当前平均字数 {progress_stats.average_word_count:.0f} 字，建议增加到 100 字以上",
            suggested_duration=20,
            confidence_score=0.8
        ))

    if progress_stats.average_expression_score < 75:
        recommendations.append(Recommendation(
            recommendation_id="rec_expression",
            category="表达能力",
            priority="高",
            title="提升表达能力",
            description="建议多阅读优秀作文，学习好的表达方式",
            target_areas=["表达能力"],
            suggested_duration=25,
            confidence_score=0.85
        ))

    if progress_stats.strong_areas:
        recommendations.append(Recommendation(
            recommendation_id="rec_strength",
            category="能力发挥",
            priority="低",
            title="发挥优势",
            description=f"在 {', '.join(progress_stats.strong_areas)} 方面表现不错，可以继续发挥",
            suggested_duration=15,
            confidence_score=0.75
        ))

    return recommendations


def create_session_context(payload: Dict[str, Any], session_id: str) -> SessionContext:
    """创建会话上下文"""
    child_profile = payload.get("child_profile", {})

    return SessionContext(
        session_id=session_id,
        start_time=datetime.now().isoformat(),
        child_id=child_profile.get("name", "未知"),
        grade_level=child_profile.get("grade", 1),
        current_stage=None,
        conversation_history=[],
        recent_performance=payload.get("raw_records", []),
        user_preferences=payload.get("preferences", {})
    )


def update_session_context(
    context: SessionContext,
    role: str,
    content: str,
    performance_data: Optional[Dict[str, Any]] = None
) -> None:
    """更新会话上下文"""
    context.add_interaction(role, content)

    if performance_data:
        context.recent_performance.append(performance_data)
        if len(context.recent_performance) > 20:
            context.recent_performance = context.recent_performance[-20:]
