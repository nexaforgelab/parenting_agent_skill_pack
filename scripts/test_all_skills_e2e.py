"""End-to-end test runner simulating real user queries for all 50 parenting skills."""
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
import textwrap

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
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            return module
        return None
    except Exception as e:
        print(f"[DEBUG] Load error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return None
    finally:
        if src_dir in sys.path:
            try:
                sys.path.remove(src_dir)
            except ValueError:
                pass


def get_test_scenarios() -> Dict[str, List[Dict[str, Any]]]:
    """为每个skill设计真实用户场景的测试用例。"""

    scenarios = {

        "01_newborn_feeding_tracker": [
            {
                "user_query": "宝宝3个月了，最近吃奶量下降，白天吃奶总是不专心，怎么办？",
                "payload": {
                    "child_profile": {"age": "3个月", "nickname": "小豆芽"},
                    "family_context": {"caregiver": "妈妈", "available_time": "随时"},
                    "current_problem": "宝宝吃奶量下降，白天不专心",
                    "goal": "分析原因并给出解决方案",
                    "raw_records": [
                        {"time": "2024-05-20 08:00", "event": "母乳", "amount": "80ml", "duration": "15min", "note": "不专心"},
                        {"time": "2024-05-20 11:00", "event": "母乳", "amount": "60ml", "duration": "10min", "note": "拒绝"},
                        {"time": "2024-05-20 14:00", "event": "母乳", "amount": "70ml", "duration": "12min", "note": "哭闹"},
                        {"time": "2024-05-21 08:00", "event": "母乳", "amount": "90ml", "duration": "20min", "note": "正常"},
                        {"time": "2024-05-21 11:00", "event": "母乳", "amount": "50ml", "duration": "8min", "note": "不专心"},
                    ],
                    "preferences": {"tone": "温和", "budget": "低成本"},
                    "history_days": 7
                }
            }
        ],

        "02_baby_routine_builder": [
            {
                "user_query": "宝宝8个月了，夜醒频繁，一晚醒3-4次，怎么办？",
                "payload": {
                    "child_profile": {"age": "8个月", "nickname": "小石头"},
                    "family_context": {"caregiver": "父母", "available_time": "白天陪玩，晚上轮流哄睡"},
                    "current_problem": "8个月宝宝夜醒频繁，影响全家睡眠",
                    "goal": "建立规律作息，减少夜醒",
                    "raw_records": [
                        {"time": "2024-05-20 08:00", "event": "起床", "note": ""},
                        {"time": "2024-05-20 09:00", "event": "早餐辅食", "note": ""},
                        {"time": "2024-05-20 21:00", "event": "入睡", "note": ""},
                        {"time": "2024-05-20 23:00", "event": "夜醒1", "note": "哭闹"},
                        {"time": "2024-05-21 02:00", "event": "夜醒2", "note": "哄抱"},
                        {"time": "2024-05-21 04:00", "event": "夜醒3", "note": "吃奶"},
                    ],
                    "preferences": {"tone": "专业", "budget": "低成本"},
                    "history_days": 7
                }
            }
        ],

        "03_baby_sleep_coach": [
            {
                "user_query": "宝宝1岁了，哄睡要1个多小时，有什么方法可以改善？",
                "payload": {
                    "child_profile": {"age": "1岁", "nickname": "糖糖"},
                    "family_context": {"caregiver": "妈妈", "available_time": "晚上2小时"},
                    "current_problem": "哄睡困难，时间太长",
                    "goal": "缩短哄睡时间，建立规律睡眠",
                    "raw_records": [
                        {"time": "2024-05-20 20:30", "event": "开始哄睡", "note": ""},
                        {"time": "2024-05-20 21:45", "event": "入睡", "duration": "75min", "note": "困难"},
                        {"time": "2024-05-21 20:00", "event": "开始哄睡", "note": ""},
                        {"time": "2024-05-21 21:30", "event": "入睡", "duration": "90min", "note": "哭闹"},
                    ],
                    "preferences": {"tone": "温和", "budget": "低成本"},
                    "history_days": 7
                }
            }
        ],

        "04_solid_food_planner": [
            {
                "user_query": "宝宝6个月开始加辅食，先加什么好？怎么加？",
                "payload": {
                    "child_profile": {"age": "6个月", "nickname": "米宝"},
                    "family_context": {"caregiver": "妈妈", "available_time": "每天30分钟"},
                    "current_problem": "刚到辅食添加月龄，不知从何开始",
                    "goal": "制定辅食添加计划",
                    "raw_records": [
                        {"time": "2024-05-20", "event": "尝试米粉", "food": "高铁米粉", "amount": "1勺", "reaction": "接受", "note": "第一天"}
                    ],
                    "preferences": {"tone": "温和", "priority": "补铁"},
                    "history_days": 7
                }
            }
        ],

        "05_baby_allergy_food_log": [
            {
                "user_query": "宝宝吃鸡蛋后嘴边发红，是过敏吗？以后还能吃吗？",
                "payload": {
                    "child_profile": {"age": "8个月", "nickname": "小土豆"},
                    "family_context": {"caregiver": "父母", "available_time": ""},
                    "current_problem": "疑似鸡蛋过敏",
                    "goal": "记录过敏反应，评估后续饮食",
                    "raw_records": [
                        {"time": "2024-05-20 12:00", "event": "添加辅食", "food": "鸡蛋黄", "amount": "1/4个", "reaction": "嘴边发红", "severity": "轻度", "note": "半小时后消退"},
                        {"time": "2024-05-15", "event": "尝试蛋黄", "food": "鸡蛋黄", "amount": "少量", "reaction": "无异常", "note": "第一次尝试"}
                    ],
                    "preferences": {"tone": "专业", "priority": "安全第一"},
                    "history_days": 30
                }
            }
        ],

        "06_development_milestone_tracker": [
            {
                "user_query": "宝宝1岁了还不会走，正常吗？",
                "payload": {
                    "child_profile": {"age": "12个月", "nickname": "跳跳"},
                    "family_context": {"caregiver": "父母", "available_time": ""},
                    "current_problem": "1岁还不会独立行走",
                    "goal": "评估发育情况，是否需要干预",
                    "raw_records": [
                        {"time": "2024-05-01", "milestone": "大运动", "status": "能扶站", "note": ""},
                        {"time": "2024-04-01", "milestone": "大运动", "status": "能独坐", "note": ""},
                        {"time": "2024-03-01", "milestone": "大运动", "status": "能翻身", "note": ""},
                    ],
                    "preferences": {"tone": "专业", "priority": "发育评估"},
                    "history_days": 90
                }
            }
        ],

        "07_vaccination_reminder": [
            {
                "user_query": "宝宝疫苗漏打了2针，怎么办？能补吗？",
                "payload": {
                    "child_profile": {"age": "18个月", "nickname": "小虎"},
                    "family_context": {"caregiver": "父母", "available_time": "周末"},
                    "current_problem": "疫苗漏打，需要补种",
                    "goal": "制定补种计划",
                    "raw_records": [
                        {"time": "2024-05-01", "vaccine": "乙肝疫苗第3剂", "status": "已接种"},
                        {"time": "2024-05-01", "vaccine": "脊灰疫苗第3剂", "status": "已接种"},
                        {"time": "2024-05-01", "vaccine": "百白破疫苗第3剂", "status": "逾期"},
                        {"time": "2024-05-01", "vaccine": "麻腮风疫苗第1剂", "status": "逾期"},
                    ],
                    "preferences": {"tone": "专业", "priority": "及时补种"},
                    "history_days": 365
                }
            }
        ],

        "11_picture_book_reading": [
            {
                "user_query": "2岁宝宝适合看什么绘本？怎么培养阅读习惯？",
                "payload": {
                    "child_profile": {"age": "2岁", "nickname": "朵朵"},
                    "family_context": {"caregiver": "妈妈", "available_time": "每晚20分钟"},
                    "current_problem": "想培养阅读习惯，不知道选什么书",
                    "goal": "推荐适龄绘本，建立阅读计划",
                    "raw_records": [
                        {"time": "2024-05-15", "book": "《猜猜我有多爱你》", "duration": "10min", "engagement": "高", "note": "喜欢"},
                        {"time": "2024-05-18", "book": "《好饿的毛毛虫》", "duration": "15min", "engagement": "高", "note": "能复述"},
                    ],
                    "preferences": {"tone": "温和", "book_preference": "图画精美"},
                    "history_days": 30
                }
            }
        ],

        "12_bedtime_story_generator": [
            {
                "user_query": "给3岁宝宝编一个关于勇气的睡前故事",
                "payload": {
                    "child_profile": {"age": "3岁", "nickname": "小太阳"},
                    "family_context": {"caregiver": "爸爸", "available_time": "睡前15分钟"},
                    "current_problem": "需要睡前故事，帮助入睡",
                    "goal": "生成一个关于勇气的故事",
                    "raw_records": [
                        {"time": "2024-05-20", "story_theme": "勇敢", "title": "小兔子找妈妈", "rating": 5}
                    ],
                    "preferences": {"tone": "温暖", "story_length": "10分钟", "theme": "勇气"},
                    "history_days": 7
                }
            }
        ],

        "17_focus_training": [
            {
                "user_query": "5岁孩子注意力不集中，坐不住，有什么游戏可以训练？",
                "payload": {
                    "child_profile": {"age": "5岁", "nickname": "小悟空"},
                    "family_context": {"caregiver": "父母", "available_time": "每天20分钟"},
                    "current_problem": "注意力不集中，多动",
                    "goal": "通过游戏训练专注力",
                    "raw_records": [
                        {"time": "2024-05-20", "activity": "拼图", "duration": "5min", "focus_score": 3, "note": "坐不住"},
                        {"time": "2024-05-21", "activity": "积木", "duration": "10min", "focus_score": 4, "note": "有进步"},
                    ],
                    "preferences": {"tone": "游戏化", "priority": "趣味性"},
                    "history_days": 14
                }
            }
        ],

        "21_primary_homework_companion": [
            {
                "user_query": "孩子写作业磨蹭，一项作业要做2小时，怎么破？",
                "payload": {
                    "child_profile": {"age": "7岁", "nickname": "小马虎", "grade": "小学一年级"},
                    "family_context": {"caregiver": "妈妈", "available_time": "晚上陪写"},
                    "current_problem": "写作业磨蹭，效率低",
                    "goal": "提高作业效率，减少磨蹭",
                    "raw_records": [
                        {"time": "2024-05-20 17:00", "subject": "语文", "task": "生字抄写", "duration": "45min", "difficulty": "中", "note": "磨蹭"},
                        {"time": "2024-05-20 18:00", "subject": "数学", "task": "口算10道", "duration": "30min", "difficulty": "低", "note": "发呆"},
                    ],
                    "preferences": {"tone": "鼓励", "priority": "效率"},
                    "history_days": 7
                }
            }
        ],

        "22_primary_mistake_notebook": [
            {
                "user_query": "孩子数学总在计算上出错，怎么办？",
                "payload": {
                    "child_profile": {"age": "8岁", "nickname": "小马虎", "grade": "小学二年级"},
                    "family_context": {"caregiver": "父母", "available_time": ""},
                    "current_problem": "数学计算总是出错",
                    "goal": "分析错题原因，制定改进计划",
                    "raw_records": [
                        {"time": "2024-05-20", "subject": "数学", "type": "计算题", "problem": "23+45=68", "correct": "正确"},
                        {"time": "2024-05-20", "subject": "数学", "type": "计算题", "problem": "67-23=34", "correct": "错误", "error_type": "退位减法"},
                        {"time": "2024-05-21", "subject": "数学", "type": "计算题", "problem": "34+17=51", "correct": "错误", "error_type": "进位加法"},
                    ],
                    "preferences": {"tone": "鼓励", "priority": "查漏补缺"},
                    "history_days": 30
                }
            }
        ],

        "31_parent_tutoring_phrases": [
            {
                "user_query": "孩子一道数学题讲了3遍还是不会，我忍不住发火了怎么办？",
                "payload": {
                    "child_profile": {"age": "9岁", "nickname": "小迷糊", "grade": "小学三年级"},
                    "family_context": {"caregiver": "妈妈", "available_time": "晚上1小时"},
                    "current_problem": "讲题多次不会，情绪失控",
                    "goal": "学习正确的辅导话术，控制情绪",
                    "raw_records": [
                        {"time": "2024-05-20 19:00", "situation": "讲数学题", "words": "你怎么这么笨", "child_reaction": "哭", "outcome": "失败"}
                    ],
                    "preferences": {"tone": "理解", "priority": "情绪管理"},
                    "history_days": 7
                }
            }
        ],

        "32_parent_child_conflict_review": [
            {
                "user_query": "孩子因为玩手机和我大吵一架，怎么处理比较好？",
                "payload": {
                    "child_profile": {"age": "10岁", "nickname": "小手机", "grade": "小学四年级"},
                    "family_context": {"caregiver": "父母", "available_time": ""},
                    "current_problem": "手机使用冲突，亲子争吵",
                    "goal": "复盘冲突，找到解决方案",
                    "raw_records": [
                        {"time": "2024-05-20 20:00", "conflict": "手机超时", "trigger": "时间到不肯放下", "parent_action": "没收手机", "child_reaction": "大哭大闹", "outcome": "两败俱伤"}
                    ],
                    "preferences": {"tone": "平和", "priority": "修复关系"},
                    "history_days": 7
                }
            }
        ],

        "36_family_schedule_manager": [
            {
                "user_query": "我们夫妻两个都要上班，奶奶接送孩子，怎样安排全家日程不冲突？",
                "payload": {
                    "child_profile": {"age": "6岁", "nickname": "小苗苗", "grade": "小学一年级"},
                    "family_context": {"caregiver": "父母+奶奶", "available_time": ""},
                    "current_problem": "全家日程混乱，接送经常出问题",
                    "goal": "梳理全家日程，解决冲突",
                    "raw_records": [
                        {"time": "2024-05-20 08:00", "event": "爸爸上班", "person": "爸爸"},
                        {"time": "2024-05-20 08:00", "event": "妈妈上班", "person": "妈妈"},
                        {"time": "2024-05-20 15:30", "event": "放学", "person": "奶奶", "note": "需要接"},
                        {"time": "2024-05-20 17:00", "event": "兴趣班", "person": "孩子", "note": "周五有课"},
                    ],
                    "preferences": {"tone": "实用", "priority": "效率"},
                    "history_days": 7
                }
            }
        ],

        "37_child_nutrition_meal_planner": [
            {
                "user_query": "孩子挑食，不爱吃蔬菜，有什么方法让他愿意吃？",
                "payload": {
                    "child_profile": {"age": "5岁", "nickname": "小挑食"},
                    "family_context": {"caregiver": "父母", "available_time": "每天1小时做饭"},
                    "current_problem": "严重挑食，不吃蔬菜",
                    "goal": "制定让孩子接受蔬菜的方案",
                    "raw_records": [
                        {"time": "2024-05-20", "meal": "午餐", "foods": ["米饭", "红烧肉"], "accepted": ["米饭"], "rejected": ["青菜", "西兰花"], "note": "只吃肉"},
                    ],
                    "preferences": {"tone": "创意", "priority": "营养均衡"},
                    "history_days": 7
                }
            }
        ],

        "46_child_book_recommender": [
            {
                "user_query": "儿子8岁，不爱看书只爱玩电子产品，有什么书能吸引他？",
                "payload": {
                    "child_profile": {"age": "8岁", "nickname": "小玩家", "grade": "小学二年级"},
                    "family_context": {"caregiver": "父母", "available_time": ""},
                    "current_problem": "不爱阅读，沉迷电子产品",
                    "goal": "推荐能吸引他的书籍",
                    "raw_records": [
                        {"time": "2024-05-01", "book": "《十万个为什么》", "rating": 2, "note": "翻了几页不要看"},
                        {"time": "2024-04-15", "book": "《米小圈上学记》", "rating": 4, "note": "喜欢"},
                    ],
                    "preferences": {"tone": "有趣", "priority": "引起兴趣", "formats": ["漫画", "故事书"]},
                    "history_days": 30
                }
            }
        ],

        "49_parent_emotion_management": [
            {
                "user_query": "辅导作业时对孩子发火了，事后很后悔，怎么调整？",
                "payload": {
                    "child_profile": {"age": "7岁", "nickname": "小磨蹭"},
                    "family_context": {"caregiver": "妈妈", "available_time": ""},
                    "current_problem": "情绪失控，对孩子发火",
                    "goal": "情绪管理，修复亲子关系",
                    "raw_records": [
                        {"time": "2024-05-20 19:00", "emotion": "愤怒", "trigger": "作业讲3遍不会", "intensity": 9, "action": "吼叫", "after_effect": "后悔"}
                    ],
                    "preferences": {"tone": "同理", "priority": "自我修复"},
                    "history_days": 7
                }
            }
        ],

        "50_family_meeting_facilitator": [
            {
                "user_query": "家里老人总是溺爱孩子，我们怎么统一教育方式？",
                "payload": {
                    "child_profile": {"age": "5岁", "nickname": "小霸王"},
                    "family_context": {"caregiver": "父母+祖父母", "available_time": ""},
                    "current_problem": "老人溺爱，教育方式不统一",
                    "goal": "召开家庭会议，统一教育理念",
                    "raw_records": [
                        {"time": "2024-05-15", "issue": "孩子要什么给什么", "person": "奶奶", "note": "溺爱"},
                        {"time": "2024-05-18", "issue": "孩子打妈妈", "person": "爷爷", "note": "护着"}
                    ],
                    "preferences": {"tone": "中立", "priority": "家庭和谐"},
                    "history_days": 30
                }
            }
        ],

    }

    return scenarios


def test_skill_with_query(skill_dir: Path, test_case: Dict[str, Any]) -> Dict[str, Any]:
    """使用真实用户问题测试单个skill。"""
    runner_path = skill_dir / "src" / "runner.py"
    manifest_path = skill_dir / "manifest.json"

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"error": f"Failed to load manifest: {e}"}

    mod = load_module(runner_path)
    if mod is None:
        print(f"[DEBUG] load_module returned None for {skill_dir.name}")
        return {"error": "Failed to load module"}

    result = {
        "skill_id": manifest.get("skill_id", "unknown"),
        "skill_name": manifest.get("name", "unknown"),
        "category": manifest.get("category", "unknown"),
        "user_query": test_case["user_query"],
        "passed": False,
        "output_analysis": {},
        "error": None
    }

    start_time = datetime.now()

    try:
        output = mod.run(test_case["payload"])
        result["execution_time"] = (datetime.now() - start_time).total_seconds()

        result["output_analysis"] = {
            "has_summary": bool(output.get("summary")),
            "summary_length": len(str(output.get("summary", ""))),
            "summary_preview": str(output.get("summary", ""))[:200] if output.get("summary") else "",

            "has_analysis": bool(output.get("analysis")),
            "analysis_count": len(output.get("analysis", [])),

            "has_action_plan": bool(output.get("action_plan")),
            "action_plan_count": len(output.get("action_plan", [])),

            "has_risk_notes": bool(output.get("risk_notes")),
            "risk_notes_count": len(output.get("risk_notes", [])),

            "has_markdown_report": bool(output.get("markdown_report")),
            "report_length": len(str(output.get("markdown_report", ""))),

            "has_deliverables": bool(output.get("deliverables")),
            "deliverables_keys": list(output.get("deliverables", {}).keys()) if output.get("deliverables") else [],

            "total_fields": list(output.keys()),
        }

        if result["output_analysis"]["has_summary"] and \
           result["output_analysis"]["has_action_plan"] and \
           result["output_analysis"]["has_markdown_report"]:
            result["passed"] = True

        result["full_output"] = output

    except Exception as e:
        result["error"] = str(e)
        result["traceback"] = traceback.format_exc()

    return result


def generate_report(all_results: List[Dict[str, Any]]) -> str:
    """生成详细分析报告。"""
    lines = []
    lines.append("# 育儿智能体Skill真实场景测试报告")
    lines.append("")
    lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append(f"**测试Skill数量**: {len(all_results)}")
    lines.append("")

    passed = sum(1 for r in all_results if r.get("passed"))
    lines.append(f"**通过数量**: {passed}/{len(all_results)} ({passed/len(all_results)*100:.0f}%)")
    lines.append("")

    lines.append("## 测试结果概览")
    lines.append("")
    lines.append("| Skill名称 | 类别 | 用户问题 | 状态 | 分析质量 |")
    lines.append("|----------|------|----------|------|----------|")

    for r in all_results:
        error_val = r.get("error")
        if error_val and error_val != "Failed to load module":
            lines.append(f"| {r.get('skill_name', 'N/A')} | {r.get('category', 'N/A')} | - | ❌ | 运行失败 |")
        else:
            analysis = r.get("output_analysis", {})
            quality = "✅优秀" if analysis.get("has_markdown_report") and analysis.get("report_length", 0) > 500 else \
                      "⚠️一般" if analysis.get("has_markdown_report") else "❌缺失"
            status = "✅通过" if r.get("passed") else "❌失败"
            query_preview = r.get("user_query", "")[:30] + "..." if len(r.get("user_query", "")) > 30 else r.get("user_query", "")
            lines.append(f"| {r['skill_name']} | {r['category']} | {query_preview} | {status} | {quality} |")

    lines.append("")
    lines.append("## 详细测试结果")
    lines.append("")

    for r in all_results:
        if "error" in r:
            lines.append(f"### ❌ {r.get('skill_name', 'Unknown')}")
            lines.append("")
            lines.append(f"**错误**: {r['error']}")
            lines.append("")
            continue

        lines.append(f"### {'✅' if r.get('passed') else '❌'} {r['skill_name']}")
        lines.append("")
        lines.append(f"**类别**: {r.get('category', 'N/A')}")
        lines.append("")
        lines.append("#### 用户问题")
        lines.append("")
        lines.append(f"> {r.get('user_query', 'N/A')}")
        lines.append("")

        analysis = r.get("output_analysis", {})

        lines.append("#### 输出分析")
        lines.append("")
        lines.append(f"- **有摘要**: {'✅ 是' if analysis.get('has_summary') else '❌ 否'}")
        lines.append(f"- **摘要长度**: {analysis.get('summary_length', 0)} 字符")
        lines.append(f"- **有分析**: {'✅ 是' if analysis.get('has_analysis') else '❌ 否'} ({analysis.get('analysis_count', 0)} 条)")
        lines.append(f"- **有行动计划**: {'✅ 是' if analysis.get('has_action_plan') else '❌ 否'} ({analysis.get('action_plan_count', 0)} 条)")
        lines.append(f"- **有风险提示**: {'✅ 是' if analysis.get('has_risk_notes') else '❌ 否'} ({analysis.get('risk_notes_count', 0)} 条)")
        lines.append(f"- **有Markdown报告**: {'✅ 是' if analysis.get('has_markdown_report') else '❌ 否'}")
        lines.append(f"- **报告长度**: {analysis.get('report_length', 0)} 字符")
        lines.append(f"- **有交付物**: {'✅ 是' if analysis.get('has_deliverables') else '❌ 否'}")
        if analysis.get("deliverables_keys"):
            lines.append(f"- **交付物字段**: {', '.join(analysis.get('deliverables_keys', []))}")
        lines.append(f"- **执行时间**: {r.get('execution_time', 0):.3f}s")
        lines.append("")

        if analysis.get("summary_preview"):
            lines.append("#### 摘要预览")
            lines.append("")
            lines.append(f"```\n{analysis['summary_preview'][:300]}...\n```")
            lines.append("")

        lines.append("**输出字段**:")
        lines.append("```")
        lines.append(', '.join(sorted(analysis.get("total_fields", []))))
        lines.append("```")
        lines.append("")

    lines.append("---")
    lines.append("*本报告由自动化端到端测试脚本生成*")

    return "\n".join(lines)


def main():
    """运行所有skill的端到端测试。"""
    print("🎯 开始运行真实场景测试...")
    print("=" * 60)

    all_results = []
    scenarios = get_test_scenarios()

    for skill_dir in sorted(SKILLS.iterdir()):
        if not skill_dir.is_dir():
            continue

        skill_name = skill_dir.name

        if skill_name in scenarios:
            test_case = scenarios[skill_name][0]
        else:
            sample_path = skill_dir / "examples" / "sample_input.json"
            payload = json.loads(sample_path.read_text(encoding="utf-8"))
            test_case = {
                "user_query": payload.get("current_problem", f"{skill_name} 示例端到端场景"),
                "payload": payload,
            }

        print(f"\n📝 测试 Skill: {skill_name}")
        print(f"   用户问题: {test_case['user_query'][:50]}...")

        result = test_skill_with_query(skill_dir, test_case)

        error_val = result.get("error")
        if error_val:
            print(f"   ❌ 失败: {error_val}")
        else:
            analysis = result.get("output_analysis", {})
            status = "✅" if result.get("passed") else "❌"
            print(f"   {status} | 摘要:{analysis.get('summary_length', 0)}字符 | 报告:{analysis.get('report_length', 0)}字符")

        all_results.append(result)

    print("\n" + "=" * 60)
    print("📊 生成测试报告...")

    report = generate_report(all_results)
    report_path = REPORT_DIR / f"e2e_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"✅ 报告已保存至: {report_path}")

    latest_path = REPORT_DIR / "e2e_test_report_latest.md"
    latest_path.write_text(report, encoding="utf-8")
    print(f"✅ 最新报告: {latest_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
