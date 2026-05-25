"""Entrypoint for 亲子冲突复盘 Agent.

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
    from .validators import require_payload
    from .planner import build_action_plan, build_analysis, build_deliverables, build_known_facts, next_fields
    from .reporting import render_report
except ImportError:  # direct CLI execution from src/
    from validators import require_payload
    from planner import build_action_plan, build_analysis, build_deliverables, build_known_facts, next_fields
    from reporting import render_report

SKILL_ID = "parent_child_conflict_review"
SKILL_NAME = "亲子冲突复盘 Agent"
RISK_NOTES = ['本 Skill 用于家庭沟通、情绪复盘和非临床自我管理，不提供心理诊断或治疗。', '涉及自伤、伤人、家暴、严重抑郁、持续失控等高风险情境时，应提示寻求专业帮助或紧急支持。', '所有话术应低评判、低羞辱、鼓励共情和边界，不制造亲子对立。']


def run(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Run the skill once and return a structured report.

    生产环境可在此处接入：OCR、语音识别、日历、提醒、表格数据库、向量记忆、可视化图表等。
    """
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

    result: Dict[str, Any] = {
        "skill_id": SKILL_ID,
        "skill_name": SKILL_NAME,
        "summary": [
            "已根据当前问题生成一版家庭可执行闭环。",
            "建议从低压力记录开始，先建立个人基线，再逐步优化。",
            "涉及专业判断的部分已放入风险与人工核验清单。"
        ],
        "known_facts": build_known_facts(payload),
        "analysis": build_analysis(payload),
        "action_plan": build_action_plan(payload),
        "deliverables": build_deliverables(payload),
        "risk_notes": RISK_NOTES,
        "next_tracking_fields": next_fields(),
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
