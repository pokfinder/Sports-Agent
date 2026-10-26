from datetime import datetime, timezone
from sports_agent.odds import Quote, compare_quotes, implied_probability, expected_value_per_dollar
from sports_agent.paper import PaperLedger

def test_probabilities():
    assert abs(implied_probability(100) - 0.5) < 1e-10
    assert abs(implied_probability(-110) - 110 / 210) < 1e-10
    assert expected_value_per_dollar(100, .55) > 0

def test_best_quote_is_not_claimed_as_edge():
    now = datetime.now(timezone.utc).isoformat()
    qs = [Quote("a", "moneyline", "home", "A", -110, now, "test"),
          Quote("a", "moneyline", "home", "B", 105, now, "test")]
    result = compare_quotes(qs)
    assert result[0]["best_book"] == "B"
    assert "no proven" in result[0]["warning"]

def test_health_and_bankroll():
    ledger = PaperLedger()
    assert ledger.equity == 32.60
    ledger.settle("007", 5, 100, "win")
    assert ledger.health == 90
    assert ledger.equity == 37.60
