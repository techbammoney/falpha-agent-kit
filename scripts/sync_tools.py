"""Rewrite the README's tool table from the live server's public catalog, so it cannot drift.

    python3 scripts/sync_tools.py            # rewrite README.md in place
    python3 scripts/sync_tools.py --check    # exit 1 when README.md is out of date

Standard library only. Reads https://agent.falpha.ai/mcp/catalog (public, read-only).
"""

import json
import pathlib
import sys
import urllib.request

CATALOG_URL = "https://agent.falpha.ai/mcp/catalog"
README = pathlib.Path(__file__).resolve().parent.parent / "README.md"
START, END = "<!-- tools:start -->", "<!-- tools:end -->"


def fetch_catalog(url=CATALOG_URL):
    with urllib.request.urlopen(url, timeout=30) as resp:  # noqa: S310 (fixed https URL)
        return json.load(resp)


def render_table(catalog):
    server = catalog.get("server") or {}
    tools = catalog.get("tools") or []
    lines = [
        f"{len(tools)} read-only tools, as listed by {server.get('name', 'the server')} "
        f"version {server.get('version', 'unknown')}.",
        "",
        "| Tool | What it returns |",
        "|---|---|",
    ]
    for tool in tools:
        title = tool.get("title") or (tool.get("annotations") or {}).get("title") or ""
        lines.append(f"| `{tool['name']}` | {title} |")
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
            print("README.md tool table is out of date; run scripts/sync_tools.py")
            return 1
        print("README.md tool table matches the live catalog")
        return 0
    README.write_text(updated)
    print("README.md tool table updated")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
