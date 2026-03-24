# X Bookmarks Sync

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
![Platform: macOS](https://img.shields.io/badge/platform-macOS-black)
![Chrome: 144+](https://img.shields.io/badge/Chrome-144%2B-blue)
![Codex Skill](https://img.shields.io/badge/Codex-skill-orange)

[中文说明](./README.zh-CN.md)

Sync your X.com bookmarks into Obsidian notes by reusing your real, logged-in Chrome session.

## At a glance

- Uses your existing authenticated Chrome session instead of a separate scraper login
- Exports bookmarks from `https://x.com/i/bookmarks`
- Generates one Markdown note per bookmark in Obsidian
- Keeps stable incremental numbering across repeated syncs
- Numbers bookmarks by bookmark-list order, from the bottom oldest item upward

This skill is designed for Codex-style agents and local desktop workflows where:

- you are already signed in to X in Chrome
- you want one Obsidian note per bookmark
- you want stable numbering across repeated syncs
- you want future syncs to append new bookmarks instead of renumbering old ones

## What it does

- Connects to your current Chrome session through remote debugging
- Reads your X bookmarks from `https://x.com/i/bookmarks`
- Writes one Markdown note per bookmark into your Obsidian vault
- Preserves numbering with filenames like:

```text
001 - Title - YYYY-MM-DD HHMMSS - author.md
002 - Title - YYYY-MM-DD HHMMSS - author.md
```

- Numbering follows bookmark-list order from bottom to top:
  - the oldest bookmark at the bottom of the list is `001`
  - newer bookmarks higher in the list get larger numbers

- Maintains:
  - `000 - X 书签索引.md` as an ordered index page
  - `.x_bookmarks_state.json` as sync state for incremental numbering

## Current output path

By default, notes are written to:

```text
~/Obsidian/X Bookmarks
```

You do not need to edit the scripts to change this.

Copy `x_bookmarks_sync.env.example` to `x_bookmarks_sync.env` and set:

```bash
X_BOOKMARKS_TARGET_DIR="$HOME/path/to/your/Obsidian/folder"
```

## Requirements

- macOS
- Google Chrome
- Chrome 144+ for the current-session remote-debugging flow used by this skill
- Python 3
- `npm`
- A working Codex-style environment that can run shell commands

`dev-browser` will be installed automatically if it is missing.

## Installation

Place this folder in your Codex skills directory, for example:

```text
~/.codex/skills/x-bookmarks-sync
```

If you are publishing to GitHub and another user wants to install it manually, they can clone or copy this folder into their skills directory.

## Quick start

1. Put this folder in `~/.codex/skills/x-bookmarks-sync`
2. Copy `x_bookmarks_sync.env.example` to `x_bookmarks_sync.env` if you want a custom output path
3. Enable remote debugging in your current Chrome session
4. Make sure you are already signed in to X in Chrome
5. Ask Codex to `Sync X bookmarks`

## How to use in Codex

Ask with prompts such as:

- `Sync X bookmarks`
- `Sync my X bookmarks into Obsidian`
- `Update the X bookmarks skill notes`
- `Use x-bookmarks-sync to refresh my bookmarks`

## How it works

1. The sync script checks that Chrome is new enough.
2. If `dev-browser` is missing, it installs it with `npm install -g dev-browser`.
3. It reads Chrome's `DevToolsActivePort` from the local profile.
4. It connects to your already-running Chrome session.
5. It exports bookmarks from X.
6. It regenerates the Obsidian notes and index.

## One-time Chrome setup

Enable Chrome remote debugging for the active browser session:

1. Open Chrome
2. Visit:

```text
chrome://inspect#remote-debugging
```

3. Enable remote debugging

After that, the skill can attempt to connect to your current Chrome session.

## Permission prompt behavior

Chrome may show a permission dialog when a new remote-debugging connection is created.

That means:

- sometimes the sync runs without extra interaction
- sometimes Chrome asks you to click `Allow`

If that prompt appears, click `Allow` and run the sync again.

## Incremental sync behavior

This skill is incremental in result, not purely incremental in transport.

What that means:

- existing bookmarks keep their original sequence numbers
- new bookmarks get appended with the next numbers
- old notes are not renumbered on future syncs
- numbering is based on bookmark-list order, not tweet/post timestamp

It also tries to stop early during scrolling:

- the exporter loads known bookmark links from `.x_bookmarks_state.json`
- if it sees several consecutive batches that are mostly already-synced bookmarks, it stops scrolling early

This makes repeated syncs faster than a full scroll every time.

## Manual shell usage

You can also run the sync directly:

```bash
~/.codex/skills/x-bookmarks-sync/scripts/sync_x_bookmarks.sh
```

Optional local config file:

```text
~/.codex/skills/x-bookmarks-sync/x_bookmarks_sync.env
```

## Files

- `SKILL.md`
  - the skill trigger and workflow definition
- `scripts/sync_x_bookmarks.sh`
  - environment checks, Chrome endpoint discovery, sync entrypoint
- `scripts/export_x_bookmarks.devbrowser.js`
  - bookmark export and early-stop scrolling logic
- `scripts/generate_x_obsidian_notes.py`
  - note generation, numbering, state tracking, index generation

## Notes and limitations

- This skill is more reliable than a normal unauthenticated scraper because it uses your real logged-in Chrome session.
- It is not a universal anti-bot bypass.
- If X changes page structure, login flow, or anti-automation behavior, this skill may need updates.
- If Chrome is too old, the script exits with a clear version message.
- If remote debugging is not enabled, the script exits with instructions.
- The default output path is only a safe example. Use `x_bookmarks_sync.env` for your own machine-specific settings.

## Recommended publishing notes

If you publish this on GitHub, consider documenting:

- your intended Codex host
- the supported Chrome version range
- whether the default Obsidian path is only an example or a required convention
- whether users should commit `.x_bookmarks_state.json`

## Related caution

This project reads content from your authenticated browser session. Use it only on machines and accounts you trust.
