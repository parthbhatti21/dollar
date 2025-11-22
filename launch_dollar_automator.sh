#!/bin/bash
# Optimized launch script for Automator/Keyboard Shortcuts
# This version runs in the background and shows a notification

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check if already running
if pgrep -f "python.*main.py" > /dev/null; then
    osascript -e 'display notification "Dollar Assistant is already running" with title "Dollar Assistant"'
    exit 0
fi

# Show notification that we're starting
osascript -e 'display notification "Starting Dollar Assistant..." with title "Dollar Assistant"'

# Change to agent directory and run in background
cd agent
nohup python3 main.py > ../dollar.log 2>&1 &

# Give it a moment to start
sleep 1

# Check if it started successfully
if pgrep -f "python.*main.py" > /dev/null; then
    osascript -e 'display notification "Dollar Assistant started successfully" with title "Dollar Assistant"'
else
    osascript -e 'display notification "Failed to start Dollar Assistant. Check dollar.log for errors." with title "Dollar Assistant"'
fi



