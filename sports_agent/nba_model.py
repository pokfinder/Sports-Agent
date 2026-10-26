"""Simple transparent NBA pregame rating model.

Ratings are estimated only from games completed before a specified cutoff.
No sportsbook odds are used to fit this model. This is a baseline for
out-of-sample evaluation, not a validated betting signal.
"""
from datetime import datetime, timezone
from math import exp, isfinite, log

def utc(value):
    if not isinstance(value, str):
        raise ValueError("Timestamp required")
    try:
        d = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Invalid timestamp") from exc
    if d.tzinfo is None:
        raise ValueError("Timezone required")
    return d.astimezone(timezone.utc)

def fit_ratings(games, cutoff, *, k=20.0, home_advantage=65.0):
    """Fit online Elo ratings from finalized chronological NBA games.

    k and home_advantage are fixed prior assumptions; tune on a training set,
    never on the held-out games.
    """
    boundary = utc(cutoff)
    if not 0 < k <= 100 or not -300 <= home_advantage <= 300:
        raise ValueError("Invalid rating parameters")
    seen = set()
    clean = []
    for game in games:
        if not isinstance(game, dict):
            raise ValueError("Invalid game")
        gid = game.get("id")
        home, away = game.get("home_team"), game.get("away_team")
        start, end = utc(game.get("start_at")), utc(game.get("completed_at"))
        hs, aws = game.get("home_score"), game.get("away_score")
        if not all(isinstance(x, str) and x for x in (gid, home, away)) or home == away or gid in seen:
            raise ValueError("Missing or duplicate game identity")
        if not start < end <= boundary:
            raise ValueError("Training game is unfinished or after cutoff")
        if type(hs) is not int or type(aws) is not int or min(hs, aws) < 0 or hs == aws:
            raise ValueError("Invalid final NBA score")
        seen.add(gid)
        clean.append((end, gid, home, away, hs, aws))
    clean.sort()
    ratings = {}
    for _, _, home, away, hs, aws in clean:
        h, a = ratings.get(home, 1500.0), ratings.get(away, 1500.0)
        p = 1 / (1 + 10 ** ((a - h - home_advantage) / 400))
        delta = k * ((1 if hs > aws else 0) - p)
        ratings[home] = h + delta
        ratings[away] = a - delta
    return {"ratings": ratings, "games_trained": len(clean), "trained_through": cutoff,
            "k": k, "home_advantage": home_advantage, "model_version": "nba_elo_v1"}

def predict_home(model, home, away, start_at):
    if not isinstance(model, dict) or model.get("model_version") != "nba_elo_v1":
        raise ValueError("Unknown model")
    if utc(start_at) <= utc(model["trained_through"]):
        raise ValueError("Prediction must occur after training cutoff")
    if home == away or not home or not away:
        raise ValueError("Invalid matchup")
    ratings = model["ratings"]
    if home not in ratings or away not in ratings:
        raise ValueError("Unknown team; no invented ratings")
    h, a = ratings[home], ratings[away]
    probability = 1 / (1 + 10 ** ((a-h-model["home_advantage"])/400))
    return {"home_probability": round(probability, 6),
            "away_probability": round(1-probability, 6),
            "model_version": model["model_version"], "trained_through": model["trained_through"],
            "status": "unvalidated_baseline"}
