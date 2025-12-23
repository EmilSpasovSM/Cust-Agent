from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# Avoid Windows console UnicodeEncodeError (common on cp1252 terminals)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

from agents import Runner
from agents.tracing import set_tracing_disabled
from dotenv import load_dotenv

# Allow running as a file: `python src/run_research_demo.py`
# (so `import src...` works even when CWD is the repo root)
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# Ensure .env is loaded for web tools too (not only Velocity client)
load_dotenv()

# The Agents SDK may try to export traces using OPENAI_API_KEY.
# This project uses Velocity (`VELOCITY_API_KEY` + `VELOCITY_BASE_URL`) instead.
# Disable tracing to avoid confusing warnings.
set_tracing_disabled(True)

from src.agents_research import build_research_agent  # noqa: E402
from src.client import close_velocity_client  # noqa: E402


DEFAULT_TOPIC = "sustainable packaging trends for e-commerce in 2025"


def _build_prompt(topic: str, *, style: str = "trends") -> str:
    topic = " ".join(topic.strip().split())
    if not topic:
        topic = DEFAULT_TOPIC

    if style == "trends":
        return (
            f"What are the current trends in {topic}? "
            "Please cite your sources."
        )

    # Generic fallback
    return f"Research the following topic: {topic}. Please cite your sources."


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="run_research_demo",
        description=(
            "Run the Deep Research Agent on any topic, using web search + local docs, with citations."
        ),
    )

    parser.add_argument(
        "--topic",
        "-t",
        help="Topic/question to research.",
        default=DEFAULT_TOPIC,
    )

    parser.add_argument(
        "--style",
        choices=["trends", "generic"],
        default="trends",
        help="How to frame the prompt given the topic.",
    )

    return parser.parse_args(argv)


async def main(argv: list[str] | None = None) -> None:
    import os

    args = _parse_args(sys.argv[1:] if argv is None else argv)
    prompt = _build_prompt(args.topic, style=args.style)

    if os.getenv("TAVILY_API_KEY", "").strip():
        print("[research-demo] Web search: live Tavily (TAVILY_API_KEY set)")
    else:
        print("[research-demo] Web search: mock fallback (TAVILY_API_KEY missing)")

    print(f"[research-demo] Topic: {args.topic}")
    print(f"[research-demo] Prompt: {prompt}")

    agent = build_research_agent()
    result = await Runner.run(agent, input=prompt)

    print("=== FINAL ANSWER ===")
    print(result.final_output)

    print("\n=== DEBUG (best-effort) ===")
    for attr in ("steps", "run_steps", "trace"):
        if hasattr(result, attr):
            value = getattr(result, attr)
            print(f"{attr}=\n{value}\n")

    # Avoid ResourceWarning: unclosed transport/socket on Windows
    await close_velocity_client()


if __name__ == "__main__":
    asyncio.run(main())
