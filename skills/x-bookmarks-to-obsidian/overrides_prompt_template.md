# X Overrides Prompt Template

Use this after running:

`python3 scripts/x_bookmarks_to_obsidian.py export`

## Goal

Read the incremental X bookmark JSON first, then write a compact overrides JSON for the current export window. Only newly discovered bookmarks should receive fresh LLM analysis.

## Inputs

- Incremental JSON to analyze: the file `x-bookmarks-to-obsidian-incremental.json` in the same directory as `X_BOOKMARKS_TO_OBSIDIAN_SOURCE_JSON`
  Default: `~/.dev-browser/tmp/x-bookmarks-to-obsidian-incremental.json`
- Full current export window: `X_BOOKMARKS_TO_OBSIDIAN_SOURCE_JSON`
  Default: `~/.dev-browser/tmp/x-bookmarks-to-obsidian-export.json`
- Overrides JSON to write: `X_BOOKMARKS_TO_OBSIDIAN_LLM_OVERRIDES_FILE`
  Default: `~/.dev-browser/tmp/x-bookmarks-to-obsidian-llm-overrides.json`
- Existing overrides file: optional, reuse it if it already exists
- Example shape: [`x_bookmarks_to_obsidian_llm_overrides.example.json`](x_bookmarks_to_obsidian_llm_overrides.example.json)

## Required Output Shape

```json
{
  "entries": {
    "https://x.com/.../status/...": {
      "title": "...",
      "summary": ["...", "..."],
      "tags": ["x-bookmarks-to-obsidian", "..."]
    }
  }
}
```

## Rules

- Keep exactly one entry per `statusLink` in the current export window.
- Analyze only bookmarks present in the incremental JSON.
- Reuse existing overrides when they are still good for known bookmarks that remain in the current export window.
- Only add or update entries that appear in the current export window.
- Remove stale override entries that are not in the current export window.
- `title`: short, concrete, higher-signal than the raw first line.
- `summary`: 1 to 3 bullets as plain strings, no markdown bullets in the strings.
- `tags`: 2 to 6 short tags, lowercase preferred, no `#` prefix.
- Do not invent claims that are not supported by the exported bookmark text or links.
- Prefer describing the value of the bookmark, not restating filler phrases from the post.
- Keep Chinese output natural when the source is Chinese; keep English when that is clearly better.

## Suggested Process

1. Read the incremental JSON.
2. Read the full current export JSON.
3. Build the set of current `statusLink` keys.
4. Read existing overrides JSON if present.
5. Reuse existing overrides for known bookmarks still present in the current export window.
6. Create fresh `title`, `summary`, and `tags` only for incremental bookmarks.
7. Write back a full JSON object with top-level `entries`.

## Ready-to-Use Prompt

```text
Read `x-bookmarks-to-obsidian-incremental.json` from the same directory as X_BOOKMARKS_TO_OBSIDIAN_SOURCE_JSON, then read X_BOOKMARKS_TO_OBSIDIAN_SOURCE_JSON and X_BOOKMARKS_TO_OBSIDIAN_LLM_OVERRIDES_FILE if it already exists. Create a fresh overrides JSON object with top-level key "entries". Keep exactly one entry per current bookmark statusLink from the full export window. Remove stale entries that are no longer in the current export.

Only bookmarks in that incremental JSON file should receive fresh analysis. For bookmarks already known but still present in the current export window, reuse good existing overrides instead of re-analyzing them.

For each incremental bookmark, write:
- title: concise and higher-signal
- summary: 1-3 plain strings, no bullet markers inside the strings
- tags: 2-6 short tags, no # prefix

Do not invent unsupported claims. If the incremental JSON is empty, keep only reusable overrides for the current export window and skip fresh analysis. Then write the final JSON to X_BOOKMARKS_TO_OBSIDIAN_LLM_OVERRIDES_FILE.
```
