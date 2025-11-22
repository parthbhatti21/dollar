#!/usr/bin/env python3
"""
Voice output module using local TTS.
Supports pyttsx3 and Coqui TTS.
"""

import logging
import platform

logger = logging.getLogger(__name__)

class VoiceOutput:
    """Text-to-Speech output using local engines."""
    
    def __init__(self, config):
        """
        Initialize TTS engine.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.engine = None
        self.method = config.get('tts', {}).get('method', 'pyttsx3')
        self._init_engine()
    
    def _init_engine(self):
        """Initialize TTS engine based on config."""
        if self.method == 'pyttsx3':
            self._init_pyttsx3()
        elif self.method == 'coqui':
            self._init_coqui()
        else:
            logger.warning(f"Unknown TTS method: {self.method}, using pyttsx3")
            self._init_pyttsx3()
    
    def _init_pyttsx3(self):
        """Initialize pyttsx3 TTS engine."""
        try:
            import pyttsx3
            
            self.engine = pyttsx3.init()
            
            # Configure voice settings
            voices = self.engine.getProperty('voices')
            if voices:
                # Prefer female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
                    elif 'samantha' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            
            # Set speech rate and volume
            rate = self.config.get('tts', {}).get('rate', 150)
            volume = self.config.get('tts', {}).get('volume', 0.8)
            
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)
            
            logger.info("pyttsx3 TTS engine initialized")
            self.method = 'pyttsx3'
            
        except ImportError:
            logger.error("pyttsx3 not installed. Install with: pip install pyttsx3")
            self.engine = None
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3: {e}")
            self.engine = None
    
    def _init_coqui(self):
        """Initialize Coqui TTS engine."""
        try:
            from TTS.api import TTS
            
            model_name = self.config.get('tts', {}).get('coqui_model', 'tts_models/en/ljspeech/tacotron2-DDC')
            self.tts = TTS(model_name=model_name, gpu=False)
            
            logger.info("Coqui TTS engine initialized")
            self.method = 'coqui'
            
        except ImportError:
            logger.warning("Coqui TTS not available, falling back to pyttsx3")
            self._init_pyttsx3()
        except Exception as e:
            logger.error(f"Failed to initialize Coqui TTS: {e}")
            self._init_pyttsx3()
    
    def speak(self, text: str):
        """
        Speak text using TTS.
        
        Args:
            text: Text to speak
        """
        if not text:
            return
        
        if not self.engine and self.method == 'pyttsx3':
            logger.error("TTS engine not initialized")
            return
        
        try:
            if self.method == 'pyttsx3':
                self.engine.say(text)
                self.engine.runAndWait()
            
            elif self.method == 'coqui':
                import tempfile
                import os
                import sounddevice as sd
                import soundfile as sf
                
                # Generate speech
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    self.tts.tts_to_file(text=text, file_path=tmp_file.name)
                    
                    # Play audio
                    data, sample_rate = sf.read(tmp_file.name)
                    sd.play(data, sample_rate)
                    sd.wait()
                    
                    # Cleanup
                    os.unlink(tmp_file.name)
            
            logger.debug(f"Spoke: {text}")
        
        except Exception as e:
            logger.error(f"Error speaking text: {e}", exc_info=True)
    
    def cleanup(self):
        """Clean up resources."""
        if self.engine and hasattr(self.engine, 'stop'):
            self.engine.stop()

