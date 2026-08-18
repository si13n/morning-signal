from pathlib import Path

from morning_signal.config import load_interests, load_sources


def test_configuration_has_personalization_and_primary_feeds():
    root = Path(__file__).resolve().parents[1]
    interests = load_interests(root)
    sources = load_sources(root)
    assert "QA automation" in interests["high_priority"]
    assert len(sources["sources"]) >= 5
    assert all(source["feed"].startswith("http") for source in sources["sources"])
