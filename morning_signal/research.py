from __future__ import annotations

import json
from datetime import date
from typing import Any, Dict, List

from .schema import DIGEST_SCHEMA


def _deduplicate_source_urls(digest: Dict[str, Any]) -> int:
    """Remove later stories that reuse a source URL from an earlier section."""
    seen = {digest["top_signal"]["source_url"].rstrip("/")}
    removed = 0
    for section in ("items", "watch", "learning"):
        unique = []
        for story in digest[section]:
            canonical_url = story["source_url"].rstrip("/")
            if canonical_url in seen:
                removed += 1
                continue
            seen.add(canonical_url)
            unique.append(story)
        digest[section] = unique
    return removed


def _prompt(candidates: List[Dict[str, Any]], interests: Dict[str, Any], issue_date: str, max_items: int, max_searches: int, min_items: int = 0) -> str:
    candidate_lines = []
    for index, item in enumerate(candidates):
        candidate_lines.append(
            "%d. %s | %s | %s | %s | %s" % (
                index + 1,
                item["title"],
                item["source"],
                item["published_at"],
                item["url"],
                item.get("summary", "")[:300],
            )
        )
    return """Create the Morning Signal technology digest for %s.

Audience: a senior QA automation / agentic engineering practitioner. Prioritize practical, verifiable developments in QA automation, AI agents, LLM evals, RAG evaluation, mobile QA, Android, Maestro, Espresso, SDK testing, Python/Pytest, TypeScript/Playwright, GitHub Actions, CI/CD, test infrastructure, observability, flaky-test investigation, device farms, BrowserStack, engineering blogs, releases, documentation, and useful talks.

Editorial rules:
- Use primary sources whenever possible and preserve the exact source URL.
- Explain what happened and why it matters in concise, non-hyped language.
- Do not invent facts, dates, links, or quotes. Drop a candidate if it cannot be verified.
- Avoid generic consumer AI, funding, cryptocurrency, gadgets, and celebrity news.
- You may use web search to fill gaps or verify important developments, but use no more than %d focused searches. Return at least %d and no more than %d concise stories across `top_signal`, `items`, `watch`, and `learning`; do not stop after a small handful when more verified candidates are available. Use at most one `watch` and one `learning` item.
- Every story must have a unique `source_url` across all sections. `top_signal` must be the single most useful signal and must not duplicate any other story.
- Use `watch` for credible things worth monitoring and `learning` for one or two genuinely useful docs/talks/tutorials.

Personalization:
high priority: %s
medium priority: %s
career focus: %s
low priority to avoid: %s

Candidate feed entries:
%s

Return only the requested JSON schema. The date must be %s.""" % (
        issue_date,
        max_searches,
        min_items,
        max_items,
        ", ".join(interests.get("high_priority", [])),
        ", ".join(interests.get("medium_priority", [])),
        ", ".join(interests.get("career_focus", [])),
        ", ".join(interests.get("low_priority", [])),
        "\n".join(candidate_lines) or "No feed candidates were available; use web search sparingly.",
        issue_date,
    )


def create_digest(candidates: List[Dict[str, Any]], interests: Dict[str, Any], issue_date: str, model: str, max_items: int, max_searches: int, min_items: int = 0) -> Dict[str, Any]:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("The openai package is required for live digest generation") from exc
    client = OpenAI()
    response = client.responses.create(
        model=model,
        tools=[{"type": "web_search", "search_context_size": "low"}],
        input=[
            {
                "role": "developer",
                "content": "You are a careful technical editor. Do not fabricate. Follow the JSON schema exactly.",
            },
            {"role": "user", "content": _prompt(candidates, interests, issue_date, max_items, max_searches, min_items)},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "morning_signal_digest",
                "description": "A concise, source-grounded Morning Signal digest.",
                "schema": DIGEST_SCHEMA,
                "strict": True,
            }
        },
        max_tool_calls=max_searches,
        parallel_tool_calls=False,
        max_output_tokens=12000,
        store=False,
    )
    search_calls = sum(
        1
        for item in (getattr(response, "output", None) or [])
        if getattr(item, "type", "") == "web_search_call"
        and getattr(getattr(item, "action", None), "type", "") == "search"
    )
    if search_calls > max_searches:
        print("research warning: response reported %d search actions (configured cap: %d)" % (search_calls, max_searches))
    status = getattr(response, "status", None)
    if status and status != "completed":
        details = getattr(response, "incomplete_details", None)
        reason = getattr(details, "reason", "unknown")
        raise RuntimeError("OpenAI response was not complete: %s" % reason)
    output = getattr(response, "output_text", "")
    if not output:
        raise RuntimeError("OpenAI returned no structured output")
    try:
        digest = json.loads(output)
    except json.JSONDecodeError as exc:
        raise RuntimeError("OpenAI returned invalid JSON") from exc
    if digest.get("date") != issue_date:
        raise RuntimeError("OpenAI returned the wrong digest date")
    removed = _deduplicate_source_urls(digest)
    if removed:
        print("research warning: removed %d story/stories with duplicate source_url values" % removed)
    story_count = 1 + len(digest["items"]) + len(digest["watch"]) + len(digest["learning"])
    if story_count < min_items:
        raise RuntimeError("OpenAI returned %d stories; at least %d are required" % (story_count, min_items))
    return digest
