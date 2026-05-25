import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "src" / "runner.py"
SAMPLE_INPUT = ROOT / "examples" / "sample_input.json"


def load_runner():
    spec = importlib.util.spec_from_file_location("runner_under_test", RUNNER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_run_smoke():
    runner = load_runner()
    payload = json.loads(SAMPLE_INPUT.read_text(encoding="utf-8"))
    result = runner.run(payload)
    assert result["skill_id"] == "extracurricular_class_selection"
    assert result["summary"]
    assert result["action_plan"]
    assert result["risk_notes"]
