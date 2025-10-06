"""
Audio Controller for SITH

Implements audio playback control.
"""

import time
import logging
from typing import Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from sith_core.hal import SoundInterface

logger = logging.getLogger(__name__)


class AudioController(SoundInterface):
    """Audio controller implementation."""
    
    def __init__(self, device: str = 'default', volume: int = 100):
        super().__init__()
        self.device = device
        self.volume = volume
        self.current_sound = None
        self.simulation_mode = True  # Always in simulation mode for now
    
    def initialize(self) -> bool:
        """Initialize audio controller."""
        self.initialized = True
        logger.info(f"Audio controller initialized (device: {self.device})")
        return True
    
    def shutdown(self) -> None:
        """Shutdown audio controller."""
        self.initialized = False
        logger.info("Audio controller shutdown")
    
    def is_available(self) -> bool:
        """Check if controller is available."""
        return self.initialized
    
    def play_sound(self, sound_id: int) -> None:
        """Play sound by ID."""
        self.current_sound = sound_id
        logger.info(f"Playing sound: {sound_id}")
    
    def play_sound_file(self, filename: str) -> None:
        """Play sound from file."""
        self.current_sound = filename
        logger.info(f"Playing sound file: {filename}")
    
    def stop_sound(self) -> None:
        """Stop current sound."""
        self.current_sound = None
        logger.info("Sound stopped")
    
    def set_volume(self, volume: int) -> None:
        """Set volume (0-100)."""
        self.volume = max(0, min(100, volume))
        logger.debug(f"Volume: {self.volume}")
    
    def play_random_sound(self, category: str = "random") -> None:
        """Play random sound from category."""
        logger.info(f"Playing random sound: {category}")
    
    def get_status(self) -> dict:
        """Get controller status."""
        return {
            'name': 'audio',
            'device': self.device,
            'volume': self.volume,
            'current_sound': self.current_sound,
            'available': self.is_available(),
            'simulation_mode': self.simulation_mode
        }