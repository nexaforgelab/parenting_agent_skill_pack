"""Shared helpers for the Parenting Agent Skill Pack."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def merge_context(*parts: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {}
    for part in parts:
        if isinstance(part, dict):
            merged.update(part)
    return merged


def classify_review_cycle(history_days: int) -> str:
    if history_days <= 1:
        return "daily"
    if history_days <= 14:
        return "weekly"
    return "monthly"
