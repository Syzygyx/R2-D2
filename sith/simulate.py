#!/usr/bin/env python3
"""
SITH Simulation Script

Demonstrates SITH functionality with logger backend.
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


def demo_shadow_commands():
    """Demonstrate Shadow command parsing."""
    print("\n" + "="*60)
    print("🎭 SHADOW COMMAND PARSING SIMULATION")
    print("="*60)
    
    # Import here to avoid circular imports
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
    print("🎬 SEQUENCE ENGINE SIMULATION")
    print("="*60)
    
    # Import here to avoid circular imports
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
        return
    
    # Create sequence engine
    sequence_engine = SequenceEngine(hal_manager)
    
    # Create a simple test sequence
    test_sequence = {
        'name': 'Test Wave',
        'description': 'Simple wave simulation',
        'steps': [
            {
                'time_ms': 200,
                'servo_positions': [2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000],
                'description': 'Close all panels'
            },
            {
                'time_ms': 300,
                'servo_positions': [1000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000],
                'description': 'Open panel 1'
            },
            {
                'time_ms': 300,
                'servo_positions': [2000, 1000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000],
                'description': 'Open panel 2'
            },
            {
                'time_ms': 300,
                'servo_positions': [2000, 2000, 1000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000],
                'description': 'Open panel 3'
            },
            {
                'time_ms': 600,
                'servo_positions': [2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000],
                'description': 'Close all panels'
            }
        ]
    }
    
    print("Loading test sequence...")
    if sequence_engine.load_sequence(test_sequence):
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
            for i in range(10):
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


def demo_pty_emulator():
    """Demonstrate PTY emulator."""
    print("\n" + "="*60)
    print("🔌 PTY EMULATOR SIMULATION")
    print("="*60)
    
    # Import here to avoid circular imports
    from sith_emulator.pty_emulator import PTYEmulator
    
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
        
        print("\n✅ PTY emulator simulation complete")
        
    except Exception as e:
        print(f"❌ PTY emulator error: {e}")
    finally:
        emulator.stop()
        print("🛑 PTY emulator stopped")


def demo_interactive_simulation():
    """Interactive simulation mode."""
    print("\n" + "="*60)
    print("🎮 INTERACTIVE SIMULATION MODE")
    print("="*60)
    
    # Import here to avoid circular imports
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
        return
    
    # Create parser
    parser = ShadowParser(hal_manager)
    
    print("Enter Shadow commands (type 'quit' to exit):")
    print("Examples: :OP01, :CL01, :SE02, *H005, @0T5, $S")
    print()
    
    try:
        while True:
            command = input("SITH> ").strip()
            
            if command.lower() in ['quit', 'exit', 'q']:
                break
            
            if not command:
                continue
            
            # Add carriage return if not present
            if not command.endswith('\r'):
                command += '\r'
            
            print(f"Executing: {command}")
            result = parser.parse_command(command)
            print(f"Result: {'✅ Success' if result else '❌ Failed'}")
            print()
    
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted")
    
    # Show final command log
    print("\nFinal Command Log:")
    commands = backend.get_command_log()
    for i, cmd in enumerate(commands[-10:]):  # Show last 10 commands
        print(f"  {i+1}. {cmd['command']}: {cmd}")


def main():
    """Main simulation function."""
    print("🤖 SITH - Shadow Integration & Translation Hub")
    print("   Raspberry Pi R2-D2 Control System Simulation")
    
    try:
        # Run demos
        demo_shadow_commands()
        demo_sequence_engine()
        demo_pty_emulator()
        
        # Ask if user wants interactive mode
        print("\n" + "="*60)
        response = input("Would you like to try interactive mode? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            demo_interactive_simulation()
        
        print("\n" + "="*60)
        print("🎉 SIMULATION COMPLETE!")
        print("="*60)
        print("SITH simulation is working perfectly!")
        print("Next steps:")
        print("  1. Connect real hardware")
        print("  2. Run with actual Sabertooth/PCA9685")
        print("  3. Start building your R2-D2!")
        
    except KeyboardInterrupt:
        print("\n\n🛑 Simulation interrupted by user")
    except Exception as e:
        print(f"\n❌ Simulation error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()