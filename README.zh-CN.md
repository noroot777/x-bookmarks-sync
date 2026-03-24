# Web Capture to Obsidian

[English README](./README.md)

把网页变成 Obsidian 笔记。丢个链接进来，或者把一段夹杂着各种 URL 的文字贴进来，甚至直接拉你的 X 书签——它会用你正在用的 Chrome 去抓内容，然后写成带 frontmatter 的 Markdown 笔记。

微信公众号、GitHub（仓库/Issue/PR/Discussion）、X 帖子、普通网页都能抓。不用单独登录，因为它直接连你已经登录好的 Chrome，走的是 remote debugging。

> 前身是 `x-bookmarks-sync`。同步 X 书签的功能还在，现在只是其中一个工作流。

## 开始用

macOS + Chrome 144+ + Python 3 + npm。

**1. 开 Chrome 远程调试（只要做一次）：**

打开 `chrome://inspect#remote-debugging`，点开就行。

**2. 告诉它你的 Obsidian 目录在哪：**

```bash
cp web_capture_to_obsidian.env.example web_capture_to_obsidian.env
```

打开文件，填绝对路径：

```
WEB_CAPTURE_TO_OBSIDIAN_TARGET_DIR="/Users/你的用户名/Obsidian/Web Capture"
```

**3. 抓个页面试试：**

```bash
./scripts/organize_knowledge.sh "https://github.com/openai/openai-python"
```

搞定。Obsidian 里会多一篇编号笔记，带摘要和页面摘录。

一次丢多个链接也行：

```bash
./scripts/organize_knowledge.sh "https://mp.weixin.qq.com/s/abc 还有 https://x.com/user/status/123"
```

从剪贴板读：

```bash
pbpaste | ./scripts/organize_knowledge.sh
```

### 同步 X 书签

```bash
cp x_bookmarks_sync.env.example x_bookmarks_sync.env
# 填 X_BOOKMARKS_TARGET_DIR
./scripts/sync_x_bookmarks.sh
```

## 两种用法

### 配合 AI agent（推荐）

在 Codex、Claude Code、OpenCode 或 OpenClaw 里用的话，agent 负责生成标题、摘要和标签。Shell 脚本只管导出：

```bash
WEB_CAPTURE_TO_OBSIDIAN_SKIP_GENERATE=1 ./scripts/organize_knowledge.sh "https://..."
```

Agent 读完导出的 JSON、写好 overrides 之后，跑生成脚本就行：

```bash
python3 scripts/generate_knowledge_obsidian_notes.py
```

X 书签一样——先 `X_BOOKMARKS_SKIP_GENERATE=1 ./scripts/sync_x_bookmarks.sh`，再 `python3 scripts/generate_x_obsidian_notes.py`。

overrides 的格式看这俩示例：[`web_capture_to_obsidian_llm_overrides.example.json`](./web_capture_to_obsidian_llm_overrides.example.json)、[`x_bookmarks_llm_overrides.example.json`](./x_bookmarks_llm_overrides.example.json)。

### 不用 agent 也行

不加 skip 标志直接跑，脚本会自己调本机的 `codex` CLI 做 LLM 那步：

```bash
./scripts/organize_knowledge.sh "https://..."
```

需要装 `codex`。没装就用 agent 模式。

## 装到 AI 客户端

放进对应 client 的 skill 目录就行：

| Client | 装到这 |
|---|---|
| Codex | `~/.codex/skills/web-capture-to-obsidian` |
| Claude Code | `~/.claude/skills/web-capture-to-obsidian` |
| OpenCode | `~/.config/opencode/skills/web-capture-to-obsidian` |
| OpenClaw | `~/.openclaw/workspace/skills/web-capture-to-obsidian` |

```bash
git clone https://github.com/noroot777/web-capture-to-obsidian.git ~/.codex/skills/web-capture-to-obsidian
# 或者本地有了直接软链接：
ln -s /你的本地仓库 ~/.codex/skills/web-capture-to-obsidian
```

然后跟 agent 说"用 web-capture-to-obsidian 抓这个链接"就行，四个 client 都认同一份 `SKILL.md`。

OpenCode 还会扫 `.claude/skills/` 和 `.agents/skills/`。

## 配置项

两个 env 文件都支持改：输出目录、状态文件路径、Chrome 路径、`DevToolsActivePort` 路径、时区、overrides 文件路径。

以前叫 `knowledge-organizer` 的那套变量名还能用。目标目录没配的话第一次跑会报错停住。

## 输出

网页抓取默认写到 `~/Obsidian/Web Capture to Obsidian`——编号笔记 + 索引（`000 - 网页采集索引.md`）+ 状态文件。X 书签默认写到 `~/Obsidian/X Bookmarks`，一样的结构。

## 仓库文件

| | |
|---|---|
| `SKILL.md` | Codex / Claude Code / OpenCode / OpenClaw 共用的 skill 定义 |
| `scripts/organize_knowledge.sh` | 网页抓取入口 |
| `scripts/sync_x_bookmarks.sh` | X 书签同步入口 |
| `scripts/export_knowledge_pages.devbrowser.js` | 驱动 Chrome 抓页面内容 |
| `scripts/generate_knowledge_obsidian_notes.py` | JSON → Obsidian 笔记 |
| `scripts/generate_x_obsidian_notes.py` | X 书签 → Obsidian 笔记 |
| `scripts/generate_knowledge_llm_overrides.py` | 网页抓取的 Codex CLI 辅助 |
| `scripts/generate_x_llm_overrides.py` | X 书签的 Codex CLI 辅助 |

## License

[MIT](./LICENSE)
