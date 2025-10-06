"""
NeoPixel Controller for SITH

Implements LED control for WS2812/NeoPixel strips.
"""

import time
import logging
from typing import List, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from sith_core.hal import LEDInterface

logger = logging.getLogger(__name__)


class NeoPixelController(LEDInterface):
    """NeoPixel LED controller implementation."""
    
    def __init__(self, pin: int = 18, num_pixels: int = 144, pixel_order: str = 'GRB'):
        super().__init__(num_pixels)
        self.pin = pin
        self.pixel_order = pixel_order
        self.pixels = [(0, 0, 0)] * num_pixels
        self.simulation_mode = True  # Always in simulation mode for now
    
    def initialize(self) -> bool:
        """Initialize NeoPixel controller."""
        self.initialized = True
        logger.info(f"NeoPixel controller initialized ({self.num_pixels} pixels)")
        return True
    
    def shutdown(self) -> None:
        """Shutdown NeoPixel controller."""
        self.initialized = False
        logger.info("NeoPixel controller shutdown")
    
    def is_available(self) -> bool:
        """Check if controller is available."""
        return self.initialized
    
    def set_pixel_color(self, pixel: int, r: int, g: int, b: int) -> None:
        """Set individual pixel color (0-255)."""
        if 0 <= pixel < self.num_pixels:
            self.pixels[pixel] = (r, g, b)
            logger.debug(f"Pixel {pixel}: RGB({r},{g},{b})")
    
    def set_all_pixels(self, r: int, g: int, b: int) -> None:
        """Set all pixels to same color."""
        for i in range(self.num_pixels):
            self.pixels[i] = (r, g, b)
        logger.debug(f"All pixels: RGB({r},{g},{b})")
    
    def clear_pixels(self) -> None:
        """Turn off all pixels."""
        self.set_all_pixels(0, 0, 0)
        logger.debug("Pixels cleared")
    
    def set_brightness(self, brightness: int) -> None:
        """Set overall brightness (0-255)."""
        self.brightness = max(0, min(255, brightness))
        logger.debug(f"Brightness: {self.brightness}")
    
    def show_pixels(self) -> None:
        """Update the LED strip with current colors."""
        logger.debug("Pixels updated")
    
    def get_status(self) -> dict:
        """Get controller status."""
        return {
            'name': 'neopixel',
            'pin': self.pin,
            'num_pixels': self.num_pixels,
            'pixel_order': self.pixel_order,
            'available': self.is_available(),
            'simulation_mode': self.simulation_mode
        }