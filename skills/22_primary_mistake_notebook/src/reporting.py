"""Markdown report renderer for 小学错题本 Agent."""
from typing import Any, Dict, List


def render_report(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# 小学错题本报告")
    lines.append("")
    lines.append("## A. 本次结论")
    for x in result.get("summary", []):
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## B. 已知信息")
    for x in result.get("known_facts", []):
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## C. 分析与判断")
    for x in result.get("analysis", []):
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## D. 执行方案")
    for item in result.get("action_plan", []):
        lines.append(f"- {item.get('day')}：{item.get('task')}｜负责人：{item.get('owner')}｜记录：{item.get('evidence_to_record')}")
    lines.append("")
    lines.append("## E. 风险与人工核验")
    for x in result.get("risk_notes", []):
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## F. 下次追踪字段")
    for x in result.get("next_tracking_fields", []):
        lines.append(f"- {x}")
    return "\n".join(lines)
