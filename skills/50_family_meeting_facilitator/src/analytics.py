"""Data analytics module for 家庭会议主持 Agent."""
from typing import Any, Dict, List
from collections import Counter, defaultdict


def analyze_meeting_patterns(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析会议模式"""
    result = {"meeting_types": {}, "participant_analysis": {}, "decision_rate": 0, "action_completion": 0}
    if not records:
        return result
    type_counter = Counter()
    participant_counter = Counter()
    total_decisions = 0
    decided_count = 0
    total_actions = 0
    completed_actions = 0
    for record in records:
        meeting_type = record.get("meeting_type", "unknown")
        type_counter[meeting_type] += 1
        for participant in record.get("participants", []):
            if isinstance(participant, dict):
                name = participant.get("name", "unknown")
            else:
                name = str(participant)
            participant_counter[name] += 1
        decisions = record.get("decisions", [])
        total_decisions += len(decisions)
        decided_count += sum(1 for d in decisions if d.get("status") == "decided")
        actions = record.get("action_items", [])
        total_actions += len(actions)
        completed_actions += sum(1 for a in actions if a.get("status") == "completed")
    result["meeting_types"] = dict(type_counter)
    result["participant_analysis"] = dict(participant_counter.most_common(5))
    result["decision_rate"] = decided_count / total_decisions if total_decisions > 0 else 0
    result["action_completion"] = completed_actions / total_actions if total_actions > 0 else 0
    return result


def aggregate_statistics(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """数据聚合统计"""
    stats = {"total_meetings": len(records), "total_decisions": 0, "pending_decisions": 0, "participation_rate": 0}
    if not records:
        return stats
    total_participants = 0
    attended_participants = 0
    for record in records:
        decisions = record.get("decisions", [])
        stats["total_decisions"] += len(decisions)
        stats["pending_decisions"] += sum(1 for d in decisions if d.get("status") == "pending")
        for participant in record.get("participants", []):
            total_participants += 1
            if isinstance(participant, dict):
                if participant.get("attendance", True):
                    attended_participants += 1
            else:
                attended_participants += 1
    stats["participation_rate"] = attended_participants / total_participants if total_participants > 0 else 0
    return stats


class ContextMemory:
    """上下文记忆类"""
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.meeting_history: List[Dict[str, Any]] = []
        self.common_issues: List[str] = []
        self.pending_decisions: List[str] = []

    def add_record(self, record: Dict[str, Any]) -> None:
        self.meeting_history.append(record)
        if len(self.meeting_history) > self.max_history:
            self.meeting_history.pop(0)

    def learn_from_history(self) -> Dict[str, Any]:
        if not self.meeting_history:
            return {}
        patterns = analyze_meeting_patterns(self.meeting_history)
        for record in self.meeting_history:
            for decision in record.get("decisions", []):
                if decision.get("status") == "pending":
                    self.pending_decisions.append(decision.get("topic", ""))
        return {"patterns": patterns, "total_meetings": len(self.meeting_history), "pending_count": len(self.pending_decisions)}

    def get_context_summary(self) -> str:
        if not self.meeting_history:
            return "暂无会议记录"
        return f"累计主持 {len(self.meeting_history)} 次会议，{len(self.pending_decisions)} 项待处理决议"