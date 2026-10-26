from sports_agent.paper import PaperLedger

def test_health_baseline():
    ledger = PaperLedger()
    assert ledger.health == 80
    assert ledger.equity == 32.60

def test_push_does_not_change_health():
    ledger = PaperLedger()
    ledger.settle("push-test", 5, 100, "push")
    assert ledger.health == 80

def test_health_is_capped():
    ledger = PaperLedger(health=100)
    ledger.settle("win-test", 5, 100, "win")
    assert ledger.health == 100
