# Claude 用量监控 SwiftBar 插件

[English](README.md) | 中文

macOS 菜单栏插件，一眼掌握 Claude Code 用量。基于 [SwiftBar](https://github.com/swiftbar/SwiftBar)。

官方自带的 Usage 只告诉你用了多少百分比，但不告诉你离下次重置还剩多久。80% 的用量剩 5 天和剩 2 小时，完全是两回事。这个插件把**用量进度**和**时间进度**放在一起对比，让你一目了然。

## 功能

- **实时用量监控** - Weekly (7 天)、Sonnet/Opus 分模型、5 小时 Burst 窗口
- **五档颜色进度条** - 绿/蓝/黄/橙/红，抬头瞄一眼就知道配额够不够
- **时间进度对比** - 用量 55% 但时间已过 90%？放心用，富余得很
- **超额用量追踪** - 开启了 Extra Usage 的话，显示消费金额和额度
- **智能缓存** - 30 分钟缓存避免 API 限流，支持手动刷新
- **自动识别套餐** - 自动显示 Pro / Max / Max 5x / Max 20x

## 前置条件

- **macOS**（SwiftBar 仅支持 macOS）
- **Claude Code**，且已通过 `claude login` 登录（OAuth 认证）
- **Python 3.9+**（macOS 自带）

> **注意:** 插件通过 macOS Keychain 读取 OAuth 凭证，不支持 API Key 方式（`ANTHROPIC_API_KEY`）。必须先用 `claude login` 登录。

## 安装

### 用 Claude Code 安装（推荐）

把这个 repo 链接丢给你的 Claude Code，让它帮你装就行。

### 手动安装

```bash
git clone https://github.com/joewongjc/claude-usage-swiftbar.git
cd claude-usage-swiftbar
./install.sh
```

安装脚本会自动:
1. 通过 Homebrew 安装 [SwiftBar](https://github.com/swiftbar/SwiftBar)（如果没装）
2. 检查 Claude Code OAuth 凭证是否存在
3. 复制插件到 `~/Library/SwiftBar/`
4. 启动 SwiftBar（如果没运行）

## 效果展示

菜单栏显示: `◆ 55%`（周用量百分比，颜色随用量变化）

点击展开详情:

```
Claude Max 5x
─────────────────────────────
📅 Weekly (7d)  剩余 4d 2h
  用量  ███████████           55%
  时间  ██████████████████    90%
─────────────────────────────
📅 Sonnet (7d)
  用量                         2%
  时间  ██████████████████    89%
─────────────────────────────
⏱ 5-Hour Burst  剩余 1h 11m
  用量  ████████              39%
  时间  ███████████████       76%
─────────────────────────────
已更新 18:48
立即刷新
```

### 颜色含义

| 用量 | 颜色 | 含义 |
|------|------|------|
| 0-19% | 🟢 绿色 | 配额充裕 |
| 20-39% | 🔵 蓝色 | 正常使用 |
| 40-59% | 🟡 黄色 | 已过半 |
| 60-79% | 🟠 橙色 | 有点吃紧 |
| 80-100% | 🔴 红色 | 快用完了 |

## 配置

插件每 5 分钟刷新一次（由文件名 `claude-usage.5m.py` 中的 `5m` 决定）。改文件名即可调整刷新频率:

- `claude-usage.1m.py` - 每分钟
- `claude-usage.10m.py` - 每 10 分钟
- `claude-usage.30m.py` - 每 30 分钟

无论刷新频率如何，API 调用都有 30 分钟缓存以避免限流。缓存过期后点"立即刷新"可强制拉取最新数据。

## 卸载

```bash
rm ~/Library/SwiftBar/claude-usage.5m.py
rm -f ~/.local/state/claude-usage-cache.json
```

## 开源协议

MIT
