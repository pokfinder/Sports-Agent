from datetime import datetime, timedelta, timezone
from sports_agent.edge import Policy, evaluate, fractional_kelly, no_vig_two_way
from sports_agent.odds import Quote

def quote(at=None):
    return Quote("event", "moneyline", "home", "ExampleBook", 120,
                 (at or datetime.now(timezone.utc)).isoformat(),
                 "https://example.org/quote")

def test_no_vig_sums_to_one():
    a, b = no_vig_two_way(-110, -110)
    assert abs(a + b - 1) < 1e-12
    assert abs(a - 0.5) < 1e-12

def test_negative_edge_zero_kelly():
    assert fractional_kelly(-150, 0.4) == 0

def test_reject_stale():
    result = evaluate(quote(datetime.now(timezone.utc) - timedelta(minutes=20)),
                      0.8, 100, probability_source="independent model")
    assert result["status"] == "reject"

def test_reject_no_provenance():
    result = evaluate(quote(), 0.8, 100)
    assert result["status"] == "reject"

def test_small_bankroll_does_not_force_minimum():
    result = evaluate(quote(), 0.6, 32.6, probability_source="independent model")
    assert result["status"] == "reject"
    assert result["reason"] == "Calculated safe stake below minimum"

def test_candidate_with_sufficient_edge_and_bankroll():
    result = evaluate(quote(), 0.7, 200, probability_source="independent model")
    assert result["status"] == "candidate"
    assert 5 <= result["paper_stake"] <= 30

def test_uncertainty_can_remove_edge():
    result = evaluate(quote(), 0.6, 200, probability_source="independent model",
                      model_uncertainty=0.15)
    assert result["status"] == "reject"
