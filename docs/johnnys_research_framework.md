# Johnny's 3-Step Stock Research Framework
### Institutional-Style Analysis for Spot Stock Swing Trades

---

> **How to use this:** Send the prompt for each step to Claude one at a time, with the ticker filled in.
> Run Step 1 first, then Step 2, then Step 3. Each one builds on the last.
> After Step 3, ask for the trade setup separately using the Step 4 prompt.
>
> **Scope:** Spot stock only. Buys = entering a new position.
> Sells = exiting a position you already own if the thesis breaks or target is hit.
> No shorting. Hold period: 1 day to 2 months.

---

## WHERE TO FIND CANDIDATES

Before running the research, you need a stock worth researching. Use these sources:

**Unusual Whales** — for institutional conviction signals
- Filter: Call flow · Premium $50K+ · Ask side (aggressive buys, not passive)
- Look for: Sweeps on $500M–$10B market cap stocks · Repeat flow on same ticker same day
- Why it works for spot: when large money is buying calls aggressively, the underlying stock
  usually follows. You buy the stock, not the option.
- Skip: AAPL/TSLA/SPY (too noisy) · Flow on stocks already up 30%+ in a week

**Earnings Whispers** — for pre-earnings drift setups
- Filter: Market cap $500M–$10B · Reports in 2–4 weeks · Historical beat rate 65%+
- Look for: Whisper number close to or below official consensus (low bar = upside surprise)
- Entry timing: Buy the stock 2–4 weeks before earnings, sell BEFORE the actual report
  unless your research gives you very high conviction on the print
- The play: you are capturing the pre-earnings drift — the stock runs up in anticipation,
  you sell into that strength before the binary event

**Finviz Scanner** — for momentum and gap setups
- Filter: Price change >5% today · Volume >2x average · Market cap >$200M
- Look for: Stocks breaking out on real news, not just technical noise
- Use the news tab to confirm there is an actual catalyst, not just a pump

**Cross-reference rule:** A stock with unusual call flow AND an upcoming catalyst
in 2–4 weeks AND a clean technical setup is your highest-conviction buy.

---

## STEP 1 — CATALYST BREAKDOWN

> *What is actually happening and why is this stock moving?*

```
You are an institutional equity research analyst. For ticker
$[TICKER], give me a complete catalyst breakdown.

Search the web for current data. Cover these in order:

1. CURRENT SETUP
   - Price right now, market cap, 30-day and YTD performance
   - The recent move that put this stock on people's radar

2. THE DOMINANT NARRATIVE
   - What is the bull thesis being repeated on X / Reddit / TikTok?
   - Quote the most viral framing if there is one
   - Note any specific price targets retail is calling for

3. THE ACTUAL CATALYST
   - The real event that triggered the move (earnings, contract,
     partnership, policy change). Be specific with dates and
     dollar amounts
   - What did the company actually announce or report?
   - What did management say about forward guidance?

4. THE INSTITUTIONAL VIEW
   - Recent analyst target changes (upgrades, downgrades,
     reiterations)
   - Where consensus sits vs current price
   - Any institutional buying or selling (13F changes, insider
     activity)

End with a one-line verdict in this format:
"The stock is moving because [REAL CATALYST], but [WHAT NOBODY
IS TALKING ABOUT] is the part that matters."

Keep response under 300 words. Be specific. No vague language.
```

**What to look for in the answer:**
- Is the catalyst real, dated, and specific — or just narrative momentum?
- Is insider activity confirming the move or quietly exiting into it?
- Is the "what nobody is talking about" a dealbreaker or a manageable risk?
- Is there a clear upcoming event (earnings, FDA, contract) that gives the trade a timer?

---

## STEP 2 — FINANCIAL HEALTH & COMPETITIVE VALUATION

> *Is the stock cheap, fair, or expensive versus its real peers?*

```
You are an institutional equity research analyst. For ticker
$[TICKER], do a financial health and competitive
valuation breakdown.

Search the web for current data. Cover these in order:

1. THE STOCK ITSELF
   - Current price, market cap, 30-day and YTD performance
   - Forward P/E and EV/Sales
   - Last quarter revenue growth, EPS growth, gross margin
   - Cash position, debt, and share count change YoY (dilution)
   - Last management guidance (revenue and EPS for next year)

2. THE 5 CLOSEST COMPETITORS
   Identify the 5 most relevant publicly-traded competitors.
   Build a comparison table with:
   - Ticker and company name
   - Forward P/E
   - EV/Sales (forward)
   - Revenue growth (last reported quarter)
   - Market cap
   - One-line note on positioning vs $[TICKER]

3. THE VERDICT
   Based on the peer comparison:
   - Is $[TICKER] at a premium, in line, or at a discount?
   - Show the math (e.g., "trading at 4.1x sales vs peer median
     of 6x = 30% discount")
   - Note any specific anomaly (e.g., "growing twice as fast at
     half the multiple")

End with a conditional verdict:
"If you believe [BULL THESIS], $[TICKER] is [CHEAP / FAIR /
EXPENSIVE] versus its peers because [REASON]."

Keep response under 300 words. Show numbers, not adjectives.
```

**Key metrics cheat sheet:**
| Metric | What it measures | Red flag |
|--------|-----------------|----------|
| Forward P/E | Future profit multiple | N/A = no earnings yet (speculative name) |
| EV/Sales | Revenue multiple including debt and cash | >20x on slow growth = expensive |
| Gross margin | Unit economics — how profitable each sale is | Contracting QoQ = cost problem |
| Share count YoY | Dilution — are shares being issued, shrinking your % ownership | >15% increase = equity destruction |
| Net cash / Net debt | Balance sheet strength | Net debt + no free cash flow = survival risk |
| Free cash flow | Actual cash generated after capex | Negative FCF + high burn = dilution coming |

**What to look for in the answer:**
- Is the valuation premium justified by faster growth than peers, or just hype?
- Is dilution eroding per-share value even as the top line grows?
- Are gross margins expanding (good) or contracting (warning) quarter-over-quarter?
- Does the company have enough cash to reach profitability without another raise?

---

## STEP 3 — SENTIMENT, ANALYST DATA & PRICE SCENARIOS

> *What does the risk/reward look like across multiple time horizons?*

```
You are an institutional equity research analyst. For ticker
$[TICKER], build a complete forward-looking framework
with sentiment, analyst data, and price scenarios.

Search the web for current data. Cover these in order:

1. RETAIL SENTIMENT (Yahoo Finance + Social)
   - Pull the sentiment summary from Yahoo Finance conversations
   - Note the dominant tone (bullish / bearish / mixed)
   - Pull 2-3 of the highest-engagement bullish takes from X
     or StockTwits with their framing
   - Pull 2-3 of the highest-engagement bearish takes
   - Identify if sentiment is uniform (warning sign) or split

2. ANALYST PROJECTIONS
   - Number of analysts covering the stock
   - Consensus rating (Strong Buy / Buy / Hold / Sell)
   - Consensus 12-month price target (median, high, low)
   - Where current price sits versus consensus
   - Recent target changes in the last 30 days
   - FY revenue and EPS estimates for next 1-2 years

3. FOUR PRICE SCENARIOS
   Build the asymmetry framework with math for each:
   - BEAR (1–4 weeks): Price if catalyst fails or macro turns
   - BASE (1–2 months): Price if execution holds at consensus
   - BULL (1–2 months): Price if catalyst beats expectations
   - EXTENDED BULL (2+ months): Price if thesis fully plays out

4. THE SPOT TRADE PLAN
   - Entry zone: ideal buy price or price range on a pullback
   - First sell level: where to sell 30–50% of the position
   - Second sell level: where to sell the rest
   - Hard stop: the price at which you sell everything —
     thesis is broken, do not hold and hope
   - Hold duration: realistic days or weeks to target,
     not a calendar date

End with the verdict in this format:
"This is a [BUY NOW / BUY ON PULLBACK / HOLD / SELL / PASS]
because [REASON]. Hold for [TIMEFRAME]."

Keep response under 400 words. Specific price levels, no hand-waving.
```

**What to look for in the answer:**
- Is sentiment split? 100% bullish = crowded trade = fragile, one bad print kills it
- Is the BASE scenario already priced in? If stock = BASE target, there is no edge left
- Is the hard stop a realistic dollar loss relative to your account size?
- Does the hold duration fit your 1 day–2 month window?
- Is the verdict BUY or PASS — if it says HOLD or unclear, that means wait for better entry

---

## STEP 4 — SPOT STOCK TRADE SETUP

> *Run this after all three steps above are complete. This is the execution plan.*

```
Based on the full research above for $[TICKER], give me a
precise spot stock trade plan for a hold period of 1 day to
2 months. No options, no shorting — spot buy and sell only.

Give me:

ENTRY
- Exact buy zone (price range, not a single number)
- Whether to buy all at once or in two tranches
- What market condition to wait for before buying
  (e.g., "wait for a green candle after a pullback to $X")

POSITION MANAGEMENT
- First sell level: price + % of position to sell (e.g., 40%)
- Second sell level: price + % of remaining position to sell
- Hard stop: the exact price at which you sell everything,
  no exceptions — thesis is broken at this level

TIMING
- Expected hold duration (realistic range, e.g., "2–6 weeks")
- The single upcoming event or date that makes or breaks the trade
- What to do if the stock does nothing for 2 weeks (hold or cut)

RISK/REWARD
- Maximum loss if hard stop is hit (in % from entry)
- Expected gain to first sell level (in % from entry)
- Expected gain to full exit (in % from entry)
- Risk/reward ratio (e.g., risking 7% to make 18% = 1:2.6)

ONE-LINE WARNING
- The single scenario that would make you sell immediately,
  even before the hard stop price is hit

Keep all levels specific. Show the math. No vague language.
```

**Spot trading rules to always apply:**
- Never buy a stock that is up 15%+ on the day — wait for the first pullback
- Always define your hard stop BEFORE entering — not after
- If a stock hits your hard stop, sell. Do not lower it. Do not "give it more room."
- Sell in tranches going up, not all at once — let winners run partially
- If you are holding into an earnings report, size down to 50% first — binary risk
- Idle positions with no catalyst and no move within 10 days: reassess or cut
- Never add to a losing position to "average down" unless the thesis is explicitly intact
  and you planned the second tranche in advance

---

## WHEN TO SELL A POSITION YOU ALREADY OWN

This framework applies to both buying new positions and deciding
whether to sell something already in your portfolio.

**Sell signals — exit partially or fully:**

| Signal | Action |
|--------|--------|
| Stock hits your first sell level | Sell 30–50%, let rest run |
| Stock hits your second sell level | Sell the rest, close position |
| Hard stop price is breached on a close | Sell everything next open, no exceptions |
| Original catalyst is confirmed and priced in | Sell 50–75%, reassess the rest |
| Management guidance disappoints on an earnings call | Sell immediately |
| Insider selling appears in SEC filings above 5% of holdings | Reduce by 50% |
| A better opportunity appears and capital is needed | Cut the weakest position first |
| Stock has done nothing in 3+ weeks with no upcoming catalyst | Cut and redeploy |

**Do not sell just because:**
- The stock pulled back 3–5% on normal market noise
- You are nervous — check if the thesis is still intact first
- Someone on Reddit or X is bearish — check the fundamentals, not the sentiment

---

## SIGNAL QUALITY CHECKLIST

Run through this before entering any position. Score below 4/6 = pass.

| Check | Question | Pass condition |
|-------|----------|---------------|
| ✅ Catalyst | Is there a real, dated, specific upcoming event? | Yes — named event with a date |
| ✅ Valuation | Is the stock at or below peer median, or premium justified? | At/below peer median, or clear growth justification |
| ✅ Sentiment | Is sentiment split, not uniformly bullish? | Bears and bulls both present |
| ✅ Analyst | Does consensus have 15%+ upside to current price? | Yes |
| ✅ Risk/Reward | Is the R:R ratio at least 1:2 (risk 1 to make 2)? | Yes |
| ✅ Timing | Does the trade fit within a 1 day–2 month window? | Catalyst or target within that window |

---

## RED FLAGS — AUTOMATIC PASS

These conditions override everything else. Do not enter the trade.

- **Stock up 40%+ in the last 30 days with no new catalyst** — momentum exhausted, late entry
- **Active shelf offering or ATM share issuance** — dilution is actively destroying equity value
- **Insider selling above 10% of their holdings** in last 90 days — smart money exiting
- **Negative gross margin** — the company loses money on every sale, no floor under price
- **Net debt + negative free cash flow + no path to profitability** — survival risk
- **Earnings in 1–3 days and you do not have a clear view on the print** — binary risk, wait
- **100% bullish sentiment with no bears** — everyone is already in, no one left to buy
- **No analyst coverage** — no institutional awareness, no price target anchor, pure speculation
- **Stock below its 200-day moving average on declining volume** — structural downtrend, not a dip

---

## FRAMEWORK SUMMARY

```
STEP 1: What is actually happening?          → Catalyst + institutional view
STEP 2: Is the price justified?              → Valuation vs peers
STEP 3: What does the risk/reward look like? → Scenarios + trade plan
STEP 4: What is the exact execution?         → Entry, sell levels, stop, R:R
CHECKLIST: Should I actually enter?          → 4/6 minimum to proceed
SELL RULES: When do I exit what I own?       → Defined signals, no guessing
```

**The most important rule in the whole framework:**
Define the hard stop before you buy. If you do not know the price
at which you are wrong, you do not have a trade — you have a hope.

---

*Built from live research on $SERV, $IWM, and $MU — June 2026*
*Framework developed with Claude (Anthropic) — not financial advice. DYOR.*
