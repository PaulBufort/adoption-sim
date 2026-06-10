#!/usr/bin/env bash
# One-click launcher for the adoption-sim Streamlit demo.
#   macOS: double-click this file in Finder (opens a Terminal window).
#   Linux: run it from a shell, or double-click where your desktop allows it.
# First run creates the Python environment (one-time, ~1-3 min); afterwards the
# demo is up in a few seconds. Close the window or press Ctrl+C to stop it.
# ALL DATA SHOWN BY THE DEMO IS SYNTHETIC (docs/limitations.md).
set -euo pipefail
cd "$(dirname "$0")"

PORT="${ADOPTION_SIM_PORT:-8501}"
URL="http://localhost:${PORT}"

health() { curl -s --max-time 2 "${URL}/_stcore/health" 2>/dev/null || true; }

open_browser() {
  [ "${ADOPTION_SIM_NO_BROWSER:-0}" = "1" ] && return 0
  if command -v open >/dev/null 2>&1; then open "$URL"
  elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$URL"
  else echo "Open ${URL} in your browser."
  fi
}

if [ "$(health)" = "ok" ]; then
  echo "Demo already running at ${URL} — opening it."
  open_browser
  exit 0
fi

PY=".venv/bin/python"
if [ ! -x "$PY" ]; then
  echo "First run: creating the Python environment (one-time, ~1-3 min)…"
  python3 -m venv .venv
  "$PY" -m pip install --quiet --upgrade pip
  "$PY" -m pip install --quiet -r requirements.txt -c constraints.txt
fi
if ! "$PY" -c "import streamlit" >/dev/null 2>&1; then
  echo "Installing demo dependencies…"
  "$PY" -m pip install --quiet -r requirements.txt -c constraints.txt
fi

echo "Starting the demo at ${URL}  (close this window or press Ctrl+C to stop)"
"$PY" -m streamlit run demo/app.py --server.port "$PORT" &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT INT TERM

for _ in $(seq 1 60); do
  [ "$(health)" = "ok" ] && break
  sleep 1
done
if [ "$(health)" = "ok" ]; then
  open_browser
else
  echo "The server did not become healthy after 60 s — see the messages above."
fi
wait "$SERVER_PID"
