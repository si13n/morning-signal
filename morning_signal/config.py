from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle) or {}
    if not isinstance(value, dict):
        raise ValueError("Expected a YAML mapping in %s" % path)
    return value


def load_interests(root: Path) -> Dict[str, Any]:
    return load_yaml(root / "config" / "interests.yaml")


def load_sources(root: Path) -> Dict[str, Any]:
    return load_yaml(root / "config" / "sources.yaml")


def env_int(name: str, default: int, minimum: int = 1) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError("%s must be an integer" % name) from exc
    if value < minimum:
        raise ValueError("%s must be at least %d" % (name, minimum))
    return value


def runtime_config(root: Path) -> Dict[str, Any]:
    min_digest_items = env_int("MIN_DIGEST_ITEMS", 20)
    max_digest_items = env_int("MAX_DIGEST_ITEMS", 25)
    if min_digest_items > max_digest_items:
        raise ValueError("MIN_DIGEST_ITEMS cannot exceed MAX_DIGEST_ITEMS")
    return {
        "model": os.getenv("OPENAI_MODEL", "gpt-5-mini"),
        "max_web_searches": env_int("MAX_WEB_SEARCHES", 6),
        "min_digest_items": min_digest_items,
        "max_digest_items": max_digest_items,
        "lookback_hours": env_int("LOOKBACK_HOURS", 72),
        "max_candidates": env_int("MAX_CANDIDATES", 40),
        "root": root,
    }
