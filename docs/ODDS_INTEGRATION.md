# Sports Agent: verified odds integration contract

## Scope

The odds adapter is provider-neutral. It **does not** log in to Bet365, collect account cookies, reverse engineer private authenticated endpoints, scrape protected pages, or place wagers.

Use a provider only when its terms authorize the intended use. A displayed Bet365 price from a third party may not be available to a Virginia account.

## JSON input shape

```json
{
  "provider": "authorized-provider-name",
  "quotes": [
    {
      "event_id": "provider-event-id",
      "market": "moneyline",
      "selection": "Home",
      "sportsbook": "Bet365",
      "american_odds": 150,
      "observed_at": "2026-10-26T12:00:00Z"
    }
  ]
}
```

For spreads, totals, and player props include a numeric `line`. Also ensure event identifiers, participant, period, market and line are mapped consistently across providers before comparing prices. The basic adapter is not a complete event/market identity reconciler.

## Safety checks

- All quotes require source provenance and an explicit timezone-aware observation time.
- Reject stale (older than 180 seconds), future, malformed, and ambiguous-line quotes.
- Do not call an observed quote an executable price.
- Do not create paper tickets from quote discrepancies alone: require independently sourced probability estimates, uncertainty adjustment, and risk checks.
- Never store provider secrets in GitHub, static dashboard files, or browser JavaScript. Configure secrets in a private server-side runtime.
- Existing static Render dashboard is not an authenticated backend. Do not expose personal Bet365 account details there.
- Keep real-account history and paper trading completely separate.
- No paid odds subscription or Bet365 account authorization has been configured yet.
