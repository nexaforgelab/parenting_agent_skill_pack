"""家长辅导话术 Agent - 规划引擎

增强版本：添加数据分析、异常检测、个性化推荐、上下文记忆、对话策略分析
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from collections import defaultdict
import json
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

try:
    from .models import (
        TutoringPhrase, PhraseCategory, ChildProfile,
        ConversationRecord, PhraseRecommendation, TutoringAnalysis,
        SkillInput, SkillOutput, SessionContext, get_or_create_context
    )
    from .validators import validate_payload, validate_payload_with_details
except ImportError:
    from models import (
        TutoringPhrase, PhraseCategory, ChildProfile,
        ConversationRecord, PhraseRecommendation, TutoringAnalysis,
        SkillInput, SkillOutput, SessionContext, get_or_create_context
    )
    from validators import validate_payload, validate_payload_with_details

try:
    from .reporting import render_report
except ImportError:
    from reporting import render_report

SKILL_FLOW = [
    '分析孩子当前问题和情绪状态',
    '匹配适合的辅导话术库',
    '提供具体话术建议和使用场景',
    '分析历史对话效果',
    '生成个性化辅导策略'
]

SAFETY_NOTES = [
    '本 Skill 只提供沟通话术参考，不替代专业心理咨询或教育指导',
    '遇到孩子严重情绪问题时请寻求专业帮助',
    '话术使用需结合孩子个体差异灵活调整'
]

DEFAULT_DELIVERABLES = [
    '个性化话术推荐清单',
    '辅导对话策略指南',
    '常见场景话术手册',
    '效果跟踪记录表'
]

PHRASE_LIBRARY = [
    TutoringPhrase(
        id="enc_001",
        category=PhraseCategory.ENCOURAGEMENT,
        phrase_text="没关系，我们慢慢来。这道题看起来有点难，让妈妈/爸爸和你一起看看。",
        applicable_ages=[6, 7, 8, 9, 10, 11, 12],
        applicable_subjects=["数学", "语文", "英语"],
        applicable_emotion_states=["anxious", "frustrated"],
        example_usage="当孩子因为题目太难而想放弃时使用",
        effect_description="降低孩子的焦虑感，建立安全感",
        usage_tips=["语气要平和", "不要急于求成", "保持耐心"]
    ),
    TutoringPhrase(
        id="enc_002",
        category=PhraseCategory.ENCOURAGEMENT,
        phrase_text="我看到你已经很努力了！这个进步真的很大，继续加油！",
        applicable_ages=[8, 9, 10, 11, 12, 13, 14, 15],
        applicable_subjects=["数学", "语文", "英语", "物理", "化学"],
        applicable_emotion_states=["confident", "excited"],
        example_usage="当孩子完成一道难题或取得进步时使用",
        effect_description="强化积极行为，增强自信心",
        usage_tips=["具体指出进步的地方", "真诚地表扬", "不要过度夸张"]
    ),
    TutoringPhrase(
        id="gui_001",
        category=PhraseCategory.GUIDANCE,
        phrase_text="让我们一起来读这道题。先找找题目里告诉我们什么了？",
        applicable_ages=[6, 7, 8, 9, 10, 11, 12],
        applicable_subjects=["数学", "语文"],
        applicable_emotion_states=["confused"],
        example_usage="当孩子不理解题目意思时使用",
        effect_description="引导孩子独立思考，而不是直接给答案",
        usage_tips=["放慢语速", "用手指着关键词", "等待孩子回应"]
    ),
    TutoringPhrase(
        id="gui_002",
        category=PhraseCategory.GUIDANCE,
        phrase_text="如果...会怎么样呢？比如说，如果把这个数字换掉，答案会变吗？",
        applicable_ages=[9, 10, 11, 12, 13, 14],
        applicable_subjects=["数学", "物理"],
        applicable_emotion_states=["confused", "bored"],
        example_usage="当孩子机械记忆公式而不理解原理时使用",
        effect_description="激发探索精神，加深理解",
        usage_tips=["用具体例子引导", "鼓励孩子尝试", "不要直接给答案"]
    ),
    TutoringPhrase(
        id="com_001",
        category=PhraseCategory.COMFORT,
        phrase_text="做不出来有点沮丧对不对？妈妈/爸爸小时候也遇到过这样的题目，当时也想了好久。",
        applicable_ages=[8, 9, 10, 11, 12, 13, 14, 15],
        applicable_subjects=["数学", "语文", "英语", "物理", "化学"],
        applicable_emotion_states=["frustrated", "anxious", "resistant"],
        example_usage="当孩子因为反复出错而情绪崩溃时使用",
        effect_description="建立情感连接，让孩子感到被理解",
        usage_tips=["共情但不妥协", "承认困难但强调可以克服", "保持温和坚定的语气"]
    ),
    TutoringPhrase(
        id="com_002",
        category=PhraseCategory.COMFORT,
        phrase_text="没关系，错题是最好的老师。我们来看看这道题能教我们什么。",
        applicable_ages=[8, 9, 10, 11, 12, 13, 14, 15],
        applicable_subjects=["数学", "语文", "英语", "物理", "化学"],
        applicable_emotion_states=["frustrated", "confused"],
        example_usage="当孩子因为错题而沮丧时使用",
        effect_description="转变对错误的看法，把错误当作学习机会",
        usage_tips=["语气要轻松", "不要责备", "引导反思"]
    ),
    TutoringPhrase(
        id="que_001",
        category=PhraseCategory.QUESTIONING,
        phrase_text="你觉得这道题考的是什么知识点？能不能用自己的话说说看？",
        applicable_ages=[10, 11, 12, 13, 14, 15],
        applicable_subjects=["数学", "物理", "化学"],
        applicable_emotion_states=["confused", "neutral"],
        example_usage="当孩子对题目类型不熟悉时使用",
        effect_description="帮助孩子建立知识框架，加深理解",
        usage_tips=["给孩子思考时间", "不要急于给出答案", "根据回答逐步引导"]
    ),
    TutoringPhrase(
        id="que_002",
        category=PhraseCategory.QUESTIONING,
        phrase_text="上次的题目和今天的有什么相同和不同？你注意到了吗？",
        applicable_ages=[10, 11, 12, 13, 14, 15],
        applicable_subjects=["数学", "物理", "化学"],
        applicable_emotion_states=["confused", "confident"],
        example_usage="当孩子遇到相似但不完全相同的题目时使用",
        effect_description="培养类比和归纳能力",
        usage_tips=["对比分析", "找出规律", "总结方法"]
    ),
    TutoringPhrase(
        id="pri_001",
        category=PhraseCategory.PRAISE,
        phrase_text="太棒了！你刚才的思路非常清晰，一步一步来得很稳！",
        applicable_ages=[6, 7, 8, 9, 10, 11, 12],
        applicable_subjects=["数学", "语文", "英语"],
        applicable_emotion_states=["confident", "excited"],
        example_usage="当孩子表现出色时使用",
        effect_description="强化正确行为，增强学习动力",
        usage_tips=["表扬具体行为", "不要只说聪明", "及时表扬"]
    ),
    TutoringPhrase(
        id="pri_002",
        category=PhraseCategory.PRAISE,
        phrase_text="我注意到你今天特别认真，这个解题步骤写得整整齐齐的！",
        applicable_ages=[8, 9, 10, 11, 12, 13, 14],
        applicable_subjects=["数学", "语文", "英语", "物理"],
        applicable_emotion_states=["neutral", "confident"],
        example_usage="当孩子态度认真但结果不够好时使用",
        effect_description="肯定努力过程，而不是只看结果",
        usage_tips=["关注过程而非结果", "具体指出优点", "培养成长型思维"]
    ),
    TutoringPhrase(
        id="lim_001",
        category=PhraseCategory.LIMIT_SETTING,
        phrase_text="现在我们需要休息一下了。做5道题，然后休息5分钟，怎么样？",
        applicable_ages=[6, 7, 8, 9, 10, 11, 12, 13, 14],
        applicable_subjects=["数学", "语文", "英语", "物理", "化学"],
        applicable_emotion_states=["bored", "resistant", "anxious"],
        example_usage="当孩子注意力下降或开始抵触时使用",
        effect_description="设置合理边界，提供喘息空间",
        usage_tips=["语气坚定但不严厉", "提供选择", "遵守约定"]
    ),
    TutoringPhrase(
        id="lim_002",
        category=PhraseCategory.LIMIT_SETTING,
        phrase_text="妈妈/爸爸理解你想玩，但是完成作业后我们可以更好地放松，你觉得呢？",
        applicable_ages=[8, 9, 10, 11, 12, 13, 14],
        applicable_subjects=["数学", "语文", "英语", "物理", "化学"],
        applicable_emotion_states=["resistant"],
        example_usage="当孩子想要逃避学习时使用",
        effect_description="温和但坚定地坚持规则",
        usage_tips=["承认感受", "解释原因", "提供替代方案"]
    ),
    TutoringPhrase(
        id="emo_001",
        category=PhraseCategory.EMOTION_COACHING,
        phrase_text="我看到你有点生气了。你能告诉我是什么让你不舒服吗？",
        applicable_ages=[8, 9, 10, 11, 12, 13, 14, 15],
        applicable_subjects=["数学", "语文", "英语", "物理", "化学"],
        applicable_emotion_states=["frustrated", "anxious"],
        example_usage="当孩子情绪激动时使用",
        effect_description="帮助孩子识别和表达情绪",
        usage_tips=["先处理情绪", "共情但不妥协", "引导表达"]
    ),
    TutoringPhrase(
        id="emo_002",
        category=PhraseCategory.EMOTION_COACHING,
        phrase_text="深呼吸一下，我们慢慢来。你现在感觉好一点了吗？",
        applicable_ages=[8, 9, 10, 11, 12, 13, 14],
        applicable_subjects=["数学", "语文", "英语", "物理", "化学"],
        applicable_emotion_states=["frustrated", "anxious"],
        example_usage="当孩子情绪失控时使用",
        effect_description="帮助孩子学会情绪调节",
        usage_tips=["保持冷静", "给出具体方法", "等待孩子平静"]
    ),
    TutoringPhrase(
        id="err_001",
        category=PhraseCategory.ERROR_HANDLING,
        phrase_text="这个答案有点不一样，我们来看看哪里不一样...啊，我看到你的思路了，其实你理解了！",
        applicable_ages=[8, 9, 10, 11, 12, 13, 14],
        applicable_subjects=["数学", "物理", "化学"],
        applicable_emotion_states=["frustrated", "confused"],
        example_usage="当孩子答案错误但思路部分正确时使用",
        effect_description="保护自尊心，同时指出改进方向",
        usage_tips=["先找优点", "温和指出问题", "引导自我发现"]
    ),
    TutoringPhrase(
        id="err_002",
        category=PhraseCategory.ERROR_HANDLING,
        phrase_text="计算的时候要小心这个步骤哦。来，我们一起重新算一遍，看看哪里需要特别注意。",
        applicable_ages=[9, 10, 11, 12, 13],
        applicable_subjects=["数学", "物理", "化学"],
        applicable_emotion_states=["neutral", "confused"],
        example_usage="当孩子因粗心而出错时使用",
        effect_description="指出问题但避免批评",
        usage_tips=["具体指出易错点", "提供检查方法", "培养细心习惯"]
    )
]


def get_or_create_session_context(session_id: str) -> SessionContext:
    """获取或创建会话上下文"""
    return get_or_create_context(session_id)


def update_context(session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
    """更新会话上下文"""
    context = get_or_create_session_context(session_id)
    context.add_interaction(role, content, metadata)


def match_phrases_to_context(
    child_profile: Dict[str, Any],
    emotion_state: str,
    subject: str,
    context_keywords: List[str]
) -> List[PhraseRecommendation]:
    """根据上下文匹配合适的话术

    Args:
        child_profile: 孩子画像
        emotion_state: 情绪状态
        subject: 学科
        context_keywords: 上下文关键词

    Returns:
        话术推荐列表，按匹配度排序
    """
    recommendations = []
    age = child_profile.get("age", 10)

    for phrase in PHRASE_LIBRARY:
        score = 0.0
        reasons = []

        if phrase.applicable_ages and age in phrase.applicable_ages:
            score += 0.3
            reasons.append(f"适合{age}岁年龄段")

        if phrase.applicable_subjects and subject in phrase.applicable_subjects:
            score += 0.3
            reasons.append(f"适用于{subject}学科")

        if phrase.applicable_emotion_states and emotion_state in phrase.applicable_emotion_states:
            score += 0.3
            reasons.append(f"适合'{emotion_state}'情绪状态")

        for keyword in context_keywords:
            if keyword.lower() in phrase.phrase_text.lower():
                score += 0.1
                reasons.append(f"包含关键词'{keyword}'")

        if score > 0:
            alternatives = [p for p in PHRASE_LIBRARY
                          if p.category == phrase.category and p.id != phrase.id][:2]
            recommendations.append(PhraseRecommendation(
                phrase=phrase,
                match_score=score,
                match_reasons=reasons,
                alternative_phrases=alternatives,
                timing_advice=f"建议在{phrase.timing}时使用",
                expected_effect=phrase.effect_description
            ))

    recommendations.sort(key=lambda x: x.match_score, reverse=True)
    return recommendations[:5]


def analyze_conversation_patterns(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析对话模式

    Args:
        records: 对话记录列表

    Returns:
        分析结果字典
    """
    if not records:
        return {
            "total_sessions": 0,
            "effective_categories": {},
            "emotion_improvement_rate": 0.0,
            "common_strategies": [],
            "recommendations": []
        }

    category_counts = defaultdict(int)
    emotion_positive = 0
    emotion_total = 0

    for record in records:
        behavior = record.get("tutor_behavior", "")
        for phrase in PHRASE_LIBRARY:
            if phrase.phrase_text[:10] in behavior:
                category_counts[phrase.category.value] += 1

        if record.get("child_emotion_before") and record.get("child_emotion_after"):
            emotion_total += 1
            positive_states = {"confident", "excited", "neutral"}
            if record["child_emotion_after"] in positive_states:
                emotion_positive += 1

    emotion_rate = (emotion_positive / emotion_total * 100) if emotion_total > 0 else 0

    common_strategies = sorted(
        [f"经常使用{cat}类型话术" for cat, count in category_counts.items() if count >= 2]
    )

    return {
        "total_sessions": len(records),
        "effective_categories": dict(category_counts),
        "emotion_improvement_rate": round(emotion_rate, 1),
        "common_strategies": common_strategies,
        "recommendations": [
            "继续保持有效的沟通方式" if emotion_rate > 60 else "建议尝试更多鼓励性话术",
            "注意观察孩子的情绪变化信号"
        ]
    }


def detect_communication_issues(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """检测沟通问题

    Args:
        records: 对话记录列表

    Returns:
        问题列表
    """
    issues = []

    if not records:
        return issues

    recent_failures = [r for r in records if r.get("outcome") in ["poor", "failed"]]
    if len(recent_failures) > len(records) * 0.3:
        issues.append({
            "type": "high_failure_rate",
            "severity": "warning",
            "message": "最近辅导失败率偏高",
            "recommendation": "建议降低难度或改变沟通方式"
        })

    emotion_declines = 0
    for record in records:
        negative_states = {"frustrated", "anxious", "resistant"}
        if (record.get("child_emotion_before") in negative_states and
            record.get("child_emotion_after") in negative_states):
            emotion_declines += 1

    if emotion_declines > len(records) * 0.2:
        issues.append({
            "type": "emotion_not_improving",
            "severity": "warning",
            "message": "孩子情绪在辅导后没有明显改善",
            "recommendation": "建议使用更多情感支持类话术"
        })

    return issues


def generate_personalized_tips(
    child_profile: Dict[str, Any],
    emotion_state: str,
    session_goal: str
) -> List[str]:
    """生成个性化辅导建议

    Args:
        child_profile: 孩子画像
        emotion_state: 情绪状态
        session_goal: 辅导目标

    Returns:
        建议列表
    """
    tips = []
    age = child_profile.get("age", 10)
    learning_style = child_profile.get("learning_style", "visual")
    attention_span = child_profile.get("attention_span_minutes", 30)

    if age <= 10:
        tips.append(f"建议每次辅导时间控制在{attention_span}分钟以内，设置短暂休息")
        tips.append("使用具体形象的例子解释抽象概念")

    if learning_style == "visual":
        tips.append("建议配合图表、颜色标记等视觉工具")
    elif learning_style == "auditory":
        tips.append("建议多使用口头讲解和讨论")
    elif learning_style == "kinesthetic":
        tips.append("建议通过动手操作和角色扮演学习")

    if emotion_state in ["frustrated", "anxious"]:
        tips.append("先处理情绪，再处理学习任务")
        tips.append("降低任务难度，建立成功体验")

    if emotion_state == "bored":
        tips.append("增加互动性和趣味性")
        tips.append("使用计时器增加紧迫感")

    if session_goal:
        tips.append(f"围绕目标'{session_goal}'设计辅导环节")
        tips.append("结束时回顾目标完成情况")

    return tips


def analyze_communication_style(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析沟通风格

    Args:
        records: 对话记录列表

    Returns:
        风格分析结果
    """
    if not records:
        return {
            "dominant_style": "unknown",
            "balance_score": 0.0,
            "strengths": [],
            "areas_for_improvement": []
        }

    category_usage = defaultdict(int)
    total_phrases = 0

    for record in records:
        behavior = record.get("tutor_behavior", "")
        for phrase in PHRASE_LIBRARY:
            if phrase.phrase_text[:10] in behavior:
                category_usage[phrase.category.value] += 1
                total_phrases += 1

    if total_phrases == 0:
        return {
            "dominant_style": "unknown",
            "balance_score": 0.0,
            "strengths": ["开始记录辅导对话可获得更准确的建议"],
            "areas_for_improvement": ["建议使用本Skill记录辅导对话"]
        }

    category_percentages = {
        cat: (count / total_phrases * 100)
        for cat, count in category_usage.items()
    }

    strengths = []
    improvements = []

    if category_usage.get(PhraseCategory.ENCOURAGEMENT.value, 0) > total_phrases * 0.2:
        strengths.append("鼓励性沟通较多，有助于建立自信心")
    else:
        improvements.append("建议增加鼓励性话术的使用")

    if category_usage.get(PhraseCategory.QUESTIONING.value, 0) > total_phrases * 0.15:
        strengths.append("善于用提问引导思考")
    else:
        improvements.append("建议增加引导性提问")

    if category_usage.get(PhraseCategory.EMOTION_COACHING.value, 0) < total_phrases * 0.1:
        improvements.append("建议增加情绪引导类话术")

    balance_score = 1.0 - (max(category_percentages.values()) / 100) if category_percentages else 0.0

    return {
        "dominant_style": max(category_usage, key=category_usage.get) if category_usage else "unknown",
        "balance_score": round(balance_score, 2),
        "category_distribution": category_percentages,
        "strengths": strengths,
        "areas_for_improvement": improvements
    }


def build_known_facts(payload: Dict[str, Any]) -> List[str]:
    """构建已知事实列表

    Args:
        payload: 输入数据

    Returns:
        事实列表
    """
    facts: List[str] = []
    child = payload.get("child_profile", {})
    if child:
        name = child.get("name", "孩子")
        age = child.get("age", 0)
        grade = child.get("grade", "")
        facts.append(f"孩子信息：{name}，{age}岁，{grade}")

    if payload.get("session_goal"):
        facts.append(f"本次辅导目标：{payload['session_goal']}")

    if payload.get("subject"):
        facts.append(f"辅导学科：{payload['subject']}")

    emotion = payload.get("child_emotion_state", "neutral")
    facts.append(f"孩子当前情绪状态：{emotion}")

    records = payload.get("conversation_history") or []
    facts.append(f"历史对话记录：{len(records)}条")

    if records:
        style_analysis = analyze_communication_style(records)
        if style_analysis.get("dominant_style") != "unknown":
            facts.append(f"沟通风格分析：{style_analysis['dominant_style']}为主")

    return facts


def build_analysis(payload: Dict[str, Any]) -> List[str]:
    """构建分析内容

    Args:
        payload: 输入数据

    Returns:
        分析内容列表
    """
    analysis = []
    child_profile = payload.get("child_profile", {})
    emotion_state = payload.get("child_emotion_state", "neutral")
    subject = payload.get("subject", "")
    problem = payload.get("current_problem", "")
    session_goal = payload.get("session_goal", "")

    analysis.append(f"当前问题聚焦：{problem}")
    analysis.append("本 Skill 会提供个性化话术建议和沟通策略")

    records = payload.get("conversation_history") or []

    if records:
        pattern_analysis = analyze_conversation_patterns(records)
        analysis.append("")
        analysis.append("📊 对话模式分析：")
        analysis.append(f"  - 总辅导次数：{pattern_analysis['total_sessions']}次")
        if pattern_analysis.get("emotion_improvement_rate"):
            analysis.append(f"  - 情绪改善率：{pattern_analysis['emotion_improvement_rate']}%")

        issues = detect_communication_issues(records)
        if issues:
            analysis.append("")
            analysis.append("⚠️ 检测到的问题：")
            for issue in issues:
                analysis.append(f"  - {issue['message']}")
                analysis.append(f"    建议：{issue['recommendation']}")

        style_analysis = analyze_communication_style(records)
        if style_analysis.get("strengths"):
            analysis.append("")
            analysis.append("✅ 沟通优势：")
            for strength in style_analysis["strengths"]:
                analysis.append(f"  - {strength}")

    return analysis


def build_action_plan(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """构建行动计划

    Args:
        payload: 输入数据

    Returns:
        行动计划列表
    """
    base_tasks = [
        "建立良好的辅导环境，保持安静无干扰",
        "先观察孩子的情绪状态，再开始辅导",
        "使用推荐的话术进行沟通",
        "记录孩子的反应和情绪变化",
        "辅导结束后进行简短总结"
    ]

    session_goal = payload.get("session_goal", "")
    if session_goal:
        base_tasks.insert(0, f"明确目标：{session_goal}")

    plan: List[Dict[str, str]] = []
    for i, task in enumerate(base_tasks, start=1):
        plan.append({
            "day": f"本次辅导",
            "step": f"步骤{i}",
            "task": task,
            "owner": "家长/辅导者",
            "difficulty": "低" if i <= 3 else "中"
        })
    return plan


def build_deliverables(payload: Dict[str, Any]) -> Dict[str, Any]:
    """构建交付物

    Args:
        payload: 输入数据

    Returns:
        交付物字典
    """
    deliverables = {
        "required": DEFAULT_DELIVERABLES,
        "templates": {
            "session_record": "时间 | 孩子情绪 | 使用话术 | 孩子反应 | 效果评估",
            "phrase_practice_log": "日期 | 场景 | 话术 | 效果 | 改进点"
        },
        "phrase_categories": {
            "encouragement": "鼓励类话术",
            "guidance": "引导类话术",
            "comfort": "安慰类话术",
            "questioning": "提问类话术",
            "praise": "表扬类话术",
            "limit_setting": "边界设置类话术",
            "emotion_coaching": "情绪引导类话术",
            "error_handling": "错误处理类话术"
        }
    }

    child_profile = payload.get("child_profile", {})
    emotion_state = payload.get("child_emotion_state", "neutral")
    subject = payload.get("subject", "")
    problem = payload.get("current_problem", "")
    keywords = problem.split()[:5]

    recommendations = match_phrases_to_context(
        child_profile, emotion_state, subject, keywords
    )

    if recommendations:
        deliverables["recommended_phrases"] = [r.to_dict() for r in recommendations]

    return deliverables


def next_fields() -> List[str]:
    """获取下次追踪字段"""
    return [
        "孩子情绪状态变化",
        "使用了哪些话术",
        "孩子的反应如何",
        "辅导目标是否达成",
        "下次需要调整的地方"
    ]


def run(payload: Dict[str, Any], session_id: str = "default") -> Dict[str, Any]:
    """主运行函数

    Args:
        payload: 输入数据字典
        session_id: 会话ID

    Returns:
        处理结果字典
    """
    validation_result = validate_payload_with_details(payload)

    if not validation_result["is_valid"]:
        return {
            "success": False,
            "errors": validation_result["errors"],
            "validation_details": validation_result
        }

    context = get_or_create_session_context(session_id)

    known_facts = build_known_facts(payload)
    analysis = build_analysis(payload)
    action_plan = build_action_plan(payload)
    deliverables = build_deliverables(payload)

    child_profile = payload.get("child_profile", {})
    emotion_state = payload.get("child_emotion_state", "neutral")
    subject = payload.get("subject", "")
    problem = payload.get("current_problem", "")
    session_goal = payload.get("session_goal", "")
    keywords = problem.split()[:5]

    recommendations = match_phrases_to_context(
        child_profile, emotion_state, subject, keywords
    )

    tips = generate_personalized_tips(child_profile, emotion_state, session_goal)

    records = payload.get("conversation_history") or []
    communication_analysis = analyze_communication_style(records)

    phrase_library = [p.to_dict() for p in PHRASE_LIBRARY]

    result = {
        "success": True,
        "skill_id": "parent_tutoring_phrases",
        "summary": [
            f"为{payload.get('child_profile', {}).get('name', '孩子')}提供辅导话术建议",
            f"根据'{problem}'提供个性化话术推荐",
            f"生成{len(recommendations)}条精准话术匹配"
        ],
        "known_facts": known_facts,
        "analysis": analysis,
        "recommended_phrases": [r.to_dict() for r in recommendations],
        "tutoring_tips": tips,
        "action_plan": action_plan,
        "deliverables": deliverables,
        "risk_notes": SAFETY_NOTES,
        "next_tracking_fields": next_fields(),
        "communication_analysis": communication_analysis,
        "phrase_library": phrase_library,
        "session_recommendations": [
            {
                "phase": "辅导前",
                "action": "观察并确认孩子情绪状态",
                "phrase_tip": "使用安慰类或鼓励类话术开场"
            },
            {
                "phase": "辅导中",
                "action": "根据孩子反应灵活调整",
                "phrase_tip": "准备多类别话术应对不同情况"
            },
            {
                "phase": "辅导后",
                "action": "简短总结，肯定进步",
                "phrase_tip": "使用鼓励类或表扬类话术收尾"
            }
        ],
        "warnings": validation_result.get("warnings", [])
    }

    result["markdown_report"] = render_report(result)

    return result


if __name__ == "__main__":
    sample_payload = {
        "child_profile": {
            "name": "小明",
            "age": 11,
            "grade": "五年级",
            "learning_style": "visual",
            "attention_span_minutes": 25
        },
        "current_problem": "数学应用题理解困难",
        "child_emotion_state": "confused",
        "subject": "数学",
        "session_goal": "理解并解决分数应用题"
    }

    result = run(sample_payload)
    print(result["markdown_report"])
