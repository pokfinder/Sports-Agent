from datetime import datetime, timezone
from sports_agent.credit_budget import may_probe, record_attempt

NOW = datetime(2026, 10, 26, tzinfo=timezone.utc)

def test_first_request_allowed():
    assert may_probe({}, NOW)["allowed"]

def test_credit_reserve_blocks():
    previous = {"odds_budget": {"month": "2026-10", "local_attempts": 12},
                "odds_provider_probe": {"credits_remaining": 150}}
    assert not may_probe(previous, NOW)["allowed"]

def test_unknown_provider_usage_blocks_after_first():
    previous = {"odds_budget": {"month": "2026-10", "local_attempts": 1}}
    assert may_probe(previous, NOW)["reason"] == "provider_usage_unknown"

def test_records_attempt():
    gate = may_probe({}, NOW)
    assert record_attempt(gate)["local_attempts"] == 1
