import pytest
from sports_agent.nba_probability_calibration import adjust, separated_calibration

def rows(n=220):
    return [{"id":str(i),"probability":0.9 if i%2 else 0.1,
             "outcome":1 if i%3 else 0,
             "prediction_recorded_at":"2025-10-01T00:00:00Z",
             "settlement_source":"test fixture"} for i in range(n)]

def test_shrink_toward_half():
    assert adjust(.9,.5)==pytest.approx(.7)

def test_later_holdout_remains_unapproved_for_trading():
    result=separated_calibration(rows())
    assert result["calibration_count"]==110
    assert result["holdout_count"]==110
    assert result["holdout_adjusted"]["sample_size"]==110
    assert not result["approved"]

def test_small_data_fail_closed():
    assert not separated_calibration([])["approved"]

def test_duplicate_rejected():
    data=rows()
    data[1]["id"]=data[0]["id"]
    with pytest.raises(ValueError):
        separated_calibration(data)
