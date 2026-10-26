from datetime import datetime, timezone
import pytest
from sports_agent.feed import ingest_payload, normalize_quote

NOW = datetime(2026, 10, 26, 12, 0, tzinfo=timezone.utc)
BASE = {"event_id":"evt1","market":"moneyline","selection":"Home",
        "sportsbook":"Bet365","american_odds":150,"observed_at":"2026-10-26T11:59:00Z"}

def test_authorized_fresh_quote():
    quote = normalize_quote(BASE, provider="licensed-test-provider", now=NOW)
    assert quote.american_odds == 150
    assert quote.source == "licensed-test-provider"

def test_stale_or_future_rejected():
    for timestamp in ("2026-10-26T11:50:00Z", "2026-10-26T12:00:01Z"):
        with pytest.raises(ValueError):
            normalize_quote({**BASE, "observed_at":timestamp}, provider="test", now=NOW)

def test_no_ambiguous_prop_line():
    with pytest.raises(ValueError):
        normalize_quote({**BASE, "market":"player prop rebounds"}, provider="test", now=NOW)
    quote = normalize_quote({**BASE, "market":"player prop rebounds", "line":5.5},
                            provider="test", now=NOW)
    assert "line=5.5" in quote.market

def test_invalid_odds_and_no_provider():
    with pytest.raises(ValueError):
        normalize_quote({**BASE, "american_odds":-90}, provider="test", now=NOW)
    with pytest.raises(ValueError):
        ingest_payload({"quotes":[BASE]}, now=NOW)

def test_batch_rejects_invalid_quote():
    with pytest.raises(ValueError):
        ingest_payload({"provider":"licensed", "quotes":[BASE,{**BASE,"american_odds":0}]}, now=NOW)
