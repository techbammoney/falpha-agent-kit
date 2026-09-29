"""Offline tests for the fAlpha x Alpaca paper recipe: no fAlpha, no Alpaca, no network.

    python3 -m pytest -q recipes/alpaca-paper
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(__file__))

import recipe  # noqa: E402

OK_CARD = {"status": "ok", "ticker": "NVDA", "horizon": "hp15d", "regime": "neutral", "ei": 0.71,
           "signal_date": "2026-09-25", "data_as_of": "2026-09-25", "stale": False, "dominant_driver": "price"}


def card(**over):
    return {**OK_CARD, **over}


def test_evidence_keeps_what_the_tool_returned():
    ev = recipe.evidence_from_card("nvda", "hp15d", "neutral", card())
    assert (ev.ticker, ev.status, ev.ei, ev.data_as_of, ev.stale) == ("NVDA", "ok", 0.71, "2026-09-25", False)
    missing = recipe.evidence_from_card("ZZZZ", "hp15d", "neutral",
                                        {"status": "no_data", "reason": "ticker_not_covered"})
    assert (missing.status, missing.ei, missing.reason) == ("no_data", None, "ticker_not_covered")
    assert recipe.evidence_from_card("X", "hp15d", "neutral", None).status == "error"
    assert recipe.evidence_from_card("X", "hp15d", "neutral", card(ei=True)).ei is None  # a bool is not a score


@pytest.mark.parametrize("over, action, why_part", [
    ({}, "buy", "EI +0.71 >= 0.60"),
    ({"ei": -0.8}, "skip", "long-only"),
    ({"ei": 0.3}, "skip", "inside +/-0.60"),
    ({"stale": True}, "skip", "stale"),
    ({"status": "no_data", "reason": "no_signal"}, "skip", "no reading (no_signal)"),
    ({"ei": None}, "skip", "no equity indicator"),
])
def test_the_agent_decides_long_only_and_skips_anything_uncertain(over, action, why_part):
    got_action, why = recipe.decide(recipe.evidence_from_card("NVDA", "hp15d", "neutral", card(**over)), 0.6)
    assert got_action == action and why_part in why


def test_the_log_chain_verifies_and_catches_an_edit(tmp_path):
    path = str(tmp_path / "decisions.jsonl")
    log = recipe.DecisionLog(path)
    first = log.append({"ticker": "NVDA", "action": "buy"})
    second = log.append({"ticker": "AAPL", "action": "skip"})
    assert first["prev_hash"] == recipe.DecisionLog.GENESIS and second["prev_hash"] == first["hash"]
    assert log.verify() == (True, "2 decisions, chain intact")
    lines = open(path).read().splitlines()
    tampered = json.loads(lines[0])
    tampered["record"]["action"] = "skip"
    lines[0] = json.dumps(tampered, sort_keys=True)
    open(path, "w").write("\n".join(lines) + "\n")
    ok, msg = log.verify()
    assert not ok and "line 1" in msg


def test_the_alpaca_server_is_always_started_in_paper_mode():
    env = recipe.alpaca_server_env({"ALPACA_PAPER_TRADE": "false", "ALPACA_TOOLSETS": "", "PATH": "/bin"})
    assert env["ALPACA_PAPER_TRADE"] == "true"
    assert env["ALPACA_TOOLSETS"] == "account,trading"
    assert env["PATH"] == "/bin"


def test_a_dry_run_logs_every_ticker_and_orders_only_the_buys(tmp_path):
    log = recipe.DecisionLog(str(tmp_path / "d.jsonl"))
    cards = {"NVDA": card(), "AAPL": card(ticker="AAPL", ei=0.2), "ZZZZ": {"status": "no_data", "reason": "ticker_not_covered"}}
    orders = recipe.run(["NVDA", "AAPL", "ZZZZ"], cards, "hp15d", "neutral", 0.6, log, "2026-09-26T14:00:00Z", "250")
    assert [o["symbol"] for o in orders] == ["NVDA"]
    order = orders[0]
    assert (order["side"], order["type"], order["notional"], order["time_in_force"]) == ("buy", "market", "250", "day")
    assert order == recipe.order_for("NVDA", "250", "2026-09-26T14:00:00Z")  # same run, same idempotency key
    assert order["client_order_id"] != recipe.order_for("NVDA", "250", "2026-09-27T14:00:00Z")["client_order_id"]
    entries = [json.loads(l) for l in open(log.path)]
    assert [e["record"]["action"] for e in entries] == ["buy", "skip", "skip"]
    assert entries[0]["record"]["evidence"]["data_as_of"] == "2026-09-25"
    assert log.verify()[0]


def test_result_data_prefers_structured_content_and_falls_back_to_text():
    class R:
        structuredContent = {"status": "ok"}
        content = []

    class T:
        structuredContent = None

        class B:
            text = '{"status": "no_data"}'

        content = [B()]

    assert recipe._result_data(R()) == {"status": "ok"}
    assert recipe._result_data(T()) == {"status": "no_data"}
