# 📈 Portfolio Command Center

Local, fully free portfolio dashboard for a Trading212 account (CZK base):
Modern Portfolio Theory optimization, efficient frontier, Sharpe/risk analytics,
and live trade signals driven by [Johnny's 3-step research framework](docs/johnnys_research_framework.md).

**Recommendations only.** The dashboard never places orders — you trade manually
in Trading212 and the app just reads the account.

## Stack

Python · Streamlit · pandas · cvxpy · plotly · yfinance (free market data, no API key).

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py
```

Opens at http://localhost:8501.

### Portfolio input — two options

1. **Trading212 API (read-only)** — in the Trading212 app: *Settings → API*,
   generate a key pair with account/portfolio **read** scopes, then:
   ```bash
   cp .env.example .env   # paste both keys: T212_API_KEY and T212_API_SECRET
   ```
   (The API uses HTTP Basic auth — both the key and the secret are required.)
2. **Manual** — use the *Manual portfolio editor* in the sidebar
   (see `data/portfolio.sample.json` for the format; LSE instruments use
   currency `GBX` with prices in pence).

If a Trading212 instrument maps to the wrong Yahoo symbol, add an override in
`data/ticker_map.json`.

## Tabs

| Tab | What it shows |
|-----|---------------|
| 📊 Overview | Account value in CZK, open P/L, day move, Sharpe, max drawdown, allocation, equity curve |
| 📌 Positions & Signals | Position table + Johnny's sell rules evaluated live (hard stops, sell levels, dead money, momentum exhaustion, 200DMA) + per-position trade-plan editor |
| 🎯 Plays & Research | Renders `research/plays.json`: actions on current holdings, next plays with full setups (entry zones, tranches, stops, R:R), watchlist |
| ⚖️ Optimizer | cvxpy efficient frontier, max-Sharpe & min-vol portfolios, rebalance deltas in CZK |
| ⚠️ Risk | VaR/CVaR, beta, Sortino, correlation heatmap, drawdown, currency exposure, concentration |

## Daily research (no paid API needed)

Once a day, open Claude Code in this repo and run:

```
/daily-research
```

Claude applies the framework (catalyst → valuation → sentiment/scenarios → trade
setup), checks every holding against the sell rules, scouts new candidates
(anything tradable on Trading212), rewrites `research/plays.json`, writes a
journal entry, and pushes to GitHub. The dashboard picks it up on next refresh
and warns when research is more than 3 days old.

Prices, P/L and FX auto-refresh every 5 minutes from yfinance regardless of
research runs.

---

*Not financial advice. DYOR.*
