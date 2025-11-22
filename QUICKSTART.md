# Quick Start Guide

Get Dollar Assistant running in 5 minutes!

## Step 1: Install Dependencies

```bash
# Run the setup script (macOS/Linux)
./setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Step 2: Get Wake Word Access Key (Recommended)

1. Go to https://console.picovoice.ai/
2. Sign up for a free account
3. Copy your access key
4. Edit `agent/config.yaml` and paste it:
   ```yaml
   wake_word:
     porcupine_access_key: "your-key-here"
   ```

**Note:** Without Porcupine, the simple VAD fallback will trigger on ANY speech, not just "hey dollar". Porcupine is strongly recommended.

## Step 3: Test Your Setup

```bash
python test_setup.py
```

Fix any missing dependencies before proceeding.

## Step 4: Run the Assistant

```bash
cd agent
python main.py
```

You should hear: **"Dollar assistant is ready."**

## Step 5: Try It Out!

1. Say: **"hey dollar"**
2. Wait for: **"Yes?"**
3. Say a command, for example:
   - **"lock device"**
   - **"open chrome"**
   - **"volume up"**
   - **"what time"**

## Troubleshooting

### "No module named 'X'"
```bash
pip install -r requirements.txt
```

### "Microphone not found"
- Check system microphone permissions
- On macOS: System Preferences > Security & Privacy > Microphone
- Test with: `python -c "import sounddevice; print(sounddevice.query_devices())"`

### "Wake word not detected"
- Verify Porcupine access key is set
- Check microphone is working
- Try speaking louder or closer to microphone

### "Command not executing"
- Check `agent.log` for errors
- Some commands require sudo/admin permissions
- Test commands manually in terminal first

## Next Steps

- Read the full [README.md](README.md) for advanced configuration
- Set up as a service using [service/README.md](service/README.md)
- Add custom commands (see README.md section "Adding New Commands")

## Need Help?

Check the logs:
```bash
tail -f agent/agent.log
```

