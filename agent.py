#!/usr/bin/env python3
"""Unattended Helsinki large-buildings agent.

Always live-fetches Ryhti and writes every Helsinki building with
gross floor area >= 3000 m². No prompts, no other datasets.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    extra = [arg for arg in sys.argv[1:] if arg != "--fetch"]
    sys.path.insert(0, str(ROOT))
    sys.argv = ["extract.py", "--fetch", *extra]
    from extract import main as extract_main

    extract_main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
