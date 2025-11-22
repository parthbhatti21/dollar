#!/bin/bash
# Stop Dollar Assistant script

# Find and kill the Dollar Assistant process
if pgrep -f "python.*main.py" > /dev/null; then
    pkill -f "python.*main.py"
    sleep 1
    
    # Verify it's stopped
    if ! pgrep -f "python.*main.py" > /dev/null; then
        osascript -e 'display notification "Dollar Assistant stopped" with title "Dollar Assistant"'
        echo "✅ Dollar Assistant stopped"
    else
        # Force kill if still running
        pkill -9 -f "python.*main.py"
        osascript -e 'display notification "Dollar Assistant force stopped" with title "Dollar Assistant"'
        echo "✅ Dollar Assistant force stopped"
    fi
else
    osascript -e 'display notification "Dollar Assistant is not running" with title "Dollar Assistant"'
    echo "ℹ️  Dollar Assistant is not running"
fi



