"""Entrypoint for 睡前故事生成 Agent.

CLI:
    python src/runner.py --input examples/sample_input.json --output outputs/report.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

try:
    from validators import require_payload
    from planner import (
        build_action_plan, build_analysis, build_deliverables, build_known_facts,
        next_fields, analyze_storytelling_progress, detect_storytelling_difficulties,
        generate_personalized_recommendations, analyze_storytelling_curve, calculate_mastery_level,
        create_session_context
    )
    from reporting import render_report
except (ImportError, ModuleNotFoundError):
    sys.path.insert(0, str(CURRENT_DIR))
    from validators import require_payload
    from planner import (
        build_action_plan, build_analysis, build_deliverables, build_known_facts,
        next_fields, analyze_storytelling_progress, detect_storytelling_difficulties,
        generate_personalized_recommendations, analyze_storytelling_curve, calculate_mastery_level,
        create_session_context
    )
    from reporting import render_report

SKILL_ID = "bedtime_story_generator"
SKILL_NAME = "睡前故事生成 Agent"
RISK_NOTES = ['本 Skill 提供家庭教育和生活管理建议，不替代专业人士意见。', '涉及安全、法律、医疗、财务或教育政策时，应提示家长二次核验。', '输出应尊重家庭差异，不用单一标准评价孩子或父母。']


def run(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Run the skill once and return a structured report."""
    errors = require_payload(payload)
    if errors:
        return {
            "skill_id": SKILL_ID,
            "summary": ["输入不完整，无法生成完整闭环。"],
            "known_facts": [],
            "analysis": errors,
            "action_plan": [],
            "deliverables": {},
            "risk_notes": RISK_NOTES,
            "next_tracking_fields": ["child_profile", "current_problem"],
            "markdown_report": "输入不完整：" + "；".join(errors)
        }

    records = payload.get("raw_records", [])
    child_profile = payload.get("child_profile", {})
    preferences = payload.get("preferences", {})

    progress = analyze_storytelling_progress(records)
    difficulties = detect_storytelling_difficulties(records)
    recommendations = generate_personalized_recommendations(child_profile, records, progress)
    storytelling_curve = analyze_storytelling_curve(records)
    mastery_level = calculate_mastery_level(records)
    session_context = create_session_context(child_profile, records, preferences)

    progress_stats = {
        "total_stories": progress.get("total_stories", 0),
        "total_minutes": progress.get("total_minutes", 0),
        "average_engagement": progress.get("average_engagement", 0.0),
        "favorite_themes": progress.get("favorite_themes", []),
        "favorite_characters": progress.get("favorite_characters", []),
        "current_streak": len([r for r in records if r.get("timestamp")]),
        "longest_streak": len([r for r in records if r.get("timestamp")])
    }

    analysis_summary = build_analysis(payload)
    if difficulties:
        analysis_summary.append("")
        analysis_summary.append("⚠️ 检测到的问题：")
        for d in difficulties:
            analysis_summary.append(f"  - [{d.get('severity', 'medium')}] {d.get('message', '')}")

    if storytelling_curve.get("curve_type") != "insufficient_data":
        analysis_summary.append("")
        analysis_summary.append(f"📈 讲故事曲线分析：{storytelling_curve.get('prediction', '')}")
        analysis_summary.append(f"   掌握程度：{mastery_level}")

    result: Dict[str, Any] = {
        "skill_id": SKILL_ID,
        "skill_name": SKILL_NAME,
        "summary": [
            f"已根据当前问题生成一版家庭可执行闭环。",
            f"当前讲故事进度：共 {progress.get('total_stories', 0)} 个故事，累计 {progress.get('total_minutes', 0)} 分钟。",
            f"生成 {len(recommendations)} 条个性化建议。",
            "涉及专业判断的部分已放入风险与人工核验清单。"
        ],
        "known_facts": build_known_facts(payload),
        "analysis": analysis_summary,
        "action_plan": build_action_plan(payload),
        "deliverables": build_deliverables(payload),
        "risk_notes": RISK_NOTES,
        "next_tracking_fields": next_fields(),
        "progress_stats": progress_stats,
        "recommendations": recommendations,
        "story_records": records,
        "session_context": session_context,
        "difficulty_alerts": difficulties,
        "storytelling_curve": storytelling_curve
    }
    result["markdown_report"] = render_report(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=False)
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        payload = json.load(f)
    result = run(payload)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()