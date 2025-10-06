"""
Hardware Abstraction Layer (HAL) for SITH

Provides unified interfaces for hardware control independent of implementation.
Based on Shadow/MarcDuino hardware control patterns.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class HALInterface(ABC):
    """Base class for all hardware abstraction interfaces."""
    
    def __init__(self, name: str):
        self.name = name
        self.initialized = False
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the hardware interface."""
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown and cleanup the hardware interface."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if hardware is available and responsive."""
        pass


class MotorInterface(HALInterface):
    """Interface for motor control (Sabertooth 2×12)."""
    
    def __init__(self):
        super().__init__("motors")
        self.left_speed = 0
        self.right_speed = 0
        self.max_speed = 100
    
    @abstractmethod
    def set_motor_speeds(self, left: int, right: int) -> None:
        """Set motor speeds (-100 to 100)."""
        pass
    
    @abstractmethod
    def stop_motors(self) -> None:
        """Stop all motors immediately."""
        pass
    
    @abstractmethod
    def set_motor_direction(self, motor: int, direction: int) -> None:
        """Set motor direction (0=forward, 1=reverse)."""
        pass


class DomeInterface(HALInterface):
    """Interface for dome rotation control."""
    
    def __init__(self):
        super().__init__("dome")
        self.current_position = 0
        self.target_position = 0
        self.speed = 50
    
    @abstractmethod
    def set_dome_position(self, position: int) -> None:
        """Set dome position (0-360 degrees)."""
        pass
    
    @abstractmethod
    def set_dome_speed(self, speed: int) -> None:
        """Set dome rotation speed (0-100)."""
        pass
    
    @abstractmethod
    def stop_dome(self) -> None:
        """Stop dome rotation."""
        pass


class ServoInterface(HALInterface):
    """Interface for servo control (PCA9685)."""
    
    def __init__(self, num_servos: int = 16):
        super().__init__("servos")
        self.num_servos = num_servos
        self.servo_positions = [0] * num_servos
        self.servo_directions = [0] * num_servos  # 0=normal, 1=reversed
        self.servo_speeds = [0] * num_servos
    
    @abstractmethod
    def set_servo_position(self, servo: int, position: int) -> None:
        """Set servo position (500-2500 microseconds)."""
        pass
    
    @abstractmethod
    def set_servo_speed(self, servo: int, speed: int) -> None:
        """Set servo movement speed (0=max, higher=slower)."""
        pass
    
    @abstractmethod
    def set_servo_direction(self, servo: int, direction: int) -> None:
        """Set servo direction (0=normal, 1=reversed)."""
        pass
    
    @abstractmethod
    def stop_servo(self, servo: int) -> None:
        """Stop servo (no pulse)."""
        pass
    
    def set_all_servos(self, positions: list) -> None:
        """Set all servo positions at once."""
        for i, pos in enumerate(positions[:self.num_servos]):
            self.set_servo_position(i + 1, pos)


class LEDInterface(HALInterface):
    """Interface for LED control (NeoPixel/WS2812)."""
    
    def __init__(self, num_pixels: int = 144):
        super().__init__("leds")
        self.num_pixels = num_pixels
        self.brightness = 255
    
    @abstractmethod
    def set_pixel_color(self, pixel: int, r: int, g: int, b: int) -> None:
        """Set individual pixel color (0-255)."""
        pass
    
    @abstractmethod
    def set_all_pixels(self, r: int, g: int, b: int) -> None:
        """Set all pixels to same color."""
        pass
    
    @abstractmethod
    def clear_pixels(self) -> None:
        """Turn off all pixels."""
        pass
    
    @abstractmethod
    def set_brightness(self, brightness: int) -> None:
        """Set overall brightness (0-255)."""
        pass
    
    @abstractmethod
    def show_pixels(self) -> None:
        """Update the LED strip with current colors."""
        pass


class SoundInterface(HALInterface):
    """Interface for audio control."""
    
    def __init__(self):
        super().__init__("sound")
        self.volume = 100
        self.current_sound = None
    
    @abstractmethod
    def play_sound(self, sound_id: int) -> None:
        """Play sound by ID."""
        pass
    
    @abstractmethod
    def play_sound_file(self, filename: str) -> None:
        """Play sound from file."""
        pass
    
    @abstractmethod
    def stop_sound(self) -> None:
        """Stop current sound."""
        pass
    
    @abstractmethod
    def set_volume(self, volume: int) -> None:
        """Set volume (0-100)."""
        pass
    
    @abstractmethod
    def play_random_sound(self, category: str = "random") -> None:
        """Play random sound from category."""
        pass


class HALManager:
    """Manages all hardware abstraction interfaces."""
    
    def __init__(self):
        self.interfaces: Dict[str, HALInterface] = {}
        self.backend = None
    
    def register_interface(self, interface: HALInterface) -> None:
        """Register a hardware interface."""
        self.interfaces[interface.name] = interface
        logger.info(f"Registered {interface.name} interface")
    
    def get_interface(self, name: str) -> Optional[HALInterface]:
        """Get a hardware interface by name."""
        return self.interfaces.get(name)
    
    def initialize_all(self) -> bool:
        """Initialize all registered interfaces."""
        success = True
        for interface in self.interfaces.values():
            if not interface.initialize():
                logger.error(f"Failed to initialize {interface.name}")
                success = False
            else:
                interface.initialized = True
        return success
    
    def shutdown_all(self) -> None:
        """Shutdown all interfaces."""
        for interface in self.interfaces.values():
            interface.shutdown()
            interface.initialized = False
    
    def set_backend(self, backend) -> None:
        """Set the hardware backend implementation."""
        self.backend = backend
        if backend:
            # Register interfaces from backend
            for interface in backend.get_interfaces():
                self.register_interface(interface)