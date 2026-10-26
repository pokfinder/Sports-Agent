"""Calibrate Elo on earlier predictions, audit on later untouched predictions.

Shrinks probabilities toward 50%, selected using Brier score on a calibration
period only. This does not establish betting profitability.
"""
from .calibration import audit_predictions

SHRINK_FACTORS = (0.0, 0.25, 0.5, 0.75, 1.0)

def adjust(p, factor):
    return 0.5 + factor * (p - 0.5)

def separated_calibration(predictions, *, calibration_fraction=0.5, min_holdout=100):
    if not isinstance(predictions, list) or not 0 < calibration_fraction < 1:
        raise ValueError("Invalid predictions or split")
    # backtest_elo outputs predictions in game-tipoff order.
    n = len(predictions)
    split = int(n * calibration_fraction)
    if split < 1 or n - split < 1:
        return {"approved": False, "reason": "insufficient_split_data",
                "calibration_count": split, "holdout_count": n-split}
    first, last = predictions[:split], predictions[split:]
    if len({r["id"] for r in predictions}) != n:
        raise ValueError("Duplicate game ID")
    def brier(rows, factor):
        return sum((adjust(r["probability"],factor)-r["outcome"])**2 for r in rows)/len(rows)
    factor = min(SHRINK_FACTORS, key=lambda f: (brier(first,f),f))
    calibrated = [{**r,"probability":adjust(r["probability"],factor)} for r in last]
    raw = audit_predictions(last,min_samples=min_holdout)
    adjusted = audit_predictions(calibrated,min_samples=min_holdout)
    return {"status": "research_only", "shrink_factor":factor,
            "calibration_count":len(first), "holdout_count":len(last),
            "calibration_period_brier":round(brier(first,factor),6),
            "holdout_raw":raw, "holdout_adjusted":adjusted,
            "approved":False,
            "warning":"Research-only. Holdout approval does not establish real betting edge; no historical odds."}
