# Alpaca paper-trading recipe

A small agent you can read in one sitting. It:

1. **Reads** fAlpha's signal card for each ticker over fAlpha's MCP server (read-only).
2. **Decides** go or no-go with its own rule: long-only, a threshold on fAlpha's equity
   indicator, and skip anything stale or missing.
3. **Trades** on your Alpaca **paper** account through Alpaca's own MCP server
   (`alpaca-mcp-server`). The script forces `ALPACA_PAPER_TRADE=true` for the server it
   starts; there is no live-trading path.
4. **Logs** every decision with the fAlpha evidence it used, in `decisions.jsonl`. Each line
   carries the hash of the previous one, so an edit after the fact is detectable.

fAlpha never places orders. This script does, on your paper account. The rule is an example of
an agent's own decision, not a strategy, and nothing about it is claimed to make money. fAlpha's
signals are model output, not investment advice.

## Setup

```bash
pip install -r requirements.txt
export FALPHA_TOKEN=falpha_pat_...                # https://falpha.ai/account#apikey
export ALPACA_API_KEY=... ALPACA_SECRET_KEY=...   # Alpaca PAPER keys
```

## Run

```bash
python recipe.py --tickers NVDA,AAPL,MSFT                 # decide and log; no orders
python recipe.py --tickers NVDA,AAPL,MSFT --execute       # also place paper orders for "buy"
python recipe.py --tickers NVDA --horizon hp5d --min-ei 0.7 --notional 250
python recipe.py --verify-log decisions.jsonl             # re-check the hash chain
```

Each buy is a paper market order for `--notional` dollars, sent with a `client_order_id`
derived from the ticker and the decision time, so a retried run cannot double-buy.

## Make it yours

Replace `decide(evidence, min_ei)` with your own agent: another rule, a model, or an LLM call.
It receives exactly what fAlpha returned:
- `ei`, `horizon`, `regime`;
- `signal_date`, `data_as_of`, `stale`;
- `dominant_driver`;
- `status`, which is `no_data` with a `reason` for uncovered tickers.

It returns `("buy" | "skip", why)`, and the rest of the file handles the logging and the paper
order.

## Tests

```bash
python -m pytest -q     # offline: no fAlpha, no Alpaca, no network
```
