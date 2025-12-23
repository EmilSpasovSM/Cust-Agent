from __future__ import annotations

import os
from typing import Any

from src.tools_web_mock import search_web as search_web_mock
from src.tools_web_tavily import TavilyError, search_web_live_tavily


def search_web(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """Web search tool with live Tavily support and mock fallback.

    - If `TAVILY_API_KEY` is set and Tavily succeeds, returns live results.
    - Otherwise returns deterministic mock results.

    This function preserves the existing tool name `search_web()` used by
    [`src/agents_research.py`](../src/agents_research.py:1).
    """

    if os.getenv("TAVILY_API_KEY", "").strip():
        try:
            return search_web_live_tavily(query=query, max_results=max_results)
        except TavilyError:
            # fall back to mock
            pass

    return search_web_mock(query=query, max_results=max_results)
