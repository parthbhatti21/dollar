# Wake Word Detection Troubleshooting

If the wake word ("dollar jack") is not being detected, try these steps:

## 1. Check Microphone Permissions (macOS)

The app needs microphone access to detect wake words.

### To grant microphone permissions:

1. **Open System Settings** (or System Preferences on older macOS)
2. Go to **Privacy & Security** → **Microphone**
3. Look for **"Dollar Assistant"** or **"Python"** in the list
4. **Enable** the toggle next to it

### If the app doesn't appear in the list:

1. Launch the Dollar Assistant app
2. When prompted, click **"Allow"** to grant microphone access
3. If no prompt appears, try:
   - Quit the app completely
   - Re-launch it
   - macOS should prompt for permission

## 2. Test Wake Word Detection

Run this test to verify wake word detection is working:

```bash
cd "/Users/parthbhatti/Codes and backups/dollar"
source .venv/bin/activate
python3 test_voice.py
```

Say **"dollar jack"** and see if it detects. If it works here but not in the GUI app, it's likely a permissions issue.

## 3. Check Audio Stream Status

In the GUI app, check the status:
- **Green dot** = Running and listening
- **Red dot** = Error (check the error message)

If you see "Wake word detector failed to initialize", it means:
- Microphone permissions not granted, OR
- Microphone is being used by another app

## 4. Common Issues

### Issue: "Wake word detector failed to initialize"
**Solution**: Grant microphone permissions (see step 1)

### Issue: No response when saying "dollar jack"
**Possible causes**:
- Microphone permissions not granted
- Microphone is muted or not working
- Another app is using the microphone
- Background noise too loud
- Speaking too quietly

**Solutions**:
1. Check microphone permissions
2. Test your microphone in System Settings → Sound → Input
3. Close other apps that might be using the microphone
4. Speak clearly: "dollar jack"
5. Wait 1-2 seconds after saying the wake word before giving your command

### Issue: Works in terminal but not in GUI app
**Solution**: The GUI app needs separate permissions. Grant microphone access to the app bundle.

## 5. Verify Wake Word File

The wake word uses a custom keyword file. Verify it exists:

```bash
ls -la "/Users/parthbhatti/Codes and backups/dollar/agent/keywords/Dollar-jack_en_mac_v3_0_0.ppn"
```

If it doesn't exist, the app will fall back to the built-in "computer" keyword.

## 6. Check Logs

Check the log file for errors:

```bash
tail -50 "/Users/parthbhatti/Codes and backups/dollar/agent.log" | grep -i "wake\|error\|microphone\|audio"
```

## 7. Reset Permissions (Last Resort)

If nothing works, reset microphone permissions:

1. Open Terminal
2. Run: `tccutil reset Microphone`
3. Re-launch Dollar Assistant
4. Grant permissions when prompted

## Quick Test

To quickly test if wake word detection is working:

1. Launch Dollar Assistant app
2. Say **"dollar jack"** clearly
3. You should see "🎤 Wake word detected!" in the GUI
4. Then say your command (e.g., "play music")

If you don't see the detection message, follow the troubleshooting steps above.


