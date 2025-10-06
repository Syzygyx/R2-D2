#!/usr/bin/env python3
"""
SITH Simulation Test

Quick test of SITH simulation capabilities.
"""

import sys
import os
import time
import logging

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_shadow_commands():
    """Test Shadow command parsing."""
    print("🎭 Testing Shadow Command Parsing...")
    
    from sith_core.hal import HALManager
    from sith_core.parser import ShadowParser
    from sith_backends.sim.logger_backend import LoggerBackend
    
    # Create HAL manager and logger backend
    hal_manager = HALManager()
    backend = LoggerBackend()
    hal_manager.set_backend(backend)
    
    # Initialize backend
    if not backend.initialize():
        print("❌ Failed to initialize logger backend")
        return False
    
    # Create parser
    parser = ShadowParser(hal_manager)
    
    # Test commands
    test_commands = [
        ":OP01\r",    # Open panel 1
        ":CL01\r",    # Close panel 1
        ":OP00\r",    # Open all panels
        ":SE02\r",    # Wave sequence
        "*H005\r",    # HP flash 5 seconds
        "@0T5\r",     # Scream display
        "$S\r",       # Scream sound
        "#SD00\r",    # Servo direction forward
    ]
    
    success_count = 0
    for cmd in test_commands:
        result = parser.parse_command(cmd)
        if result:
            success_count += 1
        print(f"  {cmd.strip()}: {'✅' if result else '❌'}")
    
    print(f"✅ Command parsing: {success_count}/{len(test_commands)} successful")
    return success_count == len(test_commands)


def test_sequence_engine():
    """Test sequence engine."""
    print("\n🎬 Testing Sequence Engine...")
    
    from sith_core.hal import HALManager
    from sith_core.sequence_engine import SequenceEngine
    from sith_backends.sim.logger_backend import LoggerBackend
    
    # Create HAL manager and logger backend
    hal_manager = HALManager()
    backend = LoggerBackend()
    hal_manager.set_backend(backend)
    
    # Initialize backend
    if not backend.initialize():
        print("❌ Failed to initialize logger backend")
        return False
    
    # Create sequence engine
    sequence_engine = SequenceEngine(hal_manager)
    
    # Create a simple test sequence
    test_sequence = {
        'name': 'Test Wave',
        'description': 'Simple wave simulation',
        'steps': [
            {
                'time_ms': 100,
                'servo_positions': [2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000],
                'description': 'Close all panels'
            },
            {
                'time_ms': 200,
                'servo_positions': [1000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000],
                'description': 'Open panel 1'
            },
            {
                'time_ms': 200,
                'servo_positions': [2000, 1000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000],
                'description': 'Open panel 2'
            }
        ]
    }
    
    # Load and test sequence
    if not sequence_engine.load_sequence(test_sequence):
        print("❌ Failed to load sequence")
        return False
    
    print("✅ Sequence loaded successfully")
    
    # Start sequence
    if not sequence_engine.start_sequence():
        print("❌ Failed to start sequence")
        return False
    
    print("✅ Sequence started")
    
    # Run sequence for a few steps
    for i in range(5):
        time.sleep(0.1)
        sequence_engine.update()
        status = sequence_engine.get_status()
        print(f"  Step {status['current_step']}/{status['total_steps']} - {status['state']}")
        
        if status['state'] == 'completed':
            print("✅ Sequence completed!")
            break
    
    return True


def test_pty_emulator():
    """Test PTY emulator."""
    print("\n🔌 Testing PTY Emulator...")
    
    from sith_emulator.pty_emulator import PTYEmulator
    
    def command_handler(command):
        print(f"  Received: {command}")
    
    # Create PTY emulator
    emulator = PTYEmulator(command_handler)
    
    try:
        # Start emulator
        slave_path = emulator.start()
        print(f"✅ PTY emulator started on: {slave_path}")
        
        # Send test commands
        test_commands = [":OP01\r", ":CL01\r", ":SE02\r"]
        for cmd in test_commands:
            emulator.send_command(cmd)
            time.sleep(0.1)
        
        print("✅ PTY emulator test complete")
        return True
        
    except Exception as e:
        print(f"❌ PTY emulator error: {e}")
        return False
    finally:
        emulator.stop()


def main():
    """Main test function."""
    print("🤖 SITH Simulation Test")
    print("=" * 50)
    
    tests = [
        ("Shadow Command Parsing", test_shadow_commands),
        ("Sequence Engine", test_sequence_engine),
        ("PTY Emulator", test_pty_emulator),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! SITH simulation is working perfectly!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)