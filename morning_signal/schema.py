from __future__ import annotations

import re
from difflib import SequenceMatcher
from datetime import date
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urlparse


STORY_PROPERTIES = {
    "title": {"type": "string"},
    "category": {"type": "string"},
    "priority": {"type": "integer", "minimum": 1, "maximum": 10},
    "summary": {"type": "string"},
    "why_it_matters": {"type": "string"},
    "source": {"type": "string"},
    "source_url": {"type": "string"},
    "published_at": {"type": "string"},
}
STORY_STRING_FIELDS = ("title", "category", "summary", "why_it_matters", "source", "source_url", "published_at")

STORY_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": STORY_PROPERTIES,
    "required": list(STORY_PROPERTIES),
}

DIGEST_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "date": {"type": "string"},
        "headline": {"type": "string"},
        "top_signal": STORY_SCHEMA,
        "items": {"type": "array", "items": STORY_SCHEMA, "maxItems": 17},
        "watch": {"type": "array", "items": STORY_SCHEMA, "maxItems": 1},
        "learning": {"type": "array", "items": STORY_SCHEMA, "maxItems": 1},
    },
    "required": ["date", "headline", "top_signal", "items", "watch", "learning"],
}

URL_RE = re.compile(r"^https?://", re.IGNORECASE)


class DigestValidationError(ValueError):
    pass


def _check_story(story: Any, label: str) -> None:
    if not isinstance(story, dict):
        raise DigestValidationError("%s must be an object" % label)
    missing = [key for key in STORY_PROPERTIES if key not in story]
    if missing:
        raise DigestValidationError("%s missing required fields: %s" % (label, ", ".join(missing)))
    if not isinstance(story["priority"], int) or isinstance(story["priority"], bool):
        raise DigestValidationError("%s priority must be an integer" % label)
    if not 1 <= story["priority"] <= 10:
        raise DigestValidationError("%s priority must be between 1 and 10" % label)
    for key in STORY_STRING_FIELDS:
        if not isinstance(story[key], str) or not story[key].strip():
            raise DigestValidationError("%s.%s must be a non-empty string" % (label, key))
    parsed = urlparse(story["source_url"])
    if not URL_RE.match(story["source_url"]) or not parsed.netloc:
        raise DigestValidationError("%s source_url must be a valid http(s) URL" % label)


def validate_digest(digest: Dict[str, Any], max_items: int = 20, expected_date: Optional[str] = None) -> None:
    if not isinstance(digest, dict):
        raise DigestValidationError("Digest must be an object")
    required = ["date", "headline", "top_signal", "items", "watch", "learning"]
    missing = [key for key in required if key not in digest]
    if missing:
        raise DigestValidationError("Digest missing required fields: %s" % ", ".join(missing))
    try:
        date.fromisoformat(digest["date"])
    except (TypeError, ValueError) as exc:
        raise DigestValidationError("date must use YYYY-MM-DD") from exc
    if expected_date and digest["date"] != expected_date:
        raise DigestValidationError("Digest date %s does not match %s" % (digest["date"], expected_date))
    if not isinstance(digest["headline"], str) or not digest["headline"].strip():
        raise DigestValidationError("headline must be a non-empty string")
    _check_story(digest["top_signal"], "top_signal")
    for section in ("items", "watch", "learning"):
        if not isinstance(digest[section], list):
            raise DigestValidationError("%s must be an array" % section)
        for index, story in enumerate(digest[section]):
            _check_story(story, "%s[%d]" % (section, index))
    if len(digest["items"]) > max_items:
        raise DigestValidationError("items exceeds maximum of %d" % max_items)
    stories: List[Dict[str, Any]] = [digest["top_signal"]]
    for section in ("items", "watch", "learning"):
        stories.extend(digest[section])
    urls = [story["source_url"].rstrip("/") for story in stories]
    if len(urls) != len(set(urls)):
        raise DigestValidationError("duplicate source_url values are not allowed")
    normalized_titles = []
    for story in stories:
        title = re.sub(r"[^a-z0-9]+", " ", story["title"].lower()).strip()
        normalized_titles.append(title)
    if len(normalized_titles) != len(set(normalized_titles)):
        raise DigestValidationError("duplicate or near-duplicate story titles are not allowed")
    if len(stories) > max_items:
        raise DigestValidationError("digest exceeds maximum of %d stories" % max_items)
    for index, title in enumerate(normalized_titles):
        for other in normalized_titles[index + 1:]:
            if SequenceMatcher(None, title, other).ratio() >= 0.90:
                raise DigestValidationError("duplicate or near-duplicate story titles are not allowed")


def validate_many(digests: Iterable[Dict[str, Any]], max_items: int = 20) -> None:
    for digest in digests:
        validate_digest(digest, max_items=max_items)
