"""Demonstration with SYNTHETIC quotes, not live sports odds."""
import json
from datetime import datetime, timezone
from sports_agent.edge import evaluate
from sports_agent.odds import Quote

def main():
    fake = Quote("DEMO-ONLY", "moneyline", "team-A", "EXAMPLE-NOT-A-SPORTSBOOK",
                 120, datetime.now(timezone.utc).isoformat(), "synthetic://example")
    result = evaluate(fake, 0.70, 200, probability_source="synthetic demo estimate")
    print(json.dumps({"mode": "synthetic demonstration only", "evaluation": result}, indent=2))

if __name__ == "__main__":
    main()
