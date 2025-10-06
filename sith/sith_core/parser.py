"""
Shadow Protocol Parser for SITH

Parses and processes Shadow/MarcDuino ASCII commands.
Based on analysis of MarcDuinoMain/main.c command processing.
"""

import re
import logging
from typing import Dict, Callable, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class CommandType(Enum):
    """Shadow command types based on start character."""
    PANEL = ':'      # Panel commands
    HP = '*'         # Holo Projector commands  
    DISPLAY = '@'    # Display commands
    SOUND = '$'      # Sound commands
    ALT1 = '!'       # Alternative sound commands
    ALT2 = '%'       # Alternative HP commands
    I2C = '&'        # I2C commands
    SETUP = '#'      # Setup/configuration commands


class ShadowParser:
    """
    Parses Shadow/MarcDuino commands and routes them to appropriate handlers.
    
    Command format: [START_CHAR][COMMAND][ARGUMENTS]\\r
    Example: ":OP01\\r" = Open Panel 01
    """
    
    def __init__(self, hal_manager):
        self.hal_manager = hal_manager
        self.command_handlers = {}
        self.setup_command_handlers = {}
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup command handlers for each command type."""
        # Panel command handlers
        self.command_handlers[CommandType.PANEL] = {
            'SE': self._handle_sequence_command,
            'OP': self._handle_open_command,
            'CL': self._handle_close_command,
            'RC': self._handle_rc_command,
            'ST': self._handle_stop_command,
            'HD': self._handle_hold_command,
        }
        
        # Holo Projector command handlers
        self.command_handlers[CommandType.HP] = {
            'H0': self._handle_hp_flash,
            'F0': self._handle_hp_flicker,
            'ON': self._handle_hp_on,
            'ST': self._handle_hp_stop,
            'RD': self._handle_hp_random,
        }
        
        # Display command handlers
        self.command_handlers[CommandType.DISPLAY] = {
            '0T': self._handle_display_type,
            '0W': self._handle_display_wait,
            '0M': self._handle_display_message,
            '1M': self._handle_display_message,
        }
        
        # Sound command handlers
        self.command_handlers[CommandType.SOUND] = {
            'S': self._handle_sound_scream,
            'W': self._handle_sound_wave,
            'D': self._handle_sound_disco,
            'R': self._handle_sound_random,
            's': self._handle_sound_stop,
            'C': self._handle_sound_cantina,
            'L': self._handle_sound_leia,
            'F': self._handle_sound_faint,
        }
        
        # Setup command handlers
        self.setup_command_handlers = {
            'SD': self._handle_servo_direction,
            'SR': self._handle_servo_reverse,
            'SS': self._handle_startup_sound,
            'SQ': self._handle_quiet_mode,
            'ST': self._handle_slave_delay,
            'SM': self._handle_mp3_player,
        }
    
    def parse_command(self, command: str) -> bool:
        """
        Parse and execute a Shadow command.
        
        Args:
            command: Raw command string (e.g., ":OP01\\r")
            
        Returns:
            True if command was successfully parsed and executed
        """
        if not command or len(command) < 3:
            logger.warning(f"Invalid command: {command}")
            return False
        
        # Remove carriage return
        command = command.rstrip('\\r\\n')
        
        # Determine command type
        start_char = command[0]
        try:
            cmd_type = CommandType(start_char)
        except ValueError:
            logger.warning(f"Unknown command start character: {start_char}")
            return False
        
        # Extract command and arguments
        if len(command) < 3:
            logger.warning(f"Command too short: {command}")
            return False
        
        cmd = command[1:3]  # Two character command
        args = command[3:] if len(command) > 3 else ""
        
        # Route to appropriate handler
        if cmd_type == CommandType.SETUP:
            return self._handle_setup_command(cmd, args)
        elif cmd_type in self.command_handlers:
            handler = self.command_handlers[cmd_type].get(cmd)
            if handler:
                return handler(args)
            else:
                logger.warning(f"Unknown {cmd_type.name} command: {cmd}")
                return False
        else:
            logger.warning(f"No handler for command type: {cmd_type.name}")
            return False
    
    def _handle_sequence_command(self, args: str) -> bool:
        """Handle sequence commands (:SExx)."""
        try:
            seq_num = int(args)
            logger.info(f"Executing sequence {seq_num}")
            # TODO: Implement sequence execution
            return True
        except ValueError:
            logger.error(f"Invalid sequence number: {args}")
            return False
    
    def _handle_open_command(self, args: str) -> bool:
        """Handle panel open commands (:OPxx)."""
        try:
            panel_num = int(args)
            logger.info(f"Opening panel {panel_num}")
            
            servo_interface = self.hal_manager.get_interface("servos")
            if servo_interface and servo_interface.is_available():
                if panel_num == 0:
                    # Open all panels
                    for i in range(1, servo_interface.num_servos + 1):
                        servo_interface.set_servo_position(i, 1000)  # Open position
                elif 1 <= panel_num <= servo_interface.num_servos:
                    servo_interface.set_servo_position(panel_num, 1000)
                else:
                    logger.error(f"Invalid panel number: {panel_num}")
                    return False
            return True
        except ValueError:
            logger.error(f"Invalid panel number: {args}")
            return False
    
    def _handle_close_command(self, args: str) -> bool:
        """Handle panel close commands (:CLxx)."""
        try:
            panel_num = int(args)
            logger.info(f"Closing panel {panel_num}")
            
            servo_interface = self.hal_manager.get_interface("servos")
            if servo_interface and servo_interface.is_available():
                if panel_num == 0:
                    # Close all panels
                    for i in range(1, servo_interface.num_servos + 1):
                        servo_interface.set_servo_position(i, 2000)  # Close position
                elif 1 <= panel_num <= servo_interface.num_servos:
                    servo_interface.set_servo_position(panel_num, 2000)
                else:
                    logger.error(f"Invalid panel number: {panel_num}")
                    return False
            return True
        except ValueError:
            logger.error(f"Invalid panel number: {args}")
            return False
    
    def _handle_rc_command(self, args: str) -> bool:
        """Handle RC control commands (:RCxx)."""
        try:
            panel_num = int(args)
            logger.info(f"Setting RC control for panel {panel_num}")
            # TODO: Implement RC control
            return True
        except ValueError:
            logger.error(f"Invalid panel number: {args}")
            return False
    
    def _handle_stop_command(self, args: str) -> bool:
        """Handle stop commands (:STxx)."""
        try:
            panel_num = int(args)
            logger.info(f"Stopping panel {panel_num}")
            
            servo_interface = self.hal_manager.get_interface("servos")
            if servo_interface and servo_interface.is_available():
                if panel_num == 0:
                    # Stop all servos
                    for i in range(1, servo_interface.num_servos + 1):
                        servo_interface.stop_servo(i)
                elif 1 <= panel_num <= servo_interface.num_servos:
                    servo_interface.stop_servo(panel_num)
                else:
                    logger.error(f"Invalid panel number: {panel_num}")
                    return False
            return True
        except ValueError:
            logger.error(f"Invalid panel number: {args}")
            return False
    
    def _handle_hold_command(self, args: str) -> bool:
        """Handle hold commands (:HDxx)."""
        try:
            panel_num = int(args)
            logger.info(f"Holding panel {panel_num}")
            # TODO: Implement hold functionality
            return True
        except ValueError:
            logger.error(f"Invalid panel number: {args}")
            return False
    
    def _handle_setup_command(self, cmd: str, args: str) -> bool:
        """Handle setup commands (#CCxx)."""
        handler = self.setup_command_handlers.get(cmd)
        if handler:
            return handler(args)
        else:
            logger.warning(f"Unknown setup command: {cmd}")
            return False
    
    def _handle_servo_direction(self, args: str) -> bool:
        """Handle servo direction setup (#SDxx)."""
        try:
            direction = int(args)
            logger.info(f"Setting servo direction: {direction}")
            # TODO: Implement servo direction setting
            return True
        except ValueError:
            logger.error(f"Invalid servo direction: {args}")
            return False
    
    def _handle_servo_reverse(self, args: str) -> bool:
        """Handle individual servo reverse setup (#SRxxy)."""
        if len(args) < 3:
            logger.error(f"Invalid servo reverse command: {args}")
            return False
        
        try:
            servo_num = int(args[:2])
            direction = int(args[2])
            logger.info(f"Setting servo {servo_num} direction: {direction}")
            # TODO: Implement individual servo direction setting
            return True
        except ValueError:
            logger.error(f"Invalid servo reverse command: {args}")
            return False
    
    def _handle_startup_sound(self, args: str) -> bool:
        """Handle startup sound setup (#SSxx)."""
        try:
            sound_id = int(args)
            logger.info(f"Setting startup sound: {sound_id}")
            # TODO: Implement startup sound setting
            return True
        except ValueError:
            logger.error(f"Invalid startup sound: {args}")
            return False
    
    def _handle_quiet_mode(self, args: str) -> bool:
        """Handle quiet mode setup (#SQxx)."""
        try:
            mode = int(args)
            logger.info(f"Setting quiet mode: {mode}")
            # TODO: Implement quiet mode setting
            return True
        except ValueError:
            logger.error(f"Invalid quiet mode: {args}")
            return False
    
    def _handle_slave_delay(self, args: str) -> bool:
        """Handle slave delay setup (#STxx)."""
        try:
            delay = int(args)
            logger.info(f"Setting slave delay: {delay}ms")
            # TODO: Implement slave delay setting
            return True
        except ValueError:
            logger.error(f"Invalid slave delay: {args}")
            return False
    
    def _handle_mp3_player(self, args: str) -> bool:
        """Handle MP3 player setup (#SMxx)."""
        try:
            player = int(args)
            logger.info(f"Setting MP3 player: {player}")
            # TODO: Implement MP3 player setting
            return True
        except ValueError:
            logger.error(f"Invalid MP3 player: {args}")
            return False
    
    # Holo Projector handlers
    def _handle_hp_flash(self, args: str) -> bool:
        """Handle HP flash command (*H0xx)."""
        try:
            duration = int(args)
            logger.info(f"HP flash for {duration} seconds")
            # TODO: Implement HP flash control
            return True
        except ValueError:
            logger.error(f"Invalid HP flash duration: {args}")
            return False
    
    def _handle_hp_flicker(self, args: str) -> bool:
        """Handle HP flicker command (*F0xx)."""
        try:
            duration = int(args)
            logger.info(f"HP flicker for {duration} seconds")
            # TODO: Implement HP flicker control
            return True
        except ValueError:
            logger.error(f"Invalid HP flicker duration: {args}")
            return False
    
    def _handle_hp_on(self, args: str) -> bool:
        """Handle HP lights on command (*ONxx)."""
        logger.info("HP lights on")
        # TODO: Implement HP lights control
        return True
    
    def _handle_hp_stop(self, args: str) -> bool:
        """Handle HP stop command (*STxx)."""
        logger.info("HP stop")
        # TODO: Implement HP stop control
        return True
    
    def _handle_hp_random(self, args: str) -> bool:
        """Handle HP random command (*RDxx)."""
        logger.info("HP random movement")
        # TODO: Implement HP random control
        return True
    
    # Display handlers
    def _handle_display_type(self, args: str) -> bool:
        """Handle display type command (@xTxx)."""
        try:
            display_type = int(args)
            logger.info(f"Display type: {display_type}")
            # TODO: Implement display type control
            return True
        except ValueError:
            logger.error(f"Invalid display type: {args}")
            return False
    
    def _handle_display_wait(self, args: str) -> bool:
        """Handle display wait command (@xWxx)."""
        try:
            wait_time = int(args)
            logger.info(f"Display wait: {wait_time} seconds")
            # TODO: Implement display wait
            return True
        except ValueError:
            logger.error(f"Invalid display wait time: {args}")
            return False
    
    def _handle_display_message(self, args: str) -> bool:
        """Handle display message command (@xMtext)."""
        logger.info(f"Display message: {args}")
        # TODO: Implement display message
        return True
    
    # Sound handlers
    def _handle_sound_scream(self, args: str) -> bool:
        """Handle scream sound command ($S)."""
        logger.info("Playing scream sound")
        # TODO: Implement sound control
        return True
    
    def _handle_sound_wave(self, args: str) -> bool:
        """Handle wave sound command ($W)."""
        logger.info("Playing wave sound")
        # TODO: Implement sound control
        return True
    
    def _handle_sound_disco(self, args: str) -> bool:
        """Handle disco sound command ($D)."""
        logger.info("Playing disco sound")
        # TODO: Implement sound control
        return True
    
    def _handle_sound_random(self, args: str) -> bool:
        """Handle random sound command ($R)."""
        logger.info("Playing random sound")
        # TODO: Implement sound control
        return True
    
    def _handle_sound_stop(self, args: str) -> bool:
        """Handle stop sound command ($s)."""
        logger.info("Stopping sound")
        # TODO: Implement sound control
        return True
    
    def _handle_sound_cantina(self, args: str) -> bool:
        """Handle cantina sound command ($C)."""
        logger.info("Playing cantina sound")
        # TODO: Implement sound control
        return True
    
    def _handle_sound_leia(self, args: str) -> bool:
        """Handle Leia sound command ($L)."""
        logger.info("Playing Leia sound")
        # TODO: Implement sound control
        return True
    
    def _handle_sound_faint(self, args: str) -> bool:
        """Handle faint sound command ($F)."""
        logger.info("Playing faint sound")
        # TODO: Implement sound control
        return True