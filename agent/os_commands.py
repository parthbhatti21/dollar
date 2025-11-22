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
from datetime import datetime
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
    
    def volume_up(self) -> Dict[str, any]:
        """Increase system volume."""
        if self.platform == "darwin":  # macOS
            return self._run_command(
                ['osascript', '-e', 'set volume output volume ((output volume of (get volume settings)) + 10)']
            )
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
            return self._run_command(
                ['osascript', '-e', 'set volume output volume ((output volume of (get volume settings)) - 10)']
            )
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
            return self._run_command(
                ['osascript', '-e', f'set volume output volume {volume}']
            )
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

