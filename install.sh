#!/bin/bash
set -euo pipefail

PLUGIN_NAME="claude-usage.5m.py"
CODEX_MODULE="codex_usage.py"
CODEX_OLD_PLUGIN="codex-usage.5m.py"
SWIFTBAR_DIR="$HOME/Library/SwiftBar"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
KEYCHAIN_SERVICE="Claude Code-credentials"

info()  { printf '\033[1;34m==>\033[0m %s\n' "$1"; }
ok()    { printf '\033[1;32m==>\033[0m %s\n' "$1"; }
error() { printf '\033[1;31m==>\033[0m %s\n' "$1" >&2; }

# 1. macOS check
if [[ "$(uname)" != "Darwin" ]]; then
    error "This plugin only works on macOS (SwiftBar is macOS-only)."
    exit 1
fi

# 2. Homebrew
if ! command -v brew &>/dev/null; then
    info "Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# 3. SwiftBar
if ! brew list --cask swiftbar &>/dev/null; then
    info "Installing SwiftBar..."
    brew install --cask swiftbar
fi

# 4. Claude Code credentials
if ! security find-generic-password -s "$KEYCHAIN_SERVICE" &>/dev/null 2>&1; then
    error "Claude Code OAuth credentials not found in Keychain."
    error "Please run 'claude login' first, then re-run this script."
    exit 1
fi
ok "Claude Code credentials found."

# 5. Plugin directory
if [[ ! -d "$SWIFTBAR_DIR" ]]; then
    info "Creating SwiftBar plugin directory: $SWIFTBAR_DIR"
    mkdir -p "$SWIFTBAR_DIR"
fi

# 6. Copy Claude plugin
info "Installing Claude plugin..."
cp "$SCRIPT_DIR/$PLUGIN_NAME" "$SWIFTBAR_DIR/$PLUGIN_NAME"
chmod +x "$SWIFTBAR_DIR/$PLUGIN_NAME"
ok "Plugin installed to $SWIFTBAR_DIR/$PLUGIN_NAME"

# 7. Copy Codex module (only if Codex is installed; no SwiftBar interval = not a plugin)
if command -v codex &>/dev/null || [[ -d "$HOME/.codex/sessions" ]]; then
    info "Codex detected — installing Codex module..."
    cp "$SCRIPT_DIR/$CODEX_MODULE" "$SWIFTBAR_DIR/$CODEX_MODULE"
    ok "Codex module installed to $SWIFTBAR_DIR/$CODEX_MODULE"
else
    info "Codex not found — skipping Codex module (usage will be Claude-only)."
fi

# Remove old standalone Codex plugin if present
if [[ -f "$SWIFTBAR_DIR/$CODEX_OLD_PLUGIN" ]]; then
    rm "$SWIFTBAR_DIR/$CODEX_OLD_PLUGIN"
    info "Removed old standalone Codex plugin."
fi

# 8. Launch SwiftBar if not running
if ! pgrep -q SwiftBar; then
    info "Starting SwiftBar..."
    open -a SwiftBar

    # First launch: SwiftBar needs a plugin directory configured
    # Give it a moment to start, then check
    sleep 2
    if ! defaults read com.ameba.SwiftBar PluginDirectory &>/dev/null 2>&1; then
        info "Setting SwiftBar plugin directory to $SWIFTBAR_DIR"
        defaults write com.ameba.SwiftBar PluginDirectory -string "$SWIFTBAR_DIR"
    fi
fi

echo ""
ok "Done! Look for the ◆ icon in your menu bar (shows ◆ N%  ⬡ N% if Codex is active)."
ok "The plugin refreshes every 5 minutes. Click it to see usage details."
