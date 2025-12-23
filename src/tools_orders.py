from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def get_order_status(order_id: str) -> dict[str, Any]:
    """Return mock order status data from `data/orders.json`.

    Note: Tool-schema-friendly (only JSON-serializable parameters).
    """

    raw = Path("data/orders.json").read_text(encoding="utf-8")
    orders = json.loads(raw)
    if not isinstance(orders, dict):
        raise ValueError("orders.json must be a JSON object keyed by order_id")

    order = orders.get(str(order_id))
    if not order:
        return {"order_id": str(order_id), "status": "UNKNOWN"}

    result = {"order_id": str(order_id)}
    if isinstance(order, dict):
        result.update(order)
    else:
        result["status"] = str(order)

    return result
