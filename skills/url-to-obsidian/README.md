# url-to-obsidian

**English** | [中文](#中文)

Grab one or more URLs from your Chrome session and turn them into Obsidian notes. Works with WeChat articles, GitHub pages, X/Twitter posts, and any normal website.

Part of [web-capture-to-obsidian](../../). For X bookmark sync, see [x-bookmarks-to-obsidian](../x-bookmarks-to-obsidian/).

## Setup

```bash
cp url_to_obsidian.env.example url_to_obsidian.env
```

Set your Obsidian path (must be absolute):

```
URL_TO_OBSIDIAN_TARGET_DIR="/Users/you/Obsidian/URL Capture"
```

Make sure Chrome remote debugging is on: `chrome://inspect#remote-debugging`.

## Usage

**Capture a page:**

```bash
./scripts/url_to_obsidian.sh "https://github.com/openai/openai-python"
```

**Multiple URLs at once:**

```bash
./scripts/url_to_obsidian.sh "https://mp.weixin.qq.com/s/abc and https://x.com/user/status/123"
```

**From clipboard:**

```bash
pbpaste | ./scripts/url_to_obsidian.sh
```

## Agent workflow

When running inside an AI agent (Codex, Claude Code, etc.), let the agent handle title/summary/tag generation:

```bash
# 1. Export only
URL_TO_OBSIDIAN_SKIP_GENERATE=1 ./scripts/url_to_obsidian.sh "https://..."

# 2. Agent reads ~/.dev-browser/tmp/url-to-obsidian-export.json
# 3. Agent writes overrides to ~/.dev-browser/tmp/url-to-obsidian-llm-overrides.json

# 4. Generate notes
python3 scripts/generate_url_obsidian_notes.py
```

Override format: [`url_to_obsidian_llm_overrides.example.json`](url_to_obsidian_llm_overrides.example.json)

## Output

Notes go to `URL_TO_OBSIDIAN_TARGET_DIR` (default `~/Obsidian/URL to Obsidian`):

- Numbered Markdown notes with frontmatter + summary + excerpts
- `000 - URL 采集索引.md` — index file
- `.url_to_obsidian_state.json` — state for incremental runs

## Config

All optional. See [`url_to_obsidian.env.example`](url_to_obsidian.env.example) for the full list: LLM model, Chrome binary path, DevToolsActivePort path, timezone, etc.

## Files

| | |
|---|---|
| `SKILL.md` | Skill definition for AI clients |
| `scripts/url_to_obsidian.sh` | Main entry point |
| `scripts/export_urls.devbrowser.js` | Chrome automation |
| `scripts/extract_input_urls.py` | URL extraction from text |
| `scripts/generate_url_obsidian_notes.py` | JSON → Obsidian notes |
| `scripts/generate_url_llm_overrides.py` | Standalone Codex LLM helper |

---

<a id="中文"></a>

# url-to-obsidian

[English](#url-to-obsidian) | **中文**

从你的 Chrome 里抓一个或多个 URL，变成 Obsidian 笔记。微信文章、GitHub 页面、X 帖子、普通网页都行。

属于 [web-capture-to-obsidian](../../) 仓库。X 书签同步看 [x-bookmarks-to-obsidian](../x-bookmarks-to-obsidian/)。

## 配置

```bash
cp url_to_obsidian.env.example url_to_obsidian.env
```

填 Obsidian 目录（必须绝对路径）：

```
URL_TO_OBSIDIAN_TARGET_DIR="/Users/你的用户名/Obsidian/URL Capture"
```

Chrome 远程调试要先开：`chrome://inspect#remote-debugging`。

## 用法

**抓一个页面：**

```bash
./scripts/url_to_obsidian.sh "https://github.com/openai/openai-python"
```

**一次抓多个：**

```bash
./scripts/url_to_obsidian.sh "https://mp.weixin.qq.com/s/abc 还有 https://x.com/user/status/123"
```

**从剪贴板读：**

```bash
pbpaste | ./scripts/url_to_obsidian.sh
```

## Agent 工作流

在 AI agent（Codex、Claude Code 等）里用的话，让 agent 生成标题/摘要/标签：

```bash
# 1. 只导出
URL_TO_OBSIDIAN_SKIP_GENERATE=1 ./scripts/url_to_obsidian.sh "https://..."

# 2. Agent 读 ~/.dev-browser/tmp/url-to-obsidian-export.json
# 3. Agent 写 overrides 到 ~/.dev-browser/tmp/url-to-obsidian-llm-overrides.json

# 4. 生成笔记
python3 scripts/generate_url_obsidian_notes.py
```

overrides 格式：[`url_to_obsidian_llm_overrides.example.json`](url_to_obsidian_llm_overrides.example.json)

## 输出

笔记写到 `URL_TO_OBSIDIAN_TARGET_DIR`（默认 `~/Obsidian/URL to Obsidian`）：

- 编号 Markdown 笔记，带 frontmatter + 摘要 + 页面摘录
- `000 - URL 采集索引.md` —— 索引
- `.url_to_obsidian_state.json` —— 增量运行状态

## 配置项

都是可选的。完整列表看 [`url_to_obsidian.env.example`](url_to_obsidian.env.example)：LLM 模型、Chrome 路径、DevToolsActivePort 路径、时区等。

## 文件

| | |
|---|---|
| `SKILL.md` | 给 AI 客户端的 skill 定义 |
| `scripts/url_to_obsidian.sh` | 入口脚本 |
| `scripts/export_urls.devbrowser.js` | Chrome 自动化 |
| `scripts/extract_input_urls.py` | 从文本提取 URL |
| `scripts/generate_url_obsidian_notes.py` | JSON → Obsidian 笔记 |
| `scripts/generate_url_llm_overrides.py` | 独立 Codex LLM 辅助 |
