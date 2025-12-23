from __future__ import annotations

from agents import Agent, function_tool

from src.client import build_velocity_model
from src.io_docs import retrieve_local_docs
from src.tools_summarize import summarize_text
from src.tools_web import search_web


search_web_tool = function_tool(search_web)
retrieve_local_docs_tool = function_tool(retrieve_local_docs)
summarize_text_tool = function_tool(summarize_text)


RESEARCH_INSTRUCTIONS = """You are a Deep Research Agent.

Goal: research the user's question using BOTH:
1) Web search results (broad, up-to-date overview)
2) Local documents from the training corpus (deeper reference)

You have tools to:
- search_web(query)
- retrieve_local_docs(query)
- summarize_text(text, max_words)

Process:
- Start by calling search_web() to gather 3–5 relevant sources.
  - If `TAVILY_API_KEY` is configured, this will use live Tavily search.
  - Otherwise, it will fall back to deterministic mocked web results.
- Then call retrieve_local_docs() to gather 3–5 relevant local excerpts.
- Use summarize_text() as needed to condense long excerpts.

Output requirements:
- Provide 4–6 bullet points of key trends and a short conclusion.
- Every bullet must include at least one citation in the form [source_id].
- Cite both web:* and local:* sources across the answer.
- Be explicit when web results appear to be mocked fallback vs live.
"""


def build_research_agent() -> Agent:
    return Agent(
        name="Deep Research Agent",
        instructions=RESEARCH_INSTRUCTIONS,
        model=build_velocity_model(),
        tools=[search_web_tool, retrieve_local_docs_tool, summarize_text_tool],
    )
