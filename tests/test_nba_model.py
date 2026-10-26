import pytest
from sports_agent.nba_model import fit_ratings, predict_home

def game(i, home="A", away="B", hs=110, aws=100):
    return {"id":str(i),"home_team":home,"away_team":away,
            "start_at":"2026-10-01T18:00:00Z","completed_at":"2026-10-01T21:00:00Z",
            "home_score":hs,"away_score":aws}

def test_training_uses_only_final_games():
    model=fit_ratings([game(1)],"2026-10-02T00:00:00Z")
    assert model["games_trained"]==1
    assert model["ratings"]["A"]>1500
    assert model["ratings"]["B"]<1500

def test_probability_is_symmetric():
    model=fit_ratings([game(1)],"2026-10-02T00:00:00Z")
    prediction=predict_home(model,"A","B","2026-10-03T00:00:00Z")
    assert prediction["home_probability"]+prediction["away_probability"]==pytest.approx(1)
    assert prediction["status"]=="unvalidated_baseline"

def test_future_training_leakage_rejected():
    with pytest.raises(ValueError):
        fit_ratings([game(1)],"2026-10-01T19:00:00Z")

def test_no_future_prediction_from_past_cutoff():
    model=fit_ratings([game(1)],"2026-10-02T00:00:00Z")
    with pytest.raises(ValueError):
        predict_home(model,"A","B","2026-10-01T00:00:00Z")

def test_no_unseen_team_fabrication():
    model=fit_ratings([game(1)],"2026-10-02T00:00:00Z")
    with pytest.raises(ValueError):
        predict_home(model,"A","C","2026-10-03T00:00:00Z")

def test_tied_nba_score_rejected():
    with pytest.raises(ValueError):
        fit_ratings([game(1,hs=100,aws=100)],"2026-10-02T00:00:00Z")

def test_duplicate_games_rejected():
    with pytest.raises(ValueError):
        fit_ratings([game(1),game(1)],"2026-10-02T00:00:00Z")

def test_offseason_regression_reduces_old_rating_advantage():
    first=game(1)
    first["start_at"]="2025-04-01T18:00:00Z"
    first["completed_at"]="2025-04-01T21:00:00Z"
    second=game(2)
    second["start_at"]="2025-10-21T18:00:00Z"
    second["completed_at"]="2025-10-21T21:00:00Z"
    baseline=fit_ratings([first,second],"2025-10-22T00:00:00Z")
    regressed=fit_ratings([first,second],"2025-10-22T00:00:00Z",offseason_retention=0)
    assert regressed["ratings"]["A"] < baseline["ratings"]["A"]

def test_invalid_offseason_retention_rejected():
    with pytest.raises(ValueError):
        fit_ratings([game(1)],"2026-10-02T00:00:00Z",offseason_retention=1.1)
