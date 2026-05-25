"""青春期亲子沟通 Agent - 报告生成器"""
from __future__ import annotations
from typing import Any, Dict, List
from datetime import datetime
import json


def render_report(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# 💬 青春期亲子沟通报告")
    lines.append("")
    lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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
        lines.append(f"{x}")
    lines.append("")

    if result.get("communication_tips"):
        lines.append("## D. 沟通建议")
        lines.append("")
        for tip in result.get("communication_tips", []):
            lines.append(f"- {tip}")
        lines.append("")

    if result.get("recommended_phrases"):
        lines.append("## E. 推荐话术")
        lines.append("")
        for phrase in result.get("recommended_phrases", []):
            lines.append(f"- \"{phrase}\"")
        lines.append("")

    lines.append("## F. 执行方案")
    for item in result.get("action_plan", []):
        lines.append(f"- [{item.get('day', '')}] {item.get('task', '')}")
    lines.append("")

    lines.append("## G. 风险与注意事项")
    for x in result.get("risk_notes", []):
        lines.append(f"- {x}")
    lines.append("")

    lines.append("## H. 下次追踪字段")
    for x in result.get("next_tracking_fields", []):
        lines.append(f"- {x}")
    lines.append("")

    return "\n".join(lines)


def export_to_json(result: Dict[str, Any], indent: int = 2) -> str:
    return json.dumps(result, ensure_ascii=False, indent=indent, default=str)


def export_to_html(result: Dict[str, Any]) -> str:
    lines = []
    lines.append("<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'><title>青春期亲子沟通报告</title></head><body><h1>💬 青春期亲子沟通报告</h1></body></html>")
    return "\n".join(lines)


def format_markdown_table(headers: List[str], rows: List[List[Any]]) -> List[str]:
    lines = []
    header_line = "| " + " | ".join(str(h) for h in headers) + " |"
    separator = "|" + "|".join("---" for _ in headers) + "|"
    lines.append(header_line)
    lines.append(separator)
    for row in rows:
        row_line = "| " + " | ".join(str(cell) for cell in row) + " |"
        lines.append(row_line)
    return lines
