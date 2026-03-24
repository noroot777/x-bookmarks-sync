#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LEGACY_X_CONFIG_FILE="${X_BOOKMARKS_CONFIG_FILE:-$SKILL_DIR/x_bookmarks_sync.env}"
LEGACY_CONFIG_FILE="${KNOWLEDGE_ORGANIZER_CONFIG_FILE:-$SKILL_DIR/knowledge_organizer.env}"
CONFIG_FILE="${WEB_CAPTURE_TO_OBSIDIAN_CONFIG_FILE:-$SKILL_DIR/web_capture_to_obsidian.env}"

for file in "$LEGACY_X_CONFIG_FILE" "$LEGACY_CONFIG_FILE" "$CONFIG_FILE"; do
  if [[ -f "$file" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "$file"
    set +a
  fi
done

TARGET_DIR_CONFIGURED=0
if [[ -n "${WEB_CAPTURE_TO_OBSIDIAN_TARGET_DIR:-}" || -n "${KNOWLEDGE_ORGANIZER_TARGET_DIR:-}" || -n "${X_BOOKMARKS_TARGET_DIR:-}" ]]; then
  TARGET_DIR_CONFIGURED=1
fi

DEVTOOLS_FILE="${WEB_CAPTURE_TO_OBSIDIAN_DEVTOOLS_FILE:-${KNOWLEDGE_ORGANIZER_DEVTOOLS_FILE:-${X_BOOKMARKS_DEVTOOLS_FILE:-$HOME/Library/Application Support/Google/Chrome/DevToolsActivePort}}}"
EXTRACT_SCRIPT="$SKILL_DIR/scripts/extract_input_urls.py"
EXPORT_SCRIPT="$SKILL_DIR/scripts/export_knowledge_pages.devbrowser.js"
GENERATE_SCRIPT="$SKILL_DIR/scripts/generate_knowledge_obsidian_notes.py"
LLM_SCRIPT="$SKILL_DIR/scripts/generate_knowledge_llm_overrides.py"
TARGET_DIR="${WEB_CAPTURE_TO_OBSIDIAN_TARGET_DIR:-${KNOWLEDGE_ORGANIZER_TARGET_DIR:-${X_BOOKMARKS_TARGET_DIR:-$HOME/Obsidian/Web Capture to Obsidian}}}"
STATE_FILE="${WEB_CAPTURE_TO_OBSIDIAN_STATE_FILE:-${KNOWLEDGE_ORGANIZER_STATE_FILE:-$TARGET_DIR/.web_capture_to_obsidian_state.json}}"
DEV_BROWSER_TMP="${WEB_CAPTURE_TO_OBSIDIAN_DEV_BROWSER_TMP:-${KNOWLEDGE_ORGANIZER_DEV_BROWSER_TMP:-${X_BOOKMARKS_DEV_BROWSER_TMP:-$HOME/.dev-browser/tmp}}}"
CHROME_BIN="${WEB_CAPTURE_TO_OBSIDIAN_CHROME_BIN:-${KNOWLEDGE_ORGANIZER_CHROME_BIN:-${X_BOOKMARKS_CHROME_BIN:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}}}"
MIN_SUPPORTED_CHROME_MAJOR="${WEB_CAPTURE_TO_OBSIDIAN_MIN_CHROME_MAJOR:-${KNOWLEDGE_ORGANIZER_MIN_CHROME_MAJOR:-${X_BOOKMARKS_MIN_CHROME_MAJOR:-144}}}"
URLS_JSON="${WEB_CAPTURE_TO_OBSIDIAN_URLS_JSON:-${KNOWLEDGE_ORGANIZER_URLS_JSON:-$DEV_BROWSER_TMP/web-capture-to-obsidian-urls.json}}"
SOURCE_JSON="${WEB_CAPTURE_TO_OBSIDIAN_SOURCE_JSON:-${KNOWLEDGE_ORGANIZER_SOURCE_JSON:-$DEV_BROWSER_TMP/web-capture-to-obsidian-export.json}}"
LLM_OVERRIDES_FILE="${WEB_CAPTURE_TO_OBSIDIAN_LLM_OVERRIDES_FILE:-${KNOWLEDGE_ORGANIZER_LLM_OVERRIDES_FILE:-$DEV_BROWSER_TMP/web-capture-to-obsidian-llm-overrides.json}}"
USE_LLM="${WEB_CAPTURE_TO_OBSIDIAN_USE_LLM:-${KNOWLEDGE_ORGANIZER_USE_LLM:-${X_BOOKMARKS_USE_LLM:-1}}}"
SKIP_EXPORT="${WEB_CAPTURE_TO_OBSIDIAN_SKIP_EXPORT:-${KNOWLEDGE_ORGANIZER_SKIP_EXPORT:-0}}"
SKIP_GENERATE="${WEB_CAPTURE_TO_OBSIDIAN_SKIP_GENERATE:-${KNOWLEDGE_ORGANIZER_SKIP_GENERATE:-0}}"
DEFAULT_TARGET_DIR="$HOME/Obsidian/Web Capture to Obsidian"

export WEB_CAPTURE_TO_OBSIDIAN_TARGET_DIR="$TARGET_DIR"
export WEB_CAPTURE_TO_OBSIDIAN_STATE_FILE="$STATE_FILE"
export WEB_CAPTURE_TO_OBSIDIAN_SOURCE_JSON="$SOURCE_JSON"
export WEB_CAPTURE_TO_OBSIDIAN_LLM_OVERRIDES_FILE="$LLM_OVERRIDES_FILE"
export KNOWLEDGE_ORGANIZER_TARGET_DIR="$TARGET_DIR"
export KNOWLEDGE_ORGANIZER_STATE_FILE="$STATE_FILE"
export KNOWLEDGE_ORGANIZER_SOURCE_JSON="$SOURCE_JSON"
export KNOWLEDGE_ORGANIZER_LLM_OVERRIDES_FILE="$LLM_OVERRIDES_FILE"

ensure_target_dir_configured() {
  if [[ "$TARGET_DIR_CONFIGURED" == "1" ]]; then
    return
  fi

  echo "First-time setup required before using web-capture-to-obsidian." >&2
  echo "Create web_capture_to_obsidian.env from web_capture_to_obsidian.env.example and set WEB_CAPTURE_TO_OBSIDIAN_TARGET_DIR to your Obsidian notes folder using an absolute path." >&2
  exit 1
}

ensure_absolute_target_dir() {
  if [[ "$TARGET_DIR" != /* ]]; then
    echo "WEB_CAPTURE_TO_OBSIDIAN_TARGET_DIR must be an absolute path. Current value: $TARGET_DIR" >&2
    echo "Update web_capture_to_obsidian.env and set WEB_CAPTURE_TO_OBSIDIAN_TARGET_DIR to an absolute path like /Users/you/obsidian/Web Capture." >&2
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
  echo "Install Codex first, or run with WEB_CAPTURE_TO_OBSIDIAN_USE_LLM=0 to skip LLM-generated titles, summaries, and tags." >&2
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

collect_input() {
  if [[ "$#" -gt 0 ]]; then
    printf '%s' "$*"
    return
  fi

  if [[ ! -t 0 ]]; then
    cat
    return
  fi

  echo "Pass a URL or paste text that contains one or more URLs." >&2
  exit 1
}

RAW_INPUT="$(collect_input "$@")"
ensure_target_dir_configured
ensure_absolute_target_dir
mkdir -p "$DEV_BROWSER_TMP"

URLS_JSON_CONTENT="$(python3 "$EXTRACT_SCRIPT" "$RAW_INPUT")"
printf '%s\n' "$URLS_JSON_CONTENT" > "$URLS_JSON"

URL_COUNT="$(
  python3 -c 'import json,sys
try:
    data=json.load(sys.stdin)
except Exception:
    data=[]
print(len(data) if isinstance(data, list) else 0)
' <<<"$URLS_JSON_CONTENT"
)"

if [[ "$URL_COUNT" == "0" ]]; then
  echo "No supported URLs were found in the provided text." >&2
  exit 1
fi

ensure_dev_browser
check_chrome_version

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
  echo "Exported $URL_COUNT pages to $SOURCE_JSON"
elif [[ "$USE_LLM" == "1" ]]; then
  echo "Organized $URL_COUNT link(s) into $TARGET_DIR with LLM-generated titles, summaries, and tags"
else
  echo "Organized $URL_COUNT link(s) into $TARGET_DIR without LLM participation"
fi
