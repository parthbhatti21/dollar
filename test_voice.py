#!/usr/bin/env python3
"""Quick test script to verify TTS and wake word detection."""

import sys
sys.path.insert(0, 'agent')

from config import load_config
from voice_output import VoiceOutput
from wake_word import WakeWordDetector

print("Testing Dollar Assistant components...\n")

config = load_config()

# Test TTS
print("1. Testing TTS...")
try:
    voice = VoiceOutput(config)
    voice.speak("Testing voice output. Can you hear me?")
    print("✓ TTS working")
except Exception as e:
    print(f"✗ TTS failed: {e}")
    import traceback
    traceback.print_exc()

# Test Wake Word
print("\n2. Testing Wake Word Detection...")
try:
    wake_word = WakeWordDetector(config)
    print(f"✓ Wake word detector initialized (method: {wake_word.method})")
    print(f"  Audio stream: {wake_word.audio_stream is not None}")
    
    if wake_word.method == 'porcupine':
        print(f"  Porcupine detector: {wake_word.detector is not None}")
        if wake_word.detector:
            print(f"  Frame length: {wake_word.detector.frame_length}")
            print(f"  Sample rate: {wake_word.detector.sample_rate}")
    
    print("\n  Listening for wake word... (say 'dollar jack', press Ctrl+C to stop)")
    import time
    detection_count = 0
    while True:
        if wake_word.detect():
            detection_count += 1
            print(f"  ✓ Wake word detected! (count: {detection_count})")
        time.sleep(0.01)
except KeyboardInterrupt:
    print("\n  Test stopped by user")
except Exception as e:
    print(f"✗ Wake word test failed: {e}")
    import traceback
    traceback.print_exc()

print("\nTest complete!")

