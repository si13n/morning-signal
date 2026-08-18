from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List

from jinja2 import Environment, FileSystemLoader, select_autoescape


def _date_label(value: str) -> str:
    return datetime.strptime(value, "%Y-%m-%d").strftime("%A, %B %-d, %Y")


def _short_date(value: str) -> str:
    return datetime.strptime(value, "%Y-%m-%d").strftime("%b %-d").upper()


def _story_count(digest: Dict[str, Any]) -> int:
    return 1 + len(digest["items"]) + len(digest["watch"]) + len(digest["learning"])


def make_environment(root: Path) -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(root / "templates")),
        autoescape=select_autoescape(["html", "xml"]),
    )
    env.filters["date_label"] = _date_label
    env.filters["short_date"] = _short_date
    return env


def render_digest(root: Path, digest: Dict[str, Any], output: Path, base_path: str = "../") -> None:
    template = make_environment(root).get_template("digest.html.j2")
    html = template.render(
        digest=digest,
        date_label=_date_label(digest["date"]),
        story_count=_story_count(digest),
        base_path=base_path,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")


def render_archive_index(root: Path, digests: Iterable[Dict[str, Any]], output: Path) -> None:
    sorted_digests = sorted(digests, key=lambda item: item["date"], reverse=True)
    template = make_environment(root).get_template("archive.html.j2")
    html = template.render(digests=sorted_digests, base_path="../")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")


def render_site(root: Path, data_dir: Path, staging: Path) -> List[Dict[str, Any]]:
    from .schema import validate_digest

    digests: List[Dict[str, Any]] = []
    for path in sorted(data_dir.glob("*.json")):
        digest = json.loads(path.read_text(encoding="utf-8"))
        validate_digest(digest, expected_date=path.stem)
        digests.append(digest)
    if not digests:
        raise ValueError("No digest JSON files found")
    digests.sort(key=lambda item: item["date"], reverse=True)
    staging.mkdir(parents=True, exist_ok=True)
    (staging / "assets").mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / "assets" / "style.css", staging / "assets" / "style.css")
    latest = digests[0]
    render_digest(root, latest, staging / "index.html", base_path="./")
    for digest in digests:
        render_digest(root, digest, staging / "archive" / (digest["date"] + ".html"), base_path="../")
    render_archive_index(root, digests, staging / "archive" / "index.html")
    return digests
