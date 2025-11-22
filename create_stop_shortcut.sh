#!/bin/bash
# Create a stop shortcut application

APP_NAME="Stop Dollar Assistant"
if [ -w "/Applications" ]; then
    APP_PATH="/Applications/$APP_NAME.app"
else
    APP_PATH="$HOME/Applications/$APP_NAME.app"
    mkdir -p "$HOME/Applications"
fi

echo "Creating stop application..."

# Remove old version if exists
if [ -d "$APP_PATH" ]; then
    rm -rf "$APP_PATH"
fi

# Create the app bundle structure
mkdir -p "$APP_PATH/Contents/MacOS"
mkdir -p "$APP_PATH/Contents/Resources"

# Create the executable script
cat > "$APP_PATH/Contents/MacOS/$APP_NAME" << 'EOF'
#!/bin/bash
exec "/Users/parthbhatti/Codes and backups/dollar/stop_dollar.sh"
EOF

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
    <string>com.dollar.assistant.stop</string>
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
</dict>
</plist>
EOF

echo "✅ Stop application created at: $APP_PATH"
echo ""
echo "📋 To assign a keyboard shortcut:"
echo "1. Open System Preferences → Keyboard → Shortcuts"
echo "2. Select 'App Shortcuts' from the left sidebar"
echo "3. Click the '+' button"
echo "4. Application: Choose '$APP_NAME'"
echo "5. Menu Title: Leave blank"
echo "6. Keyboard Shortcut: Press your desired shortcut (e.g., ⌘⌃S)"
echo "7. Click 'Add'"



