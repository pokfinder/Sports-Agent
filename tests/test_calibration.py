import pytest
from sports_agent.calibration import audit_predictions

def record(i, p, outcome):
    return {"id": str(i), "probability": p, "outcome": outcome,
            "prediction_recorded_at": "2026-10-01T00:00:00Z",
            "settlement_source": "verified official final score"}

def test_empty_model_is_not_approved():
    assert not audit_predictions([])["model_approved"]

def test_four_predictions_do_not_approve_model():
    rows = [record(i, .8 if i % 2 else .2, i % 2) for i in range(4)]
    result = audit_predictions(rows)
    assert result["sample_size"] == 4
    assert result["brier_score"] == pytest.approx(.04)
    assert not result["model_approved"]

def test_duplicate_and_unverified_predictions_rejected():
    with pytest.raises(ValueError):
        audit_predictions([record(1, .6, 1), record(1, .7, 0)])
    row = record(2, .6, 1)
    row.pop("settlement_source")
    with pytest.raises(ValueError):
        audit_predictions([row])

def test_well_calibrated_large_sample_passes_preliminary_gate():
    rows = [record(i, .8 if i % 5 else .2, 1 if i % 5 else 0) for i in range(150)]
    assert audit_predictions(rows)["model_approved"]

def test_random_predictions_fail_baseline():
    rows = [record(i, .5, i % 2) for i in range(120)]
    assert not audit_predictions(rows)["model_approved"]
