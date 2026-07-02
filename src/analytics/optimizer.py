"""Modern Portfolio Theory: efficient frontier + max-Sharpe / min-vol via cvxpy.

Long-only, fully invested, per-asset weight cap. Inputs are daily returns in
native quote currencies (FX effects are not modeled in the optimization).
"""
import cvxpy as cp
import numpy as np
import pandas as pd

TRADING_DAYS = 252


def prep_inputs(returns: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    mu = returns.mean() * TRADING_DAYS
    cov = returns.cov() * TRADING_DAYS
    # small ridge keeps short/noisy histories numerically PSD
    cov = cov + np.eye(len(cov)) * 1e-8
    return mu, cov


def _solve_min_var(mu: pd.Series, cov: pd.DataFrame, target: float | None, max_weight: float) -> pd.Series | None:
    n = len(mu)
    w = cp.Variable(n)
    cons = [cp.sum(w) == 1, w >= 0, w <= max_weight]
    if target is not None:
        cons.append(mu.values @ w >= target)
    prob = cp.Problem(cp.Minimize(cp.quad_form(w, cp.psd_wrap(cov.values))), cons)
    try:
        prob.solve()
    except cp.error.SolverError:
        return None
    if w.value is None:
        return None
    return pd.Series(np.clip(w.value, 0, None), index=mu.index).round(6)


def _max_capped_return(mu: pd.Series, max_weight: float) -> float:
    """Best achievable return when every asset is capped at max_weight."""
    remaining, total = 1.0, 0.0
    for m in mu.sort_values(ascending=False):
        take = min(max_weight, remaining)
        total += take * m
        remaining -= take
        if remaining <= 1e-9:
            break
    return total


def portfolio_stats(weights: pd.Series, mu: pd.Series, cov: pd.DataFrame, rf: float) -> dict:
    w = weights.reindex(mu.index).fillna(0.0)
    ret = float(mu @ w)
    vol = float(np.sqrt(max(w @ cov @ w, 0)))
    return {"ret": ret, "vol": vol, "sharpe": (ret - rf) / vol if vol > 0 else np.nan}


def efficient_frontier(returns: pd.DataFrame, rf: float = 0.03, max_weight: float = 0.30, n_points: int = 30):
    """Returns (frontier_df, max_sharpe_weights, min_vol_weights, mu, cov).

    frontier_df columns: ret, vol, sharpe, weights (pd.Series).
    Returns (None, ...) if the problem is infeasible (e.g. cap too low).
    """
    mu, cov = prep_inputs(returns)
    if max_weight * len(mu) < 1.0:  # cannot sum to 100%
        return None, None, None, mu, cov

    min_vol_w = _solve_min_var(mu, cov, None, max_weight)
    if min_vol_w is None:
        return None, None, None, mu, cov

    ret_lo = float(mu @ min_vol_w)
    ret_hi = _max_capped_return(mu, max_weight)
    targets = np.linspace(ret_lo, ret_hi - abs(ret_hi) * 1e-4, n_points)

    rows = []
    for t in targets:
        w = _solve_min_var(mu, cov, float(t), max_weight)
        if w is None:
            continue
        rows.append({**portfolio_stats(w, mu, cov, rf), "weights": w})
    if not rows:
        return None, None, None, mu, cov

    frontier = pd.DataFrame(rows)
    best = frontier.loc[frontier["sharpe"].idxmax()]
    return frontier, best["weights"], min_vol_w, mu, cov
