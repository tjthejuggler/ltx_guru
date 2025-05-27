#!/bin/bash

# --- Configuration ---
MP3_FILE="/home/twain/Projects/ltx_guru/lubalin_you_know_me.mp3"
WINDOW_NAME="MainWindow" # Still useful for focusing, if xdotool can
MP3_PID="" # Initialize MP3_PID

# --- Path to ydotool and ydotoold ---
YDOTOOL_CLIENT_CMD="/usr/local/bin/ydotool"
YDOTOOLD_DAEMON_PATH="/usr/local/bin/ydotoold"
YDOTOOLD_DAEMON_BASENAME="$(basename "$YDOTOOLD_DAEMON_PATH")"
YDOTOOLD_PID_TO_KILL="" # PID of ydotoold if started by this script

# --- Cleanup function ---
cleanup() {
    echo "Executing cleanup..."
    if [ -n "$YDOTOOLD_PID_TO_KILL" ]; then
        echo "Attempting to stop $YDOTOOLD_DAEMON_BASENAME (PID: $YDOTOOLD_PID_TO_KILL) which was started by this script..."
        if kill "$YDOTOOLD_PID_TO_KILL" > /dev/null 2>&1; then
            echo "SIGTERM sent to $YDOTOOLD_DAEMON_BASENAME (PID: $YDOTOOLD_PID_TO_KILL)."
            # Wait for the process to terminate.
            if wait "$YDOTOOLD_PID_TO_KILL" 2>/dev/null; then
                echo "$YDOTOOLD_DAEMON_BASENAME (PID: $YDOTOOLD_PID_TO_KILL) stopped successfully."
            else
                sleep 0.2 # Brief pause if wait failed (e.g. already exited)
                if ! ps -p "$YDOTOOLD_PID_TO_KILL" > /dev/null 2>&1; then
                    echo "$YDOTOOLD_DAEMON_BASENAME (PID: $YDOTOOLD_PID_TO_KILL) confirmed stopped."
                else
                    echo "Warning: $YDOTOOLD_DAEMON_BASENAME (PID: $YDOTOOLD_PID_TO_KILL) may still be running. 'wait' failed or it's taking time to stop."
                fi
            fi
        else
            if ! ps -p "$YDOTOOLD_PID_TO_KILL" > /dev/null 2>&1; then # Check if already gone
                echo "$YDOTOOLD_DAEMON_BASENAME (PID: $YDOTOOLD_PID_TO_KILL) was already stopped or did not exist when cleanup ran."
            else
                echo "Warning: Failed to send SIGTERM to $YDOTOOLD_DAEMON_BASENAME (PID: $YDOTOOLD_PID_TO_KILL), but it appears to be running."
            fi
        fi
    else
        echo "$YDOTOOLD_DAEMON_BASENAME was not started by this script, or its PID was not tracked for cleanup."
    fi

}
trap cleanup EXIT # Register cleanup function

# --- Sanity Checks ---
if [ ! -f "$MP3_FILE" ]; then echo "Error: MP3 Missing"; exit 1; fi
if ! command -v xdotool &> /dev/null; then echo "Error: xdotool Missing"; exit 1; fi
if ! command -v mpg123 &> /dev/null; then echo "Error: mpg123 Missing"; exit 1; fi
if ! command -v "$YDOTOOL_CLIENT_CMD" &> /dev/null; then echo "Error: $YDOTOOL_CLIENT_CMD (client) Missing"; exit 1; fi

# Check for ydotoold daemon executable
if [ ! -x "$YDOTOOLD_DAEMON_PATH" ]; then
    echo "Error: $YDOTOOLD_DAEMON_BASENAME daemon executable not found or not executable at $YDOTOOLD_DAEMON_PATH"
    exit 1
fi

# Check if ydotoold is running, start if not
echo "Checking for $YDOTOOLD_DAEMON_BASENAME daemon..."
if ! pgrep -u "$(whoami)" -x "$YDOTOOLD_DAEMON_BASENAME" > /dev/null; then
    echo "$YDOTOOLD_DAEMON_BASENAME not running for user '$(whoami)'."
    echo "Attempting to start $YDOTOOLD_DAEMON_PATH in the background..."
    "$YDOTOOLD_DAEMON_PATH" >/dev/null 2>&1 &
    YDOTOOLD_PID_TO_KILL=$!
    
    sleep 1.5 # Give it a moment to initialize

    if ! pgrep -u "$(whoami)" -x "$YDOTOOLD_DAEMON_BASENAME" > /dev/null; then
        echo "Error: Failed to start $YDOTOOLD_DAEMON_BASENAME."
        echo "Attempted to start it (intended PID: $YDOTOOLD_PID_TO_KILL), but no $YDOTOOLD_DAEMON_BASENAME process found for user '$(whoami)'."
        echo "Please check system logs or try starting it manually: $YDOTOOLD_DAEMON_PATH"
        YDOTOOLD_PID_TO_KILL="" 
        exit 1
    else
        if ps -p "$YDOTOOLD_PID_TO_KILL" > /dev/null; then
            echo "$YDOTOOLD_DAEMON_BASENAME (PID: $YDOTOOLD_PID_TO_KILL) started successfully by the script."
        else
            echo "$YDOTOOLD_DAEMON_BASENAME started, but the initial PID $YDOTOOLD_PID_TO_KILL is no longer running (it might have forked or exited quickly)."
            echo "An instance of $YDOTOOLD_DAEMON_BASENAME is running for user '$(whoami)'. Proceeding."
            echo "This script will not attempt to kill it on exit, as the original PID is not active."
            YDOTOOLD_PID_TO_KILL="" 
        fi
    fi
else
    echo "$YDOTOOLD_DAEMON_BASENAME is already running for user '$(whoami)'. This script will not start or stop it."
    YDOTOOLD_PID_TO_KILL=""
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
"$YDOTOOL_CLIENT_CMD" click 0xC0 # 0xC0 for left click

echo ""
echo "Interaction attempt complete."
echo "MP3 should be playing (PID: $MP3_PID). You can stop it with: kill $MP3_PID"
echo "Did the button in '$WINDOW_NAME' get clicked (where your mouse was pointing)?"

exit 0