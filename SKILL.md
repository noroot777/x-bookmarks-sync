---
name: x-bookmarks-sync
description: Sync the user's X.com bookmarks into Obsidian notes using the user's already logged-in Chrome session. Use this when the user asks to sync, refresh, import, capture, or update X bookmarks into Obsidian, especially for requests like "同步 X 书签", "抓取我的 X 书签", "更新 Obsidian 里的 X 书签", or "把最新书签同步进去".
---

# X Bookmarks Sync

Syncs X bookmarks from the user's real Chrome session into a configurable Obsidian directory.

## Workflow

1. Run [`scripts/sync_x_bookmarks.sh`](scripts/sync_x_bookmarks.sh).
2. The script will:
   - verify that the installed Chrome version supports the current-session remote-debugging flow
   - auto-install `dev-browser` if it is missing
   - reuse the user's logged-in Chrome session via `chrome://inspect#remote-debugging`
3. If Chrome shows a remote-debugging permission prompt, wait for the user to click `Allow`, then rerun the sync script.
4. Report how many bookmarks were synced and where the notes were written.
5. If the user wants a custom location, tell them to create `x_bookmarks_sync.env` from `x_bookmarks_sync.env.example` instead of editing the scripts directly.

## What It Writes

- One note per bookmark under `X_BOOKMARKS_TARGET_DIR`
- Stable numbered filenames like `001 - 标题 - 时间 - 作者.md`
- Numbering follows bookmark-list order from bottom to top: the oldest bookmark currently at the bottom of the list is `001`, and newer bookmarks continue upward with larger numbers
- `000 - X 书签索引.md` for ordered browsing
- `.x_bookmarks_state.json` to preserve numbering across future syncs

## Notes

- This uses the user's authenticated Chrome session, so it is much more reliable than a normal unauthenticated scraper, but it is not a guaranteed bypass for every X anti-bot check.
- This skill expects a Chrome version that supports the current-session remote-debugging flow from `chrome://inspect#remote-debugging`. If the local Chrome is too old, the script exits with a clear message instead of failing silently.
- If the user wants a different Obsidian path, use `x_bookmarks_sync.env`. If they want a different naming scheme or note format, update [`scripts/generate_x_obsidian_notes.py`](scripts/generate_x_obsidian_notes.py) and rerun the sync.
