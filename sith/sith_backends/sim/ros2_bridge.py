"""
ROS 2 Bridge for SITH

Provides ROS 2 integration for Gazebo simulation.
"""

import logging
from typing import Dict, Any, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)


class ROS2Bridge:
    """ROS 2 bridge for simulation integration."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.ros2_available = False
        self.node = None
        
        # Check if ROS 2 is available
        try:
            import rclpy
            from rclpy.node import Node
            self.ros2_available = True
            logger.info("ROS 2 available for bridge")
        except ImportError:
            logger.warning("ROS 2 not available - bridge will run in simulation mode")
            self.ros2_available = False
    
    def initialize(self) -> bool:
        """Initialize ROS 2 bridge."""
        if not self.ros2_available:
            logger.info("ROS 2 bridge running in simulation mode")
            return True
        
        try:
            import rclpy
            from rclpy.node import Node
            
            if not rclpy.ok():
                rclpy.init()
            
            self.node = Node('sith_bridge')
            logger.info("ROS 2 bridge initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize ROS 2 bridge: {e}")
            return False
    
    def shutdown(self) -> None:
        """Shutdown ROS 2 bridge."""
        if self.node:
            try:
                self.node.destroy_node()
            except Exception as e:
                logger.error(f"Error destroying ROS 2 node: {e}")
        
        self.node = None
        logger.info("ROS 2 bridge shutdown")
    
    def is_available(self) -> bool:
        """Check if bridge is available."""
        return self.ros2_available
    
    def get_status(self) -> Dict[str, Any]:
        """Get bridge status."""
        return {
            'name': 'ros2_bridge',
            'ros2_available': self.ros2_available,
            'node_active': self.node is not None,
            'available': self.is_available()
        }