"""Probe authorized The Odds API feed without exposing credentials or raw prices."""
import os
import requests

ENDPOINT = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"

def probe_odds_api(api_key=None, get=requests.get):
    key = api_key if api_key is not None else os.environ.get("ODDS_API_KEY", "")
    if not key:
        return {"ok": False, "reason": "secret_not_configured", "prices_verified": False}
    try:
        response = get(ENDPOINT, params={"apiKey": key, "regions": "us",
                        "markets": "h2h", "oddsFormat": "american"}, timeout=15)
        # Do not expose provider error bodies: some can echo request parameters.
        if response.status_code != 200:
            return {"ok": False, "http_status": response.status_code,
                    "reason": "provider_request_failed", "prices_verified": False}
        events = response.json()
        if not isinstance(events, list):
            return {"ok": False, "reason": "unexpected_payload", "prices_verified": False}
        books = sorted({str(b.get("key", "")) for e in events if isinstance(e, dict)
                        for b in e.get("bookmakers", []) if isinstance(b, dict)})
        usage = {}
        for header, name in (("x-requests-remaining", "credits_remaining"),
                             ("x-requests-used", "credits_used"),
                             ("x-requests-last", "credits_last")):
            raw = response.headers.get(header)
            if raw is not None:
                try:
                    usage[name] = max(0, int(raw))
                except ValueError:
                    pass
        return {"ok": True, "http_status": 200, **usage, "event_count": len(events),
                "bookmaker_count": len(books), "bet365_present": "bet365" in books,
                "prices_verified": False,
                "note": "Feed connectivity only; no market prices stored or validated"}
    except (requests.RequestException, ValueError, TypeError, KeyError):
        return {"ok": False, "reason": "feed_or_network_error", "prices_verified": False}
