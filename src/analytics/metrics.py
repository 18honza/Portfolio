"""Classic portfolio statistics (all annualized off daily closes)."""
import numpy as np
import pandas as pd

TRADING_DAYS = 252


def daily_returns(prices: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    return prices.ffill().pct_change().dropna(how="all")


def annualized_return(returns: pd.Series) -> float:
    r = returns.dropna()
    if r.empty:
        return np.nan
    return float((1 + r).prod() ** (TRADING_DAYS / len(r)) - 1)


def annualized_vol(returns: pd.Series) -> float:
    r = returns.dropna()
    if len(r) < 2:
        return np.nan
    return float(r.std() * np.sqrt(TRADING_DAYS))


def sharpe(returns: pd.Series, rf: float = 0.0) -> float:
    vol = annualized_vol(returns)
    if not vol or np.isnan(vol):
        return np.nan
    return (annualized_return(returns) - rf) / vol


def sortino(returns: pd.Series, rf: float = 0.0) -> float:
    r = returns.dropna()
    downside = r[r < 0]
    if len(downside) < 2:
        return np.nan
    dvol = float(downside.std() * np.sqrt(TRADING_DAYS))
    if not dvol:
        return np.nan
    return (annualized_return(r) - rf) / dvol


def drawdown_series(returns: pd.Series) -> pd.Series:
    cum = (1 + returns.dropna()).cumprod()
    return cum / cum.cummax() - 1


def max_drawdown(returns: pd.Series) -> float:
    dd = drawdown_series(returns)
    return float(dd.min()) if not dd.empty else np.nan


def var_cvar(returns: pd.Series, level: float = 0.95) -> tuple[float, float]:
    """Historical 1-day VaR and CVaR as positive fractions (e.g. 0.021 = 2.1%)."""
    r = returns.dropna()
    if len(r) < 20:
        return np.nan, np.nan
    var = -np.percentile(r, (1 - level) * 100)
    tail = r[r <= -var]
    cvar = -float(tail.mean()) if len(tail) else np.nan
    return float(var), cvar


def beta(asset_returns: pd.Series, bench_returns: pd.Series) -> float:
    df = pd.concat([asset_returns, bench_returns], axis=1).dropna()
    if len(df) < 20:
        return np.nan
    cov = np.cov(df.iloc[:, 0], df.iloc[:, 1])
    if cov[1, 1] == 0:
        return np.nan
    return float(cov[0, 1] / cov[1, 1])


def herfindahl(weights: pd.Series) -> float:
    """Concentration index: 1/n (equal weight) .. 1.0 (single position)."""
    w = weights.dropna() / 100.0
    return float((w**2).sum())
