# Fix Microphone Access for Dollar Assistant

## Quick Fix (3 Steps)

### Step 1: Reset Permissions (Already Done)
✅ I've already reset your microphone permissions. This clears any previous denials.

### Step 2: Launch the App
1. **Quit** Dollar Assistant if it's running
2. Launch **Dollar Assistant** from Applications (or Spotlight: `⌘Space` → "Dollar Assistant")
3. **macOS will prompt you** to allow microphone access
4. Click **"Allow"** or **"OK"**

### Step 3: Verify It Works
- The app window should show: **"Running - Listening..."** (green dot)
- Say **"dollar jack"** clearly
- You should see **"🎤 Wake word detected!"** in the window

## If No Prompt Appears

If macOS doesn't prompt you for permission:

### Manual Permission Grant:

1. **Open System Settings** (or System Preferences)
2. Go to **Privacy & Security** → **Microphone**
3. Look for **"Dollar Assistant"** in the list
4. **Enable the toggle** next to it

### If "Dollar Assistant" Doesn't Appear:

1. **Launch the app first** (it needs to try accessing the mic)
2. Then check System Settings → Privacy & Security → Microphone
3. It should appear as **"Dollar Assistant"** or **"Python"**
4. Enable the toggle

## Test Microphone Access

To verify your microphone is working:

```bash
cd "/Users/parthbhatti/Codes and backups/dollar"
source .venv/bin/activate
python3 test_voice.py
```

Say "dollar jack" and see if it detects. If this works, the issue is just app permissions.

## Still Not Working?

### Check System Microphone:
1. System Settings → Sound → Input
2. Test your microphone - speak and see if the level meter moves
3. Make sure the correct microphone is selected

### Check for Other Apps Using Microphone:
- Close other apps that might be using the microphone (Zoom, Teams, etc.)
- Try again

### Check Logs:
```bash
tail -50 "/Users/parthbhatti/Codes and backups/dollar/agent.log" | grep -i "microphone\|permission\|audio"
```

Look for error messages about microphone access.

## What I Changed

1. ✅ Added `NSMicrophoneUsageDescription` to Info.plist (required for macOS)
2. ✅ Added better error messages when microphone is denied
3. ✅ Reset microphone permissions (cleared previous denials)
4. ✅ Added helpful instructions in the GUI when microphone fails

The app is now ready - just launch it and grant permissions when prompted!








