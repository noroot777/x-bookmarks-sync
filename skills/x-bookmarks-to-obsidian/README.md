# x-bookmarks-to-obsidian

**English** | [中文](#中文)

Sync your full X bookmark list into Obsidian notes, using your real logged-in Chrome session.

Part of [web-capture-to-obsidian](../../). For capturing regular URLs, see [url-to-obsidian](../url-to-obsidian/).

## Setup

```bash
cp x_bookmarks_to_obsidian.env.example x_bookmarks_to_obsidian.env
```

Set your Obsidian path (must be absolute):

```
X_BOOKMARKS_TO_OBSIDIAN_TARGET_DIR="/Users/you/Obsidian/X Bookmarks"
```

Make sure Chrome remote debugging is on: `chrome://inspect#remote-debugging`.

## Usage

```bash
./scripts/x_bookmarks_to_obsidian.sh
```

It opens `https://x.com/i/bookmarks` in your Chrome, scrolls through the feed, and exports everything.

## Agent workflow

When running inside an AI agent (Codex, Claude Code, etc.), let the agent handle title/summary/tag generation:

```bash
# 1. Export only
X_BOOKMARKS_TO_OBSIDIAN_SKIP_GENERATE=1 ./scripts/x_bookmarks_to_obsidian.sh

# 2. Agent reads ~/.dev-browser/tmp/x-bookmarks-to-obsidian-export.json
# 3. Agent writes overrides to ~/.dev-browser/tmp/x-bookmarks-to-obsidian-llm-overrides.json

# 4. Generate notes
python3 scripts/generate_x_bookmarks_obsidian_notes.py
```

Override format: [`x_bookmarks_to_obsidian_llm_overrides.example.json`](x_bookmarks_to_obsidian_llm_overrides.example.json)

## Output

Notes go to `X_BOOKMARKS_TO_OBSIDIAN_TARGET_DIR` (default `~/Obsidian/X Bookmarks to Obsidian`):

- One note per bookmark with frontmatter + summary + excerpts
- `000 - X 书签索引.md` — index file
- `.x_bookmarks_to_obsidian_state.json` — state for incremental runs

## Config

All optional. See [`x_bookmarks_to_obsidian.env.example`](x_bookmarks_to_obsidian.env.example) for the full list: LLM model, Chrome binary path, DevToolsActivePort path, timezone, etc.

## Files

| | |
|---|---|
| `SKILL.md` | Skill definition for AI clients |
| `scripts/x_bookmarks_to_obsidian.sh` | Main entry point |
| `scripts/export_x_bookmarks.devbrowser.js` | Chrome automation — scrolls and exports bookmarks |
| `scripts/generate_x_bookmarks_obsidian_notes.py` | JSON → Obsidian notes |
| `scripts/generate_x_bookmarks_llm_overrides.py` | Standalone Codex LLM helper |

---

<a id="中文"></a>

# x-bookmarks-to-obsidian

[English](#x-bookmarks-to-obsidian) | **中文**

把你的 X 书签完整同步到 Obsidian 笔记，用的是你已经登录好的 Chrome。

属于 [web-capture-to-obsidian](../../) 仓库。抓普通 URL 用 [url-to-obsidian](../url-to-obsidian/)。

## 配置

```bash
cp x_bookmarks_to_obsidian.env.example x_bookmarks_to_obsidian.env
```

填 Obsidian 目录（必须绝对路径）：

```
X_BOOKMARKS_TO_OBSIDIAN_TARGET_DIR="/Users/你的用户名/Obsidian/X Bookmarks"
```

Chrome 远程调试要先开：`chrome://inspect#remote-debugging`。

## 用法

```bash
./scripts/x_bookmarks_to_obsidian.sh
```

它会在你的 Chrome 里打开 `https://x.com/i/bookmarks`，滚动整个列表，导出全部书签。

## Agent 工作流

在 AI agent（Codex、Claude Code 等）里用的话，让 agent 生成标题/摘要/标签：

```bash
# 1. 只导出
X_BOOKMARKS_TO_OBSIDIAN_SKIP_GENERATE=1 ./scripts/x_bookmarks_to_obsidian.sh

# 2. Agent 读 ~/.dev-browser/tmp/x-bookmarks-to-obsidian-export.json
# 3. Agent 写 overrides 到 ~/.dev-browser/tmp/x-bookmarks-to-obsidian-llm-overrides.json

# 4. 生成笔记
python3 scripts/generate_x_bookmarks_obsidian_notes.py
```

overrides 格式：[`x_bookmarks_to_obsidian_llm_overrides.example.json`](x_bookmarks_to_obsidian_llm_overrides.example.json)

## 输出

笔记写到 `X_BOOKMARKS_TO_OBSIDIAN_TARGET_DIR`（默认 `~/Obsidian/X Bookmarks to Obsidian`）：

- 每条书签一篇笔记，带 frontmatter + 摘要 + 摘录
- `000 - X 书签索引.md` —— 索引
- `.x_bookmarks_to_obsidian_state.json` —— 增量运行状态

## 配置项

都是可选的。完整列表看 [`x_bookmarks_to_obsidian.env.example`](x_bookmarks_to_obsidian.env.example)：LLM 模型、Chrome 路径、DevToolsActivePort 路径、时区等。

## 文件

| | |
|---|---|
| `SKILL.md` | 给 AI 客户端的 skill 定义 |
| `scripts/x_bookmarks_to_obsidian.sh` | 入口脚本 |
| `scripts/export_x_bookmarks.devbrowser.js` | Chrome 自动化——滚动并导出书签 |
| `scripts/generate_x_bookmarks_obsidian_notes.py` | JSON → Obsidian 笔记 |
| `scripts/generate_x_bookmarks_llm_overrides.py` | 独立 Codex LLM 辅助 |
