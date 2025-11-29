# 📱 Dollar Assistant - Android Installation Guide

This guide will help you install Dollar Assistant on your Android device.

## 📦 Method 1: Using Termux (Recommended - Most Flexible)

Termux is a terminal emulator for Android that provides a Linux environment.

### Step 1: Install Termux
1. Download **Termux** from [F-Droid](https://f-droid.org/en/packages/com.termux/) (recommended) or [Google Play Store](https://play.google.com/store/apps/details?id=com.termux)
2. Open Termux after installation

### Step 2: Transfer Files to Android

**Option A: Using USB Cable (Easiest)**
1. Connect your Android device to your Mac via USB
2. Enable **File Transfer** mode on your Android device
3. Copy the entire `dollar` folder to your Android device (e.g., `/sdcard/Download/dollar` or `/sdcard/Documents/dollar`)

**Option B: Using ADB (Advanced)**
```bash
# On your Mac, in the dollar directory:
adb push . /sdcard/dollar
```

**Option C: Using Cloud Storage**
1. Zip the `dollar` folder on your Mac
2. Upload to Google Drive, Dropbox, or similar
3. Download on your Android device
4. Extract to `/sdcard/dollar` or `/sdcard/Download/dollar`

**Option D: Using Git (If you have Git on Android)**
```bash
# In Termux:
cd ~
git clone <your-repo-url> dollar
# Or download as ZIP from GitHub and extract
```

### Step 3: Setup in Termux

```bash
# Update packages
pkg update && pkg upgrade

# Install Python and dependencies
pkg install python python-pip git

# Install system audio libraries
pkg install portaudio

# Navigate to dollar directory
cd /sdcard/dollar  # or wherever you placed it
# If permission denied, copy to home:
cp -r /sdcard/dollar ~/dollar
cd ~/dollar

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Grant storage permission (if needed)
termux-setup-storage
```

### Step 4: Configure

```bash
# Edit config file
nano agent/config.yaml
# Add your Porcupine access key if using Porcupine wake word detection
```

### Step 5: Run Dollar Assistant

```bash
# Make sure you're in the dollar directory and venv is activated
cd ~/dollar
source venv/bin/activate

# Run the assistant
cd agent
python main.py
```

### Step 6: Keep Running in Background

Termux can run in the background, but for better reliability:
1. Use **Termux:Widget** to create shortcuts
2. Or use **Termux:Boot** to auto-start on device boot
3. Or use a task manager to keep Termux running

---

## 📦 Method 2: Using Pydroid 3 (Easier GUI)

Pydroid 3 is a Python IDE for Android with a simpler interface.

### Step 1: Install Pydroid 3
- Download from [Google Play Store](https://play.google.com/store/apps/details?id=ru.iiec.pydroid3)

### Step 2: Transfer Files
- Same as Method 1, Step 2
- Place files in `/sdcard/dollar` or accessible location

### Step 3: Setup in Pydroid 3
1. Open Pydroid 3
2. Go to **Menu → Pip**
3. Install packages one by one (Pydroid has limitations):
   ```
   numpy
   PyYAML
   sounddevice
   openai-whisper
   pyttsx3
   fuzzywuzzy
   python-Levenshtein
   psutil
   scipy
   pygame
   ```

**Note:** Some packages like `pvporcupine` may not work in Pydroid. You may need to use Simple VAD instead.

### Step 4: Run
1. Open `agent/main.py` in Pydroid
2. Set working directory to the `dollar` folder
3. Run the script

---

## 📦 Method 3: Create APK with Buildozer (Advanced)

This creates a native Android app (APK file).

### Prerequisites
- Linux or macOS with Docker (or Linux VM)
- Android SDK

### Steps
1. Install Buildozer:
   ```bash
   pip install buildozer
   ```

2. Create `buildozer.spec` file (see below)

3. Build APK:
   ```bash
   buildozer android debug
   ```

This is more complex and requires significant setup. See [Buildozer documentation](https://buildozer.readthedocs.io/).

---

## 🔧 Android-Specific Configuration

### Microphone Permissions
- Termux: Grant microphone permission when prompted
- Pydroid: Grant microphone permission in app settings
- System Settings → Apps → Termux/Pydroid → Permissions → Microphone

### Battery Optimization
To keep Dollar Assistant running:
1. Go to **Settings → Battery → Battery Optimization**
2. Find **Termux** (or your Python app)
3. Set to **Don't optimize**

### Background App Limits
1. Go to **Settings → Apps → Special Access**
2. Find **Background App Limits**
3. Disable for Termux/Pydroid

---

## 🚀 Quick Start Script for Termux

Create a file `start_dollar.sh` in the dollar directory:

```bash
#!/data/data/com.termux/files/usr/bin/bash
cd ~/dollar
source venv/bin/activate
cd agent
python main.py
```

Make it executable:
```bash
chmod +x start_dollar.sh
```

Run with:
```bash
./start_dollar.sh
```

---

## 📝 Notes

1. **Wake Word Files**: The `.ppn` files in `keywords/` are macOS-specific. For Android, you'll need to:
   - Download Android versions from Picovoice Console
   - Or use Simple VAD instead (configure in `config.yaml`)

2. **Performance**: Android devices vary. Larger Whisper models may be slow on older devices. Use `small` or `base` model.

3. **Battery**: Continuous listening will drain battery. Consider:
   - Using a charger
   - Reducing wake word sensitivity
   - Using a smaller STT model

4. **Storage**: Whisper models are large (~500MB-3GB). Ensure you have enough storage.

---

## 🆘 Troubleshooting

### "Permission denied" errors
```bash
# Grant storage access
termux-setup-storage
# Or copy files to home directory
cp -r /sdcard/dollar ~/dollar
```

### Audio issues
```bash
# Install audio libraries
pkg install portaudio
# Or try:
pkg install pulseaudio
```

### Package installation fails
```bash
# Update pip
pip install --upgrade pip
# Try installing packages individually
pip install numpy
pip install PyYAML
# etc.
```

### App closes when screen locks
- Disable battery optimization for Termux
- Use a task manager to keep it running
- Consider using Termux:Boot for auto-start

---

## 📞 Need Help?

If you encounter issues:
1. Check the logs in `agent/agent.log`
2. Run `python test_setup.py` to verify installation
3. Check Android-specific error messages

