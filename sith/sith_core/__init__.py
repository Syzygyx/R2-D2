"""
SITH Core - Shadow Integration & Translation Hub

Core components for R2-D2 control system modernization.
"""

__version__ = "0.1.0"
__author__ = "Syzygyx, Inc."

from .hal import HALInterface
from .parser import ShadowParser
from .sequence_engine import SequenceEngine

__all__ = ["HALInterface", "ShadowParser", "SequenceEngine"]