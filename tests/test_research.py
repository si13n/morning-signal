import copy
import json
import sys
import types
from pathlib import Path

import pytest

from morning_signal.research import create_digest


ROOT = Path(__file__).resolve().parents[1]


def test_responses_api_contract_uses_web_search_and_structured_output(monkeypatch):
    fixture = json.loads((ROOT / "data" / "2026-08-18.json").read_text(encoding="utf-8"))
    calls = []

    class FakeResponses:
        def create(self, **kwargs):
            calls.append(kwargs)
            output = [
                types.SimpleNamespace(
                    type="web_search_call",
                    action=types.SimpleNamespace(type="search"),
                )
                for _ in range(12)
            ]
            return types.SimpleNamespace(output_text=json.dumps(fixture), output=output)

    class FakeClient:
        def __init__(self):
            self.responses = FakeResponses()

    monkeypatch.setitem(sys.modules, "openai", types.SimpleNamespace(OpenAI=FakeClient))
    result = create_digest([], {"high_priority": [], "medium_priority": [], "career_focus": [], "low_priority": []}, "2026-08-18", "gpt-5-mini", 10, 6)

    assert result["date"] == "2026-08-18"
    assert calls[0]["model"] == "gpt-5-mini"
    assert calls[0]["tools"] == [{"type": "web_search", "search_context_size": "low"}]
    assert calls[0]["max_tool_calls"] == 6
    assert calls[0]["max_output_tokens"] == 30000
    assert calls[0]["parallel_tool_calls"] is False
    assert calls[0]["text"]["format"]["type"] == "json_schema"
    assert calls[0]["text"]["format"]["strict"] is True
    assert calls[0]["store"] is False


def test_response_deduplicates_source_urls_across_sections(monkeypatch):
    fixture = json.loads((ROOT / "data" / "2026-08-18.json").read_text(encoding="utf-8"))
    duplicate = copy.deepcopy(fixture)
    duplicate["items"][0]["source_url"] = duplicate["top_signal"]["source_url"]
    duplicate["watch"][0]["source_url"] = duplicate["items"][1]["source_url"]

    class FakeResponses:
        def create(self, **kwargs):
            return types.SimpleNamespace(output_text=json.dumps(duplicate), output=[])

    class FakeClient:
        def __init__(self):
            self.responses = FakeResponses()

    monkeypatch.setitem(sys.modules, "openai", types.SimpleNamespace(OpenAI=FakeClient))
    result = create_digest([], {"high_priority": [], "medium_priority": [], "career_focus": [], "low_priority": []}, "2026-08-18", "gpt-5-mini", 10, 6)

    stories = [result["top_signal"]] + result["items"] + result["watch"] + result["learning"]
    urls = [story["source_url"].rstrip("/") for story in stories]
    assert len(urls) == len(set(urls))
    assert result["top_signal"]["source_url"] == fixture["top_signal"]["source_url"]
    assert len(result["items"]) == len(fixture["items"]) - 1
    assert result["watch"] == []


def test_response_below_minimum_story_count_is_rejected(monkeypatch):
    fixture = json.loads((ROOT / "data" / "2026-08-18.json").read_text(encoding="utf-8"))
    undersized = copy.deepcopy(fixture)
    undersized["items"] = undersized["items"][:3]
    undersized["watch"] = []
    undersized["learning"] = []

    class FakeResponses:
        def create(self, **kwargs):
            return types.SimpleNamespace(output_text=json.dumps(undersized), output=[])

    class FakeClient:
        def __init__(self):
            self.responses = FakeResponses()

    monkeypatch.setitem(sys.modules, "openai", types.SimpleNamespace(OpenAI=FakeClient))
    with pytest.raises(RuntimeError, match="at least 20"):
        create_digest([], {"high_priority": [], "medium_priority": [], "career_focus": [], "low_priority": []}, "2026-08-18", "gpt-5-mini", 25, 6, 20)
