"""Markdown report renderer for 宝宝哭闹原因排查 Agent."""
from typing import Any, Dict, List, Optional
import json
from datetime import datetime


def format_table(headers: List[str], rows: List[List[str]],
                align: Optional[List[str]] = None) -> str:
    """格式化Markdown表格."""
    if not headers or not rows:
        return ""

    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    if align is None:
        align = ["left"] * len(headers)

    align_map = {"left": ":--", "center": ":--:", "right": "--:"}
    separator = "| " + " | ".join(
        align_map.get(a, ":--").replace("-", "-" * w)
        for a, w in zip(align, col_widths)
    ) + " |"

    header_line = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"

    data_lines = []
    for row in rows:
        line = "| " + " | ".join(
            str(cell).ljust(col_widths[i]) if a == "left"
            else str(cell).rjust(col_widths[i]) if a == "right"
            else str(cell).center(col_widths[i])
            for i, (cell, a) in enumerate(zip(row, align))
        ) + " |"
        data_lines.append(line)

    return "\n".join([header_line, separator] + data_lines)


def render_report(result: Dict[str, Any], include_charts: bool = True) -> str:
    """渲染完整报告."""
    lines: List[str] = []

    lines.append("# 宝宝哭闹原因排查报告")
    lines.append("")
    lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    lines.append("## A. 本次结论")
    lines.append("")
    for x in result.get("summary", []):
        lines.append(f"- {x}")
    lines.append("")

    lines.append("## B. 已知信息")
    lines.append("")
    for x in result.get("known_facts", []):
        lines.append(f"- {x}")
    lines.append("")

    lines.append("## C. 分析与判断")
    lines.append("")
    for x in result.get("analysis", []):
        lines.append(f"- {x}")
    lines.append("")

    lines.append("## D. 执行方案")
    lines.append("")
    lines.append("| 阶段 | 任务 | 负责人 |")
    lines.append("|:----:|:-----|:------|")
    for item in result.get("action_plan", []):
        lines.append(f"| {item.get('day', '')} | {item.get('task', '')[:40]} | {item.get('owner', '家长')} |")
    lines.append("")

    lines.append("## E. 风险与人工核验")
    lines.append("")
    for x in result.get("risk_notes", []):
        lines.append(f"- ⚠️ {x}")
    lines.append("")

    lines.append("## F. 下次追踪字段")
    lines.append("")
    for x in result.get("next_tracking_fields", []):
        lines.append(f"- [ ] {x}")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("**免责声明**: 本报告仅供参考。如有紧急情况，请立即就医。")

    return "\n".join(lines)


def export_to_json(result: Dict[str, Any], indent: int = 2) -> str:
    """导出为JSON格式."""
    return json.dumps(result, ensure_ascii=False, indent=indent)


def add_footer(report: str, disclaimer: str = "") -> str:
    """为报告添加页脚."""
    if not disclaimer:
        disclaimer = "**免责声明**: 本报告由 AI 生成，仅供参考。如有紧急情况，请立即就医。"
    return report + "\n\n---\n\n" + disclaimer
