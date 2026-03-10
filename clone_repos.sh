#!/usr/bin/env bash
set -euo pipefail

REPOS_FILE="repos.txt"
TARGET_DIR="JS-Projects"
LOG_FILE="clone_repos.log"

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
done < "$REPOS_FILE"

echo "Done. Log: $LOG_FILE"