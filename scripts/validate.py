#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from morning_signal.config import runtime_config
from morning_signal.schema import validate_digest


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Validate Morning Signal JSON files")
    parser.add_argument("paths", nargs="*", type=Path, help="Digest JSON files")
    args = parser.parse_args()
    paths = args.paths or sorted((root / "data").glob("*.json"))
    if not paths:
        parser.error("no digest JSON files found")
    for path in paths:
        digest = json.loads(path.read_text(encoding="utf-8"))
        config = runtime_config(root)
        validate_digest(digest, max_items=config["max_digest_items"], min_items=config["min_digest_items"])
        print("valid: %s" % path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
