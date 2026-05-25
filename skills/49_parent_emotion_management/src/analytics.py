"""Data analytics module for 父母情绪管理 Agent."""
from typing import Any, Dict, List
from collections import Counter, defaultdict


def analyze_emotion_patterns(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析情绪模式"""
    result = {"emotion_distribution": {}, "trigger_analysis": {}, "avg_intensity": 0, "effective_strategies": []}
    if not records:
        return result
    emotion_counter = Counter()
    trigger_counter = Counter()
    intensities = []
    strategy_effectiveness = defaultdict(list)
    for record in records:
        emotion = record.get("emotion_type", "unknown")
        emotion_counter[emotion] += 1
        trigger = record.get("trigger", "")
        if trigger:
            trigger_counter[trigger] += 1
        intensity = record.get("intensity", 5)
        intensities.append(intensity)
        for strategy in record.get("coping_used", []):
            effectiveness = record.get("effectiveness", 3)
            strategy_effectiveness[strategy].append(effectiveness)
    result["emotion_distribution"] = dict(emotion_counter)
    result["trigger_analysis"] = dict(trigger_counter.most_common(5))
    if intensities:
        result["avg_intensity"] = sum(intensities) / len(intensities)
    for strategy, scores in strategy_effectiveness.items():
        if scores and sum(scores) / len(scores) >= 4:
            result["effective_strategies"].append(strategy)
    return result


def aggregate_statistics(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """数据聚合统计"""
    stats = {"total_records": len(records), "avg_intensity": 0, "dominant_emotion": "", "effective_strategies": []}
    if not records:
        return stats
    emotion_counter = Counter()
    intensities = []
    for record in records:
        emotion_counter[record.get("emotion_type", "unknown")] += 1
        intensities.append(record.get("intensity", 5))
    if intensities:
        stats["avg_intensity"] = sum(intensities) / len(intensities)
    if emotion_counter:
        stats["dominant_emotion"] = emotion_counter.most_common(1)[0][0]
    strategy_effectiveness = defaultdict(list)
    for record in records:
        for strategy in record.get("coping_used", []):
            strategy_effectiveness[strategy].append(record.get("effectiveness", 3))
    for strategy, scores in strategy_effectiveness.items():
        if scores and sum(scores) / len(scores) >= 4:
            stats["effective_strategies"].append(strategy)
    return stats


class ContextMemory:
    """上下文记忆类"""
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.emotion_history: List[Dict[str, Any]] = []
        self.common_triggers: List[str] = []
        self.effective_strategies: List[str] = []

    def add_record(self, record: Dict[str, Any]) -> None:
        self.emotion_history.append(record)
        if len(self.emotion_history) > self.max_history:
            self.emotion_history.pop(0)

    def learn_from_history(self) -> Dict[str, Any]:
        if not self.emotion_history:
            return {}
        patterns = analyze_emotion_patterns(self.emotion_history)
        self.common_triggers = [t for t in patterns.get("trigger_analysis", {}).keys()]
        self.effective_strategies = patterns.get("effective_strategies", [])
        return {"patterns": patterns, "total_records": len(self.emotion_history)}

    def get_context_summary(self) -> str:
        if not self.emotion_history:
            return "暂无情绪记录"
        return f"累计记录 {len(self.emotion_history)} 次情绪变化"