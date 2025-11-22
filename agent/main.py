#!/usr/bin/env python3
"""
Main entry point for the Dollar AI Voice Assistant.
Runs continuously, listening for wake word and executing commands.
"""

import time
import signal
import sys
import logging
from pathlib import Path

from wake_word import WakeWordDetector
from speech_to_text import SpeechToText
from intent_classifier import IntentClassifier
from command_router import CommandRouter
from voice_output import VoiceOutput
from visual_indicator import VisualIndicator
from config import load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log'),
        logging.StreamHandler(sys.stdout)  # Ensure output goes to stdout
    ]
)
logger = logging.getLogger(__name__)

class DollarAssistant:
    """Main assistant class that orchestrates all components."""
    
    def __init__(self):
        """Initialize all components."""
        self.config = load_config()
        self.running = True
        
        # Initialize components
        logger.info("Initializing Dollar Assistant...")
        self.wake_word = WakeWordDetector(self.config)
        self.stt = SpeechToText(self.config)
        self.classifier = IntentClassifier(self.config)
        self.router = CommandRouter(self.config)
        self.voice = VoiceOutput(self.config)
        self.visual = VisualIndicator()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("Dollar Assistant initialized successfully")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info("Received shutdown signal, stopping assistant...")
        self.running = False
    
    def record_user_speech(self, duration=3):
        """
        Record user speech after wake word detection.
        
        Args:
            duration: Maximum recording duration in seconds
            
        Returns:
            Audio data (numpy array or bytes)
        """
        import sounddevice as sd
        import numpy as np
        
        sample_rate = self.config.get('audio', {}).get('sample_rate', 16000)
        logger.info(f"Recording for {duration} seconds...")
        
        # Record audio
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()  # Wait until recording is finished
        
        # Trim silence at both ends for faster processing
        audio_flat = audio.flatten()
        
        # Simple silence detection
        threshold = 0.01
        non_silent = np.where(np.abs(audio_flat) > threshold)[0]
        
        if len(non_silent) > 0:
            # Skip minimal initial silence (first 0.1 seconds) to avoid wake word echo
            # Reduced from 0.3s since we're not doing TTS before recording
            skip_samples = int(0.1 * sample_rate)  # Skip first 100ms
            start_idx = max(0, min(non_silent[0], skip_samples))
            
            # Trim end - find where audio actually ends
            # Keep some padding after last sound
            end_idx = min(non_silent[-1] + int(0.5 * sample_rate), len(audio_flat))
            
            # Extract the relevant portion
            audio_flat = audio_flat[start_idx:end_idx]
        else:
            # If no sound detected, still skip minimal initial portion
            skip_samples = int(0.1 * sample_rate)
            audio_flat = audio_flat[skip_samples:]
        
        return audio_flat
    
    def run(self):
        """Main loop - runs continuously until stopped."""
        logger.info("Starting Dollar Assistant main loop...")
        
        # Test TTS on startup
        try:
            logger.info("Testing TTS...")
            self.voice.speak("Dollar assistant is ready.")
            logger.info("TTS test successful")
        except Exception as e:
            logger.error(f"TTS test failed: {e}", exc_info=True)
            logger.warning("Continuing without TTS - check logs for errors")
        
        logger.info(f"Wake word method: {self.wake_word.method}")
        logger.info("Listening for wake word...")
        
        while self.running:
            try:
                # Check for wake word (non-blocking, low CPU)
                try:
                    wake_detected = self.wake_word.detect()
                except Exception as e:
                    logger.error(f"Error in wake word detection: {e}", exc_info=True)
                    wake_detected = False
                
                if wake_detected:
                    logger.info("Wake word detected!")
                    
                    # Show visual indicator - listening
                    self.visual.show_listening()
                    
                    # Pause music if playing (to avoid interference with voice recognition)
                    music_was_playing = self.router.os_commands._pause_music_if_playing()
                    
                    # Start recording immediately (no delay, no TTS acknowledgment)
                    # This allows instant response to user commands
                    try:
                        logger.info("Recording user command immediately...")
                        audio = self.record_user_speech(
                            duration=self.config.get('audio', {}).get('record_duration', 3)
                        )
                        logger.info(f"Recorded {len(audio)} samples")
                        
                        # Acknowledge after recording (non-blocking, quick)
                        # This way user knows we heard them, but we don't delay listening
                        try:
                            # Use a shorter, faster acknowledgment
                            self.voice.speak("Listening.")
                        except Exception as e:
                            logger.debug(f"Could not speak acknowledgment: {e}")
                    except Exception as e:
                        logger.error(f"Error recording speech: {e}", exc_info=True)
                        # Resume music if it was playing
                        if music_was_playing:
                            self.router.os_commands._resume_music_if_paused()
                        self.visual.show_ready()
                        continue  # Skip this iteration if recording failed
                    
                    # Show processing indicator
                    self.visual.show_processing()
                    
                    # Convert speech to text
                    try:
                        logger.info("Transcribing speech...")
                        text = self.stt.transcribe(audio)
                        logger.info(f"User said: {text}")
                        
                        if not text or text.strip() == "":
                            logger.warning("No speech detected, skipping...")
                            # Resume music if it was playing
                            if music_was_playing:
                                self.router.os_commands._resume_music_if_paused()
                            self.visual.show_ready()
                            continue
                    except Exception as e:
                        logger.error(f"Error transcribing speech: {e}", exc_info=True)
                        # Resume music if it was playing
                        if music_was_playing:
                            self.router.os_commands._resume_music_if_paused()
                        self.visual.show_ready()
                        continue  # Skip if transcription failed
                    
                    # Filter out wake word phrases to prevent false commands
                    text_lower = text.lower().strip()
                    wake_word_phrases = [
                        "dollar jack", "dollar", "jack", "hey dollar", "hey dollar jack",
                        "dollar jack", "dollar jack", "dollar jack"
                    ]
                    
                    # Check if the transcription is just the wake word or very similar
                    is_wake_word_only = False
                    for phrase in wake_word_phrases:
                        # Remove punctuation and compare
                        text_clean = text_lower.replace(".", "").replace(",", "").replace("!", "").replace("?", "")
                        if phrase in text_clean or text_clean in phrase:
                            # If the text is very short and matches wake word, ignore it
                            if len(text_clean.split()) <= 3:
                                is_wake_word_only = True
                                logger.info(f"Ignoring wake word phrase in transcription: {text}")
                                break
                    
                    if is_wake_word_only:
                        logger.info("Transcription was just the wake word, ignoring command")
                        # Resume music if it was playing
                        if music_was_playing:
                            self.router.os_commands._resume_music_if_paused()
                        self.visual.show_ready()
                        continue
                    
                    # Check for stop command
                    if any(phrase in text.lower() for phrase in ["stop the agent", "stop dollar", "shut down"]):
                        logger.info("Stop command received")
                        self.voice.speak("Shutting down. Goodbye.")
                        self.running = False
                        break
                    
                    # Classify intent
                    intent = self.classifier.get_intent(text)
                    logger.info(f"Detected intent: {intent}")
                    
                    # Check if the command is a media control command (don't resume if user wants to pause/stop)
                    intent_name = intent.get('intent', '')
                    is_media_control = intent_name in ['media_pause', 'media_stop', 'spotify_play']
                    
                    # Execute command
                    result = self.router.execute(intent, text)
                    
                    # Provide feedback
                    if result.get('success'):
                        feedback = result.get('message', 'Done.')
                        logger.info(f"Command executed: {feedback}")
                        self.voice.speak(feedback)
                    else:
                        error_msg = result.get('error', 'Sorry, I could not execute that command.')
                        logger.warning(f"Command failed: {error_msg}")
                        self.voice.speak(error_msg)
                    
                    # Resume music if it was playing and the command wasn't a media control command
                    if music_was_playing and not is_media_control:
                        self.router.os_commands._resume_music_if_paused()
                    
                    # Show ready state after command completes
                    self.visual.show_ready()
                
                # Visual indicator updates are handled via notifications
                # No need to call update() for notification-based indicator
                
                # Minimal sleep for faster wake word detection (10ms = 100 checks/sec)
                time.sleep(0.01)
                
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                time.sleep(1)  # Brief pause before retrying
        
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up resources...")
        self.wake_word.cleanup()
        self.stt.cleanup()
        self.voice.cleanup()
        self.visual.cleanup()
        logger.info("Cleanup complete")


def main():
    """Entry point."""
    assistant = DollarAssistant()
    assistant.run()


if __name__ == "__main__":
    main()

