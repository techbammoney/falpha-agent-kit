# Example prompts

Each prompt below maps to tools the fAlpha MCP server exposes today. Results are model output,
not investment advice.

| Prompt | Tools it uses |
|---|---|
| What does fAlpha's signal say about NVDA over the next two months, and what is driving it? | `falpha_signal_desk_card` |
| Compare AAPL and MSFT on fAlpha's current signal. | `falpha_signal_desk_compare` |
| When did fAlpha's signal on TSLA last change direction, and what changed in its drivers? | `falpha_signal_desk_flips` |
| Show fAlpha's term structure for AMZN, from one day out to six months. | `falpha_signal_desk_curve` |
| What did fAlpha's signal on JPM say on 2026-06-30, using only data available that day? | `falpha_signal_desk_history` |
| Rank fAlpha's covered universe by the current signal in Health Care. | `falpha_screener_desk` |
| What is today's news sentiment on AMD, and which articles is it computed from? | `falpha_sentiment_desk` |
| How has news sentiment on AMD moved over the last 30 days? | `falpha_sentiment_desk_trend` |
| Show AAPL's latest 10-Q and its reported revenue from SEC XBRL filings. | `falpha_filings_scout`, `falpha_filings_scout_facts` |
| What is the US macro backdrop right now: fed funds, CPI and unemployment? | `falpha_macro_desk` |
| What does "equity indicator" mean in fAlpha's results? | `falpha_research_librarian` |
