#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PID_FILE="$ROOT/artifacts/loop/daemon.pid"
LOG_FILE="$ROOT/artifacts/loop/daemon.log"

start_loop() {
  mkdir -p "$ROOT/artifacts/loop"
  if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" >/dev/null 2>&1; then
    echo "Loop already running with PID $(cat "$PID_FILE")"
    exit 0
  fi

  nohup python3 "$ROOT/scripts/multiagent_optimize_loop.py" \
    --interval-seconds 900 \
    --until tomorrow \
    --base-path "/valley-k-small" \
    >"$LOG_FILE" 2>&1 &

  echo $! > "$PID_FILE"
  echo "Started loop PID $(cat "$PID_FILE")"
  echo "Log: $LOG_FILE"
}

stop_loop() {
  if [[ ! -f "$PID_FILE" ]]; then
    echo "No PID file found."
    exit 0
  fi
  pid="$(cat "$PID_FILE")"
  if kill -0 "$pid" >/dev/null 2>&1; then
    kill "$pid"
    echo "Stopped PID $pid"
  else
    echo "PID $pid not running"
  fi
  rm -f "$PID_FILE"
}

status_loop() {
  if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" >/dev/null 2>&1; then
    echo "running pid=$(cat "$PID_FILE")"
  else
    echo "not-running"
  fi
  if [[ -f "$ROOT/artifacts/loop/progress/latest.json" ]]; then
    echo "latest:"
    cat "$ROOT/artifacts/loop/progress/latest.json"
  fi
}

case "${1:-}" in
  start) start_loop ;;
  stop) stop_loop ;;
  status) status_loop ;;
  *)
    echo "Usage: $0 {start|stop|status}"
    exit 1
    ;;
esac
