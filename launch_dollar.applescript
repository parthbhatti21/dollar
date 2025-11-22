-- AppleScript to launch Dollar Assistant
-- Save this as an application and assign a keyboard shortcut in System Preferences

tell application "Terminal"
    -- Get the path to the dollar directory
    set dollarPath to POSIX path of (path to home folder) & "Codes and backups/dollar"
    
    -- Check if already running
    try
        do shell script "pgrep -f 'python.*main.py'"
        display notification "Dollar Assistant is already running" with title "Dollar Assistant"
        return
    end try
    
    -- Activate Terminal and run the script
    activate
    set currentTab to do script "cd " & quoted form of dollarPath & " && ./launch_dollar.sh"
end tell



