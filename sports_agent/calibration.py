"""Auditable probability calibration for settled paper predictions.

Never infer a prediction from the outcome. Each row must represent a prediction
recorded before the event, with a verified binary settlement afterward.
"""
from math import isfinite, sqrt

def audit_predictions(records, *, min_samples=100, max_brier=0.25, max_ece=0.06):
    if not isinstance(records, list):
        raise ValueError("Records must be a list")
    ids = set()
    prepared = []
    for row in records:
        if not isinstance(row, dict):
            raise ValueError("Invalid prediction record")
        identifier = row.get("id")
        p = row.get("probability")
        result = row.get("outcome")
        if not isinstance(identifier, str) or not identifier or identifier in ids:
            raise ValueError("Missing or duplicate prediction id")
        if type(p) not in (float, int) or not isfinite(p) or not 0 <= p <= 1:
            raise ValueError("Invalid predicted probability")
        if type(result) is not int or result not in (0, 1):
            raise ValueError("Unverified or non-binary outcome")
        if not row.get("prediction_recorded_at") or not row.get("settlement_source"):
            raise ValueError("Prediction timestamp and verified settlement provenance required")
        ids.add(identifier)
        prepared.append((float(p), result))
    n = len(prepared)
    if not n:
        return {"sample_size": 0, "model_approved": False, "reason": "no_verified_predictions"}
    brier = sum((p-y)**2 for p,y in prepared)/n
    baseline = sum(y for _,y in prepared)/n
    baseline_brier = sum((baseline-y)**2 for _,y in prepared)/n
    buckets = [[] for _ in range(10)]
    for p,y in prepared:
        buckets[min(9,int(p*10))].append((p,y))
    ece = sum(len(b)/n*abs(sum(p for p,_ in b)/len(b)-sum(y for _,y in b)/len(b))
              for b in buckets if b)
    approved = n >= min_samples and brier < baseline_brier and brier <= max_brier and ece <= max_ece
    return {"sample_size": n, "brier_score": round(brier, 6),
            "constant_baseline_brier": round(baseline_brier, 6),
            "calibration_error": round(ece, 6),
            "model_approved": approved,
            "reason": "passes_preliminary_gates" if approved else "insufficient_calibration_evidence",
            "warning": "Passing historical metrics does not guarantee future profit; use time-ordered out-of-sample validation."}
