"""Rewrite the README's tool list from the live server's public catalog, so it cannot drift.

    python3 scripts/sync_tools.py            # rewrite README.md in place
    python3 scripts/sync_tools.py --check    # exit 1 when README.md is out of date

Standard library only. Reads https://agent.falpha.ai/mcp/catalog (public, read-only).
"""

import json
import re
import pathlib
import sys
import urllib.request

CATALOG_URL = "https://agent.falpha.ai/mcp/catalog"
README = pathlib.Path(__file__).resolve().parent.parent / "README.md"
START, END = "<!-- tools:start -->", "<!-- tools:end -->"


def fetch_catalog(url=CATALOG_URL):
    with urllib.request.urlopen(url, timeout=30) as resp:  # noqa: S310 (fixed https URL)
        return json.load(resp)


def first_sentence(description):
    """The description's first sentence, without the "[Desk name] " prefix the server adds."""
    text = re.sub(r"^\[[^\]]*\]\s*", "", (description or "").strip())
    match = re.match(r"(.+?[.!?])(\s|$)", text)
    return (match.group(1) if match else text).strip()


def render_table(catalog):
    """A plain list, one tool per line: directory crawlers (mcp.so) read lists, not tables."""
    server = catalog.get("server") or {}
    tools = catalog.get("tools") or []
    lines = [
        f"{len(tools)} read-only tools, as listed by {server.get('name', 'the server')} "
        f"version {server.get('version', 'unknown')}.",
        "",
    ]
    for tool in tools:
        title = tool.get("title") or (tool.get("annotations") or {}).get("title") or ""
        sentence = first_sentence(tool.get("description"))
        # The shape directory crawlers are known to read (mcp.so detects it on other listings):
        # the bold tool name on its own line, then indented Title and Description lines.
        lines.append(f"- **{tool['name']}**")
        if title:
            lines.append(f"  - Title: {title}")
        if sentence:
            lines.append(f"  - Description: {sentence}")
    return "\n".join(lines)


def splice(text, table):
    if START not in text or END not in text:
        raise SystemExit(f"README.md must contain {START} and {END}")
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    return f"{head}{START}\n{table}\n{END}{tail}"


def main(argv):
    table = render_table(fetch_catalog())
    current = README.read_text()
    updated = splice(current, table)
    if "--check" in argv:
        if updated != current:
            print("README.md tool list is out of date; run scripts/sync_tools.py")
            return 1
        print("README.md tool list matches the live catalog")
        return 0
    README.write_text(updated)
    print("README.md tool list updated")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
