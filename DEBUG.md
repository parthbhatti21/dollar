# Debugging Guide - Assistant Not Responding

## Quick Tests

### 1. Test TTS (Voice Output)
```bash
cd agent
python -c "from voice_output import VoiceOutput; from config import load_config; v = VoiceOutput(load_config()); v.speak('Testing voice output')"
```

If this doesn't speak, TTS is the issue.

### 2. Test Wake Word Detection
```bash
python test_voice.py
```

This will test both TTS and wake word detection.

### 3. Check Logs
```bash
cd agent
tail -f agent.log
```

Look for:
- "Wake word detected!" - means detection is working
- "Error speaking" - TTS issue
- "Error in wake word detection" - detection issue

## Common Issues

### Issue: Wake word not detected
**Symptoms:** No response when saying "dollar jack"

**Solutions:**
1. Check microphone permissions (System Settings > Privacy > Microphone)
2. Verify keyword file exists: `ls agent/keywords/Dollar-jack_en_mac_v3_0_0.ppn`
3. Check Porcupine access key in config.yaml
4. Try saying "dollar jack" more clearly/loudly
5. Check logs for Porcupine errors

### Issue: TTS not working
**Symptoms:** Wake word detected but no voice response

**Solutions:**
1. Test TTS directly (see test above)
2. Check system volume
3. Try different TTS method in config.yaml (pyttsx3 or coqui)
4. Check logs for TTS errors

### Issue: No response at all
**Symptoms:** Nothing happens

**Check:**
1. Is the assistant running? Check process: `ps aux | grep python`
2. Check logs: `tail -f agent/agent.log`
3. Verify all components initialized successfully
4. Check for Python errors in terminal

## Manual Test Steps

1. **Start assistant:**
   ```bash
   cd agent
   python main.py
   ```

2. **You should hear:** "Dollar assistant is ready."

3. **Say:** "dollar jack"

4. **You should hear:** "Yes, I'm listening."

5. **Then say your command:** e.g., "what time is it"

## Enable Verbose Logging

Edit `agent/main.py` and change:
```python
level=logging.INFO,
```
to:
```python
level=logging.DEBUG,
```

This will show more detailed information about what's happening.

