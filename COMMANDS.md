# Dollar Assistant - Available Commands

Say **"dollar jack"** to wake the assistant, then give your command.

## 🖥️ System Control

### Lock Device
- "lock device"
- "lock screen"
- "lock computer"
- "lock my device"
- "secure"

### Shutdown
- "shutdown"
- "shut down"
- "power off"
- "turn off computer"

### Restart
- "restart"
- "reboot"
- "restart computer"
- "reboot computer"

## 📱 Applications

### Open Application
- "open [app name]"
- "launch [app name]"
- "start [app name]"

**Examples:**
- "open chrome"
- "launch terminal"
- "start calculator"
- "open safari"
- "launch spotify"
- "open notes"

**Supported apps on macOS:**
- Chrome, Firefox, Safari
- Terminal, Calculator
- Notes, Mail, Calendar
- Spotify, Music
- Messages, and more

## 🔊 Volume Control

### Volume Up
- "volume up"
- "increase volume"
- "turn up volume"
- "louder"
- "raise volume"

### Volume Down
- "volume down"
- "decrease volume"
- "turn down volume"
- "quieter"
- "lower volume"

### Set Volume
- "set volume to [number]"
- "volume to [number]"
- "volume at [number] percent"

**Examples:**
- "set volume to 50"
- "volume to 75"
- "volume at 25 percent"

## 📶 Network

### WiFi On
- "turn on wifi"
- "enable wifi"
- "wifi on"
- "connect wifi"

### WiFi Off
- "turn off wifi"
- "disable wifi"
- "wifi off"
- "disconnect wifi"

## ℹ️ Information

### Time
- "what time"
- "current time"
- "time now"
- "what's the time"
- "tell me the time"

### Date
- "what date"
- "current date"
- "date today"
- "what's the date"
- "tell me the date"

### System Info
- "system info"
- "system information"
- "system status"
- "device info"
- "computer info"
- "show system info"

### Weather
- "weather"
- "what's the weather"
- "weather forecast"
- "how's the weather"

*(Note: Weather requires API configuration)*

## 🛑 Stop Assistant

- "stop the agent"
- "stop dollar"
- "shut down"

## 📝 Usage Examples

**Complete interaction:**
```
You: "dollar jack"
Assistant: "Yes, I'm listening."
You: "what time is it"
Assistant: "The current time is 3:45 PM"
```

**More examples:**
- "dollar jack" → "lock device"
- "dollar jack" → "open chrome"
- "dollar jack" → "volume up"
- "dollar jack" → "what date"
- "dollar jack" → "system info"

## 💡 Tips

1. **Speak clearly** - The assistant uses Whisper STT, so clear speech helps
2. **Wait for acknowledgment** - After saying "dollar jack", wait for "Yes, I'm listening."
3. **Natural language** - You can phrase commands naturally, e.g., "what's the time" or "tell me the time"
4. **App names** - Use common app names (chrome, safari, terminal, etc.)

## 🔧 Adding New Commands

To add new commands, edit:
- `agent/intent_classifier.py` - Add intent patterns
- `agent/os_commands.py` - Add command implementation
- `agent/command_router.py` - Route the new intent

See README.md for detailed instructions.

