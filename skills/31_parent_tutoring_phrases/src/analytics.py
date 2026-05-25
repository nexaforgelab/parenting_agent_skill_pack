"""家长辅导话术 Agent - 数据分析模块

增强版本：提供话术效果分析、学习趋势跟踪、个性化洞察
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from collections import defaultdict


class PhraseAnalytics:
    """话术效果分析器"""

    def __init__(self):
        """初始化分析器"""
        self.history: List[Dict[str, Any]] = []

    def add_session(self, session_data: Dict[str, Any]) -> None:
        """添加辅导会话数据

        Args:
            session_data: 会话数据字典
        """
        session_data["recorded_at"] = datetime.now().isoformat()
        self.history.append(session_data)

    def analyze_effectiveness(self) -> Dict[str, Any]:
        """分析话术效果

        Returns:
            效果分析结果
        """
        if not self.history:
            return {
                "total_sessions": 0,
                "effectiveness_score": 0.0,
                "top_phrases": [],
                "improvement_trend": []
            }

        phrase_effectiveness = defaultdict(lambda: {"success": 0, "total": 0})

        for session in self.history:
            phrases_used = session.get("phrases_used", [])
            outcome = session.get("outcome", "neutral")

            for phrase in phrases_used:
                phrase_effectiveness[phrase]["total"] += 1
                if outcome in ["excellent", "good"]:
                    phrase_effectiveness[phrase]["success"] += 1

        top_phrases = []
        for phrase, stats in phrase_effectiveness.items():
            if stats["total"] >= 1:
                rate = stats["success"] / stats["total"] * 100
                top_phrases.append({
                    "phrase": phrase,
                    "success_rate": rate,
                    "usage_count": stats["total"]
                })

        top_phrases.sort(key=lambda x: x["success_rate"], reverse=True)

        total_effectiveness = sum(
            p["success_rate"] * p["usage_count"]
            for p in top_phrases
        ) / sum(p["usage_count"] for p in top_phrases) if top_phrases else 0

        return {
            "total_sessions": len(self.history),
            "effectiveness_score": round(total_effectiveness, 1),
            "top_phrases": top_phrases[:5],
            "phrase_count": len(phrase_effectiveness)
        }

    def detect_patterns(self) -> List[Dict[str, Any]]:
        """检测使用模式

        Returns:
            模式列表
        """
        patterns = []

        if len(self.history) < 3:
            return patterns

        emotion_map = defaultdict(int)
        for session in self.history:
            emotion_before = session.get("emotion_before", "")
            emotion_after = session.get("emotion_after", "")
            if emotion_before and emotion_after:
                emotion_map[(emotion_before, emotion_after)] += 1

        for (before, after), count in emotion_map.items():
            if count >= 2:
                patterns.append({
                    "pattern": f"{before} → {after}",
                    "frequency": count,
                    "interpretation": self._interpret_emotion_pattern(before, after)
                })

        return sorted(patterns, key=lambda x: x["frequency"], reverse=True)

    def _interpret_emotion_pattern(self, before: str, after: str) -> str:
        """解释情绪模式

        Args:
            before: 之前情绪
            after: 之后情绪

        Returns:
            解释文本
        """
        positive_before = {"confident", "excited", "neutral"}
        positive_after = {"confident", "excited"}
        negative_before = {"frustrated", "anxious", "resistant"}
        negative_after = {"confident", "excited", "neutral"}

        if before in negative_before and after in positive_after:
            return "有效转化：负面情绪转为正面"
        elif before in positive_before and after in positive_after:
            return "保持良好：维持正面情绪"
        elif before in negative_before and after in negative_before:
            return "需改进：负面情绪未能转化"
        else:
            return "观察中：需持续关注"

    def generate_insights(self) -> List[str]:
        """生成洞察

        Returns:
            洞察列表
        """
        insights = []

        effectiveness = self.analyze_effectiveness()

        if effectiveness["total_sessions"] == 0:
            insights.append("建议开始记录辅导对话以获得个性化分析")
            return insights

        if effectiveness["effectiveness_score"] >= 70:
            insights.append("您的辅导沟通整体效果良好，继续保持！")
        elif effectiveness["effectiveness_score"] >= 50:
            insights.append("辅导沟通有改进空间，建议增加鼓励和引导类话术")
        else:
            insights.append("建议系统学习本Skill的话术库，并记录辅导效果")

        top = effectiveness.get("top_phrases", [])
        if top:
            insights.append(f"最有效的话术类型已记录在案，建议多使用")

        patterns = self.detect_patterns()
        if patterns:
            insights.append(f"检测到{len(patterns)}个情绪转化模式，请关注辅导中的情绪变化")

        return insights


def analyze_learning_progress(
    history_records: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """分析学习进步情况

    Args:
        history_records: 历史记录列表

    Returns:
        进步分析结果
    """
    if not history_records:
        return {
            "trend": "unknown",
            "improvement_rate": 0.0,
            "difficulty_areas": [],
            "strength_areas": []
        }

    session_scores = []
    difficulty_topics = defaultdict(int)
    strength_topics = defaultdict(int)

    for record in history_records:
        score = record.get("outcome_score", 50)
        session_scores.append(score)

        topic = record.get("topic", "")
        outcome = record.get("outcome", "neutral")

        if outcome in ["excellent", "good"] and topic:
            strength_topics[topic] += 1
        elif outcome in ["poor", "failed"] and topic:
            difficulty_topics[topic] += 1

    if len(session_scores) >= 2:
        first_half = session_scores[:len(session_scores)//2]
        second_half = session_scores[len(session_scores)//2:]
        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)
        improvement = ((avg_second - avg_first) / avg_first * 100) if avg_first > 0 else 0
    else:
        improvement = 0

    return {
        "trend": "improving" if improvement > 5 else "stable" if improvement > -5 else "declining",
        "improvement_rate": round(improvement, 1),
        "difficulty_areas": [t for t, _ in sorted(difficulty_topics.items(), key=lambda x: x[1], reverse=True)[:3]],
        "strength_areas": [t for t, _ in sorted(strength_topics.items(), key=lambda x: x[1], reverse=True)[:3]],
        "average_score": round(sum(session_scores) / len(session_scores), 1) if session_scores else 0
    }


def calculate_phrase_diversity_score(
    used_phrases: List[str],
    total_available: int = 16
) -> Dict[str, Any]:
    """计算话术多样性得分

    Args:
        used_phrases: 已使用的话术列表
        total_available: 总可用话术数

    Returns:
        多样性分析结果
    """
    unique_phrases = set(used_phrases)

    diversity_score = (len(unique_phrases) / total_available * 100) if total_available > 0 else 0

    missing_categories = []
    phrase_categories = {
        "enc_": "鼓励类",
        "gui_": "引导类",
        "com_": "安慰类",
        "que_": "提问类",
        "pri_": "表扬类",
        "lim_": "边界设置类",
        "emo_": "情绪引导类",
        "err_": "错误处理类"
    }

    for prefix, cat_name in phrase_categories.items():
        if not any(p.startswith(prefix) for p in unique_phrases):
            missing_categories.append(cat_name)

    return {
        "diversity_score": round(diversity_score, 1),
        "unique_phrase_count": len(unique_phrases),
        "total_available": total_available,
        "recommendation": "建议尝试未使用的话术类别" if missing_categories else "话术使用较为均衡"
    }


def predict_success_probability(
    child_profile: Dict[str, Any],
    session_context: Dict[str, Any]
) -> Dict[str, Any]:
    """预测辅导成功概率

    Args:
        child_profile: 孩子画像
        session_context: 会话上下文

    Returns:
        预测结果
    """
    base_probability = 50.0

    age = child_profile.get("age", 10)
    if 8 <= age <= 12:
        base_probability += 10

    emotional_sensitivity = child_profile.get("emotional_sensitivity", "medium")
    if emotional_sensitivity == "high":
        base_probability -= 15
    elif emotional_sensitivity == "low":
        base_probability += 10

    emotion_state = session_context.get("emotion_state", "neutral")
    if emotion_state in ["confident", "excited"]:
        base_probability += 20
    elif emotion_state in ["frustrated", "anxious"]:
        base_probability -= 15
    elif emotion_state == "bored":
        base_probability -= 10

    recommended_phrases = session_context.get("recommended_phrases", [])
    if len(recommended_phrases) >= 3:
        base_probability += 10

    tips_followed = session_context.get("tips_followed", 0)
    total_tips = session_context.get("total_tips", 1)
    if total_tips > 0:
        tip_bonus = (tips_followed / total_tips) * 10
        base_probability += tip_bonus

    probability = max(0, min(100, base_probability))

    risk_factors = []
    protective_factors = []

    if emotional_sensitivity == "high":
        risk_factors.append("孩子情绪敏感度较高")
    if emotion_state in ["frustrated", "anxious"]:
        risk_factors.append("当前情绪状态不佳")
    if probability < 50:
        risk_factors.append("综合因素影响成功率")

    if 8 <= age <= 12:
        protective_factors.append("处于学习黄金期")
    if emotion_state in ["confident", "excited"]:
        protective_factors.append("当前情绪积极")
    if len(recommended_phrases) >= 3:
        protective_factors.append("有充足的话术支持")

    return {
        "success_probability": round(probability, 1),
        "risk_factors": risk_factors,
        "protective_factors": protective_factors,
        "recommendation": "建议降低期望，循序渐进" if probability < 50 else "条件有利，可以尝试"
    }


def generate_weekly_summary(
    records: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """生成周度总结

    Args:
        records: 记录列表

    Returns:
        周度总结
    """
    if not records:
        return {
            "total_sessions": 0,
            "average_outcome": 0,
            "main_challenges": [],
            "main_wins": [],
            "next_week_focus": []
        }

    total_sessions = len(records)
    outcomes = [r.get("outcome_score", 50) for r in records]
    avg_outcome = sum(outcomes) / len(outcomes) if outcomes else 0

    challenge_topics = defaultdict(int)
    win_topics = defaultdict(int)

    for record in records:
        topic = record.get("topic", "")
        outcome = record.get("outcome", "neutral")

        if outcome in ["poor", "failed"] and topic:
            challenge_topics[topic] += 1
        elif outcome in ["excellent", "good"] and topic:
            win_topics[topic] += 1

    main_challenges = [t for t, _ in sorted(challenge_topics.items(), key=lambda x: x[1], reverse=True)[:2]]
    main_wins = [t for t, _ in sorted(win_topics.items(), key=lambda x: x[1], reverse=True)[:2]]

    next_week_focus = []
    if main_challenges:
        next_week_focus.append(f"重点关注：{', '.join(main_challenges)}")
    if avg_outcome < 60:
        next_week_focus.append("建议调整辅导策略，增加互动")
    else:
        next_week_focus.append("保持当前有效方法")

    return {
        "total_sessions": total_sessions,
        "average_outcome": round(avg_outcome, 1),
        "main_challenges": main_challenges,
        "main_wins": main_wins,
        "next_week_focus": next_week_focus,
        "completion_rate": round(len(records) / 7 * 100, 1)
    }
