import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "src" / "runner.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("runner_under_test", RUNNER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_run_smoke():
    runner = load_runner()
    payload = {
        "child_profile": {"age": "示例年龄/月龄"},
        "family_context": {"caregiver": "父母"},
        "current_problem": "这是一个测试问题",
        "goal": "生成家庭执行方案",
        "raw_records": [{"time": "today", "event": "sample"}],
        "history_days": 7,
    }
    result = runner.run(payload)
    assert result["skill_id"] == "middle_school_exam_goal_breakdown"
    assert result["summary"]
    assert result["action_plan"]
    assert result["risk_notes"]
