#!/usr/bin/env bash
# Add fAlpha to YOUR Composio project as a custom MCP toolkit, using Composio's "Custom MCP"
# (experimental; https://docs.composio.dev/docs/extending-sessions/custom-mcp).
#
#   COMPOSIO_API_KEY=... scripts/composio-register.sh [oauth|api_key]     # default: oauth
#
#   oauth    each user approves read access on falpha.ai (the same consent as Claude and ChatGPT);
#            Composio registers itself with fAlpha's OAuth server (dynamic client registration).
#   api_key  each user pastes a fAlpha personal access token (falpha_pat_...), sent as a Bearer token.
#
# Composio cannot change a toolkit's URL or auth mode after registration: delete and re-register
# to switch. Or register under another name: SLUG=FALPHA_KEY scripts/composio-register.sh api_key
# gives CUSTOM_FALPHA_KEY. The toolkit is scoped to your Composio project; it is not a public catalog listing.
set -euo pipefail

: "${COMPOSIO_API_KEY:?Set COMPOSIO_API_KEY to your Composio project API key}"
MODE="${1:-oauth}"
case "$MODE" in
  oauth)
    AUTH='[{"mode":"DCR_OAUTH","discovery_url":"https://agent.falpha.ai/.well-known/oauth-authorization-server"}]'
    ;;
  api_key)
    AUTH='[{"mode":"API_KEY","headers":{"Authorization":"Bearer {{generic_api_key}}"}}]'
    ;;
  *)
    echo "usage: $0 [oauth|api_key]" >&2
    exit 2
    ;;
esac

curl -sS --fail-with-body --request POST \
  --url https://backend.composio.dev/api/v3.1/custom/toolkits/upsert \
  --header "x-api-key: ${COMPOSIO_API_KEY}" \
  --header "Content-Type: application/json" \
  --data "{\"slug\":\"${SLUG:-FALPHA}\",\"toolkit_config\":{\"name\":\"fAlpha\",\"app_url\":\"https://agent.falpha.ai/mcp\",\"auth_schemes\":${AUTH}}}"
echo
echo "Registered as CUSTOM_${SLUG:-FALPHA}. Use it in a session:"
echo "  session = composio.sessions.create(user_id=\"...\", toolkits=[\"CUSTOM_${SLUG:-FALPHA}\"])"
