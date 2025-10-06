#!/usr/bin/env python3
"""
SITH Web Simulator

Web-based graphical simulation of R2-D2 control system.
"""

import os
import sys
import json
import time
import threading
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sith_core.hal import HALManager
from sith_core.parser import ShadowParser
from sith_core.sequence_engine import SequenceEngine
from sith_backends.sim.logger_backend import LoggerBackend

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sith_r2d2_simulator'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global SITH components
hal_manager = None
parser = None
sequence_engine = None
backend = None
current_sequence = None
simulation_running = False

def initialize_sith():
    """Initialize SITH components."""
    global hal_manager, parser, sequence_engine, backend
    
    # Create HAL manager and logger backend
    hal_manager = HALManager()
    backend = LoggerBackend()
    hal_manager.set_backend(backend)
    
    # Initialize backend
    if not backend.initialize():
        print("❌ Failed to initialize logger backend")
        return False
    
    # Create parser and sequence engine
    parser = ShadowParser(hal_manager)
    sequence_engine = SequenceEngine(hal_manager)
    
    print("✅ SITH web simulator initialized")
    return True

def simulation_loop():
    """Background simulation loop."""
    global simulation_running, sequence_engine
    
    while simulation_running:
        if sequence_engine and sequence_engine.current_sequence:
            sequence_engine.update()
            status = sequence_engine.get_status()
            
            # Emit status update
            socketio.emit('sequence_status', {
                'current_step': status['current_step'],
                'total_steps': status['total_steps'],
                'state': status['state'],
                'progress': status['progress']
            })
            
            if status['state'] == 'completed':
                socketio.emit('sequence_completed', {'message': 'Sequence completed!'})
        
        time.sleep(0.1)  # 10Hz update rate

@app.route('/')
def index():
    """Main simulation page."""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get current system status."""
    if not backend:
        return jsonify({'error': 'System not initialized'})
    
    status = backend.get_status()
    return jsonify(status)

@app.route('/api/command', methods=['POST'])
def send_command():
    """Send a Shadow command."""
    if not parser:
        return jsonify({'error': 'Parser not initialized'})
    
    data = request.get_json()
    command = data.get('command', '')
    
    if not command:
        return jsonify({'error': 'No command provided'})
    
    # Add carriage return if not present
    if not command.endswith('\r'):
        command += '\r'
    
    # Parse command
    result = parser.parse_command(command)
    
    # Get command log
    commands = backend.get_command_log() if backend else []
    
    return jsonify({
        'success': result,
        'command': command.strip(),
        'message': 'Command processed successfully' if result else 'Command failed',
        'command_count': len(commands)
    })

@app.route('/api/sequence', methods=['POST'])
def load_sequence():
    """Load a sequence."""
    if not sequence_engine:
        return jsonify({'error': 'Sequence engine not initialized'})
    
    data = request.get_json()
    sequence_data = data.get('sequence')
    
    if not sequence_data:
        return jsonify({'error': 'No sequence data provided'})
    
    # Load sequence
    result = sequence_engine.load_sequence(sequence_data)
    
    if result:
        global current_sequence
        current_sequence = sequence_data
        return jsonify({
            'success': True,
            'message': 'Sequence loaded successfully',
            'steps': len(sequence_data.get('steps', []))
        })
    else:
        return jsonify({'error': 'Failed to load sequence'})

@app.route('/api/sequence/start', methods=['POST'])
def start_sequence():
    """Start sequence execution."""
    if not sequence_engine:
        return jsonify({'error': 'Sequence engine not initialized'})
    
    if not sequence_engine.current_sequence:
        return jsonify({'error': 'No sequence loaded'})
    
    result = sequence_engine.start_sequence()
    
    if result:
        global simulation_running
        simulation_running = True
        
        # Start background simulation loop
        thread = threading.Thread(target=simulation_loop, daemon=True)
        thread.start()
        
        return jsonify({'success': True, 'message': 'Sequence started'})
    else:
        return jsonify({'error': 'Failed to start sequence'})

@app.route('/api/sequence/stop', methods=['POST'])
def stop_sequence():
    """Stop sequence execution."""
    if not sequence_engine:
        return jsonify({'error': 'Sequence engine not initialized'})
    
    sequence_engine.stop_sequence()
    
    global simulation_running
    simulation_running = False
    
    return jsonify({'success': True, 'message': 'Sequence stopped'})

@app.route('/api/sequence/pause', methods=['POST'])
def pause_sequence():
    """Pause sequence execution."""
    if not sequence_engine:
        return jsonify({'error': 'Sequence engine not initialized'})
    
    sequence_engine.pause_sequence()
    return jsonify({'success': True, 'message': 'Sequence paused'})

@app.route('/api/sequence/resume', methods=['POST'])
def resume_sequence():
    """Resume sequence execution."""
    if not sequence_engine:
        return jsonify({'error': 'Sequence engine not initialized'})
    
    sequence_engine.resume_sequence()
    return jsonify({'success': True, 'message': 'Sequence resumed'})

@app.route('/api/sequence/status')
def get_sequence_status():
    """Get sequence status."""
    if not sequence_engine:
        return jsonify({'error': 'Sequence engine not initialized'})
    
    status = sequence_engine.get_status()
    return jsonify(status)

@app.route('/api/commands')
def get_commands():
    """Get command log."""
    if not backend:
        return jsonify({'error': 'Backend not initialized'})
    
    commands = backend.get_command_log()
    return jsonify(commands)

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print('Client connected')
    emit('status', {'message': 'Connected to SITH simulator'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')

if __name__ == '__main__':
    # Initialize SITH
    if not initialize_sith():
        print("❌ Failed to initialize SITH")
        sys.exit(1)
    
    print("🌐 Starting SITH Web Simulator...")
    print("📱 Open your browser to: http://localhost:5000")
    
    # Run the web server
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)