# Module 3 Labs Plan: Smart Support Agent + Deep Research Agent

This repo implements two simple, training-friendly agents using the OpenAI Agents SDK (the `agents` package referenced in [`app.py`](app.py:1)).

Key constraints:
- LLM calls are allowed via your existing OpenAI-compatible endpoint (Velocity), configured via `.env`.
- All business tools are mocked (no real web APIs). The deep research agent uses both local files and a mocked web search tool.

## 0) Setup

Install deps:

```bash
python -m pip install -r requirements.txt
```

Ensure `.env` contains:
- `VELOCITY_API_KEY`
- `VELOCITY_BASE_URL`

## 1) Implemented project structure

- [`app.py`](app.py:1): original minimal agent example
- [`requirements.txt`](requirements.txt:1): runtime deps
- [`data/products.json`](data/products.json:1): product catalog
- [`data/orders.json`](data/orders.json:1): orders store
- `research_docs/*.txt`: local research corpus with headers + excerpts

Source code:
- [`src/client.py`](src/client.py:1): builds `OpenAIChatCompletionsModel` using Velocity endpoint
- [`src/tools_products.py`](src/tools_products.py:1): `search_products(query, max_results)`
- [`src/tools_orders.py`](src/tools_orders.py:1): `get_order_status(order_id)`
- [`src/tools_web_mock.py`](src/tools_web_mock.py:1): `search_web(query, max_results)` (mocked)
- [`src/io_docs.py`](src/io_docs.py:1): `retrieve_local_docs(query, max_docs)` (mocked local retrieval)
- [`src/tools_summarize.py`](src/tools_summarize.py:1): `summarize_text(text, max_words)` (heuristic summarizer)
- [`src/agents_support.py`](src/agents_support.py:1): Support agent
- [`src/agents_research.py`](src/agents_research.py:1): Research agent
- [`src/run_support_demo.py`](src/run_support_demo.py:1): runnable lab demo 1
- [`src/run_research_demo.py`](src/run_research_demo.py:1): runnable lab demo 2

## 2) Tool interfaces (training-friendly)

Important: tool-callable functions must use JSON-serializable parameters only. That’s why the tool functions avoid `Path`/dataclasses in signatures.

### 2.1 Support tools
- `search_products(query: str, max_results: int = 5) -> list[dict]` in [`src/tools_products.py`](src/tools_products.py:1)
- `get_order_status(order_id: str) -> dict` in [`src/tools_orders.py`](src/tools_orders.py:1)

### 2.2 Research tools
- `search_web(query: str, max_results: int = 5) -> list[dict]` in [`src/tools_web_mock.py`](src/tools_web_mock.py:1)
- `retrieve_local_docs(query: str, max_docs: int = 5) -> list[dict]` in [`src/io_docs.py`](src/io_docs.py:1)
- `summarize_text(text: str, max_words: int = 120) -> str` in [`src/tools_summarize.py`](src/tools_summarize.py:1)

### 2.3 Citation format
The research agent is instructed to cite sources inline as:
- `[source_id]` (e.g. `[web:reuse_05]`, `[local:doc_pack_03]`)

## 3) Running the labs

### 3.1 Smart Customer Support Bot

```bash
python -m src.run_support_demo
```

Prompt used (see [`src/run_support_demo.py`](src/run_support_demo.py:1)):
- `What's the price of the 'Pro' model, and what's the status of order #12345?`

### 3.2 Deep Research Agent

```bash
python -m src.run_research_demo
```

Run with a custom topic:

```bash
python src/run_research_demo.py --topic "battery recycling supply chain 2025"
```

Use a different prompt framing:

```bash
python src/run_research_demo.py --topic "EU AI Act compliance" --style generic
```

Notes (see [`src/run_research_demo.py`](src/run_research_demo.py:1)):
- Uses live Tavily web search when `TAVILY_API_KEY` is set; otherwise uses deterministic mock web results.
- Always pulls supporting excerpts from local docs.
- Final answer includes citations like `[web:...]` and `[local:...]`.

## 4) Debugging / observing tool use

The `agents` SDK exposes traces differently depending on version and configuration. The demo scripts attempt best-effort introspection of attributes like `steps`/`trace` on the run result.

If your Velocity/OpenAI-compatible gateway supports tool-call traces, you can also log requests at the gateway layer.

---

## Notes for instructors

- The "web search" is *not* real. It is deterministic keyword overlap over an in-memory index in [`src/tools_web_mock.py`](src/tools_web_mock.py:1).
- Local retrieval is *not* embeddings-based. It is deterministic keyword overlap over `research_docs/*.txt` in [`src/io_docs.py`](src/io_docs.py:1).
- Summarization is *not* an extra LLM call. It is a small heuristic function in [`src/tools_summarize.py`](src/tools_summarize.py:1).
