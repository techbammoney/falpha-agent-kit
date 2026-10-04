"""The ChatGPT plugin manifest (openai-plugin/plugin.json) against OpenAI's published limits."""

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "openai-plugin"
MANIFEST = json.loads((PLUGIN / "plugin.json").read_text())
OPENAI = MANIFEST["extensions"]["com.openai"]
INTERFACE = OPENAI["interface"]
README_TOOLS = set(re.findall(r"^- \*\*(falpha_[a-z_]+)\*\*", (ROOT / "README.md").read_text(), re.M))


def test_required_fields_and_limits():
    assert MANIFEST["$schema"] == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
    assert re.fullmatch(r"[a-z0-9-]{1,64}", MANIFEST["name"])
    assert re.fullmatch(r"\d+\.\d+\.\d+", MANIFEST["version"])
    assert 0 < len(MANIFEST["author"]["name"]) <= 120
    assert len(INTERFACE["displayName"]) <= 30
    assert len(INTERFACE["shortDescription"]) <= 30
    assert len(INTERFACE["longDescription"]) <= 4000
    assert len(INTERFACE["developerName"]) <= 80
    assert len(INTERFACE["capabilities"]) <= 20 and all(len(c) <= 120 for c in INTERFACE["capabilities"])
    for key in ("websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL"):
        assert INTERFACE[key].startswith("https://") and len(INTERFACE[key]) <= 1024


def test_referenced_assets_exist():
    for key in ("logo", "logoDark", "composerIcon", "composerIconDark"):
        assert (PLUGIN / INTERFACE[key]).is_file(), key


def test_test_cases_name_only_real_tools():
    cases = OPENAI["review"]["test_cases"]
    assert len(cases["positive"]) == 5 and len(cases["negative"]) == 3
    assert len(README_TOOLS) >= 17
    for case in cases["positive"]:
        assert case["description"] and case["prompt"] and case["expected_behavior"]
        for tool in (t.strip() for t in case["tools_triggered"].split(",")):
            assert tool in README_TOOLS, tool
    for case in cases["negative"]:
        assert case["description"] and case["prompt"]


def test_no_purchase_or_advice_wording_in_the_listing():
    text = json.dumps(INTERFACE).lower()
    for word in ("upgrade", "pricing", "subscribe", "free trial", "outperform", "guarantee"):
        assert word not in text, word
    # "sell-side" (analyst coverage) is a description, not advice.
    assert not re.search(r"\b(buy|sell)\b(?!-side)", text)
    assert OPENAI["review"]["commerce"] is False


def test_mcp_config_points_at_the_hosted_server():
    servers = json.loads((PLUGIN / "mcp.json").read_text())["mcpServers"]
    assert list(servers) == ["falpha"]
    assert servers["falpha"]["url"] == "https://agent.falpha.ai/mcp"
