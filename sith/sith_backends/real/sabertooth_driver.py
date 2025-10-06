"""
Sabertooth 2×12 Motor Driver for SITH

Implements UART communication with Sabertooth motor driver.
Based on Shadow system motor control patterns.
"""

import serial
import time
import logging
from typing import Optional
from ...sith_core.hal import MotorInterface

logger = logging.getLogger(__name__)


class SabertoothDriver(MotorInterface):
    """Sabertooth 2×12 motor driver implementation."""
    
    def __init__(self, port: str = '/dev/ttyUSB0', baudrate: int = 2400):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.serial_conn: Optional[serial.Serial] = None
        self.left_speed = 0
        self.right_speed = 0
        self.max_speed = 100
        self.min_speed = -100
    
    def initialize(self) -> bool:
        """Initialize serial connection to Sabertooth."""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1.0,
                write_timeout=1.0
            )
            
            # Wait for connection to stabilize
            time.sleep(0.1)
            
            # Test connection with stop command
            self.stop_motors()
            
            self.initialized = True
            logger.info(f"Sabertooth driver initialized on {self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Sabertooth driver: {e}")
            return False
    
    def shutdown(self) -> None:
        """Shutdown serial connection."""
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.stop_motors()
                self.serial_conn.close()
            except Exception as e:
                logger.error(f"Error closing Sabertooth connection: {e}")
        
        self.serial_conn = None
        self.initialized = False
        logger.info("Sabertooth driver shutdown")
    
    def is_available(self) -> bool:
        """Check if driver is available."""
        return (self.initialized and 
                self.serial_conn is not None and 
                self.serial_conn.is_open)
    
    def set_motor_speeds(self, left: int, right: int) -> None:
        """Set motor speeds (-100 to 100)."""
        if not self.is_available():
            logger.error("Sabertooth driver not available")
            return
        
        # Clamp speeds to valid range
        left = max(self.min_speed, min(self.max_speed, left))
        right = max(self.min_speed, min(self.max_speed, right))
        
        try:
            # Sabertooth command format: [address][command][data]
            # Address 128 (0x80) for mixed mode
            # Command 0 = forward/backward, 1 = turn left/right
            
            if left == 0 and right == 0:
                # Stop both motors
                self._send_command(128, 0, 0)
            elif left == right:
                # Both motors same speed - forward/backward
                speed = abs(left)
                if left > 0:
                    self._send_command(128, 0, speed + 1)  # Forward
                else:
                    self._send_command(128, 0, 127 - speed)  # Backward
            else:
                # Different speeds - use turn command
                if left > right:
                    # Turn right
                    turn_speed = abs(left - right)
                    self._send_command(128, 1, turn_speed + 1)
                else:
                    # Turn left
                    turn_speed = abs(right - left)
                    self._send_command(128, 1, 127 - turn_speed)
            
            self.left_speed = left
            self.right_speed = right
            logger.debug(f"Set motor speeds: L={left}, R={right}")
            
        except Exception as e:
            logger.error(f"Failed to set motor speeds: {e}")
    
    def stop_motors(self) -> None:
        """Stop all motors immediately."""
        if not self.is_available():
            return
        
        try:
            # Send stop command
            self._send_command(128, 0, 0)
            self.left_speed = 0
            self.right_speed = 0
            logger.debug("Motors stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop motors: {e}")
    
    def set_motor_direction(self, motor: int, direction: int) -> None:
        """Set motor direction (0=forward, 1=reverse)."""
        # Sabertooth handles direction through speed sign
        # This method is for compatibility with HAL interface
        logger.debug(f"Motor direction set: motor={motor}, direction={direction}")
    
    def _send_command(self, address: int, command: int, data: int) -> None:
        """Send command to Sabertooth."""
        if not self.serial_conn or not self.serial_conn.is_open:
            raise RuntimeError("Serial connection not available")
        
        # Calculate checksum
        checksum = (address + command + data) & 0x7F
        
        # Send command packet
        packet = bytes([address, command, data, checksum])
        self.serial_conn.write(packet)
        self.serial_conn.flush()
        
        logger.debug(f"Sent Sabertooth command: {packet.hex()}")
    
    def get_status(self) -> dict:
        """Get driver status."""
        return {
            'name': 'sabertooth',
            'port': self.port,
            'baudrate': self.baudrate,
            'available': self.is_available(),
            'left_speed': self.left_speed,
            'right_speed': self.right_speed
        }