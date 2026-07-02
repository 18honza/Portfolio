"""Market data via yfinance (free, no API key)."""
import pandas as pd
import yfinance as yf


def download_history(tickers: tuple[str, ...], period: str = "1y") -> pd.DataFrame:
    """Daily close prices, one column per ticker, in each instrument's native quote currency."""
    tickers = tuple(t for t in tickers if t)
    if not tickers:
        return pd.DataFrame()
    raw = yf.download(list(tickers), period=period, auto_adjust=True, progress=False)
    if raw is None or raw.empty:
        return pd.DataFrame()
    close = raw["Close"]
    if isinstance(close, pd.Series):
        close = close.to_frame(tickers[0])
    return close.dropna(how="all")


def quote_currencies(tickers: tuple[str, ...]) -> dict[str, str]:
    """Actual quote currency per Yahoo ticker (GBp vs GBP matters on the LSE).

    Only queried for .L symbols — everywhere else the declared currency is
    reliable and this saves one HTTP call per ticker.
    """
    out: dict[str, str] = {}
    for t in tickers:
        if not t or not t.endswith(".L"):
            continue
        try:
            out[t] = yf.Ticker(t).fast_info["currency"]
        except Exception:
            pass
    return out


def latest_and_daychange(series: pd.Series) -> tuple[float, float]:
    s = series.dropna()
    if s.empty:
        return float("nan"), float("nan")
    last = float(s.iloc[-1])
    if len(s) < 2:
        return last, float("nan")
    return last, (last / float(s.iloc[-2]) - 1.0) * 100.0
