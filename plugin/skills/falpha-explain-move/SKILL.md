---
name: falpha-explain-move
description: Explain what changed fAlpha's reading on a stock: when the signal flipped direction, what drove each change, and what the model said on a past date. Use when the user asks why fAlpha turned bullish or bearish, or how the reading has moved.
---

# Explain a move in fAlpha's reading

1. Call `falpha_signal_desk_flips` for the ticker and horizon (default `hp2m`, 180-day
   lookback). It lists the dates the direction changed and the drivers at each change.
2. To compare with a specific past date, call `falpha_signal_desk_history` with that
   `as_of_date`. It reads point-in-time, using only data available on that date.
3. For a range, `falpha_signal_desk_performance` gives how the stock and the signal performed
   between two dates. Report the figures with their dates; they describe the past only.
4. If the user asks what a term means (EI, drivers, regime), call
   `falpha_research_librarian`.

Explain drivers as what changed the reading over the seven days before each date.

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
