from __future__ import annotations

import os
import sys
from pathlib import Path

# Allow running as a file: `python src/run_web_search_smoke.py`
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.tools_web import search_web  # noqa: E402


def main() -> None:
    query = "sustainable packaging e-commerce 2025"
    results = search_web(query, max_results=3)

    mode = "live" if os.getenv("TAVILY_API_KEY", "").strip() else "mock"
    print(f"[smoke] mode={mode} results={len(results)}")

    if not results:
        raise SystemExit(2)

    for r in results:
        print(f"- {r.get('source_id')} | {r.get('title')} | {r.get('url')}")


if __name__ == "__main__":
    main()
