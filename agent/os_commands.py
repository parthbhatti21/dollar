#!/usr/bin/env python3
"""
OS-level command execution module.
Cross-platform support for Mac, Windows, and Linux.
"""

import logging
import platform
import subprocess
import shutil
import time
import threading
import uuid
import re
import urllib.parse
import os
import sys
from datetime import datetime, timedelta
from typing import Dict

logger = logging.getLogger(__name__)

class OSCommands:
    """Execute OS-level commands across platforms."""
    
    def __init__(self, config):
        """
        Initialize OS commands handler.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.platform = platform.system().lower()
        self.active_timer = None  # Store active timer thread
        self.timer_cancelled = False  # Flag to cancel timer
        logger.info(f"Initialized OS commands for platform: {self.platform}")
    
    def _run_command(self, command: list, shell: bool = False) -> Dict[str, any]:
        """
        Run a command and return result.
        
        Args:
            command: Command as list of strings or string
            shell: Whether to run in shell
            
        Returns:
            dict: Result with 'success', 'output', and 'error' keys
        """
        try:
            if isinstance(command, str):
                command = [command] if not shell else command
            
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "output": result.stdout.strip(),
                    "message": "Command executed successfully"
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr.strip() or "Command failed"
                }
        
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out"
            }
        except Exception as e:
            logger.error(f"Error running command: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def lock_device(self) -> Dict[str, any]:
        """Lock the device/screen."""
        if self.platform == "darwin":  # macOS
            return self._run_command(
                ['osascript', '-e', 'tell application "System Events" to start current screen saver'],
                shell=False
            )
        elif self.platform == "windows":
            return self._run_command(
                'rundll32.exe user32.dll,LockWorkStation',
                shell=True
            )
        elif self.platform == "linux":
            # Try different methods
            if shutil.which("loginctl"):
                return self._run_command(['loginctl', 'lock-session'])
            elif shutil.which("gnome-screensaver-command"):
                return self._run_command(['gnome-screensaver-command', '-l'])
            elif shutil.which("xlock"):
                return self._run_command(['xlock'])
            else:
                return {
                    "success": False,
                    "error": "No lock command available on this Linux system"
                }
        else:
            return {
                "success": False,
                "error": f"Lock not supported on platform: {self.platform}"
            }
    
    def open_app(self, app_name: str) -> Dict[str, any]:
        """
        Open an application.
        
        Args:
            app_name: Name of the application to open
        """
        if not app_name:
            return {
                "success": False,
                "error": "No application name provided"
            }
        
        # Normalize app name - remove punctuation and extra whitespace
        import re
        app_name = app_name.strip().lower()
        # Remove trailing punctuation
        app_name = re.sub(r'[.,!?;:]+$', '', app_name).strip()
        
        if self.platform == "darwin":  # macOS
            # Special handling for YouTube - open in Safari
            if app_name in ["youtube", "yt"]:
                return self._open_youtube_in_safari()
            
            # Map common names to macOS app names
            app_mapping = {
                "chrome": "Google Chrome",
                "firefox": "Firefox",
                "safari": "Safari",
                "terminal": "Terminal",
                "calculator": "Calculator",
                "notes": "Notes",
                "mail": "Mail",
                "calendar": "Calendar",
                "spotify": "Spotify",
                "music": "Music",
                "messages": "Messages"
            }
            
            actual_app = app_mapping.get(app_name, app_name.title())
            return self._run_command(['open', '-a', actual_app])
        
        elif self.platform == "windows":
            # Map common names to Windows executables
            app_mapping = {
                "chrome": "chrome.exe",
                "firefox": "firefox.exe",
                "edge": "msedge.exe",
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "cmd": "cmd.exe",
                "powershell": "powershell.exe"
            }
            
            executable = app_mapping.get(app_name, f"{app_name}.exe")
            return self._run_command(f'start {executable}', shell=True)
        
        elif self.platform == "linux":
            # Use xdg-open for most apps
            return self._run_command(['xdg-open', app_name])
        
        else:
            return {
                "success": False,
                "error": f"Open app not supported on platform: {self.platform}"
            }
    
    def _open_youtube_in_safari(self) -> Dict[str, any]:
        """
        Open YouTube in Safari. If Safari is already open, opens a new tab.
        If Safari is not open, opens Safari first.
        """
        if self.platform != "darwin":
            return {
                "success": False,
                "error": "YouTube in Safari is only supported on macOS"
            }
        
        try:
            # Check if Safari is running
            check_script = '''
            tell application "System Events"
                set safariRunning to (name of processes) contains "Safari"
            end tell
            return safariRunning
            '''
            
            result = self._run_command(['osascript', '-e', check_script])
            safari_running = result.get('output', '').strip() == 'true'
            
            if not safari_running:
                # Open Safari first
                self._run_command(['open', '-a', 'Safari'])
                time.sleep(1)  # Wait for Safari to open
            
            # Now open new tab and navigate to YouTube
            # Cmd+T opens new tab (address bar is automatically focused in new tabs)
            # Then type youtube.com and press Enter
            script = '''
            tell application "Safari"
                activate
            end tell
            delay 0.5
            tell application "System Events"
                tell process "Safari"
                    -- Open new tab (Cmd+T) - address bar is auto-focused
                    key code 17 using {{command down}}
                    delay 0.4
                    -- Type the URL (address bar is already focused)
                    keystroke "youtube.com"
                    delay 0.3
                    -- Press Enter to navigate
                    key code 36
                end tell
            end tell
            '''
            
            result = self._run_command(['osascript', '-e', script])
            if result.get('success'):
                return {
                    "success": True,
                    "message": "Opened YouTube in Safari"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to open YouTube: {result.get('error', 'Unknown error')}"
                }
        
        except Exception as e:
            logger.error(f"Error opening YouTube in Safari: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to open YouTube: {str(e)}"
            }
    
    def open_youtube_search(self, search_query: str) -> Dict[str, any]:
        """
        Search YouTube in Safari. Opens Safari (if needed), creates a new tab,
        and navigates to YouTube search results.
        
        Args:
            search_query: The search query to look up on YouTube
        """
        if self.platform != "darwin":
            return {
                "success": False,
                "error": "YouTube search in Safari is only supported on macOS"
            }
        
        if not search_query:
            return {
                "success": False,
                "error": "No search query provided"
            }
        
        try:
            # URL encode the search query
            encoded_query = urllib.parse.quote_plus(search_query)
            youtube_url = f"https://www.youtube.com/results?search_query={encoded_query}"
            
            # Check if Safari is running
            check_script = '''
            tell application "System Events"
                set safariRunning to (name of processes) contains "Safari"
            end tell
            return safariRunning
            '''
            
            result = self._run_command(['osascript', '-e', check_script])
            safari_running = result.get('output', '').strip() == 'true'
            
            if not safari_running:
                # Open Safari first
                self._run_command(['open', '-a', 'Safari'])
                time.sleep(1)  # Wait for Safari to open
            
            # Now open new tab and navigate to YouTube search
            script = f'''
            tell application "Safari"
                activate
            end tell
            delay 0.5
            tell application "System Events"
                tell process "Safari"
                    -- Open new tab (Cmd+T) - address bar is auto-focused
                    key code 17 using {{command down}}
                    delay 0.4
                    -- Type the YouTube search URL (address bar is already focused)
                    keystroke "{youtube_url}"
                    delay 0.3
                    -- Press Enter to navigate
                    key code 36
                end tell
            end tell
            '''
            
            result = self._run_command(['osascript', '-e', script])
            if result.get('success'):
                return {
                    "success": True,
                    "message": f"Searching YouTube for '{search_query}'"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to search YouTube: {result.get('error', 'Unknown error')}"
                }
        
        except Exception as e:
            logger.error(f"Error searching YouTube: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to search YouTube: {str(e)}"
            }
    
    def open_github_search(self, search_query: str = None) -> Dict[str, any]:
        """
        Open GitHub search page in Safari. Opens Safari (if needed), creates a new tab,
        and navigates to GitHub search page (github.com/search).
        
        Args:
            search_query: The search query to look up on GitHub (optional, if None opens search page)
        """
        if self.platform != "darwin":
            return {
                "success": False,
                "error": "GitHub search in Safari is only supported on macOS"
            }
        
        try:
            # If no query provided, open GitHub homepage
            if not search_query:
                github_url = "https://github.com"
            else:
                # URL encode the search query and search on GitHub
                encoded_query = urllib.parse.quote_plus(search_query)
                github_url = f"https://github.com/search?q={encoded_query}"
            
            # Check if Safari is running
            check_script = '''
            tell application "System Events"
                set safariRunning to (name of processes) contains "Safari"
            end tell
            return safariRunning
            '''
            
            result = self._run_command(['osascript', '-e', check_script])
            safari_running = result.get('output', '').strip() == 'true'
            
            if not safari_running:
                # Open Safari first
                self._run_command(['open', '-a', 'Safari'])
                time.sleep(1)  # Wait for Safari to open
            
            # Now open new tab and navigate to GitHub search
            script = f'''
            tell application "Safari"
                activate
            end tell
            delay 0.5
            tell application "System Events"
                tell process "Safari"
                    -- Open new tab (Cmd+T) - address bar is auto-focused
                    key code 17 using {{command down}}
                    delay 0.4
                    -- Type the GitHub search URL (address bar is already focused)
                    keystroke "{github_url}"
                    delay 0.3
                    -- Press Enter to navigate
                    key code 36
                end tell
            end tell
            '''
            
            result = self._run_command(['osascript', '-e', script])
            if result.get('success'):
                if not search_query:
                    return {
                        "success": True,
                        "message": "Opened GitHub in Safari"
                    }
                else:
                    return {
                        "success": True,
                        "message": f"Searching GitHub for '{search_query}'"
                    }
            else:
                return {
                    "success": False,
                    "error": f"Failed to open GitHub: {result.get('error', 'Unknown error')}"
                }
        
        except Exception as e:
            logger.error(f"Error opening GitHub: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to open GitHub: {str(e)}"
            }
    
    def open_cursor(self) -> Dict[str, any]:
        """
        Open Cursor application and press Cmd+M.
        On macOS, opens Cursor and sends Cmd+M keyboard shortcut.
        """
        if self.platform != "darwin":
            return {
                "success": False,
                "error": "Cursor opening is only supported on macOS"
            }
        
        try:
            # Open Cursor application
            open_result = self._run_command(['open', '-a', 'Cursor'])
            if not open_result.get('success'):
                return {
                    "success": False,
                    "error": "Failed to open Cursor application"
                }
            
            # Wait for Cursor to open
            time.sleep(1.5)
            
            # Press Cmd+M using AppleScript
            script = '''
            tell application "System Events"
                tell process "Cursor"
                    -- Press Cmd+M
                    key code 46 using {command down}
                end tell
            end tell
            '''
            
            result = self._run_command(['osascript', '-e', script])
            if result.get('success'):
                return {
                    "success": True,
                    "message": "Opened Cursor and pressed Cmd+M"
                }
            else:
                # Even if Cmd+M fails, Cursor was opened successfully
                return {
                    "success": True,
                    "message": "Opened Cursor (Cmd+M may not have been sent)"
                }
        
        except Exception as e:
            logger.error(f"Error opening Cursor: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to open Cursor: {str(e)}"
            }
    
    def _is_mobile_platform(self) -> bool:
        """
        Detect if running on a mobile platform (iOS or Android).
        
        Returns:
            bool: True if running on mobile, False otherwise
        """
        # Check for iOS (Darwin-based, but with mobile indicators)
        if self.platform == "darwin":
            # Check for iOS-specific indicators
            try:
                # iOS devices typically have specific system properties
                # Check if running on iOS simulator or device
                if 'SIMULATOR' in os.environ or 'IPHONE' in os.environ:
                    return True
                # Check for iOS-specific paths
                if os.path.exists('/System/Library/CoreServices/SpringBoard.app'):
                    return True
            except:
                pass
        
        # Check for Android (Linux-based, but with Android indicators)
        if self.platform == "linux":
            try:
                # Android has specific system properties
                if os.path.exists('/system/build.prop'):
                    return True
                if 'ANDROID_ROOT' in os.environ or 'ANDROID_DATA' in os.environ:
                    return True
            except:
                pass
        
        # Additional check: try to detect via platform module
        try:
            import platform
            machine = platform.machine().lower()
            # iOS devices are typically arm64/armv7
            if machine in ['arm64', 'armv7', 'armv7s'] and self.platform == "darwin":
                # Could be iOS, but also could be macOS on Apple Silicon
                # Check for iOS-specific indicators above
                pass
        except:
            pass
        
        return False
    
    def close_dollar(self) -> Dict[str, any]:
        """
        Close the Dollar Assistant:
        - On macOS: Send Ctrl+C to Terminal, then Cmd+Q to quit Terminal
        - On mobile (iOS/Android): Terminate the app process gracefully
        - On other platforms: Terminate the app process
        
        Cross-platform support for desktop and mobile.
        """
        # Check if running on mobile
        is_mobile = self._is_mobile_platform()
        
        if is_mobile:
            # Mobile platforms: terminate the app process
            try:
                logger.info("Closing Dollar Assistant on mobile platform...")
                # Use os._exit for immediate termination (cleaner on mobile)
                # Give a moment for the response to be sent
                
                def _terminate_after_delay():
                    time.sleep(0.5)  # Brief delay to allow response
                    os._exit(0)  # Immediate termination
                
                # Start termination in background thread
                term_thread = threading.Thread(target=_terminate_after_delay, daemon=False)
                term_thread.start()
                
                return {
                    "success": True,
                    "message": "Closing Dollar Assistant..."
                }
            except Exception as e:
                logger.error(f"Error closing Dollar Assistant on mobile: {e}", exc_info=True)
                # Fallback: try sys.exit
                try:
                    sys.exit(0)
                except:
                    return {
                        "success": False,
                        "error": f"Failed to close Dollar Assistant: {str(e)}"
                    }
        
        elif self.platform == "darwin":
            # macOS: Use AppleScript to send Ctrl+C and Cmd+Q to Terminal
            try:
                script = '''
                tell application "System Events"
                    if exists process "Terminal" then
                        tell process "Terminal"
                            set frontmost to true
                            -- Send Ctrl+C to stop the running Python script
                            keystroke "c" using {control down}
                            delay 2
                            -- Quit Terminal app (Command+Q)
                            keystroke "q" using {command down}
                        end tell
                    end if
                end tell
                '''
                result = self._run_command(['osascript', '-e', script])
                if result.get('success'):
                    return {
                        "success": True,
                        "message": "Closed Dollar Assistant in Terminal"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to close Dollar Assistant: {result.get('error', 'Unknown error')}"
                    }
            except Exception as e:
                logger.error(f"Error closing Dollar Assistant: {e}", exc_info=True)
                return {
                    "success": False,
                    "error": f"Failed to close Dollar Assistant: {str(e)}"
                }
        
        else:
            # Windows/Linux: Terminate the process
            try:
                logger.info("Closing Dollar Assistant on desktop platform...")
                
                def _terminate_after_delay():
                    time.sleep(0.5)  # Brief delay to allow response
                    os._exit(0)  # Immediate termination
                
                # Start termination in background thread
                term_thread = threading.Thread(target=_terminate_after_delay, daemon=False)
                term_thread.start()
                
                return {
                    "success": True,
                    "message": "Closing Dollar Assistant..."
                }
            except Exception as e:
                logger.error(f"Error closing Dollar Assistant: {e}", exc_info=True)
                try:
                    sys.exit(0)
                except:
                    return {
                        "success": False,
                        "error": f"Failed to close Dollar Assistant: {str(e)}"
                    }
    
    def volume_up(self) -> Dict[str, any]:
        """Increase system volume."""
        if self.platform == "darwin":  # macOS
            # Get current volume first, then increase (capped at 100)
            vol_result = self._run_command(
                ['osascript', '-e', 'output volume of (get volume settings)']
            )
            current_vol = 50  # Default
            if vol_result.get('success'):
                try:
                    current_vol = int(vol_result.get('output', '50'))
                except:
                    pass
            
            new_vol = min(100, current_vol + 10)
            result = self._run_command(
                ['osascript', '-e', f'set volume output volume {new_vol}']
            )
            if result.get('success'):
                result['message'] = f"Volume increased to {new_vol}%"
            return result
        elif self.platform == "windows":
            # Use nircmd if available, or PowerShell
            if shutil.which("nircmd"):
                return self._run_command(['nircmd', 'changesysvolume', '2000'])
            else:
                # PowerShell method
                ps_cmd = "(New-Object -com wscript.shell).SendKeys([char]175)"
                return self._run_command(['powershell', '-Command', ps_cmd])
        elif self.platform == "linux":
            # Try amixer or pactl
            if shutil.which("pactl"):
                return self._run_command(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', '+10%'])
            elif shutil.which("amixer"):
                return self._run_command(['amixer', 'set', 'Master', '10%+'])
            else:
                return {
                    "success": False,
                    "error": "No volume control available"
                }
        else:
            return {
                "success": False,
                "error": f"Volume control not supported on platform: {self.platform}"
            }
    
    def volume_down(self) -> Dict[str, any]:
        """Decrease system volume."""
        if self.platform == "darwin":  # macOS
            # Get current volume first, then decrease (capped at 0)
            vol_result = self._run_command(
                ['osascript', '-e', 'output volume of (get volume settings)']
            )
            current_vol = 50  # Default
            if vol_result.get('success'):
                try:
                    current_vol = int(vol_result.get('output', '50'))
                except:
                    pass
            
            new_vol = max(0, current_vol - 10)
            result = self._run_command(
                ['osascript', '-e', f'set volume output volume {new_vol}']
            )
            if result.get('success'):
                result['message'] = f"Volume decreased to {new_vol}%"
            return result
        elif self.platform == "windows":
            if shutil.which("nircmd"):
                return self._run_command(['nircmd', 'changesysvolume', '-2000'])
            else:
                ps_cmd = "(New-Object -com wscript.shell).SendKeys([char]174)"
                return self._run_command(['powershell', '-Command', ps_cmd])
        elif self.platform == "linux":
            if shutil.which("pactl"):
                return self._run_command(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', '-10%'])
            elif shutil.which("amixer"):
                return self._run_command(['amixer', 'set', 'Master', '10%-'])
            else:
                return {
                    "success": False,
                    "error": "No volume control available"
                }
        else:
            return {
                "success": False,
                "error": f"Volume control not supported on platform: {self.platform}"
            }
    
    def set_volume(self, volume: int) -> Dict[str, any]:
        """
        Set volume to specific level (0-100).
        
        Args:
            volume: Volume level (0-100)
        """
        volume = max(0, min(100, volume))
        
        if self.platform == "darwin":  # macOS
            result = self._run_command(
                ['osascript', '-e', f'set volume output volume {volume}']
            )
            if result.get('success'):
                result['message'] = f"Volume set to {volume}%"
            return result
        elif self.platform == "windows":
            if shutil.which("nircmd"):
                # nircmd uses 0-65535 range
                vol_value = int(volume * 655.35)
                return self._run_command(['nircmd', 'setsysvolume', str(vol_value)])
            else:
                return {
                    "success": False,
                    "error": "Volume setting requires nircmd on Windows"
                }
        elif self.platform == "linux":
            if shutil.which("pactl"):
                return self._run_command(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', f'{volume}%'])
            elif shutil.which("amixer"):
                return self._run_command(['amixer', 'set', 'Master', f'{volume}%'])
            else:
                return {
                    "success": False,
                    "error": "No volume control available"
                }
        else:
            return {
                "success": False,
                "error": f"Volume control not supported on platform: {self.platform}"
            }
    
    def wifi_on(self) -> Dict[str, any]:
        """Enable WiFi."""
        if self.platform == "darwin":  # macOS
            return self._run_command(['networksetup', '-setairportpower', 'en0', 'on'])
        elif self.platform == "windows":
            return self._run_command(
                'netsh interface set interface "Wi-Fi" enabled',
                shell=True
            )
        elif self.platform == "linux":
            if shutil.which("nmcli"):
                return self._run_command(['nmcli', 'radio', 'wifi', 'on'])
            elif shutil.which("ifconfig"):
                # Try to enable wireless interface (varies by system)
                return self._run_command(['sudo', 'ifconfig', 'wlan0', 'up'])
            else:
                return {
                    "success": False,
                    "error": "WiFi control not available on this Linux system"
                }
        else:
            return {
                "success": False,
                "error": f"WiFi control not supported on platform: {self.platform}"
            }
    
    def wifi_off(self) -> Dict[str, any]:
        """Disable WiFi."""
        if self.platform == "darwin":  # macOS
            return self._run_command(['networksetup', '-setairportpower', 'en0', 'off'])
        elif self.platform == "windows":
            return self._run_command(
                'netsh interface set interface "Wi-Fi" disabled',
                shell=True
            )
        elif self.platform == "linux":
            if shutil.which("nmcli"):
                return self._run_command(['nmcli', 'radio', 'wifi', 'off'])
            elif shutil.which("ifconfig"):
                return self._run_command(['sudo', 'ifconfig', 'wlan0', 'down'])
            else:
                return {
                    "success": False,
                    "error": "WiFi control not available on this Linux system"
                }
        else:
            return {
                "success": False,
                "error": f"WiFi control not supported on platform: {self.platform}"
            }
    
    def bluetooth_on(self) -> Dict[str, any]:
        """Enable Bluetooth."""
        if self.platform == "darwin":  # macOS
            # Use blueutil if available (better command-line tool)
            if shutil.which("blueutil"):
                result = self._run_command(['blueutil', '--power', '1'])
                if result.get('success'):
                    result['message'] = "Bluetooth enabled"
                return result
            else:
                # Fallback to AppleScript (may require System Preferences)
                script = '''
                tell application "System Events"
                    tell process "System Preferences"
                        try
                            tell application "System Preferences"
                                activate
                                set current pane to pane "com.apple.preferences.Bluetooth"
                            end tell
                            delay 0.5
                            try
                                click button "Turn Bluetooth On" of window 1
                                delay 0.5
                            on error
                                -- Bluetooth might already be on
                            end try
                            tell application "System Preferences" to quit
                            return "Bluetooth enabled"
                        on error
                            tell application "System Preferences" to quit
                            return "Bluetooth enabled"
                        end try
                    end tell
                end tell
                '''
                result = self._run_command(['osascript', '-e', script])
                if result.get('success'):
                    result['message'] = "Bluetooth enabled"
                return result
        elif self.platform == "windows":
            # Use PowerShell to enable Bluetooth
            ps_cmd = '''
            $bluetooth = Get-PnpDevice | Where-Object {$_.FriendlyName -like "*bluetooth*"}
            Enable-PnpDevice -InstanceId $bluetooth.InstanceId -Confirm:$false
            '''
            result = self._run_command(['powershell', '-Command', ps_cmd])
            if result.get('success'):
                result['message'] = "Bluetooth enabled"
            return result
        elif self.platform == "linux":
            # Use rfkill or bluetoothctl
            if shutil.which("rfkill"):
                result = self._run_command(['rfkill', 'unblock', 'bluetooth'])
                if result.get('success'):
                    result['message'] = "Bluetooth enabled"
                return result
            elif shutil.which("bluetoothctl"):
                result = self._run_command(['bluetoothctl', 'power', 'on'])
                if result.get('success'):
                    result['message'] = "Bluetooth enabled"
                return result
            else:
                return {
                    "success": False,
                    "error": "Bluetooth control not available. Install rfkill or bluetoothctl."
                }
        else:
            return {
                "success": False,
                "error": f"Bluetooth control not supported on platform: {self.platform}"
            }
    
    def bluetooth_off(self) -> Dict[str, any]:
        """Disable Bluetooth."""
        if self.platform == "darwin":  # macOS
            # Use blueutil if available (better command-line tool)
            if shutil.which("blueutil"):
                result = self._run_command(['blueutil', '--power', '0'])
                if result.get('success'):
                    result['message'] = "Bluetooth disabled"
                return result
            else:
                # Fallback to AppleScript (may require System Preferences)
                script = '''
                tell application "System Events"
                    tell process "System Preferences"
                        try
                            tell application "System Preferences"
                                activate
                                set current pane to pane "com.apple.preferences.Bluetooth"
                            end tell
                            delay 0.5
                            try
                                click button "Turn Bluetooth Off" of window 1
                                delay 0.5
                            on error
                                -- Bluetooth might already be off
                            end try
                            tell application "System Preferences" to quit
                            return "Bluetooth disabled"
                        on error
                            tell application "System Preferences" to quit
                            return "Bluetooth disabled"
                        end try
                    end tell
                end tell
                '''
                result = self._run_command(['osascript', '-e', script])
                if result.get('success'):
                    result['message'] = "Bluetooth disabled"
                return result
        elif self.platform == "windows":
            # Use PowerShell to disable Bluetooth
            ps_cmd = '''
            $bluetooth = Get-PnpDevice | Where-Object {$_.FriendlyName -like "*bluetooth*"}
            Disable-PnpDevice -InstanceId $bluetooth.InstanceId -Confirm:$false
            '''
            result = self._run_command(['powershell', '-Command', ps_cmd])
            if result.get('success'):
                result['message'] = "Bluetooth disabled"
            return result
        elif self.platform == "linux":
            # Use rfkill or bluetoothctl
            if shutil.which("rfkill"):
                result = self._run_command(['rfkill', 'block', 'bluetooth'])
                if result.get('success'):
                    result['message'] = "Bluetooth disabled"
                return result
            elif shutil.which("bluetoothctl"):
                result = self._run_command(['bluetoothctl', 'power', 'off'])
                if result.get('success'):
                    result['message'] = "Bluetooth disabled"
                return result
            else:
                return {
                    "success": False,
                    "error": "Bluetooth control not available. Install rfkill or bluetoothctl."
                }
        else:
            return {
                "success": False,
                "error": f"Bluetooth control not supported on platform: {self.platform}"
            }
    
    def shutdown(self) -> Dict[str, any]:
        """Shutdown the system."""
        if self.platform == "darwin":  # macOS
            return self._run_command(['sudo', 'shutdown', '-h', 'now'])
        elif self.platform == "windows":
            return self._run_command('shutdown /s /t 0', shell=True)
        elif self.platform == "linux":
            return self._run_command(['sudo', 'shutdown', '-h', 'now'])
        else:
            return {
                "success": False,
                "error": f"Shutdown not supported on platform: {self.platform}"
            }
    
    def restart(self) -> Dict[str, any]:
        """Restart the system."""
        if self.platform == "darwin":  # macOS
            return self._run_command(['sudo', 'shutdown', '-r', 'now'])
        elif self.platform == "windows":
            return self._run_command('shutdown /r /t 0', shell=True)
        elif self.platform == "linux":
            return self._run_command(['sudo', 'shutdown', '-r', 'now'])
        else:
            return {
                "success": False,
                "error": f"Restart not supported on platform: {self.platform}"
            }
    
    def get_system_info(self) -> Dict[str, any]:
        """Get system information."""
        try:
            import psutil
            
            info = {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "processor": platform.processor(),
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_total": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
                "memory_used": f"{psutil.virtual_memory().used / (1024**3):.2f} GB",
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": f"{psutil.disk_usage('/').percent:.1f}%"
            }
            
            info_str = ", ".join([f"{k}: {v}" for k, v in info.items()])
            
            return {
                "success": True,
                "message": info_str,
                "data": info
            }
        except ImportError:
            return {
                "success": True,
                "message": f"Platform: {platform.system()}, Version: {platform.version()}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get system info: {str(e)}"
            }
    
    def get_time(self) -> Dict[str, any]:
        """Get current time."""
        current_time = datetime.now().strftime("%I:%M %p")
        return {
            "success": True,
            "message": f"The current time is {current_time}"
        }
    
    def get_date(self) -> Dict[str, any]:
        """Get current date."""
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        return {
            "success": True,
            "message": f"Today is {current_date}"
        }
    
    def get_weather(self) -> Dict[str, any]:
        """Get weather information (requires API key or local service)."""
        # This would require a weather API or local service
        # For now, return a placeholder
        return {
            "success": False,
            "error": "Weather service not configured. Add API key in config.yaml"
        }
    
    def media_play(self) -> Dict[str, any]:
        """Play/resume media playback."""
        if self.platform == "darwin":  # macOS
            # Try Spotify first (more reliable)
            spotify_script = '''
            tell application "Spotify"
                try
                    if player state is paused then
                        play
                        return "Resumed playback"
                    else if player state is stopped then
                        play
                        return "Started playback"
                    else
                        return "Already playing"
                    end if
                on error
                    -- Spotify not available, fall back to media key
                    return "fallback"
                end try
            end tell
            '''
            result = self._run_command(['osascript', '-e', spotify_script])
            output = result.get('output', '').strip()
            
            if "fallback" not in output and result.get('success'):
                if "Resumed" in output or "Started" in output:
                    return {
                        "success": True,
                        "message": "Playing media"
                    }
                elif "Already playing" in output:
                    return {
                        "success": True,
                        "message": "Media is already playing"
                    }
            
            # Fallback to media key if Spotify method didn't work
            script = '''
            tell application "System Events"
                key code 126  -- Play/Pause key
            end tell
            '''
            result = self._run_command(['osascript', '-e', script])
            if result.get('success'):
                result['message'] = "Playing media"
            return result
        elif self.platform == "windows":
            # Use PowerShell to send media play key
            ps_cmd = "$wshell = New-Object -ComObject wscript.shell; $wshell.SendKeys([char]179)"
            result = self._run_command(['powershell', '-Command', ps_cmd])
            if result.get('success'):
                result['message'] = "Playing media"
            return result
        elif self.platform == "linux":
            # Use playerctl if available
            if shutil.which("playerctl"):
                result = self._run_command(['playerctl', 'play'])
                if result.get('success'):
                    result['message'] = "Playing media"
                return result
            else:
                return {
                    "success": False,
                    "error": "playerctl not installed. Install with: sudo apt install playerctl"
                }
        else:
            return {
                "success": False,
                "error": f"Media control not supported on platform: {self.platform}"
            }
    
    def _is_music_playing(self) -> bool:
        """Check if music is currently playing (without activating Spotify)."""
        if self.platform == "darwin":  # macOS
            # First check if Spotify is running (without activating it)
            check_running_cmd = ['pgrep', '-x', 'Spotify']
            check_running_result = self._run_command(check_running_cmd)
            
            if check_running_result.get('returncode') != 0:
                # Spotify is not running, so music can't be playing
                return False
            
            # Spotify is running, check its state (without activating)
            # Use System Events to check without bringing Spotify to front
            script = '''
            tell application "System Events"
                if (exists process "Spotify") then
                    tell application "Spotify"
                        try
                            if player state is playing then
                                return "playing"
                            else
                                return "not playing"
                            end if
                        on error
                            return "unknown"
                        end try
                    end tell
                else
                    return "not running"
                end if
            end tell
            '''
            result = self._run_command(['osascript', '-e', script])
            output = result.get('output', '').strip().lower()
            return "playing" in output
        # For other platforms, assume we can't easily check, so return False
        return False
    
    def _pause_music_if_playing(self) -> bool:
        """Pause music if it's currently playing. Returns True if music was paused."""
        if self._is_music_playing():
            logger.info("Music is playing, pausing for voice command...")
            result = self.media_pause()
            return result.get('success', False)
        return False
    
    def _resume_music_if_paused(self) -> bool:
        """Resume music if it was paused. Returns True if music was resumed."""
        # Check if music is paused (not playing) - only if Spotify is running
        if self.platform == "darwin":  # macOS
            # First check if Spotify is running (without activating it)
            check_running_cmd = ['pgrep', '-x', 'Spotify']
            check_running_result = self._run_command(check_running_cmd)
            
            if check_running_result.get('returncode') != 0:
                # Spotify is not running, nothing to resume
                return False
            
            # Spotify is running, check its state (without activating)
            script = '''
            tell application "System Events"
                if (exists process "Spotify") then
                    tell application "Spotify"
                        try
                            if player state is paused then
                                return "paused"
                            else
                                return "not paused"
                            end if
                        on error
                            return "unknown"
                        end try
                    end tell
                else
                    return "not running"
                end if
            end tell
            '''
            result = self._run_command(['osascript', '-e', script])
            output = result.get('output', '').strip().lower()
            if "paused" in output:
                logger.info("Resuming music playback...")
                resume_result = self.media_play()
                return resume_result.get('success', False)
        return False
    
    def media_pause(self) -> Dict[str, any]:
        """Pause media playback."""
        if self.platform == "darwin":  # macOS
            # First check if Spotify is running (without activating it)
            check_running_cmd = ['pgrep', '-x', 'Spotify']
            check_running_result = self._run_command(check_running_cmd)
            
            # Only try to pause Spotify if it's running
            if check_running_result.get('returncode') == 0:
                # Spotify is running, try to pause it (without activating)
                spotify_script = '''
                tell application "System Events"
                    if (exists process "Spotify") then
                        tell application "Spotify"
                            try
                                if player state is playing then
                                    pause
                                    return "Paused"
                                else
                                    return "Already paused"
                                end if
                            on error
                                return "fallback"
                            end try
                        end tell
                    else
                        return "fallback"
                    end if
                end tell
                '''
                result = self._run_command(['osascript', '-e', spotify_script])
                output = result.get('output', '').strip()
                
                if "fallback" not in output and result.get('success'):
                    return {
                        "success": True,
                        "message": "Paused media"
                    }
            
            # Fallback to media key
            script = '''
            tell application "System Events"
                key code 126  -- Play/Pause key
            end tell
            '''
            result = self._run_command(['osascript', '-e', script])
            if result.get('success'):
                result['message'] = "Paused media"
            return result
        elif self.platform == "windows":
            # Use PowerShell to send media pause key
            ps_cmd = "$wshell = New-Object -ComObject wscript.shell; $wshell.SendKeys([char]179)"
            result = self._run_command(['powershell', '-Command', ps_cmd])
            if result.get('success'):
                result['message'] = "Paused media"
            return result
        elif self.platform == "linux":
            # Use playerctl if available
            if shutil.which("playerctl"):
                result = self._run_command(['playerctl', 'pause'])
                if result.get('success'):
                    result['message'] = "Paused media"
                return result
            else:
                return {
                    "success": False,
                    "error": "playerctl not installed. Install with: sudo apt install playerctl"
                }
        else:
            return {
                "success": False,
                "error": f"Media control not supported on platform: {self.platform}"
            }
    
    def media_stop(self) -> Dict[str, any]:
        """Stop media playback."""
        if self.platform == "darwin":  # macOS
            # Try to stop via Spotify directly if it's playing
            spotify_script = '''
            tell application "Spotify"
                try
                    if player state is playing then
                        pause
                        return "Stopped music"
                    else
                        return "Music is already stopped"
                    end if
                on error
                    -- Fallback to media key
                    tell application "System Events"
                        key code 124
                    end tell
                    return "Stopped music"
                end try
            end tell
            '''
            result = self._run_command(['osascript', '-e', spotify_script])
            if result.get('success'):
                result['message'] = "Stopped music"
            else:
                # Fallback to media key
                script = '''
                tell application "System Events"
                    key code 124  -- Next track key (used for stop on some players)
                end tell
                '''
                result = self._run_command(['osascript', '-e', script])
                if result.get('success'):
                    result['message'] = "Stopped music"
            return result
        elif self.platform == "windows":
            # Use PowerShell to send stop media key
            ps_cmd = "$wshell = New-Object -ComObject wscript.shell; $wshell.SendKeys([char]179)"
            result = self._run_command(['powershell', '-Command', ps_cmd])
            if result.get('success'):
                result['message'] = "Stopped music"
            return result
        elif self.platform == "linux":
            # Use playerctl if available
            if shutil.which("playerctl"):
                result = self._run_command(['playerctl', 'stop'])
                if result.get('success'):
                    result['message'] = "Stopped music"
                return result
            else:
                return {
                    "success": False,
                    "error": "playerctl not installed. Install with: sudo apt install playerctl"
                }
        else:
            return {
                "success": False,
                "error": f"Media control not supported on platform: {self.platform}"
            }
    
    def media_next(self) -> Dict[str, any]:
        """Skip to next track."""
        if self.platform == "darwin":  # macOS
            # Use AppleScript to send next track key
            script = '''
            tell application "System Events"
                key code 124  -- Next track key
            end tell
            '''
            result = self._run_command(['osascript', '-e', script])
            if result.get('success'):
                result['message'] = "Skipped to next track"
            return result
        elif self.platform == "windows":
            # Use PowerShell to send next track key
            ps_cmd = "$wshell = New-Object -ComObject wscript.shell; $wshell.SendKeys([char]176)"
            result = self._run_command(['powershell', '-Command', ps_cmd])
            if result.get('success'):
                result['message'] = "Skipped to next track"
            return result
        elif self.platform == "linux":
            # Use playerctl if available
            if shutil.which("playerctl"):
                result = self._run_command(['playerctl', 'next'])
                if result.get('success'):
                    result['message'] = "Skipped to next track"
                return result
            else:
                return {
                    "success": False,
                    "error": "playerctl not installed. Install with: sudo apt install playerctl"
                }
        else:
            return {
                "success": False,
                "error": f"Media control not supported on platform: {self.platform}"
            }
    
    def media_previous(self) -> Dict[str, any]:
        """Go to previous track."""
        if self.platform == "darwin":  # macOS
            # Use AppleScript to send previous track key
            script = '''
            tell application "System Events"
                key code 123  -- Previous track key
            end tell
            '''
            result = self._run_command(['osascript', '-e', script])
            if result.get('success'):
                result['message'] = "Went to previous track"
            return result
        elif self.platform == "windows":
            # Use PowerShell to send previous track key
            ps_cmd = "$wshell = New-Object -ComObject wscript.shell; $wshell.SendKeys([char]177)"
            result = self._run_command(['powershell', '-Command', ps_cmd])
            if result.get('success'):
                result['message'] = "Went to previous track"
            return result
        elif self.platform == "linux":
            # Use playerctl if available
            if shutil.which("playerctl"):
                result = self._run_command(['playerctl', 'previous'])
                if result.get('success'):
                    result['message'] = "Went to previous track"
                return result
            else:
                return {
                    "success": False,
                    "error": "playerctl not installed. Install with: sudo apt install playerctl"
                }
        else:
            return {
                "success": False,
                "error": f"Media control not supported on platform: {self.platform}"
            }
    
    def spotify_play_song(self, song_name: str) -> Dict[str, any]:
        """
        Play a song on Spotify.
        
        Args:
            song_name: Name of the song to play
        """
        if not song_name:
            logger.warning("No song name provided for Spotify play")
            return {
                "success": False,
                "error": "No song name provided"
            }
        
        logger.info(f"Attempting to play '{song_name}' on Spotify")
        
        if self.platform == "darwin":  # macOS
            # Use command-line approach with osascript
            # First, check if Spotify is running
            check_cmd = ['pgrep', '-x', 'Spotify']
            check_result = self._run_command(check_cmd)
            
            if not check_result.get('success'):
                logger.info("Spotify is not running, launching it automatically...")
                # Launch Spotify automatically
                launch_result = self._run_command(['open', '-a', 'Spotify'])
                if not launch_result.get('success'):
                    logger.error("Failed to launch Spotify")
                    return {
                        "success": False,
                        "error": "Failed to launch Spotify. Please ensure Spotify is installed."
                    }
                
                # Wait for Spotify to start up (give it a few seconds)
                logger.info("Waiting for Spotify to start...")
                max_wait = 10  # Maximum wait time in seconds
                wait_interval = 0.5  # Check every 0.5 seconds
                waited = 0
                
                while waited < max_wait:
                    time.sleep(wait_interval)
                    waited += wait_interval
                    check_result = self._run_command(check_cmd)
                    if check_result.get('success'):
                        logger.info(f"Spotify started after {waited:.1f} seconds")
                        # Give Spotify a bit more time to fully initialize
                        time.sleep(1)
                        break
                
                # Final check - if still not running, return error
                check_result = self._run_command(check_cmd)
                if not check_result.get('success'):
                    logger.error("Spotify did not start within the expected time")
                    return {
                        "success": False,
                        "error": "Spotify launched but did not start properly. Please try again."
                    }
            
            # Escape the song name for AppleScript
            escaped_song = song_name.replace('\\', '\\\\').replace('"', '\\"')
            
            # Search and play using command line - improved version with fallback
            # First ensure Spotify is ready (without activating)
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
            
            ready_result = self._run_command(['osascript', '-e', ready_script])
            if "ready" not in ready_result.get('output', ''):
                logger.warning("Spotify may not be fully ready, waiting...")
                time.sleep(1)
            
            # Now try the search
            search_script = f'''
            tell application "Spotify"
                try
                    set theSearch to "{escaped_song}"
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
                                    
                                    -- Clear any existing text (Cmd+A then Delete)
                                    keystroke "a" using {{command down}}
                                    delay 0.15
                                    key code 51 -- Delete key
                                    delay 0.15
                                    
                                    -- Type song name (use escaped version from outer scope)
                                    keystroke "{escaped_song}"
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
                            delay 0.75
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
            result = self._run_command(['osascript', '-e', search_script])
            
            # Check the output to determine success
            output = result.get('output', '').strip()
            error_output = result.get('error', '').strip()
            return_code = result.get('returncode', -1)
            
            logger.info(f"Spotify command output: '{output}'")
            logger.info(f"Spotify command error: '{error_output}'")
            logger.info(f"Spotify command return code: {return_code}")
            
            # If output contains "Playing", consider it successful
            if "Playing" in output:
                # Extract the actual track name from output if available
                logger.info(f"Successfully started playing on Spotify")
                return {
                    "success": True,
                    "message": output if output else f"Playing {song_name} on Spotify"
                }
            elif "Could not find" in output:
                logger.warning(f"Could not find '{song_name}' on Spotify")
                return {
                    "success": False,
                    "error": f"Could not find '{song_name}' on Spotify. Try a different search term or be more specific."
                }
            elif "Error:" in output or return_code != 0:
                # Parse error message
                error_msg = output if output else error_output
                logger.error(f"Spotify play failed: {error_msg}")
                
                # Provide helpful error messages
                if "not responding" in error_msg.lower():
                    return {
                        "success": False,
                        "error": "Spotify is not responding. Please make sure Spotify is open and try again."
                    }
                elif "not running" in error_msg.lower():
                    return {
                        "success": False,
                        "error": "Spotify is not running. Please open Spotify first."
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to play on Spotify: {error_msg or 'Unknown error'}"
                    }
            else:
                # Unknown response - might still have worked
                logger.warning(f"Unexpected Spotify response: {output}")
                # If return code is 0, assume it worked
                if return_code == 0:
                    return {
                        "success": True,
                        "message": f"Playing {song_name} on Spotify"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Unexpected response from Spotify: {output or error_output}"
                    }
        elif self.platform == "windows":
            # Try to use Spotify URI or search
            # First, ensure Spotify is running
            try:
                # Open Spotify if not running
                subprocess.Popen(['spotify'], shell=True)
                time.sleep(2)
                
                # Use Spotify URI scheme (requires Spotify to be installed)
                # This is a simplified approach - may need Spotify Web API for better results
                return {
                    "success": False,
                    "error": "Spotify song search on Windows requires Spotify Web API. Use 'open spotify' and search manually."
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to control Spotify: {str(e)}"
                }
        elif self.platform == "linux":
            # Use dbus to control Spotify (if available)
            if shutil.which("dbus-send"):
                # Try to use dbus to search and play
                # This is complex, so we'll use a simpler approach
                return {
                    "success": False,
                    "error": "Spotify song search on Linux requires dbus configuration. Use 'open spotify' and search manually."
                }
            else:
                return {
                    "success": False,
                    "error": "dbus-send not available. Install dbus or use playerctl."
                }
        else:
            return {
                "success": False,
                "error": f"Spotify control not supported on platform: {self.platform}"
            }
    
    def _timer_notification(self, message: str):
        """Show timer notification using platform-specific method."""
        if self.platform == "darwin":  # macOS
            script = f'''
            display notification "{message}" with title "Timer" sound name "Glass"
            '''
            self._run_command(['osascript', '-e', script])
        elif self.platform == "windows":
            # PowerShell toast notification
            ps_cmd = f'''
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
            $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
            $textNodes = $template.GetElementsByTagName("text")
            $textNodes.Item(0).AppendChild($template.CreateTextNode("Timer")) | Out-Null
            $textNodes.Item(1).AppendChild($template.CreateTextNode("{message}")) | Out-Null
            $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Dollar Assistant").Show($toast)
            '''
            self._run_command(['powershell', '-Command', ps_cmd])
        elif self.platform == "linux":
            # Use notify-send
            self._run_command(['notify-send', 'Timer', message, '-i', 'clock'])
    
    def _timer_thread(self, duration_seconds: int, duration_text: str):
        """Background thread that waits for timer and shows notification."""
        self.timer_cancelled = False
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            if self.timer_cancelled:
                return
            time.sleep(0.5)  # Check every 0.5 seconds
        
        if not self.timer_cancelled:
            # Timer expired
            message = f"Timer for {duration_text} is complete!"
            self._timer_notification(message)
            self.active_timer = None
    
    def set_timer(self, duration_seconds: int, duration_text: str = None) -> Dict[str, any]:
        """
        Set a timer for specified duration.
        
        Args:
            duration_seconds: Duration in seconds
            duration_text: Human-readable duration (e.g., "5 minutes")
        """
        if duration_seconds <= 0:
            return {
                "success": False,
                "error": "Timer duration must be greater than 0"
            }
        
        # Cancel existing timer if any
        if self.active_timer and self.active_timer.is_alive():
            self.timer_cancelled = True
            time.sleep(0.5)  # Give it a moment to cancel
        
        # Create new timer thread
        if duration_text is None:
            if duration_seconds < 60:
                duration_text = f"{duration_seconds} second{'s' if duration_seconds != 1 else ''}"
            elif duration_seconds < 3600:
                minutes = duration_seconds // 60
                duration_text = f"{minutes} minute{'s' if minutes != 1 else ''}"
            else:
                hours = duration_seconds // 3600
                duration_text = f"{hours} hour{'s' if hours != 1 else ''}"
        
        self.active_timer = threading.Thread(
            target=self._timer_thread,
            args=(duration_seconds, duration_text),
            daemon=True
        )
        self.active_timer.start()
        
        return {
            "success": True,
            "message": f"Timer set for {duration_text}"
        }
    
    def cancel_timer(self) -> Dict[str, any]:
        """Cancel the active timer if one is running."""
        if self.active_timer and self.active_timer.is_alive():
            self.timer_cancelled = True
            time.sleep(0.5)  # Give it a moment to cancel
            self.active_timer = None
            return {
                "success": True,
                "message": "Timer cancelled"
            }
        else:
            return {
                "success": False,
                "error": "No active timer to cancel"
            }
    
    def _parse_time(self, time_str: str) -> Dict[str, any]:
        """
        Parse time string to calculate seconds until that time.
        Supports formats: "3 PM", "7:30 AM", "6 o'clock", "14:30"
        
        Returns:
            dict with 'success', 'seconds_until', 'time_str' keys
        """
        time_str = time_str.strip().lower()
        now = datetime.now()
        
        # Pattern 1: "3 PM" or "3pm" or "3 o'clock"
        match1 = re.search(r'(\d{1,2})\s*(?:o\'?clock|am|pm|a\.m\.|p\.m\.)?', time_str)
        if match1:
            hour = int(match1.group(1))
            is_pm = 'pm' in time_str or 'p.m.' in time_str
            is_am = 'am' in time_str or 'a.m.' in time_str
            
            if is_pm and hour != 12:
                hour += 12
            elif is_am and hour == 12:
                hour = 0
            
            target_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            
            # If time has passed today, set for tomorrow
            if target_time <= now:
                target_time += timedelta(days=1)
            
            seconds_until = (target_time - now).total_seconds()
            return {
                "success": True,
                "seconds_until": int(seconds_until),
                "time_str": target_time.strftime("%I:%M %p")
            }
        
        # Pattern 2: "7:30 AM" or "14:30"
        match2 = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm|a\.m\.|p\.m\.)?', time_str)
        if match2:
            hour = int(match2.group(1))
            minute = int(match2.group(2))
            period = match2.group(3) if match2.group(3) else None
            
            if period:
                is_pm = 'pm' in period.lower() or 'p.m.' in period.lower()
                if is_pm and hour != 12:
                    hour += 12
                elif not is_pm and hour == 12:
                    hour = 0
            else:
                # 24-hour format
                if hour >= 24:
                    return {"success": False, "error": "Invalid hour"}
            
            target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # If time has passed today, set for tomorrow
            if target_time <= now:
                target_time += timedelta(days=1)
            
            seconds_until = (target_time - now).total_seconds()
            return {
                "success": True,
                "seconds_until": int(seconds_until),
                "time_str": target_time.strftime("%I:%M %p")
            }
        
        return {"success": False, "error": f"Could not parse time: {time_str}"}
    
    
    def set_reminder(self, time_str: str = None, duration_seconds: int = None, duration_text: str = None, task: str = None) -> Dict[str, any]:
        """
        Set a reminder in the system Reminders app.
        
        Args:
            time_str: Absolute time (e.g., "3 PM", "7:30 AM")
            duration_seconds: Relative duration in seconds
            duration_text: Human-readable duration (e.g., "30 minutes")
            task: Optional task description
        """
        if self.platform == "darwin":  # macOS
            # Calculate reminder time
            if time_str:
                time_result = self._parse_time(time_str)
                if not time_result.get('success'):
                    return {
                        "success": False,
                        "error": time_result.get('error', 'Invalid time format')
                    }
                target_datetime = datetime.now() + timedelta(seconds=time_result['seconds_until'])
                display_time = time_result['time_str']
            elif duration_seconds:
                if duration_seconds <= 0:
                    return {
                        "success": False,
                        "error": "Reminder duration must be greater than 0"
                    }
                target_datetime = datetime.now() + timedelta(seconds=duration_seconds)
                if duration_text:
                    display_time = duration_text
                else:
                    if duration_seconds < 60:
                        display_time = f"{duration_seconds} second{'s' if duration_seconds != 1 else ''}"
                    elif duration_seconds < 3600:
                        minutes = duration_seconds // 60
                        display_time = f"{minutes} minute{'s' if minutes != 1 else ''}"
                    else:
                        hours = duration_seconds // 3600
                        display_time = f"{hours} hour{'s' if hours != 1 else ''}"
            else:
                return {
                    "success": False,
                    "error": "Please specify either a time or duration for the reminder"
                }
            
            # Calculate seconds until target time
            seconds_until = (target_datetime - datetime.now()).total_seconds()
            
            reminder_name = task if task else "Reminder"
            # Escape quotes and backslashes in reminder name
            reminder_name = reminder_name.replace('\\', '\\\\').replace('"', '\\"')
            
            # Create reminder in Reminders app using date calculation
            # Calculate the target date by adding seconds to current date
            script = f'''
            tell application "Reminders"
                set newReminder to make new reminder
                set name of newReminder to "{reminder_name}"
                set targetDate to (current date) + ({int(seconds_until)} * 1)
                set remind me date of newReminder to targetDate
                set body of newReminder to "Set by Dollar Assistant"
            end tell
            '''
            
            result = self._run_command(['osascript', '-e', script])
            if result.get('success'):
                task_text = f" '{task}'" if task else ""
                return {
                    "success": True,
                    "message": f"Reminder{task_text} set for {display_time} in Reminders app"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create reminder: {result.get('error', 'Unknown error')}"
                }
        
        elif self.platform == "windows":
            # Use PowerShell to create calendar event/reminder
            if time_str:
                time_result = self._parse_time(time_str)
                if not time_result.get('success'):
                    return {
                        "success": False,
                        "error": time_result.get('error', 'Invalid time format')
                    }
                target_datetime = datetime.now() + timedelta(seconds=time_result['seconds_until'])
                display_time = time_result['time_str']
            elif duration_seconds:
                target_datetime = datetime.now() + timedelta(seconds=duration_seconds)
                display_time = duration_text or f"{duration_seconds} seconds"
            else:
                return {
                    "success": False,
                    "error": "Please specify either a time or duration for the reminder"
                }
            
            reminder_name = task if task else "Reminder"
            date_str = target_datetime.strftime("%Y-%m-%d %H:%M:%S")
            
            ps_cmd = f'''
            $reminder = New-Object -ComObject Outlook.Application
            $reminder.CreateItem(1) | ForEach-Object {{
                $_.Subject = "{reminder_name}"
                $_.Start = [DateTime]::Parse("{date_str}")
                $_.ReminderSet = $true
                $_.Save()
            }}
            '''
            result = self._run_command(['powershell', '-Command', ps_cmd])
            if result.get('success'):
                return {
                    "success": True,
                    "message": f"Reminder set for {display_time}"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create reminder. Make sure Outlook is installed."
                }
        
        elif self.platform == "linux":
            # Use calendar/reminder tools (e.g., evolution, thunderbird, or at command)
            if duration_seconds:
                # Use 'at' command for relative time
                reminder_name = task if task else "Reminder"
                at_time = f"now + {duration_seconds // 60} minutes"
                cmd = f'echo "notify-send \\"Reminder\\" \\"{reminder_name}\\" -i reminder" | at {at_time}'
                result = self._run_command(['bash', '-c', cmd])
            else:
                return {
                    "success": False,
                    "error": "Linux reminders require duration. Absolute time not yet supported."
                }
            
            if result.get('success'):
                return {
                    "success": True,
                    "message": f"Reminder set for {duration_text or f'{duration_seconds} seconds'}"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create reminder. Install 'at' package: sudo apt-get install at"
                }
        
        else:
            return {
                "success": False,
                "error": f"Reminders not supported on platform: {self.platform}"
            }
    
    def cancel_reminders(self) -> Dict[str, any]:
        """Cancel reminders - note: system reminders must be cancelled manually in the app."""
        return {
            "success": True,
            "message": "Please cancel reminders manually in the Reminders app"
        }
    
    def set_alarm(self, time_str: str) -> Dict[str, any]:
        """
        Set an alarm in the system Clock app.
        
        Args:
            time_str: Time string (e.g., "7 AM", "6:30 AM", "14:30")
        """
        time_result = self._parse_time(time_str)
        if not time_result.get('success'):
            return {
                "success": False,
                "error": time_result.get('error', 'Invalid time format')
            }
        
        target_datetime = datetime.now() + timedelta(seconds=time_result['seconds_until'])
        display_time = time_result['time_str']
        
        if self.platform == "darwin":  # macOS
            # Create alarm in Clock app using Calendar event (Clock app doesn't have direct AppleScript support)
            # Alternative: Use Calendar app to create an event that acts as an alarm
            seconds_until = (target_datetime - datetime.now()).total_seconds()
            
            script = f'''
            tell application "Calendar"
                tell calendar "Home"
                    set targetDate to (current date) + ({int(seconds_until)} * 1)
                    set newEvent to make new event at end with properties {{summary:"Alarm - Wake Up", start date:targetDate, allday event:false}}
                end tell
            end tell
            '''
            
            result = self._run_command(['osascript', '-e', script])
            if result.get('success'):
                return {
                    "success": True,
                    "message": f"Alarm set for {display_time} in Calendar app"
                }
            else:
                # Fallback: Try to open Clock app (user can set manually)
                self._run_command(['open', '-a', 'Clock'])
                return {
                    "success": True,
                    "message": f"Opened Clock app. Please set alarm for {display_time} manually"
                }
        
        elif self.platform == "windows":
            # Use PowerShell to create calendar event with reminder
            date_str = target_datetime.strftime("%Y-%m-%d %H:%M:%S")
            
            ps_cmd = f'''
            $alarm = New-Object -ComObject Outlook.Application
            $alarm.CreateItem(1) | ForEach-Object {{
                $_.Subject = "Alarm - Wake Up"
                $_.Start = [DateTime]::Parse("{date_str}")
                $_.ReminderSet = $true
                $_.ReminderMinutesBeforeStart = 0
                $_.Save()
            }}
            '''
            result = self._run_command(['powershell', '-Command', ps_cmd])
            if result.get('success'):
                return {
                    "success": True,
                    "message": f"Alarm set for {display_time}"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create alarm. Make sure Outlook is installed."
                }
        
        elif self.platform == "linux":
            # Use at command or calendar tools
            date_str = target_datetime.strftime("%H:%M %Y-%m-%d")
            cmd = f'echo "notify-send \\"Alarm\\" \\"Time to wake up!\\" -i alarm-clock --urgency=critical -a Alarm" | at {date_str}'
            result = self._run_command(['bash', '-c', cmd])
            if result.get('success'):
                return {
                    "success": True,
                    "message": f"Alarm set for {display_time}"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create alarm. Install 'at' package: sudo apt-get install at"
                }
        
        else:
            return {
                "success": False,
                "error": f"Alarms not supported on platform: {self.platform}"
            }
    
    def cancel_alarms(self) -> Dict[str, any]:
        """Cancel alarms - note: system alarms must be cancelled manually in the app."""
        return {
            "success": True,
            "message": "Please cancel alarms manually in the Clock/Calendar app"
        }

