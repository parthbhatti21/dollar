#!/usr/bin/env python3
"""
Intent classification module.
Uses pattern matching, fuzzy matching, and optionally local LLM.
"""

import logging
import re
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class IntentClassifier:
    """Classifies user intents from transcribed text."""
    
    def __init__(self, config):
        """
        Initialize intent classifier.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.intents = self._load_intents()
        self.use_fuzzy = config.get('intent', {}).get('use_fuzzy', True)
        self.use_llm = config.get('intent', {}).get('use_llm_fallback', False)
        self.llm_model = None
        
        if self.use_fuzzy:
            try:
                from fuzzywuzzy import fuzz
                self.fuzz = fuzz
            except ImportError:
                logger.warning("fuzzywuzzy not available, using exact matching only")
                self.use_fuzzy = False
        
        if self.use_llm:
            self._init_llm()
    
    def _load_intents(self) -> Dict[str, List[str]]:
        """Load intent patterns from config."""
        return {
            "lock": [
                "lock", "lock device", "lock screen", "secure", "lock computer",
                "lock my device", "lock the screen", "lock this device"
            ],
            "open_app": [
                "open", "launch", "start app", "open app", "run", "start",
                "open application", "launch application", "open the app"
            ],
            "volume_up": [
                "volume up", "increase volume", "turn up volume", "louder",
                "raise volume", "volume higher"
            ],
            "volume_down": [
                "volume down", "decrease volume", "turn down volume", "quieter",
                "lower volume", "volume lower"
            ],
            "volume_set": [
                "set volume", "volume to", "volume at", "set volume to"
            ],
            "wifi_on": [
                "turn on wifi", "enable wifi", "wifi on", "connect wifi",
                "turn wifi on", "enable wireless", "turn on wi-fi", "turn on wi fi",
                "turn on the wifi", "turn on the wi-fi", "enable the wifi"
            ],
            "wifi_off": [
                "turn off wifi", "disable wifi", "wifi off", "disconnect wifi",
                "turn wifi off", "disable wireless", "turn off wi-fi", "turn off wi fi",
                "turn off the wifi", "turn off the wi-fi", "disable the wifi",
                "turn off wireless", "turn off the wireless"
            ],
            "bluetooth_on": [
                "turn on bluetooth", "enable bluetooth", "bluetooth on",
                "turn bluetooth on", "enable bluetooth"
            ],
            "bluetooth_off": [
                "turn off bluetooth", "disable bluetooth", "bluetooth off",
                "turn bluetooth off", "disable bluetooth"
            ],
            "shutdown": [
                "shutdown", "shut down", "power off", "shut down computer",
                "power down", "turn off computer", "turn off the computer",
                "shutdown computer", "power off computer"
            ],
            "restart": [
                "restart", "reboot", "restart computer", "reboot computer",
                "restart the system", "reboot the system"
            ],
            "system_info": [
                "system info", "system information", "system status", "device info",
                "computer info", "show system info", "what's my system info"
            ],
            "time": [
                "what time", "current time", "time now", "what's the time",
                "tell me the time"
            ],
            "date": [
                "what date", "current date", "date today", "what's the date",
                "tell me the date"
            ],
            "weather": [
                "weather", "what's the weather", "weather forecast", "how's the weather"
            ],
            "media_play": [
                "play", "play music", "resume", "resume music", "unpause", "start music"
            ],
            "media_pause": [
                "pause", "pause music", "pause playback"
            ],
            "media_stop": [
                "stop", "stop music", "stop song", "stop the song", "stop playback",
                "stop playing", "stop the music"
            ],
            "media_next": [
                "next song", "next track", "skip", "skip song", "next", "play next"
            ],
            "media_previous": [
                "previous song", "previous track", "go back", "last song", "previous", "play previous"
            ],
            "spotify_play": [
                "play on spotify", "play in spotify", "spotify play", "play song on spotify",
                "play track on spotify", "play music on spotify", "spotify", "play on 45",
                "play in 45", "45 play", "play song on 45", "play on spot if i", "play on spot if i"
            ],
            "greeting": [
                "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
                "how are you", "how are you doing", "what's up", "how's it going"
            ],
            "thanks": [
                "thank you", "thanks", "thank you very much", "appreciate it"
            ],
            "goodbye": [
                "goodbye", "bye", "see you", "see you later", "farewell"
            ],
            "unknown": []  # Fallback intent
        }
    
    def _init_llm(self):
        """Initialize local LLM for intent classification fallback."""
        try:
            # Try to load a lightweight local LLM
            # Options: llama.cpp, transformers with small model, etc.
            logger.info("LLM fallback enabled but not implemented yet")
            # This would require additional setup with llama.cpp or similar
            self.use_llm = False
        except Exception as e:
            logger.warning(f"Failed to initialize LLM: {e}")
            self.use_llm = False
    
    def get_intent(self, text: str) -> Dict[str, any]:
        """
        Classify intent from text.
        
        Args:
            text: User's transcribed speech
            
        Returns:
            dict: Intent information with 'intent' and 'entities' keys
        """
        if not text:
            return {"intent": "unknown", "entities": {}}
        
        text_lower = text.lower().strip()
        
        # PRIORITY 1: Check for Spotify play commands FIRST (before other patterns)
        # This handles cases where "spotify" is mispronounced as "45" or similar
        spotify_keywords = r'(?:spotify|spot\s*if\s*i|45|spot\s*if\s*eye)'
        
        # Check regex patterns FIRST (they handle complex Spotify patterns)
        regex_match = self._regex_match(text_lower)
        if regex_match and regex_match.get('intent') == 'spotify_play':
            return regex_match
        
        # Also check if text contains Spotify keywords and "play"
        if re.search(spotify_keywords, text_lower) and re.search(r'\bplay\b', text_lower):
            # Try to extract song name - pattern: "play [song] on spotify"
            song_match = re.search(r'play\s+(.+?)\s+(?:on|in)\s+' + spotify_keywords, text_lower)
            if song_match:
                song_name = song_match.group(1).strip()
                song_name = re.sub(r'[.,!?;:]+$', '', song_name)
                if song_name and len(song_name) > 0:
                    logger.info(f"Detected Spotify play command for song: {song_name}")
                    return {
                        "intent": "spotify_play",
                        "entities": {"song_name": song_name}
                    }
        
        # PRIORITY 2: Check for app opening patterns (open/launch/start + app name)
        # This must be checked BEFORE other intents to avoid false matches
        app_pattern = re.search(r'\b(?:open|launch|start)\s+(?:the\s+)?(.+)', text_lower)
        if app_pattern:
            app_name = app_pattern.group(1).strip()
            # Remove trailing punctuation
            app_name = re.sub(r'[.,!?;:]+$', '', app_name).strip()
            # Remove "app" or "application" suffix
            app_name = re.sub(r'\s+(app|application)$', '', app_name, flags=re.IGNORECASE)
            if app_name:  # Only if we actually have an app name
                return {
                    "intent": "open_app",
                    "entities": {"app_name": app_name}
                }
        
        # PRIORITY 3: Check for WiFi/Bluetooth commands BEFORE generic "turn off" (shutdown)
        # This prevents "turn off wifi" from matching "turn off" (shutdown)
        wifi_off_patterns = [
            r'\b(?:turn\s+off|disable|turn\s+off\s+the)\s+(?:the\s+)?(?:wi[-\s]?fi|wireless)\b',
            r'\b(?:wi[-\s]?fi|wireless)\s+(?:off|disable)\b'
        ]
        for pattern in wifi_off_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.info(f"Detected WiFi off command: {text_lower}")
                return {"intent": "wifi_off", "entities": {}}
        
        wifi_on_patterns = [
            r'\b(?:turn\s+on|enable|turn\s+on\s+the)\s+(?:the\s+)?(?:wi[-\s]?fi|wireless)\b',
            r'\b(?:wi[-\s]?fi|wireless)\s+(?:on|enable)\b'
        ]
        for pattern in wifi_on_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.info(f"Detected WiFi on command: {text_lower}")
                return {"intent": "wifi_on", "entities": {}}
        
        bluetooth_off_patterns = [
            r'\b(?:turn\s+off|disable|turn\s+off\s+the)\s+(?:the\s+)?bluetooth\b',
            r'\bbluetooth\s+(?:off|disable)\b'
        ]
        for pattern in bluetooth_off_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.info(f"Detected Bluetooth off command: {text_lower}")
                return {"intent": "bluetooth_off", "entities": {}}
        
        bluetooth_on_patterns = [
            r'\b(?:turn\s+on|enable|turn\s+on\s+the)\s+(?:the\s+)?bluetooth\b',
            r'\bbluetooth\s+(?:on|enable)\b'
        ]
        for pattern in bluetooth_on_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.info(f"Detected Bluetooth on command: {text_lower}")
                return {"intent": "bluetooth_on", "entities": {}}
        
        # PRIORITY 4: Try exact matching with word boundaries to avoid substring matches
        # SKIP media_play if we have "spotify" or "45" in the text (to avoid false matches)
        has_spotify_keyword = bool(re.search(spotify_keywords, text_lower))
        
        for intent, patterns in self.intents.items():
            if intent == "unknown" or intent == "open_app":  # Skip open_app, already handled above
                continue
            
            # Skip wifi/bluetooth intents (already handled above with regex priority)
            if intent in ["wifi_on", "wifi_off", "bluetooth_on", "bluetooth_off"]:
                continue
            
            # Skip media_play if text contains Spotify keywords (already handled above)
            if intent == "media_play" and has_spotify_keyword:
                continue
            
            for pattern in patterns:
                # Use word boundaries to avoid substring matches (e.g., "lock" in "launch")
                # For single words, require word boundaries
                if len(pattern.split()) == 1:
                    pattern_re = r'\b' + re.escape(pattern) + r'\b'
                else:
                    # For multi-word patterns, just check if pattern exists
                    pattern_re = re.escape(pattern)
                
                if re.search(pattern_re, text_lower, re.IGNORECASE):
                    entities = self._extract_entities(intent, text_lower)
                    return {"intent": intent, "entities": entities}
        
        # Try fuzzy matching
        if self.use_fuzzy:
            best_match = self._fuzzy_match(text_lower)
            if best_match:
                entities = self._extract_entities(best_match, text_lower)
                return {"intent": best_match, "entities": entities}
        
        # Regex patterns already checked at the beginning for Spotify
        # Only check again if we haven't found a match yet (for other patterns like volume_set)
        regex_match_retry = self._regex_match(text_lower)
        if regex_match_retry and regex_match_retry.get('intent') != 'spotify_play':
            return regex_match_retry
        
        # Fallback to LLM if enabled
        if self.use_llm and self.llm_model:
            llm_intent = self._llm_classify(text_lower)
            if llm_intent:
                return llm_intent
        
        # Default to unknown
        logger.warning(f"Could not classify intent for: {text}")
        return {"intent": "unknown", "entities": {}}
    
    def _fuzzy_match(self, text: str) -> str:
        """Use fuzzy matching to find best intent match."""
        best_score = 0
        best_intent = None
        
        for intent, patterns in self.intents.items():
            if intent == "unknown":
                continue
            
            for pattern in patterns:
                score = self.fuzz.partial_ratio(text, pattern)
                if score > best_score and score > 70:  # Threshold
                    best_score = score
                    best_intent = intent
        
        return best_intent
    
    def _regex_match(self, text: str) -> Dict[str, any]:
        """Use regex patterns for complex intent matching."""
        # Spotify play pattern - handle various formats and common mispronunciations
        # Patterns: "play [song] on spotify", "play [song] on 45", "spotify play [song]", etc.
        # Also handle: "play [song] on spot if i", "play [song] in spotify", etc.
        
        # First, check for explicit Spotify mentions (including common mispronunciations)
        spotify_keywords = r'(?:spotify|spot\s*if\s*i|45|spot\s*if\s*eye|spot\s*if\s*why)'
        
        # Pattern 1: "play [song] on spotify" or "play [song] on 45"
        spotify_pattern1 = re.search(
            r'play\s+(.+?)\s+(?:on|in)\s+' + spotify_keywords,
            text,
            re.IGNORECASE
        )
        if spotify_pattern1:
            song_name = spotify_pattern1.group(1).strip()
            song_name = re.sub(r'[.,!?;:]+$', '', song_name)
            if song_name and len(song_name) > 0:
                return {
                    "intent": "spotify_play",
                    "entities": {"song_name": song_name}
                }
        
        # Pattern 2: "spotify play [song]" or "45 play [song]"
        spotify_pattern2 = re.search(
            r'(?:spotify|45|spot\s*if\s*i)\s+play\s+(.+)',
            text,
            re.IGNORECASE
        )
        if spotify_pattern2:
            song_name = spotify_pattern2.group(1).strip()
            song_name = re.sub(r'[.,!?;:]+$', '', song_name)
            if song_name and len(song_name) > 0:
                return {
                    "intent": "spotify_play",
                    "entities": {"song_name": song_name}
                }
        
        # Pattern 3: "play [song] on spotify" (more flexible)
        spotify_pattern3 = re.search(
            r'play\s+(.+?)\s+(?:on|in)\s+(?:spotify|45|spot\s*if\s*i)',
            text,
            re.IGNORECASE
        )
        if spotify_pattern3:
            song_name = spotify_pattern3.group(1).strip()
            song_name = re.sub(r'[.,!?;:]+$', '', song_name)
            if song_name and len(song_name) > 0:
                return {
                    "intent": "spotify_play",
                    "entities": {"song_name": song_name}
                }
        
        # Pattern 4: If text contains "45" or "spotify" keywords and "play", assume Spotify intent
        # This handles cases like "play song on 45" where "45" is mispronounced "spotify"
        if re.search(r'\b(?:45|spotify|spot\s*if\s*i)\b', text, re.IGNORECASE) and re.search(r'\bplay\b', text, re.IGNORECASE):
            # Extract song name - everything after "play" and before "on 45" or similar
            song_match = re.search(r'play\s+(.+?)\s+(?:on|in)\s+(?:45|spotify|spot\s*if\s*i)', text, re.IGNORECASE)
            if song_match:
                song_name = song_match.group(1).strip()
                song_name = re.sub(r'[.,!?;:]+$', '', song_name)
                if song_name and len(song_name) > 0:
                    return {
                        "intent": "spotify_play",
                        "entities": {"song_name": song_name}
                    }
        
        # Volume set pattern: "set volume to X" or "volume to X percent"
        volume_match = re.search(r'volume\s+(?:to|at)\s+(\d+)', text)
        if volume_match:
            volume = int(volume_match.group(1))
            return {
                "intent": "volume_set",
                "entities": {"volume": min(100, max(0, volume))}
            }
        
        # Open app pattern: "open [app name]" or "launch [app name]"
        app_match = re.search(r'(?:open|launch|start)\s+(?:the\s+)?(.+)', text)
        if app_match:
            app_name = app_match.group(1).strip()
            # Remove common trailing words
            app_name = re.sub(r'\s+(app|application)$', '', app_name, flags=re.IGNORECASE)
            return {
                "intent": "open_app",
                "entities": {"app_name": app_name}
            }
        
        return None
    
    def _extract_entities(self, intent: str, text: str) -> Dict[str, any]:
        """Extract entities from text based on intent."""
        entities = {}
        
        if intent == "open_app":
            # Extract app name
            match = re.search(r'(?:open|launch|start)\s+(?:the\s+)?(.+)', text)
            if match:
                app_name = match.group(1).strip()
                # Remove trailing "app" or "application"
                app_name = re.sub(r'\s+(app|application)$', '', app_name, flags=re.IGNORECASE)
                # Remove trailing punctuation (periods, commas, etc.)
                app_name = re.sub(r'[.,!?;:]+$', '', app_name).strip()
                entities["app_name"] = app_name
        
        elif intent == "volume_set":
            # Extract volume level
            match = re.search(r'(\d+)', text)
            if match:
                volume = int(match.group(1))
                entities["volume"] = min(100, max(0, volume))
        
        elif intent == "spotify_play":
            # Extract song name - handle various formats and mispronunciations
            song_text = text.lower()
            
            # Remove Spotify keywords (including mispronunciations)
            spotify_keywords = r'(?:spotify|spot\s*if\s*i|45|spot\s*if\s*eye|spot\s*if\s*why)'
            
            # Pattern 1: "play [song] on spotify" -> extract [song]
            match1 = re.search(r'play\s+(.+?)\s+(?:on|in)\s+' + spotify_keywords, song_text)
            if match1:
                song_text = match1.group(1).strip()
            else:
                # Pattern 2: "spotify play [song]" -> extract [song]
                match2 = re.search(r'(?:spotify|45|spot\s*if\s*i)\s+play\s+(.+)', song_text)
                if match2:
                    song_text = match2.group(1).strip()
                else:
                    # Pattern 3: Just remove common prefixes/suffixes
                    song_text = re.sub(r'^(?:play|spotify\s+play|45\s+play)\s+', '', song_text)
                    song_text = re.sub(r'\s+(?:on|in)\s+(?:spotify|45|spot\s*if\s*i).*$', '', song_text)
            
            # Clean up: remove "song", "track", trailing punctuation
            song_text = re.sub(r'^(?:play\s+)?(?:song|track)\s+', '', song_text)
            song_text = re.sub(r'[.,!?;:]+$', '', song_text).strip()
            
            # Remove any remaining "on 45" or similar patterns
            song_text = re.sub(r'\s+on\s+(?:45|spotify|spot\s*if\s*i).*$', '', song_text)
            song_text = re.sub(r'\s+in\s+(?:45|spotify|spot\s*if\s*i).*$', '', song_text)
            
            if song_text and len(song_text) > 0:
                entities["song_name"] = song_text
        
        return entities
    
    def _llm_classify(self, text: str) -> Dict[str, any]:
        """Use local LLM to classify intent (fallback)."""
        # Placeholder for LLM-based classification
        # Would use llama.cpp or similar for local inference
        return None

