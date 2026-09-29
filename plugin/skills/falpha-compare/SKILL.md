---
name: falpha-compare
description: Compare two or more US stocks on fAlpha's model signal: direction, strength, quality and main driver side by side. Use when the user asks which of several tickers fAlpha reads more strongly, or wants them compared on the model.
---

# Compare stocks on fAlpha's signal

1. For exactly two tickers, call `falpha_signal_desk_compare`. For three or more, call
   `falpha_signal_desk_card` for each, with the same horizon and regime (default `hp2m`,
   `neutral`, unless the user says otherwise).
2. Show one table: ticker, direction, EI, quality (Sharpe and hit rate when present), dominant
   driver, date.
3. Say which carries the stronger reading and on what horizon. "Stronger" means a larger EI
   magnitude, nothing more. If readings disagree across horizons and it matters,
   `falpha_signal_desk_curve` shows the term structure for each.

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
