import json
from pathlib import Path

import pytest

from morning_signal.publishing import publish


ROOT = Path(__file__).resolve().parents[1]


def test_invalid_digest_does_not_overwrite_existing_site(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "assets").mkdir()
    (tmp_path / "templates").mkdir()
    for relative in ("assets/style.css", "templates/digest.html.j2", "templates/archive.html.j2"):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text((ROOT / relative).read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "index.html").write_text("previous valid homepage", encoding="utf-8")
    invalid = json.loads((ROOT / "data" / "2026-08-18.json").read_text(encoding="utf-8"))
    invalid["top_signal"]["source_url"] = "bad"
    (tmp_path / "data" / "2026-08-18.json").write_text(json.dumps(invalid), encoding="utf-8")
    with pytest.raises(Exception):
        publish(tmp_path)
    assert (tmp_path / "index.html").read_text(encoding="utf-8") == "previous valid homepage"
