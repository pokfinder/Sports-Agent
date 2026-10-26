from scripts.publish_status import build_status

BASE = dict(starting_bankroll=40, realized_profit=-7.4, health=80, wins=1, losses=3,
            terminated=False, open_tickets=[dict(stake=5, description="pending")])

def test_baseline_and_reservations():
    result = build_status(BASE, {"nba": {"ok": True}, "nfl": {"ok": False}}, "2026-10-26T12:00:00+00:00")
    assert result["equity"] == 32.6
    assert result["available_bankroll"] == 27.6
    assert result["market_prices_verified"] is False

def test_zero_health_must_be_terminal():
    import pytest
    with pytest.raises(ValueError):
        build_status({**BASE, "health": 0}, {}, "now")

def test_zero_health_terminal_snapshot():
    result = build_status({**BASE, "health": 0, "terminated": True}, {}, "now")
    assert result["terminated"] is True
