"""
Sequence Engine for SITH

Converts and executes Shadow panel sequences from YAML format.
Based on analysis of MarcDuinoMain/panel_sequences.h and sequencer.c
"""

import yaml
import time
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SequenceState(Enum):
    """Sequence execution states."""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass
class SequenceStep:
    """Represents a single step in a sequence."""
    time_ms: int
    servo_positions: List[int]
    speed: Optional[int] = None
    start_servo: int = 1
    end_servo: int = 16
    description: str = ""


class SequenceEngine:
    """
    Executes panel sequences from YAML definitions.
    
    Converts Shadow C sequences to YAML format and executes them
    with proper timing and servo control.
    """
    
    # Shadow servo position constants
    SERVO_OPEN = 1000    # 1.0ms pulse
    SERVO_MID = 1750     # 1.75ms pulse (middle position)
    SERVO_CLOSE = 2000   # 2.0ms pulse
    SERVO_NO_PULSE = -1  # No pulse (servo off)
    
    def __init__(self, hal_manager):
        self.hal_manager = hal_manager
        self.current_sequence = None
        self.current_step = 0
        self.state = SequenceState.STOPPED
        self.start_time = 0
        self.completion_callbacks = []
        self.servo_speeds = [0] * 16  # Default max speed
    
    def load_sequence(self, sequence_data: Dict[str, Any]) -> bool:
        """
        Load a sequence from YAML data.
        
        Args:
            sequence_data: Dictionary containing sequence definition
            
        Returns:
            True if sequence loaded successfully
        """
        try:
            self.current_sequence = []
            
            for step_data in sequence_data.get('steps', []):
                step = SequenceStep(
                    time_ms=step_data['time_ms'],
                    servo_positions=step_data['servo_positions'],
                    speed=step_data.get('speed'),
                    start_servo=step_data.get('start_servo', 1),
                    end_servo=step_data.get('end_servo', 16),
                    description=step_data.get('description', '')
                )
                self.current_sequence.append(step)
            
            self.current_step = 0
            self.state = SequenceState.STOPPED
            logger.info(f"Loaded sequence with {len(self.current_sequence)} steps")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load sequence: {e}")
            return False
    
    def load_sequence_file(self, filename: str) -> bool:
        """Load sequence from YAML file."""
        try:
            with open(filename, 'r') as f:
                sequence_data = yaml.safe_load(f)
            return self.load_sequence(sequence_data)
        except Exception as e:
            logger.error(f"Failed to load sequence file {filename}: {e}")
            return False
    
    def start_sequence(self) -> bool:
        """Start executing the loaded sequence."""
        if not self.current_sequence:
            logger.error("No sequence loaded")
            return False
        
        if self.state == SequenceState.RUNNING:
            logger.warning("Sequence already running")
            return False
        
        self.current_step = 0
        self.state = SequenceState.RUNNING
        self.start_time = time.time()
        logger.info("Started sequence execution")
        return True
    
    def stop_sequence(self) -> None:
        """Stop the current sequence."""
        self.state = SequenceState.STOPPED
        self.current_step = 0
        logger.info("Stopped sequence execution")
    
    def pause_sequence(self) -> None:
        """Pause the current sequence."""
        if self.state == SequenceState.RUNNING:
            self.state = SequenceState.PAUSED
            logger.info("Paused sequence execution")
    
    def resume_sequence(self) -> None:
        """Resume a paused sequence."""
        if self.state == SequenceState.PAUSED:
            self.state = SequenceState.RUNNING
            logger.info("Resumed sequence execution")
    
    def update(self) -> None:
        """Update sequence execution. Call this regularly."""
        if self.state != SequenceState.RUNNING or not self.current_sequence:
            return
        
        if self.current_step >= len(self.current_sequence):
            self._complete_sequence()
            return
        
        current_time = time.time()
        elapsed_ms = (current_time - self.start_time) * 1000
        
        # Check if current step is complete
        step = self.current_sequence[self.current_step]
        if elapsed_ms >= step.time_ms:
            self._execute_step(step)
            self.current_step += 1
            self.start_time = current_time  # Reset timer for next step
    
    def _execute_step(self, step: SequenceStep) -> None:
        """Execute a single sequence step."""
        logger.debug(f"Executing step {self.current_step}: {step.description}")
        
        servo_interface = self.hal_manager.get_interface("servos")
        if not servo_interface or not servo_interface.is_available():
            logger.error("Servo interface not available")
            return
        
        # Set servo positions
        for i, position in enumerate(step.servo_positions):
            servo_num = i + 1
            if servo_num > servo_interface.num_servos:
                break
            
            # Check if servo is in range for this step
            if servo_num < step.start_servo or servo_num > step.end_servo:
                continue
            
            if position == self.SERVO_NO_PULSE:
                servo_interface.stop_servo(servo_num)
            else:
                # Apply speed limiting if specified
                if step.speed is not None and step.speed > 0:
                    servo_interface.set_servo_speed(servo_num, step.speed)
                servo_interface.set_servo_position(servo_num, position)
    
    def _complete_sequence(self) -> None:
        """Handle sequence completion."""
        self.state = SequenceState.COMPLETED
        logger.info("Sequence completed")
        
        # Call completion callbacks
        for callback in self.completion_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in completion callback: {e}")
    
    def add_completion_callback(self, callback: Callable) -> None:
        """Add a callback to be called when sequence completes."""
        self.completion_callbacks.append(callback)
    
    def remove_completion_callback(self, callback: Callable) -> None:
        """Remove a completion callback."""
        if callback in self.completion_callbacks:
            self.completion_callbacks.remove(callback)
    
    def set_servo_speeds(self, speeds: List[int]) -> None:
        """Set default servo speeds (0 = max speed, higher = slower)."""
        self.servo_speeds = speeds[:16]  # Limit to 16 servos
        logger.info(f"Set servo speeds: {self.servo_speeds}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current sequence status."""
        return {
            'state': self.state.value,
            'current_step': self.current_step,
            'total_steps': len(self.current_sequence) if self.current_sequence else 0,
            'progress': self.current_step / len(self.current_sequence) if self.current_sequence else 0
        }


def convert_shadow_sequence(sequence_name: str, c_sequence: List[List[int]]) -> Dict[str, Any]:
    """
    Convert Shadow C sequence to YAML format.
    
    Args:
        sequence_name: Name of the sequence
        c_sequence: C array sequence data
        
    Returns:
        Dictionary ready for YAML serialization
    """
    steps = []
    
    for i, row in enumerate(c_sequence):
        time_ms = row[0] * 10  # Convert from 1/100s to ms
        servo_positions = row[1:13]  # Servos 1-12
        speed = row[13] if len(row) > 13 else None
        start_servo = row[14] if len(row) > 14 else 1
        end_servo = row[15] if len(row) > 15 else 12
        
        # Convert Shadow constants
        converted_positions = []
        for pos in servo_positions:
            if pos == 1000:  # _OPN
                converted_positions.append(SequenceEngine.SERVO_OPEN)
            elif pos == 2000:  # _CLS
                converted_positions.append(SequenceEngine.SERVO_CLOSE)
            elif pos == 1750:  # _MID
                converted_positions.append(SequenceEngine.SERVO_MID)
            elif pos == -1:  # _NP
                converted_positions.append(SequenceEngine.SERVO_NO_PULSE)
            else:
                converted_positions.append(pos)
        
        step = {
            'time_ms': time_ms,
            'servo_positions': converted_positions,
            'speed': speed if speed != -1 else None,
            'start_servo': start_servo,
            'end_servo': end_servo,
            'description': f"Step {i+1}"
        }
        steps.append(step)
    
    return {
        'name': sequence_name,
        'description': f"Converted from Shadow C sequence: {sequence_name}",
        'steps': steps
    }