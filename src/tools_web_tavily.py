from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True)
class TavilyResult:
    source_id: str
    title: str
    url: str
    published: str
    snippet: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "title": self.title,
            "url": self.url,
            "published": self.published,
            "snippet": self.snippet,
        }


class TavilyError(RuntimeError):
    pass


def search_web_live_tavily(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """Live web search via Tavily.

    Returns URLs + titles + snippets only (fast/cheap).

    Env:
      - TAVILY_API_KEY: required for live search

    Raises:
      - TavilyError: on missing key or request/response issues

    Output matches the mock tool shape so it can be used interchangeably.
    """

    api_key = os.getenv("TAVILY_API_KEY", "").strip()
    if not api_key:
        raise TavilyError("TAVILY_API_KEY is not set")

    # Tavily REST API: https://docs.tavily.com/
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "max_results": int(max_results),
        "include_answer": False,
        "include_raw_content": False,
        "include_images": False,
    }

    try:
        with httpx.Client(timeout=20.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:  # noqa: BLE001
        raise TavilyError(f"Tavily request failed: {e}") from e

    results = data.get("results") or []
    out: list[TavilyResult] = []

    for i, r in enumerate(results[: int(max_results)]):
        title = (r.get("title") or "").strip()
        link = (r.get("url") or "").strip()
        snippet = (r.get("content") or r.get("snippet") or "").strip()
        published = (r.get("published_date") or "").strip()

        if not link:
            continue

        source_id = f"web:tavily:{i+1}"
        out.append(
            TavilyResult(
                source_id=source_id,
                title=title or link,
                url=link,
                published=published,
                snippet=snippet,
            )
        )

    return [r.to_dict() for r in out]
