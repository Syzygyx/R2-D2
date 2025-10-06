#!/usr/bin/env python3
"""
SITH Simple Web Simulator

A simplified web-based R2-D2 simulator using only built-in Python modules.
"""

import os
import sys
import json
import time
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import socketserver

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sith_core.hal import HALManager
from sith_core.parser import ShadowParser
from sith_core.sequence_engine import SequenceEngine
from sith_backends.sim.logger_backend import LoggerBackend

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
        time.sleep(0.1)  # 10Hz update rate

class SITHRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for SITH simulator."""
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/':
            self.serve_index()
        elif path == '/api/status':
            self.serve_status()
        elif path == '/api/sequence/status':
            self.serve_sequence_status()
        elif path == '/api/commands':
            self.serve_commands()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/command':
            self.handle_command()
        elif path == '/api/sequence':
            self.handle_load_sequence()
        elif path == '/api/sequence/start':
            self.handle_start_sequence()
        elif path == '/api/sequence/stop':
            self.handle_stop_sequence()
        elif path == '/api/sequence/pause':
            self.handle_pause_sequence()
        elif path == '/api/sequence/resume':
            self.handle_resume_sequence()
        else:
            self.send_error(404, "Not Found")
    
    def serve_index(self):
        """Serve the main HTML page."""
        html_content = self.get_html_content()
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def serve_status(self):
        """Serve system status."""
        if not backend:
            self.send_json_response({'error': 'System not initialized'})
            return
        
        status = backend.get_status()
        self.send_json_response(status)
    
    def serve_sequence_status(self):
        """Serve sequence status."""
        if not sequence_engine:
            self.send_json_response({'error': 'Sequence engine not initialized'})
            return
        
        status = sequence_engine.get_status()
        self.send_json_response(status)
    
    def serve_commands(self):
        """Serve command log."""
        if not backend:
            self.send_json_response({'error': 'Backend not initialized'})
            return
        
        commands = backend.get_command_log()
        self.send_json_response(commands)
    
    def handle_command(self):
        """Handle command requests."""
        if not parser:
            self.send_json_response({'error': 'Parser not initialized'})
            return
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        command = data.get('command', '')
        
        if not command:
            self.send_json_response({'error': 'No command provided'})
            return
        
        # Add carriage return if not present
        if not command.endswith('\r'):
            command += '\r'
        
        # Parse command
        result = parser.parse_command(command)
        
        # Get command log
        commands = backend.get_command_log() if backend else []
        
        self.send_json_response({
            'success': result,
            'command': command.strip(),
            'message': 'Command processed successfully' if result else 'Command failed',
            'command_count': len(commands)
        })
    
    def handle_load_sequence(self):
        """Handle sequence loading."""
        if not sequence_engine:
            self.send_json_response({'error': 'Sequence engine not initialized'})
            return
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        sequence_data = data.get('sequence')
        
        if not sequence_data:
            self.send_json_response({'error': 'No sequence data provided'})
            return
        
        # Load sequence
        result = sequence_engine.load_sequence(sequence_data)
        
        if result:
            global current_sequence
            current_sequence = sequence_data
            self.send_json_response({
                'success': True,
                'message': 'Sequence loaded successfully',
                'steps': len(sequence_data.get('steps', []))
            })
        else:
            self.send_json_response({'error': 'Failed to load sequence'})
    
    def handle_start_sequence(self):
        """Handle sequence start."""
        if not sequence_engine:
            self.send_json_response({'error': 'Sequence engine not initialized'})
            return
        
        if not sequence_engine.current_sequence:
            self.send_json_response({'error': 'No sequence loaded'})
            return
        
        result = sequence_engine.start_sequence()
        
        if result:
            global simulation_running
            simulation_running = True
            
            # Start background simulation loop
            thread = threading.Thread(target=simulation_loop, daemon=True)
            thread.start()
            
            self.send_json_response({'success': True, 'message': 'Sequence started'})
        else:
            self.send_json_response({'error': 'Failed to start sequence'})
    
    def handle_stop_sequence(self):
        """Handle sequence stop."""
        if not sequence_engine:
            self.send_json_response({'error': 'Sequence engine not initialized'})
            return
        
        sequence_engine.stop_sequence()
        
        global simulation_running
        simulation_running = False
        
        self.send_json_response({'success': True, 'message': 'Sequence stopped'})
    
    def handle_pause_sequence(self):
        """Handle sequence pause."""
        if not sequence_engine:
            self.send_json_response({'error': 'Sequence engine not initialized'})
            return
        
        sequence_engine.pause_sequence()
        self.send_json_response({'success': True, 'message': 'Sequence paused'})
    
    def handle_resume_sequence(self):
        """Handle sequence resume."""
        if not sequence_engine:
            self.send_json_response({'error': 'Sequence engine not initialized'})
            return
        
        sequence_engine.resume_sequence()
        self.send_json_response({'success': True, 'message': 'Sequence resumed'})
    
    def send_json_response(self, data):
        """Send JSON response."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def get_html_content(self):
        """Get the HTML content for the simulator."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SITH - R2-D2 Web Simulator</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #fff;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        header {
            text-align: center;
            margin-bottom: 30px;
        }
        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .panel {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
        }
        .dome {
            width: 300px;
            height: 300px;
            border-radius: 50%;
            background: radial-gradient(circle, #4a4a4a 0%, #2a2a2a 100%);
            border: 4px solid #666;
            position: relative;
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            grid-template-rows: repeat(4, 1fr);
            gap: 2px;
            padding: 20px;
            box-shadow: 0 0 30px rgba(0,0,0,0.5);
            margin: 0 auto;
        }
        .dome-panel {
            background: #333;
            border: 2px solid #555;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8em;
            font-weight: bold;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .dome-panel.open {
            background: #4CAF50;
            border-color: #66BB6A;
            box-shadow: 0 0 15px rgba(76, 175, 80, 0.5);
        }
        .dome-panel.closed {
            background: #333;
            border-color: #555;
        }
        .command-input {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .command-input input {
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            background: rgba(255,255,255,0.9);
            color: #333;
        }
        .command-input button {
            padding: 12px 20px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
        }
        .command-buttons {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }
        .cmd-btn {
            padding: 10px;
            background: #2196F3;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9em;
        }
        .sequence-controls {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-bottom: 20px;
        }
        .sequence-controls button {
            padding: 12px;
            background: #9C27B0;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9em;
        }
        .sequence-controls button:disabled {
            background: #666;
            cursor: not-allowed;
            opacity: 0.5;
        }
        .log-content {
            background: rgba(0,0,0,0.3);
            border-radius: 8px;
            padding: 15px;
            height: 200px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        .log-entry {
            margin-bottom: 5px;
            padding: 5px;
            border-radius: 4px;
            background: rgba(255,255,255,0.05);
        }
        .log-entry.success {
            background: rgba(76, 175, 80, 0.2);
            border-left: 3px solid #4CAF50;
        }
        .log-entry.error {
            background: rgba(244, 67, 54, 0.2);
            border-left: 3px solid #F44336;
        }
        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(0,0,0,0.3);
            padding: 15px 20px;
            border-radius: 10px;
        }
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            .dome {
                width: 250px;
                height: 250px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 SITH - R2-D2 Web Simulator</h1>
            <p>Shadow Integration & Translation Hub - Browser Simulation</p>
        </header>

        <div class="main-content">
            <div class="panel">
                <h2>🎭 R2-D2 Dome</h2>
                <div class="dome" id="dome">
                    <!-- Panels will be generated by JavaScript -->
                </div>
            </div>

            <div class="panel">
                <h2>🎮 Control Panel</h2>
                
                <div class="command-input">
                    <input type="text" id="commandInput" placeholder="Enter Shadow command (e.g., :OP01)" value=":OP01">
                    <button onclick="sendCommand()">Send</button>
                </div>
                
                <h3>Quick Commands:</h3>
                <div class="command-buttons">
                    <button class="cmd-btn" onclick="sendQuickCommand(':OP01')">Open Panel 1</button>
                    <button class="cmd-btn" onclick="sendQuickCommand(':CL01')">Close Panel 1</button>
                    <button class="cmd-btn" onclick="sendQuickCommand(':OP00')">Open All</button>
                    <button class="cmd-btn" onclick="sendQuickCommand(':CL00')">Close All</button>
                    <button class="cmd-btn" onclick="sendQuickCommand(':SE02')">Wave Sequence</button>
                    <button class="cmd-btn" onclick="sendQuickCommand('*H005')">HP Flash</button>
                    <button class="cmd-btn" onclick="sendQuickCommand('@0T5')">Scream Display</button>
                    <button class="cmd-btn" onclick="sendQuickCommand('$S')">Scream Sound</button>
                </div>

                <h3>Sequence Control:</h3>
                <div class="sequence-controls">
                    <button onclick="loadWaveSequence()">Load Wave</button>
                    <button onclick="loadScreamSequence()">Load Scream</button>
                    <button id="startBtn" onclick="startSequence()" disabled>Start</button>
                    <button id="stopBtn" onclick="stopSequence()" disabled>Stop</button>
                </div>
            </div>
        </div>

        <div class="panel">
            <h2>📋 Command Log</h2>
            <div class="log-content" id="commandLog">
                <div class="log-entry">Ready to receive commands...</div>
            </div>
        </div>

        <div class="status-bar">
            <div>Status: <span id="status">Ready</span></div>
            <div>Commands: <span id="commandCount">0</span></div>
            <div>Time: <span id="currentTime"></span></div>
        </div>
    </div>

    <script>
        let panels = [];
        let currentSequence = null;

        // Initialize dome panels
        function initializeDome() {
            const dome = document.getElementById('dome');
            for (let i = 1; i <= 16; i++) {
                const panel = document.createElement('div');
                panel.className = 'dome-panel closed';
                panel.id = 'panel-' + i;
                panel.textContent = i;
                panel.onclick = () => togglePanel(i);
                dome.appendChild(panel);
                panels.push(panel);
            }
        }

        function togglePanel(panelNum) {
            const panel = panels[panelNum - 1];
            const isOpen = panel.classList.contains('open');
            panel.className = 'dome-panel ' + (isOpen ? 'closed' : 'open');
        }

        function setPanelState(panelNum, state) {
            if (panelNum === 0) {
                panels.forEach(panel => panel.className = 'dome-panel ' + state);
            } else if (panelNum >= 1 && panelNum <= 16) {
                panels[panelNum - 1].className = 'dome-panel ' + state;
            }
        }

        function sendCommand() {
            const command = document.getElementById('commandInput').value.trim();
            if (!command) return;

            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({command: command})
            })
            .then(response => response.json())
            .then(data => {
                addLogEntry((data.success ? '✅' : '❌') + ' ' + command + ' - ' + data.message, data.success ? 'success' : 'error');
                updateCommandCount(data.command_count);
                updatePanelsFromCommand(command);
            })
            .catch(error => addLogEntry('❌ Error: ' + error.message, 'error'));

            document.getElementById('commandInput').value = '';
        }

        function sendQuickCommand(command) {
            document.getElementById('commandInput').value = command;
            sendCommand();
        }

        function updatePanelsFromCommand(command) {
            if (command.startsWith(':OP')) {
                const panelNum = parseInt(command.substring(3));
                setPanelState(panelNum, 'open');
            } else if (command.startsWith(':CL')) {
                const panelNum = parseInt(command.substring(3));
                setPanelState(panelNum, 'closed');
            }
        }

        function loadWaveSequence() {
            const sequence = {
                name: 'R2-D2 Wave',
                steps: [
                    {time_ms: 200, servo_positions: [2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000], description: 'Close all'},
                    {time_ms: 300, servo_positions: [1000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000], description: 'Open 1'},
                    {time_ms: 300, servo_positions: [2000,1000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000], description: 'Open 2'},
                    {time_ms: 300, servo_positions: [2000,2000,1000,2000,2000,2000,2000,2000,2000,2000,2000,2000], description: 'Open 3'},
                    {time_ms: 600, servo_positions: [2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000], description: 'Close all'}
                ]
            };
            loadSequence(sequence);
        }

        function loadScreamSequence() {
            const sequence = {
                name: 'R2-D2 Scream',
                steps: [
                    {time_ms: 200, servo_positions: [2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000], description: 'Close all'},
                    {time_ms: 1000, servo_positions: [1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000], description: 'SCREAM!'},
                    {time_ms: 1500, servo_positions: [2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000], description: 'Close all'}
                ]
            };
            loadSequence(sequence);
        }

        function loadSequence(sequence) {
            fetch('/api/sequence', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({sequence: sequence})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    currentSequence = sequence;
                    addLogEntry('✅ Loaded: ' + sequence.name + ' (' + data.steps + ' steps)', 'success');
                    document.getElementById('startBtn').disabled = false;
                } else {
                    addLogEntry('❌ Failed to load: ' + data.error, 'error');
                }
            });
        }

        function startSequence() {
            fetch('/api/sequence/start', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    addLogEntry('🚀 Sequence started', 'success');
                    document.getElementById('startBtn').disabled = true;
                    document.getElementById('stopBtn').disabled = false;
                    runSequence();
                } else {
                    addLogEntry('❌ Failed to start: ' + data.error, 'error');
                }
            });
        }

        function stopSequence() {
            fetch('/api/sequence/stop', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                addLogEntry('🛑 Sequence stopped', 'info');
                document.getElementById('startBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
            });
        }

        function runSequence() {
            if (!currentSequence) return;
            
            let stepIndex = 0;
            const runStep = () => {
                if (stepIndex >= currentSequence.steps.length) {
                    addLogEntry('🎉 Sequence completed!', 'success');
                    document.getElementById('startBtn').disabled = false;
                    document.getElementById('stopBtn').disabled = true;
                    return;
                }
                
                const step = currentSequence.steps[stepIndex];
                addLogEntry('Step ' + (stepIndex + 1) + ': ' + step.description, 'info');
                
                // Update panels based on servo positions
                step.servo_positions.forEach((pos, index) => {
                    if (index < panels.length) {
                        panels[index].className = 'dome-panel ' + (pos === 1000 ? 'open' : 'closed');
                    }
                });
                
                stepIndex++;
                setTimeout(runStep, step.time_ms);
            };
            
            runStep();
        }

        function addLogEntry(message, type = 'info') {
            const log = document.getElementById('commandLog');
            const entry = document.createElement('div');
            entry.className = 'log-entry ' + type;
            entry.textContent = '[' + new Date().toLocaleTimeString() + '] ' + message;
            log.appendChild(entry);
            log.scrollTop = log.scrollHeight;
        }

        function updateCommandCount(count) {
            document.getElementById('commandCount').textContent = count;
        }

        function updateTime() {
            document.getElementById('currentTime').textContent = new Date().toLocaleTimeString();
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            initializeDome();
            setInterval(updateTime, 1000);
            addLogEntry('🤖 SITH Web Simulator Ready!', 'success');
        });

        // Handle Enter key in command input
        document.getElementById('commandInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendCommand();
        });
    </script>
</body>
</html>
        """

def main():
    """Main function to start the web simulator."""
    print("🤖 SITH Simple Web Simulator")
    print("=" * 40)
    
    # Initialize SITH
    if not initialize_sith():
        print("❌ Failed to initialize SITH")
        return 1
    
    # Start web server
    port = 5000
    handler = SITHRequestHandler
    
    with HTTPServer(('localhost', port), handler) as httpd:
        print(f"🌐 Starting web simulator on http://localhost:{port}")
        print("📱 Open your browser to view the simulator")
        print("🛑 Press Ctrl+C to stop")
        print()
        
        # Open browser
        threading.Timer(1.0, lambda: webbrowser.open(f'http://localhost:{port}')).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Simulator stopped by user")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())