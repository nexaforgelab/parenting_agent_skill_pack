"""Pytest isolation for the generated skill package.

Each skill owns modules with the same top-level names, such as ``planner`` and
``validators``. The individual smoke tests load runners by file path, so pytest
needs to clear those transient imports between skills.
"""
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SKILLS_DIR = ROOT / "skills"
LOCAL_MODULE_NAMES = {
    "analytics",
    "communication",
    "models",
    "planner",
    "progress",
    "reporting",
    "runner_under_test",
    "validators",
}


def _is_skill_src_path(raw_path: str) -> bool:
    try:
        path = Path(raw_path).resolve()
    except (OSError, RuntimeError):
        return False

    return path.name == "src" and path.parent.parent == SKILLS_DIR


def pytest_runtest_setup(item):  # type: ignore[no-untyped-def]
    for module_name in list(sys.modules):
        root_name = module_name.split(".", 1)[0]
        if root_name in LOCAL_MODULE_NAMES:
            del sys.modules[module_name]

    sys.path[:] = [path for path in sys.path if not _is_skill_src_path(path)]
