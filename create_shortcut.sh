#!/bin/bash
# Script to create a keyboard shortcut for Dollar Assistant
# This creates an AppleScript application that can be assigned a shortcut

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_NAME="Launch Dollar Assistant"

# Try /Applications first (system-wide), fallback to ~/Applications
if [ -w "/Applications" ]; then
    APP_PATH="/Applications/$APP_NAME.app"
else
    APP_PATH="$HOME/Applications/$APP_NAME.app"
    mkdir -p "$HOME/Applications"
fi

echo "Creating keyboard shortcut application..."
echo "App will be created at: $APP_PATH"

# Remove old version if exists
if [ -d "$APP_PATH" ]; then
    echo "Removing old version..."
    rm -rf "$APP_PATH"
fi

# Create the app bundle structure
mkdir -p "$APP_PATH/Contents/MacOS"
mkdir -p "$APP_PATH/Contents/Resources"

# Create the executable script - use the wrapper script
cat > "$APP_PATH/Contents/MacOS/$APP_NAME" << 'SCRIPTEOF'
#!/bin/bash
# Use the native launch wrapper
exec "/Users/parthbhatti/Codes and backups/dollar/launch_native.sh"
SCRIPTEOF

# Check if already running
if pgrep -f "python.*main.py" > /dev/null; then
    osascript -e 'display notification "Dollar Assistant is already running" with title "Dollar Assistant"'
    exit 0
fi

# Change to dollar directory
cd "$DOLLAR_DIR" || {
    osascript -e 'display notification "Error: Could not find Dollar Assistant directory" with title "Dollar Assistant"'
    exit 1
}

# Determine Python executable (prefer venv Python, but check architecture compatibility)
if [ -d ".venv" ] && [ -f ".venv/bin/python3" ]; then
    PYTHON_EXE="$DOLLAR_DIR/.venv/bin/python3"
    echo "Using .venv Python: $PYTHON_EXE"
elif [ -d "venv" ] && [ -f "venv/bin/python3" ]; then
    PYTHON_EXE="$DOLLAR_DIR/venv/bin/python3"
    echo "Using venv Python: $PYTHON_EXE"
else
    PYTHON_EXE="python3"
    echo "Using system Python: $PYTHON_EXE"
fi

# Verify Python works and can import numpy (architecture check)
if ! "$PYTHON_EXE" --version > /dev/null 2>&1; then
    osascript -e 'display notification "Error: Python not found or not working" with title "Dollar Assistant"'
    exit 1
fi

# Test if numpy can be imported (architecture compatibility check)
if ! "$PYTHON_EXE" -c "import numpy" > /dev/null 2>&1; then
    osascript -e 'display notification "Error: Virtual environment has architecture mismatch. Please recreate venv." with title "Dollar Assistant"'
    exit 1
fi

# Show notification
osascript -e 'display notification "Starting Dollar Assistant..." with title "Dollar Assistant"'

# Run in background
cd agent || {
    osascript -e 'display notification "Error: Could not find agent directory" with title "Dollar Assistant"'
    exit 1
}

# Launch in background using the correct Python
# Force native arm64 execution (not Rosetta)
cd "$DOLLAR_DIR/agent"
if [ "$(uname -m)" = "arm64" ]; then
    # Force native arm64 execution
    arch -arm64 "$PYTHON_EXE" main.py > "$DOLLAR_DIR/dollar.log" 2>&1 &
else
    "$PYTHON_EXE" main.py > "$DOLLAR_DIR/dollar.log" 2>&1 &
fi

# Give it a moment to start
sleep 2

# Check if it started successfully
sleep 2
if pgrep -f "python.*main.py" > /dev/null; then
    osascript -e 'display notification "Dollar Assistant started successfully" with title "Dollar Assistant"'
else
    # Get last few lines of error log
    ERROR_MSG="Failed to start. Check dollar.log"
    if [ -f "../dollar.log" ]; then
        LAST_ERROR=$(tail -3 "../dollar.log" | grep -i "error\|exception\|traceback" | head -1)
        if [ -n "$LAST_ERROR" ]; then
            ERROR_MSG="Failed: ${LAST_ERROR:0:100}"
        fi
    fi
    osascript -e "display notification \"$ERROR_MSG\" with title \"Dollar Assistant\""
    # Also open log file location in Finder
    open -R "../dollar.log" 2>/dev/null || true
fi
SCRIPTEOF

chmod +x "$APP_PATH/Contents/MacOS/$APP_NAME"

# Create Info.plist
cat > "$APP_PATH/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>$APP_NAME</string>
    <key>CFBundleIdentifier</key>
    <string>com.dollar.assistant.launcher</string>
    <key>CFBundleName</key>
    <string>$APP_NAME</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSUIElement</key>
    <true/>
    <key>LSArchitecturePriority</key>
    <array>
        <string>arm64</string>
    </array>
    <key>LSMinimumSystemVersion</key>
    <string>11.0</string>
</dict>
</plist>
EOF

# Create a proper app icon (optional, but helps with Spotlight)
# For now, we'll just ensure the app is properly indexed

echo "✅ Application created at: $APP_PATH"
echo ""
echo "🔍 Indexing application for Spotlight (this may take a moment)..."
# Force Spotlight to reindex the app
mdimport "$APP_PATH" 2>/dev/null || touch "$APP_PATH"

echo ""
echo "📋 Next steps:"
echo ""
echo "Option 1: Use Spotlight"
echo "  1. Press ⌘Space to open Spotlight"
echo "  2. Type: Launch Dollar Assistant"
echo "  3. Press Enter"
echo "  4. If it doesn't appear, wait a few seconds for Spotlight to index it"
echo ""
echo "Option 2: Assign Keyboard Shortcut"
echo "  1. Open System Preferences → Keyboard → Shortcuts"
echo "  2. Select 'App Shortcuts' from the left sidebar"
echo "  3. Click the '+' button"
echo "  4. Application: Choose '$APP_NAME'"
echo "  5. Menu Title: Leave blank (or enter any text)"
echo "  6. Keyboard Shortcut: Press your desired shortcut (e.g., ⌘⌃D)"
echo "  7. Click 'Add'"
echo ""
echo "Option 3: Test directly"
echo "  Open Finder, go to Applications, find '$APP_NAME', and double-click it"
echo ""
echo "💡 Tip: If Spotlight doesn't find it immediately, try:"
echo "  - Wait 10-30 seconds for Spotlight to index"
echo "  - Or run: sudo mdutil -E /"
echo ""

