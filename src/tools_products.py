from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def search_products(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """Simple retrieval over `data/products.json` by keyword overlap.

    Note: This function is intentionally tool-schema-friendly (only JSON-serializable
    parameters). Keep it that way for tool calling.
    """

    raw = Path("data/products.json").read_text(encoding="utf-8")
    products = json.loads(raw)
    if not isinstance(products, list):
        raise ValueError("products.json must be a JSON array")

    q = _normalize(query)
    q_tokens = set([t for t in q.replace("#", " ").replace("'", " ").split() if t])

    scored: list[tuple[int, dict[str, Any]]] = []
    for p in products:
        name = _normalize(str(p.get("name", "")))
        pid = _normalize(str(p.get("id", "")))
        keywords = [_normalize(k) for k in (p.get("keywords") or [])]

        hay = set(name.split()) | set(pid.split())
        for kw in keywords:
            hay |= set(kw.split())

        score = len(q_tokens & hay)
        if score > 0 or q in name or q in pid:
            scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)

    results: list[dict[str, Any]] = []
    for _, p in scored[:max_results]:
        results.append(
            {
                "id": p.get("id"),
                "name": p.get("name"),
                "price": p.get("price"),
                "currency": p.get("currency", "USD"),
                "description": p.get("description"),
                "features": p.get("features", []),
            }
        )

    return results
