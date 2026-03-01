#!/usr/bin/env bash
set -euo pipefail

REPOS_FILE="repos.txt"
TARGET_DIR="JS-Projects"
LOG_FILE="clone_validate.log"

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

discard_repo () {
  local repo_path="$1"
  local reason="$2"
  echo "!! discarding $repo_path ($reason)" | tee -a "$LOG_FILE"
  rm -rf "$repo_path" >>"$LOG_FILE" 2>&1 || true
}

while IFS= read -r url; do
  url="$(echo "$url" | sed -e 's/[[:space:]]//g')"
  [[ -z "$url" || "$url" == \#* ]] && continue

  name="$(basename "$url")"
  name="${name%.git}"
  dest="$TARGET_DIR/$name"

  echo "==== $name ====" | tee -a "$LOG_FILE"
  echo "URL: $url" | tee -a "$LOG_FILE"
  echo "DIR: $dest" | tee -a "$LOG_FILE"

  if [[ -d "$dest/.git" ]]; then
    echo "-> already cloned" | tee -a "$LOG_FILE"
  elif [[ -d "$dest" && -n "$(ls -A "$dest" 2>/dev/null || true)" ]]; then
    echo "-> dir exists and not empty; skipping clone" | tee -a "$LOG_FILE"
    continue
  else
    mkdir -p "$dest"
    run_logged "cloning" git clone --depth 1 "$url" "$dest" || { discard_repo "$dest" "clone failed"; continue; }
  fi

  if [[ ! -f "$dest/package.json" ]]; then
    discard_repo "$dest" "no package.json"
    continue
  fi

  pushd "$dest" >/dev/null

  if [[ -f package-lock.json ]]; then
    if ! run_logged "npm ci" npm ci; then
      popd >/dev/null
      discard_repo "$dest" "npm ci failed"
      continue
    fi
  else
    if ! run_logged "npm install" npm install; then
      popd >/dev/null
      discard_repo "$dest" "npm install failed"
      continue
    fi
  fi

  if node -e 'process.exit((require("./package.json").scripts||{}).build?0:1)' ; then
    run_logged "npm run build" npm run build || true
  elif [[ -f tsconfig.json ]]; then
    run_logged "tsc --noEmit (best effort)" npx --yes tsc -p . --noEmit || true
  else
    echo "-> no build script; skipping build" | tee -a "$LOG_FILE"
  fi

  popd >/dev/null
done < "$REPOS_FILE"

echo "Done. Log: $LOG_FILE"