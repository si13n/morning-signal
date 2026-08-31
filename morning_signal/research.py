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
    return """Create the Morning Signal QA digest for %s.

Audience: a senior QA Automation Engineer / QA Lead. This is a QA-only publication. Include only developments with direct, concrete relevance to software quality, testing, or test automation.

Primary scope:
- QA automation and quality engineering
- Agentic QA: agents used for test design, test generation, test execution, exploratory testing, failure triage, flaky-test investigation, healing, root-cause analysis, and quality governance
- AI for QA and AI-assisted testing
- testing and evaluation of AI/LLM-powered products when the focus is software quality, eval design, reliability, or validation
- mobile QA and automation: Appium, Espresso, XCUITest, Maestro, device farms, SDK testing
- web/API automation: Playwright, Cypress, Selenium, Pytest and related QA frameworks
- test infrastructure, test observability, test reliability, testability and test data
- performance, load and stress testing
- CI quality gates and release quality only when directly connected to testing or QA
- major QA tools, testing documentation, QA-focused engineering posts, talks, research, benchmarks and practical approaches

Strict scope rules:
- Do NOT include generic AI news, generic agentic engineering, coding-agent news, model releases, developer tooling, cloud/platform news, programming-language news, company news, acquisitions, product launches, security news, or CI/CD news unless the item has a clear and substantial QA/testing impact.
- A coding agent is relevant only when it is being used for QA/testing, test maintenance, validation, debugging, quality gates, or independent verification.
- Android/iOS/platform releases are relevant only when they materially affect testing strategy, automation compatibility, device coverage, SDK validation, or test infrastructure.
- Observability is relevant only when applied to test diagnostics, flaky-test investigation, QA evidence, or quality validation.
- AI/LLM research is relevant only when it teaches us how to test, evaluate, validate, or improve reliability of AI-powered software.
- Do not fill the digest with adjacent technology news just to reach the minimum story count. If fewer high-quality QA stories exist, prefer the most directly relevant verified QA items available within the lookback window.

Editorial rules:
- Use primary sources whenever possible and preserve the exact source URL.
- Explain what happened and why it matters to a Senior QA Automation Engineer / QA Lead in concise, non-hyped language. Keep each summary to roughly 35 words and each why-it-matters field to roughly 25 words so the full edition fits the output budget.
- Do not invent facts, dates, links, or quotes. Drop a candidate if it cannot be verified.
- You may use web search to fill gaps or verify important developments, but use no more than %d focused searches. Web searches must be QA/testing-focused, not broad technology searches.
- Return at least %d and no more than %d concise stories across `top_signal`, `items`, `watch`, and `learning`; use only genuinely QA-relevant stories. Use at most one `watch` and one `learning` item.
- Every story must have a unique `source_url` across all sections. `top_signal` must be the single most useful QA signal and must not duplicate any other story.
- Use `watch` only for credible QA/testing events, releases or developments worth monitoring.
- Use `learning` only for QA/testing documentation, talks, tutorials, research or techniques worth learning today.

Personalization:
high priority: %s
medium priority: %s
career focus: %s
low priority to avoid: %s

Candidate feed entries:
%s

Ignore candidate feed entries that do not meet the QA-only scope, even if their source quality is high.

Return only the requested JSON schema. The date must be %s.""" % (
        issue_date,
        max_searches,
        min_items,
        max_items,
        ", ".join(interests.get("high_priority", [])),
        ", ".join(interests.get("medium_priority", [])),
        ", ".join(interests.get("career_focus", [])),
        ", ".join(interests.get("low_priority", [])),
        "\n".join(candidate_lines) or "No feed candidates were available; use QA-focused web search sparingly.",
        issue_date,
    )


def create_digest(candidates: List[Dict[str, Any]], interests: Dict[str, Any], issue_date: str, model: str, max_items: int, max_searches: int, min_items: int = 0, max_output_tokens: int = 30000) -> Dict[str, Any]:
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
                "content": "You are a careful senior QA technical editor. Publish only QA/testing-relevant stories. Do not fabricate. Follow the JSON schema exactly.",
            },
            {"role": "user", "content": _prompt(candidates, interests, issue_date, max_items, max_searches, min_items)},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "morning_signal_digest",
                "description": "A concise, source-grounded QA-only Morning Signal digest.",
                "schema": DIGEST_SCHEMA,
                "strict": True,
            }
        },
        max_tool_calls=max_searches,
        parallel_tool_calls=False,
        max_output_tokens=max_output_tokens,
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
