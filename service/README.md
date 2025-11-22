# Service Installation Guides

This directory contains service configuration files for running Dollar Assistant as a background service on different operating systems.

## macOS (LaunchAgent)

1. **Edit the plist file:**
   - Open `macos/com.dollar.assistant.plist`
   - Update the paths to match your installation:
     - Replace `/Users/parthbhatti/Codes and backups/dollar/` with your actual path
     - Replace `venv/bin/python` path if different

2. **Copy to LaunchAgents directory:**
   ```bash
   cp service/macos/com.dollar.assistant.plist ~/Library/LaunchAgents/
   ```

3. **Load the service:**
   ```bash
   launchctl load ~/Library/LaunchAgents/com.dollar.assistant.plist
   ```

4. **Start the service:**
   ```bash
   launchctl start com.dollar.assistant
   ```

5. **Check status:**
   ```bash
   launchctl list | grep dollar
   ```

6. **View logs:**
   ```bash
   tail -f /tmp/dollar-assistant.log
   ```

7. **Stop the service:**
   ```bash
   launchctl stop com.dollar.assistant
   ```

8. **Unload the service:**
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.dollar.assistant.plist
   ```

## Linux (systemd)

1. **Edit the service file:**
   - Open `linux/dollar-assistant.service`
   - Update paths:
     - Replace `/path/to/dollar` with your actual path
     - Replace `%i` with your username, or set `User=your-username`

2. **Copy to systemd directory:**
   ```bash
   sudo cp service/linux/dollar-assistant.service /etc/systemd/system/
   ```

3. **Reload systemd:**
   ```bash
   sudo systemctl daemon-reload
   ```

4. **Enable service (start on boot):**
   ```bash
   sudo systemctl enable dollar-assistant
   ```

5. **Start the service:**
   ```bash
   sudo systemctl start dollar-assistant
   ```

6. **Check status:**
   ```bash
   sudo systemctl status dollar-assistant
   ```

7. **View logs:**
   ```bash
   sudo journalctl -u dollar-assistant -f
   ```

8. **Stop the service:**
   ```bash
   sudo systemctl stop dollar-assistant
   ```

9. **Disable service:**
   ```bash
   sudo systemctl disable dollar-assistant
   ```

## Windows

### Option 1: Task Scheduler (Recommended)

1. Open **Task Scheduler** (search in Start menu)
2. Click **Create Basic Task**
3. Name: "Dollar Assistant"
4. Trigger: **When the computer starts**
5. Action: **Start a program**
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `C:\path\to\dollar\agent\main.py`
   - Start in: `C:\path\to\dollar`
6. Check **"Run whether user is logged on or not"**
7. Check **"Run with highest privileges"** (if needed for some commands)
8. Finish and test

### Option 2: NSSM (Non-Sucking Service Manager)

1. **Download NSSM:**
   - Visit https://nssm.cc/download
   - Extract to `C:\nssm\`

2. **Edit the PowerShell script:**
   - Open `windows/install-service.ps1`
   - Update paths to match your installation

3. **Run as Administrator:**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   .\service\windows\install-service.ps1
   ```

4. **Start the service:**
   ```cmd
   net start DollarAssistant
   ```

5. **Stop the service:**
   ```cmd
   net stop DollarAssistant
   ```

6. **View logs:**
   - Check `C:\logs\dollar-assistant.log`

## Troubleshooting

### Service won't start
- Check file paths are correct
- Verify Python and dependencies are installed
- Check logs for errors
- Ensure microphone permissions are granted

### Service stops immediately
- Check Python virtual environment is activated in the service
- Verify all dependencies are installed
- Check system logs for errors

### No audio/microphone access
- Grant microphone permissions in system settings
- On macOS: System Preferences > Security & Privacy > Microphone
- On Linux: Check PulseAudio/ALSA configuration
- On Windows: Settings > Privacy > Microphone

### High CPU usage
- Use smaller Whisper model in config
- Reduce wake word detection frequency
- Check for other audio processes

