from __future__ import annotations

import re


def summarize_text(text: str, max_words: int = 120) -> str:
    """Deterministic, heuristic summarizer.

    Training-friendly: avoids extra LLM calls. Produces a short extractive summary.
    """

    cleaned = re.sub(r"\s+", " ", text.strip())
    if not cleaned:
        return ""

    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    kept: list[str] = []
    word_count = 0

    for s in sentences:
        s = s.strip()
        if not s:
            continue
        words = s.split()
        if word_count + len(words) > max_words:
            break
        kept.append(s)
        word_count += len(words)

    # If the first sentence is extremely short, add the next one if possible.
    if kept and len(kept) == 1 and len(kept[0].split()) < min(14, max_words):
        for s in sentences[1:]:
            words = s.split()
            if word_count + len(words) <= max_words:
                kept.append(s.strip())
                break

    return " ".join(kept)
