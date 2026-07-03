# Portfolio Command Center

Local Streamlit dashboard for a Trading212 CZK account (~100–110k CZK) combining
MPT optimization (cvxpy), risk analytics, and the swing-trade methodology in
`docs/johnnys_research_framework.md`. **Recommendations only — the user places
every order manually in Trading212.**

## Run

```bash
.venv/bin/streamlit run app.py
```

Prices/FX come from yfinance (free, no key). Optional Trading212 read-only API
key goes in `.env` (see `.env.example`). Personal position files
(`data/portfolio.json`, `data/positions_meta.json`) are gitignored on purpose.

## Daily research workflow

The user prompts Claude once a day (skill: `/daily-research`) instead of using a
paid API. The run does web research per the framework, rewrites
`research/plays.json` + adds `research/journal/YYYY-MM-DD.md`, then commits and
pushes `research/` to GitHub. The dashboard's **Plays & Research** tab renders
`plays.json` directly and shows a staleness warning after 3 days.

## research/plays.json schema

```jsonc
{
  "as_of": "YYYY-MM-DD",
  "generated_by": "claude + date",
  "market_context": "1-3 sentences: tape, rotation, macro this week",
  "position_actions": [
    {
      "ticker": "MU",                      // matches portfolio ticker
      "action": "SELL 50% at 142.0",       // HOLD | SELL x% at market | SELL x% at LEVEL | RAISE STOP to X | SIZE DOWN
      "urgency": "level",                  // now | level | info
      "reason": "why, per framework sell rules"
    }
  ],
  "new_plays": [
    {
      "ticker": "XYZ", "yf_ticker": "XYZ", "name": "Company",
      "type": "swing",                     // swing | earnings | long
      "action": "BUY ON PULLBACK",         // BUY NOW | BUY ON PULLBACK | WATCH
      "entry_zone": [10.5, 11.2],          // native currency
      "tranches": [{"pct": 50, "condition": "at market"}, {"pct": 50, "condition": "pullback to 10.6"}],
      "first_sell": {"price": 13.0, "pct": 40},
      "second_sell": {"price": 14.5},
      "hard_stop": 9.8,
      "catalyst": "Q3 earnings", "catalyst_date": "YYYY-MM-DD",
      "hold_period": "2-6 weeks", "risk_reward": "1:2.6",
      "checklist_score": "5/6",
      "suggested_size_czk": 15000,
      "thesis": "...", "risks": "..."
    }
  ],
  "watchlist": [
    {"ticker": "ABC", "yf_ticker": "ABC", "note": "why it is interesting", "trigger": "what would make it a play"}
  ]
}
```

`data/positions_meta.json` (written by the dashboard UI) holds per-ticker trade
plans: `hard_stop`, `sell1`, `sell1_pct`, `sell2`, `catalyst`, `catalyst_date`,
`type`, `thesis` — levels in the instrument's native currency.

## Conventions

- After every research update: commit and push (`research: YYYY-MM-DD daily update`).
- Code changes: normal commits, push to `main` on https://github.com/18honza/Portfolio.git.
- New play candidates must be tradable on Trading212 (any market is fine).
- Position sizes are suggested in CZK; never exceed ~20% of account per name.
- Never automate order placement anywhere in this project.
- Posture: user wants ~85–90% invested by default (small cash buffer for new
  plays); defensive cash only during active risk-off tapes, and every exit or
  cancel recommendation must ship with a re-entry trigger (see the
  daily-research skill).
