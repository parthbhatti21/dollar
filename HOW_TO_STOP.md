# How to Stop Dollar Assistant

There are several ways to stop the Dollar Assistant:

## Method 1: Voice Command (Easiest)

Just say:
- **"dollar jack"** → **"stop the agent"**
- **"dollar jack"** → **"stop dollar"**
- **"dollar jack"** → **"shut down"**

The assistant will say "Shutting down. Goodbye." and stop.

---

## Method 2: Stop Script

Run in Terminal:
```bash
cd "/Users/parthbhatti/Codes and backups/dollar"
./stop_dollar.sh
```

Or use Spotlight:
1. Press `⌘Space`
2. Type: **"Stop Dollar Assistant"**
3. Press Enter

---

## Method 3: Keyboard Shortcut

1. Run: `./create_stop_shortcut.sh` (if you haven't already)
2. Open **System Preferences** → **Keyboard** → **Shortcuts**
3. Select **App Shortcuts**
4. Click **+**
5. Application: **"Stop Dollar Assistant"**
6. Keyboard Shortcut: Press your shortcut (e.g., `⌘⌃S`)
7. Click **Add**

Now press your shortcut to stop the assistant!

---

## Method 4: Terminal Command

```bash
pkill -f "python.*main.py"
```

Or if that doesn't work:
```bash
pkill -9 -f "python.*main.py"
```

---

## Method 5: Activity Monitor

1. Open **Activity Monitor** (Applications → Utilities)
2. Search for: **"python"** or **"main.py"**
3. Select the process
4. Click **Quit** or **Force Quit**

---

## Quick Reference

| Method | Command/Shortcut |
|--------|------------------|
| Voice | "dollar jack" → "stop the agent" |
| Spotlight | `⌘Space` → "Stop Dollar Assistant" |
| Keyboard | Your assigned shortcut (e.g., `⌘⌃S`) |
| Terminal | `./stop_dollar.sh` or `pkill -f "python.*main.py"` |

---

## Recommended Setup

1. **Start**: `⌘⌃D` (Launch Dollar Assistant)
2. **Stop**: `⌘⌃S` (Stop Dollar Assistant)

This gives you quick control with keyboard shortcuts!



