"""Paper-only bankroll and health bookkeeping. No wager execution."""
from dataclasses import dataclass, field

@dataclass
class PaperLedger:
    starting_bankroll: float = 40.0
    health: int = 80
    realized_profit: float = -7.40
    record_wins: int = 1
    record_losses: int = 3
    entries: list[dict] = field(default_factory=list)

    @property
    def equity(self) -> float:
        return round(self.starting_bankroll + self.realized_profit, 2)

    def settle(self, ticket_id: str, stake: float, american_odds: int, result: str) -> dict:
        if result not in ("win", "loss", "push"):
            raise ValueError("Result must be win, loss, or push")
        if stake <= 0 or american_odds == 0:
            raise ValueError("Invalid stake or odds")
        if self.health == 0:
            raise ValueError("Experiment terminated at 0% health")
        if any(x["ticket_id"] == ticket_id for x in self.entries):
            raise ValueError("Ticket already settled")
        if result == "win":
            profit = stake * (american_odds / 100 if american_odds > 0 else 100 / -american_odds)
            self.health = min(100, self.health + 10)
            self.record_wins += 1
        elif result == "loss":
            profit = -stake
            self.health = max(0, self.health - 10)
            self.record_losses += 1
        else:
            profit = 0
        self.realized_profit = round(self.realized_profit + profit, 2)
        entry = {"ticket_id": ticket_id, "stake": stake, "american_odds": american_odds,
                 "result": result, "profit": round(profit, 2), "health_after": self.health}
        self.entries.append(entry)
        return entry
