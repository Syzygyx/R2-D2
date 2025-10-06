"""
Real Hardware Backend for SITH

Implements hardware control using actual devices.
"""

from .real_backend import RealBackend
from .sabertooth_driver import SabertoothDriver
from .pca9685_controller import PCA9685Controller
from .neopixel_controller import NeoPixelController
from .audio_controller import AudioController

__all__ = [
    "RealBackend",
    "SabertoothDriver", 
    "PCA9685Controller",
    "NeoPixelController",
    "AudioController"
]