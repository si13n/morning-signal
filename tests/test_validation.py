import copy
import json
from pathlib import Path

import pytest

from morning_signal.schema import DigestValidationError, validate_digest


ROOT = Path(__file__).resolve().parents[1]


def fixture_digest():
    return json.loads((ROOT / "data" / "2026-08-18.json").read_text(encoding="utf-8"))


def test_fixture_digest_is_valid():
    validate_digest(fixture_digest())


def test_required_fields_are_checked():
    digest = fixture_digest()
    del digest["top_signal"]["why_it_matters"]
    with pytest.raises(DigestValidationError, match="missing required fields"):
        validate_digest(digest)


def test_invalid_priority_is_rejected():
    digest = fixture_digest()
    digest["top_signal"]["priority"] = 11
    with pytest.raises(DigestValidationError, match="between 1 and 10"):
        validate_digest(digest)


def test_invalid_url_is_rejected():
    digest = fixture_digest()
    digest["top_signal"]["source_url"] = "not-a-url"
    with pytest.raises(DigestValidationError, match="valid http"):
        validate_digest(digest)


def test_duplicate_links_are_rejected():
    digest = fixture_digest()
    story = copy.deepcopy(digest["top_signal"])
    story["title"] = "A distinct story"
    digest["items"] = [story]
    with pytest.raises(DigestValidationError, match="duplicate source_url"):
        validate_digest(digest)


def test_duplicate_titles_are_rejected():
    digest = fixture_digest()
    first = copy.deepcopy(digest["top_signal"])
    first["title"] = "Same title"
    first["source_url"] = "https://example.com/first"
    second = copy.deepcopy(first)
    second["source_url"] = "https://example.com/second"
    digest["items"] = [first, second]
    with pytest.raises(DigestValidationError, match="duplicate or near-duplicate"):
        validate_digest(digest)


def test_near_duplicate_titles_are_rejected():
    digest = fixture_digest()
    first = copy.deepcopy(digest["top_signal"])
    first["title"] = "Playwright improves test setup"
    first["source_url"] = "https://example.com/first"
    second = copy.deepcopy(first)
    second["title"] = "Playwright improves test setup today"
    second["source_url"] = "https://example.com/second"
    digest["top_signal"] = first
    digest["items"] = [second]
    with pytest.raises(DigestValidationError, match="duplicate or near-duplicate"):
        validate_digest(digest)


def test_item_limit_is_checked():
    digest = fixture_digest()
    for index in range(3):
        story = copy.deepcopy(digest["top_signal"])
        story["title"] = "Story %d" % index
        story["source_url"] = "https://example.com/%d" % index
        digest["items"].append(story)
    with pytest.raises(DigestValidationError, match="maximum of 2"):
        validate_digest(digest, max_items=2)


def test_minimum_story_count_is_checked():
    digest = fixture_digest()
    digest["items"] = digest["items"][:3]
    digest["watch"] = []
    digest["learning"] = []
    with pytest.raises(DigestValidationError, match="minimum is 20"):
        validate_digest(digest, min_items=20)
