"""Markdown report renderer for 宝宝体检记录管理 Agent.

提供美化的Markdown表格、趋势可视化（ASCII art）、摘要生成和多格式导出功能。
"""
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


def create_progress_bar(value: float, max_value: float = 100,
                       width: int = 20, filled_char: str = "█",
                       empty_char: str = "░") -> str:
    """创建ASCII进度条."""
    percentage = min(value / max_value, 1.0) if max_value > 0 else 0
    filled = int(width * percentage)
    empty = width - filled
    bar = filled_char * filled + empty_char * empty
    return f"[{bar}] {percentage * 100:.1f}%"


def create_growth_chart(heights: List[float], weights: List[float],
                       dates: List[str], height_width: int = 20) -> str:
    """创建生长曲线图表."""
    lines = []

    if heights:
        lines.append("**身高趋势**")
        min_h, max_h = min(heights), max(heights)
        range_h = max_h - min_h if max_h != min_h else 1
        for i, (h, d) in enumerate(zip(heights, dates)):
            normalized = (h - min_h) / range_h
            bar_len = int(normalized * height_width)
            lines.append(f"{d}: {'█' * bar_len}{'░' * (height_width - bar_len)} {h:.1f}cm")

    if weights:
        lines.append("\n**体重趋势**")
        min_w, max_w = min(weights), max(weights)
        range_w = max_w - min_w if max_w != min_w else 1
        for i, (w, d) in enumerate(zip(weights, dates)):
            normalized = (w - min_w) / range_w
            bar_len = int(normalized * height_width)
            lines.append(f"{d}: {'█' * bar_len}{'░' * (height_width - bar_len)} {w:.1f}kg")

    return "\n".join(lines) if lines else "暂无数据"


def render_report(result: Dict[str, Any], include_charts: bool = True) -> str:
    """渲染完整报告."""
    lines: List[str] = []

    lines.append("# 宝宝体检记录管理报告")
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

    if include_charts and "deliverables" in result:
        deliverables = result["deliverables"]
        if "growth_analysis" in deliverables:
            lines.append("### 📊 生长数据分析")
            lines.append("")
            analysis = deliverables["growth_analysis"]
            if "avg_height" in analysis:
                lines.append(f"- 平均身高：{analysis['avg_height']} cm")
            if "avg_weight" in analysis:
                lines.append(f"- 平均体重：{analysis['avg_weight']} kg")
            lines.append("")

    lines.append("## D. 执行方案")
    lines.append("")
    lines.append("| 阶段 | 任务 | 负责人 | 难度 |")
    lines.append("|:----:|:-----|:------|:----:|")
    for item in result.get("action_plan", []):
        lines.append(f"| {item.get('day', '')} | {item.get('task', '')[:40]} | {item.get('owner', '家长')} | {item.get('difficulty', '低')} |")
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
    lines.append("**免责声明**: 本报告仅供参考，不构成医疗建议。如有疑虑，请咨询专业儿科医生。")

    return "\n".join(lines)


def render_compact_report(result: Dict[str, Any]) -> str:
    """渲染精简报告."""
    lines: List[str] = []
    lines.append("## 宝宝体检记录管理")
    lines.append("")
    lines.append("### 摘要")
    for x in result.get("summary", [])[:3]:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("### 行动计划")
    for item in result.get("action_plan", [])[:3]:
        lines.append(f"- [{item.get('day', 'D0')}] {item.get('task', '')[:50]}")
    return "\n".join(lines)


def export_to_json(result: Dict[str, Any], indent: int = 2) -> str:
    """导出为JSON格式."""
    return json.dumps(result, ensure_ascii=False, indent=indent)


def export_to_csv(result: Dict[str, Any]) -> str:
    """导出为CSV格式."""
    lines: List[str] = []
    lines.append("日期,月龄,身高(cm),体重(kg),头围(cm),备注")
    if "deliverables" in result and "growth_records" in result["deliverables"]:
        for record in result["deliverables"]["growth_records"]:
            lines.append(f"{record.get('date', '')},{record.get('age_months', '')},{record.get('height_cm', '')},{record.get('weight_kg', '')},{record.get('head_circumference_cm', '')},{record.get('notes', '')}")
    return "\n".join(lines)


def add_footer(report: str, disclaimer: str = "") -> str:
    """为报告添加页脚."""
    if not disclaimer:
        disclaimer = ("**免责声明**: 本报告由 AI 生成，仅供参考。\n"
                    "不构成医疗建议、诊断或治疗方案。\n"
                    "如有健康疑虑，请及时咨询专业儿科医生。")
    return report + "\n\n---\n\n" + disclaimer
