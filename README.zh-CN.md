# X 书签同步

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
![Platform: macOS](https://img.shields.io/badge/platform-macOS-black)
![Chrome: 144+](https://img.shields.io/badge/Chrome-144%2B-blue)
![Agent Friendly](https://img.shields.io/badge/agent-friendly-orange)

[English README](./README.md)

通过复用你已经登录的 Chrome 会话，把 `X.com` 书签同步成 Obsidian 笔记。
它既可以当作独立脚本使用，也可以接到支持自定义技能/命令的代理工具里。

## 一眼看懂

- 借用你当前已经登录的 Chrome 会话，而不是单独处理登录
- 从 `https://x.com/i/bookmarks` 导出书签
- 为每条书签生成一篇 Obsidian Markdown 笔记
- 多次同步时保持稳定递增编号
- 编号按收藏列表顺序分配，从列表底部最老的书签开始

这个项目适合下面这种场景：

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
- 任意能运行 shell 命令的环境

如果本机没有安装 `dev-browser`，脚本会自动执行安装。

## 安装 / 集成方式

你可以按 4 种方式使用这个项目。

### 方式 1：直接当独立脚本运行

把仓库 clone 到任意目录：

```bash
git clone https://github.com/noroot777/x-bookmarks-sync.git
cd x-bookmarks-sync
```

然后直接运行：

```bash
./scripts/sync_x_bookmarks.sh
```

这是最通用的方式，不依赖任何 skill 系统。

### 方式 2：作为 Codex skill 安装

把整个目录放到你的 Codex skills 目录，例如：

```text
~/.codex/skills/x-bookmarks-sync
```

然后你可以直接对 Codex 说：

- `同步 X 书签`
- `把我的 X 书签到 Obsidian`

### 方式 3：接到其他代理工具

如果你的工具支持自定义 skills、slash commands、prompt snippets 或 shell tasks，就把它指向：

```text
scripts/sync_x_bookmarks.sh
```

常见接法：

- 注册一个自定义命令，执行 `./scripts/sync_x_bookmarks.sh`
- 建一个可复用 prompt，提示代理去运行这个脚本
- 在任务系统或自动化系统里，把这个脚本作为一个固定任务入口

如果工具本身没有正式的 skill 格式，通常直接调用脚本是最稳的。

### 方式 4：直接让大模型帮你安装

如果你的助手能访问本地文件系统并运行 shell 命令，也可以直接让它帮你装。

可以直接复制这类提示词：

- `帮我安装 x-bookmarks-sync：https://github.com/noroot777/x-bookmarks-sync`
- `把这个仓库 clone 下来，复制 x_bookmarks_sync.env.example 为 x_bookmarks_sync.env，并帮我改成我的 Obsidian 路径`
- `把这个项目安装成我本地代理工具里的一个 skill，并让它运行 scripts/sync_x_bookmarks.sh`
- `在这台机器上配置好 x-bookmarks-sync，然后告诉我怎么用`

一个能执行命令的大模型，通常应该帮你做这些事：

- clone 这个仓库
- 如果你的宿主有 skills/tools 目录，就放到对应目录
- 把 `x_bookmarks_sync.env.example` 复制成 `x_bookmarks_sync.env`
- 把 `X_BOOKMARKS_TARGET_DIR` 改成你真实的 Obsidian 路径
- 检查 Chrome remote debugging 是否已开启
- 运行 `./scripts/sync_x_bookmarks.sh`

## 快速开始

1. 把仓库 clone 或复制到你的机器上
2. 如果你想自定义输出路径，先把 `x_bookmarks_sync.env.example` 复制成 `x_bookmarks_sync.env`
3. 在你当前使用的 Chrome 会话里开启 remote debugging
4. 确保你已经在 Chrome 中登录 X
5. 运行 `./scripts/sync_x_bookmarks.sh`，或者让你的代理工具调用它

## 代理工具里的示例提示词

如果你的代理工具能运行 shell 命令，通常可以直接说：

- `同步 X 书签`
- `把我的 X 书签到 Obsidian`
- `刷新我的 X 书签笔记`
- `运行 x-bookmarks-sync 脚本`

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

之后这个脚本才能连接你当前的 Chrome 会话。

## 关于授权弹窗

Chrome 在建立新的远程调试连接时，可能会弹出权限确认框。

所以真实体验通常是：

- 有时可以直接同步，不用点任何东西
- 有时会弹出 `Allow`，需要你手动确认

如果出现弹窗，点一下 `Allow`，然后重新执行同步即可。

## 增量同步逻辑

这个流程的“增量”是结果层面的增量，不是纯 API 增量请求。

意思是：

- 已同步过的书签保留原编号
- 新书签从下一个编号继续追加
- 不会因为后续同步而重排旧笔记
- 编号依据是收藏列表顺序，不是发帖时间

同时它还做了“提前停止”优化：

- 会先从 `.x_bookmarks_state.json` 读取已同步书签链接
- 滚动抓取时，如果连续几批内容大部分都已经同步过，就提前停止

这样重复同步时，通常会比每次都完整滚到底更快。

## 独立脚本运行

不依赖任何 skill 系统，直接运行：

```bash
./scripts/sync_x_bookmarks.sh
```

可选本地配置文件：

```text
./x_bookmarks_sync.env
```

如果你是在别的目录调用，也可以这样运行：

```bash
bash /path/to/x-bookmarks-sync/scripts/sync_x_bookmarks.sh
```

## 目录说明

- `SKILL.md`
  - 供支持 skill 元数据的工具使用的示例定义
- `scripts/sync_x_bookmarks.sh`
  - 环境检查、Chrome 连接、同步入口
- `scripts/export_x_bookmarks.devbrowser.js`
  - 书签抓取与“遇到旧书签批次提前停止”的逻辑
- `scripts/generate_x_obsidian_notes.py`
  - 笔记生成、编号维护、状态文件维护、索引页生成

## 注意事项

- 这个项目不是普通未登录爬虫，而是借用你自己已登录的 Chrome 会话，所以成功率会高很多。
- 但它不是“万能跳过反爬”方案。
- 如果 X 修改页面结构、登录流程、风控策略，这个项目可能需要更新。
- 如果 Chrome 版本太低，脚本会直接给出明确提示。
- 如果没开启 remote debugging，脚本也会直接提示。
- 默认输出路径只是通用示例。针对你自己的机器路径，建议放到 `x_bookmarks_sync.env` 里配置，不要直接改源码。

## 安全提醒

这个项目会读取你已登录浏览器会话中的内容。请只在你信任的机器、信任的账号环境里使用。
