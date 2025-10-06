"""
Tests for Shadow Parser

Tests all Shadow command parsing functionality.
"""

import pytest
import logging
from unittest.mock import Mock, MagicMock
from sith_core.parser import ShadowParser, CommandType
from sith_core.hal import HALManager

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def hal_manager():
    """Create a mock HAL manager for testing."""
    manager = Mock(spec=HALManager)
    manager.get_interface.return_value = Mock()
    return manager


@pytest.fixture
def parser(hal_manager):
    """Create a parser instance for testing."""
    return ShadowParser(hal_manager)


class TestCommandParsing:
    """Test command parsing functionality."""
    
    def test_panel_open_command(self, parser, hal_manager):
        """Test panel open commands."""
        # Test single panel open
        result = parser.parse_command(":OP01\r")
        assert result is True
        
        # Test all panels open
        result = parser.parse_command(":OP00\r")
        assert result is True
    
    def test_panel_close_command(self, parser, hal_manager):
        """Test panel close commands."""
        # Test single panel close
        result = parser.parse_command(":CL01\r")
        assert result is True
        
        # Test all panels close
        result = parser.parse_command(":CL00\r")
        assert result is True
    
    def test_panel_stop_command(self, parser, hal_manager):
        """Test panel stop commands."""
        result = parser.parse_command(":ST01\r")
        assert result is True
        
        result = parser.parse_command(":ST00\r")
        assert result is True
    
    def test_sequence_command(self, parser, hal_manager):
        """Test sequence execution commands."""
        result = parser.parse_command(":SE02\r")
        assert result is True
        
        result = parser.parse_command(":SE15\r")
        assert result is True
    
    def test_holo_projector_commands(self, parser, hal_manager):
        """Test holoprojector commands."""
        result = parser.parse_command("*H005\r")
        assert result is True
        
        result = parser.parse_command("*ON00\r")
        assert result is True
        
        result = parser.parse_command("*ST00\r")
        assert result is True
    
    def test_display_commands(self, parser, hal_manager):
        """Test display commands."""
        result = parser.parse_command("@0T5\r")
        assert result is True
        
        result = parser.parse_command("@0W10\r")
        assert result is True
        
        result = parser.parse_command("@1MHello\r")
        assert result is True
    
    def test_sound_commands(self, parser, hal_manager):
        """Test sound commands."""
        result = parser.parse_command("$S\r")
        assert result is True
        
        result = parser.parse_command("$W\r")
        assert result is True
        
        result = parser.parse_command("$s\r")
        assert result is True
    
    def test_setup_commands(self, parser, hal_manager):
        """Test setup commands."""
        result = parser.parse_command("#SD00\r")
        assert result is True
        
        result = parser.parse_command("#SR010\r")
        assert result is True
        
        result = parser.parse_command("#SS01\r")
        assert result is True
    
    def test_i2c_commands(self, parser, hal_manager):
        """Test I2C commands."""
        result = parser.parse_command("&42,1,255\r")
        assert result is True
        
        result = parser.parse_command("&10,xA7,210\r")
        assert result is True


class TestCommandValidation:
    """Test command validation and error handling."""
    
    def test_invalid_start_character(self, parser):
        """Test commands with invalid start characters."""
        result = parser.parse_command("XOP01\r")
        assert result is False
    
    def test_short_command(self, parser):
        """Test commands that are too short."""
        result = parser.parse_command(":OP\r")
        assert result is False
    
    def test_empty_command(self, parser):
        """Test empty commands."""
        result = parser.parse_command("")
        assert result is False
        
        result = parser.parse_command("\r")
        assert result is False
    
    def test_invalid_panel_number(self, parser):
        """Test commands with invalid panel numbers."""
        result = parser.parse_command(":OP99\r")
        assert result is True  # Parser should handle gracefully
    
    def test_malformed_command(self, parser):
        """Test malformed commands."""
        result = parser.parse_command(":OP\r")
        assert result is False
        
        result = parser.parse_command(":OP01\r\r")
        assert result is True  # Should handle extra \r


class TestCommandTypes:
    """Test command type detection."""
    
    def test_panel_command_type(self, parser):
        """Test panel command type detection."""
        # This would require access to internal parser methods
        # For now, we test through public interface
        result = parser.parse_command(":OP01\r")
        assert result is True
    
    def test_holo_command_type(self, parser):
        """Test holoprojector command type detection."""
        result = parser.parse_command("*H005\r")
        assert result is True
    
    def test_display_command_type(self, parser):
        """Test display command type detection."""
        result = parser.parse_command("@0T5\r")
        assert result is True
    
    def test_sound_command_type(self, parser):
        """Test sound command type detection."""
        result = parser.parse_command("$S\r")
        assert result is True
    
    def test_setup_command_type(self, parser):
        """Test setup command type detection."""
        result = parser.parse_command("#SD00\r")
        assert result is True
    
    def test_i2c_command_type(self, parser):
        """Test I2C command type detection."""
        result = parser.parse_command("&42,1,255\r")
        assert result is True


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_servo_interface_not_available(self, parser):
        """Test behavior when servo interface is not available."""
        # Mock servo interface to return None
        parser.hal_manager.get_interface.return_value = None
        
        result = parser.parse_command(":OP01\r")
        assert result is True  # Should still return True but log error
    
    def test_invalid_sequence_number(self, parser):
        """Test invalid sequence numbers."""
        result = parser.parse_command(":SE99\r")
        assert result is True  # Should handle gracefully
    
    def test_servo_interface_error(self, parser, hal_manager):
        """Test behavior when servo interface raises an error."""
        # Mock servo interface to raise an exception
        mock_servo = Mock()
        mock_servo.is_available.return_value = True
        mock_servo.set_servo_position.side_effect = Exception("Hardware error")
        hal_manager.get_interface.return_value = mock_servo
        
        result = parser.parse_command(":OP01\r")
        assert result is True  # Should still return True but log error


class TestCommandHandlers:
    """Test individual command handlers."""
    
    def test_open_command_handler(self, parser, hal_manager):
        """Test open command handler."""
        mock_servo = Mock()
        mock_servo.is_available.return_value = True
        mock_servo.num_servos = 16
        hal_manager.get_interface.return_value = mock_servo
        
        result = parser._handle_open_command("01")
        assert result is True
        mock_servo.set_servo_position.assert_called_once_with(1, 1000)
    
    def test_close_command_handler(self, parser, hal_manager):
        """Test close command handler."""
        mock_servo = Mock()
        mock_servo.is_available.return_value = True
        mock_servo.num_servos = 16
        hal_manager.get_interface.return_value = mock_servo
        
        result = parser._handle_close_command("01")
        assert result is True
        mock_servo.set_servo_position.assert_called_once_with(1, 2000)
    
    def test_stop_command_handler(self, parser, hal_manager):
        """Test stop command handler."""
        mock_servo = Mock()
        mock_servo.is_available.return_value = True
        mock_servo.num_servos = 16
        hal_manager.get_interface.return_value = mock_servo
        
        result = parser._handle_stop_command("01")
        assert result is True
        mock_servo.stop_servo.assert_called_once_with(1)
    
    def test_sequence_command_handler(self, parser):
        """Test sequence command handler."""
        result = parser._handle_sequence_command("02")
        assert result is True
        
        result = parser._handle_sequence_command("invalid")
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__])