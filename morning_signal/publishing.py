from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any

from .rendering import render_site


def publish(root: Path) -> None:
    staging = Path(tempfile.mkdtemp(prefix="morning-signal-", dir=str(root)))
    try:
        render_site(root, root / "data", staging)
        # Promote only after the entire site rendered successfully. index.html is
        # promoted last so a render failure cannot remove the current homepage.
        for relative in (Path("assets/style.css"), Path("archive/index.html")):
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(staging / relative, target)
        for path in sorted((staging / "archive").glob("*.html")):
            target = root / "archive" / path.name
            os.replace(path, target)
        os.replace(staging / "index.html", root / "index.html")
    finally:
        shutil.rmtree(staging, ignore_errors=True)
