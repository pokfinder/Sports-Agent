"""Evaluate the NBA Elo baseline in chronological, pregame walk-forward order.

Historical games must be sourced externally with documented provenance.
This deliberately produces no bets and requires no Odds API credits.
"""
from .nba_model import fit_ratings, predict_home, utc
from .calibration import audit_predictions

def backtest_elo(games, *, minimum_training_games=100, min_evaluation_games=100,
                 k=20.0, home_advantage=65.0):
    if not isinstance(games, list) or minimum_training_games < 1:
        raise ValueError("Invalid game dataset")
    ordered = sorted(games, key=lambda g: utc(g["start_at"]))
    predictions = []
    skipped = 0
    for i in range(minimum_training_games, len(ordered)):
        target = ordered[i]
        start = utc(target["start_at"])
        # Avoid leakage from earlier games that finished after target tipped off.
        history = [g for g in ordered[:i] if utc(g["completed_at"]) < start]
        if len(history) < minimum_training_games:
            skipped += 1
            continue
        model = fit_ratings(history, max(g["completed_at"] for g in history),
                            k=k, home_advantage=home_advantage)
        try:
            p = predict_home(model, target["home_team"], target["away_team"], target["start_at"])["home_probability"]
        except ValueError:
            skipped += 1
            continue
        hs, aws = target.get("home_score"), target.get("away_score")
        if type(hs) is not int or type(aws) is not int or hs == aws or min(hs,aws) < 0:
            raise ValueError("Target must have verified final NBA score")
        if not target.get("result_source"):
            raise ValueError("Final-score provenance required")
        predictions.append({"id": target["id"], "probability": p,
                            "outcome": int(hs > aws),
                            "prediction_recorded_at": model["trained_through"],
                            "settlement_source": target["result_source"]})
    result = audit_predictions(predictions, min_samples=min_evaluation_games)
    result.update({"training_games_minimum": minimum_training_games,
                   "skipped_unknown_or_overlapping": skipped,
                   "status": "historical_research_only",
                   "note": "No sportsbook prices, stake sizing, or validated profit claims."})
    return result
