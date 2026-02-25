#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOOP_DIR="$ROOT/artifacts/loop"
MAIN_LOG="$LOOP_DIR/daemon.log"
SUP_LOG="$LOOP_DIR/supervisor.log"
PID_FILE="$LOOP_DIR/supervisor.pid"
HEARTBEAT="$LOOP_DIR/progress/heartbeat.json"

INTERVAL_SECONDS="${INTERVAL_SECONDS:-900}"
UNTIL_ARG="${UNTIL_ARG:-tomorrow}"
BASE_PATH="${BASE_PATH:-/valley-k-small}"
MODE="${MODE:-changed}"

mkdir -p "$LOOP_DIR" "$LOOP_DIR/progress"
echo $$ > "$PID_FILE"

calc_until_utc() {
  python3 - "$1" <<'PY'
from datetime import datetime, timedelta
import sys

text = (sys.argv[1] or "").strip().lower()
if text == "tomorrow":
    now = datetime.utcnow()
    target = (now + timedelta(days=1)).date().isoformat() + "T23:59:59"
    print(target)
elif text.endswith("z"):
    print(text[:-1])
else:
    print(text)
PY
}

to_epoch() {
  python3 - "$1" <<'PY'
from datetime import datetime
import sys

print(int(datetime.fromisoformat(sys.argv[1]).timestamp()))
PY
}

UTC_UNTIL="$(calc_until_utc "$UNTIL_ARG")"
UNTIL_EPOCH="$(to_epoch "$UTC_UNTIL")"

echo "{\"event\":\"supervisor_start\",\"pid\":$$,\"until\":\"${UTC_UNTIL}Z\",\"interval_seconds\":${INTERVAL_SECONDS}}" >>"$SUP_LOG"

while true; do
  NOW_EPOCH="$(date -u +%s)"
  if [[ "$NOW_EPOCH" -ge "$UNTIL_EPOCH" ]]; then
    echo "{\"event\":\"supervisor_stop\",\"reason\":\"until_reached\",\"time\":\"$(date -u +%FT%TZ)\"}" >>"$SUP_LOG"
    rm -f "$PID_FILE"
    exit 0
  fi

  echo "{\"event\":\"round_launch\",\"time\":\"$(date -u +%FT%TZ)\",\"mode\":\"$MODE\"}" >>"$SUP_LOG"
  set +e
  python3 -u "$ROOT/scripts/multiagent_optimize_loop.py" \
    --once \
    --interval-seconds "$INTERVAL_SECONDS" \
    --until "$UTC_UNTIL" \
    --base-path "$BASE_PATH" \
    --mode "$MODE" >>"$MAIN_LOG" 2>&1
  RC=$?
  set -e

  echo "{\"event\":\"round_exit\",\"time\":\"$(date -u +%FT%TZ)\",\"rc\":$RC}" >>"$SUP_LOG"

  if [[ -f "$HEARTBEAT" ]]; then
    cp "$HEARTBEAT" "$LOOP_DIR/progress/heartbeat.last.json" || true
  fi

  sleep "$INTERVAL_SECONDS"
done
