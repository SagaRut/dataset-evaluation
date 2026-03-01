#!/usr/bin/env bash
set -euo pipefail

REPOS_FILE="benchmark.txt"
TARGET_DIR="Benchmark-Projects"
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

extract_repo_and_commit () {
  local url="$1"

  if [[ "$url" == *github.com* ]]; then
    repo_url="$(echo "$url" | sed -E 's|(https://github.com/[^/]+/[^/]+)/commit/.*|\1.git|')"
    commit_hash="$(echo "$url" | sed -E 's|.*/commit/([a-f0-9]+).*|\1|')"

  elif [[ "$url" == *gitlab.com* ]]; then
    repo_url="$(echo "$url" | sed -E 's|(https://gitlab.com/[^/]+/[^/]+)/-?/commit/.*|\1.git|')"
    commit_hash="$(echo "$url" | sed -E 's|.*/commit/([a-f0-9]+).*|\1|')"

  else
    return 1
  fi

  echo "$repo_url;$commit_hash"
}

while IFS= read -r url; do
  url="$(echo "$url" | xargs)"
  [[ -z "$url" || "$url" == \#* ]] && continue

  parsed="$(extract_repo_and_commit "$url")" || {
    echo "!! Could not parse URL: $url" | tee -a "$LOG_FILE"
    continue
  }

  repo_url="${parsed%%;*}"
  commit_hash="${parsed##*;}"

  name="$(basename "$repo_url")"
  name="${name%.git}"
  dest="$TARGET_DIR/$name"

  echo "==== $name ====" | tee -a "$LOG_FILE"
  echo "Commit URL: $url" | tee -a "$LOG_FILE"
  echo "Repo URL:   $repo_url" | tee -a "$LOG_FILE"
  echo "Commit:     $commit_hash" | tee -a "$LOG_FILE"
  echo "DIR:        $dest" | tee -a "$LOG_FILE"

  if [[ -d "$dest/.git" ]]; then
    echo "-> already cloned" | tee -a "$LOG_FILE"
  elif [[ -d "$dest" && -n "$(ls -A "$dest" 2>/dev/null || true)" ]]; then
    echo "-> dir exists and not empty; skipping clone" | tee -a "$LOG_FILE"
    continue
  else
    run_logged "cloning" git clone "$repo_url" "$dest" || {
      discard_repo "$dest" "clone failed"
      continue
    }
  fi

  pushd "$dest" >/dev/null

  run_logged "fetching" git fetch --all || {
    popd >/dev/null
    discard_repo "$dest" "fetch failed"
    continue
  }

  run_logged "checkout $commit_hash" git checkout "$commit_hash" || {
    popd >/dev/null
    discard_repo "$dest" "checkout failed"
    continue
  }

  if [[ ! -f package.json ]]; then
    popd >/dev/null
    discard_repo "$dest" "no package.json"
    continue
  fi

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