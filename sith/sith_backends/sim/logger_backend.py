"""
Logger Backend for SITH

Logs all commands without hardware control for testing and debugging.
"""

import logging
import time
from typing import List, Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from sith_backends.base import BackendBase
from sith_core.hal import MotorInterface, ServoInterface, LEDInterface, SoundInterface

logger = logging.getLogger(__name__)


class LoggerMotorInterface(MotorInterface):
    """Motor interface that logs commands instead of controlling hardware."""
    
    def __init__(self):
        super().__init__()
        self.left_speed = 0
        self.right_speed = 0
        self.command_log = []
    
    def initialize(self) -> bool:
        self.initialized = True
        logger.info("Logger motor interface initialized")
        return True
    
    def shutdown(self) -> None:
        self.initialized = False
        logger.info("Logger motor interface shutdown")
    
    def is_available(self) -> bool:
        return self.initialized
    
    def set_motor_speeds(self, left: int, right: int) -> None:
        self.left_speed = left
        self.right_speed = right
        self.command_log.append({
            'timestamp': time.time(),
            'command': 'set_motor_speeds',
            'left': left,
            'right': right
        })
        logger.info(f"Motor speeds: L={left}, R={right}")
    
    def stop_motors(self) -> None:
        self.left_speed = 0
        self.right_speed = 0
        self.command_log.append({
            'timestamp': time.time(),
            'command': 'stop_motors'
        })
        logger.info("Motors stopped")
    
    def set_motor_direction(self, motor: int, direction: int) -> None:
        self.command_log.append({
            'timestamp': time.time(),
            'command': 'set_motor_direction',
            'motor': motor,
            'direction': direction
        })
        logger.info(f"Motor {motor} direction: {direction}")


class LoggerServoInterface(ServoInterface):
    """Servo interface that logs commands instead of controlling hardware."""
    
    def __init__(self, num_servos: int = 16):
        super().__init__(num_servos)
        self.command_log = []
    
    def initialize(self) -> bool:
        self.initialized = True
        logger.info(f"Logger servo interface initialized ({self.num_servos} servos)")
        return True
    
    def shutdown(self) -> None:
        self.initialized = False
        logger.info("Logger servo interface shutdown")
    
    def is_available(self) -> bool:
        return self.initialized
    
    def set_servo_position(self, servo: int, position: int) -> None:
        if 1 <= servo <= self.num_servos:
            self.servo_positions[servo - 1] = position
            self.command_log.append({
                'timestamp': time.time(),
                'command': 'set_servo_position',
                'servo': servo,
                'position': position
            })
            logger.info(f"Servo {servo} position: {position}μs")
    
    def set_servo_speed(self, servo: int, speed: int) -> None:
        if 1 <= servo <= self.num_servos:
            self.servo_speeds[servo - 1] = speed
            self.command_log.append({
                'timestamp': time.time(),
                'command': 'set_servo_speed',
                'servo': servo,
                'speed': speed
            })
            logger.info(f"Servo {servo} speed: {speed}")
    
    def set_servo_direction(self, servo: int, direction: int) -> None:
        if 1 <= servo <= self.num_servos:
            self.servo_directions[servo - 1] = direction
            self.command_log.append({
                'timestamp': time.time(),
                'command': 'set_servo_direction',
                'servo': servo,
                'direction': direction
            })
            logger.info(f"Servo {servo} direction: {'reversed' if direction else 'normal'}")
    
    def stop_servo(self, servo: int) -> None:
        if 1 <= servo <= self.num_servos:
            self.servo_positions[servo - 1] = -1
            self.command_log.append({
                'timestamp': time.time(),
                'command': 'stop_servo',
                'servo': servo
            })
            logger.info(f"Servo {servo} stopped")


class LoggerLEDInterface(LEDInterface):
    """LED interface that logs commands instead of controlling hardware."""
    
    def __init__(self, num_pixels: int = 144):
        super().__init__(num_pixels)
        self.command_log = []
    
    def initialize(self) -> bool:
        self.initialized = True
        logger.info(f"Logger LED interface initialized ({self.num_pixels} pixels)")
        return True
    
    def shutdown(self) -> None:
        self.initialized = False
        logger.info("Logger LED interface shutdown")
    
    def is_available(self) -> bool:
        return self.initialized
    
    def set_pixel_color(self, pixel: int, r: int, g: int, b: int) -> None:
        if 0 <= pixel < self.num_pixels:
            self.command_log.append({
                'timestamp': time.time(),
                'command': 'set_pixel_color',
                'pixel': pixel,
                'r': r, 'g': g, 'b': b
            })
            logger.info(f"Pixel {pixel}: RGB({r},{g},{b})")
    
    def set_all_pixels(self, r: int, g: int, b: int) -> None:
        self.command_log.append({
            'timestamp': time.time(),
            'command': 'set_all_pixels',
            'r': r, 'g': g, 'b': b
        })
        logger.info(f"All pixels: RGB({r},{g},{b})")
    
    def clear_pixels(self) -> None:
        self.command_log.append({
            'timestamp': time.time(),
            'command': 'clear_pixels'
        })
        logger.info("Pixels cleared")
    
    def set_brightness(self, brightness: int) -> None:
        self.brightness = brightness
        self.command_log.append({
            'timestamp': time.time(),
            'command': 'set_brightness',
            'brightness': brightness
        })
        logger.info(f"Brightness: {brightness}")
    
    def show_pixels(self) -> None:
        self.command_log.append({
            'timestamp': time.time(),
            'command': 'show_pixels'
        })
        logger.info("Pixels updated")


class LoggerSoundInterface(SoundInterface):
    """Sound interface that logs commands instead of controlling hardware."""
    
    def __init__(self):
        super().__init__()
        self.command_log = []
    
    def initialize(self) -> bool:
        self.initialized = True
        logger.info("Logger sound interface initialized")
        return True
    
    def shutdown(self) -> None:
        self.initialized = False
        logger.info("Logger sound interface shutdown")
    
    def is_available(self) -> bool:
        return self.initialized
    
    def play_sound(self, sound_id: int) -> None:
        self.command_log.append({
            'timestamp': time.time(),
            'command': 'play_sound',
            'sound_id': sound_id
        })
        logger.info(f"Playing sound: {sound_id}")
    
    def play_sound_file(self, filename: str) -> None:
        self.command_log.append({
            'timestamp': time.time(),
            'command': 'play_sound_file',
            'filename': filename
        })
        logger.info(f"Playing sound file: {filename}")
    
    def stop_sound(self) -> None:
        self.command_log.append({
            'timestamp': time.time(),
            'command': 'stop_sound'
        })
        logger.info("Sound stopped")
    
    def set_volume(self, volume: int) -> None:
        self.volume = volume
        self.command_log.append({
            'timestamp': time.time(),
            'command': 'set_volume',
            'volume': volume
        })
        logger.info(f"Volume: {volume}")
    
    def play_random_sound(self, category: str = "random") -> None:
        self.command_log.append({
            'timestamp': time.time(),
            'command': 'play_random_sound',
            'category': category
        })
        logger.info(f"Playing random sound: {category}")


class LoggerBackend(BackendBase):
    """Logger backend that logs all commands without hardware control."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("logger")
        self.config = config or {}
        self.interfaces = {}
        self.log_file = self.config.get('log_file', 'sith_commands.log')
        self.command_count = 0
    
    def initialize(self) -> bool:
        """Initialize logger backend."""
        try:
            # Create logger interfaces
            self.interfaces['motors'] = LoggerMotorInterface()
            self.interfaces['servos'] = LoggerServoInterface(16)
            self.interfaces['leds'] = LoggerLEDInterface(144)
            self.interfaces['sound'] = LoggerSoundInterface()
            
            # Initialize all interfaces
            for interface in self.interfaces.values():
                interface.initialize()
            
            self.initialized = True
            logger.info("Logger backend initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize logger backend: {e}")
            return False
    
    def shutdown(self) -> None:
        """Shutdown logger backend."""
        for interface in self.interfaces.values():
            interface.shutdown()
        
        self.interfaces.clear()
        self.initialized = False
        logger.info("Logger backend shutdown")
    
    def get_interfaces(self) -> List[Any]:
        """Get list of logger interfaces."""
        return list(self.interfaces.values())
    
    def is_available(self) -> bool:
        """Check if backend is available."""
        return self.initialized
    
    def get_command_log(self) -> List[Dict[str, Any]]:
        """Get all logged commands."""
        all_commands = []
        for interface in self.interfaces.values():
            if hasattr(interface, 'command_log'):
                all_commands.extend(interface.command_log)
        
        # Sort by timestamp
        all_commands.sort(key=lambda x: x['timestamp'])
        return all_commands
    
    def save_log(self, filename: str = None) -> None:
        """Save command log to file."""
        import json
        
        filename = filename or self.log_file
        commands = self.get_command_log()
        
        try:
            with open(filename, 'w') as f:
                json.dump(commands, f, indent=2)
            logger.info(f"Command log saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save log: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get backend status."""
        status = super().get_status()
        status.update({
            'log_file': self.log_file,
            'command_count': len(self.get_command_log()),
            'interfaces': {
                name: interface.get_status() if hasattr(interface, 'get_status') else {}
                for name, interface in self.interfaces.items()
            }
        })
        return status