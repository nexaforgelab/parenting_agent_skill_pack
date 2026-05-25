"""Dedicated test script for the 5 failed skills with proper test cases."""
from __future__ import annotations

import importlib.util
import json
import importlib
from pathlib import Path
import traceback
import sys
import uuid
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
REPORT_DIR = ROOT / "test_reports"
REPORT_DIR.mkdir(exist_ok=True)


def load_module(path: Path):
    """Load skill runner module."""
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
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            return module
        return None
    except Exception as e:
        print(f"[ERROR] Load failed: {e}")
        return None
    finally:
        if src_dir in sys.path:
            try:
                sys.path.remove(src_dir)
            except ValueError:
                pass


def get_specialized_test_cases():
    """Get proper test cases for each failed skill."""

    return {
        "41_family_photo_organizer": {
            "user_query": "宝宝从出生到3岁的照片太多了，怎么整理比较好？",
            "payload": {
                "child_profile": {"age": "3岁", "nickname": "小星星"},
                "family_context": {"caregiver": "父母", "available_time": "周末有空"},
                "current_problem": "宝宝照片太多，需要整理归档",
                "goal": "制定照片整理方案",
                "photos": [
                    {"date": "2021-06-01", "event": "满月照", "tags": ["满月", "室内"], "location": "家"},
                    {"date": "2021-09-15", "event": "百天照", "tags": ["百天", "室外"], "location": "公园"},
                    {"date": "2022-01-01", "event": "周岁照", "tags": ["周岁", "生日"], "location": "家"},
                    {"date": "2022-06-01", "event": "生日派对", "tags": ["生日", "2岁"], "location": "家"},
                    {"date": "2023-01-01", "event": "新年照", "tags": ["新年", "3岁"], "location": "室外"},
                    {"date": "2023-06-01", "event": "日常", "tags": ["日常"], "location": "家"},
                ],
                "preferences": {"tone": "实用", "priority": "效率"},
                "history_days": 730
            }
        },

        "42_child_growth_archive": {
            "user_query": "想给孩子建一个成长档案，记录重要的里程碑，怎么做比较好？",
            "payload": {
                "child_profile": {"age": "5岁", "nickname": "小苗苗", "birth_date": "2019-05-01"},
                "family_context": {"caregiver": "父母", "available_time": "周末"},
                "current_problem": "想建立孩子的成长档案",
                "goal": "设计成长档案结构和记录方法",
                "growth_records": [
                    {"date": "2019-08-01", "milestone": "能抬头", "category": "大运动", "note": "趴着能抬头45度"},
                    {"date": "2020-01-01", "milestone": "能翻身", "category": "大运动", "note": "从仰卧到俯卧"},
                    {"date": "2020-06-01", "milestone": "能独坐", "category": "大运动", "note": "不需要支撑"},
                    {"date": "2021-01-01", "milestone": "能走路", "category": "大运动", "note": "独立行走"},
                    {"date": "2021-06-01", "milestone": "会说爸爸", "category": "语言", "note": "第一句话"},
                    {"date": "2022-01-01", "milestone": "会说句子", "category": "语言", "note": "能用短句表达"},
                ],
                "preferences": {"tone": "温暖", "priority": "记录珍贵时刻"},
                "history_days": 365
            }
        },

        "43_kindergarten_selection": {
            "user_query": "孩子2岁了，想找一家合适的幼儿园，怎么选？",
            "payload": {
                "child_profile": {"age": "2岁", "nickname": "小豆芽"},
                "family_context": {"caregiver": "父母", "available_time": "工作日下班后", "budget": "5-8万/年"},
                "current_problem": "孩子2岁，需要选择幼儿园",
                "goal": "制定择校方案",
                "kindergartens": [
                    {
                        "kindergarten_id": "kg001",
                        "name": "阳光双语幼儿园",
                        "type": "私立",
                        "rating": 4.6,
                        "tuition_per_year": 80000,
                        "distance_from_home": 2,
                        "teacher_student_ratio": 0.08,
                        "features": ["双语教学", "外教全天", "国际课程"]
                    },
                    {
                        "kindergarten_id": "kg002",
                        "name": "社区公立幼儿园",
                        "type": "公立",
                        "rating": 4.2,
                        "tuition_per_year": 30000,
                        "distance_from_home": 0.5,
                        "teacher_student_ratio": 0.12,
                        "features": ["就近入学", "师资稳定", "费用低"]
                    },
                    {
                        "kindergarten_id": "kg003",
                        "name": "蒙特梭利幼儿园",
                        "type": "私立",
                        "rating": 4.8,
                        "tuition_per_year": 120000,
                        "distance_from_home": 5,
                        "teacher_student_ratio": 0.05,
                        "features": ["蒙特梭利教学法", "混龄班", "小班教学"]
                    }
                ],
                "preferences": {"tone": "专业", "priority": "教学质量和距离"},
                "history_days": 30
            }
        },

        "44_extracurricular_class_selection": {
            "user_query": "孩子5岁了，想给他报几个兴趣班，有什么推荐吗？",
            "payload": {
                "child_profile": {
                    "age": "5岁",
                    "nickname": "小太阳",
                    "interests": ["画画", "音乐", "运动"],
                    "personality": "活泼好动"
                },
                "family_context": {"caregiver": "父母", "available_time": "周末和放学后", "budget": "5000元/月"},
                "current_problem": "想给孩子选择合适的兴趣班",
                "goal": "制定兴趣班选择方案",
                "classes": [
                    {
                        "class_id": "cls001",
                        "name": "创意美术",
                        "type": "艺术",
                        "tuition_per_month": 2500,
                        "hours_per_week": 2,
                        "rating": 4.7,
                        "related_interests": ["画画"],
                        "features": ["小班教学", "材料丰富"]
                    },
                    {
                        "class_id": "cls002",
                        "name": "钢琴启蒙",
                        "type": "音乐",
                        "tuition_per_month": 4000,
                        "hours_per_week": 2,
                        "rating": 4.5,
                        "related_interests": ["音乐"],
                        "features": ["一对一教学", "专业老师"]
                    },
                    {
                        "class_id": "cls003",
                        "name": "跆拳道",
                        "type": "运动",
                        "tuition_per_month": 1800,
                        "hours_per_week": 3,
                        "rating": 4.3,
                        "related_interests": ["运动"],
                        "features": ["强身健体", "培养意志"]
                    },
                    {
                        "class_id": "cls004",
                        "name": "乐高机器人",
                        "type": "科技",
                        "tuition_per_month": 3000,
                        "hours_per_week": 2,
                        "rating": 4.8,
                        "related_interests": ["搭建", "编程"],
                        "features": ["培养逻辑思维", "动手能力"]
                    }
                ],
                "preferences": {"tone": "实用", "priority": "孩子兴趣和性价比"},
                "history_days": 30
            }
        },

        "45_after_school_class_risk_checker": {
            "user_query": "看到一个钢琴班，招生说能保证考级通过，靠谱吗？",
            "payload": {
                "child_profile": {"age": "6岁", "nickname": "小音符"},
                "family_context": {"caregiver": "父母", "available_time": "周末"},
                "current_problem": "想报钢琴班，但担心被坑",
                "goal": "评估这个钢琴班的风险",
                "classes": [
                    {
                        "class_id": "cls001",
                        "name": "某某钢琴培训",
                        "institution": "某某教育",
                        "years_in_business": 1,
                        "accreditation": [],
                        "refund_policy": "不可退款",
                        "contract_required": False,
                        "tuition": 25000,
                        "installment_available": False,
                        "teacher_qualification": "不明",
                        "class_size": 15,
                        "red_flags": ["升学保障", "限时优惠"]
                    }
                ],
                "preferences": {"tone": "谨慎", "priority": "资金安全"},
                "history_days": 30
            }
        }
    }


def test_single_skill(skill_dir: Path, test_case: Dict) -> Dict:
    """Test a single skill with a specific test case."""
    runner_path = skill_dir / "src" / "runner.py"
    manifest_path = skill_dir / "manifest.json"

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"error": f"Failed to load manifest: {e}"}

    mod = load_module(runner_path)
    if mod is None:
        return {"error": "Failed to load module"}

    result = {
        "skill_id": manifest.get("skill_id", "unknown"),
        "skill_name": manifest.get("name", "unknown"),
        "user_query": test_case["user_query"],
        "passed": False,
        "output_analysis": {},
        "error": None
    }

    try:
        output = mod.run(test_case["payload"])

        result["execution_time"] = 0.0
        result["output_analysis"] = {
            "has_summary": bool(output.get("summary")),
            "summary_length": len(str(output.get("summary", ""))),
            "summary_preview": str(output.get("summary", ""))[:300],

            "has_analysis": bool(output.get("analysis")),
            "analysis_count": len(output.get("analysis", [])),

            "has_action_plan": bool(output.get("action_plan")),
            "action_plan_count": len(output.get("action_plan", [])),

            "has_risk_notes": bool(output.get("risk_notes")),
            "risk_notes_count": len(output.get("risk_notes", [])),

            "has_markdown_report": bool(output.get("markdown_report")),
            "report_length": len(str(output.get("markdown_report", ""))),

            "has_deliverables": bool(output.get("deliverables")),

            "total_fields": list(output.keys()),
        }

        if result["output_analysis"]["has_summary"] and \
           result["output_analysis"]["has_action_plan"] and \
           result["output_analysis"]["has_markdown_report"] and \
           result["output_analysis"]["report_length"] > 500:
            result["passed"] = True

        result["full_output"] = output

    except Exception as e:
        result["error"] = str(e)
        result["traceback"] = traceback.format_exc()

    return result


def main():
    """Run tests for the 5 failed skills."""
    print("🔍 测试5个之前失败的Skill...")
    print("=" * 60)

    test_cases = get_specialized_test_cases()
    results = []

    for skill_id, test_case in test_cases.items():
        skill_dir = SKILLS / skill_id

        if not skill_dir.exists():
            print(f"❌ 目录不存在: {skill_dir}")
            continue

        print(f"\n📝 测试: {test_case['user_query'][:50]}...")

        result = test_single_skill(skill_dir, test_case)

        if "error" in result:
            print(f"   ❌ 失败: {result['error']}")
        else:
            analysis = result.get("output_analysis", {})
            status = "✅" if result.get("passed") else "❌"
            print(f"   {status} | 摘要:{analysis.get('summary_length', 0)}字符 | 报告:{analysis.get('report_length', 0)}字符")

            if analysis.get("report_length", 0) < 500:
                print(f"   ⚠️  报告长度不足500字符")

        results.append(result)

    print("\n" + "=" * 60)
    print("\n📊 测试结果汇总")
    print("-" * 60)

    passed = sum(1 for r in results if r.get("passed"))
    total = len(results)

    print(f"通过: {passed}/{total} ({passed/total*100:.0f}%)\n")

    for r in results:
        analysis = r.get("output_analysis", {})
        status = "✅通过" if r.get("passed") else "❌失败"
        print(f"{r['skill_name']}")
        print(f"  状态: {status}")
        print(f"  摘要长度: {analysis.get('summary_length', 0)}字符")
        print(f"  报告长度: {analysis.get('report_length', 0)}字符")
        print(f"  分析条数: {analysis.get('analysis_count', 0)}条")
        print(f"  行动计划条数: {analysis.get('action_plan_count', 0)}条")

        if analysis.get("summary_preview"):
            print(f"  摘要预览: {analysis['summary_preview'][:100]}...")

        if "error" in r:
            print(f"  错误: {r['error']}")

        print()


if __name__ == "__main__":
    main()