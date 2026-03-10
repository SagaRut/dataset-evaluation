#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="Benchmark-Projects"
LOG_FILE="install_benchmark.log"

mkdir -p "$TARGET_DIR"
: > "$LOG_FILE"

LOG_FILE="$(cd "$(dirname "$LOG_FILE")" && pwd)/$(basename "$LOG_FILE")"

run_logged () {
  local step="$1"; shift
  echo "-> $step..." | tee -a "$LOG_FILE"
  if ! "$@" >>"$LOG_FILE" 2>&1; then
    echo "!! $step failed (see $LOG_FILE)" | tee -a "$LOG_FILE"
    echo "---- last 40 log lines ----" | tee -a "$LOG_FILE"
    tail -n 40 "$LOG_FILE" | tee -a "$LOG_FILE"
    echo "---------------------------" | tee -a "$LOG_FILE"
    return 1
  fi
}

for dest in "$TARGET_DIR"/*; do
  [[ -d "$dest" ]] || continue
  name=$(basename "$dest")

  echo "==== $name ====" | tee -a "$LOG_FILE"
  echo "DIR: $dest" | tee -a "$LOG_FILE"

  if [[ ! -f "$dest/package.json" ]]; then
    echo "!! no package.json in $dest, skipping" | tee -a "$LOG_FILE"
    continue
  fi

  pushd "$dest" >/dev/null

  if [[ -f package-lock.json ]]; then
    run_logged "npm ci" npm ci || {
      popd >/dev/null
      echo "!! npm ci failed for $name" | tee -a "$LOG_FILE"
      continue
    }
  else
    run_logged "npm install" npm install || {
      popd >/dev/null
      echo "!! npm install failed for $name" | tee -a "$LOG_FILE"
      continue
    }
  fi

  if node -e 'process.exit((require("./package.json").scripts||{}).build?0:1)' ; then
    run_logged "npm run build" npm run build || true
  elif [[ -f tsconfig.json ]]; then
    run_logged "tsc --noEmit (best effort)" npx --yes tsc -p . --noEmit || true
  else
    echo "-> no build script; skipping build" | tee -a "$LOG_FILE"
  fi

  popd >/dev/null

done

echo "Done. Log: $LOG_FILE"
