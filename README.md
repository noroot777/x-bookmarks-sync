# Web Capture to Obsidian

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
![Platform: macOS](https://img.shields.io/badge/platform-macOS-black)
![Chrome: 144+](https://img.shields.io/badge/Chrome-144%2B-blue)
![Agent Friendly](https://img.shields.io/badge/agent-friendly-orange)

[中文说明](./README.zh-CN.md)

`web-capture-to-obsidian` is a cross-client Agent Skill package for capturing web content into Obsidian.

It supports:

- a single URL
- pasted text that contains one or more URLs
- WeChat, GitHub, X, and generic web pages
- the original full X bookmarks sync workflow

This project started as `x-bookmarks-sync`, but the scope is now broader: web capture first, Obsidian output second, X bookmarks still supported as one workflow inside the same package.

## At a glance

- Reuses your real logged-in Chrome session through remote debugging
- Uses `dev-browser` for repeatable browser automation
- Works as a shared `SKILL.md` package across Codex, Claude Code, OpenCode, and OpenClaw
- Lets the active agent session generate titles, summaries, and tags
- Still supports optional standalone shell automation with Codex CLI
- Writes compact Obsidian notes with frontmatter plus `摘要` and `页面摘录`

## Recommended flow

The recommended cross-client flow is:

1. Run browser export with the shell scripts
2. Let the current agent session read the exported JSON
3. Let the agent write the overrides JSON
4. Run the generator script to write final Obsidian notes

Before first use, set your Obsidian target directory in a local env file and use an absolute path.

For generic web capture:

```bash
WEB_CAPTURE_TO_OBSIDIAN_SKIP_GENERATE=1 ./scripts/organize_knowledge.sh "https://github.com/openai/openai-python"
python3 scripts/generate_knowledge_obsidian_notes.py
```

For X bookmarks:

```bash
X_BOOKMARKS_SKIP_GENERATE=1 ./scripts/sync_x_bookmarks.sh
python3 scripts/generate_x_obsidian_notes.py
```

In normal skill usage, the active agent session should create the overrides JSON itself.

Generic overrides shape:

- [`web_capture_to_obsidian_llm_overrides.example.json`](./web_capture_to_obsidian_llm_overrides.example.json)

X bookmark overrides shape:

- [`x_bookmarks_llm_overrides.example.json`](./x_bookmarks_llm_overrides.example.json)

## Standalone shell automation

Standalone shell automation is still available:

```bash
./scripts/organize_knowledge.sh "https://github.com/openai/openai-python"
./scripts/sync_x_bookmarks.sh
```

In that mode, the LLM enhancement step uses the local `codex` CLI. If you do not want that dependency, either disable LLM participation or use the recommended agent-driven flow above.

## Installation in AI clients

Public Git URL:

```text
https://github.com/noroot777/web-capture-to-obsidian.git
```

The install directory and skill name should use `web-capture-to-obsidian`. You can also use the local symlink examples.

### Codex

Install path:

```text
~/.codex/skills/web-capture-to-obsidian
```

Clone example:

```bash
git clone https://github.com/noroot777/web-capture-to-obsidian.git ~/.codex/skills/web-capture-to-obsidian
```

Symlink example:

```bash
ln -s /path/to/web-capture-to-obsidian ~/.codex/skills/web-capture-to-obsidian
```

Invocation example:

- `Use $web-capture-to-obsidian to capture this link into Obsidian`
- `Use $web-capture-to-obsidian to sync my X bookmarks`

Chrome prerequisite:

- Open `chrome://inspect#remote-debugging`
- Enable remote debugging for the current Chrome session

### Claude Code

Install path:

```text
~/.claude/skills/web-capture-to-obsidian
```

Clone example:

```bash
git clone https://github.com/noroot777/web-capture-to-obsidian.git ~/.claude/skills/web-capture-to-obsidian
```

Symlink example:

```bash
ln -s /path/to/web-capture-to-obsidian ~/.claude/skills/web-capture-to-obsidian
```

Invocation example:

- `/web-capture-to-obsidian https://mp.weixin.qq.com/s/...`
- `Capture this GitHub page with web-capture-to-obsidian`

Chrome prerequisite:

- Open `chrome://inspect#remote-debugging`
- Enable remote debugging for the current Chrome session

### OpenCode

Install path:

```text
~/.config/opencode/skills/web-capture-to-obsidian
```

Clone example:

```bash
git clone https://github.com/noroot777/web-capture-to-obsidian.git ~/.config/opencode/skills/web-capture-to-obsidian
```

Symlink example:

```bash
ln -s /path/to/web-capture-to-obsidian ~/.config/opencode/skills/web-capture-to-obsidian
```

Invocation example:

- `Use the web-capture-to-obsidian skill to capture this link`
- `Use the web-capture-to-obsidian skill to sync my X bookmarks`

Chrome prerequisite:

- Open `chrome://inspect#remote-debugging`
- Enable remote debugging for the current Chrome session

Notes:

- OpenCode also discovers compatible skills from `.claude/skills/` and `.agents/skills/`, but the standard install location in this README is `~/.config/opencode/skills/`.

### OpenClaw

Install path:

```text
~/.openclaw/workspace/skills/web-capture-to-obsidian
```

Clone example:

```bash
git clone https://github.com/noroot777/web-capture-to-obsidian.git ~/.openclaw/workspace/skills/web-capture-to-obsidian
```

Symlink example:

```bash
ln -s /path/to/web-capture-to-obsidian ~/.openclaw/workspace/skills/web-capture-to-obsidian
```

Invocation example:

- `Use the web-capture-to-obsidian skill to save this article to Obsidian`
- `Use the web-capture-to-obsidian skill to sync my X bookmarks`

Chrome prerequisite:

- Open `chrome://inspect#remote-debugging`
- Enable remote debugging for the current Chrome session

## Workflows

### 1. Capture one link or pasted text

Use:

```bash
./scripts/organize_knowledge.sh "https://github.com/openai/openai-python"
```

You can also paste a paragraph that contains multiple URLs:

```bash
./scripts/organize_knowledge.sh "Capture these: https://mp.weixin.qq.com/s/... and https://x.com/.../status/123"
```

Or pipe text in:

```bash
pbpaste | ./scripts/organize_knowledge.sh
```

### 2. Sync full X bookmarks

Use:

```bash
./scripts/sync_x_bookmarks.sh
```

## Configuration

For generic capture:

```text
web_capture_to_obsidian.env.example -> web_capture_to_obsidian.env
```

Main setting:

```bash
WEB_CAPTURE_TO_OBSIDIAN_TARGET_DIR="$HOME/path/to/your/Obsidian/folder"
```

Use an absolute path such as `/Users/your-name/Obsidian/Web Capture`.

For X bookmarks:

```text
x_bookmarks_sync.env.example -> x_bookmarks_sync.env
```

Main setting:

```bash
X_BOOKMARKS_TARGET_DIR="$HOME/path/to/your/Obsidian/folder"
```

Use an absolute path such as `/Users/your-name/Obsidian/X Bookmarks`.

Both flows support overriding:

- output directory
- state file path
- `DevToolsActivePort` path
- Chrome binary path
- timezone
- LLM override file path

Compatibility note:

- Legacy `knowledge-organizer` config file and environment variable names are still accepted, but `web-capture-to-obsidian` is now the canonical public name.
- On first use, the shell scripts now stop with a clear message until the Obsidian target directory is configured.

## Output

### Generic web capture

Default output path:

```text
~/Obsidian/Web Capture to Obsidian
```

Files include:

- numbered notes
- `000 - 网页采集索引.md`
- `.web_capture_to_obsidian_state.json`

### X bookmarks sync

Default output path:

```text
~/Obsidian/X Bookmarks
```

Files include:

- numbered notes
- `000 - X 书签索引.md`
- `.x_bookmarks_state.json`

## Requirements

Base capture requirements:

- macOS
- Google Chrome
- Chrome 144+ for the current-session remote-debugging flow
- Python 3
- `npm`

Optional agent/runtime requirements:

- one of: Codex, Claude Code, OpenCode, or OpenClaw

Optional standalone automation requirement:

- Codex CLI if you want the shell scripts themselves to perform LLM enhancement automatically

If `dev-browser` is missing, the scripts install it automatically.

## One-time Chrome setup

1. Open Chrome
2. Visit `chrome://inspect#remote-debugging`
3. Enable remote debugging for the active browser session

If Chrome later shows a permission dialog, click `Allow` and rerun the command.

## Supported sources

- WeChat public article pages
- GitHub repositories, issues, pull requests, and discussions
- X / Twitter post pages
- Generic webpages accessible from your current Chrome session

## Repository layout

- `SKILL.md`: shared skill definition for all supported clients
- `scripts/organize_knowledge.sh`: generic URL/text capture entrypoint
- `scripts/export_knowledge_pages.devbrowser.js`: multi-source page capture
- `scripts/generate_knowledge_llm_overrides.py`: optional standalone Codex automation helper for generic links
- `scripts/generate_knowledge_obsidian_notes.py`: generic Obsidian note generation
- `scripts/sync_x_bookmarks.sh`: full X bookmarks sync
- `scripts/generate_x_llm_overrides.py`: optional standalone Codex automation helper for X bookmarks
- `scripts/generate_x_obsidian_notes.py`: X bookmark note generation

## Notes

- This package is cross-client at the skill level: the same `SKILL.md` works across Codex, Claude Code, OpenCode, and OpenClaw.
- The default cross-client LLM path is agent-driven, not CLI-runner-driven.
- Standalone Codex shell automation remains supported, but it is optional.
