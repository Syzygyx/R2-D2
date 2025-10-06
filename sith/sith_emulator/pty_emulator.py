"""
PTY Emulator for SITH

Creates a pseudo-terminal device for testing Shadow commands without hardware.
"""

import os
import pty
import tty
import select
import logging
import threading
from typing import Optional, Callable
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

logger = logging.getLogger(__name__)


class PTYEmulator:
    """
    Creates a pseudo-terminal device that emulates Shadow/MarcDuino serial communication.
    
    This allows testing of Shadow commands without physical hardware by providing
    a virtual serial port that responds like a real MarcDuino.
    """
    
    def __init__(self, command_handler: Optional[Callable] = None):
        self.master_fd = None
        self.slave_fd = None
        self.slave_name = None
        self.running = False
        self.command_handler = command_handler
        self.thread = None
    
    def start(self) -> str:
        """
        Start the PTY emulator and return the slave device path.
        
        Returns:
            Path to the slave pseudo-terminal device
        """
        try:
            # Create pseudo-terminal pair
            self.master_fd, self.slave_fd = pty.openpty()
            self.slave_name = os.ttyname(self.slave_fd)
            
            # Configure terminal settings
            tty.setraw(self.master_fd)
            
            self.running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()
            
            logger.info(f"PTY emulator started on {self.slave_name}")
            return self.slave_name
            
        except Exception as e:
            logger.error(f"Failed to start PTY emulator: {e}")
            raise
    
    def stop(self) -> None:
        """Stop the PTY emulator."""
        self.running = False
        if self.master_fd:
            os.close(self.master_fd)
        if self.slave_fd:
            os.close(self.slave_fd)
        logger.info("PTY emulator stopped")
    
    def _run_loop(self) -> None:
        """Main emulator loop."""
        buffer = b""
        
        while self.running:
            try:
                # Check for data to read
                ready, _, _ = select.select([self.master_fd], [], [], 0.1)
                
                if ready:
                    data = os.read(self.master_fd, 1024)
                    if data:
                        buffer += data
                        
                        # Process complete commands (ending with \r)
                        while b'\r' in buffer:
                            line, buffer = buffer.split(b'\r', 1)
                            command = line.decode('utf-8', errors='ignore')
                            self._process_command(command)
                
            except Exception as e:
                logger.error(f"Error in PTY emulator loop: {e}")
                break
    
    def _process_command(self, command: str) -> None:
        """Process a received command."""
        logger.debug(f"Received command: {command}")
        
        # Echo the command back
        self._send_response(command)
        
        # Send OK response
        self._send_response("OK")
        
        # Call custom handler if provided
        if self.command_handler:
            try:
                self.command_handler(command)
            except Exception as e:
                logger.error(f"Error in command handler: {e}")
    
    def _send_response(self, response: str) -> None:
        """Send a response back through the PTY."""
        try:
            data = (response + '\r\n').encode('utf-8')
            os.write(self.master_fd, data)
        except Exception as e:
            logger.error(f"Failed to send response: {e}")
    
    def send_command(self, command: str) -> None:
        """Send a command to the emulator (for testing)."""
        try:
            data = (command + '\r').encode('utf-8')
            os.write(self.master_fd, data)
        except Exception as e:
            logger.error(f"Failed to send command: {e}")


def create_pty_emulator(command_handler: Optional[Callable] = None) -> PTYEmulator:
    """
    Create and start a PTY emulator.
    
    Args:
        command_handler: Optional function to handle received commands
        
    Returns:
        Started PTY emulator instance
    """
    emulator = PTYEmulator(command_handler)
    emulator.start()
    return emulator