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
