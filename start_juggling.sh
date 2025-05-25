#!/bin/bash

# --- Configuration ---
MP3_FILE="/home/twain/Projects/ltx_guru/lubalin_you_know_me.mp3"
WINDOW_NAME="MainWindow" # Still useful for focusing, if xdotool can

# --- Path to ydotool ---
YDOTOOL_CMD="/usr/local/bin/ydotool"

# --- Sanity Checks ---
if [ ! -f "$MP3_FILE" ]; then echo "Error: MP3 Missing"; exit 1; fi
if ! command -v xdotool &> /dev/null; then echo "Error: xdotool Missing"; exit 1; fi
if ! command -v mpg123 &> /dev/null; then echo "Error: mpg123 Missing"; exit 1; fi
if ! command -v "$YDOTOOL_CMD" &> /dev/null; then echo "Error: $YDOTOOL_CMD Missing"; exit 1; fi
if ! pgrep -u "$(whoami)" -x "$(basename /usr/local/bin/ydotoold)" > /dev/null; then
    echo "Error: ydotoold (ydotool daemon) not running for user '$(whoami)'."
    echo "Please start it in another terminal with: /usr/local/bin/ydotoold"
    exit 1
fi

# --- User Action Required ---
echo ""
echo "--------------------------------------------------------------------"
echo "MANUAL MOUSE POSITIONING REQUIRED:"
echo "1. Make sure your '$WINDOW_NAME' application is open and visible."
echo "2. MANUALLY move your mouse cursor PRECISELY over the 'Play' button."
echo "3. LEAVE the mouse cursor there."
echo "4. Come back to THIS terminal window (without moving the mouse off the button if possible, or quickly move it back)."
read -p "   Press ENTER when your mouse is positioned over the 'Play' button and you are ready..."
echo "--------------------------------------------------------------------"
echo ""

# --- Start MP3 ---
echo "Starting MP3 player..."
mpg123 -q "$MP3_FILE" > /dev/null 2>&1 &
MP3_PID=$!

# --- Interact with Window ---
# Attempt to focus the window. This is good practice so the click definitely goes to it.
# If MainWindow is already focused, this might not be strictly necessary.
TARGET_WINDOW_DECIMAL_ID=$(xdotool search --onlyvisible --name "$WINDOW_NAME" | head -1)

if [ -z "$TARGET_WINDOW_DECIMAL_ID" ]; then
    echo "Warning: Window '$WINDOW_NAME' not found by xdotool. Click will happen at current mouse position on WHATEVER is active."
else
    echo "Attempting to activate/focus '$WINDOW_NAME' (ID: $TARGET_WINDOW_DECIMAL_ID) using xdotool..."
    xdotool windowactivate "$TARGET_WINDOW_DECIMAL_ID"
    # A brief sleep is important for focus to take effect BEFORE the click
    sleep 0.3 # Adjust if click seems to go to the wrong window (e.g., the terminal)
fi

# ydotool click clicks at the CURRENT mouse cursor position.
echo "Attempting left click at current mouse position using ydotool..."
"$YDOTOOL_CMD" click 0xC0 # 0xC0 for left click

echo ""
echo "Interaction attempt complete."
echo "MP3 should be playing (PID: $MP3_PID). You can stop it with: kill $MP3_PID"
echo "Did the button in '$WINDOW_NAME' get clicked (where your mouse was pointing)?"

exit 0