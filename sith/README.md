# SITH - Shadow Integration & Translation Hub

A Raspberry Pi-based modernization of R2-D2 control systems, porting legacy Shadow/MarcDuino control to modern Python with optional ROS 2 simulation and on-device TensorFlow Lite vision.

## Architecture

SITH provides a thin, testable software layer independent of hardware:

- **HAL Interfaces** (`motors`, `dome`, `servos`, `leds`, `sound`)  
  - `RealBackend`: Sabertooth (UART), PCA9685 (I²C), GPIO, NeoPixels, audio  
  - `LoggerBackend` / `SimBackend`: Logs or publishes to ROS topics, no hardware needed
- **MarcDuino/Shadow Emulator**: PTY serial device parsing ASCII commands → HAL calls
- **Sequence Engine**: YAML-defined timed actions (servo moves, sounds, lights)
- **AI Module**: TFLite face/person detection → dome "suggestions"
- **Control Modes**: Manual > Assisted > Autonomous
- **Simulation**: Gazebo + ROS 2 URDF (diff-drive, dome joint, hero servos)

## Directory Structure

```
sith/
├── sith_core/          # Parser, HAL, sequence engine
├── sith_backends/
│   ├── real/           # Sabertooth, PCA9685, GPIO, LEDs, sound
│   └── sim/            # LoggerBackend, ROS 2 bridge
├── sith_emulator/      # PTY serial emulator
├── sith_sequences/     # YAML routines
├── simulation/         # URDF, controllers, launch files
├── curriculum/         # Lessons, slides, notebooks
├── docs/               # Wiring diagrams, setup, safety
└── tests/              # Pytest unit tests
```

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Run emulator: `python -m sith_emulator`
3. Test sequences: `python -m sith_core.sequence_engine`
4. Hardware mode: `python -m sith_backends.real`

## Shadow Protocol Support

SITH maintains compatibility with the original Shadow/MarcDuino command protocol:

- **Panel Commands**: `:OPxx`, `:CLxx`, `:RCxx`, `:STxx`, `:HDxx`, `:SExx`
- **HP Commands**: `*CCxx` (holo projector control)
- **Display Commands**: `@CCxx` (JEDI display control)
- **Sound Commands**: `$CCxx` (audio control)
- **Setup Commands**: `#CCxx` (configuration)
- **I2C Commands**: `&device,arg1,arg2\r`

## License

MIT License - see LICENSE file for details.