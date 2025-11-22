#!/usr/bin/env python3
"""
Speech-to-Text module using local Whisper.
"""

import logging
import numpy as np
from pathlib import Path
import ssl
import urllib.request

# Patch urllib to handle SSL certificate issues BEFORE importing whisper
# This is needed because whisper downloads models using urllib
class UnverifiedHTTPSHandler(urllib.request.HTTPSHandler):
    """HTTPS handler with unverified SSL context for certificate issues."""
    def __init__(self, *args, **kwargs):
        # Create unverified SSL context
        context = ssl._create_unverified_context()
        super().__init__(*args, context=context, **kwargs)

# Install the patched handler globally
urllib.request.HTTPSHandler = UnverifiedHTTPSHandler
# Create and install a new opener with the patched handler
_opener = urllib.request.build_opener(UnverifiedHTTPSHandler())
urllib.request.install_opener(_opener)

logger = logging.getLogger(__name__)

class SpeechToText:
    """Converts speech audio to text using local Whisper model."""
    
    def __init__(self, config):
        """
        Initialize Whisper STT.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.model = None
        self.model_name = config.get('stt', {}).get('model', 'base')
        self._load_model()
    
    def _load_model(self):
        """Load Whisper model."""
        try:
            import whisper
            
            logger.info(f"Loading Whisper model: {self.model_name}")
            # SSL patching is done at module import time, so this should work
            self.model = whisper.load_model(self.model_name)
            
            logger.info("Whisper model loaded successfully")
        except ImportError:
            logger.error("Whisper not installed. Install with: pip install openai-whisper")
            raise
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def transcribe(self, audio):
        """
        Transcribe audio to text.
        
        Args:
            audio: Audio data (numpy array, float32, 16kHz)
            
        Returns:
            str: Transcribed text
        """
        if self.model is None:
            logger.error("Whisper model not loaded")
            return ""
        
        try:
            # Ensure audio is in correct format
            if isinstance(audio, np.ndarray):
                # Normalize if needed
                if audio.dtype != np.float32:
                    audio = audio.astype(np.float32)
                
                # Ensure mono and correct sample rate
                if len(audio.shape) > 1:
                    audio = audio[:, 0]  # Take first channel
                
                # Resample if needed (Whisper expects 16kHz)
                sample_rate = self.config.get('audio', {}).get('sample_rate', 16000)
                if sample_rate != 16000:
                    from scipy import signal
                    audio = signal.resample(audio, int(len(audio) * 16000 / sample_rate))
            
            logger.info("Transcribing audio...")
            result = self.model.transcribe(
                audio,
                language='en',
                task='transcribe',
                fp16=False  # Use fp32 for compatibility
            )
            
            text = result['text'].strip()
            logger.info(f"Transcription: {text}")
            return text
            
        except Exception as e:
            logger.error(f"Error during transcription: {e}", exc_info=True)
            return ""
    
    def cleanup(self):
        """Clean up resources."""
        # Whisper models are loaded in memory, cleanup if needed
        self.model = None

