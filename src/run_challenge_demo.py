from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Avoid Windows console UnicodeEncodeError (common on cp1252 terminals)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

from dotenv import load_dotenv

# Allow running as a file: `python src/run_challenge_demo.py`
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

load_dotenv()

from src.challenge_mac_studio_ultra import Constraints, run_challenge  # noqa: E402


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="run_challenge_demo",
        description="Module 4 challenge: find best discount vs Apple refurbished for Mac Studio Ultra.",
    )
    p.add_argument("--max-results", type=int, default=8)
    p.add_argument("--min-ram", type=int, default=64)
    p.add_argument("--min-ssd", type=int, default=1024)
    p.add_argument("--chip", type=str, default="M2 Ultra")
    return p.parse_args(argv)


async def main(argv: list[str] | None = None) -> None:
    args = _parse_args(sys.argv[1:] if argv is None else argv)

    constraints = Constraints(chip=args.chip, min_ram_gb=args.min_ram, min_ssd_gb=args.min_ssd)
    out = run_challenge(constraints, max_results=args.max_results)

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
