# Simple Keyboard Shortcut Setup (All macOS Versions)

## Method 1: Using System Preferences Directly (Easiest)

### Step 1: Create the Application

Run this command in Terminal:

```bash
cd "/Users/parthbhatti/Codes and backups/dollar"
./create_shortcut.sh
```

This creates an application in your Applications folder.

### Step 2: Assign Keyboard Shortcut

1. Open **System Preferences** → **Keyboard** → **Shortcuts**
2. Select **App Shortcuts** from the left sidebar
3. Click the **+** button
4. **Application**: Select "Launch Dollar Assistant" (or "All Applications" for global)
5. **Menu Title**: Leave blank or enter any text
6. **Keyboard Shortcut**: Press your desired keys (e.g., `⌘⌃D` or `⌘⌥D`)
7. Click **Add**

### Step 3: Test

Press your keyboard shortcut! The assistant should start.

---

## Method 2: Using Automator (If Available)

### Finding Automator Options

1. Open **Automator** (Applications → Utilities → Automator)
2. When prompted, look for these options:
   - **Application** - Creates a standalone app
   - **Service** - Creates a service (older macOS)
   - **Quick Action** - Creates a quick action (newer macOS)
   - **Workflow** - Basic automation

### If you see "Application":

1. Choose **Application**
2. Add action: **Run Shell Script**
3. Set Shell to: `/bin/bash`
4. Paste this script:
   ```bash
   cd "/Users/parthbhatti/Codes and backups/dollar"
   ./launch_dollar_automator.sh
   ```
5. Save as: **"Launch Dollar Assistant.app"** in your Applications folder
6. Then follow Step 2 from Method 1 above

### If you see "Service" or "Quick Action":

1. Choose **Service** or **Quick Action**
2. Set: **Workflow receives: no input** in **any application**
3. Add action: **Run Shell Script**
4. Set Shell to: `/bin/bash`
5. Paste this script:
   ```bash
   cd "/Users/parthbhatti/Codes and backups/dollar"
   ./launch_dollar_automator.sh
   ```
6. Save as: **"Launch Dollar Assistant"**
7. Go to **System Preferences** → **Keyboard** → **Shortcuts** → **Services**
8. Find "Launch Dollar Assistant" and assign a shortcut

---

## Method 3: Using Terminal Command (Fastest)

### Create a simple alias

Add this to your `~/.zshrc` or `~/.bash_profile`:

```bash
alias dollar='cd "/Users/parthbhatti/Codes and backups/dollar" && ./launch_dollar_automator.sh'
```

Then reload:
```bash
source ~/.zshrc  # or source ~/.bash_profile
```

Now you can just type `dollar` in Terminal to start it!

---

## Method 4: Using Spotlight (No Shortcut Needed)

1. Press `⌘Space` to open Spotlight
2. Type: `Launch Dollar Assistant`
3. Press Enter

This works if you created the app using Method 1 or 2.

---

## Recommended Keyboard Shortcuts

- `⌘⌃D` (Cmd+Ctrl+D) - "D" for Dollar
- `⌘⌥D` (Cmd+Option+D) - Also good
- `⌃⌥D` (Ctrl+Option+D) - If Cmd conflicts
- `⌘⌃⌥D` (Cmd+Ctrl+Option+D) - Very unlikely to conflict

---

## Troubleshooting

### "Application not found"
- Make sure you ran `./create_shortcut.sh` first
- Check that the app is in `~/Applications/` or `/Applications/`

### Shortcut doesn't work
- Make sure it's enabled in System Preferences
- Check for conflicts with other apps
- Try a different shortcut combination
- Restart System Preferences

### Script doesn't run
- Check file permissions: `chmod +x launch_dollar_automator.sh`
- Verify the path in the script matches your directory
- Check `dollar.log` for errors

---

## Quick Test

Test the launch script directly:

```bash
cd "/Users/parthbhatti/Codes and backups/dollar"
./launch_dollar_automator.sh
```

If this works, the keyboard shortcut will work too!



