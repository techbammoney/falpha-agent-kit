---
name: falpha-sector-screen
description: Screen fAlpha's covered US stocks by the current model signal, optionally within a sector or one direction, ranked by signal strength or realized Sharpe. Use when the user asks which names fAlpha leans on in a sector, or for the strongest current readings.
---

# Screen with fAlpha

1. Call `falpha_screener_desk` with the user's sector, direction (`long`, `short` or `any`),
   ranking (`ei` for signal strength, `sharpe` for realized quality), horizon, regime and
   `top_k`.
2. Read the result's `universe` field and say which set was ranked. On trial and
   pay-as-you-go plans it is only the tickers the plan covers today, not the whole universe.
3. Show the rows with ticker, direction, EI, the ranking statistic and date. Offer
   `falpha_signal_desk_card` for any row the user wants to look at.

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
