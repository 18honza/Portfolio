"""Portfolio Command Center — local Streamlit dashboard.

MPT optimization (cvxpy), risk analytics, and Johnny's 3-step framework
signals over a Trading212 (or manual) portfolio. Recommendations only —
all orders are placed manually by the user.
"""
from datetime import date, datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src import config
from src.analytics import metrics, optimizer, signals
from src.data import fx, prices, store, t212

st.set_page_config(page_title="Portfolio Command Center", page_icon="📈", layout="wide")

CZK = config.ACCOUNT_CURRENCY


def czk(x: float) -> str:
    return "—" if x is None or x != x else f"{x:,.0f} {CZK}"


def pct(x: float, digits: int = 1) -> str:
    return "—" if x is None or x != x else f"{x:+.{digits}f}%"


# ---------------------------------------------------------------- cached IO
@st.cache_data(ttl=config.PRICE_CACHE_TTL, show_spinner="Downloading prices…")
def load_history(tickers: tuple, period: str) -> pd.DataFrame:
    return prices.download_history(tickers, period)


@st.cache_data(ttl=config.PRICE_CACHE_TTL, show_spinner=False)
def load_fx_rates(currencies: tuple) -> dict:
    return fx.get_rates(currencies, CZK)


@st.cache_data(ttl=24 * 3600, show_spinner=False)
def load_quote_currencies(tickers: tuple) -> dict:
    return prices.quote_currencies(tickers)


@st.cache_data(ttl=120, show_spinner="Reading Trading212 account…")
def load_t212() -> tuple[list, dict]:
    return t212.fetch_positions(), t212.fetch_summary()


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.title("📈 Command Center")
    default_source = 1 if config.T212_API_KEY else 0
    source = st.radio("Portfolio source", ["Manual", "Trading212 API"], index=default_source)
    period = st.selectbox("History window", ["6mo", "1y", "2y"], index=1)
    rf = st.number_input("Risk-free rate (%)", 0.0, 15.0, config.DEFAULT_RISK_FREE * 100, 0.25) / 100
    benchmark = st.text_input("Benchmark ticker", config.DEFAULT_BENCHMARK).strip().upper()
    if st.button("🔄 Force refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.caption(
        f"Prices auto-refresh every {config.PRICE_CACHE_TTL // 60} min · "
        f"account currency {CZK} · recommendations only, you place all orders."
    )

# ---------------------------------------------------------------- load portfolio
positions: list[dict] = []
cash_czk = 0.0
t212_error = None

if source == "Trading212 API":
    try:
        positions, summary = load_t212()
        cash_czk = t212.free_cash(summary)
    except Exception as exc:  # T212Error, network, etc.
        t212_error = str(exc)
else:
    manual = store.load_manual_portfolio()
    positions = manual.get("positions", [])
    cash_czk = float(manual.get("cash_czk") or 0.0)

if t212_error:
    st.error(f"Trading212: {t212_error}")

# Manual portfolio editor (always available so you can prep it even in API mode)
with st.sidebar.expander("✏️ Manual portfolio editor"):
    manual = store.load_manual_portfolio()
    editor_df = pd.DataFrame(
        manual.get("positions", []),
        columns=["ticker", "yf_ticker", "shares", "avg_price", "currency"],
    )
    edited = st.data_editor(
        editor_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "ticker": st.column_config.TextColumn("Ticker", required=True),
            "yf_ticker": st.column_config.TextColumn("Yahoo ticker", help="Only if different, e.g. VUSA.L"),
            "shares": st.column_config.NumberColumn("Shares", min_value=0.0, format="%.4f"),
            "avg_price": st.column_config.NumberColumn("Avg price", min_value=0.0),
            "currency": st.column_config.TextColumn("CCY", help="USD, EUR, GBX (pence!), CZK…"),
        },
    )
    cash_input = st.number_input(f"Cash ({CZK})", min_value=0.0, value=float(manual.get("cash_czk") or 0.0), step=1000.0)
    if st.button("💾 Save manual portfolio"):
        rows = edited.dropna(subset=["ticker"]).to_dict("records")
        for r in rows:
            r["ticker"] = str(r["ticker"]).strip().upper()
            r["yf_ticker"] = str(r.get("yf_ticker") or "").strip().upper() or None
            r["currency"] = str(r.get("currency") or "USD").strip().upper()
            r["shares"] = float(r.get("shares") or 0)
            r["avg_price"] = float(r.get("avg_price") or 0)
        store.save_manual_portfolio({"cash_czk": cash_input, "positions": rows})
        st.success("Saved.")
        st.rerun()

# ---------------------------------------------------------------- enrichment
plays = store.load_plays()
meta_all = store.load_meta()

yf_tickers = tuple(sorted({(p.get("yf_ticker") or p["ticker"]) for p in positions}))
hist = load_history(yf_tickers, period) if yf_tickers else pd.DataFrame()
rates = load_fx_rates(tuple(sorted({p.get("currency", "USD") for p in positions}))) if positions else {CZK: 1.0}
quote_ccys = load_quote_currencies(yf_tickers) if yf_tickers else {}

rows, missing_data = [], []
value_parts = {}
for p in positions:
    yft = p.get("yf_ticker") or p["ticker"]
    ccy_raw = p.get("currency", "USD")
    # Yahoo's quote currency decides how the *market price* is scaled (LSE can be
    # GBp or GBP); the declared currency decides how the *avg buy price* is read.
    scale = fx.price_scale(quote_ccys.get(yft, ccy_raw))
    rate = rates.get(fx.normalize_currency(ccy_raw), np.nan)
    series = hist[yft].dropna() * scale if yft in hist.columns else pd.Series(dtype=float)

    declared_scale = fx.price_scale(ccy_raw)
    if series.empty:
        missing_data.append(yft)
        price = float(p["t212_price"]) * declared_scale if p.get("t212_price") else np.nan
        day_chg = np.nan
    else:
        price, day_chg = prices.latest_and_daychange(series)

    shares = float(p.get("shares") or 0)
    avg = float(p.get("avg_price") or 0) * declared_scale
    value = shares * price * rate
    pnl = p["t212_ppl_czk"] if p.get("t212_ppl_czk") is not None else (value - shares * avg * rate)
    if not series.empty:
        value_parts[yft] = series * shares * rate

    rows.append(
        {
            "Ticker": p["ticker"],
            "yf": yft,
            "Name": p.get("name", p["ticker"]),
            "Shares": shares,
            "Avg": avg,
            "Price": price,
            "CCY": fx.normalize_currency(ccy_raw),
            "Day %": day_chg,
            f"Value {CZK}": value,
            f"P/L {CZK}": pnl,
            "P/L %": (price / avg - 1) * 100 if avg else np.nan,
        }
    )

df = pd.DataFrame(rows)
invested_czk = float(df[f"Value {CZK}"].sum()) if not df.empty else 0.0
total_czk = invested_czk + cash_czk
if not df.empty and invested_czk:
    df["Weight %"] = df[f"Value {CZK}"] / invested_czk * 100

value_series = (
    pd.concat(value_parts.values(), axis=1).ffill().dropna().sum(axis=1)
    if value_parts
    else pd.Series(dtype=float)
)
port_returns = metrics.daily_returns(value_series) if len(value_series) > 2 else pd.Series(dtype=float)

bench_hist = load_history((benchmark,), period) if benchmark else pd.DataFrame()
bench_returns = (
    metrics.daily_returns(bench_hist[benchmark]) if benchmark in bench_hist.columns else pd.Series(dtype=float)
)

# ---------------------------------------------------------------- header
as_of = plays.get("as_of")
research_age = (date.today() - signals.parse_date(as_of)).days if signals.parse_date(as_of) else None
h1, h2 = st.columns([3, 1])
with h1:
    st.title("Portfolio Command Center")
with h2:
    if research_age is None:
        st.warning("No research yet — run `/daily-research`")
    elif research_age > 3:
        st.warning(f"Research is {research_age}d old — run `/daily-research`")
    else:
        st.success(f"Research as of {as_of}")

if missing_data:
    st.warning(
        f"No Yahoo price data for: {', '.join(missing_data)}. "
        "Fix the mapping in data/ticker_map.json or set the Yahoo ticker in the editor."
    )

tab_overview, tab_positions, tab_plays, tab_opt, tab_risk = st.tabs(
    ["📊 Overview", "📌 Positions & Signals", "🎯 Plays & Research", "⚖️ Optimizer", "⚠️ Risk"]
)

# ---------------------------------------------------------------- OVERVIEW
with tab_overview:
    if df.empty:
        st.info(
            "No positions yet. Add them in the **Manual portfolio editor** (sidebar) "
            "or set your Trading212 API key in `.env` and switch the source."
        )
    else:
        day_pnl_pct = (
            float((df["Day %"] * df[f"Value {CZK}"]).sum() / invested_czk) if invested_czk else np.nan
        )
        c = st.columns(6)
        c[0].metric("Account value", czk(total_czk))
        c[1].metric("Invested", czk(invested_czk), f"cash {czk(cash_czk)}")
        c[2].metric("Open P/L", czk(float(df[f'P/L {CZK}'].sum())))
        c[3].metric("Day", pct(day_pnl_pct, 2))
        c[4].metric("Sharpe", f"{metrics.sharpe(port_returns, rf):.2f}" if len(port_returns) > 20 else "—")
        c[5].metric("Max DD", pct(metrics.max_drawdown(port_returns) * 100) if len(port_returns) > 20 else "—")

        left, right = st.columns([1, 2])
        with left:
            pie = px.pie(df, values=f"Value {CZK}", names="Ticker", hole=0.45, title="Allocation")
            pie.update_layout(margin=dict(t=40, b=0, l=0, r=0), height=350)
            st.plotly_chart(pie, use_container_width=True)
        with right:
            if len(value_series) > 2:
                curve = go.Figure()
                curve.add_trace(
                    go.Scatter(x=value_series.index, y=value_series.values, fill="tozeroy", name="Portfolio")
                )
                curve.update_layout(
                    title=f"Portfolio value ({CZK}, current FX, current share counts)",
                    height=350,
                    margin=dict(t=40, b=0, l=0, r=0),
                    yaxis_title=CZK,
                )
                st.plotly_chart(curve, use_container_width=True)

        bar = px.bar(
            df.sort_values(f"P/L {CZK}"),
            x=f"P/L {CZK}",
            y="Ticker",
            orientation="h",
            color=f"P/L {CZK}",
            color_continuous_scale=["#e45756", "#888888", "#54a24b"],
            title="Open P/L by position",
        )
        bar.update_layout(height=max(250, 40 * len(df)), coloraxis_showscale=False, margin=dict(t=40, b=0))
        st.plotly_chart(bar, use_container_width=True)

# ---------------------------------------------------------------- POSITIONS & SIGNALS
with tab_positions:
    if df.empty:
        st.info("No positions to evaluate.")
    else:
        show = df[
            ["Ticker", "Name", "Shares", "Avg", "Price", "CCY", "Day %", f"Value {CZK}", f"P/L {CZK}", "P/L %", "Weight %"]
        ]
        st.dataframe(
            show,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Day %": st.column_config.NumberColumn(format="%+.2f%%"),
                "P/L %": st.column_config.NumberColumn(format="%+.1f%%"),
                "Weight %": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=100),
                f"Value {CZK}": st.column_config.NumberColumn(format="%.0f"),
                f"P/L {CZK}": st.column_config.NumberColumn(format="%+.0f"),
            },
        )

        st.subheader("Framework signals")
        st.caption("Johnny's sell rules applied live to every position. Orders are always yours to place.")
        for _, row in df.iterrows():
            tick = row["Ticker"]
            meta = meta_all.get(tick, {})
            series = (
                hist[row["yf"]].dropna() * fx.price_scale(quote_ccys.get(row["yf"], row["CCY"]))
                if row["yf"] in hist.columns
                else None
            )
            flags = signals.evaluate_position(tick, row["Price"], meta, series)
            worst = flags[0]["severity"]
            icon = {"critical": "🔴", "action": "🟠", "warning": "🟡", "info": "🟢"}[worst]
            with st.expander(f"{icon} {tick} — {flags[0]['action']}", expanded=worst in ("critical", "action")):
                for f in flags:
                    render = {"critical": st.error, "action": st.warning, "warning": st.warning, "info": st.success}[
                        f["severity"]
                    ]
                    render(f"**{f['action']}** — {f['why']}")

                st.markdown("**Trade plan** (native currency levels)")
                p1, p2, p3, p4 = st.columns(4)
                new_meta = {
                    "type": p1.selectbox(
                        "Type",
                        ["swing", "earnings", "long"],
                        index=["swing", "earnings", "long"].index(meta.get("type", "swing")),
                        key=f"type_{tick}",
                    ),
                    "hard_stop": p2.number_input("Hard stop", value=float(meta.get("hard_stop") or 0.0), key=f"stop_{tick}"),
                    "sell1": p3.number_input("Sell level 1", value=float(meta.get("sell1") or 0.0), key=f"s1_{tick}"),
                    "sell2": p4.number_input("Sell level 2", value=float(meta.get("sell2") or 0.0), key=f"s2_{tick}"),
                }
                p5, p6, p7 = st.columns([1, 1, 2])
                new_meta["sell1_pct"] = p5.number_input(
                    "Sell 1 size (%)", 10, 90, int(meta.get("sell1_pct") or 40), 5, key=f"s1p_{tick}"
                )
                new_meta["catalyst_date"] = str(
                    p6.date_input(
                        "Catalyst date",
                        value=signals.parse_date(meta.get("catalyst_date")),
                        key=f"cd_{tick}",
                    )
                    or ""
                )
                new_meta["catalyst"] = p7.text_input("Catalyst", value=meta.get("catalyst", ""), key=f"cat_{tick}")
                new_meta["thesis"] = st.text_area("Thesis", value=meta.get("thesis", ""), key=f"th_{tick}", height=70)
                if st.button("💾 Save plan", key=f"save_{tick}"):
                    meta_all[tick] = {k: (v or None) for k, v in new_meta.items()}
                    store.save_meta(meta_all)
                    st.success("Plan saved.")
                    st.rerun()

# ---------------------------------------------------------------- PLAYS & RESEARCH
with tab_plays:
    if not plays or not plays.get("as_of"):
        st.info(
            "No research run yet. Open Claude Code in this repo and run **/daily-research** — "
            "it applies Johnny's 3-step framework (catalysts, valuation, sentiment, scenarios), "
            "updates `research/plays.json` and pushes it to GitHub. This tab renders that file."
        )
    else:
        st.caption(f"Research as of **{plays['as_of']}** · generated by {plays.get('generated_by', '?')}")
        if plays.get("market_context"):
            st.markdown(f"> {plays['market_context']}")

        actions = plays.get("position_actions", [])
        st.subheader("Actions on current positions")
        if actions:
            for a in actions:
                sev = a.get("urgency", "info")
                render = {"now": st.error, "level": st.warning, "info": st.info}.get(sev, st.info)
                render(f"**{a.get('ticker')} — {a.get('action')}**: {a.get('reason', '')}")
        else:
            st.success("No sell/trim actions recommended — holdings intact.")

        st.subheader("Next plays")
        new_plays = plays.get("new_plays", [])
        if not new_plays:
            st.info("No new plays passed the 4/6 signal-quality checklist in the last run.")
        for play in new_plays:
            with st.container(border=True):
                head = f"**{play.get('ticker')}** · {play.get('name', '')} — " f"`{play.get('action', 'WATCH')}`"
                st.markdown(head)
                zone = play.get("entry_zone") or ["?", "?"]
                cc = st.columns(6)
                cc[0].metric("Entry zone", f"{zone[0]}–{zone[1]}")
                cc[1].metric("Sell 1", f"{play.get('first_sell', {}).get('price', '—')} ({play.get('first_sell', {}).get('pct', '—')}%)")
                cc[2].metric("Sell 2", str(play.get("second_sell", {}).get("price", "—")))
                cc[3].metric("Hard stop", str(play.get("hard_stop", "—")))
                cc[4].metric("R:R", play.get("risk_reward", "—"))
                cc[5].metric("Size", czk(play.get("suggested_size_czk")))
                st.markdown(
                    f"**Catalyst:** {play.get('catalyst', '—')} ({play.get('catalyst_date', 'no date')}) · "
                    f"**Hold:** {play.get('hold_period', '—')} · **Type:** {play.get('type', 'swing')} · "
                    f"**Checklist:** {play.get('checklist_score', '—')}"
                )
                if play.get("tranches"):
                    st.markdown(
                        "**Tranches:** " + " → ".join(f"{t['pct']}% {t['condition']}" for t in play["tranches"])
                    )
                st.markdown(f"**Thesis:** {play.get('thesis', '—')}")
                if play.get("risks"):
                    st.markdown(f"**Risks:** {play['risks']}")

        wl = plays.get("watchlist", [])
        st.subheader("Watchlist / scouting")
        if wl:
            st.dataframe(pd.DataFrame(wl), use_container_width=True, hide_index=True)
        else:
            st.caption("Empty — the daily run refills this with candidates worth tracking.")

# ---------------------------------------------------------------- OPTIMIZER
with tab_opt:
    st.caption(
        "Modern Portfolio Theory over daily returns (native currencies, long-only, fully invested). "
        "Output is a *suggested* allocation — compare, don't blindly follow."
    )
    watch_tickers = [w.get("yf_ticker") or w.get("ticker") for w in plays.get("watchlist", []) if isinstance(w, dict)]
    default_universe = sorted({t for t in list(yf_tickers) + watch_tickers if t})
    extra = st.text_input("Extra tickers (comma-separated Yahoo symbols)", "")
    universe = sorted(set(default_universe) | {t.strip().upper() for t in extra.split(",") if t.strip()})
    universe = st.multiselect("Universe", universe, default=universe)
    max_w = st.slider("Max weight per asset (%)", 5, 100, 30, 5) / 100

    if len(universe) < 2:
        st.info("Pick at least 2 assets (holdings + watchlist are preselected once they exist).")
    else:
        uni_hist = load_history(tuple(universe), period)
        rets = metrics.daily_returns(uni_hist).dropna(axis=1, thresh=60)
        dropped = sorted(set(universe) - set(rets.columns))
        if dropped:
            st.warning(f"Dropped (not enough history): {', '.join(dropped)}")
        if rets.shape[1] < 2:
            st.error("Not enough usable price history to optimize.")
        else:
            eff_max_w = max(max_w, 1.0 / rets.shape[1] + 1e-6)
            if eff_max_w > max_w:
                st.caption(
                    f"Cap raised to {eff_max_w:.0%} — with {rets.shape[1]} assets a "
                    f"{max_w:.0%} cap cannot sum to 100%."
                )
            frontier, w_sharpe, w_minvol, mu, cov = optimizer.efficient_frontier(rets, rf, eff_max_w)
            if frontier is None:
                st.error("Optimization infeasible — raise the max weight cap.")
            else:
                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x=frontier["vol"] * 100,
                        y=frontier["ret"] * 100,
                        mode="lines+markers",
                        name="Efficient frontier",
                        marker=dict(color=frontier["sharpe"], colorscale="Viridis", size=7),
                        hovertemplate="vol %{x:.1f}% · ret %{y:.1f}%<extra></extra>",
                    )
                )
                for w, name, symbol in ((w_sharpe, "Max Sharpe", "star"), (w_minvol, "Min volatility", "diamond")):
                    s = optimizer.portfolio_stats(w, mu, cov, rf)
                    fig.add_trace(
                        go.Scatter(
                            x=[s["vol"] * 100],
                            y=[s["ret"] * 100],
                            mode="markers+text",
                            name=name,
                            text=[name],
                            textposition="top center",
                            marker=dict(size=16, symbol=symbol),
                        )
                    )
                if not df.empty:
                    cur_w = df.set_index("yf")[f"Value {CZK}"]
                    cur_w = cur_w[cur_w.index.isin(rets.columns)]
                    if len(cur_w) >= 2:
                        cur_w = cur_w / cur_w.sum()
                        s = optimizer.portfolio_stats(cur_w, mu, cov, rf)
                        fig.add_trace(
                            go.Scatter(
                                x=[s["vol"] * 100],
                                y=[s["ret"] * 100],
                                mode="markers+text",
                                name="Current portfolio",
                                text=["Current"],
                                textposition="bottom center",
                                marker=dict(size=16, symbol="x", color="#e45756"),
                            )
                        )
                fig.update_layout(
                    xaxis_title="Annualized volatility (%)",
                    yaxis_title="Annualized return (%)",
                    height=480,
                    margin=dict(t=20),
                )
                st.plotly_chart(fig, use_container_width=True)

                comp = pd.DataFrame(
                    {
                        "Max Sharpe %": (w_sharpe * 100).round(1),
                        "Min Vol %": (w_minvol * 100).round(1),
                    }
                )
                if not df.empty:
                    cur = df.set_index("yf")["Weight %"].reindex(comp.index).fillna(0).round(1)
                    comp.insert(0, "Current %", cur)
                    comp["Δ to Max Sharpe (CZK)"] = (
                        (comp["Max Sharpe %"] - comp["Current %"]) / 100 * invested_czk
                    ).round(0)
                comp = comp[(comp > 0.05).any(axis=1)].sort_values(comp.columns[-2], ascending=False)
                st.dataframe(comp, use_container_width=True)

# ---------------------------------------------------------------- RISK
with tab_risk:
    if df.empty or hist.empty:
        st.info("Add positions first.")
    else:
        pos_rets = metrics.daily_returns(hist[[c for c in hist.columns if c in set(df["yf"])]])
        r1, r2, r3, r4 = st.columns(4)
        if len(port_returns) > 20:
            var, cvar = metrics.var_cvar(port_returns)
            r1.metric("1-day VaR 95%", czk(var * invested_czk), pct(-var * 100, 2))
            r2.metric("1-day CVaR 95%", czk(cvar * invested_czk), pct(-cvar * 100, 2))
            r3.metric(f"Beta vs {benchmark}", f"{metrics.beta(port_returns, bench_returns):.2f}")
            r4.metric("Sortino", f"{metrics.sortino(port_returns, rf):.2f}")
        hhi = metrics.herfindahl(df["Weight %"]) if "Weight %" in df else np.nan
        st.caption(
            f"Concentration (HHI): **{hhi:.2f}** — 1/n = {1 / max(len(df), 1):.2f} would be equal-weight. "
            "Above ~0.30 means one position dominates the book."
        )

        cl, cr = st.columns(2)
        with cl:
            if pos_rets.shape[1] >= 2:
                corr = pos_rets.corr()
                heat = px.imshow(
                    corr,
                    text_auto=".2f",
                    color_continuous_scale="RdBu_r",
                    zmin=-1,
                    zmax=1,
                    title="Correlation matrix (daily returns)",
                )
                heat.update_layout(height=420, margin=dict(t=40))
                st.plotly_chart(heat, use_container_width=True)
        with cr:
            if len(port_returns) > 20:
                dd = metrics.drawdown_series(port_returns) * 100
                ddfig = go.Figure(go.Scatter(x=dd.index, y=dd.values, fill="tozeroy", line=dict(color="#e45756")))
                ddfig.update_layout(title="Portfolio drawdown (%)", height=420, margin=dict(t=40))
                st.plotly_chart(ddfig, use_container_width=True)

        cur_exp = df.groupby("CCY")[f"Value {CZK}"].sum().reset_index()
        cpie = px.pie(cur_exp, values=f"Value {CZK}", names="CCY", hole=0.45, title="Currency exposure")
        cpie.update_layout(height=330, margin=dict(t=40, b=0))
        st.plotly_chart(cpie, use_container_width=True)
