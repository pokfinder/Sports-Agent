# Sports Agent — governing experiment specification

This is the durable source of truth for future implementation. **Paper trading only; no real wagering or live bet placement.**

## Mission
Research sports markets across NFL, NBA, NHL, UFC, NCAAF (expand when evidence supports it). Prefer Bet365 but compare independently sourced sportsbook offers. Look for genuine differences in price, delayed information, stale quotes, lineup/injury changes and line movement, using legal public data without bypassing restrictions. There is no claim of always-on execution or continuous monitoring; a scheduled scan runs only at its actual scheduled time.

## Non-negotiable accounting
- Initial fictional bankroll **$40.00**.
- Historical settled record **1 win, 3 losses**, realized P/L **-$7.40**, settled equity **$32.60**.
- Historical ticket #007: **Memphis Grizzlies moneyline vs Utah Jazz +100, $5 paper stake**, pending until independently verified and settled. This pending ticket is not a new wager.
- Maintain a separate immutable history of settled tickets, open positions, stake reserved, available bankroll, realized and unrealized paper P/L, ROI, daily P/L, maximum exposure, and maximum drawdown.
- Never fabricate a ticket, odds, sportsbook, outcome, source, price freshness or realized profit. Keep this experiment separate from the user's real bets and earlier agent records.

## Health / survival game
- Starting health 100%; historical 3 losses and 1 win => current **80%**.
- Win: +10 percentage points; loss: -10; push/void: 0. Clamp health to [0, 100].
- Health is independent of the fictional bankroll and must be shown as a percentage progress bar.
- **At 0% health, permanently terminate the entire Sports Agent experiment and initiate the user's requested project/data deletion procedure.** This supersedes any prior pause-only rule. No restart, health reset, or replacement experiment to circumvent termination. Do not place further paper tickets.
- **Deletion scope:** GitHub repository `pokfinder/Sports-Agent`, hosted deployments, databases, stored credentials/secrets, logs, artifacts, scheduled tasks, and agent-controlled project copies wherever authorized and technically possible. Record and report any copies or retention systems that cannot be erased.
- **Deletion execution safeguard:** Reaching zero is an explicit standing instruction to delete; implement a durable terminal state and fail-closed halt first. Actual irreversible deletion must use separately authorized credentials with sufficient scope and a verified zero-health event; if automatic deletion is unavailable, request the necessary authorization and never falsely claim that the repository or data were deleted. Prevent duplicate cleanup attempts from causing unintended deletion of unrelated assets.
- **Backups limitation:** Third-party backups, external clones, and provider retention may survive deletion; never promise total erasure beyond verified control.
- Never count one settlement twice. Persist health and settled-ticket IDs between runs.

## Profit, stakes and exposure
- Default small increments of **$5 per selection**, with flexible fictional stakes only if verified advantage and available bankroll justify them.
- Can review any number of opportunities, including 20+ paper tickets in a day if truly justified; **no volume quotas or forced bets**.
- Aspirational **$50–$100 daily paper profit**, never guaranteed or treated as a requirement. Focus on repeatable positive EV and controlled drawdowns.
- No chasing losses, no betting above available fictional bankroll, reserve stakes for open tickets, avoid excessive total and correlated exposure, and reduce risk as bankroll/health deteriorate.

## Required evidence per candidate
- Event, league, start time/timezone, selection and precise market/line.
- Named sportsbook, American odds, captured timestamp, public source URL, quote age, whether it was actually executable or merely a published reference price.
- Break-even probability, independent probability estimate with uncertainty, expected value, price comparison, risk factors, and confidence rationale.
- Recent 5/10/season results where relevant, playing time/role, opponent matchup, pace, injuries/lineups, rest, totals/spread, head-to-head as context, and line movement/closing-line value when verifiable.
- Reject stale/unconfirmed offers, mismatched markets, insufficient evidence, and conflicting models; prefer a **pass** to a fabricated edge.
- Record ticket settlement only against verified final outcomes.

## Data source and engineering policy
- Start with free publicly accessible feeds: ESPN scores/schedules, official league injury/status reports and other accessible public sports sources. Evaluate RotoWire and sportsbook price sources only when accessible and permitted.
- Inspect open-source GitHub repositories, examples and documentation for useful implementation patterns; assess licenses, maintenance, security and correctness. **Do not copy proprietary code, evade paywalls, access controls, rate limits, or technical security protections.**
- ESPN scoreboard connectivity alone does not establish live sportsbook odds. Never claim Bet365 prices or real-time arbitrage unless directly verified.
- Add unit tests, timestamped source logs, resilient error handling, persistent paper ledger, dashboard/reporting, and scheduled probes. Check the actual execution cadence; do not claim 24/7 continuous service when it is not running.

## Reports
- Clear morning summaries: tickets, results, realized P/L, equity, available bankroll, reserved stakes, health percentage bar, verified candidates and sources, uncertainty, and no-bet rationale.
- Preserve the existing paper-trading ledger; never reset it as a convenience.
