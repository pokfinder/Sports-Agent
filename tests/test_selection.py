from datetime import datetime, timezone
from sports_agent.odds import Quote
from sports_agent.selection import select_paper_candidates

def opportunity(event, probability=0.7):
    q = Quote(event, "moneyline", "home", "Example", 150,
              datetime.now(timezone.utc).isoformat(), "licensed-source")
    return {"quote":q, "estimated_probability":probability,
            "probability_source":"independent calibrated model",
            "model_uncertainty":0.03, "expected_settlement_minutes":4,
            "settlement_source":"verified market rules"}

def test_small_bankroll_allows_fractional_stakes():
    result = select_paper_candidates([opportunity("a")], 32.6, 5, 80)
    assert len(result["accepted"]) == 1
    assert 0.01 <= result["accepted"][0]["paper_stake"] < 5

def test_large_bankroll_can_select_without_double_counting():
    result = select_paper_candidates([opportunity("a"), opportunity("a"), opportunity("b")], 200, 0, 80)
    assert len(result["accepted"]) >= 1
    assert len(result["accepted"]) <= 2
    assert result["reserved_stakes"] <= 70

def test_zero_health_blocks_all_entries():
    result = select_paper_candidates([opportunity("a")], 200, 0, 0)
    assert result["status"] == "terminated"
    assert result["accepted"] == []
