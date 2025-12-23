from __future__ import annotations

import os

from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel


# Keep a single client instance per process so it can be cleanly closed.
# This also avoids repeated connector/session creation in multi-run scenarios.
_VELOCITY_CLIENT: AsyncOpenAI | None = None


def _get_velocity_client() -> AsyncOpenAI:
    load_dotenv()

    global _VELOCITY_CLIENT
    if _VELOCITY_CLIENT is None:
        _VELOCITY_CLIENT = AsyncOpenAI(
            api_key=os.environ["VELOCITY_API_KEY"],
            base_url=os.environ["VELOCITY_BASE_URL"],
        )
    return _VELOCITY_CLIENT


async def close_velocity_client() -> None:
    """Close the underlying HTTP client to avoid ResourceWarning on Windows."""

    global _VELOCITY_CLIENT
    if _VELOCITY_CLIENT is None:
        return

    client = _VELOCITY_CLIENT
    _VELOCITY_CLIENT = None

    # openai.AsyncOpenAI has evolved across versions.
    # In current versions, `.close()` is async (returns coroutine) and `.aclose()` may not exist.
    for method_name in ("aclose", "close"):
        meth = getattr(client, method_name, None)
        if not callable(meth):
            continue
        res = meth()
        # If it returned a coroutine/awaitable, await it; else it was sync.
        if hasattr(res, "__await__"):
            await res
        return


def build_velocity_model(model: str = "openai.openai/gpt-5.2") -> OpenAIChatCompletionsModel:
    """Build an Agents SDK model using a Velocity-backed OpenAI-compatible endpoint."""

    velocity_client = _get_velocity_client()

    return OpenAIChatCompletionsModel(
        model=model,
        openai_client=velocity_client,
    )
