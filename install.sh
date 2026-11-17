#!/usr/bin/env bash
# auto-mouse-mover installer for macOS
#
# Usage (paste into Terminal):
#   curl -fsSL https://raw.githubusercontent.com/Diana-Lee0912/auto-mouse-mover/main/install.sh | bash
#
# What it does:
#   1. Downloads auto_mouse_mover.py into ~/auto-mouse-mover
#   2. Adds two files there that you can double-click:
#        "Start auto-mouse-mover.command"  starts the program
#        "Change settings.command"         asks for your work hours again
#   3. Asks for your work hours, then starts the program
#
# Running it again updates the program and keeps your saved settings.

set -euo pipefail

RAW_URL="https://raw.githubusercontent.com/Diana-Lee0912/auto-mouse-mover/main"
INSTALL_DIR="$HOME/auto-mouse-mover"

echo "=== auto-mouse-mover installer ==="
echo

if [ "$(uname -s)" != "Darwin" ]; then
  echo "This installer is for macOS."
  echo "On Windows, see the README for the PowerShell command."
  exit 1
fi

# On a fresh Mac, python3 is a placeholder that offers to install the
# Command Line Developer Tools (which include Python).
if ! python3 --version >/dev/null 2>&1; then
  echo "Python 3 isn't ready yet."
  echo "If a window asked to install the Command Line Developer Tools, click Install,"
  echo "wait for it to finish, then paste the install command again."
  exit 1
fi

mkdir -p "$INSTALL_DIR"
echo "Downloading to $INSTALL_DIR ..."
curl -fsSL "$RAW_URL/auto_mouse_mover.py" -o "$INSTALL_DIR/auto_mouse_mover.py"

cat > "$INSTALL_DIR/Start auto-mouse-mover.command" <<'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 auto_mouse_mover.py
EOF

cat > "$INSTALL_DIR/Change settings.command" <<'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 auto_mouse_mover.py --setup
EOF

chmod +x "$INSTALL_DIR"/*.command

echo
echo "Installed!"
echo "  Next time, open the \"auto-mouse-mover\" folder in your home folder and"
echo "  double-click \"Start auto-mouse-mover\"."
echo
echo "IMPORTANT, first time only: let Terminal control the mouse."
echo "  System Settings -> Privacy & Security -> Accessibility -> turn on Terminal."
echo "  Without this, the program runs but the mouse never moves."
echo "  After turning it on, quit Terminal (Command + Q) and double-click"
echo "  \"Start auto-mouse-mover\"."

# Show the folder in Finder so the double-click files are easy to find
open "$INSTALL_DIR" >/dev/null 2>&1 || true

# This script itself arrives through a pipe, so read the answers from the keyboard
python3 "$INSTALL_DIR/auto_mouse_mover.py" --setup < /dev/tty
