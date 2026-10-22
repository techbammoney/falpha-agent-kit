#!/usr/bin/env bash
# Build the ChatGPT plugin upload: codex-plugin/ (.codex-plugin/plugin.json, .mcp.json, assets) plus the same
# skills the Claude plugin ships (plugin/skills), so one set of skills serves both directories.
#
#   scripts/build-codex-plugin.sh      # writes dist/falpha-codex-plugin.zip
set -euo pipefail
cd "$(dirname "$0")/.."
out=dist/falpha-codex-plugin.zip
stage=$(mktemp -d)
trap 'rm -rf "$stage"' EXIT
mkdir "$stage/.codex-plugin"
cp codex-plugin/.codex-plugin/plugin.json "$stage/.codex-plugin/"
cp codex-plugin/.mcp.json "$stage/"
cp -R codex-plugin/assets "$stage/assets"
cp -R plugin/skills "$stage/skills"
mkdir -p dist
rm -f "$out"
(cd "$stage" && zip -qr -X "$OLDPWD/$out" .)
echo "wrote $out"
unzip -l "$out" | tail -n +4 | sed '$d' | sed '$d' | awk '{print "  " $4}'
