#!/usr/bin/env python3
"""
Test script to play a song on Spotify via command line.
Usage: python test_spotify.py "song name"
"""

import sys
import subprocess
import time

def play_spotify_song(song_name):
    """Play a song on Spotify using command line."""
    
    # Check if Spotify is running
    check_cmd = ['pgrep', '-x', 'Spotify']
    result = subprocess.run(check_cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Spotify is not running. Please open Spotify first.")
        return False
    
    print(f"✅ Spotify is running")
    print(f"🎵 Searching for: {song_name}")
    
    # Escape the song name for AppleScript
    escaped_song = song_name.replace('\\', '\\\\').replace('"', '\\"')
    
    # Search and play - using a more reliable method (in background)
    # First ensure Spotify is ready by checking its state
    ready_script = '''
    tell application "Spotify"
        try
            set playerState to player state
            return "ready"
        on error
            return "not ready"
        end try
    end tell
    '''
    
    ready_result = subprocess.run(['osascript', '-e', ready_script], capture_output=True, text=True)
    if "ready" not in ready_result.stdout:
        print("⚠️  Spotify may not be fully ready. Waiting a bit more...")
        time.sleep(1)
    
    # Now try the search with a simpler approach
    search_script = f'''
    tell application "Spotify"
        try
            set theSearch to "{escaped_song}"
            
            -- Try search with explicit type
            set searchResults to search for theSearch
            
            if (count of searchResults) > 0 then
                set trackToPlay to item 1 of searchResults
                play trackToPlay
                delay 0.75
                
                try
                    set currentTrack to name of current track
                    set currentArtist to artist of current track
                    return "Playing " & currentTrack & " by " & currentArtist
                on error
                    return "Playing track from search results"
                end try
            else
                return "Could not find: " & theSearch
            end if
        on error errMsg number errNum
            if errNum = -1728 then
                return "Error: Spotify is not responding. Make sure Spotify is open and logged in."
            else if errNum = -1708 then
                -- Fallback: Use keyboard shortcuts to search and play (minimize popup)
                try
                    -- Save current frontmost application
                    tell application "System Events"
                        set frontApp to name of first application process whose frontmost is true
                    end tell
                    
                    -- Activate Spotify and immediately minimize it
                    tell application "Spotify"
                        activate
                    end tell
                    
                    -- Minimize Spotify window immediately so it doesn't pop up
                    tell application "System Events"
                        tell process "Spotify"
                            -- Minimize all windows
                            repeat with w in windows
                                try
                                    set minimized of w to true
                                end try
                            end repeat
                            delay 0.1
                        end tell
                        
                        -- Now send keyboard commands (app is active but minimized)
                        tell process "Spotify"
                            -- Open search (Cmd+K)
                            keystroke "k" using {{command down}}
                            delay 0.75
                            
                            -- Clear any existing text and type song name
                            keystroke "a" using {{command down}}
                            delay 0.15
                            key code 51 -- Delete key
                            delay 0.15
                            keystroke "{song_name}"
                            delay 1
                            
                            -- Press Shift+Enter directly to search and play first result
                            key code 36 using {{shift down}} -- Shift+Enter to search and play
                            delay 0.5
                            
                            -- Press Escape to close search interface
                            key code 53 -- Escape key
                            delay 0.2
                        end tell
                        
                        -- Restore previous frontmost app
                        delay 0.1
                        try
                            set frontmost of process frontApp to true
                        end try
                    end tell
                    
                    -- Verify it's playing
                    delay 0.5
                    tell application "Spotify"
                        try
                            set currentTrack to name of current track
                            set currentArtist to artist of current track
                            return "Playing " & currentTrack & " by " & currentArtist
                        on error
                            return "Playing via search interface"
                        end try
                    end tell
                on error fallbackErr
                    return "Error: Search failed. " & fallbackErr
                end try
            else
                return "Error: " & errMsg & " (Error number: " & errNum & ")"
            end if
        end try
    end tell
    '''
    
    # Run the search and play script
    result = subprocess.run(
        ['osascript', '-e', search_script],
        capture_output=True,
        text=True
    )
    
    output = result.stdout.strip()
    error = result.stderr.strip()
    
    print(f"\n📊 Command Output:")
    print(f"   Return code: {result.returncode}")
    print(f"   Output: {output}")
    if error:
        print(f"   Error: {error}")
    
    if "Playing" in output:
        print(f"\n✅ SUCCESS: {output}")
        return True
    elif "Could not find" in output:
        print(f"\n❌ SONG NOT FOUND: {output}")
        return False
    elif "Error:" in output:
        print(f"\n❌ ERROR: {output}")
        return False
    else:
        print(f"\n⚠️  UNEXPECTED RESPONSE: {output}")
        return result.returncode == 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_spotify.py \"song name\"")
        print("Example: python test_spotify.py \"starboy\"")
        print("Example: python test_spotify.py \"bohemian rhapsody\"")
        sys.exit(1)
    
    song_name = " ".join(sys.argv[1:])
    print(f"🎵 Testing Spotify play command")
    print(f"   Song: {song_name}\n")
    
    success = play_spotify_song(song_name)
    sys.exit(0 if success else 1)

