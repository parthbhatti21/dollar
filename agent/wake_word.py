#!/usr/bin/env python3
"""
Wake word detection module.
Supports Picovoice Porcupine and Silero VAD + keyword spotting.
"""

import logging
import platform
import time
from pathlib import Path

logger = logging.getLogger(__name__)

class WakeWordDetector:
    """Detects wake words ('hey dollar', 'hello dollar', 'dollar jack') using local models."""
    
    def __init__(self, config):
        """
        Initialize wake word detector.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.detector = None
        self.audio_stream = None
        self.method = config.get('wake_word', {}).get('method', 'porcupine')
        
        # Try to initialize preferred method, fallback to others
        if self.method == 'porcupine':
            self._init_porcupine()
        elif self.method == 'silero':
            self._init_silero()
        else:
            logger.warning(f"Unknown wake word method: {self.method}, trying Porcupine...")
            self._init_porcupine()
    
    def _init_porcupine(self):
        """Initialize Picovoice Porcupine wake word engine."""
        try:
            import pvporcupine
            
            access_key = self.config.get('wake_word', {}).get('porcupine_access_key', '').strip()
            
            # Check if access key is empty or invalid (contains non-ASCII characters that aren't valid)
            if not access_key or len(access_key) < 10:  # Valid keys are typically long strings
                logger.warning("⚠️  No valid Porcupine access key provided. Using fallback simple VAD method.")
                logger.warning("⚠️  Simple VAD will detect ANY speech (not specific wake words).")
                logger.warning("⚠️  Get a free Porcupine key from https://console.picovoice.ai/ for proper wake word detection.")
                print("⚠️  WARNING: Using fallback wake word detection (will trigger on any speech)")
                self._init_simple_vad()
                return
            
            # Always auto-detect all keyword files in keywords directory
            # This allows multiple wake words to work simultaneously
            keyword_paths = self._get_keyword_paths()
            
            # If no keywords found via auto-detection, check config for a single keyword path (backward compatibility)
            if not keyword_paths:
                keyword_path = self.config.get('wake_word', {}).get('keyword_path', None)
                if keyword_path:
                    keyword_file = Path(keyword_path)
                    # If relative path, resolve relative to agent directory
                    if not keyword_file.is_absolute():
                        keyword_file = Path(__file__).parent / keyword_path
                    
                    if keyword_file.exists():
                        keyword_paths = [str(keyword_file.absolute())]
                        logger.info(f"Using single keyword file from config: {keyword_path}")
            
            # Create Porcupine instance with all detected keywords
            if keyword_paths:
                self.detector = pvporcupine.create(
                    access_key=access_key,
                    keyword_paths=keyword_paths
                )
                # Store keyword names for logging which one was detected
                self._keyword_names = {
                    i: Path(p).stem.replace('_en_mac_v3_0_0', '').replace('-', ' ').title()
                    for i, p in enumerate(keyword_paths)
                }
                logger.info(f"Using {len(keyword_paths)} custom keyword file(s): {', '.join([Path(p).name for p in keyword_paths])}")
                logger.info(f"Wake words enabled: {', '.join(self._keyword_names.values())}")
            else:
                # Use built-in keyword (fallback to "computer" since custom keywords aren't found)
                logger.warning("No custom keyword files found.")
                logger.info("Using built-in 'computer' keyword. To use custom wake words, add .ppn files to the keywords directory.")
                self.detector = pvporcupine.create(
                    access_key=access_key,
                    keywords=['computer']  # Built-in keyword as fallback
                )
                logger.info("Using built-in 'computer' keyword (say 'computer' to wake)")
            
            # Initialize audio stream with optimized settings
            import pyaudio
            self.audio = pyaudio.PyAudio()
            # Use larger buffer to prevent overflow (especially with heavy Whisper models)
            # frames_per_buffer should be a multiple of Porcupine's frame_length for best performance
            # Using 2x frame_length gives more buffer room to prevent overflows
            buffer_multiplier = 2  # Increase buffer to prevent overflows
            frames_per_buffer = self.detector.frame_length * buffer_multiplier
            try:
                self.audio_stream = self.audio.open(
                    rate=self.detector.sample_rate,
                    channels=1,
                    format=pyaudio.paInt16,
                    input=True,
                    frames_per_buffer=frames_per_buffer,
                    stream_callback=None,  # No callback for lower latency
                    start=False  # Start manually for better control
                )
                self.audio_stream.start_stream()
                logger.info("Porcupine wake word detector initialized")
                self.method = 'porcupine'
            except OSError as e:
                # Microphone permission denied or not available
                error_msg = str(e).lower()
                if 'permission' in error_msg or 'denied' in error_msg or 'input device' in error_msg:
                    logger.error("Microphone permission denied. Please grant microphone access in System Settings > Privacy & Security > Microphone")
                    raise PermissionError("Microphone access denied. Please grant microphone permissions in System Settings.")
                else:
                    logger.error(f"Failed to open audio stream: {e}")
                    raise
            
        except ImportError:
            logger.debug("pvporcupine not available, falling back to simple VAD")
            self._init_simple_vad()
        except Exception as e:
            # Check if it's an access key error
            error_str = str(e).lower()
            if 'accesskey' in error_str or 'access key' in error_str or '0000006f' in error_str:
                logger.debug("Invalid Porcupine access key. Using fallback method.")
            else:
                logger.debug(f"Porcupine initialization failed: {e}")
            self._init_simple_vad()
    
    def _init_silero(self):
        """Initialize Silero VAD + keyword spotting."""
        try:
            import torch
            import torchaudio
            from silero_vad import load_silero_vad
            
            self.vad_model, self.vad_utils = load_silero_vad()
            self.sample_rate = 16000
            
            # Initialize audio stream
            import sounddevice as sd
            self.audio_stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32',
                blocksize=512
            )
            self.audio_stream.start()
            
            # Simple keyword matching for all wake words
            self.keyword_patterns = [
                'dollar jack', 'hey dollar', 'hello dollar', 'dollar'
            ]
            
            logger.info("Silero VAD wake word detector initialized")
            self.method = 'silero'
            
        except ImportError:
            logger.warning("Silero VAD not available, falling back to simple VAD")
            self._init_simple_vad()
        except Exception as e:
            logger.error(f"Failed to initialize Silero: {e}")
            self._init_simple_vad()
    
    def _init_simple_vad(self):
        """Fallback: Simple VAD with basic keyword matching."""
        logger.info("Initializing simple VAD fallback...")
        import sounddevice as sd
        
        self.sample_rate = 16000
        self.audio_stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32',
            blocksize=1600  # 100ms chunks
        )
        self.audio_stream.start()
        
        # Simple energy-based VAD - lower threshold for better sensitivity
        # Adjust this if you get too many false positives (increase) or miss detections (decrease)
        self.energy_threshold = 0.005  # Lowered from 0.01 for better sensitivity
        self.keyword_patterns = ['dollar jack', 'hey dollar', 'hello dollar', 'dollar']
        
        logger.info("Simple VAD wake word detector initialized")
        logger.info(f"Energy threshold: {self.energy_threshold} (lower = more sensitive)")
        print("⚠️  Using Simple VAD: Will detect ANY speech, not just wake words")
        self.method = 'simple'
    
    def _get_keyword_paths(self):
        """Get paths to all custom keyword files."""
        keyword_dir = Path(__file__).parent / 'keywords'
        keyword_dir.mkdir(exist_ok=True)
        
        # List of all wake word keyword files
        keyword_files = [
            'Dollar-jack_en_mac_v3_0_0.ppn',      # "dollar jack"
            'Hey-dollar_en_mac_v3_0_0.ppn',       # "hey dollar"
            'Hello-Dollar_en_mac_v3_0_0.ppn'      # "hello dollar"
        ]
        
        # Return list of existing keyword file paths
        keyword_paths = []
        for filename in keyword_files:
            keyword_path = keyword_dir / filename
            if keyword_path.exists():
                keyword_paths.append(str(keyword_path.absolute()))
                logger.info(f"Found keyword file: {filename}")
            else:
                logger.debug(f"Keyword file not found: {filename}")
        
        return keyword_paths
    
    def detect(self):
        """
        Check if wake word is detected (non-blocking).
        
        Returns:
            bool: True if wake word detected
        """
        if not self.audio_stream:
            return False
        
        try:
            if self.method == 'porcupine':
                return self._detect_porcupine()
            elif self.method == 'silero':
                return self._detect_silero()
            else:
                return self._detect_simple()
        except Exception as e:
            # Only log errors occasionally to avoid spam
            import time
            if not hasattr(self, '_last_error_log') or time.time() - self._last_error_log > 5:
                logger.error(f"Error in wake word detection: {e}")
                self._last_error_log = time.time()
            return False
    
    def _detect_porcupine(self):
        """Detect using Porcupine - optimized for speed."""
        import struct
        
        try:
            # Read exactly frame_length frames (non-blocking, exception_on_overflow=False)
            # PyAudio returns bytes, with paInt16 format: 2 bytes per sample
            pcm_bytes = self.audio_stream.read(
                self.detector.frame_length, 
                exception_on_overflow=False
            )
            
            # Fast path: if we got exactly what we need, process directly
            expected_bytes = self.detector.frame_length * 2
            if len(pcm_bytes) == expected_bytes:
                # Direct unpack without slicing - fastest path
                pcm = list(struct.unpack_from('<' + 'h' * self.detector.frame_length, pcm_bytes))
            elif len(pcm_bytes) > expected_bytes:
                # Got more than expected (shouldn't happen, but handle it)
                pcm = list(struct.unpack_from('<' + 'h' * self.detector.frame_length, pcm_bytes[:expected_bytes]))
            else:
                # Got less than expected - return False (incomplete frame)
                return False
            
            # Process with Porcupine (this is the actual detection)
            # Returns -1 if no keyword detected, or index (0, 1, 2...) if a keyword is detected
            keyword_index = self.detector.process(pcm)
            if keyword_index >= 0:
                # Log which wake word was detected (for debugging)
                if hasattr(self, '_keyword_names'):
                    keyword_name = self._keyword_names.get(keyword_index, f"keyword_{keyword_index}")
                    logger.info(f"Wake word detected: {keyword_name} (index: {keyword_index})")
                else:
                    logger.info(f"Wake word detected (index: {keyword_index})")
                return True
            return False
            
        except Exception as e:
            # Silently handle read errors (buffer underflow/overflow)
            # This is normal when audio stream isn't ready
            return False
    
    def _detect_silero(self):
        """Detect using Silero VAD + keyword matching."""
        import numpy as np
        
        audio_chunk, _ = self.audio_stream.read(512)
        audio_chunk = audio_chunk.flatten()
        
        # Run VAD
        speech_prob = self.vad_model(torch.from_numpy(audio_chunk), self.sample_rate).item()
        
        if speech_prob > 0.5:  # Speech detected
            # In a real implementation, you'd run STT here and match keywords
            # For now, this is a simplified version
            return False  # Would need full STT pipeline
        
        return False
    
    def _detect_simple(self):
        """
        Simple energy-based detection.
        
        NOTE: This is a basic fallback that only detects speech activity,
        not the specific keyword. For actual wake word detection, use Porcupine.
        This method will trigger on any speech, which may cause false positives.
        """
        import numpy as np
        
        try:
            # sounddevice InputStream.read() returns (audio_data, overflowed)
            # It doesn't accept exception_on_overflow parameter (that's for PyAudio)
            audio_chunk, overflowed = self.audio_stream.read(1600)
            if overflowed:
                # Only log as debug to reduce console noise - overflows are common with heavy models
                logger.debug("Audio buffer overflowed (this is normal with heavy Whisper models)")
            
            audio_chunk = audio_chunk.flatten()
            
            # Calculate energy
            energy = np.mean(audio_chunk ** 2)
            
            # Simple threshold - if energy is high, assume speech
            # WARNING: This will trigger on ANY speech, not just "hey dollar"
            # For production use, Porcupine is strongly recommended
            if energy > self.energy_threshold:
                logger.debug(f"Simple VAD detected speech (energy: {energy:.6f}, threshold: {self.energy_threshold})")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error in simple detection: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources."""
        if self.audio_stream:
            if hasattr(self.audio_stream, 'stop'):
                self.audio_stream.stop()
            if hasattr(self.audio_stream, 'close'):
                self.audio_stream.close()
        
        if hasattr(self, 'audio') and self.audio:
            self.audio.terminate()
        
        if hasattr(self, 'detector') and self.detector:
            self.detector.delete()

