"""Paper-only market evaluation with conservative risk controls.

Only compare exact same event/market/line. Inputs must be sourced externally;
this module NEVER invents prices, win probabilities, or opportunities.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from .odds import Quote, implied_probability, decimal_odds, expected_value_per_dollar

@dataclass(frozen=True)
class Policy:
    min_stake: float = 0.01
    max_fraction_bankroll: float = 0.15
    max_total_fraction: float = 0.35
    min_ev: float = 0.02
    max_age_seconds: int = 180
    kelly_fraction: float = 0.25

def no_vig_two_way(odds_a: int, odds_b: int) -> tuple[float, float]:
    """Normalize a two-sided market; only appropriate for matched two-way lines."""
    a, b = implied_probability(odds_a), implied_probability(odds_b)
    if a + b <= 0:
        raise ValueError("Invalid market")
    return a / (a + b), b / (a + b)

def fractional_kelly(odds: int, estimated_probability: float, fraction: float = 0.25) -> float:
    if not 0 <= estimated_probability <= 1 or not 0 <= fraction <= 1:
        raise ValueError("Probability and Kelly fraction must be within [0, 1]")
    b = decimal_odds(odds) - 1
    return max(0.0, fraction * (estimated_probability * (b + 1) - 1) / b)

def evaluate(
    quote: Quote, estimated_probability: float, available_bankroll: float,
    reserved_stakes: float = 0, policy: Policy = Policy(),
    probability_source: str = "", model_uncertainty: float = 0.0,
) -> dict:
    """Return a reject or a paper candidate; probability must have provenance.

    Model uncertainty is an absolute probability margin deducted for sizing and
    admission, not a claimed statistical confidence interval.
    """
    base = {"event_id": quote.event_id, "market": quote.market,
            "selection": quote.selection, "sportsbook": quote.sportsbook,
            "american_odds": quote.american_odds, "source": quote.source,
            "observed_at": quote.observed_at, "status": "reject"}
    if not probability_source or not quote.source:
        return {**base, "reason": "Missing independent probability or quote provenance"}
    if not 0 <= estimated_probability <= 1 or not 0 <= model_uncertainty <= 1:
        return {**base, "reason": "Invalid probability or uncertainty"}
    try:
        observed = datetime.fromisoformat(quote.observed_at.replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - observed).total_seconds()
    except ValueError:
        return {**base, "reason": "Invalid quote timestamp"}
    if observed.tzinfo is None or not 0 <= age <= policy.max_age_seconds:
        return {**base, "reason": "Stale, future, or timezone-naive quote"}
    conservative_probability = max(0.0, estimated_probability - model_uncertainty)
    ev = expected_value_per_dollar(quote.american_odds, conservative_probability)
    if ev < policy.min_ev:
        return {**base, "reason": "Insufficient conservative expected value",
                "conservative_ev": round(ev, 5)}
    if available_bankroll < policy.min_stake:
        return {**base, "reason": "Insufficient available bankroll"}
    # available_bankroll already excludes reserved stakes; enforce overall exposure
    total_bankroll = available_bankroll + reserved_stakes
    remaining_exposure = max(0, policy.max_total_fraction * total_bankroll - reserved_stakes)
    kelly_stake = available_bankroll * fractional_kelly(
        quote.american_odds, conservative_probability, policy.kelly_fraction)
    stake = min(kelly_stake, available_bankroll * policy.max_fraction_bankroll,
                remaining_exposure, available_bankroll)
    stake = int(stake * 100) / 100
    if stake < policy.min_stake:
        return {**base, "reason": "Calculated safe stake below minimum",
                "conservative_ev": round(ev, 5), "calculated_stake": stake}
    return {**base, "status": "candidate", "paper_stake": stake,
            "conservative_probability": round(conservative_probability, 5),
            "conservative_ev": round(ev, 5), "probability_source": probability_source,
            "note": "Candidate only: validate market match and executable price before paper entry."}
