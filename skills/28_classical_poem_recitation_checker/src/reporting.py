"""Markdown report renderer for 古诗背诵检查 Agent.

提供增强的报告渲染功能，包括Markdown表格美化、学习进度可视化、摘要生成和多格式导出支持。
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
import json


class TableFormatter:
    """表格格式化器"""

    @staticmethod
    def format_table(headers: List[str], rows: List[List[str]], align: Optional[List[str]] = None) -> str:
        """格式化表格"""
        if not headers or not rows:
            return ""

        if align is None:
            align = ['left'] * len(headers)

        lines = []
        header_line = "| " + " | ".join(headers) + " |"
        lines.append(header_line)

        separator_parts = []
        for i, header in enumerate(headers):
            alignment = align[i] if i < len(align) else 'left'
            if alignment == 'center':
                separator_parts.append(":-:")
            elif alignment == 'right':
                separator_parts.append("-:")
            else:
                separator_parts.append(":-")
        separator_line = "| " + " | ".join(separator_parts) + " |"
        lines.append(separator_line)

        for row in rows:
            row_line = "| " + " | ".join(str(cell) for cell in row) + " |"
            lines.append(row_line)

        return "\n".join(lines)

    @staticmethod
    def format_progress_bar(value: float, max_value: float = 1.0, width: int = 20, prefix: str = "", suffix: str = "") -> str:
        """格式化进度条"""
        percentage = min(value / max_value, 1.0)
        filled = int(width * percentage)
        empty = width - filled
        bar = "█" * filled + "░" * empty
        return f"{prefix}{bar}{suffix} {value*100:.0f}%"


class ProgressVisualizer:
    """进度可视化器"""

    @staticmethod
    def format_trend_indicator(trend: str) -> str:
        """格式化趋势指示器"""
        indicators = {
            "improving": "📈 上升",
            "declining": "📉 下降",
            "stable": "➡️ 稳定",
            "insufficient_data": "⏳ 数据不足"
        }
        return indicators.get(trend, trend)

    @staticmethod
    def format_mastery_badge(level: str) -> str:
        """格式化掌握程度徽章"""
        badges = {
            "MASTERED": "🟢 已掌握",
            "FAMILIAR": "🟡 熟悉",
            "LEARNING": "🟠学习中",
            "NOT_STARTED": "⚪ 未开始"
        }
        return badges.get(level, level)

    @staticmethod
    def generate_progress_summary(progress: Dict[str, Any]) -> List[str]:
        """生成进度摘要"""
        summary = []
        summary.append(f"总练习次数：{progress.get('total_sessions', 0)} 次")
        summary.append(f"背诵古诗数：{progress.get('total_poems', 0)} 首")
        summary.append(f"平均准确率：{progress.get('average_accuracy', 0.0)*100:.1f}%")
        summary.append(f"趋势：{ProgressVisualizer.format_trend_indicator(progress.get('recent_trend', 'insufficient_data'))}")
        return summary

    @staticmethod
    def generate_difficulty_list(difficulties: List[Dict[str, Any]]) -> List[str]:
        """生成困难列表"""
        result = []
        severity_emojis = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }
        for diff in difficulties:
            severity = diff.get("severity", "medium")
            emoji = severity_emojis.get(severity, "🟡")
            result.append(f"{emoji} {diff.get('message', '')}")
        return result


class SummaryGenerator:
    """摘要生成器"""

    @staticmethod
    def generate_executive_summary(result: Dict[str, Any]) -> str:
        """生成执行摘要"""
        lines = []
        lines.append("**核心发现**")
        lines.append("")

        if result.get("summary"):
            for item in result["summary"]:
                lines.append(f"- {item}")

        lines.append("")

        progress = result.get("progress", {})
        if progress:
            lines.append(f"**学习进度**: 完成 {progress.get('total_sessions', 0)} 次练习")
            lines.append(f"**平均准确率**: {progress.get('average_accuracy', 0.0)*100:.1f}%")

        difficulties = result.get("difficulties", [])
        if difficulties:
            lines.append("")
            lines.append(f"**发现 {len(difficulties)} 个需要关注的问题**")

        return "\n".join(lines)

    @staticmethod
    def generate_recommendations_summary(recommendations: List[Dict[str, Any]]) -> str:
        """生成推荐摘要"""
        if not recommendations:
            return "暂无推荐"

        lines = []
        lines.append("**个性化建议**")
        lines.append("")

        high_priority = [r for r in recommendations if r.get("priority") == "high"]
        if high_priority:
            lines.append("🔴 **高优先级建议**")
            for rec in high_priority[:2]:
                lines.append(f"- **{rec.get('title', '')}**: {rec.get('description', '')}")
            lines.append("")

        return "\n".join(lines)


class ExportFormatter:
    """导出格式化器"""

    @staticmethod
    def to_json(data: Dict[str, Any], pretty: bool = True) -> str:
        """导出为JSON格式"""
        if pretty:
            return json.dumps(data, ensure_ascii=False, indent=2)
        return json.dumps(data, ensure_ascii=False)

    @staticmethod
    def to_csv(data: List[Dict[str, Any]], columns: Optional[List[str]] = None) -> str:
        """导出为CSV格式"""
        if not data:
            return ""

        if columns is None:
            columns = list(data[0].keys())

        lines = []
        lines.append(",".join(columns))
        for row in data:
            values = [str(row.get(col, "")) for col in columns]
            lines.append(",".join(values))

        return "\n".join(lines)

    @staticmethod
    def to_html_table(data: List[Dict[str, Any]], columns: Optional[List[str]] = None) -> str:
        """导出为HTML表格"""
        if not data:
            return "<table><tr><td>无数据</td></tr></table>"

        if columns is None:
            columns = list(data[0].keys())

        lines = ['<table border="1">']
        lines.append("<thead><tr>")
        for col in columns:
            lines.append(f"<th>{col}</th>")
        lines.append("</tr></thead>")
        lines.append("<tbody>")
        for row in data:
            lines.append("<tr>")
            for col in columns:
                lines.append(f"<td>{row.get(col, '')}</td>")
            lines.append("</tr>")
        lines.append("</tbody>")
        lines.append("</table>")

        return "\n".join(lines)


def render_report(result: Dict[str, Any]) -> str:
    """渲染完整报告"""
    lines = []

    lines.append("# 古诗背诵检查报告")
    lines.append("")
    lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    lines.append("## 📋 执行摘要")
    lines.append("")
    summary_gen = SummaryGenerator()
    lines.append(summary_gen.generate_executive_summary(result))
    lines.append("")

    lines.append("## A. 本次结论")
    for x in result.get("summary", []):
        lines.append(f"- {x}")
    lines.append("")

    lines.append("## B. 已知信息")
    for x in result.get("known_facts", []):
        lines.append(f"- {x}")
    lines.append("")

    lines.append("## C. 学习进度")
    progress = result.get("progress", {})
    if progress:
        lines.append("")
        lines.append("### 进度概览")
        lines.append("")

        summary_items = ProgressVisualizer.generate_progress_summary(progress)
        for item in summary_items:
            lines.append(f"- {item}")

        if progress.get("difficulty_distribution"):
            lines.append("")
            lines.append(f"**难度分布**: {progress['difficulty_distribution']}")

    difficulties = result.get("difficulties", [])
    if difficulties:
        lines.append("")
        lines.append("### ⚠️ 需要关注的问题")
        lines.append("")
        difficulty_items = ProgressVisualizer.generate_difficulty_list(difficulties)
        for item in difficulty_items:
            lines.append(f"- {item}")
        lines.append("")
        lines.append("**改进建议**:")
        for diff in difficulties:
            lines.append(f"  - {diff.get('suggestion', '')}")
    lines.append("")

    recommendations = result.get("recommendations", [])
    if recommendations:
        lines.append("### 💡 个性化建议")
        lines.append("")
        lines.append(summary_gen.generate_recommendations_summary(recommendations))
        lines.append("")

        high_recs = [r for r in recommendations if r.get("priority") == "high"]
        if high_recs:
            lines.append("#### 高优先级行动计划")
            lines.append("")
            for rec in high_recs[:2]:
                lines.append(f"**{rec.get('title', '')}**")
                lines.append(f"{rec.get('description', '')}")
                lines.append("")
                lines.append("具体行动:")
                for action in rec.get("action_items", []):
                    lines.append(f"- [ ] {action}")
                lines.append("")

    learning_curve = result.get("learning_curve", {})
    if learning_curve and learning_curve.get("curve_type") != "insufficient_data":
        lines.append("### 📈 学习曲线分析")
        lines.append("")
        lines.append(f"- 曲线类型: {ProgressVisualizer.format_trend_indicator(learning_curve.get('curve_type', ''))}")
        lines.append(f"- 预测: {learning_curve.get('prediction', '')}")
        lines.append(f"- 斜率: {learning_curve.get('slope', 0):.4f}")
        lines.append("")

    mastery_level = result.get("mastery_level", "NOT_STARTED")
    lines.append("### 🎯 掌握程度")
    lines.append("")
    lines.append(f"当前掌握程度: {ProgressVisualizer.format_mastery_badge(mastery_level)}")
    lines.append("")

    lines.append("## D. 分析与判断")
    for x in result.get("analysis", []):
        lines.append(f"- {x}")
    lines.append("")

    lines.append("## E. 执行方案")
    for item in result.get("action_plan", []):
        if isinstance(item, dict):
            lines.append(f"- {item.get('day', '')}：{item.get('task', '')}｜负责人：{item.get('owner', '')}｜记录：{item.get('evidence_to_record', '')}")
        else:
            lines.append(f"- {item}")
    lines.append("")

    lines.append("## F. 风险与人工核验")
    for x in result.get("risk_notes", []):
        lines.append(f"- {x}")
    lines.append("")

    lines.append("## G. 下次追踪字段")
    for x in result.get("next_tracking_fields", []):
        lines.append(f"- {x}")
    lines.append("")

    return "\n".join(lines)


def export_report(result: Dict[str, Any], format: str = "markdown") -> str:
    """导出报告"""
    if format == "json":
        return ExportFormatter.to_json(result)
    elif format == "html":
        records = result.get("raw_records", [])
        return ExportFormatter.to_html_table(records)
    elif format == "csv":
        records = result.get("raw_records", [])
        columns = ["timestamp", "poem_title", "poet", "accuracy_rate", "error_count"]
        return ExportFormatter.to_csv(records, columns)
    else:
        return render_report(result)
