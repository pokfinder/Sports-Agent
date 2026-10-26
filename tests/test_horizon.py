from sports_agent.horizon import preferred_max_minutes, time_filter, expected_profit_per_capital_hour

def test_tiers():
    assert preferred_max_minutes(.48) == 5
    assert preferred_max_minutes(.50) == 10
    assert preferred_max_minutes(2.5) == 45
    assert preferred_max_minutes(10) == 240

def test_fast_small_stakes():
    assert time_filter(.48, 4, "market settlement schedule")["accepted"]
    assert not time_filter(.48, 120, "market settlement schedule")["accepted"]

def test_unknown_settlement_not_accepted():
    assert not time_filter(.50, None)["accepted"]

def test_time_efficiency_metric():
    assert round(expected_profit_per_capital_hour(.50, .1, 5), 2) == 1.2
