#!/usr/bin/env bash
# Build the ChatGPT plugin upload: openai-plugin/ (manifest, MCP config, assets) plus the same
# skills the Claude plugin ships (plugin/skills), so one set of skills serves both directories.
#
#   scripts/build-openai-plugin.sh      # writes dist/falpha-openai-plugin.zip
set -euo pipefail
cd "$(dirname "$0")/.."
out=dist/falpha-openai-plugin.zip
stage=$(mktemp -d)
trap 'rm -rf "$stage"' EXIT
cp openai-plugin/plugin.json openai-plugin/mcp.json "$stage/"
cp -R openai-plugin/assets "$stage/assets"
cp -R plugin/skills "$stage/skills"
mkdir -p dist
rm -f "$out"
(cd "$stage" && zip -qr -X "$OLDPWD/$out" .)
echo "wrote $out"
unzip -l "$out" | tail -n +4 | sed '$d' | sed '$d' | awk '{print "  " $4}'
