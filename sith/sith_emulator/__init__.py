"""
SITH Emulator - PTY Serial Emulator

Provides a pseudo-terminal device for testing Shadow commands without hardware.
"""

from .pty_emulator import PTYEmulator
from .shadow_emulator import ShadowEmulator

__all__ = ["PTYEmulator", "ShadowEmulator"]