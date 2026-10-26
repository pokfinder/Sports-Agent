"""Best-effort public ESPN scoreboard connectivity probe.

ESPN's endpoint is unofficial, can change, and does not guarantee sportsbook
price availability. Never describe a score or cached price as an executable quote.
"""
import requests

LEAGUES = {
    "nba": ("basketball", "nba"),
    "nfl": ("football", "nfl"),
    "nhl": ("hockey", "nhl"),
    "mlb": ("baseball", "mlb"),
}

def probe_espn(league: str, timeout: int = 12) -> dict:
    if league not in LEAGUES:
        raise ValueError(f"Unsupported league: {league}")
    sport, code = LEAGUES[league]
    url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{code}/scoreboard"
    try:
        response = requests.get(url, timeout=timeout, headers={"User-Agent": "SportsAgentResearch/0.1"})
        response.raise_for_status()
        payload = response.json()
        events = payload.get("events", [])
        return {"league": league, "ok": True, "http_status": response.status_code,
                "event_count": len(events), "event_examples": [
                    {"id": event.get("id"), "name": event.get("name"),
                     "date": event.get("date")} for event in events[:3]],
                "odds_verified": False,
                "note": "Scoreboard accessible; current multi-book prices not established."}
    except (requests.RequestException, ValueError) as exc:
        return {"league": league, "ok": False, "error": str(exc), "odds_verified": False}
