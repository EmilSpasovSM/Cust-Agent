from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any


@dataclass(frozen=True)
class WebResult:
    source_id: str
    title: str
    url: str
    published: str
    snippet: str
    keywords: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "title": self.title,
            "url": self.url,
            "published": self.published,
            "snippet": self.snippet,
        }


_WEB_INDEX: list[WebResult] = [
    WebResult(
        source_id="web:packaging_2025_01",
        title="2025 E-commerce Packaging Trends: Right-sizing, Mono-materials, and Reuse",
        url="https://example.com/reports/packaging-trends-2025",
        published="2025-03-11",
        snippet="Retailers are adopting right-sized packaging, mono-material solutions, and reusable shipping programs to reduce waste and cost.",
        keywords=("2025", "e-commerce", "packaging", "right-sizing", "mono-material", "reuse"),
    ),
    WebResult(
        source_id="web:policy_02",
        title="Policy Watch: Extended Producer Responsibility (EPR) Updates Affecting Online Retail",
        url="https://example.com/policy/epr-updates-online-retail",
        published="2025-02-02",
        snippet="EPR programs expand reporting requirements and fees, incentivizing recyclability and recycled content in packaging.",
        keywords=("policy", "epr", "fees", "recycled", "reporting"),
    ),
    WebResult(
        source_id="web:material_03",
        title="Barrier Coatings for Paper Packaging: Progress and Remaining Tradeoffs",
        url="https://example.com/materials/barrier-coatings-paper",
        published="2024-11-18",
        snippet="New water-based barrier coatings improve grease/moisture resistance but can complicate recycling if over-applied.",
        keywords=("barrier", "coatings", "paper", "recycling", "water-based"),
    ),
    WebResult(
        source_id="web:logistics_04",
        title="Damage Reduction in Parcel Shipping: Testing, Cushioning, and Frustration-Free Unboxing",
        url="https://example.com/logistics/damage-reduction-parcel",
        published="2025-01-20",
        snippet="Companies reduce returns by optimizing cushioning, lab testing, and simplifying unboxing while maintaining protection.",
        keywords=("damage", "returns", "cushioning", "testing", "unboxing"),
    ),
    WebResult(
        source_id="web:reuse_05",
        title="Reusable Mailers at Scale: Deposit Models and Reverse Logistics",
        url="https://example.com/circular/reusable-mailers-deposit",
        published="2025-04-05",
        snippet="Reusable mailers expand through deposit incentives and improved return logistics; cost depends on return rate.",
        keywords=("reusable", "mailers", "deposit", "reverse", "logistics", "return"),
    ),
    WebResult(
        source_id="web:lca_06",
        title="How to Compare Packaging Options: Practical LCA for E-commerce",
        url="https://example.com/sustainability/lca-practical-ecommerce",
        published="2024-12-12",
        snippet="Lifecycle assessment shows results depend on reuse cycles, recycled content, and local recycling/composting realities.",
        keywords=("lca", "life-cycle", "assessment", "recycled", "composting", "reuse"),
    ),
    WebResult(
        source_id="web:labels_07",
        title="Packaging Labels and Consumer Guidance: What Actually Improves Sorting",
        url="https://example.com/recycling/labels-consumer-guidance",
        published="2025-03-30",
        snippet="Clear disposal labels and consistent messaging improve sorting rates more than vague sustainability claims.",
        keywords=("labels", "sorting", "recycling", "consumer", "guidance"),
    ),
    WebResult(
        source_id="web:automation_08",
        title="Fulfillment Automation Meets Sustainability: On-demand Box Making",
        url="https://example.com/fulfillment/on-demand-box-making",
        published="2025-05-14",
        snippet="On-demand box making reduces void fill and DIM weight; requires capex and careful material selection.",
        keywords=("automation", "fulfillment", "box", "making", "dim", "void"),
    ),
]


def _normalize(text: str) -> list[str]:
    return [t for t in " ".join(text.lower().strip().split()).replace("-", " ").split() if t]


def search_web(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """Mock web search.

    Deterministic keyword-overlap scoring over an in-memory index.
    """

    q_tokens = set(_normalize(query))
    scored: list[tuple[int, WebResult]] = []

    for r in _WEB_INDEX:
        hay = set([t.lower() for t in r.keywords]) | set(_normalize(r.title)) | set(_normalize(r.snippet))
        score = len(q_tokens & hay)
        if score > 0:
            scored.append((score, r))

    scored.sort(key=lambda x: x[0], reverse=True)

    # If no hits, return a couple of general items to keep training flow moving.
    if not scored:
        fallback = sorted(_WEB_INDEX, key=lambda x: x.published, reverse=True)[: max_results]
        return [r.to_dict() for r in fallback]

    return [r.to_dict() for _, r in scored[:max_results]]
