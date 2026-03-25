# Web Capture to Obsidian

**English** | [中文](#中文)

Two AI agent skills that turn browser content into Obsidian notes, powered by your real Chrome session.

| Skill | What it does |
|---|---|
| [url-to-obsidian](./skills/url-to-obsidian/) | Capture any URL — WeChat, GitHub, X, or generic pages |
| [x-bookmarks-to-obsidian](./skills/x-bookmarks-to-obsidian/) | Sync your full X bookmark list |

Both work across Codex, Claude Code, OpenCode, and OpenClaw. They talk to your logged-in Chrome via remote debugging, so no cookies to export, no extra login.

## Requirements

macOS, Chrome 144+, Python 3, npm.

One-time Chrome setup: open `chrome://inspect#remote-debugging` and turn it on.

## Install

Each skill is a self-contained folder under `skills/`. Install whichever you need:

**Codex / Claude Code / OpenClaw** — symlink or copy the skill folder:

```bash
ln -s /path/to/web-capture-to-obsidian/skills/url-to-obsidian ~/.codex/skills/url-to-obsidian
ln -s /path/to/web-capture-to-obsidian/skills/x-bookmarks-to-obsidian ~/.codex/skills/x-bookmarks-to-obsidian
```

For Claude Code or OpenClaw, swap `~/.codex/skills` with your client's skills directory.

Or install from GitHub directly:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo noroot777/web-capture-to-obsidian \
  --path skills/url-to-obsidian
```

**OpenCode** — clone the whole repo so it can discover both skills:

```bash
git clone https://github.com/noroot777/web-capture-to-obsidian.git ~/.config/opencode/skills/web-capture-to-obsidian
```

## Repo structure

```
skills/
  url-to-obsidian/          ← general URL capture
  x-bookmarks-to-obsidian/  ← X bookmark sync
```

Each skill has its own SKILL.md, README, scripts, env example, and overrides example. See the individual READMEs for setup and usage details.

## License

[MIT](./LICENSE)

---

<a id="中文"></a>

# Web Capture to Obsidian

[English](#web-capture-to-obsidian) | **中文**

两个 AI agent skill，把浏览器内容变成 Obsidian 笔记。直接连你登录好的 Chrome，走 remote debugging。

| Skill | 干啥的 |
|---|---|
| [url-to-obsidian](./skills/url-to-obsidian/) | 抓任意 URL——微信、GitHub、X、普通网页 |
| [x-bookmarks-to-obsidian](./skills/x-bookmarks-to-obsidian/) | 同步完整的 X 书签列表 |

Codex、Claude Code、OpenCode、OpenClaw 都能用。不需要导 cookie，不用重新登录。

## 环境要求

macOS、Chrome 144+、Python 3、npm。

Chrome 只要设置一次：打开 `chrome://inspect#remote-debugging`，开启远程调试。

## 安装

每个 skill 是 `skills/` 下的独立目录，装你需要的就行：

**Codex / Claude Code / OpenClaw** —— 软链接或复制 skill 目录：

```bash
ln -s /path/to/web-capture-to-obsidian/skills/url-to-obsidian ~/.codex/skills/url-to-obsidian
ln -s /path/to/web-capture-to-obsidian/skills/x-bookmarks-to-obsidian ~/.codex/skills/x-bookmarks-to-obsidian
```

Claude Code 或 OpenClaw 把 `~/.codex/skills` 换成对应客户端的 skills 目录。

也可以从 GitHub 直接装：

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo noroot777/web-capture-to-obsidian \
  --path skills/url-to-obsidian
```

**OpenCode** —— 整仓 clone，它会自动发现两个 skill：

```bash
git clone https://github.com/noroot777/web-capture-to-obsidian.git ~/.config/opencode/skills/web-capture-to-obsidian
```

## 仓库结构

```
skills/
  url-to-obsidian/          ← 通用 URL 抓取
  x-bookmarks-to-obsidian/  ← X 书签同步
```

每个 skill 自带 SKILL.md、README、脚本、env 示例和 overrides 示例。具体用法看各自的 README。

## 许可

[MIT](./LICENSE)
