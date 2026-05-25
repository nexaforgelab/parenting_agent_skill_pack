"""Entrypoint for 兴趣班选择 Agent.

增强版本：增强run()函数输出结果，支持多种导出格式
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict
from datetime import datetime

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

try:
    from .validators import require_payload, validate_child_profile, validate_batch_classes
    from .planner import (
        build_action_plan, build_analysis, build_deliverables,
        build_known_facts, next_fields, compare_classes,
        detect_class_anomalies, generate_class_recommendations
    )
    from .reporting import render_report, export_to_json, export_to_html, export_to_csv_summary
except ImportError:
    from validators import require_payload, validate_child_profile, validate_batch_classes
    from planner import (
        build_action_plan, build_analysis, build_deliverables,
        build_known_facts, next_fields, compare_classes,
        detect_class_anomalies, generate_class_recommendations
    )
    from reporting import render_report, export_to_json, export_to_html, export_to_csv_summary

SKILL_ID = "extracurricular_class_selection"
SKILL_NAME = "兴趣班选择 Agent"
RISK_NOTES = [
    '本 Skill 提供家庭教育和生活管理建议，不替代专业人士意见。',
    '涉及安全、法律、医疗、财务或教育政策时，应提示家长二次核验。',
    '输出应尊重家庭差异，不用单一标准评价孩子或父母。',
    '兴趣班选择建议仅供参考，最终决定需结合孩子意愿。',
    '建议关注孩子兴趣，避免过度安排。'
]


def run(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Run the skill once and return a structured report."""
    errors = require_payload(payload)
    if errors:
        return {
            "skill_id": SKILL_ID,
            "skill_name": SKILL_NAME,
            "summary": ["输入不完整，无法生成完整闭环。"],
            "known_facts": [],
            "analysis": [f"验证错误：{err}" for err in errors],
            "action_plan": [],
            "deliverables": {},
            "risk_notes": RISK_NOTES,
            "next_tracking_fields": ["child_profile", "current_problem"],
            "markdown_report": "输入不完整：" + "；".join(errors),
            "validation_errors": errors,
            "success": False,
            "timestamp": datetime.now().isoformat()
        }

    child_profile = payload.get("child_profile", {})
    profile_errors = validate_child_profile(child_profile)
    if profile_errors:
        return {
            "skill_id": SKILL_ID,
            "skill_name": SKILL_NAME,
            "summary": ["孩子画像验证失败。"],
            "known_facts": [],
            "analysis": [f"画像验证错误：{err}" for err in profile_errors],
            "action_plan": [],
            "deliverables": {},
            "risk_notes": RISK_NOTES,
            "next_tracking_fields": ["child_profile", "current_problem"],
            "markdown_report": "孩子画像验证失败：" + "；".join(profile_errors),
            "validation_errors": profile_errors,
            "success": False,
            "timestamp": datetime.now().isoformat()
        }

    classes = payload.get("classes") or []
    if classes:
        batch_result = validate_batch_classes(classes)
        if batch_result["invalid_count"] > 0:
            print(f"⚠️  警告：{batch_result['invalid_count']} 个兴趣班验证失败")

    preferences = payload.get("preferences", {})

    comparisons = compare_classes(classes, preferences, child_profile)
    alerts = detect_class_anomalies(classes, comparisons)
    recommendations = generate_class_recommendations(classes, comparisons, child_profile, alerts)

    result: Dict[str, Any] = {
        "skill_id": SKILL_ID,
        "skill_name": SKILL_NAME,
        "summary": [
            "已根据当前问题生成一版家庭可执行闭环。",
            "建议试课后根据孩子反馈再做决定。",
            "涉及专业判断的部分已放入风险与人工核验清单。",
            f"已对比 {len(classes)} 个兴趣班，" +
            (f"发现 {len(alerts)} 项需要关注的异常。" if alerts else "未发现明显异常。") +
            (f"生成了 {len(recommendations)} 条选择建议。" if recommendations else "")
        ],
        "known_facts": build_known_facts(payload),
        "analysis": build_analysis(payload),
        "action_plan": build_action_plan(payload),
        "deliverables": build_deliverables(payload),
        "risk_notes": RISK_NOTES,
        "next_tracking_fields": next_fields(),
        "comparison_results": comparisons,
        "alerts": [a.to_dict() if hasattr(a, 'to_dict') else a for a in alerts],
        "recommendations": [r.to_dict() if hasattr(r, 'to_dict') else r for r in recommendations],
        "validation_errors": [],
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "metadata": {
            "total_classes": len(classes),
            "total_comparisons": len(comparisons),
            "total_alerts": len(alerts),
            "total_recommendations": len(recommendations)
        }
    }

    result["markdown_report"] = render_report(result)

    if payload.get("export_format"):
        export_format = payload["export_format"].lower()
        if export_format == "json":
            result["exported_data"] = export_to_json(result)
        elif export_format == "html":
            result["exported_data"] = export_to_html(result)
        elif export_format == "csv":
            result["exported_data"] = export_to_csv_summary(result)

    return result


def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(description="兴趣班选择 Agent")
    parser.add_argument("--input", required=True, help="输入JSON文件路径")
    parser.add_argument("--output", help="输出JSON文件路径（可选）")
    parser.add_argument("--format", choices=["json", "html", "markdown", "csv"],
                       default="json", help="输出格式（默认：json）")
    parser.add_argument("--export-file", help="导出文件路径（可选）")

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ 错误：输入文件不存在：{args.input}", file=sys.stderr)
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    payload["export_format"] = args.format

    result = run(payload)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✅ 结果已保存到：{args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.export_file:
        export_path = Path(args.export_file)
        export_path.parent.mkdir(parents=True, exist_ok=True)

        if args.format == "json":
            content = export_to_json(result)
        elif args.format == "html":
            content = export_to_html(result)
        elif args.format == "csv":
            content = export_to_csv_summary(result)
        else:
            content = result["markdown_report"]

        export_path.write_text(content, encoding="utf-8")
        print(f"✅ 导出文件已保存到：{args.export_file}")

    if result.get("metadata"):
        metadata = result["metadata"]
        print(f"\n📊 分析摘要：")
        print(f"  - 兴趣班总数：{metadata['total_classes']}")
        print(f"  - 完成对比：{metadata['total_comparisons']}个")
        print(f"  - 异常告警：{metadata['total_alerts']}项")
        print(f"  - 选择建议：{metadata['total_recommendations']}条")


if __name__ == "__main__":
    main()
