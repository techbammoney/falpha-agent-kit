# fAlpha for AI agents

fAlpha's MCP server gives AI assistants and agent frameworks read-only research tools:
- fAlpha's model signal for a US stock, with the drivers behind it;
- its history, flips and term structure;
- news sentiment and analyst coverage;
- SEC filings and XBRL facts;
- the FRED macro backdrop;
- company fundamentals.

Every result says which source produced it and the date the data is for.

The signal is model output, not investment advice. The server never places orders.

## Connect

- **Endpoint:** `https://agent.falpha.ai/mcp` (Streamable HTTP)
- **Auth:** OAuth 2.1 with PKCE, or a personal access token (`falpha_pat_…`)
- **Docs:** https://falpha.ai/mcp

**With your fAlpha account (OAuth).** One-click links for Cursor and VS Code are at
https://falpha.ai/mcp#connect-account. Elsewhere:
- **Claude (web and desktop):**
  1. Customize → Connectors → +.
  2. Name it fAlpha, paste the endpoint, select Add.
  3. Approve access on falpha.ai.
- **ChatGPT:**
  1. Settings → Security and login → turn on Developer mode.
  2. In ChatGPT Plugins, select + and enter the endpoint.
  3. Approve access on falpha.ai.
- **Claude Code:** `claude mcp add --transport http falpha https://agent.falpha.ai/mcp`, then
  `/mcp` to sign in.
- **Codex:** add the server to `~/.codex/config.toml`, then run `codex mcp login falpha`:
  ```toml
  [mcp_servers.falpha]
  url = "https://agent.falpha.ai/mcp"
  ```

**With a token.** Mint one at https://falpha.ai/account#apikey, or get a no-card trial token at
https://falpha.ai/mcp/trial. Send it as `Authorization: Bearer falpha_pat_…`. Config snippets for
each client are at https://falpha.ai/mcp#connect-token.

## Tools

<!-- tools:start -->
17 read-only tools, as listed by fAlpha version 2026.09.23.

- **falpha_signal_desk_card**: Signal card. The model's current reading on one ticker: the equity indicator (EI, signed: positive leans long, negative leans short), the signal's risk-adjusted track record, and the driver carrying the reading, with the date the signal is for.
- **falpha_signal_desk_compare**: Compare two signals. Two tickers side by side on the current signal, with which of the two carries the stronger reading.
- **falpha_signal_desk_history**: Signal on a past date. The signal and its drivers as they stood on a past date, read point-in-time: only data available on that date is used.
- **falpha_signal_desk_performance**: Signal performance over a range. How a ticker performed over a date range and how the signal would have performed if followed, measured against a benchmark.
- **falpha_signal_desk_flips**: Signal direction flips. The dates the signal changed direction (long to short or back) over a lookback window, the drivers at each change, and the current direction.
- **falpha_signal_desk_curve**: Signal term structure. The model's term structure for a ticker: the equity indicator's direction from one day out to six months, the curve's shape (strengthening, weakening or flipping) and whether the sign changes across horizons.
- **falpha_screener_desk**: Screen the covered universe. Ranks fAlpha's covered universe (about 5,000 US equities) by the current signal, either the equity indicator or the signal's realized Sharpe ratio, filtered by direction, sector or a minimum Sharpe ratio.
- **falpha_screener_desk_coverage**: Coverage check. Whether a ticker is in fAlpha's covered universe, with its sector and latest signal date, or a page through the universe.
- **falpha_sentiment_desk**: News sentiment. fAlpha's daily news sentiment score for a ticker, with the articles it was computed from and the date of the reading.
- **falpha_sentiment_desk_trend**: News sentiment trend. How news sentiment has moved over a window: the current reading, the change since the window opened, the direction, the high/low band and the daily series.
- **falpha_analyst_desk**: Analyst coverage. Sell-side coverage for a ticker: recent price-target calls with source links, an accuracy-weighted consensus lean, and each analyst's historical hit rate, including their accuracy when agreeing and when disagreeing with the fAlpha model.
- **falpha_research_librarian**: Define a fAlpha term. The fAlpha definition of a term the desks return: EI (equity indicator), VICE, drivers, Sharpe, Sortino, percent_positive_pnl, signal flip, term structure.
- **falpha_filings_scout**: SEC filings. Recent SEC filings for a ticker from SEC EDGAR (10-K, 10-Q and 8-K by default), newest first, each with its filing date and document URL.
- **falpha_filings_scout_facts**: SEC XBRL company facts. Reported fundamentals from SEC XBRL filings: revenue, net income, diluted EPS, total assets, total liabilities and stockholders' equity, for the latest reported quarters and fiscal years, each with its period end and filing date.
- **falpha_macro_desk**: Macro backdrop (FRED). The US macro backdrop from FRED: the fed funds rate (DFF), CPI (CPIAUCSL), unemployment (UNRATE), the 10y-2y spread (T10Y2Y) and the 10-year yield (DGS10).
- **falpha_fundamentals_desk**: Company profile and ratios (FMP). Company profile and trailing-twelve-month ratios from FMP: sector, market cap, P/E, margins, debt/equity.
- **falpha_open_in_web**: Open fAlpha on the web. Links to the fAlpha website and the user's account page, where plan, usage and billing are shown.
<!-- tools:end -->

The list is generated from the live server's public catalog
(`https://agent.falpha.ai/mcp/catalog`) by `scripts/sync_tools.py`.

## Claude plugin

[plugin/](plugin) packages four skills that use the fAlpha connector: research a ticker, compare
names, screen a sector, and explain a move in the reading. Try it locally with
`claude --plugin-dir ./plugin`.

## ChatGPT plugin

[openai-plugin/](openai-plugin) holds the ChatGPT plugin manifest, MCP config and icons. It ships
the same four skills as the Claude plugin. `scripts/build-openai-plugin.sh` writes the upload
ZIP to `dist/`.

## Recipes

- [recipes/alpaca-paper](recipes/alpaca-paper): an agent that reads fAlpha, makes its own
  decision, places paper orders on Alpaca through Alpaca's MCP server, and keeps a
  tamper-evident decision log.

## Use fAlpha in Composio

[Composio](https://composio.dev) gives agents built with LangChain, CrewAI, the OpenAI Agents SDK and
others a catalog of tools. Composio's Custom MCP feature (experimental) adds fAlpha to your own
Composio project:

```bash
COMPOSIO_API_KEY=... scripts/composio-register.sh          # users approve read access on falpha.ai
COMPOSIO_API_KEY=... scripts/composio-register.sh api_key  # or: users paste a falpha_pat_ token
```

Then, in your agent:

```python
session = composio.sessions.create(user_id="...", toolkits=["CUSTOM_FALPHA"])
tools = session.tools()
```

- **Where the credential lives:** Composio stores each user's fAlpha credential on its side.
- **What the agent gets:** the same 17 read-only tools as every other client.

## Example prompts

See [examples/prompts.md](examples/prompts.md).

## Data

- **fAlpha's own:** the model signal and its drivers, and news sentiment computed from public
  news articles.
- **Financial Modeling Prep:** the prices the model reads, the sell-side price targets behind the
  analyst desk, and company profile and ratios.
- **SEC EDGAR:** filings and XBRL facts.
- **FRED:** macro series.

## Registry

fAlpha is listed in the official MCP Registry as `ai.falpha/mcp` (`server.json` is the entry's
source) and on [Smithery](https://smithery.ai/servers/falpha/mcp).

## License

Everything in this repository (the recipes, the Claude plugin, the scripts and examples) is
MIT-licensed; see [LICENSE](LICENSE). Using the fAlpha service itself (the MCP server and API)
requires an fAlpha account and is governed by fAlpha's Terms of Service. The MIT license covers
this code, not fAlpha's data or service.
