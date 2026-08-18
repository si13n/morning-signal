import json
from pathlib import Path

from morning_signal.rendering import render_site
from morning_signal.sitecheck import internal_link_errors


ROOT = Path(__file__).resolve().parents[1]


def test_rendered_site_contains_expected_content(tmp_path):
    digests = render_site(ROOT, ROOT / "data", tmp_path)
    assert len(digests) == 1
    index = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "QA / Agentic AI Morning" in index
    assert "Top Signal" in index
    assert "https://github.com/" in index
    assert (tmp_path / "archive" / "2026-08-18.html").exists()
    assert (tmp_path / "archive" / "index.html").exists()
    assert internal_link_errors(tmp_path) == []


def test_archive_is_newest_first(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    base = json.loads((ROOT / "data" / "2026-08-18.json").read_text(encoding="utf-8"))
    for issue_date in ("2026-08-17", "2026-08-18", "2026-08-19"):
        digest = json.loads(json.dumps(base))
        digest["date"] = issue_date
        (data_dir / (issue_date + ".json")).write_text(json.dumps(digest), encoding="utf-8")
    output = tmp_path / "site"
    render_site(ROOT, data_dir, output)
    html = (output / "archive" / "index.html").read_text(encoding="utf-8")
    assert html.index("2026-08-19") < html.index("2026-08-18") < html.index("2026-08-17")
    assert internal_link_errors(output) == []
