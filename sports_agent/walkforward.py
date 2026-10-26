"""Time-ordered out-of-sample audit for NBA moneyline probability forecasts.

This is a validation gate, not a probability model or an automatic betting system.
All probabilities must have been frozen before the game's scheduled start.
"""
from datetime import datetime, timezone
from math import isfinite
from .odds import decimal_odds
from .calibration import audit_predictions

def _utc(value):
    if not isinstance(value, str):
        raise ValueError("Missing timestamp")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Invalid timestamp") from exc
    if result.tzinfo is None:
        raise ValueError("Timezone required")
    return result.astimezone(timezone.utc)

def validate_holdout(rows, *, minimum=100, cutoff=None):
    """Evaluate strictly pregame predictions, with no training overlap.

    The cutoff separates model training and evaluation. The caller must supply
    a documented model-training cutoff; this function cannot verify its truth.
    """
    if not cutoff:
        raise ValueError("Model training cutoff required")
    training_cutoff = _utc(cutoff)
    if not isinstance(rows, list):
        raise ValueError("Expected prediction list")
    verified = []
    seen = set()
    net_units = 0.0
    staked = 0.0
    for r in rows:
        if not isinstance(r, dict):
            raise ValueError("Invalid row")
        event = r.get("event_id")
        selection = r.get("selection")
        key = (event, selection)
        if not isinstance(event, str) or not event or not isinstance(selection, str) or not selection or key in seen:
            raise ValueError("Missing or duplicate selection")
        seen.add(key)
        observed = _utc(r.get("predicted_at"))
        start = _utc(r.get("start_at"))
        settled = _utc(r.get("settled_at"))
        if not training_cutoff < observed < start < settled:
            raise ValueError("Chronology or training leakage detected")
        p = r.get("probability")
        outcome = r.get("outcome")
        odds = r.get("american_odds")
        if type(p) not in (int, float) or not isfinite(p) or not 0 <= p <= 1:
            raise ValueError("Invalid probability")
        if type(outcome) is not int or outcome not in (0, 1):
            raise ValueError("Only verified win/loss outcomes supported")
        if type(odds) is not int or -100 < odds < 100:
            raise ValueError("Invalid quoted odds")
        if not all(isinstance(r.get(k), str) and r[k].strip() for k in ("model_version", "quote_source", "settlement_source")):
            raise ValueError("Missing source or model provenance")
        # One unit per prediction; all selections counted, not just winning bets.
        net_units += (decimal_odds(odds)-1) if outcome else -1
        staked += 1
        verified.append({"id": event + "|" + selection, "probability": p,
                         "outcome": outcome, "prediction_recorded_at": r["predicted_at"],
                         "settlement_source": r["settlement_source"]})
    metrics = audit_predictions(verified, min_samples=minimum)
    # Model quality and positive ROI are separate conditions.
    roi = net_units / staked if staked else None
    metrics.update({"holdout_cutoff": cutoff, "flat_stake_roi": round(roi, 6) if roi is not None else None,
                    "net_units": round(net_units, 4), "paper_entries_enabled": False,
                    "warning": "Audit only. No model training, automated wagers, or proof of future profit."})
    return metrics
