#!/usr/bin/env python3

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

file_handler = logging.FileHandler('agent.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.WARNING)
console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

for module_name in ['wake_word', 'speech_to_text', 'intent_classifier', 'command_router', 
                     'os_commands', 'voice_output', 'visual_indicator', 'config']:
    module_logger = logging.getLogger(module_name)
    module_logger.setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

class DollarAssistant:
    
    def __init__(self, enable_signal_handlers=True, wake_word_callback=None):
        self.config = load_config()
        self.running = True
        self.wake_word_callback = wake_word_callback
        logger.debug("Initializing Dollar Assistant...")
        self.wake_word = WakeWordDetector(self.config)
        self.stt = SpeechToText(self.config)
        self.classifier = IntentClassifier(self.config)
        self.router = CommandRouter(self.config)
        self.voice = VoiceOutput(self.config)
        self.visual = VisualIndicator()
        if enable_signal_handlers:
            try:
                signal.signal(signal.SIGINT, self._signal_handler)
                signal.signal(signal.SIGTERM, self._signal_handler)
            except ValueError:
                logger.debug("Signal handlers not set (not in main thread)")
        logger.debug("Dollar Assistant initialized successfully")
    
    def _signal_handler(self, signum, frame):
        logger.debug("Received shutdown signal, stopping assistant...")
        self.running = False
    
    def record_user_speech(self, duration=5):
        import sounddevice as sd
        import numpy as np
        sample_rate = self.config.get('audio', {}).get('sample_rate', 16000)
        logger.debug(f"Recording for {duration} seconds...")
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()
        audio_flat = audio.flatten()
        threshold = 0.01
        non_silent = np.where(np.abs(audio_flat) > threshold)[0]
        if len(non_silent) > 0:
            skip_samples = int(0.1 * sample_rate)
            start_idx = max(0, min(non_silent[0], skip_samples))
            end_idx = min(non_silent[-1] + int(0.5 * sample_rate), len(audio_flat))
            audio_flat = audio_flat[start_idx:end_idx]
        else:
            skip_samples = int(0.1 * sample_rate)
            audio_flat = audio_flat[skip_samples:]
        return audio_flat
    
    def run(self):
        logger.debug("Starting Dollar Assistant main loop...")
        try:
            logger.debug("Testing TTS...")
            self.voice.speak("Dollar assistant is ready.")
            logger.debug("TTS test successful")
        except Exception as e:
            logger.error(f"TTS test failed: {e}", exc_info=True)
            logger.warning("Continuing without TTS - check logs for errors")
        logger.debug(f"Wake word method: {self.wake_word.method}")
        logger.debug(f"Audio stream exists: {self.wake_word.audio_stream is not None}")
        if self.wake_word.audio_stream and hasattr(self.wake_word.audio_stream, 'is_active'):
            logger.debug(f"Audio stream active: {self.wake_word.audio_stream.is_active()}")
        print("✅ Dollar Assistant is working")
        print(f"🔧 Wake word method: {self.wake_word.method}")
        print("👂 Listening for wake word...")
        if not self.wake_word.audio_stream:
            print("⚠️  WARNING: Audio stream is None - wake word detection will not work!")
            logger.error("Audio stream is None - wake word detection disabled")
        elif self.wake_word.method == 'simple':
            print("⚠️  NOTE: Using Simple VAD - will detect ANY speech (not specific wake words)")
            print("💡 Tip: Get a Porcupine key from https://console.picovoice.ai/ for proper wake word detection")
        while self.running:
            try:
                try:
                    wake_detected = self.wake_word.detect()
                except Exception as e:
                    logger.error(f"Error in wake word detection: {e}", exc_info=True)
                    wake_detected = False
                if wake_detected:
                    print("🎤 Wake word detected - listening...")
                    logger.debug("Wake word detected!")
                    if self.wake_word_callback:
                        try:
                            self.wake_word_callback()
                        except Exception as e:
                            logger.debug(f"Error in wake word callback: {e}")
                    self.visual.show_listening()
                    music_was_playing = self.router.os_commands._pause_music_if_playing()
                    try:
                        logger.debug("Recording user command immediately...")
                        audio = self.record_user_speech(
                            duration=self.config.get('audio', {}).get('record_duration', 3)
                        )
                        logger.debug(f"Recorded {len(audio)} samples")
                        try:
                            self.voice.speak("Listening.")
                        except Exception as e:
                            logger.debug(f"Could not speak acknowledgment: {e}")
                    except Exception as e:
                        logger.error(f"Error recording speech: {e}", exc_info=True)
                        if music_was_playing:
                            self.router.os_commands._resume_music_if_paused()
                        self.visual.show_ready()
                        continue
                    self.visual.show_processing()
                    try:
                        logger.debug("Transcribing speech...")
                        text = self.stt.transcribe(audio)
                        logger.debug(f"User said: {text}")
                        if not text or text.strip() == "":
                            logger.debug("No speech detected, skipping...")
                            if music_was_playing:
                                self.router.os_commands._resume_music_if_paused()
                            self.visual.show_ready()
                            continue
                    except Exception as e:
                        logger.error(f"Error transcribing speech: {e}", exc_info=True)
                        if music_was_playing:
                            self.router.os_commands._resume_music_if_paused()
                        self.visual.show_ready()
                        continue
                    text_lower = text.lower().strip()
                    wake_word_phrases = [
                        "dollar jack", "hey dollar", "hello dollar",
                        "dollar", "jack", "hey", "hello"
                    ]
                    is_wake_word_only = False
                    for phrase in wake_word_phrases:
                        text_clean = text_lower.replace(".", "").replace(",", "").replace("!", "").replace("?", "")
                        if phrase in text_clean or text_clean in phrase:
                            if len(text_clean.split()) <= 3:
                                is_wake_word_only = True
                                logger.debug(f"Ignoring wake word phrase in transcription: {text}")
                                break
                    if is_wake_word_only:
                        logger.debug("Transcription was just the wake word, ignoring command")
                        if music_was_playing:
                            self.router.os_commands._resume_music_if_paused()
                        self.visual.show_ready()
                        continue
                    if any(phrase in text.lower() for phrase in ["stop the agent", "stop dollar", "shut down"]):
                        logger.debug("Stop command received")
                        print("🛑 Shutting down...")
                        self.voice.speak("Shutting down. Goodbye.")
                        self.running = False
                        break
                    intent = self.classifier.get_intent(text)
                    logger.debug(f"Detected intent: {intent}")
                    intent_name = intent.get('intent', '')
                    is_media_control = intent_name in ['media_pause', 'media_stop', 'spotify_play']
                    result = self.router.execute(intent, text)
                    if result.get('success'):
                        feedback = result.get('message', 'Done.')
                        logger.debug(f"Command executed: {feedback}")
                        self.voice.speak(feedback)
                    else:
                        error_msg = result.get('error', 'Sorry, I could not execute that command.')
                        logger.warning(f"Command failed: {error_msg}")
                        self.voice.speak(error_msg)
                    if music_was_playing and not is_media_control:
                        self.router.os_commands._resume_music_if_paused()
                    self.visual.show_ready()
                    print("👂 Listening for wake word...")
                time.sleep(0.01)
                if not hasattr(self, '_last_heartbeat') or time.time() - self._last_heartbeat > 30:
                    logger.debug("Wake word detection loop running (heartbeat)")
                    self._last_heartbeat = time.time()
            except KeyboardInterrupt:
                logger.debug("Keyboard interrupt received")
                print("\n🛑 Shutting down...")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                time.sleep(1)
        self.cleanup()
    
    def cleanup(self):
        logger.debug("Cleaning up resources...")
        self.wake_word.cleanup()
        self.stt.cleanup()
        self.voice.cleanup()
        self.visual.cleanup()
        logger.debug("Cleanup complete")


def main():
    assistant = DollarAssistant()
    assistant.run()


if __name__ == "__main__":
    main()

