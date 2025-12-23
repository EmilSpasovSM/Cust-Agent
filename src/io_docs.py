from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LocalDoc:
    source_id: str
    title: str
    published: str
    path: Path
    text: str

    def excerpt(self, max_chars: int = 400) -> str:
        t = " ".join(self.text.strip().split())
        return (t[: max_chars - 3] + "...") if len(t) > max_chars else t

    def to_retrieval_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "title": self.title,
            "published": self.published,
            "path": str(self.path).replace("\\", "/"),
            "excerpt": self.excerpt(),
        }


def _parse_header(lines: list[str]) -> dict[str, str]:
    meta: dict[str, str] = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        meta[k.strip().lower()] = v.strip()
    return meta


def load_local_docs(folder: str = "research_docs") -> list[LocalDoc]:
    base = Path(folder)
    docs: list[LocalDoc] = []

    for path in sorted(base.glob("*.txt")):
        raw = path.read_text(encoding="utf-8")
        parts = raw.split("\n\n", 1)
        header = parts[0].splitlines() if parts else []
        body = parts[1] if len(parts) > 1 else raw

        meta = _parse_header(header)
        source_id = meta.get("doc_id") or f"local:{path.stem}"
        title = meta.get("title") or path.stem
        published = meta.get("date") or "unknown"

        docs.append(
            LocalDoc(
                source_id=source_id if source_id.startswith("local:") else f"local:{source_id}",
                title=title,
                published=published,
                path=path,
                text=body.strip(),
            )
        )

    return docs


def _normalize(text: str) -> list[str]:
    return [t for t in " ".join(text.lower().strip().split()).replace("-", " ").split() if t]


def retrieve_local_docs(query: str, max_docs: int = 5, folder: str = "research_docs") -> list[dict[str, Any]]:
    """Mock local retrieval by keyword overlap over `research_docs/*.txt`."""

    docs = load_local_docs(folder)
    q_tokens = set(_normalize(query))

    scored: list[tuple[int, LocalDoc]] = []
    for d in docs:
        hay = set(_normalize(d.title)) | set(_normalize(d.text))
        score = len(q_tokens & hay)
        if score > 0:
            scored.append((score, d))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [d.to_retrieval_dict() for _, d in scored[:max_docs]]
