#!/usr/bin/env python3
"""
Configuration management module.
"""

import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def load_config(config_path=None):
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file (default: agent/config.yaml)
        
    Returns:
        dict: Configuration dictionary
    """
    if config_path is None:
        config_path = Path(__file__).parent / 'config.yaml'
    
    # Default configuration
    default_config = {
        'wake_word': {
            'method': 'porcupine',  # 'porcupine', 'silero', or 'simple'
            'porcupine_access_key': '',  # Get from https://console.picovoice.ai/
            'keyword_path': None
        },
        'stt': {
            'model': 'base',  # 'tiny', 'base', 'small', 'medium', 'large'
        },
        'intent': {
            'use_fuzzy': True,
            'use_llm_fallback': False
        },
        'tts': {
            'method': 'pyttsx3',  # 'pyttsx3' or 'coqui'
            'rate': 150,
            'volume': 0.8,
            'coqui_model': 'tts_models/en/ljspeech/tacotron2-DDC'
        },
        'audio': {
            'sample_rate': 16000,
            'record_duration': 5
        }
    }
    
    # Try to load from file
    config_file = Path(config_path)
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                file_config = yaml.safe_load(f) or {}
                # Merge with defaults
                config = _merge_config(default_config, file_config)
                logger.info(f"Loaded configuration from {config_file}")
                return config
        except Exception as e:
            logger.warning(f"Failed to load config file: {e}, using defaults")
            return default_config
    else:
        logger.info("Config file not found, using defaults")
        # Create default config file
        try:
            with open(config_file, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)
            logger.info(f"Created default config file at {config_file}")
        except Exception as e:
            logger.warning(f"Could not create config file: {e}")
        
        return default_config

def _merge_config(default, user):
    """Recursively merge user config into default config."""
    result = default.copy()
    for key, value in user.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_config(result[key], value)
        else:
            result[key] = value
    return result

