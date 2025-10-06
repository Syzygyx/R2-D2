"""
Shadow Emulator for SITH

Provides complete Shadow/MarcDuino emulation with command processing.
"""

import logging
import time
import os
import sys
from typing import Optional, Callable
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from .pty_emulator import PTYEmulator
from sith_core.hal import HALManager
from sith_core.parser import ShadowParser
from sith_backends.sim.logger_backend import LoggerBackend

logger = logging.getLogger(__name__)


class ShadowEmulator:
    """
    Complete Shadow/MarcDuino emulator with command processing.
    
    Combines PTY emulation with Shadow command parsing and HAL control.
    """
    
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.hal_manager = HALManager()
        self.backend = LoggerBackend(self.config)
        self.parser = None
        self.pty_emulator = None
        self.running = False
    
    def initialize(self) -> bool:
        """Initialize the Shadow emulator."""
        try:
            # Initialize HAL manager and backend
            self.hal_manager.set_backend(self.backend)
            if not self.backend.initialize():
                logger.error("Failed to initialize logger backend")
                return False
            
            # Create parser
            self.parser = ShadowParser(self.hal_manager)
            
            # Create PTY emulator with command handler
            self.pty_emulator = PTYEmulator(self._handle_command)
            
            self.running = True
            logger.info("Shadow emulator initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Shadow emulator: {e}")
            return False
    
    def start(self) -> str:
        """Start the emulator and return PTY device path."""
        if not self.running:
            if not self.initialize():
                raise RuntimeError("Failed to initialize emulator")
        
        return self.pty_emulator.start()
    
    def stop(self) -> None:
        """Stop the emulator."""
        if self.pty_emulator:
            self.pty_emulator.stop()
        
        if self.backend:
            self.backend.shutdown()
        
        self.running = False
        logger.info("Shadow emulator stopped")
    
    def _handle_command(self, command: str) -> None:
        """Handle incoming commands."""
        if not self.parser:
            logger.error("Parser not initialized")
            return
        
        try:
            result = self.parser.parse_command(command)
            if result:
                logger.debug(f"Command processed successfully: {command.strip()}")
            else:
                logger.warning(f"Command processing failed: {command.strip()}")
        except Exception as e:
            logger.error(f"Error processing command {command.strip()}: {e}")
    
    def send_command(self, command: str) -> None:
        """Send a command to the emulator."""
        if self.pty_emulator:
            self.pty_emulator.send_command(command)
    
    def get_command_log(self) -> list:
        """Get the command log from the backend."""
        if self.backend:
            return self.backend.get_command_log()
        return []
    
    def get_status(self) -> dict:
        """Get emulator status."""
        return {
            'running': self.running,
            'backend_status': self.backend.get_status() if self.backend else {},
            'command_count': len(self.get_command_log())
        }