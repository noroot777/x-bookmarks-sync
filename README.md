# Web Capture to Obsidian

[中文说明](./README.zh-CN.md)

Save web pages as Obsidian notes. Give it a URL, paste a chunk of text with links scattered in it, or let it pull your full X bookmarks — it'll extract the content via your real Chrome session and write clean Markdown notes with frontmatter.

Works with WeChat articles, GitHub (repos/issues/PRs/discussions), X posts, and basically anything your Chrome can open. No separate login needed — it talks to your already-logged-in browser through Chrome's remote debugging protocol.

> Formerly `x-bookmarks-sync`. X bookmark sync is still supported, it's just one of the workflows now.

## Get started

You need macOS, Chrome 144+, Python 3, and npm.

**1. Turn on Chrome remote debugging (once):**

Go to `chrome://inspect#remote-debugging` and enable it. That's the only Chrome setup.

**2. Set your Obsidian directory:**

```bash
cp web_capture_to_obsidian.env.example web_capture_to_obsidian.env
```

Open the file, put in your absolute Obsidian path:

```
WEB_CAPTURE_TO_OBSIDIAN_TARGET_DIR="/Users/you/Obsidian/Web Capture"
```

**3. Capture something:**

```bash
./scripts/organize_knowledge.sh "https://github.com/openai/openai-python"
```

Done. You'll find a numbered note in your Obsidian folder with a summary and key excerpts.

Multiple URLs in one go? Sure:

```bash
./scripts/organize_knowledge.sh "https://mp.weixin.qq.com/s/abc and https://x.com/user/status/123"
```

Or from clipboard:

```bash
pbpaste | ./scripts/organize_knowledge.sh
```

### X bookmarks

```bash
cp x_bookmarks_sync.env.example x_bookmarks_sync.env
# set X_BOOKMARKS_TARGET_DIR to your Obsidian path
./scripts/sync_x_bookmarks.sh
```

## Two modes

### With an AI agent (recommended)

When you're working inside Codex, Claude Code, OpenCode, or OpenClaw, the agent handles the smart part — generating titles, summaries, and tags. The shell script just does the browser export:

```bash
WEB_CAPTURE_TO_OBSIDIAN_SKIP_GENERATE=1 ./scripts/organize_knowledge.sh "https://..."
```

The agent reads the exported JSON, writes an overrides file, then you run the generator:

```bash
python3 scripts/generate_knowledge_obsidian_notes.py
```

X bookmarks work the same way — `X_BOOKMARKS_SKIP_GENERATE=1 ./scripts/sync_x_bookmarks.sh` then `python3 scripts/generate_x_obsidian_notes.py`.

Override format examples: [`web_capture_to_obsidian_llm_overrides.example.json`](./web_capture_to_obsidian_llm_overrides.example.json), [`x_bookmarks_llm_overrides.example.json`](./x_bookmarks_llm_overrides.example.json).

### Without an agent

Run the scripts without the skip flag and they'll call `codex` CLI locally to do the LLM work:

```bash
./scripts/organize_knowledge.sh "https://..."
```

Requires `codex` to be installed. If you don't have it, just use agent mode.

## Install as an AI skill

Put it in the skill directory for your client:

| Client | Install to |
|---|---|
| Codex | `~/.codex/skills/web-capture-to-obsidian` |
| Claude Code | `~/.claude/skills/web-capture-to-obsidian` |
| OpenCode | `~/.config/opencode/skills/web-capture-to-obsidian` |
| OpenClaw | `~/.openclaw/workspace/skills/web-capture-to-obsidian` |

```bash
git clone https://github.com/noroot777/web-capture-to-obsidian.git ~/.codex/skills/web-capture-to-obsidian
# or symlink:
ln -s /your/local/clone ~/.codex/skills/web-capture-to-obsidian
```

Then tell your agent: *"Use web-capture-to-obsidian to capture this link"* — each client recognizes the skill from the shared `SKILL.md`.

OpenCode also scans `.claude/skills/` and `.agents/skills/`.

## Config reference

Both env files accept: output directory, state file path, Chrome binary, `DevToolsActivePort` path, timezone, and override file path.

Old `knowledge-organizer` variable names still work. If the target directory isn't set, the script stops with a clear error on first run.

## What gets written

Web capture goes to `~/Obsidian/Web Capture to Obsidian` by default — numbered notes, an index (`000 - 网页采集索引.md`), and a state file. X bookmarks go to `~/Obsidian/X Bookmarks` with the same layout.

## Files in this repo

| | |
|---|---|
| `SKILL.md` | Skill definition read by Codex / Claude Code / OpenCode / OpenClaw |
| `scripts/organize_knowledge.sh` | Web capture entry point |
| `scripts/sync_x_bookmarks.sh` | X bookmark sync entry point |
| `scripts/export_knowledge_pages.devbrowser.js` | Drives Chrome to extract page content |
| `scripts/generate_knowledge_obsidian_notes.py` | JSON → Obsidian notes |
| `scripts/generate_x_obsidian_notes.py` | X bookmark data → Obsidian notes |
| `scripts/generate_knowledge_llm_overrides.py` | Codex CLI helper for web capture |
| `scripts/generate_x_llm_overrides.py` | Codex CLI helper for X bookmarks |

## License

[MIT](./LICENSE)
