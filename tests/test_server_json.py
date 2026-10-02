"""Offline checks of server.json against the official registry schema's rules
(https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json, read 2026-09-26),
and of the README tool-table splice. Run: python3 -m pytest -q tests
"""

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import sync_tools  # noqa: E402

SERVER = json.loads((ROOT / "server.json").read_text())


def test_required_fields_and_limits():
    assert SERVER["$schema"] == "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json"
    assert re.fullmatch(r"[a-zA-Z0-9.-]+/[a-zA-Z0-9._-]+", SERVER["name"])
    assert 3 <= len(SERVER["name"]) <= 200
    assert 1 <= len(SERVER["description"]) <= 100
    assert 1 <= len(SERVER["title"]) <= 100
    assert SERVER["version"] and len(SERVER["version"]) <= 255
    assert not re.search(r"[\^~<>=*]|\|\|", SERVER["version"]), "version ranges are rejected"


def test_name_is_in_the_dns_namespace_for_falpha_ai():
    # Domain auth for falpha.ai grants the reverse-DNS namespace ai.falpha/*.
    assert SERVER["name"].split("/")[0] == "ai.falpha"


def test_remote_is_the_production_streamable_http_endpoint():
    assert SERVER["remotes"] == [{"type": "streamable-http", "url": "https://agent.falpha.ai/mcp"}]
    assert "packages" not in SERVER


def test_icons_follow_the_schema():
    assert {i["theme"] for i in SERVER["icons"]} == {"light", "dark"}
    for icon in SERVER["icons"]:
        assert icon["src"].startswith("https://") and len(icon["src"]) <= 255
        assert icon["mimeType"] in {"image/png", "image/jpeg", "image/jpg", "image/svg+xml", "image/webp"}
        assert all(re.fullmatch(r"\d+x\d+|any", s) for s in icon["sizes"])


def test_description_makes_no_performance_or_advice_claim():
    text = (SERVER["description"] + " " + SERVER["title"]).lower()
    for word in ("alpha generation", "outperform", "beat the market", "buy", "sell", "guarantee", "profit"):
        assert word not in text


def test_readme_list_splice_replaces_only_the_marked_block():
    catalog = {"server": {"name": "fAlpha", "version": "2026.09.23"},
               "tools": [{"name": "falpha_x", "title": "X"}, {"name": "falpha_y", "annotations": {"title": "Y"}}]}
    table = sync_tools.render_table(catalog)
    assert "2 read-only tools, as listed by fAlpha version 2026.09.23." in table
    assert "- **falpha_x**: X" in table and "- **falpha_y**: Y" in table
    text = "intro\n<!-- tools:start -->\nold\n<!-- tools:end -->\noutro\n"
    out = sync_tools.splice(text, table)
    assert out.startswith("intro\n<!-- tools:start -->\n2 read-only") and out.endswith("<!-- tools:end -->\noutro\n")
    assert "old" not in out


def test_tool_list_line_takes_the_first_sentence_without_the_desk_prefix():
    catalog = {"tools": [{"name": "falpha_x", "title": "Signal card",
                          "description": "[Signal Desk] The model's reading on one ticker. For questions like 'x'."}]}
    assert "- **falpha_x**: Signal card. The model's reading on one ticker." in sync_tools.render_table(catalog)
