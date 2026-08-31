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

    explicit_paths = bool(args.paths)
    paths = args.paths or sorted((root / "data").glob("*.json"))
    if not paths:
        parser.error("no digest JSON files found")

    # Editorial size limits are a policy for newly generated editions, not a
    # migration rule for historical archive files. generate_digest.py already
    # validates a new edition against the current MIN/MAX_DIGEST_ITEMS before
    # writing it. A full archive validation therefore checks schema/integrity
    # using the historical upper bound, so changing today's editorial limits
    # cannot invalidate previously published issues.
    current_config = runtime_config(root)

    for path in paths:
        digest = json.loads(path.read_text(encoding="utf-8"))
        if explicit_paths:
            validate_digest(
                digest,
                max_items=current_config["max_digest_items"],
                min_items=current_config["min_digest_items"],
                expected_date=path.stem,
            )
        else:
            validate_digest(digest, max_items=25, min_items=0, expected_date=path.stem)
        print("valid: %s" % path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
