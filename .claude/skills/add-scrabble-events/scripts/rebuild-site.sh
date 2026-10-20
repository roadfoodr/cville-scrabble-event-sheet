#!/usr/bin/env bash
# Trigger a Render deploy to rebuild cvillescrabble.club
# The deploy hook URL (which contains a secret key) lives in the gitignored .env at the repo root.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
if [[ -f "$repo_root/.env" ]]; then
    set -a
    source "$repo_root/.env"
    set +a
fi

if [[ -z "${RENDER_DEPLOY_HOOK:-}" ]]; then
    echo "RENDER_DEPLOY_HOOK is not set. Copy .env.example to .env and fill it in." >&2
    exit 1
fi

curl -s -X POST "$RENDER_DEPLOY_HOOK"
