#!/usr/bin/env python3
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from morning_signal.collect import collect_candidates
from morning_signal.config import load_interests, load_sources, runtime_config


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    config = runtime_config(root)
    candidates = collect_candidates(load_sources(root), load_interests(root), config["lookback_hours"], config["max_candidates"])
    for item in candidates:
        print("%s | %s | %s" % (item["published_at"], item["source"], item["title"]))
