"""Download dated NBA finals and produce a research-only backtest report.

Example: python -m scripts.backtest_nba --start 2025-10-21 --end 2025-12-19
"""
import argparse
import json
from pathlib import Path
from sports_agent.nba_history import fetch_historical_games
from sports_agent.nba_backtest import backtest_elo
from sports_agent.nba_probability_calibration import separated_calibration

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--start",required=True)
    parser.add_argument("--end",required=True)
    parser.add_argument("--minimum-training",type=int,default=100)
    parser.add_argument("--minimum-evaluation",type=int,default=100)
    parser.add_argument("--output",default="data/nba_backtest_report.json")
    args=parser.parse_args()
    games=fetch_historical_games(args.start,args.end)
    result=backtest_elo(games,minimum_training_games=args.minimum_training,
                        min_evaluation_games=args.minimum_evaluation, return_predictions=True)
    predictions=result.pop("predictions")
    result["separated_calibration"]=separated_calibration(predictions,min_holdout=args.minimum_evaluation)
    result.update({"source":"ESPN public scoreboard (unofficial)",
                   "start_date":args.start,"end_date":args.end,
                   "historical_games":len(games),
                   "completion_timestamps":"conservative six-hour proxies, not actual completion times"})
    path=Path(args.output)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2,sort_keys=True)+"
")
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
