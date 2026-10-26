"""Research-only two-way moneyline market consensus.

These estimates derive from sportsbook prices, NOT an independent predictive
model. Never treat them as verified positive EV or automatic paper entries.
"""
from statistics import median
from math import isfinite
from .odds import implied_probability, decimal_odds

def research_moneylines(events, min_other_books=3):
    findings = []
    if not isinstance(events, list):
        raise ValueError("Events must be a list")
    for event in events:
        if not isinstance(event, dict):
            continue
        event_id = event.get("id")
        home, away = event.get("home_team"), event.get("away_team")
        if not all(isinstance(x, str) and x for x in (event_id, home, away)) or home == away:
            continue
        quotes = []
        for book in event.get("bookmakers", []):
            if not isinstance(book, dict) or not book.get("key"):
                continue
            for market in book.get("markets", []):
                if not isinstance(market, dict) or market.get("key") != "h2h":
                    continue
                outcomes = market.get("outcomes", [])
                if len(outcomes) != 2:
                    continue
                prices = {x.get("name"): x.get("price") for x in outcomes if isinstance(x, dict)}
                if set(prices) != {home, away}:
                    continue
                if any(type(v) is not int or -100 < v < 100 for v in prices.values()):
                    continue
                implied = {team: implied_probability(price) for team, price in prices.items()}
                overround = sum(implied.values())
                if not 1 <= overround <= 1.25:
                    continue
                quotes.append({"book": str(book["key"]), "prices": prices,
                               "fair": {team: implied[team]/overround for team in (home, away)}})
        # One market per sportsbook; avoid double-counting duplicated feeds.
        by_book = {q["book"]: q for q in quotes}
        quotes = list(by_book.values())
        for q in quotes:
            peers = [other for other in quotes if other["book"] != q["book"]]
            if len(peers) < min_other_books:
                continue
            for team in (home, away):
                consensus = median(other["fair"][team] for other in peers)
                price = q["prices"][team]
                ev = consensus * decimal_odds(price) - 1
                if ev <= 0:
                    continue
                findings.append({"event_id": event_id, "selection": team,
                                 "sportsbook": q["book"], "american_odds": price,
                                 "break_even_probability": round(implied_probability(price), 5),
                                 "peer_no_vig_probability": round(consensus, 5),
                                 "market_implied_ev": round(ev, 5),
                                 "peer_book_count": len(peers),
                                 "status": "research_only",
                                 "warning": "Market-consensus discrepancy, not independently validated positive EV."})
    return sorted(findings, key=lambda x: x["market_implied_ev"], reverse=True)
