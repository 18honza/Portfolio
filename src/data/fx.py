"""FX conversion to the account currency (CZK) via Yahoo Finance pairs."""
import numpy as np
import pandas as pd
import yfinance as yf


def normalize_currency(currency: str) -> str:
    """LSE stocks quote in pence (GBX/GBp) — treat them as GBP after a /100 scale."""
    if currency in ("GBX", "GBp", "GBp."):
        return "GBP"
    return currency or "USD"


def price_scale(currency: str) -> float:
    return 0.01 if currency in ("GBX", "GBp", "GBp.") else 1.0


def get_rates(currencies: tuple[str, ...], target: str = "CZK") -> dict[str, float]:
    """Latest spot rate per currency into `target`. Target itself maps to 1.0."""
    rates: dict[str, float] = {target: 1.0}
    need = sorted({normalize_currency(c) for c in currencies} - {target})
    if not need:
        return rates
    pairs = {c: f"{c}{target}=X" for c in need}
    data = yf.download(list(pairs.values()), period="5d", auto_adjust=True, progress=False)
    if data is None or data.empty:
        return {**rates, **{c: np.nan for c in need}}
    close = data["Close"]
    if isinstance(close, pd.Series):
        close = close.to_frame(list(pairs.values())[0])
    close = close.ffill()
    for cur, pair in pairs.items():
        if pair in close.columns and not close[pair].dropna().empty:
            rates[cur] = float(close[pair].dropna().iloc[-1])
        else:
            rates[cur] = np.nan
    return rates
