# Sports Agent

Free-source sports data validation and **paper-only** market analysis. No paid API keys and no real wagering.

## First milestone
- Probe ESPN's unofficial public scoreboard feeds for NBA, NFL, NHL, MLB.
- Normalize American odds and compare independently timestamped quotes.
- Reject stale comparisons and **never confuse best price with demonstrated edge**.
- Preserve paper-trading bookkeeping: initial $40, settled 1–3, net -$7.40, health 80%; #007 Memphis ML +100 $5 remains pending until verified.
- GitHub Actions runs a source probe every six hours (subject to GitHub scheduling and usage limits). The scheduled job prints diagnostics; it does **not** make bets or claim real-time coverage.

## Run
```bash
pip install -r requirements.txt
pytest -q
python -m scripts.probe_sources
```

## Important limitations
ESPN's feed is unofficial and does not establish executable sportsbook odds. This repository does not yet have a reliable multi-book odds feed or a verified positive expected-value model. No scraping of restricted pages or bypassing access controls. Before considering paper tickets, verify the quoted sportsbook price, market, timestamp, fair probability, and freshness.
