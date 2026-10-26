"""Run: python -m scripts.probe_sources"""
import json
from datetime import datetime, timezone
from sports_agent.sources import LEAGUES, probe_espn

def main():
    print(json.dumps({"tested_at": datetime.now(timezone.utc).isoformat(),
                      "sources": [probe_espn(league) for league in LEAGUES]},
                     indent=2))

if __name__ == "__main__":
    main()
