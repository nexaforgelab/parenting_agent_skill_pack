"""家长辅导话术 Agent - 报告生成器

增强版本：添加Markdown表格美化、可视化、摘要生成、多格式导出支持
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from collections import defaultdict
import json


def render_report(result: Dict[str, Any]) -> str:
    """渲染完整报告

    Args:
        result: 结果字典

    Returns:
        Markdown格式的报告字符串
    """
    lines: List[str] = []
    lines.append("# 📚 家长辅导话术建议报告")
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

    if result.get("recommended_phrases"):
        lines.append("## D. 推荐话术")
        lines.append("")
        lines.extend(render_phrases_table(result.get("recommended_phrases", [])))
        lines.append("")

    if result.get("tutoring_tips"):
        lines.append("## E. 个性化辅导建议")
        lines.append("")
        for tip in result.get("tutoring_tips", []):
            lines.append(f"- {tip}")
        lines.append("")

    if result.get("communication_analysis"):
        lines.append("## F. 沟通风格分析")
        lines.append("")
        lines.extend(render_communication_analysis(result.get("communication_analysis", {})))
        lines.append("")

    lines.append("## G. 执行方案")
    for item in result.get("action_plan", []):
        lines.append(f"- [{item.get('step', '')}] {item.get('task', '')}｜负责人：{item.get('owner', '')}")
    lines.append("")

    if result.get("session_recommendations"):
        lines.append("## H. 辅导阶段建议")
        lines.append("")
        lines.extend(render_session_recommendations(result.get("session_recommendations", [])))
        lines.append("")

    lines.append("## I. 话术类别参考")
    lines.append("")
    lines.extend(render_phrase_categories())
    lines.append("")

    lines.append("## J. 风险与注意事项")
    for x in result.get("risk_notes", []):
        lines.append(f"- {x}")
    lines.append("")

    lines.append("## K. 下次追踪字段")
    for x in result.get("next_tracking_fields", []):
        lines.append(f"- {x}")
    lines.append("")

    return "\n".join(lines)


def render_phrases_table(phrases: List[Dict[str, Any]]) -> List[str]:
    """渲染话术推荐表格

    Args:
        phrases: 话术列表

    Returns:
        Markdown表格行列表
    """
    lines = []

    if not phrases:
        return ["暂无推荐话术"]

    header = "| 优先级 | 话术类别 | 推荐话术 | 使用场景 | 匹配度 |"
    separator = "|------|---------|---------|---------|------|"
    lines.append(header)
    lines.append(separator)

    for i, phrase_data in enumerate(phrases, 1):
        phrase = phrase_data.get("phrase", {})
        category_cn = {
            "encouragement": "鼓励类",
            "guidance": "引导类",
            "comfort": "安慰类",
            "questioning": "提问类",
            "praise": "表扬类",
            "limit_setting": "边界设置类",
            "emotion_coaching": "情绪引导类",
            "error_handling": "错误处理类"
        }.get(phrase.get("category", ""), phrase.get("category", ""))

        phrase_text = phrase.get("phrase_text", "")[:50] + "..." if len(phrase.get("phrase_text", "")) > 50 else phrase.get("phrase_text", "")
        example = phrase.get("example_usage", "")[:30] + "..." if len(phrase.get("example_usage", "")) > 30 else phrase.get("example_usage", "")
        score = phrase_data.get("match_score", 0)

        priority = "🔴" if i == 1 else "🟡" if i == 2 else "🟢"

        line = f"| {priority} | {category_cn} | {phrase_text} | {example} | {score:.1%} |"
        lines.append(line)

    return lines


def render_communication_analysis(analysis: Dict[str, Any]) -> List[str]:
    """渲染沟通风格分析

    Args:
        analysis: 分析结果字典

    Returns:
        Markdown行列表
    """
    lines = []

    dominant = analysis.get("dominant_style", "unknown")
    balance = analysis.get("balance_score", 0)

    style_cn = {
        "encouragement": "鼓励型",
        "guidance": "引导型",
        "comfort": "安慰型",
        "questioning": "提问型",
        "praise": "表扬型",
        "emotion_coaching": "情绪引导型",
        "unknown": "待观察"
    }.get(dominant, dominant)

    lines.append(f"**主导风格**: {style_cn}")
    lines.append(f"**话术平衡度**: {balance:.0%} (越高表示越均衡)")
    lines.append("")

    if analysis.get("strengths"):
        lines.append("**✅ 沟通优势**:")
        for s in analysis["strengths"]:
            lines.append(f"  - {s}")
        lines.append("")

    if analysis.get("areas_for_improvement"):
        lines.append("**📝 改进建议**:")
        for imp in analysis["areas_for_improvement"]:
            lines.append(f"  - {imp}")
        lines.append("")

    distribution = analysis.get("category_distribution", {})
    if distribution:
        lines.append("**📊 话术分布**:")
        lines.append("")
        max_count = max(distribution.values()) if distribution else 1
        for cat, pct in sorted(distribution.items(), key=lambda x: x[1], reverse=True):
            cat_cn = {
                "encouragement": "鼓励",
                "guidance": "引导",
                "comfort": "安慰",
                "questioning": "提问",
                "praise": "表扬",
                "limit_setting": "边界设置",
                "emotion_coaching": "情绪引导",
                "error_handling": "错误处理"
            }.get(cat, cat)
            bar_len = int(pct / 100 * 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            lines.append(f"  {cat_cn:8s} │ {bar} │ {pct:5.1f}%")
        lines.append("")

    return lines


def render_session_recommendations(recommendations: List[Dict[str, Any]]) -> List[str]:
    """渲染辅导阶段建议

    Args:
        recommendations: 建议列表

    Returns:
        Markdown行列表
    """
    lines = []

    phase_icons = {
        "辅导前": "🟢",
        "辅导中": "🟡",
        "辅导后": "🔵"
    }

    for rec in recommendations:
        phase = rec.get("phase", "")
        icon = phase_icons.get(phase, "⚪")
        lines.append(f"### {icon} {phase}")
        lines.append(f"**行动**: {rec.get('action', '')}")
        lines.append(f"**话术提示**: {rec.get('phrase_tip', '')}")
        lines.append("")

    return lines


def render_phrase_categories() -> List[str]:
    """渲染话术类别参考

    Returns:
        Markdown行列表
    """
    lines = []

    categories = [
        ("encouragement", "鼓励类", "肯定努力、给予信心", ["没关系，慢慢来", "你已经做得很好了"]),
        ("guidance", "引导类", "启发思考、引导探索", ["你觉得呢", "让我们一起看看"]),
        ("comfort", "安慰类", "共情理解、情绪安抚", ["妈妈理解你的感受", "没关系，我们休息一下"]),
        ("questioning", "提问类", "激发思考、培养独立", ["为什么", "你是怎么想的"]),
        ("praise", "表扬类", "肯定成果、强化行为", ["太棒了", "这个方法真不错"]),
        ("limit_setting", "边界设置类", "设定规则、保持底线", ["我们需要先...然后...", "规则是..."]),
        ("emotion_coaching", "情绪引导类", "识别情绪、管理情绪", ["你现在感觉怎么样", "深呼吸"]),
        ("error_handling", "错误处理类", "接纳错误、从中学习", ["错题是最好的老师", "我们来一起看看哪里不同"])
    ]

    header = "| 类别 | 描述 | 示例话术 |"
    separator = "|------|------|---------|"
    lines.append(header)
    lines.append(separator)

    for cat_id, cat_name, desc, examples in categories:
        ex_text = "、".join(examples[:2])
        lines.append(f"| {cat_name} | {desc} | {ex_text} |")

    return lines


def render_trend_chart_ascii(data_points: List[float], width: int = 40, height: int = 10) -> str:
    """渲染ASCII趋势图表

    Args:
        data_points: 数据点列表
        width: 图表宽度
        height: 图表高度

    Returns:
        ASCII图表字符串
    """
    if not data_points or len(data_points) < 2:
        return "数据点不足，无法生成图表"

    min_val = min(data_points)
    max_val = max(data_points)
    val_range = max_val - min_val

    if val_range == 0:
        val_range = 1

    chart = []
    chart.append("📈 趋势变化:")
    chart.append("")

    rows = []
    for i in range(height):
        row = [" "] * width
        rows.append(row)

    for i, val in enumerate(data_points):
        x = int((i / (len(data_points) - 1)) * (width - 1))
        normalized = (val - min_val) / val_range
        y = height - 1 - int(normalized * (height - 1))
        rows[y][x] = "█"

        if i > 0:
            prev_normalized = (data_points[i-1] - min_val) / val_range
            prev_y = height - 1 - int(prev_normalized * (height - 1))
            if prev_y != y:
                step = 1 if y < prev_y else -1
                for step_y in range(prev_y, y, step):
                    if rows[step_y][x] == " ":
                        rows[step_y][x] = "│"
            else:
                prev_x = int((i-1) / (len(data_points) - 1) * (width - 1))
                for step_x in range(min(x, prev_x), max(x, prev_x)):
                    if rows[y][step_x] == " ":
                        rows[y][step_x] = "─"

    for row in rows:
        chart.append("│" + "".join(row) + "│")

    chart.append("└" + "─" * width + "┘")
    chart.append("")
    chart.append(f"最小值: {min_val:.1f}  |  最大值: {max_val:.1f}  |  平均: {sum(data_points)/len(data_points):.1f}")

    return "\n".join(chart)


def generate_summary_text(result: Dict[str, Any]) -> str:
    """生成摘要文本

    Args:
        result: 结果字典

    Returns:
        摘要文本
    """
    lines = []

    summary = result.get("summary", [])
    if summary:
        lines.append("📋 核心结论:")
        for point in summary[:3]:
            lines.append(f"  • {point}")
        lines.append("")

    phrases = result.get("recommended_phrases", [])
    if phrases:
        top_phrase = phrases[0].get("phrase", {})
        lines.append(f"💡 首要推荐话术:")
        lines.append(f"  \"{top_phrase.get('phrase_text', '')}\"")
        lines.append("")

    tips = result.get("tutoring_tips", [])
    if tips:
        lines.append("🎯 关键建议:")
        for tip in tips[:2]:
            lines.append(f"  • {tip}")

    return "\n".join(lines)


def export_to_json(result: Dict[str, Any], indent: int = 2) -> str:
    """导出为JSON格式

    Args:
        result: 结果字典
        indent: 缩进空格数

    Returns:
        JSON字符串
    """
    return json.dumps(result, ensure_ascii=False, indent=indent, default=str)


def export_to_csv_summary(result: Dict[str, Any]) -> str:
    """导出为CSV摘要格式

    Args:
        result: 结果字典

    Returns:
        CSV字符串
    """
    lines = []
    lines.append("类别,项目,内容")

    for fact in result.get("known_facts", []):
        lines.append(f"已知信息,{fact},")

    for phrase_data in result.get("recommended_phrases", []):
        phrase = phrase_data.get("phrase", {})
        lines.append(f"推荐话术,{phrase.get('category', '')},{phrase.get('phrase_text', '')}")

    for tip in result.get("tutoring_tips", []):
        lines.append(f"辅导建议,,{tip}")

    return "\n".join(lines)


def export_to_html(result: Dict[str, Any]) -> str:
    """导出为HTML格式

    Args:
        result: 结果字典

    Returns:
        HTML字符串
    """
    lines = []
    lines.append("<!DOCTYPE html>")
    lines.append("<html lang='zh-CN'>")
    lines.append("<head>")
    lines.append("    <meta charset='UTF-8'>")
    lines.append("    <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    lines.append("    <title>家长辅导话术报告</title>")
    lines.append("    <style>")
    lines.append("        body { font-family: 'Microsoft YaHei', Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }")
    lines.append("        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }")
    lines.append("        h2 { color: #34495e; margin-top: 30px; }")
    lines.append("        .phrase { background-color: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #3498db; }")
    lines.append("        .tip { background-color: #e8f5e9; padding: 10px; margin: 5px 0; border-radius: 5px; }")
    lines.append("        table { width: 100%; border-collapse: collapse; margin: 15px 0; }")
    lines.append("        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
    lines.append("        th { background-color: #3498db; color: white; }")
    lines.append("    </style>")
    lines.append("</head>")
    lines.append("<body>")
    lines.append("    <h1>📚 家长辅导话术建议报告</h1>")

    if result.get("summary"):
        lines.append("    <h2>📋 本次结论</h2>")
        lines.append("    <ul>")
        for item in result.get("summary", []):
            lines.append(f"        <li>{item}</li>")
        lines.append("    </ul>")

    if result.get("recommended_phrases"):
        lines.append("    <h2>💬 推荐话术</h2>")
        for phrase_data in result.get("recommended_phrases", []):
            phrase = phrase_data.get("phrase", {})
            lines.append(f"    <div class='phrase'>")
            lines.append(f"        <strong>{phrase.get('phrase_text', '')}</strong>")
            lines.append(f"        <p><em>使用场景:</em> {phrase.get('example_usage', '')}</p>")
            lines.append(f"    </div>")

    if result.get("tutoring_tips"):
        lines.append("    <h2>🎯 辅导建议</h2>")
        for tip in result.get("tutoring_tips", []):
            lines.append(f"    <div class='tip'>{tip}</div>")

    lines.append("</body>")
    lines.append("</html>")

    return "\n".join(lines)


def format_markdown_table(headers: List[str], rows: List[List[Any]]) -> List[str]:
    """格式化Markdown表格

    Args:
        headers: 表头列表
        rows: 行数据列表

    Returns:
        Markdown表格行列表
    """
    lines = []

    header_line = "| " + " | ".join(str(h) for h in headers) + " |"
    separator = "|" + "|".join("---" for _ in headers) + "|"

    lines.append(header_line)
    lines.append(separator)

    for row in rows:
        row_line = "| " + " | ".join(str(cell) for cell in row) + " |"
        lines.append(row_line)

    return lines
