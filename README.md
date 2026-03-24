# X Bookmarks Sync

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
![Platform: macOS](https://img.shields.io/badge/platform-macOS-black)
![Chrome: 144+](https://img.shields.io/badge/Chrome-144%2B-blue)
![Agent Friendly](https://img.shields.io/badge/agent-friendly-orange)

[中文说明](./README.zh-CN.md)

Sync your X.com bookmarks into Obsidian notes by reusing your real, logged-in Chrome session.
Use it either as a standalone shell workflow or as a skill/integration inside an agent tool.

Recommended mode: let an LLM agent export the bookmarks, improve titles and summaries, then generate the final notes.

## At a glance

- Uses your existing authenticated Chrome session instead of a separate scraper login
- Exports bookmarks from `https://x.com/i/bookmarks`
- Generates one Markdown note per bookmark in Obsidian
- Keeps stable incremental numbering across repeated syncs
- Numbers bookmarks by bookmark-list order, from the bottom oldest item upward

This project is useful for local desktop workflows where:

- you are already signed in to X in Chrome
- you want one Obsidian note per bookmark
- you want stable numbering across repeated syncs
- you want future syncs to append new bookmarks instead of renumbering old ones

## What it does

- Connects to your current Chrome session through remote debugging
- Reads your X bookmarks from `https://x.com/i/bookmarks`
- Writes one Markdown note per bookmark into your Obsidian vault
- Supports LLM-written title and summary overrides during agent execution
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
- Chrome 144+ for the current-session remote-debugging flow used by this project
- Python 3
- `npm`
- Any environment that can run shell commands

`dev-browser` will be installed automatically if it is missing.

## Installation options

You can use this project in three common ways.

### Option 1: Ask an LLM agent to install it for you

If your assistant can access your filesystem and run shell commands, you can ask it to install this repo for you.

Example prompts:

- `Help me install x-bookmarks-sync from https://github.com/noroot777/x-bookmarks-sync`
- `Clone this repo, copy x_bookmarks_sync.env.example to x_bookmarks_sync.env, and configure it for my Obsidian folder`
- `Install this as a skill in my local agent setup and make it run scripts/sync_x_bookmarks.sh`
- `Set up x-bookmarks-sync on this machine and tell me how to run it`

What the agent should generally do:

- clone the repository
- place it in the correct skills/tools directory if your host uses one
- copy `x_bookmarks_sync.env.example` to `x_bookmarks_sync.env`
- set `X_BOOKMARKS_TARGET_DIR` to your actual Obsidian path
- verify Chrome remote debugging is enabled
- run `X_BOOKMARKS_SKIP_GENERATE=1 ./scripts/sync_x_bookmarks.sh`
- write `x-bookmarks-llm-overrides.json` based on the exported bookmarks
- run `python3 scripts/generate_x_obsidian_notes.py`

### Option 2: Install it as a Codex skill

Place this folder in your Codex skills directory, for example:

```text
~/.codex/skills/x-bookmarks-sync
```

Then ask Codex something like:

- `Sync X bookmarks`
- `Sync my X bookmarks into Obsidian`

### Option 3: Integrate it into other agent tools

If your tool supports custom skills, slash commands, prompt libraries, or shell tasks, point it at:

```text
scripts/sync_x_bookmarks.sh
```

Typical patterns:

- register a custom command that runs `./scripts/sync_x_bookmarks.sh`
- add a reusable prompt/snippet that tells the agent to run that script
- create a task or automation entry that launches the sync script in this repo

For tools without a formal skill format, using the shell script directly is usually the simplest setup.

## Quick start

1. Clone or copy this repo to your machine
2. Copy `x_bookmarks_sync.env.example` to `x_bookmarks_sync.env` if you want a custom output path
3. Enable remote debugging in your current Chrome session
4. Make sure you are already signed in to X in Chrome
5. Run `./scripts/sync_x_bookmarks.sh` or call it from your agent tool

## Example prompts for agent tools

If your agent can run shell commands, prompts such as these usually work:

- `Sync X bookmarks`
- `Sync my X bookmarks into Obsidian`
- `Refresh my X bookmarks notes`
- `Run the x-bookmarks-sync script`
- `Export my X bookmarks, improve each note title and summary with the model, then generate the final Obsidian notes`

## LLM-assisted extraction

If an agent is running this project, it can improve title and summary quality by writing:

```text
~/.dev-browser/tmp/x-bookmarks-llm-overrides.json
```

The generator automatically reads that file when present. See:

- `x_bookmarks_llm_overrides.example.json`
- `SKILL.md`

Recommended agent flow:

1. Run `X_BOOKMARKS_SKIP_GENERATE=1 ./scripts/sync_x_bookmarks.sh`
2. Read `~/.dev-browser/tmp/x-bookmarks-export.json`
3. Write better `title` and `summary` values into `~/.dev-browser/tmp/x-bookmarks-llm-overrides.json`
4. Run `python3 scripts/generate_x_obsidian_notes.py`

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

After that, the script can attempt to connect to your current Chrome session.

## Permission prompt behavior

Chrome may show a permission dialog when a new remote-debugging connection is created.

That means:

- sometimes the sync runs without extra interaction
- sometimes Chrome asks you to click `Allow`

If that prompt appears, click `Allow` and run the sync again.

## Incremental sync behavior

This workflow is incremental in result, not purely incremental in transport.

What that means:

- existing bookmarks keep their original sequence numbers
- new bookmarks get appended with the next numbers
- old notes are not renumbered on future syncs
- numbering is based on bookmark-list order, not tweet/post timestamp

It also tries to stop early during scrolling:

- the exporter loads known bookmark links from `.x_bookmarks_state.json`
- if it sees several consecutive batches that are mostly already-synced bookmarks, it stops scrolling early

This makes repeated syncs faster than a full scroll every time.

## Standalone shell usage

You can run the sync directly without any skill system:

```bash
./scripts/sync_x_bookmarks.sh
```

Optional local config file:

```text
./x_bookmarks_sync.env
```

From another directory, you can also run:

```bash
bash /path/to/x-bookmarks-sync/scripts/sync_x_bookmarks.sh
```

## Files

- `SKILL.md`
  - an example skill definition for tools that support skill-style metadata
- `x_bookmarks_llm_overrides.example.json`
  - example format for LLM-generated title and summary overrides
- `scripts/sync_x_bookmarks.sh`
  - environment checks, Chrome endpoint discovery, sync entrypoint
- `scripts/export_x_bookmarks.devbrowser.js`
  - bookmark export and early-stop scrolling logic
- `scripts/generate_x_obsidian_notes.py`
  - note generation, numbering, state tracking, index generation

## Notes and limitations

- This project is more reliable than a normal unauthenticated scraper because it uses your real logged-in Chrome session.
- It is not a universal anti-bot bypass.
- If X changes page structure, login flow, or anti-automation behavior, this project may need updates.
- If Chrome is too old, the script exits with a clear version message.
- If remote debugging is not enabled, the script exits with instructions.
- The default output path is only a safe example. Use `x_bookmarks_sync.env` for your own machine-specific settings.

## Related caution

This project reads content from your authenticated browser session. Use it only on machines and accounts you trust.
