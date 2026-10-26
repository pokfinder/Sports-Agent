"""Normalize authorized sportsbook odds feeds without scraping or credentials.

Provider adapters must supply UTC observations and explicit market/line identity.
No quote is assumed executable merely because it was observed.
"""
from datetime import datetime, timezone
from .odds import Quote

def normalize_quote(item: dict, *, provider: str, max_age_seconds: int = 180, now=None) -> Quote:
    required = ("event_id", "market", "selection", "sportsbook", "american_odds", "observed_at")
    if not provider or any(key not in item for key in required):
        raise ValueError("Missing provider or required quote field")
    if not all(isinstance(item[key], str) and item[key].strip()
               for key in ("event_id", "market", "selection", "sportsbook", "observed_at")):
        raise ValueError("Invalid quote identifiers")
    odds = item["american_odds"]
    if type(odds) is not int or (-100 < odds < 100):
        raise ValueError("Invalid American odds")
    observed = datetime.fromisoformat(item["observed_at"].replace("Z", "+00:00"))
    current = now or datetime.now(timezone.utc)
    if observed.tzinfo is None or current.tzinfo is None:
        raise ValueError("Timezone required")
    age = (current - observed).total_seconds()
    if age < 0 or age > max_age_seconds:
        raise ValueError("Future or stale odds")
    # Require explicit line identity for spreads/totals/props, so unlike lines cannot mix.
    market = item["market"].strip()
    if any(token in market.lower() for token in ("spread", "total", "over", "under", "prop")):
        line = item.get("line")
        if isinstance(line, bool) or not isinstance(line, (int, float)):
            raise ValueError("Numerical line required for spread, total, or prop")
        market = f"{market} | line={line:g}"
    return Quote(
        event_id=item["event_id"].strip(), market=market,
        selection=item["selection"].strip(), sportsbook=item["sportsbook"].strip(),
        american_odds=odds, observed_at=item["observed_at"], source=provider
    )

def ingest_payload(payload: dict, *, max_age_seconds: int = 180, now=None) -> dict:
    """Reject entire payload on malformed quotes rather than silently accept bad pricing."""
    if not isinstance(payload, dict) or not isinstance(payload.get("quotes"), list):
        raise ValueError("Expected object with quotes list")
    provider = payload.get("provider")
    if not isinstance(provider, str) or not provider.strip():
        raise ValueError("Missing data provider")
    quotes = [normalize_quote(item, provider=provider, max_age_seconds=max_age_seconds, now=now)
              for item in payload["quotes"]]
    return {"provider": provider, "quotes": quotes, "count": len(quotes),
            "note": "Observed odds only; account access and execution not supported"}
