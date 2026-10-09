---
name: stock-news-timeline
description: Build a dated timeline of news and price impact for one or more stocks (IBKR holdings or any tickers) over a chosen timeframe, with the user's own trades overlaid.
---

# Stock news timeline

Explains *why* a stock (or a portfolio) moved: find the biggest price moves in a window, match each to the news that caused it, overlay the user's own buys/sells, and render it as a vertical timeline.

## Inputs (ask only if missing and not inferable)
- **Stocks**: tickers the user names, or "my portfolio" -> current IBKR positions.
- **Timeframe**: default 1 year / year-to-date. Map to IBKR `period`: 1M -> ONE_MONTH, 3M -> THREE_MONTHS, 6M -> SIX_MONTHS, 1Y/YTD -> ONE_YEAR, 2Y -> TWO_YEARS, 5Y -> FIVE_YEARS.
- Bar size: `ONE_DAY` for <=1Y; `ONE_WEEK` for 2Y/5Y.

## Steps

### 1. Resolve contracts and holdings (IBKR connector)
- Load IBKR tools in one ToolSearch call: `get_account_positions`, `get_account_trades`, `get_price_history`, `search_contracts`.
- Portfolio mode: `get_account_positions` gives `contract_id`, quantity, avg cost, unrealized P&L.
- Named tickers not held: `search_contracts` to get `contract_id`.
- Trades: `get_account_trades` with `YEAR_TO_DATE` (add LAST_QUARTER ... FOUR_QUARTERS_AGO for longer windows). Keep only STK trades for the stocks in scope; ignore FX conversion rows. Treat DRIP buys (exchange IBDRIPUS) as dividend reinvestments, not decisions.
- If IBKR isn't connected, skip trades and use web/market data for prices.

### 2. Pull prices and find the big moves
Call `get_price_history` per stock (security_type STK, outside_rth false). Save each response's `time` and `close` arrays to a JSON file and run code - never eyeball the numbers:

```python
import json, sys, pandas as pd
d = json.load(open(sys.argv[1]))           # {"TICKER": {"time": [...], "close": [...]}, ...}
for tk, s in d.items():
    df = pd.Series(s["close"], index=pd.to_datetime(s["time"]).date)
    r = df.pct_change().dropna()
    thr = max(0.04, 2.5 * r.std())          # use 0.06 for weekly bars
    big = r[r.abs() >= thr].sort_values(key=abs, ascending=False).head(8)
    print(tk, f"start {df.iloc[0]:.2f} end {df.iloc[-1]:.2f} chg {df.iloc[-1]/df.iloc[0]-1:+.1%}",
          f"high {df.max():.2f} ({df.idxmax()}) low {df.min():.2f} ({df.idxmin()})")
    for dt, v in big.sort_index().items():
        prev = df.iloc[df.index.get_loc(dt) - 1]
        print(f"  {dt}  {v:+.1%}  {prev:.2f} -> {df[dt]:.2f}")
```
Also note slow multi-week drifts (e.g. >8% over 3 weeks with no single big day) - these are usually macro, not company news.

### 3. Match each move to news
- For each big move, search the web separately: `<company> stock <month year>` / `<company> shares fall <keyword>`. Earnings, guidance, regulator actions, downgrades, FX and index selloffs are the usual causes.
- One search per stock and per event; don't combine.
- Prefer primary sources (company releases, SEC 6-K/8-K, exchange filings) and reputable outlets over SEO aggregator pages.
- For ADRs, check the home-market currency (e.g. INR, CNY/HKD) - currency weakness alone can move an ADR.
- For drifts with no company news, check the relevant index (Hang Seng, Nifty, S&P 500, etc.) for that window.

**Honesty rules**
- Only attribute a move to news whose date matches. If no cause is found, say "no clear catalyst found" or describe it as coinciding with a macro event - never invent a reason.
- If sources disagree on a date, use the price data to settle which day the move happened.
- Paraphrase sources; cite them. No financial advice - present facts, not buy/sell calls.

### 4. Overlay the user's trades
- Group trades into lots (date range, shares, avg price) and place them on the timeline as "You bought / sold" events.
- Compute P&L per lot vs the latest close (in code) so the user sees which entries caused the loss/gain.
- If this contradicts something said earlier in the conversation (e.g. "you bought before the bad news"), correct it plainly.

### 5. Render
Inline timeline (default) via the Visualizer (`read_me` with the `interactive` module), then `show_widget`:
- Top: one metric card per stock (period % change, start -> end price). Max 2 columns on mobile.
- Legend: one color per stock (coral, purple, teal, pink in that order), gray for market-wide events, blue outline dot for the user's trades.
- Vertical timeline, oldest first. Each card: date (muted, 12px), headline <=6 words (15px/500), one-line detail (13px secondary), impact pill ("-17% in a day", danger tint for negative) plus "$from -> $to".
- Last card: "Where it stands" with latest prices.
- Build the cards from a JS array so the code stays short; CSS variables only, no hardcoded text colors.

If the user wants to keep or share it, publish it as an Artifact instead of (or after) the inline view.

### 6. Reply text (after the visual)
- 1-2 lines on the main takeaway (which events did the damage, and which of the user's lots carry the loss).
- A short bullet per key event with cited sources.
- A "Sources:" list of links.
- Don't repeat the timeline cards verbatim in prose.
