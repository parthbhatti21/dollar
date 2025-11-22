# Keyboard Shortcut Setup for Dollar Assistant

This guide shows you how to set up a keyboard shortcut to launch the Dollar Assistant on macOS.

## Method 1: Using Automator (Recommended)

### Step 1: Create an Automator Service

1. Open **Automator** (Applications → Utilities → Automator)
2. Choose **Quick Action** (or **Service** on older macOS)
3. Set the workflow to receive **no input** in **any application**
4. Add these actions:

   **Action 1: Run Shell Script**
   - Shell: `/bin/bash`
   - Pass input: `as arguments`
   - Script:
     ```bash
     cd "/Users/parthbhatti/Codes and backups/dollar"
     if [ -d "venv" ]; then
         source venv/bin/activate
     fi
     if pgrep -f "python.*main.py" > /dev/null; then
         osascript -e 'display notification "Dollar Assistant is already running" with title "Dollar Assistant"'
         exit 0
     fi
     cd agent
     python3 main.py &
     ```
   
   **Action 2: Display Notification** (optional)
   - Title: "Dollar Assistant"
   - Message: "Starting Dollar Assistant..."

5. Save as: **"Launch Dollar Assistant"**

### Step 2: Assign Keyboard Shortcut

1. Open **System Preferences** → **Keyboard** → **Shortcuts**
2. Select **Services** from the left sidebar
3. Find **"Launch Dollar Assistant"** in the list
4. Click on it and press your desired keyboard shortcut (e.g., `⌘⌃D` or `⌘⌥D`)
5. Make sure the checkbox is enabled

### Step 3: Test

Press your keyboard shortcut to launch the Dollar Assistant!

---

## Method 2: Using AppleScript Application

### Step 1: Create AppleScript App

1. Open **Script Editor** (Applications → Utilities → Script Editor)
2. Copy and paste the contents of `launch_dollar.applescript`
3. Update the path in the script to match your system:
   ```applescript
   set dollarPath to POSIX path of (path to home folder) & "Codes and backups/dollar"
   ```
4. Save as: **"Launch Dollar.app"** (File Format: Application)
5. Save it to your Applications folder

### Step 2: Assign Keyboard Shortcut

1. Open **System Preferences** → **Keyboard** → **Shortcuts**
2. Select **App Shortcuts** from the left sidebar
3. Click the **+** button
4. Select **Launch Dollar** from the Application dropdown
5. Enter menu title: **"Launch Dollar"** (or leave blank for global shortcut)
6. Press your desired keyboard shortcut
7. Click **Add**

---

## Method 3: Using Third-Party Apps

### Option A: Keyboard Maestro
1. Create a new macro
2. Add trigger: Keyboard shortcut
3. Add action: Execute Shell Script
4. Use the script from `launch_dollar.sh`

### Option B: BetterTouchTool
1. Create a new gesture/shortcut
2. Set action: Execute Terminal Command
3. Use the script from `launch_dollar.sh`

---

## Method 4: Using Launch Agents (Background Service)

If you want the assistant to run in the background automatically:

1. Use the existing LaunchAgent configuration:
   ```bash
   cd service/macos
   cp com.dollar.assistant.plist ~/Library/LaunchAgents/
   launchctl load ~/Library/LaunchAgents/com.dollar.assistant.plist
   ```

2. Then create a keyboard shortcut to check status or restart:
   ```bash
   # Check if running
   pgrep -f "python.*main.py" || launchctl start com.dollar.assistant
   ```

---

## Recommended Shortcuts

- `⌘⌃D` (Cmd+Ctrl+D) - Easy to press, unlikely to conflict
- `⌘⌥D` (Cmd+Option+D) - Also good, "D" for Dollar
- `⌃⌥D` (Ctrl+Option+D) - If Cmd conflicts with other apps

---

## Troubleshooting

### Shortcut doesn't work
- Make sure the service/application is enabled in System Preferences
- Check for conflicts with other applications
- Try a different shortcut combination

### Script doesn't run
- Check that the path in the script matches your actual directory
- Make sure Python 3 is installed and accessible
- Verify the virtual environment path is correct

### Permission errors
- Make sure `launch_dollar.sh` is executable: `chmod +x launch_dollar.sh`
- Grant Terminal/Automator full disk access in System Preferences → Security & Privacy

---

## Quick Test

Test the launch script directly:
```bash
cd "/Users/parthbhatti/Codes and backups/dollar"
./launch_dollar.sh
```

If this works, the keyboard shortcut will work too!



