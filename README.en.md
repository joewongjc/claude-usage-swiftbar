# Claude Usage SwiftBar Plugin

[中文](README.md) | English

A macOS menu bar plugin that displays your Claude Code usage at a glance. Built for [SwiftBar](https://github.com/swiftbar/SwiftBar).

Shows weekly usage, model-specific breakdowns (Sonnet/Opus), 5-hour burst limits, and extra usage credits with color-coded progress bars.

## Features

- **Real-time usage tracking** - Weekly (7-day), per-model (Sonnet/Opus), and 5-hour burst usage
- **Color-coded progress bars** - 5-tier color system (green/blue/yellow/orange/red) so you know at a glance how much quota remains
- **Time progress** - See how much of each usage window has elapsed
- **Extra usage credits** - Track overage spending if enabled
- **Smart caching** - 30-minute cache to avoid API rate limits, with manual refresh option
- **Auto plan detection** - Displays your subscription tier (Pro, Max, Max 5x, Max 20x)

## Requirements

- **macOS** (SwiftBar is macOS-only)
- **Claude Code** with OAuth login (`claude login`)
- **Python 3.9+** (included with macOS)

> **Note:** This plugin reads OAuth credentials from macOS Keychain. It does NOT work with API key authentication (`ANTHROPIC_API_KEY`). You must be logged in via `claude login`.

## Install

### One-liner (with Claude Code)

Give this repo URL to your Claude Code and ask it to install.

### Manual

```bash
git clone https://github.com/joewongjc/claude-usage-swiftbar.git
cd claude-usage-swiftbar
./install.sh
```

The install script will:
1. Install [SwiftBar](https://github.com/swiftbar/SwiftBar) via Homebrew (if needed)
2. Verify your Claude Code OAuth credentials
3. Copy the plugin to `~/Library/SwiftBar/`
4. Start SwiftBar if not running

## What it looks like

Menu bar shows: `◆ 55%` (your weekly usage percentage, color changes with usage level)

Clicking reveals a dropdown with detailed breakdowns:

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

### Color Scale

| Usage | Color | Meaning |
|-------|-------|---------|
| 0-19% | 🟢 Green | Plenty of quota |
| 20-39% | 🔵 Blue | Normal usage |
| 40-59% | 🟡 Yellow | Over halfway |
| 60-79% | 🟠 Orange | Getting tight |
| 80-100% | 🔴 Red | Running low |

## Configuration

The plugin refreshes every 5 minutes (configured via the filename `claude-usage.5m.py`). To change the refresh interval, rename the file:

- `claude-usage.1m.py` - Every minute
- `claude-usage.10m.py` - Every 10 minutes
- `claude-usage.30m.py` - Every 30 minutes

API calls are cached for 30 minutes regardless of refresh interval to avoid rate limiting. You can click "立即刷新" to force a fresh API call when the cache expires.

## Uninstall

```bash
rm ~/Library/SwiftBar/claude-usage.5m.py
rm -f ~/.local/state/claude-usage-cache.json
```

## License

MIT
