"""
Simulation Backend for SITH

Provides ROS 2 simulation backend for Gazebo integration.
"""

import logging
from typing import List, Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from sith_backends.base import BackendBase

logger = logging.getLogger(__name__)


class SimBackend(BackendBase):
    """Simulation backend for ROS 2/Gazebo integration."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("sim")
        self.config = config or {}
        self.interfaces = {}
        self.ros2_available = False
    
    def initialize(self) -> bool:
        """Initialize simulation backend."""
        try:
            # Check if ROS 2 is available
            try:
                import rclpy
                self.ros2_available = True
                logger.info("ROS 2 available for simulation")
            except ImportError:
                logger.warning("ROS 2 not available - using basic simulation mode")
                self.ros2_available = False
            
            self.initialized = True
            logger.info("Simulation backend initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize simulation backend: {e}")
            return False
    
    def shutdown(self) -> None:
        """Shutdown simulation backend."""
        self.interfaces.clear()
        self.initialized = False
        logger.info("Simulation backend shutdown")
    
    def get_interfaces(self) -> List[Any]:
        """Get list of simulation interfaces."""
        return list(self.interfaces.values())
    
    def is_available(self) -> bool:
        """Check if backend is available."""
        return self.initialized
    
    def get_status(self) -> Dict[str, Any]:
        """Get backend status."""
        status = super().get_status()
        status.update({
            'ros2_available': self.ros2_available,
            'interfaces': {
                name: interface.get_status() if hasattr(interface, 'get_status') else {}
                for name, interface in self.interfaces.items()
            }
        })
        return status