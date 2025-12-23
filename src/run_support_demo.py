from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from agents import Runner

# Allow running as a file: `python src/run_support_demo.py`
# (so `import src...` works even when CWD is the repo root)
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.agents_support import build_support_agent  # noqa: E402
from src.client import close_velocity_client  # noqa: E402


PROMPT = "What's the price of the 'Pro' model, and what's the status of order #12345?"


async def main() -> None:
    agent = build_support_agent()
    result = await Runner.run(agent, input=PROMPT)

    print("=== FINAL ANSWER ===")
    print(result.final_output)

    # Trace/debug: best-effort introspection (varies by Agents SDK version)
    print("\n=== DEBUG (best-effort) ===")
    for attr in ("steps", "run_steps", "trace"):
        if hasattr(result, attr):
            value = getattr(result, attr)
            print(f"{attr}=\n{value}\n")

    # Avoid ResourceWarning: unclosed transport/socket on Windows
    await close_velocity_client()


if __name__ == "__main__":
    asyncio.run(main())
