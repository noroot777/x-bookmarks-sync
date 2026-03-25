#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_FILE="${X_BOOKMARKS_TO_OBSIDIAN_CONFIG_FILE:-$SKILL_DIR/x_bookmarks_to_obsidian.env}"

if [[ -f "$CONFIG_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$CONFIG_FILE"
  set +a
fi

TARGET_DIR_CONFIGURED=0
if [[ -n "${X_BOOKMARKS_TO_OBSIDIAN_TARGET_DIR:-}" ]]; then
  TARGET_DIR_CONFIGURED=1
fi

DEVTOOLS_FILE="${X_BOOKMARKS_TO_OBSIDIAN_DEVTOOLS_FILE:-$HOME/Library/Application Support/Google/Chrome/DevToolsActivePort}"
EXPORT_SCRIPT="$SKILL_DIR/scripts/export_x_bookmarks.devbrowser.js"
GENERATE_SCRIPT="$SKILL_DIR/scripts/generate_x_bookmarks_obsidian_notes.py"
LLM_SCRIPT="$SKILL_DIR/scripts/generate_x_bookmarks_llm_overrides.py"
TARGET_DIR="${X_BOOKMARKS_TO_OBSIDIAN_TARGET_DIR:-$HOME/Obsidian/X Bookmarks to Obsidian}"
STATE_FILE="${X_BOOKMARKS_TO_OBSIDIAN_STATE_FILE:-$TARGET_DIR/.x_bookmarks_to_obsidian_state.json}"
LEGACY_STATE_FILE="${TARGET_DIR}/.x_bookmarks_state.json"
DEV_BROWSER_TMP="${X_BOOKMARKS_TO_OBSIDIAN_DEV_BROWSER_TMP:-$HOME/.dev-browser/tmp}"
KNOWN_LINKS_FILE="${X_BOOKMARKS_TO_OBSIDIAN_KNOWN_LINKS_FILE:-$DEV_BROWSER_TMP/x-bookmarks-to-obsidian-known.json}"
CHROME_BIN="${X_BOOKMARKS_TO_OBSIDIAN_CHROME_BIN:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
MIN_SUPPORTED_CHROME_MAJOR="${X_BOOKMARKS_TO_OBSIDIAN_MIN_CHROME_MAJOR:-144}"
SOURCE_JSON="${X_BOOKMARKS_TO_OBSIDIAN_SOURCE_JSON:-$DEV_BROWSER_TMP/x-bookmarks-to-obsidian-export.json}"
LLM_OVERRIDES_FILE="${X_BOOKMARKS_TO_OBSIDIAN_LLM_OVERRIDES_FILE:-$DEV_BROWSER_TMP/x-bookmarks-to-obsidian-llm-overrides.json}"
USE_LLM="${X_BOOKMARKS_TO_OBSIDIAN_USE_LLM:-1}"
SKIP_EXPORT="${X_BOOKMARKS_TO_OBSIDIAN_SKIP_EXPORT:-0}"
SKIP_GENERATE="${X_BOOKMARKS_TO_OBSIDIAN_SKIP_GENERATE:-0}"

export X_BOOKMARKS_TO_OBSIDIAN_TARGET_DIR="$TARGET_DIR"
export X_BOOKMARKS_TO_OBSIDIAN_STATE_FILE="$STATE_FILE"
export X_BOOKMARKS_TO_OBSIDIAN_SOURCE_JSON="$SOURCE_JSON"
export X_BOOKMARKS_TO_OBSIDIAN_LLM_OVERRIDES_FILE="$LLM_OVERRIDES_FILE"

ensure_target_dir_configured() {
  if [[ "$TARGET_DIR_CONFIGURED" == "1" ]]; then
    return
  fi

  echo "First-time setup required before syncing X bookmarks." >&2
  echo "Create x_bookmarks_to_obsidian.env from x_bookmarks_to_obsidian.env.example and set X_BOOKMARKS_TO_OBSIDIAN_TARGET_DIR to your Obsidian notes folder using an absolute path." >&2
  exit 1
}

ensure_absolute_target_dir() {
  if [[ "$TARGET_DIR" != /* ]]; then
    echo "X_BOOKMARKS_TO_OBSIDIAN_TARGET_DIR must be an absolute path. Current value: $TARGET_DIR" >&2
    echo "Update x_bookmarks_to_obsidian.env and set X_BOOKMARKS_TO_OBSIDIAN_TARGET_DIR to an absolute path like /Users/you/Obsidian/X Bookmarks." >&2
    exit 1
  fi
}

ensure_dev_browser() {
  if command -v dev-browser >/dev/null 2>&1; then
    return
  fi

  if ! command -v npm >/dev/null 2>&1; then
    echo "dev-browser is not installed, and npm is not available to install it automatically." >&2
    exit 1
  fi

  echo "dev-browser not found. Installing it automatically with npm..."
  npm install -g dev-browser
}

ensure_codex() {
  if command -v codex >/dev/null 2>&1; then
    return
  fi

  echo "Standalone shell automation with LLM participation is enabled, but the codex CLI is not available." >&2
  echo "Install Codex first, or run with X_BOOKMARKS_TO_OBSIDIAN_USE_LLM=0 to skip LLM-generated titles, summaries, and tags." >&2
  exit 1
}

check_chrome_version() {
  if [[ ! -x "$CHROME_BIN" ]]; then
    echo "Google Chrome was not found at: $CHROME_BIN" >&2
    exit 1
  fi

  local version_output major
  version_output="$("$CHROME_BIN" --version 2>/dev/null || true)"
  major="$(printf '%s' "$version_output" | sed -E 's/.* ([0-9]+)\..*/\1/')"

  if [[ -z "$major" || ! "$major" =~ ^[0-9]+$ ]]; then
    echo "Could not determine the installed Chrome version. Output was: $version_output" >&2
    exit 1
  fi

  if (( major < MIN_SUPPORTED_CHROME_MAJOR )); then
    echo "Chrome $major is too old for this skill's current-session remote-debugging flow." >&2
    echo "This skill expects Chrome ${MIN_SUPPORTED_CHROME_MAJOR}+ with chrome://inspect#remote-debugging support for active browser sessions." >&2
    exit 1
  fi
}

ensure_target_dir_configured
ensure_absolute_target_dir
ensure_dev_browser
check_chrome_version

if [[ ! -f "$STATE_FILE" && -f "$LEGACY_STATE_FILE" ]]; then
  STATE_FILE="$LEGACY_STATE_FILE"
fi

if [[ ! -f "$DEVTOOLS_FILE" ]]; then
  echo "Chrome remote debugging is not enabled: $DEVTOOLS_FILE not found" >&2
  echo "Open chrome://inspect#remote-debugging in Chrome and enable remote debugging first." >&2
  exit 1
fi

PORT="$(sed -n '1p' "$DEVTOOLS_FILE" | tr -d '\r')"
WS_PATH="$(sed -n '2p' "$DEVTOOLS_FILE" | tr -d '\r')"

if [[ -z "$PORT" || -z "$WS_PATH" ]]; then
  echo "Invalid DevToolsActivePort contents" >&2
  exit 1
fi

ENDPOINT="ws://127.0.0.1:${PORT}${WS_PATH}"

export X_BOOKMARKS_TO_OBSIDIAN_STATE_FILE="$STATE_FILE"

mkdir -p "$DEV_BROWSER_TMP"

if [[ -f "$STATE_FILE" ]]; then
  python3 - <<'PY' > "$KNOWN_LINKS_FILE"
import json
import os
from pathlib import Path

state = Path(os.environ["X_BOOKMARKS_TO_OBSIDIAN_STATE_FILE"]).expanduser()
try:
    data = json.loads(state.read_text(encoding="utf-8"))
    entries = data.get("entries", {})
    print(json.dumps(list(entries.keys()), ensure_ascii=False))
except Exception:
    print("[]")
PY
else
  printf '[]' > "$KNOWN_LINKS_FILE"
fi

KNOWN_COUNT="$(KNOWN_LINKS_FILE="$KNOWN_LINKS_FILE" python3 - <<'PY'
import json
import os
from pathlib import Path

path = Path(os.environ["KNOWN_LINKS_FILE"]).expanduser()
try:
    data = json.loads(path.read_text(encoding="utf-8"))
    print(len(data) if isinstance(data, list) else 0)
except Exception:
    print(0)
PY
)"

if [[ -f "$STATE_FILE" ]]; then
  echo "Loaded $KNOWN_COUNT known bookmarks from $STATE_FILE"
else
  echo "No prior state file found; export will scan until the end of the bookmark list"
fi

if [[ "$SKIP_EXPORT" != "1" ]]; then
  dev-browser --connect "$ENDPOINT" --timeout 900 run "$EXPORT_SCRIPT"
fi

if [[ "$SKIP_GENERATE" != "1" && "$USE_LLM" == "1" ]]; then
  ensure_codex
  python3 "$LLM_SCRIPT"
fi

if [[ "$SKIP_GENERATE" != "1" ]]; then
  python3 "$GENERATE_SCRIPT"
fi

if [[ "$SKIP_GENERATE" == "1" ]]; then
  echo "Exported X bookmarks to $SOURCE_JSON"
elif [[ "$USE_LLM" == "1" ]]; then
  echo "Synced X bookmarks into $TARGET_DIR with LLM-generated titles, summaries, and tags"
else
  echo "Synced X bookmarks into $TARGET_DIR without LLM participation"
fi
