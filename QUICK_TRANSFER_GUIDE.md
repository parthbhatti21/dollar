# 🚀 Quick Guide: Transfer Dollar Assistant to Android

## ✅ Package Ready!

Your Android package has been created:
- **File**: `dollar-assistant-android.zip`
- **Location**: Same folder as this file
- **Size**: ~64KB (plus dependencies to be installed)

---

## 📱 Easiest Transfer Methods

### Method 1: USB Cable (Recommended - Fastest)

1. **Connect your Android device to your Mac via USB**
2. **On Android**: When prompted, select **"File Transfer"** or **"MTP"** mode
3. **On Mac**: 
   - Open **Finder**
   - You should see your Android device in the sidebar
   - Navigate to **Internal Storage → Download** (or any folder you prefer)
4. **Copy the ZIP file**:
   - Drag `dollar-assistant-android.zip` from your Mac to the Android device's Download folder
5. **On Android**: 
   - Open **Files** app
   - Find `dollar-assistant-android.zip` in Downloads
   - Tap it to extract (or use a file manager like ZArchiver)

---

### Method 2: Cloud Storage (No Cable Needed)

1. **Upload to Cloud**:
   - Go to Google Drive, Dropbox, or any cloud service
   - Upload `dollar-assistant-android.zip`
2. **On Android**:
   - Open the cloud app (Google Drive, Dropbox, etc.)
   - Download `dollar-assistant-android.zip`
   - Extract using a file manager

---

### Method 3: Email (For Small Files)

1. **Email yourself**:
   - Attach `dollar-assistant-android.zip` to an email
   - Send to your own email address
2. **On Android**:
   - Open email app
   - Download the attachment
   - Extract using a file manager

---

### Method 4: ADB (For Developers)

If you have Android Debug Bridge (ADB) installed:

```bash
# Connect device via USB and enable USB debugging
adb devices  # Verify device is connected

# Transfer the ZIP file
adb push dollar-assistant-android.zip /sdcard/Download/
```

---

## 📲 After Transfer - Quick Setup

### Step 1: Install Termux
- Download from [F-Droid](https://f-droid.org/en/packages/com.termux/) (recommended)
- Or [Google Play Store](https://play.google.com/store/apps/details?id=com.termux)

### Step 2: Extract Files
- Extract `dollar-assistant-android.zip` to `/sdcard/Download/dollar` (or any location)

### Step 3: Open Termux and Run:

```bash
# Update packages
pkg update && pkg upgrade

# Install Python
pkg install python python-pip

# Install audio libraries
pkg install portaudio

# Navigate to dollar folder
cd /sdcard/Download/dollar
# If permission denied, copy to home:
cp -r /sdcard/Download/dollar ~/dollar
cd ~/dollar

# Setup Python environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run Dollar Assistant
cd agent
python main.py
```

---

## ⚠️ Important Notes

1. **Wake Word Files**: The `.ppn` files included are for macOS. For Android:
   - Download Android versions from [Picovoice Console](https://console.picovoice.ai/)
   - Or use Simple VAD (configure in `config.yaml`)

2. **First Run**: 
   - Grant microphone permission when Termux asks
   - Whisper will download models on first run (~500MB-3GB depending on model size)

3. **Battery**: 
   - Go to **Settings → Battery → Battery Optimization**
   - Disable optimization for Termux to keep it running

4. **Storage**: Make sure you have at least 2-3GB free for Whisper models

---

## 📖 Full Instructions

For detailed setup instructions, see **ANDROID_INSTALLATION.md**

---

## 🆘 Troubleshooting

**"Permission denied" when accessing /sdcard:**
```bash
termux-setup-storage
# Then copy files to home directory
cp -r /sdcard/Download/dollar ~/dollar
cd ~/dollar
```

**Package installation fails:**
```bash
pip install --upgrade pip
# Try installing packages one by one
pip install numpy
pip install PyYAML
```

**Microphone not working:**
- Grant microphone permission: **Settings → Apps → Termux → Permissions → Microphone**

---

## ✅ You're All Set!

Once transferred and set up, you can say **"close dollar"** on your Android device and it will work! 🎉


