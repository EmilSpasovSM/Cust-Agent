from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable

from src.tools_web import search_web


@dataclass(frozen=True)
class Constraints:
    chip: str = "M2 Ultra"
    min_ram_gb: int = 64
    min_ssd_gb: int = 1024
    currency: str = "USD"


@dataclass(frozen=True)
class Offer:
    source_id: str
    title: str
    url: str
    snippet: str
    price_usd: float | None
    condition: str | None
    chip: str | None
    ram_gb: int | None
    ssd_gb: int | None


@dataclass(frozen=True)
class Baseline:
    source_id: str
    title: str
    url: str
    snippet: str
    price_usd: float | None
    chip: str | None
    ram_gb: int | None
    ssd_gb: int | None


@dataclass(frozen=True)
class ScoredResult:
    offer: Offer
    baseline: Baseline
    discount_pct: float | None


_PRICE_RE = re.compile(
    r"\$\s*(?P<amount>\d{1,3}(?:,\d{3})*(?:\.\d{2})?)"
)
_PRICE_ANY_RE = re.compile(
    r"\$\s*(?P<amount>\d{1,3}(?:,\d{3})*(?:\.\d{2})?)|\$\s*(?P<amount2>\d{1,3}(?:,\d{3})*)"
)
_RAM_RE = re.compile(r"(?P<ram>\d{2,4})\s*GB\s*(?:unified\s*)?memory", re.IGNORECASE)
_RAM_RE2 = re.compile(r"(?P<ram>\d{2,4})\s*GB\s*RAM", re.IGNORECASE)
_SSD_TB_RE = re.compile(r"(?P<ssd>\d+(?:\.\d+)?)\s*TB\s*SSD", re.IGNORECASE)
_SSD_GB_RE = re.compile(r"(?P<ssd>\d{3,5})\s*GB\s*SSD", re.IGNORECASE)


def _normalize(text: str) -> str:
    return " ".join((text or "").strip().split())


def _extract_price_usd(text: str) -> float | None:
    """Extract a plausible USD price.

    Handles both "$2,299.00" and "$2299".

    Heuristics:
    - Ignore very small values like $21 that are usually abbreviations for $21xx.
    - Prefer amounts in a reasonable Mac Studio range when multiple matches exist.
    """

    text = text or ""
    matches: list[str] = []
    for m in _PRICE_ANY_RE.finditer(text):
        v = m.group("amount") or m.group("amount2")
        if v:
            matches.append(v)

    if not matches:
        return None

    parsed: list[float] = []
    for amt in matches:
        try:
            parsed.append(float(amt.replace(",", "")))
        except ValueError:
            continue

    parsed = [p for p in parsed if p >= 500.0]
    if not parsed:
        return None

    typical = [p for p in parsed if 1500.0 <= p <= 6000.0]
    if typical:
        return min(typical)

    return min(parsed)


def _extract_ram_gb(text: str) -> int | None:
    text = text or ""
    m = _RAM_RE.search(text) or _RAM_RE2.search(text)
    if not m:
        return None
    try:
        return int(m.group("ram"))
    except ValueError:
        return None


def _extract_ssd_gb(text: str) -> int | None:
    text = text or ""
    m_tb = _SSD_TB_RE.search(text)
    if m_tb:
        try:
            tb = float(m_tb.group("ssd"))
            return int(tb * 1024)
        except ValueError:
            return None

    m_gb = _SSD_GB_RE.search(text)
    if m_gb:
        try:
            return int(m_gb.group("ssd"))
        except ValueError:
            return None

    return None


def _extract_chip(text: str) -> str | None:
    text = (text or "").lower()
    if "m2 ultra" in text:
        return "M2 Ultra"
    if "m1 ultra" in text:
        return "M1 Ultra"
    if "m3 ultra" in text:
        return "M3 Ultra"
    if "m2 max" in text:
        return "M2 Max"
    if "ultra" in text:
        return "Ultra"
    return None


def _extract_condition(text: str) -> str | None:
    t = (text or "").lower()
    if "refurb" in t or "refurbished" in t:
        return "refurbished"
    if "used" in t or "pre-owned" in t or "preowned" in t:
        return "used"
    if "open box" in t or "open-box" in t:
        return "open-box"
    if "new" in t:
        return "new"
    return None


def _meets_constraints(offer: Offer, c: Constraints) -> bool:
    if offer.chip is None or offer.chip != c.chip:
        return False
    if offer.ram_gb is None or offer.ram_gb < c.min_ram_gb:
        return False
    if offer.ssd_gb is None or offer.ssd_gb < c.min_ssd_gb:
        return False
    if offer.price_usd is None:
        return False
    return True


def _as_offer(r: dict[str, Any]) -> Offer:
    title = _normalize(r.get("title") or "")
    snippet = _normalize(r.get("snippet") or "")
    combined = f"{title} {snippet}"

    return Offer(
        source_id=str(r.get("source_id") or "web:unknown"),
        title=title,
        url=_normalize(r.get("url") or ""),
        snippet=snippet,
        price_usd=_extract_price_usd(combined),
        condition=_extract_condition(combined),
        chip=_extract_chip(combined),
        ram_gb=_extract_ram_gb(combined),
        ssd_gb=_extract_ssd_gb(combined),
    )


def _as_baseline(r: dict[str, Any]) -> Baseline:
    title = _normalize(r.get("title") or "")
    snippet = _normalize(r.get("snippet") or "")
    url = _normalize(r.get("url") or "")
    combined = f"{title} {snippet} {url}"

    price = _extract_price_usd(combined)
    if price is None and "apple.com" in url.lower():
        price = _extract_price_from_apple_url(url)

    return Baseline(
        source_id=str(r.get("source_id") or "web:apple_refurb"),
        title=title,
        url=url,
        snippet=snippet,
        price_usd=price,
        # Apple URLs/snippets may mention multiple chips; don't infer chip from that.
        chip=None,
        ram_gb=_extract_ram_gb(combined),
        ssd_gb=_extract_ssd_gb(combined),
    )


def _discount_pct(offer_price: float | None, baseline_price: float | None) -> float | None:
    if not offer_price or not baseline_price:
        return None
    if baseline_price <= 0:
        return None
    return (baseline_price - offer_price) / baseline_price * 100.0


def _extract_price_from_apple_url(url: str) -> float | None:
    """Best-effort: Apple product pages often omit price in search snippets.

    We try to infer price from common Apple "?price=$####" patterns if present.
    (If not present, returns None.)
    """

    if not url:
        return None

    # Examples we might see in some contexts: ...?price=$3,399.00
    m = re.search(r"price=\$?(?P<amount>\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", url)
    if not m:
        return None

    try:
        return float(m.group("amount").replace(",", ""))
    except ValueError:
        return None


def _best_baseline_for_offer(offer: Offer, baselines: Iterable[Baseline], c: Constraints) -> Baseline | None:
    """Pick the best *Apple refurbished* baseline.

    Priority:
    1) Apple refurb source (apple.com URLs, or snippet/title mentions refurbished)
    2) Closest spec match (RAM/SSD) to the offer
    3) Has a parseable price
    """

    def is_apple_refurb(b: Baseline) -> bool:
        u = (b.url or "").lower()
        t = (b.title or "").lower()
        s = (b.snippet or "").lower()
        if "apple.com" in u and ("refurb" in t or "refurb" in s or "refurb" in u):
            return True
        if "apple.com" in u and "refurb" in u:
            return True
        if "refurb" in t or "refurb" in s:
            return True
        return False

    candidates: list[Baseline] = []
    for b in baselines:
        candidates.append(b)

    if not candidates:
        return None

    def score(b: Baseline) -> tuple[int, int, int, float]:
        refurb_pen = 0 if is_apple_refurb(b) else 1

        ram_pen = 0
        ssd_pen = 0

        if offer.ram_gb is not None and b.ram_gb is not None:
            ram_pen = abs(b.ram_gb - offer.ram_gb)
        elif offer.ram_gb is not None and b.ram_gb is None:
            ram_pen = 10_000

        if offer.ssd_gb is not None and b.ssd_gb is not None:
            ssd_pen = abs(b.ssd_gb - offer.ssd_gb)
        elif offer.ssd_gb is not None and b.ssd_gb is None:
            ssd_pen = 10_000

        price_pen = 0.0 if (b.price_usd is not None) else 10_000.0
        return (refurb_pen, ram_pen + ssd_pen, ram_pen, price_pen)

    candidates.sort(key=score)
    return candidates[0]


def run_challenge(constraints: Constraints | None = None, *, max_results: int = 8) -> dict[str, Any]:
    """Search web for offers and Apple refurbished baselines and compute best discount.

    Returns a JSON-serializable dict for easy printing / tool usage.
    """

    c = constraints or Constraints()

    ssd_tb = int(c.min_ssd_gb / 1024)

    # 1) Offers: broad query (US, allow used/open-box/new)
    offers_query = f"Mac Studio {c.chip} {c.min_ram_gb}GB {ssd_tb}TB price open box used new USD"
    offer_results = search_web(offers_query, max_results=max_results)
    offers = [_as_offer(r) for r in offer_results]
    offers = [o for o in offers if _meets_constraints(o, c)]

    # 2) Baseline: Apple refurbished (try multiple queries; Tavily may return different product pages)
    baseline_queries = [
        f"Apple refurbished Mac Studio M2 Ultra price site:apple.com",
        f"site:apple.com refurbished Mac Studio M2 Ultra",
        f"Apple refurbished Mac Studio M2 Ultra 64GB 1TB price site:apple.com",
        f"Apple refurbished Mac Studio M2 Ultra 64GB 1TB",
    ]

    baselines: list[Baseline] = []
    baseline_query = baseline_queries[0]
    for q in baseline_queries:
        baseline_query = q
        baseline_results = search_web(baseline_query, max_results=max_results)
        baselines = [_as_baseline(r) for r in baseline_results]
        # Accept this batch if it contains at least one Apple refurb URL AND at least one price.
        if any("apple.com" in (b.url or "") and "refurb" in (b.url or "").lower() for b in baselines) and any(
            b.price_usd is not None for b in baselines
        ):
            break

    # If still no priced baseline, keep the last batch anyway.

    # 3) Score
    scored: list[ScoredResult] = []
    for o in offers:
        b = _best_baseline_for_offer(o, baselines, c)
        if not b:
            continue
        scored.append(ScoredResult(offer=o, baseline=b, discount_pct=_discount_pct(o.price_usd, b.price_usd)))

    scored.sort(key=lambda s: (s.discount_pct is None, -(s.discount_pct or -1e9)))

    def to_dict(s: ScoredResult) -> dict[str, Any]:
        return {
            "discount_pct": s.discount_pct,
            "offer": {
                "source_id": s.offer.source_id,
                "title": s.offer.title,
                "url": s.offer.url,
                "snippet": s.offer.snippet,
                "price_usd": s.offer.price_usd,
                "condition": s.offer.condition,
                "chip": s.offer.chip,
                "ram_gb": s.offer.ram_gb,
                "ssd_gb": s.offer.ssd_gb,
            },
            "baseline": {
                "source_id": s.baseline.source_id,
                "title": s.baseline.title,
                "url": s.baseline.url,
                "snippet": s.baseline.snippet,
                "price_usd": s.baseline.price_usd,
                "chip": s.baseline.chip,
                "ram_gb": s.baseline.ram_gb,
                "ssd_gb": s.baseline.ssd_gb,
            },
        }

    return {
        "constraints": {
            "chip": c.chip,
            "min_ram_gb": c.min_ram_gb,
            "min_ssd_gb": c.min_ssd_gb,
            "currency": c.currency,
        },
        "offers_query": offers_query,
        "baseline_query": baseline_query,
        "offer_sources": [o.source_id for o in offers],
        "baseline_sources": [b.source_id for b in baselines],
        "ranked": [to_dict(s) for s in scored],
        "winner": to_dict(scored[0]) if scored else None,
    }
