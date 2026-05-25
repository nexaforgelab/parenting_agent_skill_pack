"""Run every skill through its command-line entrypoint.

This is the closest generated-pack end-to-end test: for each skill it executes
``src/runner.py`` with the sample input, writes an output file, then validates
the produced JSON against the manifest and required output-schema fields.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
REPORT_DIR = ROOT / "test_reports"
REPORT_DIR.mkdir(exist_ok=True)

REQUIRED_NON_EMPTY_FIELDS = ("summary", "action_plan", "risk_notes", "markdown_report")


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_output(skill_dir: Path, output: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    manifest = _load_json(skill_dir / "manifest.json")
    schema = _load_json(skill_dir / "schemas" / "output.schema.json")

    expected_skill_id = manifest.get("skill_id")
    if output.get("skill_id") != expected_skill_id:
        errors.append(f"skill_id mismatch: expected {expected_skill_id!r}, got {output.get('skill_id')!r}")

    for field in schema.get("required", []):
        if field not in output:
            errors.append(f"missing required field: {field}")

    for field in REQUIRED_NON_EMPTY_FIELDS:
        if not output.get(field):
            errors.append(f"empty required runtime field: {field}")

    type_checks = {
        "summary": list,
        "known_facts": list,
        "analysis": list,
        "action_plan": list,
        "deliverables": dict,
        "risk_notes": list,
        "next_tracking_fields": list,
        "markdown_report": str,
    }
    for field, expected_type in type_checks.items():
        if field in output and not isinstance(output[field], expected_type):
            errors.append(f"{field} should be {expected_type.__name__}, got {type(output[field]).__name__}")

    return errors


def test_skill_cli(skill_dir: Path, tmp_dir: Path) -> Dict[str, Any]:
    runner = skill_dir / "src" / "runner.py"
    input_path = skill_dir / "examples" / "sample_input.json"
    output_path = tmp_dir / f"{skill_dir.name}.json"

    result: Dict[str, Any] = {
        "skill": skill_dir.name,
        "passed": False,
        "output": str(output_path),
        "errors": [],
        "stdout": "",
        "stderr": "",
        "execution_time": 0.0,
    }

    start = datetime.now()
    proc = subprocess.run(
        [sys.executable, str(runner), "--input", str(input_path), "--output", str(output_path)],
        cwd=str(skill_dir),
        capture_output=True,
        text=True,
        timeout=20,
    )
    result["execution_time"] = (datetime.now() - start).total_seconds()
    result["stdout"] = proc.stdout.strip()
    result["stderr"] = proc.stderr.strip()

    if proc.returncode != 0:
        result["errors"].append(f"process exited with {proc.returncode}")
        return result

    if not output_path.exists():
        result["errors"].append("output file was not created")
        return result

    try:
        output = _load_json(output_path)
    except Exception as exc:  # pragma: no cover - diagnostics path
        result["errors"].append(f"output is not valid JSON: {exc}")
        return result

    result["errors"].extend(_validate_output(skill_dir, output))
    result["passed"] = not result["errors"]
    result["field_count"] = len(output)
    result["report_length"] = len(str(output.get("markdown_report", "")))
    return result


def render_report(results: List[Dict[str, Any]]) -> str:
    passed = sum(1 for item in results if item["passed"])
    lines = [
        "# 育儿智能体 Skill CLI 端到端测试报告",
        "",
        f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**测试 Skill 数量**: {len(results)}",
        f"**通过数量**: {passed}/{len(results)} ({passed / len(results) * 100:.0f}%)",
        "",
        "## 结果概览",
        "",
        "| Skill | 状态 | 字段数 | 报告长度 | 执行时间 | 问题 |",
        "|---|---|---:|---:|---:|---|",
    ]

    for item in results:
        status = "通过" if item["passed"] else "失败"
        errors = "; ".join(item["errors"])
        lines.append(
            f"| {item['skill']} | {status} | {item.get('field_count', 0)} | "
            f"{item.get('report_length', 0)} | {item['execution_time']:.3f}s | {errors} |"
        )

    failed = [item for item in results if not item["passed"]]
    if failed:
        lines.extend(["", "## 失败详情", ""])
        for item in failed:
            lines.extend(
                [
                    f"### {item['skill']}",
                    "",
                    "```text",
                    "\n".join(item["errors"]) or "(no structured error)",
                    item["stderr"],
                    "```",
                    "",
                ]
            )

    lines.extend(["", "---", "*本报告由 CLI 端到端测试脚本生成*"])
    return "\n".join(lines)


def main() -> int:
    print("🎯 开始运行 CLI 端到端测试...")
    print("=" * 60)

    with tempfile.TemporaryDirectory(prefix="parenting_skill_cli_e2e_") as temp_dir:
        tmp_dir = Path(temp_dir)
        results = []
        for skill_dir in sorted(path for path in SKILLS.iterdir() if path.is_dir()):
            print(f"📝 CLI 测试 Skill: {skill_dir.name}")
            result = test_skill_cli(skill_dir, tmp_dir)
            results.append(result)
            status = "✅" if result["passed"] else "❌"
            print(
                f"   {status} 字段:{result.get('field_count', 0)} "
                f"报告:{result.get('report_length', 0)}字符 "
                f"耗时:{result['execution_time']:.3f}s"
            )
            if result["errors"]:
                print(f"   问题: {'; '.join(result['errors'])}")

    report = render_report(results)
    report_path = REPORT_DIR / f"cli_e2e_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_path.write_text(report, encoding="utf-8")
    latest_path = REPORT_DIR / "cli_e2e_test_report_latest.md"
    latest_path.write_text(report, encoding="utf-8")

    print("=" * 60)
    print(f"✅ 报告已保存至: {report_path}")
    print(f"✅ 最新报告: {latest_path}")

    return 0 if all(item["passed"] for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
