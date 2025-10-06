"""
Base Backend Class for SITH

Defines the interface that all backends must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BackendBase(ABC):
    """Base class for all SITH backends."""
    
    def __init__(self, name: str):
        self.name = name
        self.initialized = False
        self.interfaces = {}
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the backend."""
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the backend."""
        pass
    
    @abstractmethod
    def get_interfaces(self) -> List[Any]:
        """Get list of hardware interfaces provided by this backend."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if backend is available and ready."""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get backend status information."""
        return {
            'name': self.name,
            'initialized': self.initialized,
            'available': self.is_available(),
            'interfaces': list(self.interfaces.keys())
        }