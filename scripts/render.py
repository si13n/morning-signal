#!/usr/bin/env python3
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from morning_signal.publishing import publish


if __name__ == "__main__":
    publish(Path(__file__).resolve().parents[1])
    print("rendered and published static site")
