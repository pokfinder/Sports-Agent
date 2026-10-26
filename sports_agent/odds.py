"""Normalize prices and compare quoted sportsbook markets."""
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class Quote:
    event_id: str
    market: str
    selection: str
    sportsbook: str
    american_odds: int
    observed_at: str
    source: str

def implied_probability(odds: int) -> float:
    if odds == 0:
        raise ValueError("American odds cannot be zero")
    return 100 / (odds + 100) if odds > 0 else -odds / (-odds + 100)

def decimal_odds(odds: int) -> float:
    return 1 + (odds / 100 if odds > 0 else 100 / -odds)

def expected_value_per_dollar(odds: int, probability: float) -> float:
    if not 0 <= probability <= 1:
        raise ValueError("Probability must be between 0 and 1")
    return probability * (decimal_odds(odds) - 1) - (1 - probability)

def compare_quotes(quotes: list[Quote], max_age_seconds: int = 300) -> list[dict]:
    now = datetime.now(timezone.utc)
    groups = {}
    for q in quotes:
        try:
            timestamp = datetime.fromisoformat(q.observed_at.replace("Z", "+00:00"))
            if timestamp.tzinfo is None or not 0 <= (now - timestamp).total_seconds() <= max_age_seconds:
                continue
        except ValueError:
            continue
        groups.setdefault((q.event_id, q.market, q.selection), []).append(q)
    findings = []
    for key, group in groups.items():
        if len({q.sportsbook for q in group}) < 2:
            continue
        best = max(group, key=lambda q: decimal_odds(q.american_odds))
        findings.append({"event_id": key[0], "market": key[1], "selection": key[2],
                         "best_book": best.sportsbook, "best_odds": best.american_odds,
                         "books_compared": len({q.sportsbook for q in group}),
                         "quotes": [q.__dict__ for q in group],
                         "warning": "Price comparison only; no proven positive expected value."})
    return findings
