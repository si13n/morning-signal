from __future__ import annotations

import calendar
import re
import time
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Dict, List
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import feedparser


def _published(entry: Any) -> datetime:
    for key in ("published", "updated", "created"):
        value = entry.get(key)
        if value:
            try:
                parsed = parsedate_to_datetime(value)
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                return parsed.astimezone(timezone.utc)
            except (TypeError, ValueError, IndexError):
                pass
    for key in ("published_parsed", "updated_parsed"):
        value = entry.get(key)
        if value:
            return datetime.fromtimestamp(calendar.timegm(value), tz=timezone.utc)
    return datetime.now(timezone.utc)


def _clean_summary(value: str, limit: int = 420) -> str:
    clean = re.sub(r"<[^>]+>", " ", value or "")
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean[:limit]


def fetch_feed(url: str, timeout: int = 20) -> Any:
    request = Request(url, headers={"User-Agent": "morning-signal/0.1 (+https://github.com/)"})
    with urlopen(request, timeout=timeout) as response:
        return feedparser.parse(response.read())


def collect_candidates(sources: Dict[str, Any], interests: Dict[str, Any], lookback_hours: int = 72, max_candidates: int = 40) -> List[Dict[str, Any]]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
    priorities = {term.lower(): 3 for term in interests.get("high_priority", [])}
    priorities.update({term.lower(): 2 for term in interests.get("medium_priority", [])})
    priorities.update({term.lower(): 1 for term in interests.get("career_focus", [])})
    results: List[Dict[str, Any]] = []
    for source in sources.get("sources", []):
        feed_url = source.get("feed")
        if not feed_url:
            continue
        try:
            parsed = fetch_feed(feed_url)
        except Exception as exc:
            print("source warning: %s (%s)" % (source.get("name", feed_url), exc))
            continue
        for entry in parsed.entries[:20]:
            published = _published(entry)
            if published < cutoff:
                continue
            title = _clean_summary(entry.get("title", ""), 180)
            link = entry.get("link", "").strip()
            if not title or not link or urlparse(link).scheme not in ("http", "https"):
                continue
            searchable = (title + " " + _clean_summary(entry.get("summary", ""))).lower()
            relevance = sum(weight for term, weight in priorities.items() if term in searchable)
            source_quality = int(source.get("quality", 1))
            results.append({
                "title": title,
                "url": link,
                "source": source.get("name", urlparse(link).netloc),
                "published_at": published.isoformat().replace("+00:00", "Z"),
                "category": source.get("category", "Engineering"),
                "summary": _clean_summary(entry.get("summary", "")),
                "relevance_score": relevance + source_quality,
            })
    results.sort(key=lambda item: (item["relevance_score"], item["published_at"]), reverse=True)
    unique: List[Dict[str, Any]] = []
    seen = set()
    for candidate in results:
        canonical = candidate["url"].split("#", 1)[0].rstrip("/")
        if canonical in seen:
            continue
        seen.add(canonical)
        unique.append(candidate)
        if len(unique) >= max_candidates:
            break
    return unique
