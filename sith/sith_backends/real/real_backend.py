"""
Real Hardware Backend for SITH

Implements hardware control using actual devices like Sabertooth, PCA9685, etc.
"""

import logging
from typing import List, Optional, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from sith_backends.base import BackendBase
from sith_core.hal import MotorInterface, ServoInterface, LEDInterface, SoundInterface
from .sabertooth_driver import SabertoothDriver
from .pca9685_controller import PCA9685Controller
from .neopixel_controller import NeoPixelController
from .audio_controller import AudioController

logger = logging.getLogger(__name__)


class RealBackend(BackendBase):
    """Real hardware backend implementation."""
    
    def __init__(self, config: Optional[dict] = None):
        super().__init__("real")
        self.config = config or {}
        self.drivers = {}
        self.interfaces = {}
    
    def initialize(self) -> bool:
        """Initialize all hardware drivers."""
        try:
            # Initialize Sabertooth motor driver
            if self.config.get('enable_motors', True):
                sabertooth_config = self.config.get('sabertooth', {})
                self.drivers['sabertooth'] = SabertoothDriver(
                    port=sabertooth_config.get('port', '/dev/ttyUSB0'),
                    baudrate=sabertooth_config.get('baudrate', 2400)
                )
                if self.drivers['sabertooth'].initialize():
                    self.interfaces['motors'] = self.drivers['sabertooth']
                else:
                    logger.warning("Failed to initialize Sabertooth driver")
            
            # Initialize PCA9685 servo controller
            if self.config.get('enable_servos', True):
                pca9685_config = self.config.get('pca9685', {})
                self.drivers['pca9685'] = PCA9685Controller(
                    address=pca9685_config.get('address', 0x40),
                    frequency=pca9685_config.get('frequency', 50)
                )
                if self.drivers['pca9685'].initialize():
                    self.interfaces['servos'] = self.drivers['pca9685']
                else:
                    logger.warning("Failed to initialize PCA9685 controller")
            
            # Initialize NeoPixel LED controller
            if self.config.get('enable_leds', True):
                neopixel_config = self.config.get('neopixel', {})
                self.drivers['neopixel'] = NeoPixelController(
                    pin=neopixel_config.get('pin', 18),
                    num_pixels=neopixel_config.get('num_pixels', 144),
                    pixel_order=neopixel_config.get('pixel_order', 'GRB')
                )
                if self.drivers['neopixel'].initialize():
                    self.interfaces['leds'] = self.drivers['neopixel']
                else:
                    logger.warning("Failed to initialize NeoPixel controller")
            
            # Initialize audio controller
            if self.config.get('enable_audio', True):
                audio_config = self.config.get('audio', {})
                self.drivers['audio'] = AudioController(
                    device=audio_config.get('device', 'default'),
                    volume=audio_config.get('volume', 100)
                )
                if self.drivers['audio'].initialize():
                    self.interfaces['sound'] = self.drivers['audio']
                else:
                    logger.warning("Failed to initialize audio controller")
            
            self.initialized = True
            logger.info(f"Real backend initialized with {len(self.interfaces)} interfaces")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize real backend: {e}")
            return False
    
    def shutdown(self) -> None:
        """Shutdown all hardware drivers."""
        for driver in self.drivers.values():
            try:
                driver.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down driver: {e}")
        
        self.drivers.clear()
        self.interfaces.clear()
        self.initialized = False
        logger.info("Real backend shutdown complete")
    
    def get_interfaces(self) -> List[Any]:
        """Get list of hardware interfaces."""
        return list(self.interfaces.values())
    
    def is_available(self) -> bool:
        """Check if backend is available."""
        return self.initialized and len(self.interfaces) > 0
    
    def get_driver(self, name: str):
        """Get a specific driver by name."""
        return self.drivers.get(name)
    
    def get_interface(self, name: str):
        """Get a specific interface by name."""
        return self.interfaces.get(name)