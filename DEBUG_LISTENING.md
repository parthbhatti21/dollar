# Debug: App Says Ready But Not Listening

## Quick Check

The app says "Dollar assistant is ready" but doesn't detect wake words. Here's how to debug:

## Step 1: Check if Detection Loop is Running

The app should be continuously checking for wake words. Check the logs:

```bash
tail -f "/Users/parthbhatti/Codes and backups/dollar/agent.log"
```

You should see:
- "Wake word detection loop running (heartbeat)" every 30 seconds
- If you don't see this, the loop might not be running

## Step 2: Test Wake Word Detection Directly

Run this test to verify wake word detection works:

```bash
cd "/Users/parthbhatti/Codes and backups/dollar"
source .venv/bin/activate
python3 test_voice.py
```

Say **"dollar jack"** clearly. If it detects here but not in the app, there's an issue with the app.

## Step 3: Check Audio Stream Status

In the GUI app, check:
- Status should show: **"Running - Listening for 'porcupine' wake word..."** (green dot)
- If it shows red, there's an error

## Step 4: Verify Wake Word

Make sure you're saying the correct wake word:
- **"dollar jack"** (two words, clearly pronounced)
- Not "dollar" alone
- Not "hey dollar" (unless you configured that)

## Step 5: Check for Errors

Look for errors in the logs:

```bash
grep -i "error\|exception\|failed" "/Users/parthbhatti/Codes and backups/dollar/agent.log" | tail -20
```

## Common Issues

### Issue: Loop Not Running
**Symptoms**: No heartbeat logs, app frozen
**Solution**: Restart the app

### Issue: Audio Stream Not Active
**Symptoms**: "Audio stream is None" in logs
**Solution**: 
1. Click "Test Microphone Access" button
2. Grant microphone permissions
3. Restart app

### Issue: Wake Word Not Detected
**Possible causes**:
- Speaking too quietly
- Background noise too loud
- Wrong wake word pronunciation
- Microphone not working

**Solutions**:
1. Speak clearly: **"dollar jack"**
2. Wait 1-2 seconds after saying wake word
3. Check microphone in System Settings → Sound → Input
4. Test with `test_voice.py` script

### Issue: Detection Works in Terminal But Not in App
**Solution**: This is usually a permissions issue. Make sure Python has microphone access in System Settings.

## Still Not Working?

1. **Quit the app completely**
2. **Check logs**: `tail -50 agent.log`
3. **Restart the app**
4. **Say "dollar jack" clearly and wait**

If it still doesn't work, share the log output and I can help debug further.



