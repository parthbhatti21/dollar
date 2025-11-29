#!/bin/bash
# Script to package Dollar Assistant for Android transfer
# Creates a ZIP file with all necessary files

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PACKAGE_NAME="dollar-assistant-android"
OUTPUT_DIR="$SCRIPT_DIR"
ZIP_FILE="$OUTPUT_DIR/$PACKAGE_NAME.zip"

echo "📦 Packaging Dollar Assistant for Android..."
echo ""

# Create temporary directory
TEMP_DIR=$(mktemp -d)
PACKAGE_DIR="$TEMP_DIR/dollar"

# Copy necessary files
echo "📋 Copying files..."

# Create directory structure
mkdir -p "$PACKAGE_DIR/agent"
mkdir -p "$PACKAGE_DIR/agent/keywords"

# Copy agent files
cp -r "$SCRIPT_DIR/agent"/*.py "$PACKAGE_DIR/agent/" 2>/dev/null
cp "$SCRIPT_DIR/agent/config.yaml" "$PACKAGE_DIR/agent/" 2>/dev/null
cp "$SCRIPT_DIR/agent/__init__.py" "$PACKAGE_DIR/agent/" 2>/dev/null

# Copy keywords (note: .ppn files are macOS-specific, but include for reference)
if [ -d "$SCRIPT_DIR/agent/keywords" ]; then
    cp -r "$SCRIPT_DIR/agent/keywords"/* "$PACKAGE_DIR/agent/keywords/" 2>/dev/null
fi

# Copy requirements and documentation
cp "$SCRIPT_DIR/requirements.txt" "$PACKAGE_DIR/" 2>/dev/null
cp "$SCRIPT_DIR/README.md" "$PACKAGE_DIR/" 2>/dev/null
cp "$SCRIPT_DIR/ANDROID_INSTALLATION.md" "$PACKAGE_DIR/" 2>/dev/null
cp "$SCRIPT_DIR/COMMANDS.md" "$PACKAGE_DIR/" 2>/dev/null

# Create Android-specific README
cat > "$PACKAGE_DIR/ANDROID_README.txt" << 'EOF'
========================================
Dollar Assistant - Android Package
========================================

This package contains all files needed to run Dollar Assistant on Android.

INSTALLATION:
1. Extract this ZIP file to your Android device
2. Follow the instructions in ANDROID_INSTALLATION.md
3. Recommended: Use Termux app for best results

QUICK START (Termux):
1. Install Termux from F-Droid or Play Store
2. In Termux, run:
   pkg update && pkg upgrade
   pkg install python python-pip
   pkg install portaudio
   
3. Navigate to this folder:
   cd /sdcard/Download/dollar  # or wherever you extracted
   
4. Setup Python environment:
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
5. Run:
   cd agent
   python main.py

IMPORTANT NOTES:
- Wake word files (.ppn) are macOS-specific
- For Android, you may need to download Android versions from Picovoice
- Or use Simple VAD instead (configure in config.yaml)
- Grant microphone permission when prompted
- Disable battery optimization for continuous operation

For detailed instructions, see ANDROID_INSTALLATION.md
EOF

# Create a simple start script for Termux
cat > "$PACKAGE_DIR/start_dollar.sh" << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
# Dollar Assistant startup script for Termux

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Run Dollar Assistant
cd agent
python main.py
EOF

chmod +x "$PACKAGE_DIR/start_dollar.sh"

# Create .gitignore for Android
cat > "$PACKAGE_DIR/.gitignore" << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.log

# Android
*.apk
*.aab
EOF

# Create ZIP file
echo "📦 Creating ZIP file..."
cd "$TEMP_DIR"
zip -r "$ZIP_FILE" dollar > /dev/null

# Cleanup
rm -rf "$TEMP_DIR"

# Calculate size
SIZE=$(du -h "$ZIP_FILE" | cut -f1)

echo ""
echo "✅ Package created successfully!"
echo ""
echo "📦 Package: $ZIP_FILE"
echo "📊 Size: $SIZE"
echo ""
echo "📱 Next steps:"
echo "1. Transfer $ZIP_FILE to your Android device"
echo "2. Extract it on your device"
echo "3. Follow instructions in ANDROID_INSTALLATION.md"
echo ""
echo "💡 Transfer methods:"
echo "   - USB cable: Connect device and copy file"
echo "   - Cloud: Upload to Google Drive/Dropbox and download on device"
echo "   - ADB: adb push $ZIP_FILE /sdcard/Download/"
echo ""


