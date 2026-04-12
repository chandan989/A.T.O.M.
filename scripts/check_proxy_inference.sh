#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ATOM_SERVER_URL="${ATOM_SERVER_URL:-http://127.0.0.1:8000}"
SERVER_PID=""

cleanup() {
  if [[ -n "${SERVER_PID}" ]]; then
    kill "${SERVER_PID}" >/dev/null 2>&1 || true
    wait "${SERVER_PID}" 2>/dev/null || true
  fi
}

trap cleanup EXIT

require_env() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    echo "[ERROR] Missing required environment variable: ${name}" >&2
    exit 1
  fi
}

require_env "API_BASE_URL"
require_env "API_KEY"

if [[ -z "${MODEL_NAME:-}" ]]; then
  echo "[WARN] MODEL_NAME is not set. inference.py will use its default model." >&2
fi

echo "[INFO] Repo root: ${ROOT_DIR}" >&2
echo "[INFO] Proxy base URL: ${API_BASE_URL}" >&2
echo "[INFO] ATOM server URL: ${ATOM_SERVER_URL}" >&2

echo "[INFO] Checking LiteLLM proxy reachability..." >&2
curl -fsS \
  -H "Authorization: Bearer ${API_KEY}" \
  "${API_BASE_URL%/}/models" >/dev/null

if ! curl -fsS "${ATOM_SERVER_URL%/}/health" >/dev/null 2>&1; then
  echo "[INFO] Local ATOM server is not running. Starting one for the preflight check..." >&2
  (
    cd "${ROOT_DIR}"
    python -m uvicorn server.app:app --host 127.0.0.1 --port 8000
  ) >/tmp/atom_proxy_preflight.log 2>&1 &
  SERVER_PID="$!"

  for _ in {1..30}; do
    if curl -fsS "${ATOM_SERVER_URL%/}/health" >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done

  if ! curl -fsS "${ATOM_SERVER_URL%/}/health" >/dev/null 2>&1; then
    echo "[ERROR] Failed to start the local ATOM server. Check /tmp/atom_proxy_preflight.log" >&2
    exit 1
  fi
fi

echo "[INFO] Running inference.py with the injected proxy configuration..." >&2
cd "${ROOT_DIR}"
python inference.py
