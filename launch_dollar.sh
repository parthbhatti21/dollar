#!/bin/bash
# Launch script for Dollar Assistant
# This script can be used with keyboard shortcuts or Automator

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check if we're already running
if pgrep -f "python.*main.py" > /dev/null; then
    osascript -e 'display notification "Dollar Assistant is already running" with title "Dollar Assistant"'
    exit 0
fi

# Change to agent directory and run
cd agent
python3 main.py



