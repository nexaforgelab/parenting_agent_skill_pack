"""Validate all generated parenting skills."""
from __future__ import annotations

import importlib.util
import json
import importlib
from pathlib import Path
import traceback
import sys
import types
import uuid

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


def load_module(path: Path):
    """加载skill的runner模块，使用唯一模块名避免冲突。"""
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

            for key in list(sys.modules.keys()):
                if module_name in key or src_dir in key:
                    pass

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


def main() -> int:
    failures = []
    count = 0
    for skill_dir in sorted(SKILLS.iterdir()):
        if not skill_dir.is_dir():
            continue
        count += 1
        runner_path = skill_dir / "src" / "runner.py"
        manifest_path = skill_dir / "manifest.json"
        sample_path = skill_dir / "examples" / "sample_input.json"
        try:
            assert runner_path.exists(), "missing runner.py"
            assert manifest_path.exists(), "missing manifest.json"
            assert sample_path.exists(), "missing sample_input.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            payload = json.loads(sample_path.read_text(encoding="utf-8"))
            mod = load_module(runner_path)
            if mod is None:
                raise ImportError("Failed to load module")
            result = mod.run(payload)
            assert result["skill_id"] == manifest["skill_id"]
            assert result["summary"]
            assert result["action_plan"]
            assert result["risk_notes"]
        except Exception as exc:
            failures.append((skill_dir.name, str(exc), traceback.format_exc()))

    print(f"checked={count}, failures={len(failures)}")
    for name, err, tb in failures:
        print(f"FAIL {name}: {err}")
        print(tb)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())