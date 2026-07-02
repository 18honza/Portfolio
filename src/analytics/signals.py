"""Johnny's framework sell rules turned into a live rule engine.

Evaluates each held position against its trade plan (data/positions_meta.json)
and price history, and emits actionable flags. Recommendations only — the
user always places orders manually.
"""
from datetime import date, datetime

import pandas as pd

SEV_ORDER = {"critical": 0, "action": 1, "warning": 2, "info": 3}


def parse_date(value) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def evaluate_position(
    ticker: str,
    price: float | None,
    meta: dict,
    history: pd.Series | None = None,
    today: date | None = None,
) -> list[dict]:
    """`price`/levels are in the instrument's native currency (GBX already scaled)."""
    today = today or date.today()
    flags: list[dict] = []

    def add(severity: str, action: str, why: str) -> None:
        flags.append({"ticker": ticker, "severity": severity, "action": action, "why": why})

    stop = meta.get("hard_stop") or None
    sell1 = meta.get("sell1") or None
    sell2 = meta.get("sell2") or None
    sell1_pct = int(meta.get("sell1_pct") or 40)
    catalyst_date = parse_date(meta.get("catalyst_date"))
    has_price = price is not None and price == price  # not NaN

    if not stop:
        add(
            "warning",
            "SET A HARD STOP",
            'No hard stop defined. "If you do not know the price at which you are '
            'wrong, you do not have a trade — you have a hope."',
        )

    if has_price and stop and price <= float(stop):
        add(
            "critical",
            "SELL 100% at market",
            f"Hard stop {stop:g} breached (last {price:g}). Framework: sell everything, "
            "no exceptions — do not lower the stop, do not give it more room.",
        )
    elif has_price and sell2 and price >= float(sell2):
        add(
            "action",
            "SELL remaining position",
            f"Second sell level {sell2:g} hit — close the position into strength.",
        )
    elif has_price and sell1 and price >= float(sell1):
        add(
            "action",
            f"SELL {sell1_pct}% of position",
            f"First sell level {sell1:g} hit — take partial profit, let the rest run.",
        )

    if catalyst_date:
        dte = (catalyst_date - today).days
        if 0 <= dte <= 3 and meta.get("type") != "earnings":
            add(
                "warning",
                "SIZE DOWN to ~50% before the event",
                f"Catalyst '{meta.get('catalyst', 'event')}' in {dte} day(s) — binary "
                "risk rule: holding full size into a binary event is not allowed.",
            )

    if history is not None:
        h = history.dropna()
        if has_price and len(h) >= 22:
            chg30 = price / float(h.iloc[-22]) - 1
            if chg30 >= 0.40:
                add(
                    "warning",
                    "Consider trimming into strength",
                    f"Up {chg30:.0%} over the last month — momentum-exhaustion red flag. "
                    "Do not add here; tighten the stop or take partials.",
                )
        if has_price and len(h) >= 16:
            chg3w = price / float(h.iloc[-16]) - 1
            no_catalyst = (
                catalyst_date is None
                or catalyst_date < today
                or (catalyst_date - today).days > 45
            )
            if abs(chg3w) < 0.03 and no_catalyst:
                add(
                    "warning",
                    "Reassess or cut — dead money",
                    "Flat for 3+ weeks with no upcoming catalyst. Framework: cut and "
                    "redeploy into a setup with a timer.",
                )
        if has_price and len(h) >= 200:
            ma200 = float(h.rolling(200).mean().iloc[-1])
            if price < ma200:
                add(
                    "warning",
                    "Below 200-day MA — downtrend check",
                    f"Last {price:g} < 200DMA {ma200:g}. Make sure this is a dip in an "
                    "uptrend, not a structural downtrend.",
                )

    if not any(f["severity"] in ("critical", "action") for f in flags):
        add("info", "HOLD", "No sell rules triggered — thesis intact by the framework.")

    flags.sort(key=lambda f: SEV_ORDER[f["severity"]])
    return flags
