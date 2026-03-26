# x-bookmarks-to-obsidian

**English** | [中文](#中文)

Sync your full X bookmark list into Obsidian notes, with incremental updates. Uses your real logged-in Chrome session.

Part of [web-capture-to-obsidian](../../). For capturing regular URLs, see [url-to-obsidian](../url-to-obsidian/).

## Install

Tell your AI agent:

> Install the x-bookmarks-to-obsidian skill from GitHub repo noroot777/web-capture-to-obsidian, path skills/x-bookmarks-to-obsidian

For OpenCode, ask the agent to clone the whole repo into its skills directory.

## First-time setup

Tell your agent where your Obsidian vault is. The agent will create the env file automatically:

> Set up the x-bookmarks-to-obsidian skill. My Obsidian vault is at /Users/me/Obsidian/X Bookmarks

Prerequisites: Chrome 144+, Python 3, npm. Chrome remote debugging must be turned on once: `chrome://inspect#remote-debugging`.

## Usage

Talk to your agent in natural language:

> Sync my X bookmarks to Obsidian

> Refresh my X bookmark notes

## Agent Template

Use [`overrides_prompt_template.md`](overrides_prompt_template.md) when the current session needs to turn exported JSON into overrides JSON before the final `generate` step. The export step also writes an internal incremental-only JSON so the agent can analyze only newly added bookmarks.

## Output

Notes go to `X_BOOKMARKS_TO_OBSIDIAN_TARGET_DIR` (default `~/Obsidian/X Bookmarks to Obsidian`):

- One note per bookmark with frontmatter + summary + excerpts
- `000 - X 书签索引.md` — index file
- `.x_bookmarks_to_obsidian_state.json` — state for incremental runs

## Config

All optional. See [`x_bookmarks_to_obsidian.env.example`](x_bookmarks_to_obsidian.env.example) for the full list: Chrome binary path, DevToolsActivePort path, timezone, etc.

## Files

| | |
|---|---|
| `SKILL.md` | Skill definition — the agent reads this to know what to do |
| `scripts/x_bookmarks_to_obsidian.py` | Main cross-platform entry point |
| `scripts/export_x_bookmarks.devbrowser.js` | Chrome automation — scrolls and exports bookmarks |
| `scripts/generate_x_bookmarks_obsidian_notes.py` | JSON → Obsidian notes |

---

<a id="中文"></a>

# x-bookmarks-to-obsidian

[English](#x-bookmarks-to-obsidian) | **中文**

把你的 X 书签完整同步到 Obsidian 笔记，支持增量更新。用的是你已经登录好的 Chrome。

属于 [web-capture-to-obsidian](../../) 仓库。抓普通 URL 用 [url-to-obsidian](../url-to-obsidian/)。

## 安装

告诉你的 AI agent：

> 从 GitHub 仓库 noroot777/web-capture-to-obsidian 安装 x-bookmarks-to-obsidian skill，路径 skills/x-bookmarks-to-obsidian

OpenCode 的话，让 agent 把整个仓库 clone 到 skills 目录。

## 首次配置

告诉 agent 你的 Obsidian 笔记目录，agent 会自动创建 env 文件：

> 配置 x-bookmarks-to-obsidian skill，我的 Obsidian 目录是 /Users/我/Obsidian/X Bookmarks

环境要求：Chrome 144+、Python 3、npm。Chrome 远程调试要先开一次：`chrome://inspect#remote-debugging`。

## 使用

用自然语言跟 agent 说就行：

> 把我的 X 书签同步到 Obsidian

> 刷新一下我的 X 书签笔记

## Agent 模板

需要当前会话把导出 JSON 整理成 overrides JSON 时，直接参考 [`overrides_prompt_template.md`](overrides_prompt_template.md)，再执行最后的 `generate` 阶段。导出阶段还会额外写出一个内部使用的、仅包含新增书签的 JSON，方便 agent 只分析真正的增量内容。

## 输出

笔记写到 `X_BOOKMARKS_TO_OBSIDIAN_TARGET_DIR`（默认 `~/Obsidian/X Bookmarks to Obsidian`）：

- 每条书签一篇笔记，带 frontmatter + 摘要 + 摘录
- `000 - X 书签索引.md` —— 索引
- `.x_bookmarks_to_obsidian_state.json` —— 增量运行状态

## 配置项

都是可选的。完整列表看 [`x_bookmarks_to_obsidian.env.example`](x_bookmarks_to_obsidian.env.example)：Chrome 路径、DevToolsActivePort 路径、时区等。

## 文件

| | |
|---|---|
| `SKILL.md` | Skill 定义——agent 读这个来知道该怎么做 |
| `scripts/x_bookmarks_to_obsidian.py` | 跨平台主入口 |
| `scripts/export_x_bookmarks.devbrowser.js` | Chrome 自动化——滚动并导出书签 |
| `scripts/generate_x_bookmarks_obsidian_notes.py` | JSON → Obsidian 笔记 |
