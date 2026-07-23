#!/bin/bash
# install.sh — installs the Apple Mail AI Reply plugin.
#
# What this does:
#   1. Copies the Python backend + config into a stable location
#      (~/Library/Application Support/AppleMailAI/) so it keeps working even
#      if this repo checkout is later moved or deleted.
#   2. Compiles the shared AppleScript library (AIMailCore.applescript) into
#      ~/Library/Script Libraries/, which the two entry-point scripts depend on.
#   3. Compiles "Suggest Replies" and "Quick Reply" into
#      ~/Library/Scripts/Applications/Mail/, so they show up in Mail's Script
#      menu once it's enabled.
#
# Safe to re-run: it won't overwrite an existing config.json.
#
# macOS only. Requires Xcode Command Line Tools (for `osacompile`) — normally
# already present; if not, run `xcode-select --install`.

set -euo pipefail

if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "This installer only works on macOS (Apple Mail + AppleScript)." >&2
    exit 1
fi

if ! command -v osacompile >/dev/null 2>&1; then
    echo "osacompile not found. Install the Xcode Command Line Tools with:" >&2
    echo "    xcode-select --install" >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

APP_SUPPORT_DIR="$HOME/Library/Application Support/AppleMailAI"
SCRIPT_LIB_DIR="$HOME/Library/Script Libraries"
MAIL_SCRIPTS_DIR="$HOME/Library/Scripts/Applications/Mail"

echo "==> Installing Python backend + config to: $APP_SUPPORT_DIR"
mkdir -p "$APP_SUPPORT_DIR"
cp "$SCRIPT_DIR/suggest_replies.py" "$APP_SUPPORT_DIR/suggest_replies.py"
cp "$SCRIPT_DIR/config.example.json" "$APP_SUPPORT_DIR/config.example.json"

if [[ -f "$APP_SUPPORT_DIR/config.json" ]]; then
    echo "    config.json already exists — leaving your settings untouched."
else
    cp "$SCRIPT_DIR/config.example.json" "$APP_SUPPORT_DIR/config.json"
    echo "    Created config.json from the example. Edit it before first use:"
    echo "        open \"$APP_SUPPORT_DIR/config.json\""
fi

echo "==> Compiling shared AppleScript library"
mkdir -p "$SCRIPT_LIB_DIR"
osacompile -o "$SCRIPT_LIB_DIR/AIMailCore.scpt" "$SCRIPT_DIR/scripts/AIMailCore.applescript"

echo "==> Compiling Mail scripts (Script menu items)"
mkdir -p "$MAIL_SCRIPTS_DIR"
osacompile -o "$MAIL_SCRIPTS_DIR/Suggest Replies.scpt" "$SCRIPT_DIR/scripts/SuggestReplies.applescript"
osacompile -o "$MAIL_SCRIPTS_DIR/Quick Reply.scpt" "$SCRIPT_DIR/scripts/QuickReply.applescript"

echo ""
echo "Install complete. Remaining manual steps (one-time):"
echo ""
echo "  1. Edit your config (name / signature / tone):"
echo "         open \"$APP_SUPPORT_DIR/config.json\""
echo ""
echo "  2. Make sure the Claude Code CLI is installed and logged in:"
echo "         claude -p \"say hi in 3 words\""
echo "     (If 'claude' isn't on your PATH, set \"claude_path\" in config.json"
echo "      to its full path — find it with: which claude)"
echo ""
echo "  3. Show Mail's Script menu: open Script Editor > Settings >"
echo "     General > check 'Show Script menu in menu bar'."
echo "     'Suggest Replies' and 'Quick Reply' will now appear under the"
echo "     scroll-icon menu in the menu bar while Mail is frontmost."
echo ""
echo "  4. (Optional) Assign keyboard shortcuts via Automator Quick Actions —"
echo "     see README.md for step-by-step instructions."
echo ""
echo "  5. The first time you run either script, macOS will ask permission"
echo "     for it to control Mail — click OK."
echo ""
echo "Nothing this plugin does will ever send an email automatically — it"
echo "only opens a draft for you to review and send yourself."
