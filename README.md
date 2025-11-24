# Dollar AI Voice Assistant

A fully local, always-running AI voice assistant that listens continuously for the wake word "hey dollar jack" and executes natural-language commands by mapping them to OS-level actions.

## 🎯 Features

- **24/7 Background Operation**: Runs continuously with minimal CPU usage
- **Always-On Wake Word Detection**: Listens for "hey dollar jack" trigger phrase
- **100% Local**: No cloud calls, all processing happens on your device
- **Cross-Platform**: Supports macOS, Windows, and Linux
- **Modular Architecture**: Easy to extend with new commands

## 📋 Requirements

- Python 3.8 or higher
- Microphone access
- macOS, Windows, or Linux

## 🚀 Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd dollar
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install system audio dependencies:**

   **macOS:**
   ```bash
   brew install portaudio
   ```

   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt-get install portaudio19-dev python3-pyaudio
   ```

   **Windows:**
   - PyAudio should install automatically via pip

5. **Configure wake word detection:**

   For **Picovoice Porcupine** (recommended):
   - Get a free access key from [Picovoice Console](https://console.picovoice.ai/)
   - Add it to `agent/config.yaml`:
     ```yaml
     wake_word:
       porcupine_access_key: "your-access-key-here"
     ```

   For **Silero VAD** (alternative):
   - Install PyTorch: `pip install torch torchaudio`
   - Install Silero VAD: `pip install silero-vad`
   - Update `config.yaml`:
     ```yaml
     wake_word:
       method: silero
     ```

## 🧪 Testing Your Setup

Before running the assistant, test your setup:

```bash
python test_setup.py
```

This will verify all dependencies and components are properly installed.

## 🏃 Running the Assistant

### Start the Assistant

**From the project root directory:**

```bash
cd agent
python main.py
```

Or if using a virtual environment:

```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
cd agent
python main.py
```

The assistant will:
1. Initialize all components
2. Say "Dollar assistant is ready."
3. Start listening for "hey dollar jack" (or your configured wake word)
4. Process commands when wake word is detected

### Run in Background (Optional)

To run the assistant in the background and keep using your terminal:

**macOS/Linux:**
```bash
cd agent
nohup python main.py > ../dollar.log 2>&1 &
```

**Check if it's running:**
```bash
pgrep -f "python.*main.py"
```

**View logs:**
```bash
tail -f dollar.log
```

### Stop the Assistant

**Option 1: Voice Command**
Say: **"dollar jack"** → **"stop the agent"** or **"stop dollar"** or **"shut down"**

**Option 2: Terminal Command**
```bash
pkill -f "python.*main.py"
```

**Option 3: Keyboard Interrupt**
If running in foreground, press `Ctrl+C` in the terminal.

## 🔧 Configuration

Edit `agent/config.yaml` to customize:

- **Wake word method**: Choose between Porcupine, Silero, or simple VAD
- **STT model**: Select Whisper model size (tiny/base/small/medium/large)
- **TTS settings**: Adjust speech rate and volume
- **Audio settings**: Configure sample rate and recording duration

## 📝 Supported Commands

### System Control
- **"lock device"** / **"lock screen"** - Lock your device
- **"shutdown"** / **"shut down"** - Shutdown the computer
- **"restart"** / **"reboot"** - Restart the computer
- **"system info"** - Get system information

### Applications
- **"open [app name]"** / **"launch [app name]"** - Open an application
  - Examples: "open chrome", "launch terminal", "start calculator"

### Media Control
- **"play"** / **"play music"** / **"start music"** - Play/resume media
- **"pause"** / **"pause music"** - Pause media playback
- **"next song"** / **"next track"** - Skip to next track
- **"previous song"** / **"previous track"** - Go to previous track
- **"stop"** / **"stop music"** / **"stop the song"** - Stop media playback
- **"play [song name] on spotify"** / **"spotify [song name]"** - Play a specific song on Spotify
  - Examples: "play bohemian rhapsody on spotify", "spotify shape of you"

### Volume Control
- **"volume up"** / **"increase volume"** - Increase volume
- **"volume down"** / **"decrease volume"** - Decrease volume
- **"set volume to [number]"** - Set volume to specific level (0-100)

### Network & Bluetooth
- **"turn on wifi"** / **"enable wifi"** - Enable WiFi
- **"turn off wifi"** / **"disable wifi"** - Disable WiFi
- **"turn on bluetooth"** / **"enable bluetooth"** - Enable Bluetooth
- **"turn off bluetooth"** / **"disable bluetooth"** - Disable Bluetooth

### Information
- **"what time"** / **"current time"** - Get current time
- **"what date"** / **"current date"** - Get current date
- **"how are you"** / **"hello"** - Greeting
- **"thank you"** / **"thanks"** - Thank the assistant
- **"goodbye"** / **"bye"** - Say goodbye

## 🏗️ Architecture

```
/agent
  ├── main.py              # Main loop and orchestration
  ├── wake_word.py         # Wake word detection
  ├── speech_to_text.py    # Whisper STT
  ├── intent_classifier.py # Intent classification
  ├── command_router.py    # Command routing
  ├── os_commands.py       # OS-level command execution
  ├── voice_output.py      # TTS output
  ├── config.py            # Configuration management
  └── config.yaml          # Configuration file
```

## 🔌 Running as a Service

### macOS (LaunchAgent)

1. Create `~/Library/LaunchAgents/com.dollar.assistant.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dollar.assistant</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/venv/bin/python</string>
        <string>/path/to/dollar/agent/main.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/dollar-assistant.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/dollar-assistant.error.log</string>
</dict>
</plist>
```

2. Load the service:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.dollar.assistant.plist
   ```

3. Start the service:
   ```bash
   launchctl start com.dollar.assistant
   ```

### Linux (systemd)

1. Create `/etc/systemd/system/dollar-assistant.service`:

```ini
[Unit]
Description=Dollar AI Voice Assistant
After=network.target sound.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/dollar
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python /path/to/dollar/agent/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. Enable and start:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable dollar-assistant
   sudo systemctl start dollar-assistant
   ```

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: "When the computer starts"
4. Action: Start a program
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `C:\path\to\dollar\agent\main.py`
5. Check "Run whether user is logged on or not"
6. Save and run

## 🛠️ Adding New Commands

1. **Add intent patterns** in `intent_classifier.py`:
   ```python
   "my_command": [
       "do something", "perform action", "execute task"
   ]
   ```

2. **Add command handler** in `os_commands.py`:
   ```python
   def my_command(self) -> Dict[str, any]:
       # Your implementation
       return {"success": True, "message": "Done"}
   ```

3. **Route the command** in `command_router.py`:
   ```python
   elif intent == "my_command":
       return self.os_commands.my_command()
   ```

## 🐛 Troubleshooting

### Wake word not detected
- Check microphone permissions
- Verify Porcupine access key is set (if using Porcupine)
- Try different wake word methods in config

### Audio issues
- Ensure microphone is working: `python -c "import sounddevice; print(sounddevice.query_devices())"`
- Check audio permissions in system settings
- Try different sample rates in config

### Command not executing
- Check logs in `agent.log`
- Verify you have necessary permissions (sudo for some commands)
- Test commands manually in terminal

### High CPU usage
- Use smaller Whisper model (tiny/base instead of large)
- Reduce wake word detection sensitivity
- Check for background processes

## 📄 License

MIT License - Feel free to modify and extend!

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Better wake word detection
- More command support
- Local LLM integration
- Better error handling
- Performance optimization

## ⚠️ Security Notes

- This assistant runs with your user permissions
- Commands like shutdown/restart require appropriate permissions
- Be cautious when adding commands that modify system settings
- Review code before running as a service

