#!/usr/bin/env python3
"""
Visual indicator using system notifications to show assistant status.
Shows notifications when listening for commands.
"""

import logging
import platform
import subprocess

logger = logging.getLogger(__name__)

class VisualIndicator:
    """Visual indicator using system notifications."""
    
    def __init__(self):
        """Initialize the visual indicator."""
        self.enabled = True
        self.platform = platform.system()
        self._state = 'idle'
        logger.info(f"Visual indicator initialized for platform: {self.platform}")
    
    def _show_notification(self, title: str, message: str):
        """Show a system notification."""
        if not self.enabled:
            return
        
        try:
            if self.platform == "Darwin":  # macOS
                # Use osascript to show notification
                script = f'''
                display notification "{message}" with title "{title}"
                '''
                subprocess.run(
                    ['osascript', '-e', script],
                    capture_output=True,
                    timeout=2
                )
            elif self.platform == "Linux":
                # Use notify-send if available
                try:
                    subprocess.run(
                        ['notify-send', title, message],
                        capture_output=True,
                        timeout=2
                    )
                except FileNotFoundError:
                    logger.debug("notify-send not available")
            elif self.platform == "Windows":
                # Use PowerShell to show notification
                ps_cmd = f'''
                [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
                $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
                $textNodes = $template.GetElementsByTagName("text")
                $textNodes.Item(0).AppendChild($template.CreateTextNode("{title}")) | Out-Null
                $textNodes.Item(1).AppendChild($template.CreateTextNode("{message}")) | Out-Null
                $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
                [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Dollar Assistant").Show($toast)
                '''
                subprocess.run(
                    ['powershell', '-Command', ps_cmd],
                    capture_output=True,
                    timeout=2
                )
        except Exception as e:
            logger.debug(f"Failed to show notification: {e}")
    
    def show_listening(self):
        """Show the listening indicator."""
        self._state = 'listening'
        # Don't show notification for listening (too frequent)
        # Just log it
        logger.debug("Visual indicator: Listening")
    
    def show_processing(self):
        """Show processing indicator."""
        self._state = 'processing'
        self._show_notification("Dollar Assistant", "Processing your command...")
        logger.debug("Visual indicator: Processing")
    
    def show_ready(self):
        """Show ready state."""
        self._state = 'idle'
        # Don't show notification for ready state
        logger.debug("Visual indicator: Ready")
    
    def hide(self):
        """Hide the indicator (no-op for notifications)."""
        self._state = 'idle'
    
    def cleanup(self):
        """Clean up resources."""
        pass
    
    def update(self):
        """Update the window (not needed for notifications)."""
        pass
