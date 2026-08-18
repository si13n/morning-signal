from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urldefrag, urlparse
from typing import List


HREF_RE = re.compile(r"(?:href|src)=\"([^\"]+)\"")


def internal_link_errors(root: Path) -> List[str]:
    errors: List[str] = []
    for html in sorted(root.rglob("*.html")):
        for raw in HREF_RE.findall(html.read_text(encoding="utf-8")):
            link, _fragment = urldefrag(raw)
            parsed = urlparse(link)
            if not link or link.startswith("#") or parsed.scheme in ("http", "https", "mailto", "data"):
                continue
            target = (html.parent / link).resolve()
            try:
                target.relative_to(root.resolve())
            except ValueError:
                errors.append("%s points outside site: %s" % (html, raw))
                continue
            if not target.exists():
                errors.append("%s points to missing %s" % (html, raw))
    return errors
