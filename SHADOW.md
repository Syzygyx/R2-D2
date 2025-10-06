# Shadow/MarcDuino Protocol Documentation

## Overview

The Shadow system is a legacy R2-D2 control architecture developed by Marc Verdiell and maintained by Neil Hutchison. It consists of multiple Arduino-based controllers communicating via serial protocols to control R2-D2's dome panels, holoprojectors, displays, and audio systems.

## System Architecture

### Master-Slave Configuration
- **MarcDuinoMain**: Master controller for dome panel servos (11-13 servos)
- **MarcDuinoClient**: Slave controller for additional panels and features
- **Communication**: Serial UART at 9600 baud between master and slave
- **External Devices**: HP controllers, JEDI displays, CF-III sound systems

### Hardware Stack
```
┌─────────────────────────────────────┐
│           R2-D2 Dome                │
├─────────────────────────────────────┤
│     MarcDuinoMain (Master)          │
│  - 12 servo outputs (panels)        │
│  - UART to slave                    │
│  - UART to HP controller            │
│  - UART to sound system             │
├─────────────────────────────────────┤
│     MarcDuinoClient (Slave)         │
│  - Additional servos                │
│  - HP control forwarding            │
│  - I2C support                      │
└─────────────────────────────────────┘
```

## Command Protocol

### Command Structure
All commands follow the format: `[START_CHAR][COMMAND][ARGUMENTS]\r`

### Command Types

#### 1. Panel Commands (`:`)
Control dome panel servos and sequences.

| Command | Format | Description | Example |
|---------|--------|-------------|---------|
| `SE` | `:SExx` | Execute sequence | `:SE02` = Wave sequence |
| `OP` | `:OPxx` | Open panel | `:OP01` = Open panel 1, `:OP00` = Open all |
| `CL` | `:CLxx` | Close panel | `:CL01` = Close panel 1, `:CL00` = Close all |
| `RC` | `:RCxx` | RC control | `:RC01` = Panel 1 under RC, `:RC00` = All panels |
| `ST` | `:STxx` | Stop servo | `:ST01` = Stop panel 1, `:ST00` = Stop all |
| `HD` | `:HDxx` | Hold position | `:HD01` = Hold panel 1, `:HD00` = Hold all |

**Panel Numbers:**
- `01-11`: Master servos (dome panels)
- `12-13`: Slave servos (additional panels)
- `14`: Top panels group
- `15`: Bottom panels group
- `00`: All panels

#### 2. Holo Projector Commands (`*`)
Control holoprojector movement and lighting.

| Command | Format | Description | Example |
|---------|--------|-------------|---------|
| `H0` | `*H0xx` | HP flash | `*H005` = Flash for 5 seconds |
| `F0` | `*F0xx` | HP flicker | `*F010` = Flicker for 10 seconds |
| `ON` | `*ON00` | HP lights on | `*ON00` = Turn on all HP lights |
| `ST` | `*ST00` | HP stop | `*ST00` = Stop all HP movement |
| `RD` | `*RD00` | HP random | `*RD00` = Random HP movement |

#### 3. Display Commands (`@`)
Control JEDI display patterns and messages.

| Command | Format | Description | Example |
|---------|--------|-------------|---------|
| `T` | `@0Txx` | Display type | `@0T5` = Scream display |
| `W` | `@0Wxx` | Display wait | `@0W10` = Wait 10 seconds |
| `M` | `@xMtext` | Display message | `@1MHello` = Show "Hello" |

**Display Types:**
- `@0T1`: Normal display
- `@0T2`: Flash display
- `@0T4`: Short circuit display
- `@0T5`: Scream display
- `@0T6`: Leia message display
- `@0T92`: Spectrum display

#### 4. Sound Commands (`$`)
Control audio playback and sound effects.

| Command | Format | Description | Example |
|---------|--------|-------------|---------|
| `S` | `$S` | Scream sound | `$S` = Play scream |
| `W` | `$W` | Wave sound | `$W` = Play wave sound |
| `D` | `$D` | Disco music | `$D` = Play disco |
| `R` | `$R` | Random sounds | `$R` = Enable random sounds |
| `s` | `$s` | Stop sounds | `$s` = Stop all sounds |
| `C` | `$C` | Cantina music | `$C` = Play cantina |
| `L` | `$L` | Leia message | `$L` = Play Leia sound |
| `F` | `$F` | Faint sound | `$F` = Play faint sound |

**Sound Banks:**
- Bank 1: Basic sounds
- Bank 2: Chat sounds (`$2xx`)
- Bank 3: Special sounds (`$3xx`)

#### 5. Setup Commands (`#`)
Configure MarcDuino settings and parameters.

| Command | Format | Description | Example |
|---------|--------|-------------|---------|
| `SD` | `#SDxx` | Servo direction | `#SD00` = Forward, `#SD01` = Reversed |
| `SR` | `#SRxxy` | Individual servo | `#SR010` = Servo 1 forward, `#SR011` = Servo 1 reversed |
| `SS` | `#SSxx` | Startup sound | `#SS00` = None, `#SS01` = Default |
| `SQ` | `#SQxx` | Quiet mode | `#SQ00` = Chatty, `#SQ01` = Silent |
| `ST` | `#STxx` | Slave delay | `#ST050` = 50ms delay |
| `SM` | `#SMxx` | MP3 player | `#SM0` = SparkFun, `#SM1` = DFPlayer |

#### 6. I2C Commands (`&`)
Send I2C commands to slave devices.

| Format | Description | Example |
|--------|-------------|---------|
| `&addr,arg1,arg2` | I2C command | `&42,1,255` = Send 1,255 to device 42 |

**Argument Types:**
- Decimal: `210` (0-255)
- Hex: `xA7` (0x00-0xFF)
- Character: `'c'`
- String: `"hello"`

#### 7. Alternative Commands
- `!`: Alt1 sound commands (forwarded to sound system)
- `%`: Alt2 HP commands (forwarded to HP controller)

## Panel Sequences

### Sequence Definitions
Panel sequences are defined as arrays of servo positions with timing:

```c
sequence_t const panel_wave PROGMEM = {
    // time, servo1, servo2, ..., servo12, speed, first, last
    {30, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, -1, 1, 11},
    {30, 1000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, -1, 1, 11},
    // ... more steps
};
```

### Servo Position Constants
- `_OPN` (1000): Open position (1.0ms pulse)
- `_CLS` (2000): Closed position (2.0ms pulse)
- `_MID` (1750): Middle position (1.75ms pulse)
- `_NP` (-1): No pulse (servo off)

### Predefined Sequences

| ID | Name | Description |
|----|------|-------------|
| `:SE00` | Close All | Close all panels, servo off |
| `:SE01` | Scream | All panels open with sound/light effects |
| `:SE02` | Wave | Panels open one at a time |
| `:SE03` | Fast Wave | Quick back and forth wave |
| `:SE04` | Open Close Wave | Progressive open then close |
| `:SE05` | Marching Ants | Alternating panel pattern |
| `:SE06` | Short Circuit | Slow open with effects |
| `:SE07` | Cantina Dance | Rhythmic panel dance |
| `:SE08` | Leia | Special Leia sequence |
| `:SE09` | Disco | Long disco sequence (6+ minutes) |
| `:SE10` | Quiet Mode | Reset to quiet state |
| `:SE11` | Wide Awake | Random sounds, holos on |
| `:SE12` | Top RC | Top panels to RC control |
| `:SE13` | Awake | Random sounds, holos off |
| `:SE14` | Excited | Random sounds, holos on with lights |
| `:SE15` | Scream No Panels | Sound/light effects only |
| `:SE16` | Panel Wiggle | Quick open/close wiggle |

### Panel-Only Sequences (51-59)
- `:SE51-:SE59`: Same as above but without sound/light effects

## Hardware Interfaces

### Servo Control
- **Hardware**: PCA9685 16-channel PWM controller
- **Protocol**: I2C communication
- **Pulse Range**: 500-2500 microseconds
- **Frequency**: 50Hz (20ms period)
- **Speed Control**: Software-based speed limiting

### Motor Control
- **Hardware**: Sabertooth 2×12 motor driver
- **Protocol**: Serial UART at 2400 baud
- **Speed Range**: -100 to +100
- **Features**: Emergency stop, speed ramping

### LED Control
- **Hardware**: WS2812/NeoPixel strips
- **Protocol**: Single-wire data protocol
- **Features**: RGB color control, brightness, patterns

### Audio Control
- **Hardware**: SparkFun MP3 Trigger or DFPlayer Mini
- **Protocol**: Serial UART at 9600 baud
- **Features**: Multiple sound banks, random playback, volume control

## Communication Protocols

### Serial Communication
- **Baud Rate**: 9600 baud (8N1)
- **Flow Control**: None
- **Buffering**: Interrupt-driven with FIFO buffers
- **Error Handling**: Basic framing error detection

### I2C Communication
- **Speed**: 100kHz (standard mode)
- **Addressing**: 7-bit addresses
- **Pull-ups**: 10kΩ resistors
- **Error Handling**: ACK/NACK detection

## Configuration and EEPROM

### EEPROM Layout
| Address | Size | Description |
|---------|------|-------------|
| 0-1 | 2 bytes | Servo directions (bitmask) |
| 2 | 1 byte | Startup sound setting |
| 3 | 1 byte | Slave delay time |
| 4 | 1 byte | Last servo number |
| 5 | 1 byte | Random sound disabled |
| 6 | 1 byte | MP3 player selection |
| 7-8 | 2 bytes | CRC checksum |

### CRC Calculation
```c
uint16_t calc_crc() {
    uint16_t crc = 0;
    crc += eeprom_read_word((uint16_t*)servo_eeprom_addr);
    crc += eeprom_read_byte((uint8_t*)start_sound_eeprom_addr);
    crc += eeprom_read_byte((uint8_t*)random_sound_disabled);
    crc += eeprom_read_byte((uint8_t*)mp3_player_select_addr);
    return crc;
}
```

## Real-Time Control

### Interrupt System
- **Timer1**: Servo PWM generation (0.5μs resolution)
- **UART RX**: Command reception
- **UART TX**: Response transmission
- **Input Capture**: RC signal reading

### Servo Timing
- **Pulse Width**: 0.5-2.5ms (1000-5000 timer ticks)
- **Period**: 20ms (40000 timer ticks)
- **Resolution**: 0.5μs per tick
- **Update Rate**: 50Hz

### Sequence Execution
- **Update Rate**: 100Hz (10ms intervals)
- **Speed Control**: Gradual position changes
- **Callback System**: Completion callbacks for sequences

## Error Handling

### Command Validation
- **Length Check**: Commands must be 5 characters (`:CCxx\r`)
- **Range Check**: Panel numbers 1-16, values 0-255
- **Format Check**: Proper start/end characters

### Hardware Errors
- **Servo Timeout**: Stop servos if no valid position received
- **Communication**: Retry failed UART/I2C operations
- **Power**: Monitor supply voltage, graceful shutdown

### Safety Features
- **Emergency Stop**: Immediate servo shutdown
- **Watchdog Timer**: Reset if system hangs
- **Fuse Protection**: Hardware overcurrent protection

## Development and Debugging

### Debug Features
- **Serial Console**: Command echo and status messages
- **Error Messages**: Detailed error reporting
- **Status LEDs**: Visual system status indication
- **Memory Usage**: Monitor RAM/Flash usage

### Testing
- **Unit Tests**: Individual function testing
- **Integration Tests**: Full system testing
- **Hardware-in-the-Loop**: Real hardware testing
- **Simulation**: Software-only testing

## Migration to SITH

### Key Differences
| Aspect | Shadow | SITH |
|--------|--------|------|
| **Platform** | Arduino C | Raspberry Pi Python |
| **Sequences** | C arrays | YAML files |
| **Hardware** | Direct control | HAL abstraction |
| **AI** | None | TensorFlow Lite |
| **Simulation** | None | Gazebo/ROS 2 |
| **Testing** | Hardware required | PTY emulation |

### Porting Strategy
1. **Command Parser**: Direct port of command processing logic
2. **Sequence Engine**: Convert C arrays to YAML format
3. **HAL Interface**: Abstract hardware control
4. **Backend System**: Support multiple hardware backends
5. **Testing**: PTY emulator for hardware-free testing

## References

### Original Documentation
- **MarcDuinoMain**: Master controller source code
- **MarcDuinoClient**: Slave controller source code
- **Panel Sequences**: Predefined movement patterns
- **Hardware Schematics**: Circuit diagrams and pinouts

### Related Projects
- **R2-D2 Builders Club**: Community documentation
- **Shadow System**: Legacy control system
- **JEDI Display**: Holoprojector control
- **CF-III Sound**: Audio system integration

### Version History
- **v1.4r**: Original release (March 2013)
- **v1.5**: Hololights commands, panel glitch fix
- **v1.6**: CF-III program, MP3 and R2 Touch support
- **v1.7**: MarcDuino v2 support
- **v1.8**: I2C command parsing support
- **v3.0**: EEPROM support, 13 servo support (March 2020)
- **v3.7**: Latest version (December 2023)

---

*This documentation is based on analysis of the Shadow/MarcDuino source code and is intended to support the SITH modernization project.*