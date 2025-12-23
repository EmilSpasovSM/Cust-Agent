from __future__ import annotations

from agents import Agent, function_tool

from src.client import build_velocity_model
from src.tools_orders import get_order_status
from src.tools_products import search_products


# Wrap plain Python functions as Agents SDK tools
search_products_tool = function_tool(search_products)
get_order_status_tool = function_tool(get_order_status)


SUPPORT_INSTRUCTIONS = """You are a Smart Customer Support Bot.

You can help customers with:
- Product questions (plans, pricing, features): use the product search tool.
- Order questions (status, ETA, tracking): use the order status tool.

Rules:
- If the user asks for BOTH product info and order status, do BOTH and return a single combined answer.
- Be concise. If the order_id is unknown, say you cannot find it and ask for confirmation.
- Never invent pricing or order statuses—use tools.
"""


def build_support_agent() -> Agent:
    return Agent(
        name="Smart Support Agent",
        instructions=SUPPORT_INSTRUCTIONS,
        model=build_velocity_model(),
        tools=[search_products_tool, get_order_status_tool],
    )
