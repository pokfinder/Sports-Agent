from sports_agent.nba_history import parse_scoreboard, fetch_historical_games
import pytest

def payload(completed=True):
    return {"events":[{"id":"123","date":"2025-10-25T23:00:00Z",
      "competitions":[{"status":{"type":{"completed":completed}},
        "competitors":[
          {"homeAway":"home","team":{"id":"1"},"score":"110"},
          {"homeAway":"away","team":{"id":"2"},"score":"100"}]}]}]}

def test_completed_game_has_explicit_proxy_flag():
    rows=parse_scoreboard(payload())
    assert len(rows)==1
    assert rows[0]["completion_time_is_proxy"]
    assert rows[0]["home_score"]==110
    assert rows[0]["completed_at"].startswith("2025-10-26T05:00:00")

def test_incomplete_game_excluded():
    assert parse_scoreboard(payload(False))==[]

def test_malformed_payload_rejected():
    with pytest.raises(ValueError):
        parse_scoreboard({})

def test_fetch_one_day_without_network():
    class Response:
        def raise_for_status(self): pass
        def json(self): return payload()
    calls=[]
    def fake_get(url,params,timeout,headers):
        calls.append(params["dates"])
        return Response()
    games=fetch_historical_games("2025-10-25","2025-10-25",get=fake_get)
    assert len(games)==1
    assert calls==["20251025"]

def test_bad_range_fails_closed():
    with pytest.raises(ValueError):
        fetch_historical_games("2025-11-01","2025-10-01",get=lambda *a,**k: None)
