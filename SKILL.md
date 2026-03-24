---
name: web-capture-to-obsidian
description: Capture one or more web links into Obsidian notes. Use this when the user wants to save a URL, paste text that contains URLs, capture WeChat/GitHub/X/general web pages into Obsidian, or sync full X bookmarks.
---

# Web Capture to Obsidian

Capture saved links and X bookmarks from the user's real Chrome session into Obsidian.

## Recommended Cross-Client Workflow

Use this workflow in Codex, Claude Code, OpenCode, and OpenClaw.

Before first use, tell the user to configure their Obsidian target directory:

- `web_capture_to_obsidian.env` for generic web capture
- `x_bookmarks_sync.env` for X bookmark sync
- the target directory must be an absolute path

### For one link or pasted text containing URLs

1. Run export-only capture:
   - `WEB_CAPTURE_TO_OBSIDIAN_SKIP_GENERATE=1 ./scripts/organize_knowledge.sh "<user input>"`
2. Read the exported JSON from:
   - `WEB_CAPTURE_TO_OBSIDIAN_SOURCE_JSON`
   - default: `~/.dev-browser/tmp/web-capture-to-obsidian-export.json`
3. Generate better `title`, `summary`, and `tags` in the current agent session.
4. Write overrides to:
   - `WEB_CAPTURE_TO_OBSIDIAN_LLM_OVERRIDES_FILE`
   - default: `~/.dev-browser/tmp/web-capture-to-obsidian-llm-overrides.json`
5. Follow the JSON shape from:
   - [`web_capture_to_obsidian_llm_overrides.example.json`](web_capture_to_obsidian_llm_overrides.example.json)
6. Generate final notes:
   - `python3 scripts/generate_knowledge_obsidian_notes.py`

### For full X bookmark sync

1. Run export-only sync:
   - `X_BOOKMARKS_SKIP_GENERATE=1 ./scripts/sync_x_bookmarks.sh`
2. Read the exported JSON from:
   - `X_BOOKMARKS_SOURCE_JSON`
   - default: `~/.dev-browser/tmp/x-bookmarks-export.json`
3. Generate better `title`, `summary`, and `tags` in the current agent session.
4. Write overrides to:
   - `X_BOOKMARKS_LLM_OVERRIDES_FILE`
   - default: `~/.dev-browser/tmp/x-bookmarks-llm-overrides.json`
5. Follow the JSON shape from:
   - [`x_bookmarks_llm_overrides.example.json`](x_bookmarks_llm_overrides.example.json)
6. Generate final notes:
   - `python3 scripts/generate_x_obsidian_notes.py`

## Standalone Shell Automation

Optional standalone shell automation is still available:

- `./scripts/organize_knowledge.sh "<user input>"`
- `./scripts/sync_x_bookmarks.sh`

In standalone LLM mode, the shell scripts use the local `codex` CLI. If `codex` is not installed, disable LLM participation or use the recommended cross-client workflow above.

## User Choice

- If the user wants to capture one link or pasted text with URLs, use `scripts/organize_knowledge.sh`.
- If the user wants full X bookmark sync, use `scripts/sync_x_bookmarks.sh`.
- If the user explicitly says not to use the model, disable LLM participation and skip overrides.
- On first use, tell them to create `web_capture_to_obsidian.env` or `x_bookmarks_sync.env` from the example files and set the Obsidian target directory to an absolute path instead of editing the scripts directly.

## Supported Sources

- WeChat article links such as `https://mp.weixin.qq.com/...`
- GitHub repositories, issues, pull requests, discussions, and README pages
- X / Twitter post links
- Generic web pages accessible from the user's current Chrome session
- Full X bookmark list sync from `https://x.com/i/bookmarks`

## Input Handling

- `scripts/organize_knowledge.sh` accepts:
  - a direct URL
  - a pasted paragraph that contains one or more URLs
  - piped text from stdin
- It extracts unique `http://` and `https://` URLs in appearance order.

## Extraction Guidance

When generating `title` and `summary` for any source:

- Prefer the real core idea over the first visible line.
- Remove handles, metrics, navigation text, and low-signal UI boilerplate.
- For link-heavy pages, summarize what the linked resource is about.
- Keep `title` concise and filename-friendly.
- Keep `summary` to 2-4 concrete bullets.
- Return tags that are specific enough to be useful in Obsidian.

## What It Writes

- For generic links:
  - one note per captured URL under `WEB_CAPTURE_TO_OBSIDIAN_TARGET_DIR`
  - stable numbered filenames
  - `000 - 网页采集索引.md`
  - `.web_capture_to_obsidian_state.json`
- For full X bookmark sync:
  - one note per bookmark under `X_BOOKMARKS_TARGET_DIR`
  - stable numbered filenames
  - `000 - X 书签索引.md`
  - `.x_bookmarks_state.json`

## Notes

- This uses the user's authenticated Chrome session, so it is much more reliable than an unauthenticated scraper, but it is not a guaranteed bypass for every site restriction.
- This skill expects Chrome with the current-session remote-debugging flow from `chrome://inspect#remote-debugging`.
- The current minimal note template is intentional:
  - frontmatter: `tags`, `source_type`, `source_host`
  - body: `摘要`, `页面摘录`
- Legacy `knowledge-organizer` environment variable names are still accepted for compatibility, but `web-capture-to-obsidian` is now the primary public name.
