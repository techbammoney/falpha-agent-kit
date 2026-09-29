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

| Tool | What it returns |
|---|---|
| `falpha_signal_desk_card` | Signal card |
| `falpha_signal_desk_compare` | Compare two signals |
| `falpha_signal_desk_history` | Signal on a past date |
| `falpha_signal_desk_performance` | Signal performance over a range |
| `falpha_signal_desk_flips` | Signal direction flips |
| `falpha_signal_desk_curve` | Signal term structure |
| `falpha_screener_desk` | Screen the covered universe |
| `falpha_screener_desk_coverage` | Coverage check |
| `falpha_sentiment_desk` | News sentiment |
| `falpha_sentiment_desk_trend` | News sentiment trend |
| `falpha_analyst_desk` | Analyst coverage |
| `falpha_research_librarian` | Define a fAlpha term |
| `falpha_filings_scout` | SEC filings |
| `falpha_filings_scout_facts` | SEC XBRL company facts |
| `falpha_macro_desk` | Macro backdrop (FRED) |
| `falpha_fundamentals_desk` | Company profile and ratios (FMP) |
| `falpha_open_in_web` | Open fAlpha on the web |
<!-- tools:end -->

The table is generated from the live server's public catalog
(`https://agent.falpha.ai/mcp/catalog`) by `scripts/sync_tools.py`.

## Claude plugin

[plugin/](plugin) packages four skills that use the fAlpha connector: research a ticker, compare
names, screen a sector, and explain a move in the reading. Try it locally with
`claude --plugin-dir ./plugin`.

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

fAlpha is listed in the official MCP Registry as `ai.falpha/mcp`. `server.json` is the entry's
source.

## License

Everything in this repository (the recipes, the Claude plugin, the scripts and examples) is
MIT-licensed; see [LICENSE](LICENSE). Using the fAlpha service itself (the MCP server and API)
requires an fAlpha account and is governed by fAlpha's Terms of Service. The MIT license covers
this code, not fAlpha's data or service.
