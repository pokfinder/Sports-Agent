"""Risk-controlled selection for the fictional sports portfolio."""
from .edge import Policy, evaluate

def select_paper_candidates(opportunities, equity, reserved_stakes=0, health=100, policy=Policy()):
    if not 0 <= health <= 100:
        raise ValueError("Invalid health")
    if equity < 0 or reserved_stakes < 0 or reserved_stakes > equity:
        raise ValueError("Invalid balance")
    if health == 0:
        return {"status": "terminated", "accepted": [], "rejected": []}
    accepted, rejected = [], []
    reserved = reserved_stakes
    seen = set()
    for item in opportunities:
        q = item["quote"]
        key = (q.event_id, q.market, q.selection)
        if key in seen:
            rejected.append({"event_id": q.event_id, "reason": "Duplicate selection"})
            continue
        result = evaluate(q, item["estimated_probability"], equity - reserved,
                          reserved_stakes=reserved, policy=policy,
                          probability_source=item.get("probability_source", ""),
                          model_uncertainty=item.get("model_uncertainty", 0))
        if result["status"] == "candidate":
            accepted.append(result)
            reserved = round(reserved + result["paper_stake"], 2)
            seen.add(key)
        else:
            rejected.append(result)
    return {"status": "active", "accepted": accepted, "rejected": rejected,
            "reserved_stakes": reserved, "available_bankroll": round(equity - reserved, 2)}
