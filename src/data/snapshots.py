"""Daily account-value snapshots.

Trading212's API has no equity-curve endpoint, so the dashboard records one
row per day whenever it runs — the account history builds up locally in
data/account_history.csv (kept out of git).
"""
import csv
from datetime import date

import pandas as pd

from src import config

HISTORY_FILE = config.DATA_DIR / "account_history.csv"
FIELDS = ["date", "total_czk", "invested_czk", "cash_czk"]


def load() -> pd.DataFrame:
    if not HISTORY_FILE.exists():
        return pd.DataFrame(columns=FIELDS)
    df = pd.read_csv(HISTORY_FILE, parse_dates=["date"])
    return df.sort_values("date")


def record(total_czk: float, invested_czk: float, cash_czk: float) -> None:
    """Upsert today's row — the last run of the day wins."""
    if not total_czk or total_czk != total_czk:
        return
    today = date.today().isoformat()
    rows = []
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE) as fh:
            rows = [r for r in csv.DictReader(fh) if r["date"] != today]
    rows.append(
        {
            "date": today,
            "total_czk": round(total_czk, 2),
            "invested_czk": round(invested_czk, 2),
            "cash_czk": round(cash_czk, 2),
        }
    )
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
