# Grant Microphone Permission - Step by Step

## The Issue
The app might appear as **"Python"** or **"Terminal"** in System Settings instead of "Dollar Assistant" because it runs a Python script.

## Solution: Grant Permission to Python/Terminal

### Step 1: Launch the App
1. Launch **Dollar Assistant** from Applications
2. Click the **"Test Microphone Access"** button in the app window
3. This will trigger a permission request

### Step 2: Grant Permission
When macOS prompts you:
- Click **"Allow"** or **"OK"**

### Step 3: If No Prompt Appears
If you don't see a prompt, manually grant permission:

1. **Open System Settings** (or System Preferences)
2. Go to **Privacy & Security** → **Microphone**
3. Look for one of these in the list:
   - **"Python"** (most likely)
   - **"Terminal"**
   - **"Dollar Assistant"** (if you're lucky)
   - **"Python Launcher"**
4. **Enable the toggle** next to it

### Step 4: Verify
1. In the Dollar Assistant app, click **"Test Microphone Access"** again
2. You should see: **"✅ Microphone access granted!"**
3. The status should change to: **"Running - Listening..."** (green dot)

## Alternative: Grant Permission via Terminal

If the app still doesn't work, you can grant permission by running this in Terminal:

```bash
cd "/Users/parthbhatti/Codes and backups/dollar"
source .venv/bin/activate
python3 -c "import pyaudio; p = pyaudio.PyAudio(); s = p.open(rate=16000, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=512); s.start_stream(); s.stop_stream(); s.close(); p.terminate(); print('Microphone test successful')"
```

This will:
1. Trigger a permission prompt
2. Click **"Allow"**
3. This grants permission to Python, which the app uses

## Why This Happens

On macOS, when an app runs a Python script, the system sees it as "Python" accessing the microphone, not the app bundle name. This is normal behavior.

## After Granting Permission

Once you've granted permission:
1. The Dollar Assistant app should work
2. You can say **"dollar jack"** to activate it
3. The app will remember this permission for future launches

## Still Not Working?

1. **Quit the app completely**
2. **Re-launch it**
3. Click **"Test Microphone Access"** button
4. Check System Settings → Privacy & Security → Microphone
5. Make sure **"Python"** is enabled

If it still doesn't work, check:
- Is your microphone working? (System Settings → Sound → Input)
- Is another app using the microphone? (Close Zoom, Teams, etc.)
- Check the logs: `tail -50 agent.log`









