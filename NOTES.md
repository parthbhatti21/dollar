# Important Notes

## Wake Word

**Current Status:** Porcupine is using the built-in "computer" keyword as a fallback since "hey dollar" is not a built-in keyword.

**To use "hey dollar" as wake word:**
1. Go to [Picovoice Console](https://console.picovoice.ai/)
2. Create a custom keyword "hey dollar"
3. Download the `.ppn` file
4. Save it to `agent/keywords/hey_dollar.ppn`
5. Update `config.yaml`:
   ```yaml
   wake_word:
     keyword_path: "agent/keywords/hey_dollar.ppn"
   ```

**For now:** Say **"computer"** to wake the assistant (this is Porcupine's built-in keyword).

## SSL Certificate Issues

The code includes SSL workarounds for Whisper model downloads. If you encounter SSL errors, they should be automatically handled. If issues persist, you may need to:
- Update your system's SSL certificates
- Configure your network/proxy settings
- Download the Whisper model manually

## First Run

On the first run, Whisper will download the model (base size, ~150MB). This may take a few minutes depending on your internet connection. The model is cached locally after the first download.

