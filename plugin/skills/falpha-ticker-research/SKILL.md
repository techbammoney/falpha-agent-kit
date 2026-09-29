---
name: falpha-ticker-research
description: Research one US-listed stock with fAlpha: the model's reading across horizons, what drives it, news sentiment, analyst coverage and reported fundamentals. Use when the user asks what fAlpha or "the model" says about a ticker, or wants a research brief on a US stock.
---

# Research a ticker with fAlpha

1. If you are not sure the ticker is covered, call `falpha_screener_desk_coverage` with it. If
   it is not covered, say so and stop.
2. Call `falpha_signal_desk_curve` for the term structure (one day out to six months), then
   `falpha_signal_desk_card` for the horizon the user cares about (default `hp2m`) to get the
   drivers and quality statistics. Use the `neutral` regime unless the user names bull or bear.
3. Call `falpha_sentiment_desk_trend` (30 days) for how the news tone has moved.
4. Call `falpha_analyst_desk` for sell-side coverage, and `falpha_filings_scout_facts` when
   the user wants reported fundamentals.

Present a short brief:
- the reading per horizon, with direction, EI and date;
- the dominant driver, explained as what changed the reading over the last seven days, not a
  judgement on the stock;
- the sentiment trend, analyst coverage and any fundamentals, each with its date and source.

## Ground rules (every answer)

- Use only the fAlpha tools (`falpha_*`). Every figure you state comes from a tool result in
  this conversation; never estimate or invent one.
- Give each reading its date (`data_as_of` or `signal_date`). If a result says `stale: true`,
  say so next to the figure.
- If a tool returns `status: "no_data"`, a refusal such as `plan_not_entitled` or
  `ticker_not_in_plan`, or an error, say that plainly. Do not fill the gap.
- The equity indicator (EI) is a signed model score (positive leans up, negative leans down,
  relative to the index), not a probability.
- Never present a reading as a recommendation to buy or sell. Close with: "fAlpha signals are
  model output, not investment advice."
