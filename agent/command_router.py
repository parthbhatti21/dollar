#!/usr/bin/env python3
"""
Command router - routes intents to appropriate OS command handlers.
"""

import logging
import re
from os_commands import OSCommands

logger = logging.getLogger(__name__)

class CommandRouter:
    """Routes classified intents to command execution."""
    
    def __init__(self, config):
        """
        Initialize command router.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.os_commands = OSCommands(config)
    
    def execute(self, intent_data: dict, original_text: str) -> dict:
        """
        Execute command based on intent.
        
        Args:
            intent_data: Dictionary with 'intent' and 'entities' keys
            original_text: Original user text (for context)
            
        Returns:
            dict: Result with 'success' and 'message'/'error' keys
        """
        intent = intent_data.get('intent', 'unknown')
        entities = intent_data.get('entities', {})
        
        logger.info(f"Executing intent: {intent} with entities: {entities}")
        
        try:
            if intent == "lock":
                return self.os_commands.lock_device()
            
            elif intent == "open_app":
                app_name = entities.get('app_name', '')
                if not app_name:
                    # Try to extract from original text
                    app_name = self._extract_app_name(original_text)
                return self.os_commands.open_app(app_name)
            
            elif intent == "youtube_search":
                search_query = entities.get('search_query', '')
                if not search_query:
                    # Try to extract from original text
                    search_match = re.search(r'search\s+(.+?)\s+(?:on\s+)?(?:youtube|yt)', original_text, re.IGNORECASE)
                    if search_match:
                        search_query = search_match.group(1).strip()
                        search_query = re.sub(r'[.,!?;:]+$', '', search_query).strip()
                if search_query:
                    return self.os_commands.open_youtube_search(search_query)
                else:
                    return {
                        "success": False,
                        "error": "Please specify what to search on YouTube"
                    }
            
            elif intent == "github_search":
                search_query = entities.get('search_query', None)
                # Extract search query from "open github [query]" or "search github [query]"
                if search_query is None:
                    # Try to extract from original text
                    github_match = re.search(r'(?:open\s+)?github\s+(.+?)$', original_text, re.IGNORECASE)
                    if github_match and github_match.group(1):
                        search_query = github_match.group(1).strip()
                        search_query = re.sub(r'[.,!?;:]+$', '', search_query).strip()
                        # Remove common trailing phrases
                        search_query = re.sub(r'\s+(?:and\s+)?(?:search|find|look|for).*$', '', search_query, flags=re.IGNORECASE).strip()
                        if not search_query or search_query.lower() in ['and', 'search', 'find', 'look', 'for']:
                            search_query = None
                # If still None, it means just "open github" - open search page without query
                return self.os_commands.open_github_search(search_query)
            
            elif intent == "open_cursor":
                return self.os_commands.open_cursor()
            
            elif intent == "close_dollar":
                return self.os_commands.close_dollar()
            
            elif intent == "volume_up":
                return self.os_commands.volume_up()
            
            elif intent == "volume_down":
                return self.os_commands.volume_down()
            
            elif intent == "volume_set":
                volume = entities.get('volume', 50)
                return self.os_commands.set_volume(volume)
            
            elif intent == "wifi_on":
                return self.os_commands.wifi_on()
            
            elif intent == "wifi_off":
                return self.os_commands.wifi_off()
            
            elif intent == "bluetooth_on":
                return self.os_commands.bluetooth_on()
            
            elif intent == "bluetooth_off":
                return self.os_commands.bluetooth_off()
            
            elif intent == "shutdown":
                return self.os_commands.shutdown()
            
            elif intent == "restart":
                return self.os_commands.restart()
            
            elif intent == "system_info":
                return self.os_commands.get_system_info()
            
            elif intent == "time":
                return self.os_commands.get_time()
            
            elif intent == "date":
                return self.os_commands.get_date()
            
            elif intent == "weather":
                return self.os_commands.get_weather()
            
            elif intent == "media_play":
                return self.os_commands.media_play()
            
            elif intent == "media_pause":
                return self.os_commands.media_pause()
            
            elif intent == "media_stop":
                return self.os_commands.media_stop()
            
            elif intent == "media_next":
                return self.os_commands.media_next()
            
            elif intent == "media_previous":
                return self.os_commands.media_previous()
            
            elif intent == "spotify_play":
                song_name = entities.get('song_name', '')
                if not song_name:
                    # Try to extract from original text
                    song_name = self._extract_song_name(original_text)
                return self.os_commands.spotify_play_song(song_name)
            
            elif intent == "timer_set":
                duration_seconds = entities.get('duration_seconds', 0)
                duration_text = entities.get('duration_text', None)
                if duration_seconds <= 0:
                    return {
                        "success": False,
                        "error": "Please specify a valid timer duration (e.g., 'set timer for 5 minutes')"
                    }
                return self.os_commands.set_timer(duration_seconds, duration_text)
            
            elif intent == "timer_cancel":
                return self.os_commands.cancel_timer()
            
            elif intent == "reminder_set":
                time_str = entities.get('time')
                duration_seconds = entities.get('duration_seconds')
                duration_text = entities.get('duration_text')
                task = entities.get('task')
                return self.os_commands.set_reminder(
                    time_str=time_str,
                    duration_seconds=duration_seconds,
                    duration_text=duration_text,
                    task=task
                )
            
            elif intent == "reminder_cancel":
                return self.os_commands.cancel_reminders()
            
            elif intent == "alarm_set":
                time_str = entities.get('time')
                if not time_str:
                    return {
                        "success": False,
                        "error": "Please specify a time for the alarm (e.g., 'set alarm for 7 AM')"
                    }
                return self.os_commands.set_alarm(time_str)
            
            elif intent == "alarm_cancel":
                return self.os_commands.cancel_alarms()
            
            elif intent == "greeting":
                import random
                responses = [
                    "Hello! How can I help you?",
                    "Hi there! What can I do for you?",
                    "Hey! I'm here to help.",
                    "Good to see you! How can I assist?",
                    "I'm doing great, thanks for asking! How can I help you today?"
                ]
                return {
                    "success": True,
                    "message": random.choice(responses)
                }
            
            elif intent == "thanks":
                import random
                responses = [
                    "You're welcome!",
                    "Happy to help!",
                    "Anytime!",
                    "Glad I could help!",
                    "My pleasure!"
                ]
                return {
                    "success": True,
                    "message": random.choice(responses)
                }
            
            elif intent == "goodbye":
                return {
                    "success": True,
                    "message": "Goodbye! Have a great day!"
                }
            
            else:
                return {
                    "success": False,
                    "error": f"I don't understand the command: {original_text}"
                }
        
        except Exception as e:
            logger.error(f"Error executing command: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to execute command: {str(e)}"
            }
    
    def _extract_song_name(self, text: str) -> str:
        """Extract song name from text if not in entities."""
        import re
        song_text = text.lower()
        
        # Handle Spotify keywords including mispronunciations
        spotify_keywords = r'(?:spotify|spot\s*if\s*i|45|spot\s*if\s*eye)'
        
        # Pattern 1: "play [song] on spotify" or "play [song] on 45"
        match1 = re.search(r'play\s+(.+?)\s+(?:on|in)\s+' + spotify_keywords, song_text)
        if match1:
            song_text = match1.group(1).strip()
        else:
            # Pattern 2: "spotify play [song]" or "45 play [song]"
            match2 = re.search(r'(?:spotify|45|spot\s*if\s*i)\s+play\s+(.+)', song_text)
            if match2:
                song_text = match2.group(1).strip()
            else:
                # Pattern 3: Just remove prefixes
                song_text = re.sub(r'^(?:play|spotify\s+play|45\s+play)\s+', '', song_text)
                song_text = re.sub(r'\s+(?:on|in)\s+(?:spotify|45|spot\s*if\s*i).*$', '', song_text)
        
        # Clean up
        song_text = re.sub(r'^(?:play\s+)?(?:song|track)\s+', '', song_text)
        song_text = re.sub(r'[.,!?;:]+$', '', song_text).strip()
        song_text = re.sub(r'\s+on\s+(?:45|spotify|spot\s*if\s*i).*$', '', song_text)
        song_text = re.sub(r'\s+in\s+(?:45|spotify|spot\s*if\s*i).*$', '', song_text)
        
        return song_text
    
    def _extract_app_name(self, text: str) -> str:
        """Extract app name from text if not in entities."""
        import re
        match = re.search(r'(?:open|launch|start)\s+(?:the\s+)?(.+)', text.lower())
        if match:
            app_name = match.group(1).strip()
            # Remove trailing "app" or "application"
            app_name = re.sub(r'\s+(app|application)$', '', app_name, flags=re.IGNORECASE)
            # Remove trailing punctuation (periods, commas, etc.)
            app_name = re.sub(r'[.,!?;:]+$', '', app_name).strip()
            return app_name
        return ""

