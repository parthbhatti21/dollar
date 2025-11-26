#!/bin/bash
# Script to create a macOS application bundle for Dollar Assistant GUI

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_NAME="Dollar Assistant"

# Try /Applications first (system-wide), fallback to ~/Applications
if [ -w "/Applications" ]; then
    APP_PATH="/Applications/$APP_NAME.app"
else
    APP_PATH="$HOME/Applications/$APP_NAME.app"
    mkdir -p "$HOME/Applications"
fi

echo "Creating Dollar Assistant application..."
echo "App will be created at: $APP_PATH"

# Remove old version if exists
if [ -d "$APP_PATH" ]; then
    echo "Removing old version..."
    rm -rf "$APP_PATH"
fi

# Create the app bundle structure
mkdir -p "$APP_PATH/Contents/MacOS"
mkdir -p "$APP_PATH/Contents/Resources"

# Find Python executable (prefer venv)
if [ -f "$SCRIPT_DIR/.venv/bin/python3" ]; then
    PYTHON="$SCRIPT_DIR/.venv/bin/python3"
elif [ -f "$SCRIPT_DIR/venv/bin/python3" ]; then
    PYTHON="$SCRIPT_DIR/venv/bin/python3"
else
    PYTHON="python3"
fi

# Create the executable script
cat > "$APP_PATH/Contents/MacOS/$APP_NAME" << 'SCRIPTEOF'
#!/bin/bash
# Dollar Assistant Launcher - Opens Terminal and runs main.py

# Get the project directory (where this script was created from)
SCRIPT_DIR="/Users/parthbhatti/Codes and backups/dollar"
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Force arm64 architecture (important for NumPy and other native libraries)
if [ "$(uname -m)" = "x86_64" ] && [ "$(sysctl -n machdep.cpu.brand_string 2>/dev/null | grep -i intel)" = "" ]; then
    # Running under Rosetta, re-execute in native arm64
    exec arch -arm64 "$0" "$@"
fi

# Determine Python executable
if [ -f "$SCRIPT_DIR/.venv/bin/python3" ]; then
    PYTHON_EXEC="$SCRIPT_DIR/.venv/bin/python3"
elif [ -f "$SCRIPT_DIR/venv/bin/python3" ]; then
    PYTHON_EXEC="$SCRIPT_DIR/venv/bin/python3"
else
    PYTHON_EXEC="python3"
fi

# Open Terminal and run the assistant
osascript <<EOF
tell application "Terminal"
    activate
    do script "cd '$SCRIPT_DIR' && source .venv/bin/activate 2>/dev/null || source venv/bin/activate 2>/dev/null; cd agent && '$PYTHON_EXEC' main.py; echo ''; echo 'Press Ctrl+C to quit (or close this window)'"
end tell
EOF
SCRIPTEOF

# Make executable
chmod +x "$APP_PATH/Contents/MacOS/$APP_NAME"

# Create Info.plist
cat > "$APP_PATH/Contents/Info.plist" << PLISTEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>$APP_NAME</string>
    <key>CFBundleIdentifier</key>
    <string>com.dollar.assistant</string>
    <key>CFBundleName</key>
    <string>$APP_NAME</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSUIElement</key>
    <false/>
    <key>NSMicrophoneUsageDescription</key>
    <string>Dollar Assistant needs microphone access to detect wake words and listen to your voice commands.</string>
    <key>CFBundleIconFile</key>
    <string>app_icon</string>
</dict>
</plist>
PLISTEOF

# Copy icon to app bundle (if it exists)
if [ -f "$SCRIPT_DIR/app_icon.icns" ]; then
    cp "$SCRIPT_DIR/app_icon.icns" "$APP_PATH/Contents/Resources/app_icon.icns"
    echo "✅ Icon added to app bundle"
elif [ -f "$SCRIPT_DIR/app_icon.png" ]; then
    # If .icns doesn't exist, try to create it
    echo "Creating icon from PNG..."
    mkdir -p "$SCRIPT_DIR/app_icon.iconset"
    sips -z 16 16 "$SCRIPT_DIR/app_icon.png" --out "$SCRIPT_DIR/app_icon.iconset/icon_16x16.png" >/dev/null 2>&1
    sips -z 32 32 "$SCRIPT_DIR/app_icon.png" --out "$SCRIPT_DIR/app_icon.iconset/icon_16x16@2x.png" >/dev/null 2>&1
    sips -z 32 32 "$SCRIPT_DIR/app_icon.png" --out "$SCRIPT_DIR/app_icon.iconset/icon_32x32.png" >/dev/null 2>&1
    sips -z 64 64 "$SCRIPT_DIR/app_icon.png" --out "$SCRIPT_DIR/app_icon.iconset/icon_32x32@2x.png" >/dev/null 2>&1
    sips -z 128 128 "$SCRIPT_DIR/app_icon.png" --out "$SCRIPT_DIR/app_icon.iconset/icon_128x128.png" >/dev/null 2>&1
    sips -z 256 256 "$SCRIPT_DIR/app_icon.png" --out "$SCRIPT_DIR/app_icon.iconset/icon_128x128@2x.png" >/dev/null 2>&1
    sips -z 256 256 "$SCRIPT_DIR/app_icon.png" --out "$SCRIPT_DIR/app_icon.iconset/icon_256x256.png" >/dev/null 2>&1
    sips -z 512 512 "$SCRIPT_DIR/app_icon.png" --out "$SCRIPT_DIR/app_icon.iconset/icon_256x256@2x.png" >/dev/null 2>&1
    sips -z 512 512 "$SCRIPT_DIR/app_icon.png" --out "$SCRIPT_DIR/app_icon.iconset/icon_512x512.png" >/dev/null 2>&1
    sips -z 1024 1024 "$SCRIPT_DIR/app_icon.png" --out "$SCRIPT_DIR/app_icon.iconset/icon_512x512@2x.png" >/dev/null 2>&1
    iconutil -c icns "$SCRIPT_DIR/app_icon.iconset" -o "$SCRIPT_DIR/app_icon.icns" 2>/dev/null
    rm -rf "$SCRIPT_DIR/app_icon.iconset" 2>/dev/null
    if [ -f "$SCRIPT_DIR/app_icon.icns" ]; then
        cp "$SCRIPT_DIR/app_icon.icns" "$APP_PATH/Contents/Resources/app_icon.icns"
        echo "✅ Icon created and added to app bundle"
    fi
fi

echo ""
echo "✅ Dollar Assistant application created successfully!"
echo ""
echo "📍 Location: $APP_PATH"
echo ""
echo "🚀 How to use:"
echo "   1. Open Finder"
echo "   2. Go to Applications (or ~/Applications)"
echo "   3. Double-click 'Dollar Assistant'"
echo ""
echo "   Or use Spotlight:"
echo "   • Press ⌘Space"
echo "   • Type 'Dollar Assistant'"
echo "   • Press Enter"
echo ""
echo "💡 Tip: You can also drag it to your Dock for quick access!"
echo ""

# Force Spotlight to index the new app
if command -v mdimport &> /dev/null; then
    mdimport "$APP_PATH" 2>/dev/null || true
fi

echo "✅ Done!"

