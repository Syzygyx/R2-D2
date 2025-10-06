#!/usr/bin/env python3
"""
SITH Web Simulator Backend Server
Provides a REST API and WebSocket server for real-time R2-D2 control
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sith_core.hal import HALManager
from sith_core.parser import ShadowParser
from sith_core.sequence_engine import SequenceEngine
from sith_backends.sim.logger_backend import LoggerBackend

try:
    from flask import Flask, request, jsonify, render_template
    from flask_socketio import SocketIO, emit, join_room, leave_room
    from flask_cors import CORS
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "flask-socketio", "flask-cors"])
    from flask import Flask, request, jsonify, render_template
    from flask_socketio import SocketIO, emit, join_room, leave_room
    from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SITHBackendServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'sith_r2d2_secret_key'
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Initialize SITH components
        self.hal_manager = HALManager()
        self.backend = LoggerBackend()
        self.hal_manager.set_backend(self.backend)
        self.backend.initialize()
        
        self.parser = ShadowParser(self.hal_manager)
        self.sequence_engine = SequenceEngine(self.hal_manager)
        
        # Connected clients
        self.clients = set()
        
        # Current state
        self.current_state = {
            'panels': {i: False for i in range(1, 17)},  # Panel states (1-16)
            'dome_rotation': 0.0,
            'status': 'ready',
            'command_count': 0,
            'last_command': None,
            'sequence_running': False,
            'current_sequence': None
        }
        
        self.setup_routes()
        self.setup_socketio_events()
        
    def setup_routes(self):
        """Setup REST API routes"""
        
        @self.app.route('/')
        def index():
            return render_template('3d_simulator.html')
        
        @self.app.route('/api/status')
        def get_status():
            """Get current R2-D2 status"""
            return jsonify({
                'success': True,
                'data': self.current_state
            })
        
        @self.app.route('/api/command', methods=['POST'])
        def send_command():
            """Send a Shadow command to R2-D2"""
            try:
                data = request.get_json()
                command = data.get('command', '').strip()
                
                if not command:
                    return jsonify({
                        'success': False,
                        'error': 'No command provided'
                    }), 400
                
                # Add carriage return if not present
                if not command.endswith('\r'):
                    command += '\r'
                
                # Parse and execute command
                result = self.parser.parse_command(command)
                
                # Update state based on command
                self.update_state_from_command(command)
                
                # Broadcast state update to all connected clients
                self.broadcast_state_update()
                
                # Log command
                self.current_state['command_count'] += 1
                self.current_state['last_command'] = command.strip()
                
                return jsonify({
                    'success': result,
                    'command': command.strip(),
                    'message': 'Command processed successfully' if result else 'Command failed',
                    'state': self.current_state
                })
                
            except Exception as e:
                logger.error(f"Error processing command: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/panels', methods=['GET'])
        def get_panels():
            """Get current panel states"""
            return jsonify({
                'success': True,
                'panels': self.current_state['panels']
            })
        
        @self.app.route('/api/panels/<int:panel_num>', methods=['POST'])
        def set_panel(panel_num):
            """Set individual panel state"""
            if panel_num < 1 or panel_num > 16:
                return jsonify({
                    'success': False,
                    'error': 'Panel number must be between 1 and 16'
                }), 400
            
            data = request.get_json()
            state = data.get('state', 'open') == 'open'
            
            self.current_state['panels'][panel_num] = state
            self.broadcast_state_update()
            
            return jsonify({
                'success': True,
                'panel': panel_num,
                'state': 'open' if state else 'closed'
            })
        
        @self.app.route('/api/panels/all', methods=['POST'])
        def set_all_panels():
            """Set all panels to same state"""
            data = request.get_json()
            state = data.get('state', 'open') == 'open'
            
            for i in range(1, 17):
                self.current_state['panels'][i] = state
            
            self.broadcast_state_update()
            
            return jsonify({
                'success': True,
                'state': 'open' if state else 'closed',
                'panels_affected': 16
            })
        
        @self.app.route('/api/sequences', methods=['GET'])
        def get_sequences():
            """Get available sequences"""
            sequences = self.sequence_engine.list_sequences()
            return jsonify({
                'success': True,
                'sequences': sequences
            })
        
        @self.app.route('/api/sequences/<sequence_name>', methods=['POST'])
        def run_sequence(sequence_name):
            """Run a sequence by name"""
            try:
                if self.sequence_engine.load_sequence(sequence_name):
                    self.sequence_engine.start_sequence()
                    self.current_state['sequence_running'] = True
                    self.current_state['current_sequence'] = sequence_name
                    self.broadcast_state_update()
                    
                    return jsonify({
                        'success': True,
                        'sequence': sequence_name,
                        'message': 'Sequence started'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': f'Sequence {sequence_name} not found'
                    }), 404
                    
            except Exception as e:
                logger.error(f"Error running sequence {sequence_name}: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/sequences/stop', methods=['POST'])
        def stop_sequence():
            """Stop current sequence"""
            self.sequence_engine.stop_sequence()
            self.current_state['sequence_running'] = False
            self.current_state['current_sequence'] = None
            self.broadcast_state_update()
            
            return jsonify({
                'success': True,
                'message': 'Sequence stopped'
            })
        
        @self.app.route('/api/reset', methods=['POST'])
        def reset_system():
            """Reset R2-D2 to default state"""
            # Close all panels
            for i in range(1, 17):
                self.current_state['panels'][i] = False
            
            # Reset other state
            self.current_state['dome_rotation'] = 0.0
            self.current_state['status'] = 'ready'
            self.current_state['sequence_running'] = False
            self.current_state['current_sequence'] = None
            
            self.broadcast_state_update()
            
            return jsonify({
                'success': True,
                'message': 'System reset'
            })
    
    def setup_socketio_events(self):
        """Setup WebSocket events"""
        
        @self.socketio.on('connect')
        def handle_connect():
            logger.info(f"Client connected: {request.sid}")
            self.clients.add(request.sid)
            
            # Send current state to new client
            emit('state_update', self.current_state)
            emit('log_message', {
                'message': 'Connected to SITH backend',
                'type': 'info',
                'timestamp': datetime.now().isoformat()
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            logger.info(f"Client disconnected: {request.sid}")
            self.clients.discard(request.sid)
        
        @self.socketio.on('join_room')
        def handle_join_room(data):
            room = data.get('room', 'default')
            join_room(room)
            emit('joined_room', {'room': room})
        
        @self.socketio.on('leave_room')
        def handle_leave_room(data):
            room = data.get('room', 'default')
            leave_room(room)
            emit('left_room', {'room': room})
        
        @self.socketio.on('send_command')
        def handle_command(data):
            command = data.get('command', '').strip()
            if not command:
                emit('error', {'message': 'No command provided'})
                return
            
            # Process command
            if not command.endswith('\r'):
                command += '\r'
            
            result = self.parser.parse_command(command)
            self.update_state_from_command(command)
            
            # Update state
            self.current_state['command_count'] += 1
            self.current_state['last_command'] = command.strip()
            
            # Broadcast to all clients
            self.broadcast_state_update()
            
            # Send response to sender
            emit('command_response', {
                'success': result,
                'command': command.strip(),
                'message': 'Command processed' if result else 'Command failed'
            })
        
        @self.socketio.on('request_state')
        def handle_state_request():
            emit('state_update', self.current_state)
    
    def update_state_from_command(self, command: str):
        """Update internal state based on Shadow command"""
        try:
            if command.startswith(':OP'):
                panel_num = int(command[3:5])
                if panel_num == 0:
                    # Open all panels
                    for i in range(1, 17):
                        self.current_state['panels'][i] = True
                elif 1 <= panel_num <= 16:
                    self.current_state['panels'][panel_num] = True
                    
            elif command.startswith(':CL'):
                panel_num = int(command[3:5])
                if panel_num == 0:
                    # Close all panels
                    for i in range(1, 17):
                        self.current_state['panels'][i] = False
                elif 1 <= panel_num <= 16:
                    self.current_state['panels'][panel_num] = False
                    
            elif command.startswith(':SE'):
                # Sequence command
                self.current_state['status'] = 'running_sequence'
                
        except (ValueError, IndexError) as e:
            logger.warning(f"Could not parse command for state update: {command} - {e}")
    
    def broadcast_state_update(self):
        """Broadcast current state to all connected clients"""
        self.socketio.emit('state_update', self.current_state)
    
    def broadcast_log_message(self, message: str, msg_type: str = 'info'):
        """Broadcast log message to all connected clients"""
        self.socketio.emit('log_message', {
            'message': message,
            'type': msg_type,
            'timestamp': datetime.now().isoformat()
        })
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Start the server"""
        logger.info(f"Starting SITH Backend Server on {host}:{port}")
        logger.info("Available endpoints:")
        logger.info("  GET  /api/status - Get current status")
        logger.info("  POST /api/command - Send Shadow command")
        logger.info("  GET  /api/panels - Get panel states")
        logger.info("  POST /api/panels/<num> - Set panel state")
        logger.info("  POST /api/panels/all - Set all panels")
        logger.info("  GET  /api/sequences - List sequences")
        logger.info("  POST /api/sequences/<name> - Run sequence")
        logger.info("  POST /api/sequences/stop - Stop sequence")
        logger.info("  POST /api/reset - Reset system")
        logger.info("  WebSocket: /socket.io/ - Real-time communication")
        
        self.socketio.run(self.app, host=host, port=port, debug=debug)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SITH Web Simulator Backend Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    server = SITHBackendServer()
    server.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == '__main__':
    main()