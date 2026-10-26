import pytest
from sports_agent.walkforward import validate_holdout

def row(i, p=.6, result=1):
    return {"event_id":str(i),"selection":"Home","predicted_at":"2026-10-02T12:00:00Z",
            "start_at":"2026-10-02T19:00:00Z","settled_at":"2026-10-02T22:00:00Z",
            "probability":p,"outcome":result,"american_odds":110,
            "model_version":"v1","quote_source":"licensed_feed",
            "settlement_source":"official_result"}

def test_holdout_is_research_only():
    result=validate_holdout([row(1)],cutoff="2026-10-01T00:00:00Z")
    assert result["sample_size"]==1
    assert result["net_units"]==1.1
    assert result["flat_stake_roi"]==1.1
    assert not result["paper_entries_enabled"]
    assert not result["model_approved"]

def test_missing_cutoff_rejected():
    with pytest.raises(ValueError):
        validate_holdout([row(1)])

def test_leaked_prediction_rejected():
    r=row(1)
    r["predicted_at"]="2026-10-02T20:00:00Z"
    with pytest.raises(ValueError):
        validate_holdout([r],cutoff="2026-10-01T00:00:00Z")

def test_training_overlap_rejected():
    with pytest.raises(ValueError):
        validate_holdout([row(1)],cutoff="2026-10-02T13:00:00Z")

def test_duplicate_selection_rejected():
    with pytest.raises(ValueError):
        validate_holdout([row(1),row(1)],cutoff="2026-10-01T00:00:00Z")

def test_unverified_outcome_rejected():
    r=row(1)
    r["settlement_source"]=""
    with pytest.raises(ValueError):
        validate_holdout([r],cutoff="2026-10-01T00:00:00Z")

def test_losing_picks_count_toward_roi():
    results=validate_holdout([row(1),row(2,result=0)],cutoff="2026-10-01T00:00:00Z")
    assert results["net_units"]==.1
    assert results["flat_stake_roi"]==.05
