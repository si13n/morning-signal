#!/usr/bin/env python3
from __future__ import annotations

from datetime import date
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from morning_signal.collect import collect_candidates
from morning_signal.config import load_interests, load_sources, runtime_config
from morning_signal.research import create_digest
from morning_signal.schema import validate_digest


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Generate one live Morning Signal edition")
    parser.add_argument("--date", default=date.today().isoformat())
    args = parser.parse_args()
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is required for live generation; use the checked-in fixture for offline rendering")
    config = runtime_config(root)
    interests = load_interests(root)
    candidates = collect_candidates(load_sources(root), interests, config["lookback_hours"], config["max_candidates"])
    digest = create_digest(candidates, interests, args.date, config["model"], config["max_digest_items"], config["max_web_searches"])
    validate_digest(digest, max_items=config["max_digest_items"], expected_date=args.date)
    output = root / "data" / (args.date + ".json")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=str(output.parent), delete=False) as handle:
        json.dump(digest, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
        temporary = Path(handle.name)
    temporary.replace(output)
    print("generated %s" % output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
