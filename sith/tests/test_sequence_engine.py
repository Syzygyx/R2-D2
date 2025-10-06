"""
Tests for Sequence Engine

Tests YAML sequence loading and execution.
"""

import pytest
import tempfile
import yaml
from unittest.mock import Mock, MagicMock
from sith_core.sequence_engine import SequenceEngine, SequenceStep, SequenceState
from sith_core.hal import HALManager

# Configure logging for tests
import logging
logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def hal_manager():
    """Create a mock HAL manager for testing."""
    manager = Mock(spec=HALManager)
    manager.get_interface.return_value = Mock()
    return manager


@pytest.fixture
def sequence_engine(hal_manager):
    """Create a sequence engine instance for testing."""
    return SequenceEngine(hal_manager)


@pytest.fixture
def sample_sequence_data():
    """Sample sequence data for testing."""
    return {
        'name': 'Test Sequence',
        'description': 'A test sequence',
        'steps': [
            {
                'time_ms': 100,
                'servo_positions': [1000, 2000, 1000, 2000],
                'description': 'Step 1'
            },
            {
                'time_ms': 200,
                'servo_positions': [2000, 1000, 2000, 1000],
                'description': 'Step 2'
            },
            {
                'time_ms': 0,
                'servo_positions': [-1, -1, -1, -1],
                'description': 'Stop all'
            }
        ]
    }


class TestSequenceLoading:
    """Test sequence loading functionality."""
    
    def test_load_sequence_from_data(self, sequence_engine, sample_sequence_data):
        """Test loading sequence from dictionary data."""
        result = sequence_engine.load_sequence(sample_sequence_data)
        assert result is True
        assert len(sequence_engine.current_sequence) == 3
        assert sequence_engine.current_step == 0
        assert sequence_engine.state == SequenceState.STOPPED
    
    def test_load_sequence_from_file(self, sequence_engine, sample_sequence_data):
        """Test loading sequence from YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(sample_sequence_data, f)
            f.flush()
            
            result = sequence_engine.load_sequence_file(f.name)
            assert result is True
            assert len(sequence_engine.current_sequence) == 3
    
    def test_load_invalid_sequence(self, sequence_engine):
        """Test loading invalid sequence data."""
        invalid_data = {
            'name': 'Invalid',
            'steps': 'not a list'
        }
        
        result = sequence_engine.load_sequence(invalid_data)
        assert result is False
    
    def test_load_empty_sequence(self, sequence_engine):
        """Test loading empty sequence."""
        empty_data = {
            'name': 'Empty',
            'steps': []
        }
        
        result = sequence_engine.load_sequence(empty_data)
        assert result is True
        assert len(sequence_engine.current_sequence) == 0


class TestSequenceExecution:
    """Test sequence execution functionality."""
    
    def test_start_sequence(self, sequence_engine, sample_sequence_data):
        """Test starting a sequence."""
        sequence_engine.load_sequence(sample_sequence_data)
        
        result = sequence_engine.start_sequence()
        assert result is True
        assert sequence_engine.state == SequenceState.RUNNING
        assert sequence_engine.current_step == 0
    
    def test_start_sequence_no_sequence_loaded(self, sequence_engine):
        """Test starting sequence when none is loaded."""
        result = sequence_engine.start_sequence()
        assert result is False
    
    def test_stop_sequence(self, sequence_engine, sample_sequence_data):
        """Test stopping a sequence."""
        sequence_engine.load_sequence(sample_sequence_data)
        sequence_engine.start_sequence()
        
        sequence_engine.stop_sequence()
        assert sequence_engine.state == SequenceState.STOPPED
        assert sequence_engine.current_step == 0
    
    def test_pause_resume_sequence(self, sequence_engine, sample_sequence_data):
        """Test pausing and resuming a sequence."""
        sequence_engine.load_sequence(sample_sequence_data)
        sequence_engine.start_sequence()
        
        sequence_engine.pause_sequence()
        assert sequence_engine.state == SequenceState.PAUSED
        
        sequence_engine.resume_sequence()
        assert sequence_engine.state == SequenceState.RUNNING
    
    def test_sequence_completion(self, sequence_engine, sample_sequence_data):
        """Test sequence completion."""
        sequence_engine.load_sequence(sample_sequence_data)
        sequence_engine.start_sequence()
        
        # Simulate time passing to complete sequence
        import time
        time.sleep(0.5)  # Wait for sequence to complete
        
        sequence_engine.update()
        assert sequence_engine.state == SequenceState.COMPLETED


class TestSequenceSteps:
    """Test individual sequence step functionality."""
    
    def test_step_execution(self, sequence_engine, hal_manager):
        """Test executing a single step."""
        mock_servo = Mock()
        mock_servo.is_available.return_value = True
        mock_servo.num_servos = 16
        hal_manager.get_interface.return_value = mock_servo
        
        step = SequenceStep(
            time_ms=100,
            servo_positions=[1000, 2000, 1000, 2000],
            start_servo=1,
            end_servo=4
        )
        
        sequence_engine._execute_step(step)
        
        # Check that servo positions were set
        assert mock_servo.set_servo_position.call_count == 4
        mock_servo.set_servo_position.assert_any_call(1, 1000)
        mock_servo.set_servo_position.assert_any_call(2, 2000)
        mock_servo.set_servo_position.assert_any_call(3, 1000)
        mock_servo.set_servo_position.assert_any_call(4, 2000)
    
    def test_step_with_no_pulse(self, sequence_engine, hal_manager):
        """Test step with no pulse (servo off)."""
        mock_servo = Mock()
        mock_servo.is_available.return_value = True
        mock_servo.num_servos = 16
        hal_manager.get_interface.return_value = mock_servo
        
        step = SequenceStep(
            time_ms=100,
            servo_positions=[-1, -1, -1, -1],
            start_servo=1,
            end_servo=4
        )
        
        sequence_engine._execute_step(step)
        
        # Check that servos were stopped
        assert mock_servo.stop_servo.call_count == 4
        mock_servo.stop_servo.assert_any_call(1)
        mock_servo.stop_servo.assert_any_call(2)
        mock_servo.stop_servo.assert_any_call(3)
        mock_servo.stop_servo.assert_any_call(4)
    
    def test_step_with_speed_control(self, sequence_engine, hal_manager):
        """Test step with speed control."""
        mock_servo = Mock()
        mock_servo.is_available.return_value = True
        mock_servo.num_servos = 16
        hal_manager.get_interface.return_value = mock_servo
        
        step = SequenceStep(
            time_ms=100,
            servo_positions=[1000, 2000],
            speed=50,
            start_servo=1,
            end_servo=2
        )
        
        sequence_engine._execute_step(step)
        
        # Check that servo speeds were set
        assert mock_servo.set_servo_speed.call_count == 2
        mock_servo.set_servo_speed.assert_any_call(1, 50)
        mock_servo.set_servo_speed.assert_any_call(2, 50)


class TestSequenceUpdate:
    """Test sequence update functionality."""
    
    def test_update_running_sequence(self, sequence_engine, sample_sequence_data):
        """Test updating a running sequence."""
        sequence_engine.load_sequence(sample_sequence_data)
        sequence_engine.start_sequence()
        
        # First update should execute first step
        sequence_engine.update()
        assert sequence_engine.current_step == 1
        
        # Second update should execute second step
        sequence_engine.update()
        assert sequence_engine.current_step == 2
    
    def test_update_stopped_sequence(self, sequence_engine, sample_sequence_data):
        """Test updating a stopped sequence."""
        sequence_engine.load_sequence(sample_sequence_data)
        # Don't start the sequence
        
        sequence_engine.update()
        assert sequence_engine.current_step == 0
        assert sequence_engine.state == SequenceState.STOPPED
    
    def test_update_paused_sequence(self, sequence_engine, sample_sequence_data):
        """Test updating a paused sequence."""
        sequence_engine.load_sequence(sample_sequence_data)
        sequence_engine.start_sequence()
        sequence_engine.pause_sequence()
        
        sequence_engine.update()
        assert sequence_engine.current_step == 0  # Should not advance when paused


class TestSequenceCallbacks:
    """Test sequence completion callbacks."""
    
    def test_completion_callback(self, sequence_engine, sample_sequence_data):
        """Test sequence completion callback."""
        callback_called = False
        
        def completion_callback():
            nonlocal callback_called
            callback_called = True
        
        sequence_engine.add_completion_callback(completion_callback)
        sequence_engine.load_sequence(sample_sequence_data)
        sequence_engine.start_sequence()
        
        # Complete the sequence
        import time
        time.sleep(0.5)
        sequence_engine.update()
        
        assert callback_called is True
    
    def test_remove_completion_callback(self, sequence_engine, sample_sequence_data):
        """Test removing completion callback."""
        callback_called = False
        
        def completion_callback():
            nonlocal callback_called
            callback_called = True
        
        sequence_engine.add_completion_callback(completion_callback)
        sequence_engine.remove_completion_callback(completion_callback)
        
        sequence_engine.load_sequence(sample_sequence_data)
        sequence_engine.start_sequence()
        
        # Complete the sequence
        import time
        time.sleep(0.5)
        sequence_engine.update()
        
        assert callback_called is False


class TestSequenceStatus:
    """Test sequence status functionality."""
    
    def test_get_status(self, sequence_engine, sample_sequence_data):
        """Test getting sequence status."""
        sequence_engine.load_sequence(sample_sequence_data)
        sequence_engine.start_sequence()
        
        status = sequence_engine.get_status()
        
        assert status['state'] == SequenceState.RUNNING.value
        assert status['current_step'] == 0
        assert status['total_steps'] == 3
        assert status['progress'] == 0.0
    
    def test_set_servo_speeds(self, sequence_engine):
        """Test setting servo speeds."""
        speeds = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
        sequence_engine.set_servo_speeds(speeds)
        
        assert sequence_engine.servo_speeds == speeds[:16]


class TestShadowConversion:
    """Test Shadow sequence conversion."""
    
    def test_convert_shadow_sequence(self, sequence_engine):
        """Test converting Shadow C sequence to YAML."""
        from sith_core.sequence_engine import convert_shadow_sequence
        
        # Sample Shadow C sequence data
        c_sequence = [
            [30, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, -1, 1, 11],
            [30, 1000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, -1, 1, 11],
            [0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 11]
        ]
        
        yaml_data = convert_shadow_sequence("test_wave", c_sequence)
        
        assert yaml_data['name'] == 'test_wave'
        assert len(yaml_data['steps']) == 3
        assert yaml_data['steps'][0]['time_ms'] == 300  # 30 * 10
        assert yaml_data['steps'][0]['servo_positions'][0] == 2000  # _CLS
        assert yaml_data['steps'][1]['servo_positions'][0] == 1000  # _OPN
        assert yaml_data['steps'][2]['servo_positions'][0] == -1    # _NP


if __name__ == "__main__":
    pytest.main([__file__])