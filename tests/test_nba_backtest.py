from datetime import datetime, timedelta, timezone
from sports_agent.nba_backtest import backtest_elo

def games(n):
    start=datetime(2025,1,1,tzinfo=timezone.utc)
    output=[]
    for i in range(n):
        at=start+timedelta(days=i)
        output.append({"id":str(i),"home_team":"A" if i%2 else "B",
                       "away_team":"B" if i%2 else "A",
                       "start_at":at.isoformat(),"completed_at":(at+timedelta(hours=3)).isoformat(),
                       "home_score":110 if i%3 else 100,"away_score":100 if i%3 else 110,
                       "result_source":"verified test fixture"})
    return output

def test_no_data_is_not_approved():
    r=backtest_elo([],minimum_training_games=2,min_evaluation_games=3)
    assert r["sample_size"]==0
    assert not r["model_approved"]

def test_walk_forward_creates_pre_game_predictions():
    r=backtest_elo(games(10),minimum_training_games=3,min_evaluation_games=100)
    assert r["sample_size"]==7
    assert not r["model_approved"]
    assert r["status"]=="historical_research_only"
