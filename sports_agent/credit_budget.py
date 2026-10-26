"""Conservative credit gate for scheduled Odds API sampling.

The provider's remaining-credit header is authoritative when available.
The local count is only a fallback and must not be used to exceed a hard cap.
"""
from datetime import datetime, timezone

MONTHLY_SOFT_CAP = 350
RESERVE_CREDITS = 150

def may_probe(previous: dict, now=None) -> dict:
    now = now or datetime.now(timezone.utc)
    month = now.strftime("%Y-%m")
    budget = previous.get("odds_budget", {}) if isinstance(previous, dict) else {}
    used_local = budget.get("local_attempts", 0) if budget.get("month") == month else 0
    if not isinstance(used_local, int) or used_local < 0:
        used_local = 0
    prior_provider = previous.get("odds_provider_probe", {}) if isinstance(previous, dict) else {}
    remaining = prior_provider.get("credits_remaining")
    if used_local > 0 and not isinstance(remaining, int):
        return {"allowed": False, "reason": "provider_usage_unknown",
                "month": month, "local_attempts": used_local}
    if isinstance(remaining, int) and remaining <= RESERVE_CREDITS:
        return {"allowed": False, "reason": "provider_reserve_reached",
                "month": month, "local_attempts": used_local}
    if used_local >= MONTHLY_SOFT_CAP:
        return {"allowed": False, "reason": "monthly_soft_cap_reached",
                "month": month, "local_attempts": used_local}
    return {"allowed": True, "month": month, "local_attempts": used_local}

def record_attempt(gate: dict) -> dict:
    return {"month": gate["month"], "local_attempts": gate["local_attempts"] + 1,
            "monthly_soft_cap": MONTHLY_SOFT_CAP, "reserve_credits": RESERVE_CREDITS}
