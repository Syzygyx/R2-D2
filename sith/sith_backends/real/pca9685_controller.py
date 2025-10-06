"""
PCA9685 Servo Controller for SITH

Implements I2C communication with PCA9685 16-channel PWM controller.
Based on Shadow system servo control patterns.
"""

import time
import logging
from typing import List, Optional
try:
    import board
    import busio
    from adafruit_pca9685 import PCA9685
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("PCA9685 hardware libraries not available - using simulation mode")

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from sith_core.hal import ServoInterface

logger = logging.getLogger(__name__)


class PCA9685Controller(ServoInterface):
    """PCA9685 16-channel servo controller implementation."""
    
    # Servo timing constants (in microseconds)
    SERVO_MIN_PULSE = 500
    SERVO_MAX_PULSE = 2500
    SERVO_FREQUENCY = 50  # 50Hz
    
    def __init__(self, address: int = 0x40, frequency: int = 50):
        super().__init__(16)  # 16 servos
        self.address = address
        self.frequency = frequency
        self.pca9685: Optional[PCA9685] = None
        self.i2c: Optional[busio.I2C] = None
        self.servo_positions = [0] * 16
        self.servo_directions = [0] * 16  # 0=normal, 1=reversed
        self.servo_speeds = [0] * 16  # 0=max speed, higher=slower
        self.simulation_mode = not HARDWARE_AVAILABLE
    
    def initialize(self) -> bool:
        """Initialize I2C connection and PCA9685."""
        if self.simulation_mode:
            logger.info("PCA9685 running in simulation mode")
            self.initialized = True
            return True
        
        try:
            # Initialize I2C bus
            self.i2c = busio.I2C(board.SCL, board.SDA)
            
            # Initialize PCA9685
            self.pca9685 = PCA9685(self.i2c, address=self.address)
            self.pca9685.frequency = self.frequency
            
            # Initialize all servos to center position
            for i in range(self.num_servos):
                self.set_servo_position(i + 1, 1500)  # Center position
            
            self.initialized = True
            logger.info(f"PCA9685 controller initialized at address 0x{self.address:02X}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize PCA9685 controller: {e}")
            return False
    
    def shutdown(self) -> None:
        """Shutdown PCA9685 controller."""
        if self.pca9685:
            try:
                # Stop all servos
                for i in range(self.num_servos):
                    self.stop_servo(i + 1)
                
                # Close I2C connection
                if self.i2c:
                    self.i2c.deinit()
                
            except Exception as e:
                logger.error(f"Error shutting down PCA9685: {e}")
        
        self.pca9685 = None
        self.i2c = None
        self.initialized = False
        logger.info("PCA9685 controller shutdown")
    
    def is_available(self) -> bool:
        """Check if controller is available."""
        return self.initialized and (self.simulation_mode or self.pca9685 is not None)
    
    def set_servo_position(self, servo: int, position: int) -> None:
        """Set servo position (500-2500 microseconds)."""
        if not self.is_available():
            logger.error("PCA9685 controller not available")
            return
        
        if servo < 1 or servo > self.num_servos:
            logger.error(f"Invalid servo number: {servo}")
            return
        
        # Clamp position to valid range
        position = max(self.SERVO_MIN_PULSE, min(self.SERVO_MAX_PULSE, position))
        
        # Apply direction reversal if needed
        if self.servo_directions[servo - 1] == 1:
            position = self.SERVO_MAX_PULSE - (position - self.SERVO_MIN_PULSE)
        
        # Store position
        self.servo_positions[servo - 1] = position
        
        if not self.simulation_mode:
            try:
                # Convert microseconds to duty cycle
                duty_cycle = int((position / 1000000) * self.frequency * 4096)
                self.pca9685.channels[servo - 1].duty_cycle = duty_cycle
                
            except Exception as e:
                logger.error(f"Failed to set servo {servo} position: {e}")
        else:
            logger.debug(f"Simulation: Servo {servo} position = {position}μs")
    
    def set_servo_speed(self, servo: int, speed: int) -> None:
        """Set servo movement speed (0=max, higher=slower)."""
        if servo < 1 or servo > self.num_servos:
            logger.error(f"Invalid servo number: {servo}")
            return
        
        self.servo_speeds[servo - 1] = max(0, speed)
        logger.debug(f"Servo {servo} speed set to {speed}")
    
    def set_servo_direction(self, servo: int, direction: int) -> None:
        """Set servo direction (0=normal, 1=reversed)."""
        if servo < 1 or servo > self.num_servos:
            logger.error(f"Invalid servo number: {servo}")
            return
        
        self.servo_directions[servo - 1] = 1 if direction else 0
        logger.debug(f"Servo {servo} direction set to {'reversed' if direction else 'normal'}")
    
    def stop_servo(self, servo: int) -> None:
        """Stop servo (no pulse)."""
        if servo < 1 or servo > self.num_servos:
            logger.error(f"Invalid servo number: {servo}")
            return
        
        if not self.simulation_mode:
            try:
                # Set duty cycle to 0 (no pulse)
                self.pca9685.channels[servo - 1].duty_cycle = 0
            except Exception as e:
                logger.error(f"Failed to stop servo {servo}: {e}")
        else:
            logger.debug(f"Simulation: Servo {servo} stopped")
        
        self.servo_positions[servo - 1] = -1  # Mark as stopped
    
    def set_all_servos(self, positions: List[int]) -> None:
        """Set all servo positions at once."""
        for i, pos in enumerate(positions[:self.num_servos]):
            self.set_servo_position(i + 1, pos)
    
    def get_servo_position(self, servo: int) -> int:
        """Get current servo position."""
        if servo < 1 or servo > self.num_servos:
            return -1
        return self.servo_positions[servo - 1]
    
    def get_status(self) -> dict:
        """Get controller status."""
        return {
            'name': 'pca9685',
            'address': f"0x{self.address:02X}",
            'frequency': self.frequency,
            'available': self.is_available(),
            'simulation_mode': self.simulation_mode,
            'servo_positions': self.servo_positions.copy(),
            'servo_directions': self.servo_directions.copy()
        }