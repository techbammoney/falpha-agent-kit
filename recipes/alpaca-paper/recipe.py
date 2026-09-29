"""fAlpha x Alpaca paper recipe.

A small agent that reads fAlpha's research tools, makes its own go/no-go, and trades on an
Alpaca PAPER account through Alpaca's own MCP server. fAlpha supplies read-only research and
never places orders; this script (your agent) does, on your paper account only. Every decision
is logged with the fAlpha evidence it used, in a hash-chained file anyone can re-check.

    export FALPHA_TOKEN=falpha_pat_...                  # falpha.ai/account#apikey
    export ALPACA_API_KEY=... ALPACA_SECRET_KEY=...     # Alpaca PAPER keys
    python recipe.py --tickers NVDA,AAPL,MSFT           # decide and log; no orders
    python recipe.py --tickers NVDA,AAPL,MSFT --execute # also place paper orders for "buy"
    python recipe.py --verify-log decisions.jsonl       # re-check the hash chain

The go/no-go rule here is deliberately plain (long-only, a threshold on fAlpha's equity
indicator, skip stale or missing data). It is an example of an agent's own decision, not a
strategy, and nothing about it is claimed to make money. Replace `decide` with your own agent.
"""

import argparse
import asyncio
import hashlib
import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

FALPHA_MCP_URL = "https://agent.falpha.ai/mcp"
CARD_TOOL = "falpha_signal_desk_card"
ORDER_TOOL = "place_stock_order"


# --------------------------------------------------------------------------- evidence


@dataclass
class Evidence:
    """What the agent read from fAlpha for one ticker, exactly as the tool returned it."""

    ticker: str
    status: str
    horizon: str
    regime: str
    ei: Optional[float] = None
    signal_date: Optional[str] = None
    data_as_of: Optional[str] = None
    stale: Optional[bool] = None
    dominant_driver: Optional[str] = None
    reason: Optional[str] = None


def evidence_from_card(ticker: str, horizon: str, regime: str, card: Dict[str, Any]) -> Evidence:
    """Map a falpha_signal_desk_card result to Evidence. Unknown shapes become status='error'."""
    if not isinstance(card, dict):
        return Evidence(ticker, "error", horizon, regime, reason="unreadable tool result")
    ei = card.get("ei")
    return Evidence(
        ticker=ticker.upper(),
        status=str(card.get("status") or "error"),
        horizon=card.get("horizon") or horizon,
        regime=card.get("regime") or regime,
        ei=float(ei) if isinstance(ei, (int, float)) and not isinstance(ei, bool) else None,
        signal_date=card.get("signal_date"),
        data_as_of=card.get("data_as_of"),
        stale=card.get("stale") if isinstance(card.get("stale"), bool) else None,
        dominant_driver=card.get("dominant_driver"),
        reason=card.get("reason") or card.get("message") or card.get("error_code"),
    )


# --------------------------------------------------------------------------- the agent's decision


def decide(ev: Evidence, min_ei: float) -> Tuple[str, str]:
    """The agent's own go/no-go: ('buy' | 'skip', why). Long-only; skips anything uncertain."""
    if ev.status != "ok":
        return "skip", f"fAlpha has no reading ({ev.reason or ev.status})"
    if ev.stale is True:
        return "skip", f"fAlpha marks this data stale (data as of {ev.data_as_of})"
    if ev.ei is None:
        return "skip", "no equity indicator in the result"
    if ev.ei >= min_ei:
        return "buy", f"EI {ev.ei:+.2f} >= {min_ei:.2f} ({ev.horizon}, {ev.regime})"
    if ev.ei <= -min_ei:
        return "skip", f"EI {ev.ei:+.2f} leans down; this recipe is long-only"
    return "skip", f"EI {ev.ei:+.2f} is inside +/-{min_ei:.2f}"


# --------------------------------------------------------------------------- the decision log


class DecisionLog:
    """Append-only JSONL where each line carries the hash of the previous one."""

    GENESIS = "0" * 64

    def __init__(self, path: str):
        self.path = path

    @staticmethod
    def _digest(prev: str, record: Dict[str, Any]) -> str:
        body = json.dumps(record, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256((prev + body).encode("utf-8")).hexdigest()

    def last_hash(self) -> str:
        if not os.path.exists(self.path):
            return self.GENESIS
        last = None
        with open(self.path) as fh:
            for line in fh:
                if line.strip():
                    last = line
        return json.loads(last)["hash"] if last else self.GENESIS

    def append(self, record: Dict[str, Any]) -> Dict[str, Any]:
        prev = self.last_hash()
        entry = {"record": record, "prev_hash": prev, "hash": self._digest(prev, record)}
        with open(self.path, "a") as fh:
            fh.write(json.dumps(entry, sort_keys=True, default=str) + "\n")
        return entry

    def verify(self) -> Tuple[bool, str]:
        prev = self.GENESIS
        n = 0
        with open(self.path) as fh:
            for n, line in enumerate((l for l in fh if l.strip()), start=1):
                entry = json.loads(line)
                if entry["prev_hash"] != prev:
                    return False, f"line {n}: prev_hash does not match line {n - 1}"
                if entry["hash"] != self._digest(prev, entry["record"]):
                    return False, f"line {n}: record was changed after it was written"
                prev = entry["hash"]
        return True, f"{n} decisions, chain intact"


# --------------------------------------------------------------------------- the two servers


def alpaca_server_env(base_env: Dict[str, str]) -> Dict[str, str]:
    """Environment for the Alpaca MCP server this script starts: paper trading is forced on,
    and only the account and trading toolsets are exposed."""
    env = dict(base_env)
    env["ALPACA_PAPER_TRADE"] = "true"
    env["ALPACA_TOOLSETS"] = "account,trading"
    return env


def _result_data(result: Any) -> Any:
    data = getattr(result, "structuredContent", None)
    if data is not None:
        return data
    for block in getattr(result, "content", None) or []:
        text = getattr(block, "text", None)
        if text:
            try:
                return json.loads(text)
            except ValueError:
                return {"status": "error", "message": text[:300]}
    return {"status": "error", "message": "empty tool result"}


async def read_cards(url: str, token: str, tickers, horizon: str, regime: str) -> Dict[str, Any]:
    """Call falpha_signal_desk_card for each ticker over fAlpha's MCP (read-only)."""
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client

    cards = {}
    async with streamablehttp_client(url, headers={"Authorization": f"Bearer {token}"}) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            for ticker in tickers:
                result = await session.call_tool(CARD_TOOL, {"ticker": ticker, "horizon": horizon, "regime": regime})
                cards[ticker] = _result_data(result)
    return cards


async def place_orders(orders, command: str = "alpaca-mcp-server") -> Dict[str, Any]:
    """Place paper market orders through Alpaca's MCP server started over stdio."""
    from mcp import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client

    params = StdioServerParameters(command=command, args=[], env=alpaca_server_env(dict(os.environ)))
    results = {}
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            for order in orders:
                result = await session.call_tool(ORDER_TOOL, order)
                results[order["symbol"]] = _result_data(result)
    return results


# --------------------------------------------------------------------------- run


def order_for(ticker: str, notional: str, decided_at: str) -> Dict[str, Any]:
    """A paper market buy with an idempotency key, so a retried run cannot double-buy."""
    key = hashlib.sha256(f"falpha-recipe|{ticker}|{decided_at}".encode()).hexdigest()[:32]
    return {"symbol": ticker, "side": "buy", "notional": notional, "type": "market",
            "time_in_force": "day", "client_order_id": f"falpha-{key}"}


def run(tickers, cards: Dict[str, Any], horizon: str, regime: str, min_ei: float,
        log: DecisionLog, decided_at: str, notional: str = "100"):
    """Decide for every ticker and log each decision. Returns the paper orders to place."""
    orders = []
    for ticker in tickers:
        ev = evidence_from_card(ticker, horizon, regime, cards.get(ticker))
        action, why = decide(ev, min_ei)
        record = {"decided_at": decided_at, "ticker": ev.ticker, "action": action, "why": why,
                  "evidence": asdict(ev), "source": f"fAlpha MCP {CARD_TOOL}"}
        if action == "buy":
            record["order"] = order_for(ev.ticker, notional, decided_at)
            orders.append(record["order"])
        log.append(record)
        print(f"{ev.ticker:6s} {action:4s}  {why}")
    return orders


def main(argv) -> int:
    ap = argparse.ArgumentParser(description="fAlpha x Alpaca paper recipe")
    ap.add_argument("--tickers", help="comma-separated US tickers, e.g. NVDA,AAPL")
    ap.add_argument("--horizon", default="hp15d", choices=["hp5d", "hp15d", "hp2m"])
    ap.add_argument("--regime", default="neutral", choices=["neutral", "bull", "bear"])
    ap.add_argument("--min-ei", type=float, default=0.6)
    ap.add_argument("--notional", default="100", help="dollars per paper buy (default 100)")
    ap.add_argument("--log", default="decisions.jsonl")
    ap.add_argument("--execute", action="store_true", help="place paper orders for 'buy' decisions")
    ap.add_argument("--verify-log", metavar="PATH", help="re-check a decision log's hash chain and exit")
    args = ap.parse_args(argv)

    if args.verify_log:
        ok, msg = DecisionLog(args.verify_log).verify()
        print(("OK: " if ok else "BROKEN: ") + msg)
        return 0 if ok else 1
    if not args.tickers:
        ap.error("--tickers is required")
    token = os.environ.get("FALPHA_TOKEN")
    if not token:
        print("Set FALPHA_TOKEN to a fAlpha personal access token (falpha.ai/account#apikey).")
        return 2
    if args.execute and not (os.environ.get("ALPACA_API_KEY") and os.environ.get("ALPACA_SECRET_KEY")):
        print("Set ALPACA_API_KEY and ALPACA_SECRET_KEY (paper keys) to use --execute.")
        return 2

    tickers = [t.strip().upper() for t in args.tickers.split(",") if t.strip()]
    decided_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    url = os.environ.get("FALPHA_MCP_URL", FALPHA_MCP_URL)
    try:
        cards = asyncio.run(read_cards(url, token, tickers, args.horizon, args.regime))
    except Exception as e:  # noqa: BLE001 - say what failed; no decision is made on no data
        status = getattr(getattr(e, "response", None), "status_code", None)
        for inner in getattr(e, "exceptions", ()) or ():
            status = status or getattr(getattr(inner, "response", None), "status_code", None)
        if status == 401:
            print("fAlpha refused the token (HTTP 401): check FALPHA_TOKEN.")
        else:
            print(f"Could not read fAlpha ({type(e).__name__}: {e}). No decisions made.")
        return 1
    log = DecisionLog(args.log)
    orders = run(tickers, cards, args.horizon, args.regime, args.min_ei, log, decided_at, args.notional)

    if orders and args.execute:
        results = asyncio.run(place_orders(orders))
        for symbol, result in results.items():
            log.append({"decided_at": decided_at, "ticker": symbol, "action": "order_result",
                        "result": result, "paper": True})
            print(f"{symbol:6s} paper order: {json.dumps(result)[:200]}")
    elif orders:
        print(f"{len(orders)} buy decision(s); dry run, no orders placed (use --execute).")
    ok, msg = log.verify()
    print(f"log {args.log}: {msg}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
