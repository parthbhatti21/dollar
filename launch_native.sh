#!/bin/bash
# Wrapper script that forces native arm64 execution
# This script ensures we're running in native mode, not Rosetta

DOLLAR_DIR="/Users/parthbhatti/Codes and backups/dollar"

# Check if we're running in x86_64 mode (Rosetta)
if [ "$(uname -m)" = "x86_64" ]; then
    # Re-execute in native arm64 mode
    exec arch -arm64 "$0" "$@"
fi

# Now we're guaranteed to be in arm64 mode
cd "$DOLLAR_DIR" || exit 1

# Check if already running
if pgrep -f "python.*main.py" > /dev/null; then
    osascript -e 'display notification "Dollar Assistant is already running" with title "Dollar Assistant"'
    exit 0
fi

# Use venv Python
if [ -f ".venv/bin/python3" ]; then
    PYTHON_EXE="$DOLLAR_DIR/.venv/bin/python3"
elif [ -f "venv/bin/python3" ]; then
    PYTHON_EXE="$DOLLAR_DIR/venv/bin/python3"
else
    PYTHON_EXE="python3"
fi

# Show notification
osascript -e 'display notification "Starting Dollar Assistant..." with title "Dollar Assistant"'

# Launch in background
cd agent
nohup "$PYTHON_EXE" main.py > ../dollar.log 2>&1 &
LAUNCH_PID=$!

# Wait a bit longer for it to start
sleep 3

# Check if process is running (check both PID and process name)
if kill -0 $LAUNCH_PID 2>/dev/null || pgrep -f "python.*main.py" > /dev/null || pgrep -f "main.py" > /dev/null; then
    osascript -e 'display notification "Dollar Assistant started successfully" with title "Dollar Assistant"'
    exit 0
fi

# If not running, check for errors in log
ERROR_MSG="Failed to start. Check dollar.log"
if [ -f "../dollar.log" ]; then
    # Check if it actually started (look for "Listening" message)
    if grep -q "Listening for wake word" "../dollar.log" 2>/dev/null; then
        osascript -e 'display notification "Dollar Assistant started successfully" with title "Dollar Assistant"'
        exit 0
    fi
    # Otherwise, get the actual error
    LAST_ERROR=$(tail -5 "../dollar.log" | grep -i "error\|exception\|traceback\|failed" | head -1)
    if [ -n "$LAST_ERROR" ]; then
        ERROR_MSG="Failed: ${LAST_ERROR:0:80}"
    fi
fi
osascript -e "display notification \"$ERROR_MSG\" with title \"Dollar Assistant\""
exit 1

