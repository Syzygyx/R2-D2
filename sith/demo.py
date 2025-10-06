#!/usr/bin/env python3
"""
SITH Demo Script

Demonstrates SITH functionality with logger backend.
"""

import sys
import os
import time
import logging

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sith_core.hal import HALManager
from sith_core.parser import ShadowParser
from sith_core.sequence_engine import SequenceEngine
from sith_backends.sim.logger_backend import LoggerBackend
from sith_emulator.pty_emulator import PTYEmulator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def demo_shadow_commands():
    """Demonstrate Shadow command parsing."""
    print("\n" + "="*60)
    print("🎭 SHADOW COMMAND PARSING DEMO")
    print("="*60)
    
    # Create HAL manager and logger backend
    hal_manager = HALManager()
    backend = LoggerBackend()
    hal_manager.set_backend(backend)
    
    # Initialize backend
    if not backend.initialize():
        print("❌ Failed to initialize logger backend")
        return
    
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
    
    print("Testing Shadow commands:")
    for cmd in test_commands:
        print(f"  Command: {cmd.strip()}")
        result = parser.parse_command(cmd)
        print(f"  Result: {'✅ Success' if result else '❌ Failed'}")
        print()
    
    # Show command log
    print("Command Log:")
    commands = backend.get_command_log()
    for i, cmd in enumerate(commands[:5]):  # Show first 5 commands
        print(f"  {i+1}. {cmd['command']}: {cmd}")
    
    if len(commands) > 5:
        print(f"  ... and {len(commands) - 5} more commands")


def demo_sequence_engine():
    """Demonstrate sequence engine."""
    print("\n" + "="*60)
    print("🎬 SEQUENCE ENGINE DEMO")
    print("="*60)
    
    # Create HAL manager and logger backend
    hal_manager = HALManager()
    backend = LoggerBackend()
    hal_manager.set_backend(backend)
    
    # Initialize backend
    if not backend.initialize():
        print("❌ Failed to initialize logger backend")
        return
    
    # Create sequence engine
    sequence_engine = SequenceEngine(hal_manager)
    
    # Load wave sequence
    sequence_file = "sith_sequences/panel_wave.yaml"
    if os.path.exists(sequence_file):
        print(f"Loading sequence: {sequence_file}")
        if sequence_engine.load_sequence_file(sequence_file):
            print("✅ Sequence loaded successfully")
            
            # Show sequence info
            status = sequence_engine.get_status()
            print(f"  Steps: {status['total_steps']}")
            print(f"  State: {status['state']}")
            
            # Start sequence
            print("\nStarting sequence...")
            if sequence_engine.start_sequence():
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
            else:
                print("❌ Failed to start sequence")
        else:
            print("❌ Failed to load sequence")
    else:
        print(f"❌ Sequence file not found: {sequence_file}")


def demo_pty_emulator():
    """Demonstrate PTY emulator."""
    print("\n" + "="*60)
    print("🔌 PTY EMULATOR DEMO")
    print("="*60)
    
    def command_handler(command):
        print(f"  Received command: {command}")
    
    # Create PTY emulator
    emulator = PTYEmulator(command_handler)
    
    try:
        # Start emulator
        slave_path = emulator.start()
        print(f"✅ PTY emulator started on: {slave_path}")
        print(f"  You can connect to this device with: screen {slave_path}")
        print(f"  Or use it in your code with: serial.Serial('{slave_path}')")
        
        # Send some test commands
        print("\nSending test commands...")
        test_commands = [":OP01\r", ":CL01\r", ":SE02\r"]
        
        for cmd in test_commands:
            print(f"  Sending: {cmd.strip()}")
            emulator.send_command(cmd)
            time.sleep(0.1)
        
        print("\n✅ PTY emulator demo complete")
        
    except Exception as e:
        print(f"❌ PTY emulator error: {e}")
    finally:
        emulator.stop()
        print("🛑 PTY emulator stopped")


def main():
    """Main demo function."""
    print("🤖 SITH - Shadow Integration & Translation Hub")
    print("   Raspberry Pi R2-D2 Control System Demo")
    
    try:
        # Run demos
        demo_shadow_commands()
        demo_sequence_engine()
        demo_pty_emulator()
        
        print("\n" + "="*60)
        print("🎉 DEMO COMPLETE!")
        print("="*60)
        print("SITH is ready for development and testing.")
        print("Next steps:")
        print("  1. Run tests: python -m sith.tests.run_tests")
        print("  2. Connect real hardware")
        print("  3. Start building your R2-D2!")
        
    except KeyboardInterrupt:
        print("\n\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()