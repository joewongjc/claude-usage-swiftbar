# Claude Usage SwiftBar Plugin

## Deployment

Run `./install.sh` to install. The script will:
1. Check that this is macOS
2. Install SwiftBar via Homebrew if not present
3. Verify Claude Code OAuth credentials exist in Keychain
4. Copy the plugin to `~/Library/SwiftBar/`
5. Set executable permissions

## Prerequisites

- macOS
- Claude Code, logged in via `claude login` (OAuth authentication)
- Homebrew (will be used to install SwiftBar if needed)

## Project Structure

- `claude-usage.5m.py` - The SwiftBar plugin script (refreshes every 5 minutes)
- `install.sh` - Automated installer
- `README.md` - User-facing documentation
