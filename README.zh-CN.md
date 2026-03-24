# X 书签同步

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
![Platform: macOS](https://img.shields.io/badge/platform-macOS-black)
![Chrome: 144+](https://img.shields.io/badge/Chrome-144%2B-blue)
![Codex Skill](https://img.shields.io/badge/Codex-skill-orange)

[English README](./README.md)

通过复用你已经登录的 Chrome 会话，把 `X.com` 书签同步成 Obsidian 笔记。

## 一眼看懂

- 借用你当前已经登录的 Chrome 会话，而不是单独处理登录
- 从 `https://x.com/i/bookmarks` 导出书签
- 为每条书签生成一篇 Obsidian Markdown 笔记
- 多次同步时保持稳定递增编号
- 编号按收藏列表顺序分配，从列表底部最老的书签开始

这个 skill 适合下面这种场景：

- 你已经在 Chrome 里登录了 X
- 你想把每条书签落成一篇 Obsidian 笔记
- 你希望编号稳定，不要每次同步都重排旧文件
- 你希望后续同步只给新书签继续追加编号

## 功能

- 通过 Chrome 远程调试连接你当前正在使用的浏览器会话
- 读取 `https://x.com/i/bookmarks`
- 为每条书签生成一篇 Markdown 笔记
- 使用稳定文件名，例如：

```text
001 - 标题 - YYYY-MM-DD HHMMSS - 作者.md
002 - 标题 - YYYY-MM-DD HHMMSS - 作者.md
```

- 编号按收藏列表顺序倒序分配：
  - 收藏列表最下面、最老的那条是 `001`
  - 越靠上、越新的收藏编号越大

- 同时维护：
  - `000 - X 书签索引.md`
  - `.x_bookmarks_state.json`

## 当前默认输出路径

默认写入：

```text
~/Obsidian/X Bookmarks
```

不需要直接改脚本。

复制 `x_bookmarks_sync.env.example` 为 `x_bookmarks_sync.env`，然后设置：

```bash
X_BOOKMARKS_TARGET_DIR="$HOME/你的/Obsidian/目录"
```

## 依赖要求

- macOS
- Google Chrome
- Chrome 144+
- Python 3
- `npm`
- 能运行 shell 命令的 Codex 类环境

如果本机没有安装 `dev-browser`，脚本会自动执行安装。

## 安装方式

把整个目录放到你的 Codex skills 目录，例如：

```text
~/.codex/skills/x-bookmarks-sync
```

如果你要发布到 GitHub，别人可以把这个目录 clone 或复制到他们自己的 skills 目录中。

## 快速开始

1. 把这个目录放到 `~/.codex/skills/x-bookmarks-sync`
2. 如果你想自定义输出路径，先把 `x_bookmarks_sync.env.example` 复制成 `x_bookmarks_sync.env`
3. 在你当前使用的 Chrome 会话里开启 remote debugging
4. 确保你已经在 Chrome 中登录 X
5. 对 Codex 说 `同步 X 书签`

## 在 Codex 里怎么触发

可以直接说：

- `同步 X 书签`
- `把我的 X 书签到 Obsidian`
- `更新一下 X 书签笔记`
- `用 x-bookmarks-sync 刷新书签`

## 工作流程

1. 检查 Chrome 版本是否满足要求
2. 如果没装 `dev-browser`，自动执行 `npm install -g dev-browser`
3. 从本机 Chrome 配置里读取 `DevToolsActivePort`
4. 连接到你当前已经打开的 Chrome 会话
5. 导出 X 书签
6. 重新生成 Obsidian 笔记与索引页

## Chrome 一次性准备

先在 Chrome 中启用当前会话的远程调试：

1. 打开 Chrome
2. 访问：

```text
chrome://inspect#remote-debugging
```

3. 开启 remote debugging

之后这个 skill 才能连接你当前的 Chrome 会话。

## 关于授权弹窗

Chrome 在建立新的远程调试连接时，可能会弹出权限确认框。

所以真实体验通常是：

- 有时可以直接同步，不用点任何东西
- 有时会弹出 `Allow`，需要你手动确认

如果出现弹窗，点一下 `Allow`，然后重新执行同步即可。

## 增量同步逻辑

这个 skill 的“增量”是结果层面的增量，不是纯 API 增量请求。

意思是：

- 已同步过的书签保留原编号
- 新书签从下一个编号继续追加
- 不会因为后续同步而重排旧笔记
- 编号依据是收藏列表顺序，不是发帖时间

同时它还做了“提前停止”优化：

- 会先从 `.x_bookmarks_state.json` 读取已同步书签链接
- 滚动抓取时，如果连续几批内容大部分都已经同步过，就提前停止

这样重复同步时，通常会比每次都完整滚到底更快。

## 命令行手动运行

也可以直接运行：

```bash
~/.codex/skills/x-bookmarks-sync/scripts/sync_x_bookmarks.sh
```

可选本地配置文件：

```text
~/.codex/skills/x-bookmarks-sync/x_bookmarks_sync.env
```

## 目录说明

- `SKILL.md`
  - skill 的触发条件和使用流程
- `scripts/sync_x_bookmarks.sh`
  - 环境检查、Chrome 连接、同步入口
- `scripts/export_x_bookmarks.devbrowser.js`
  - 书签抓取与“遇到旧书签批次提前停止”的逻辑
- `scripts/generate_x_obsidian_notes.py`
  - 笔记生成、编号维护、状态文件维护、索引页生成

## 注意事项

- 这个 skill 不是普通未登录爬虫，而是借用你自己已登录的 Chrome 会话，所以成功率会高很多。
- 但它不是“万能跳过反爬”方案。
- 如果 X 修改页面结构、登录流程、风控策略，这个 skill 可能需要更新。
- 如果 Chrome 版本太低，脚本会直接给出明确提示。
- 如果没开启 remote debugging，脚本也会直接提示。
- 默认输出路径只是通用示例。针对你自己的机器路径，建议放到 `x_bookmarks_sync.env` 里配置，不要直接改源码。

## 发布到 GitHub 时建议补充说明

建议你在仓库主页再明确写一下：

- 这个 skill 面向哪种 Codex / agent 宿主
- 支持的 Chrome 版本范围
- 默认 Obsidian 路径只是示例，还是你的固定约定
- `.x_bookmarks_state.json` 是否应该提交到仓库

## 安全提醒

这个项目会读取你已登录浏览器会话中的内容。请只在你信任的机器、信任的账号环境里使用。
