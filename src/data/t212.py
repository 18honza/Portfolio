"""Read-only Trading212 client (public API).

Docs: https://docs.trading212.com/api
Auth: HTTP Basic — API key as username, API secret as password.
Never places orders — this app only reads positions and cash.
"""
import json
import time

import requests

from src import config
from src.data.store import load_ticker_map

_INSTRUMENTS_CACHE = config.CACHE_DIR / "t212_instruments.json"
_INSTRUMENTS_TTL = 7 * 24 * 3600  # instrument list changes rarely

# Trading212 ticker suffix letter -> Yahoo Finance exchange suffix (best effort;
# anything odd can be fixed in data/ticker_map.json which always wins).
_EXCHANGE_SUFFIX = {
    "l": ".L",   # London
    "d": ".DE",  # Xetra / Deutsche Boerse
    "a": ".AS",  # Euronext Amsterdam
    "p": ".PA",  # Euronext Paris
    "b": ".BR",  # Euronext Brussels
    "m": ".MC",  # Bolsa de Madrid
    "z": ".SW",  # SIX Swiss
    "v": ".VI",  # Vienna
    "h": ".HE",  # Helsinki
    "s": ".ST",  # Stockholm
    "o": ".OL",  # Oslo
    "c": ".CO",  # Copenhagen
}

_CURRENCY_SUFFIX = {"GBX": ".L", "GBP": ".L", "CHF": ".SW", "PLN": ".WA", "CZK": ".PR"}


class T212Error(RuntimeError):
    pass


def _auth() -> tuple[str, str]:
    if not config.T212_API_KEY or not config.T212_API_SECRET:
        raise T212Error(
            "T212_API_KEY / T212_API_SECRET is not set. Put both keys from the "
            "Trading212 app (Settings -> API) into .env, or use Manual mode."
        )
    return (config.T212_API_KEY, config.T212_API_SECRET)


def _get(path: str, retry_429: bool = True):
    resp = requests.get(f"{config.T212_BASE_URL}{path}", auth=_auth(), timeout=30)
    if resp.status_code == 429:
        if retry_429:
            time.sleep(3)
            return _get(path, retry_429=False)
        raise T212Error("Trading212 rate limit hit — wait ~30s and press Refresh.")
    if resp.status_code in (401, 403):
        raise T212Error(
            "Trading212 rejected the credentials (401/403). Check both T212_API_KEY "
            "and T212_API_SECRET in .env and that the key has read scopes."
        )
    resp.raise_for_status()
    return resp.json()


def fetch_summary() -> dict:
    """Account summary: cash, investments value, currency, total value."""
    return _get("/equity/account/summary")


def free_cash(summary: dict) -> float:
    """All uninvested cash: free + reserved for pending orders + sitting in pies."""
    cash = summary.get("cash", summary)
    if isinstance(cash, dict):
        return float(
            (cash.get("availableToTrade") or cash.get("free") or 0.0)
            + (cash.get("reservedForOrders") or 0.0)
            + (cash.get("inPies") or 0.0)
        )
    if isinstance(cash, (int, float)):
        return float(cash)
    return 0.0


def fetch_instruments() -> list[dict]:
    if _INSTRUMENTS_CACHE.exists() and time.time() - _INSTRUMENTS_CACHE.stat().st_mtime < _INSTRUMENTS_TTL:
        return json.loads(_INSTRUMENTS_CACHE.read_text())
    data = _get("/equity/metadata/instruments")
    _INSTRUMENTS_CACHE.parent.mkdir(parents=True, exist_ok=True)
    _INSTRUMENTS_CACHE.write_text(json.dumps(data))
    return data


def yf_ticker_for(t212_ticker: str, short_name: str, currency: str) -> str | None:
    """Map a Trading212 instrument to its Yahoo Finance symbol."""
    overrides = load_ticker_map()
    if t212_ticker in overrides:
        return overrides[t212_ticker]
    if short_name in overrides:
        return overrides[short_name]
    if t212_ticker.endswith("_US_EQ"):
        return short_name.replace(".", "-")  # BRK.B -> BRK-B
    base = t212_ticker.split("_")[0]
    if base and base[-1].islower():
        suffix = _EXCHANGE_SUFFIX.get(base[-1])
        if suffix:
            return base[:-1] + suffix
    suffix = _CURRENCY_SUFFIX.get(currency)
    if suffix:
        return (short_name or base) + suffix
    return short_name or None


def _first(d: dict, *keys, default=None):
    for k in keys:
        if d.get(k) is not None:
            return d[k]
    return default


def fetch_positions() -> list[dict]:
    """Open positions normalized to the app's unified shape.

    The positions payload nests instrument info and a walletImpact block with
    values already converted to the account currency (CZK).
    """
    positions = []
    for p in _get("/equity/positions"):
        inst = p.get("instrument") or {}
        t212_ticker = str(inst.get("ticker") or _first(p, "ticker", default=""))
        base = t212_ticker.split("_")[0]
        short = base[:-1] if len(base) > 1 and base[-1].islower() else base
        currency = _first(inst, "currency", "currencyCode", default="USD")
        wallet = p.get("walletImpact") or {}
        positions.append(
            {
                "ticker": short,
                "t212_ticker": t212_ticker,
                "yf_ticker": yf_ticker_for(t212_ticker, short, currency),
                "name": inst.get("name", short),
                "shares": float(_first(p, "quantity", "shares", default=0.0)),
                "avg_price": float(_first(p, "averagePricePaid", "averagePrice", default=0.0)),
                "currency": currency,
                "t212_price": _first(p, "currentPrice", "price"),
                "t212_ppl_czk": _first(wallet, "unrealizedProfitLoss", default=p.get("ppl")),
                "t212_value_czk": wallet.get("currentValue"),
            }
        )
    return positions
