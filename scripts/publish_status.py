"""Publish timestamped dashboard snapshots from a persisted paper ledger.

This script does not place or settle tickets. It does not invent odds or results.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from sports_agent.sources import probe_espn
from sports_agent.odds_provider import probe_odds_api
from sports_agent.credit_budget import may_probe, record_attempt

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "paper_ledger.json"
OUTPUT = ROOT / "docs" / "status.json"

def build_status(ledger: dict, probes: dict, generated_at: str, odds_probe=None, odds_budget=None) -> dict:
    required = ("starting_bankroll", "realized_profit", "health", "wins", "losses", "open_tickets")
    if any(key not in ledger for key in required):
        raise ValueError("Missing required ledger field")
    health = ledger["health"]
    if not isinstance(health, int) or not 0 <= health <= 100:
        raise ValueError("Invalid health")
    if health == 0 and not ledger.get("terminated"):
        raise ValueError("Zero health requires durable termination before publication")
    equity = round(ledger["starting_bankroll"] + ledger["realized_profit"], 2)
    reserved = round(sum(float(t["stake"]) for t in ledger["open_tickets"]), 2)
    if equity < 0 or reserved > equity:
        raise ValueError("Inconsistent bankroll or reserved stakes")
    healthy = sum(bool(p.get("ok")) for p in probes.values())
    return {
        "schema_version": 1, "generated_at": generated_at, "verified_snapshot": True,
        "snapshot_type": "ledger_and_source_probe", "market_prices_verified": False,
        "health": health, "terminated": bool(ledger.get("terminated", False)),
        "equity": equity, "realized_profit": ledger["realized_profit"],
        "wins": ledger["wins"], "losses": ledger["losses"],
        "reserved_stakes": reserved, "available_bankroll": round(equity - reserved, 2),
        "open_tickets": ledger["open_tickets"],
        "source_probes": probes,
        "odds_provider_probe": odds_probe or {"ok": False, "reason": "not_checked"},
        "odds_budget": odds_budget or {},
        "activity": f"Scheduled source check: {healthy}/{len(probes)} ESPN feeds responding. No verified live sportsbook odds connected."
    }

def main():
    ledger = json.loads(LEDGER.read_text())
    leagues = ("nba", "nfl", "nhl", "mlb")
    probes = {}
    for league in leagues:
        try:
            result = probe_espn(league)
            probes[league] = {"ok": bool(result.get("ok")), "event_count": result.get("event_count"),
                              "http_status": result.get("http_status")}
        except Exception as exc:
            probes[league] = {"ok": False, "error": type(exc).__name__}
    now = datetime.now(timezone.utc).isoformat()
    previous = json.loads(OUTPUT.read_text()) if OUTPUT.exists() else {}
    gate = may_probe(previous)
    if gate["allowed"]:
        odds_probe = probe_odds_api()
        budget = record_attempt(gate)
    else:
        odds_probe = {**previous.get("odds_provider_probe", {}), "skipped": True,
                      "skip_reason": gate["reason"]}
        budget = {"month": gate["month"], "local_attempts": gate["local_attempts"]}
    status = build_status(ledger, probes, now, odds_probe, budget)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")
    print(f"Published snapshot at {now}: health={status['health']}%, equity=${status['equity']}, sources={status['activity']}")

if __name__ == "__main__":
    main()
