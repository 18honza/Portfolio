"""Read-only Trading212 client (public API beta).

Docs: https://t212public-api-docs.redoc.ly/
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


def _headers() -> dict:
    if not config.T212_API_KEY:
        raise T212Error(
            "T212_API_KEY is not set. Copy .env.example to .env, paste your key "
            "(Trading212 app -> Settings -> API), or switch to Manual mode."
        )
    return {"Authorization": config.T212_API_KEY}


def _get(path: str):
    resp = requests.get(f"{config.T212_BASE_URL}{path}", headers=_headers(), timeout=30)
    if resp.status_code == 429:
        raise T212Error("Trading212 rate limit hit — wait ~30s and press Refresh.")
    if resp.status_code in (401, 403):
        raise T212Error(
            "Trading212 rejected the API key (401/403). Check the key in .env and "
            "that it has account + portfolio read scopes."
        )
    resp.raise_for_status()
    return resp.json()


def fetch_cash() -> dict:
    """Account cash in the account currency (CZK): free, invested, total, ppl..."""
    return _get("/equity/account/cash")


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


def fetch_positions() -> list[dict]:
    """Open positions normalized to the app's unified shape."""
    instruments = {i["ticker"]: i for i in fetch_instruments()}
    positions = []
    for p in _get("/equity/portfolio"):
        info = instruments.get(p["ticker"], {})
        short = info.get("shortName") or p["ticker"].split("_")[0]
        currency = info.get("currencyCode", "USD")
        positions.append(
            {
                "ticker": short,
                "t212_ticker": p["ticker"],
                "yf_ticker": yf_ticker_for(p["ticker"], short, currency),
                "name": info.get("name", short),
                "shares": float(p["quantity"]),
                "avg_price": float(p.get("averagePrice") or 0.0),
                "currency": currency,
                "t212_price": p.get("currentPrice"),
                "t212_ppl_czk": p.get("ppl"),  # P/L already in account currency
            }
        )
    return positions
