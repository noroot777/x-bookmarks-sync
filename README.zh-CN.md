# Web Capture to Obsidian

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
![Platform: macOS](https://img.shields.io/badge/platform-macOS-black)
![Chrome: 144+](https://img.shields.io/badge/Chrome-144%2B-blue)
![Agent Friendly](https://img.shields.io/badge/agent-friendly-orange)

[English README](./README.md)

`web-capture-to-obsidian` 是一个跨 client 的 Agent Skill 包，目标是把网页内容抓取并整理进 Obsidian。

它支持：

- 单个链接
- 从一段文本里提取一个或多个 URL
- 微信公众号、GitHub、X 和普通网页
- 原来的完整 X 书签同步流程

这个项目最早来自 `x-bookmarks-sync`，但现在范围已经更大了：重点是网页采集进 Obsidian，X 书签同步只是同一个包里的一个工作流。

## 一眼看懂

- 复用你当前真实登录着的 Chrome 会话
- 用 `dev-browser` 做稳定、可重复的浏览器自动化
- 同一份 `SKILL.md` 可被 Codex、Claude Code、OpenCode、OpenClaw 使用
- 默认由当前 agent 会话负责生成标题、摘要、标签
- 仍然保留基于 Codex CLI 的独立 shell 自动化模式
- 输出成适合 Obsidian 的精简笔记，正文只保留 `摘要` 和 `页面摘录`

## 推荐工作流

推荐的跨 client 流程是：

1. 先用 shell 脚本做浏览器导出
2. 让当前 agent 会话读取导出的 JSON
3. 让 agent 写 overrides JSON
4. 再调用生成脚本落盘到 Obsidian

首次使用前，先在本地 env 文件里设置 Obsidian 保存目录，并且必须使用绝对路径。

通用网页抓取：

```bash
WEB_CAPTURE_TO_OBSIDIAN_SKIP_GENERATE=1 ./scripts/organize_knowledge.sh "https://github.com/openai/openai-python"
python3 scripts/generate_knowledge_obsidian_notes.py
```

X 书签同步：

```bash
X_BOOKMARKS_SKIP_GENERATE=1 ./scripts/sync_x_bookmarks.sh
python3 scripts/generate_x_obsidian_notes.py
```

在正常的 skill 使用方式里，`title / summary / tags` 这一步应该由当前 agent 会话自己生成。

通用网页 overrides 格式：

- [`web_capture_to_obsidian_llm_overrides.example.json`](./web_capture_to_obsidian_llm_overrides.example.json)

X 书签 overrides 格式：

- [`x_bookmarks_llm_overrides.example.json`](./x_bookmarks_llm_overrides.example.json)

## 独立 shell 自动化

也保留独立 shell 自动化模式：

```bash
./scripts/organize_knowledge.sh "https://github.com/openai/openai-python"
./scripts/sync_x_bookmarks.sh
```

在这种模式下，脚本自己的 LLM 增强步骤会调用本机 `codex` CLI。如果你不想依赖它，可以关闭 LLM，或者改用上面的 agent 驱动流程。

## 安装到 AI 客户端

公开 Git 地址：

```text
https://github.com/noroot777/web-capture-to-obsidian.git
```

安装目录和 skill 名称统一使用 `web-capture-to-obsidian`；如果你本地已经有一份仓库，也可以直接用软链接方式安装。

### Codex

安装路径：

```text
~/.codex/skills/web-capture-to-obsidian
```

clone 示例：

```bash
git clone https://github.com/noroot777/web-capture-to-obsidian.git ~/.codex/skills/web-capture-to-obsidian
```

软链接示例：

```bash
ln -s /path/to/web-capture-to-obsidian ~/.codex/skills/web-capture-to-obsidian
```

调用示例：

- `Use $web-capture-to-obsidian to capture this link into Obsidian`
- `Use $web-capture-to-obsidian to sync my X bookmarks`

Chrome 前置要求：

- 打开 `chrome://inspect#remote-debugging`
- 为当前 Chrome 会话开启 remote debugging

### Claude Code

安装路径：

```text
~/.claude/skills/web-capture-to-obsidian
```

clone 示例：

```bash
git clone https://github.com/noroot777/web-capture-to-obsidian.git ~/.claude/skills/web-capture-to-obsidian
```

软链接示例：

```bash
ln -s /path/to/web-capture-to-obsidian ~/.claude/skills/web-capture-to-obsidian
```

调用示例：

- `/web-capture-to-obsidian https://mp.weixin.qq.com/s/...`
- `Capture this GitHub page with web-capture-to-obsidian`

Chrome 前置要求：

- 打开 `chrome://inspect#remote-debugging`
- 为当前 Chrome 会话开启 remote debugging

### OpenCode

安装路径：

```text
~/.config/opencode/skills/web-capture-to-obsidian
```

clone 示例：

```bash
git clone https://github.com/noroot777/web-capture-to-obsidian.git ~/.config/opencode/skills/web-capture-to-obsidian
```

软链接示例：

```bash
ln -s /path/to/web-capture-to-obsidian ~/.config/opencode/skills/web-capture-to-obsidian
```

调用示例：

- `Use the web-capture-to-obsidian skill to capture this link`
- `Use the web-capture-to-obsidian skill to sync my X bookmarks`

Chrome 前置要求：

- 打开 `chrome://inspect#remote-debugging`
- 为当前 Chrome 会话开启 remote debugging

说明：

- OpenCode 也能识别 `.claude/skills/` 和 `.agents/skills/` 下的兼容 skill，但这份 README 统一采用 `~/.config/opencode/skills/` 作为标准安装路径。

### OpenClaw

安装路径：

```text
~/.openclaw/workspace/skills/web-capture-to-obsidian
```

clone 示例：

```bash
git clone https://github.com/noroot777/web-capture-to-obsidian.git ~/.openclaw/workspace/skills/web-capture-to-obsidian
```

软链接示例：

```bash
ln -s /path/to/web-capture-to-obsidian ~/.openclaw/workspace/skills/web-capture-to-obsidian
```

调用示例：

- `Use the web-capture-to-obsidian skill to save this article to Obsidian`
- `Use the web-capture-to-obsidian skill to sync my X bookmarks`

Chrome 前置要求：

- 打开 `chrome://inspect#remote-debugging`
- 为当前 Chrome 会话开启 remote debugging

## 两条工作流

### 1. 抓取单个链接或一段文本

用法：

```bash
./scripts/organize_knowledge.sh "https://github.com/openai/openai-python"
```

也可以给一段包含多个 URL 的文本：

```bash
./scripts/organize_knowledge.sh "Capture these: https://mp.weixin.qq.com/s/... and https://x.com/.../status/123"
```

也支持标准输入：

```bash
pbpaste | ./scripts/organize_knowledge.sh
```

### 2. 同步完整 X 书签

用法：

```bash
./scripts/sync_x_bookmarks.sh
```

## 配置方式

通用网页抓取使用：

```text
web_capture_to_obsidian.env.example -> web_capture_to_obsidian.env
```

最常改的是：

```bash
WEB_CAPTURE_TO_OBSIDIAN_TARGET_DIR="$HOME/你的/Obsidian/目录"
```

请使用绝对路径，例如 `/Users/your-name/Obsidian/Web Capture`。

X 书签同步继续使用：

```text
x_bookmarks_sync.env.example -> x_bookmarks_sync.env
```

最常改的是：

```bash
X_BOOKMARKS_TARGET_DIR="$HOME/你的/Obsidian/目录"
```

请使用绝对路径，例如 `/Users/your-name/Obsidian/X Bookmarks`。

两条流程都支持覆盖：

- 输出目录
- 状态文件路径
- `DevToolsActivePort` 路径
- Chrome 可执行文件路径
- 时区
- overrides 文件路径

兼容说明：

- 老的 `knowledge-organizer` 配置文件名和环境变量名仍然可用，但公开主名称已经统一改为 `web-capture-to-obsidian`。
- 现在 shell 脚本在首次使用时会先检查是否已经配置 Obsidian 绝对路径；没配置就会直接提示并停止执行。

## 输出位置

### 通用网页抓取

默认输出：

```text
~/Obsidian/Web Capture to Obsidian
```

会生成：

- 编号笔记
- `000 - 网页采集索引.md`
- `.web_capture_to_obsidian_state.json`

### X 书签同步

默认输出：

```text
~/Obsidian/X Bookmarks
```

会生成：

- 编号笔记
- `000 - X 书签索引.md`
- `.x_bookmarks_state.json`

## 依赖要求

基础抓取依赖：

- macOS
- Google Chrome
- Chrome 144+
- Python 3
- `npm`

可选 agent/runtime 依赖：

- Codex、Claude Code、OpenCode、OpenClaw 四选一即可

可选独立自动化依赖：

- 如果你希望 shell 脚本自己自动完成 LLM 增强，需要本机安装 Codex CLI

如果本机没有安装 `dev-browser`，脚本会自动安装。

## Chrome 一次性准备

1. 打开 Chrome
2. 访问 `chrome://inspect#remote-debugging`
3. 为当前浏览器会话开启 remote debugging

如果之后 Chrome 弹出授权框，点 `Allow` 后重新执行命令即可。

## 支持的来源

- 微信公众号文章
- GitHub 仓库、Issue、PR、Discussion
- X / Twitter 帖子页面
- 当前 Chrome 会话里能正常打开的普通网页

## 仓库结构

- `SKILL.md`：四个 client 共用的 skill 定义
- `scripts/organize_knowledge.sh`：通用 URL / 文本抓取入口
- `scripts/export_knowledge_pages.devbrowser.js`：多来源网页抓取
- `scripts/generate_knowledge_llm_overrides.py`：通用网页的可选 Codex 独立自动化助手
- `scripts/generate_knowledge_obsidian_notes.py`：通用网页笔记生成
- `scripts/sync_x_bookmarks.sh`：X 全量书签同步
- `scripts/generate_x_llm_overrides.py`：X 书签的可选 Codex 独立自动化助手
- `scripts/generate_x_obsidian_notes.py`：X 书签笔记生成

## 说明

- 这是“skill 层面跨 client 兼容”的方案：同一份 `SKILL.md` 供 Codex、Claude Code、OpenCode、OpenClaw 使用。
- 默认的跨 client LLM 路径是“当前 agent 会话生成 overrides”，不是“所有 client 都实现一套统一的 headless CLI runner”。
- 基于 Codex CLI 的独立 shell 自动化仍然保留，但它现在是可选模式，不再是这个项目的唯一主路径。
