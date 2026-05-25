"""Comprehensive test runner for all 50 parenting skills."""
from __future__ import annotations

import importlib.util
import json
import importlib
from pathlib import Path
import traceback
import sys
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import random

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
REPORT_DIR = ROOT / "test_reports"
REPORT_DIR.mkdir(exist_ok=True)


def load_module(path: Path):
    """加载skill的runner模块。"""
    src_dir = str(path.parent)
    module_name = f"skill_{uuid.uuid4().hex}"

    modules_to_remove = []
    for key in list(sys.modules.keys()):
        if any(x in key for x in ['planner', 'validators', 'reporting', 'models', 'analytics', 'communication', 'progress']):
            modules_to_remove.append(key)

    for key in modules_to_remove:
        try:
            del sys.modules[key]
        except KeyError:
            pass

    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        return None
    except Exception as e:
        return None
    finally:
        if src_dir in sys.path:
            try:
                sys.path.remove(src_dir)
            except ValueError:
                pass


def generate_test_cases(skill_id: str) -> List[Dict[str, Any]]:
    """根据skill类型生成测试用例。"""
    test_cases = []

    def multi_records() -> List[Dict[str, Any]]:
        if skill_id == "41_family_photo_organizer":
            return [
                {
                    "photo_id": f"photo_2024010{i}_001",
                    "timestamp": f"2024-01-0{i}",
                    "event": f"照片事件{i}",
                    "category": "daily",
                    "location": "家里",
                    "people": ["孩子", "父母"],
                    "tags": ["日常"]
                }
                for i in range(1, 6)
            ]

        if skill_id == "42_child_growth_archive":
            return [
                {
                    "record_id": f"growth_2024010{i}_001",
                    "record_date": f"2024-01-0{i}",
                    "title": f"成长事件{i}",
                    "category": "milestone",
                    "record_type": "physical",
                    "description": f"成长记录备注{i}",
                    "tags": ["里程碑"],
                    "importance": "normal"
                }
                for i in range(1, 6)
            ]

        return [
            {"time": "2024-01-01 08:00", "event": "事件1", "note": "备注1"},
            {"time": "2024-01-01 12:00", "event": "事件2", "note": "备注2"},
            {"time": "2024-01-02 08:00", "event": "事件3", "note": "备注3"},
            {"time": "2024-01-02 12:00", "event": "事件4", "note": "备注4"},
            {"time": "2024-01-03 08:00", "event": "事件5", "note": "备注5"}
        ]

    base_payload = {
        "child_profile": {
            "age": "6岁",
            "nickname": "小明"
        },
        "family_context": {
            "caregiver": "父母",
            "available_time": "每天30分钟",
            "notes": "双职工家庭"
        },
        "current_problem": "需要分析和规划",
        "goal": "生成执行计划",
        "raw_records": [],
        "preferences": {
            "tone": "温和",
            "budget": "适中"
        },
        "history_days": 7,
        "privacy_mode": "family_local_first"
    }

    test_cases.append({
        "name": "标准场景测试",
        "payload": base_payload
    })

    test_cases.append({
        "name": "空记录测试",
        "payload": {
            **base_payload,
            "raw_records": []
        }
    })

    test_cases.append({
        "name": "多条记录测试",
        "payload": {
            **base_payload,
            "raw_records": multi_records()
        }
    })

    test_cases.append({
        "name": "边界情况-极端年龄",
        "payload": {
            **base_payload,
            "child_profile": {
                "age": "0岁" if "infant" in skill_id or "newborn" in skill_id or "baby" in skill_id else "18岁",
                "nickname": "测试"
            }
        }
    })

    test_cases.append({
        "name": "边界情况-长周期",
        "payload": {
            **base_payload,
            "history_days": 30
        }
    })

    return test_cases


def test_skill(skill_dir: Path, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """测试单个skill的多个用例。"""
    runner_path = skill_dir / "src" / "runner.py"
    manifest_path = skill_dir / "manifest.json"

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"error": f"Failed to load manifest: {e}", "cases": []}

    mod = load_module(runner_path)
    if mod is None:
        return {"error": "Failed to load module", "cases": []}

    results = []
    for tc in test_cases:
        case_result = {
            "name": tc["name"],
            "passed": False,
            "error": None,
            "output_fields": [],
            "execution_time": 0
        }

        start_time = datetime.now()
        try:
            result = mod.run(tc["payload"])

            required_fields = ["skill_id", "summary", "action_plan", "risk_notes"]
            missing_fields = [f for f in required_fields if f not in result]

            if missing_fields:
                case_result["error"] = f"Missing required fields: {missing_fields}"
                case_result["output_fields"] = list(result.keys())
            else:
                case_result["passed"] = True
                case_result["output_fields"] = list(result.keys())

                if "trends" in result and result["trends"]:
                    case_result["has_trends"] = True
                if "alerts" in result and result["alerts"]:
                    case_result["has_alerts"] = True
                if "recommendations" in result and result["recommendations"]:
                    case_result["has_recommendations"] = True
                if "weekly_stats" in result and result["weekly_stats"]:
                    case_result["has_weekly_stats"] = True

        except Exception as e:
            case_result["error"] = str(e)
            case_result["traceback"] = traceback.format_exc()

        case_result["execution_time"] = (datetime.now() - start_time).total_seconds()
        results.append(case_result)

    return {
        "skill_id": manifest.get("skill_id", "unknown"),
        "skill_name": manifest.get("name", "unknown"),
        "category": manifest.get("category", "unknown"),
        "cases": results,
        "passed_count": sum(1 for r in results if r["passed"]),
        "total_count": len(results)
    }


def generate_report(all_results: List[Dict[str, Any]]) -> str:
    """生成Markdown测试报告。"""
    lines = []
    lines.append("# 育儿智能体Skill全面测试报告")
    lines.append("")
    lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append(f"**测试Skill总数**: {len(all_results)}")
    lines.append("")

    total_cases = sum(r["total_count"] for r in all_results if "error" not in r)
    total_passed = sum(r["passed_count"] for r in all_results if "error" not in r)
    lines.append(f"**总测试用例数**: {total_cases}")
    lines.append(f"**通过用例数**: {total_passed}")
    lines.append(f"**通过率**: {total_passed/total_cases*100:.1f}%" if total_cases > 0 else "**通过率**: N/A")
    lines.append("")

    lines.append("## 测试结果概览")
    lines.append("")
    lines.append("| Skill ID | Skill名称 | 类别 | 用例数 | 通过数 | 通过率 |")
    lines.append("|----------|----------|------|--------|--------|--------|")

    for r in all_results:
        if "error" in r:
            lines.append(f"| {r.get('skill_id', 'N/A')} | {r.get('skill_name', 'N/A')} | {r.get('category', 'N/A')} | - | - | ❌ |")
        else:
            rate = r["passed_count"] / r["total_count"] * 100 if r["total_count"] > 0 else 0
            status = "✅" if rate == 100 else "⚠️" if rate >= 60 else "❌"
            lines.append(f"| {r['skill_id']} | {r['skill_name']} | {r['category']} | {r['total_count']} | {r['passed_count']} | {status} {rate:.0f}% |")

    lines.append("")
    lines.append("## 详细测试结果")
    lines.append("")

    for r in all_results:
        if "error" in r:
            lines.append(f"### ❌ {r.get('skill_name', 'Unknown')} ({r.get('skill_id', 'N/A')})")
            lines.append("")
            lines.append(f"**错误**: {r['error']}")
            lines.append("")
            continue

        rate = r["passed_count"] / r["total_count"] * 100 if r["total_count"] > 0 else 0
        lines.append(f"### {'✅' if rate == 100 else '⚠️' if rate >= 60 else '❌'} {r['skill_name']} ({r['skill_id']})")
        lines.append("")
        lines.append(f"**类别**: {r['category']}")
        lines.append(f"**用例数**: {r['passed_count']}/{r['total_count']} ({rate:.0f}%)")
        lines.append("")

        lines.append("| 用例名称 | 状态 | 执行时间 | 错误信息 |")
        lines.append("|----------|------|----------|----------|")

        for case in r["cases"]:
            status = "✅通过" if case["passed"] else "❌失败"
            error = case["error"][:50] + "..." if case["error"] and len(case["error"]) > 50 else (case["error"] or "")
            lines.append(f"| {case['name']} | {status} | {case['execution_time']:.3f}s | {error} |")

        lines.append("")

        features = []
        for case in r["cases"]:
            if case.get("has_trends"):
                features.append("趋势分析")
            if case.get("has_alerts"):
                features.append("告警")
            if case.get("has_recommendations"):
                features.append("个性化推荐")
            if case.get("has_weekly_stats"):
                features.append("周统计")

        if features:
            lines.append(f"**增强功能**: {', '.join(set(features))}")
            lines.append("")

        lines.append("**输出字段**:")
        output_fields = set()
        for case in r["cases"]:
            output_fields.update(case.get("output_fields", []))
        lines.append("```")
        lines.append(', '.join(sorted(output_fields)))
        lines.append("```")
        lines.append("")

    failed_skills = [r for r in all_results if "error" in r or any(not c["passed"] for c in r.get("cases", []))]
    if failed_skills:
        lines.append("## 失败Skill详情")
        lines.append("")
        for r in failed_skills:
            if "error" in r:
                lines.append(f"### {r.get('skill_name', 'Unknown')}")
                lines.append("")
                lines.append(f"```\n{r['error']}\n```")
                lines.append("")

    lines.append("---")
    lines.append("*本报告由自动化测试脚本生成*")

    return "\n".join(lines)


def main():
    """运行所有skill的测试。"""
    print("🚀 开始运行全面测试...")
    print("=" * 60)

    all_results = []

    for skill_dir in sorted(SKILLS.iterdir()):
        if not skill_dir.is_dir():
            continue

        skill_name = skill_dir.name
        print(f"\n📝 测试 Skill: {skill_name}")

        test_cases = generate_test_cases(skill_name)
        print(f"   生成 {len(test_cases)} 个测试用例")

        result = test_skill(skill_dir, test_cases)

        if "error" in result:
            print(f"   ❌ 加载失败: {result['error']}")
        else:
            print(f"   ✅ {result['passed_count']}/{result['total_count']} 用例通过")

            has_features = []
            for case in result["cases"]:
                if case.get("has_trends"):
                    has_features.append("趋势分析")
                if case.get("has_alerts"):
                    has_features.append("告警")
                if case.get("has_recommendations"):
                    has_features.append("推荐")
                if case.get("has_weekly_stats"):
                    has_features.append("周统计")

            if has_features:
                print(f"   🔧 增强功能: {', '.join(set(has_features))}")

        all_results.append(result)

    print("\n" + "=" * 60)
    print("📊 生成测试报告...")

    report = generate_report(all_results)
    report_path = REPORT_DIR / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"✅ 报告已保存至: {report_path}")

    summary_path = REPORT_DIR / "test_report_latest.md"
    summary_path.write_text(report, encoding="utf-8")
    print(f"✅ 最新报告: {summary_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
