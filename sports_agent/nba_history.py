"""Historical NBA final-score ingestion from ESPN's public, unofficial scoreboard.

Use explicit date ranges; do not claim completeness when any day fails.
No sportsbook API calls or credentials required.
"""
from datetime import date, timedelta
import requests

URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"

def parse_scoreboard(payload, *, source="ESPN public scoreboard"):
    if not isinstance(payload, dict) or not isinstance(payload.get("events"), list):
        raise ValueError("Invalid ESPN scoreboard")
    games = []
    for event in payload["events"]:
        if not isinstance(event, dict) or not event.get("id"):
            continue
        competitions = event.get("competitions") or []
        if len(competitions) != 1:
            continue
        competition = competitions[0]
        status = competition.get("status") or event.get("status") or {}
        if status.get("type", {}).get("completed") is not True:
            continue
        competitors = competition.get("competitors") or []
        if len(competitors) != 2:
            continue
        sides = {c.get("homeAway"): c for c in competitors if isinstance(c, dict)}
        if set(sides) != {"home", "away"}:
            continue
        home, away = sides["home"], sides["away"]
        if not all(isinstance(c.get("team", {}).get("id"), str) for c in (home, away)):
            continue
        try:
            hs, aws = int(home["score"]), int(away["score"])
        except (ValueError, TypeError, KeyError):
            continue
        if min(hs, aws) < 0 or hs == aws:
            continue
        start = event.get("date")
        end = status.get("type", {}).get("completed_at")
        # ESPN does not reliably publish an exact game completion timestamp.
        # Use a conservative proxy at least 6 hours after scheduled tipoff.
        # This is not a verified actual completion time.
        from datetime import datetime, timedelta, timezone
        try:
            tip = datetime.fromisoformat(start.replace("Z", "+00:00"))
            if tip.tzinfo is None:
                continue
        except (ValueError, AttributeError):
            continue
        conservative_end = (tip + timedelta(hours=6)).astimezone(timezone.utc).isoformat()
        games.append({"id": str(event["id"]),
                      "home_team": str(home["team"]["id"]),
                      "away_team": str(away["team"]["id"]),
                      "start_at": tip.astimezone(timezone.utc).isoformat(),
                      "completed_at": conservative_end,
                      "completion_time_is_proxy": True,
                      "home_score": hs, "away_score": aws,
                      "result_source": source})
    return games

def fetch_historical_games(start_date, end_date, *, get=requests.get, max_days=90):
    first, last = date.fromisoformat(start_date), date.fromisoformat(end_date)
    count = (last-first).days+1
    if not 1 <= count <= max_days:
        raise ValueError("Invalid date range")
    results = {}
    for offset in range(count):
        day = first+timedelta(days=offset)
        response = get(URL, params={"dates": day.strftime("%Y%m%d"), "limit": 200},
                       timeout=15, headers={"User-Agent": "SportsAgentResearch/0.1"})
        response.raise_for_status()
        for game in parse_scoreboard(response.json()):
            if game["id"] in results and results[game["id"]] != game:
                raise ValueError("Conflicting duplicate historical result")
            results[game["id"]] = game
    return sorted(results.values(), key=lambda g: (g["start_at"],g["id"]))
