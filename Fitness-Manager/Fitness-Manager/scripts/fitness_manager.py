#!/usr/bin/env python3
"""Stable CLI entry point; implementation lives in the fitness_manager package."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fitness_manager.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
