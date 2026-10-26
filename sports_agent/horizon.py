"""Experimental settlement-time preference for paper candidates.

Expected settlement is an estimate, not a guarantee. Do not infer it from
game clocks alone. No ticket can be admitted without a sourced estimate.
"""

def preferred_max_minutes(stake: float) -> int:
    if stake <= 0:
        raise ValueError("Stake must be positive")
    if stake < 0.50:
        return 5
    if stake < 1:
        return 10
    if stake < 2.50:
        return 20
    if stake < 5:
        return 45
    if stake < 10:
        return 90
    return 240

def time_filter(stake: float, expected_settlement_minutes: float | None,
                settlement_source: str = "") -> dict:
    """Reject missing, negative or overly slow settlement estimates."""
    if stake <= 0:
        raise ValueError("Stake must be positive")
    limit = preferred_max_minutes(stake)
    if (not settlement_source or expected_settlement_minutes is None
            or isinstance(expected_settlement_minutes, bool)
            or not isinstance(expected_settlement_minutes, (int, float))
            or not 0 <= expected_settlement_minutes < float("inf")):
        return {"accepted": False, "reason": "Missing reliable settlement estimate",
                "max_minutes": limit}
    if expected_settlement_minutes > limit:
        return {"accepted": False, "reason": "Settlement estimate exceeds time preference",
                "max_minutes": limit}
    return {"accepted": True, "max_minutes": limit,
            "expected_settlement_minutes": expected_settlement_minutes}

def expected_profit_per_capital_hour(stake: float, ev_per_dollar: float,
                                     expected_settlement_minutes: float) -> float:
    """Comparison metric only; not a promise of realized or repeatable returns."""
    if stake <= 0 or expected_settlement_minutes <= 0:
        raise ValueError("Positive stake and duration required")
    return ev_per_dollar * 60 / expected_settlement_minutes
