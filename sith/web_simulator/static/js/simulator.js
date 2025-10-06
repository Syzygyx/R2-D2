// SITH R2-D2 Web Simulator JavaScript

class SITHSimulator {
    constructor() {
        this.socket = io();
        this.panels = [];
        this.currentSequence = null;
        this.isConnected = false;
        
        this.initializeEventListeners();
        this.initializeSocket();
        this.initializeDome();
        this.updateTime();
        
        // Update time every second
        setInterval(() => this.updateTime(), 1000);
    }
    
    initializeEventListeners() {
        // Command input
        document.getElementById('commandInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendCommand();
            }
        });
        
        document.getElementById('sendCommand').addEventListener('click', () => {
            this.sendCommand();
        });
        
        // Quick command buttons
        document.querySelectorAll('.cmd-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const command = e.target.getAttribute('data-cmd');
                document.getElementById('commandInput').value = command;
                this.sendCommand();
            });
        });
        
        // Sequence controls
        document.getElementById('loadWaveSequence').addEventListener('click', () => {
            this.loadWaveSequence();
        });
        
        document.getElementById('loadScreamSequence').addEventListener('click', () => {
            this.loadScreamSequence();
        });
        
        document.getElementById('startSequence').addEventListener('click', () => {
            this.startSequence();
        });
        
        document.getElementById('pauseSequence').addEventListener('click', () => {
            this.pauseSequence();
        });
        
        document.getElementById('resumeSequence').addEventListener('click', () => {
            this.resumeSequence();
        });
        
        document.getElementById('stopSequence').addEventListener('click', () => {
            this.stopSequence();
        });
        
        // Log controls
        document.getElementById('clearLog').addEventListener('click', () => {
            this.clearLog();
        });
        
        document.getElementById('refreshLog').addEventListener('click', () => {
            this.refreshLog();
        });
    }
    
    initializeSocket() {
        this.socket.on('connect', () => {
            this.isConnected = true;
            this.updateConnectionStatus(true);
            this.addLogEntry('Connected to SITH simulator', 'success');
        });
        
        this.socket.on('disconnect', () => {
            this.isConnected = false;
            this.updateConnectionStatus(false);
            this.addLogEntry('Disconnected from SITH simulator', 'error');
        });
        
        this.socket.on('sequence_status', (data) => {
            this.updateSequenceStatus(data);
        });
        
        this.socket.on('sequence_completed', (data) => {
            this.addLogEntry(data.message, 'success');
            this.updateSequenceButtons(false);
        });
        
        this.socket.on('status', (data) => {
            this.addLogEntry(data.message, 'info');
        });
    }
    
    initializeDome() {
        const dome = document.getElementById('dome');
        
        // Create 16 panels (4x4 grid)
        for (let i = 1; i <= 16; i++) {
            const panel = document.createElement('div');
            panel.className = 'panel closed';
            panel.id = `panel-${i}`;
            panel.textContent = i;
            panel.addEventListener('click', () => {
                this.togglePanel(i);
            });
            dome.appendChild(panel);
            this.panels.push(panel);
        }
    }
    
    updateConnectionStatus(connected) {
        const statusDot = document.getElementById('connectionStatus');
        const statusText = document.getElementById('connectionText');
        
        if (connected) {
            statusDot.style.background = '#4CAF50';
            statusText.textContent = 'Connected';
        } else {
            statusDot.style.background = '#F44336';
            statusText.textContent = 'Disconnected';
        }
    }
    
    updateTime() {
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        document.getElementById('currentTime').textContent = timeString;
    }
    
    async sendCommand() {
        const commandInput = document.getElementById('commandInput');
        const command = commandInput.value.trim();
        
        if (!command) return;
        
        try {
            const response = await fetch('/api/command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ command: command })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.addLogEntry(`✅ ${command} - ${result.message}`, 'success');
                this.updateCommandCount(result.command_count);
                
                // Update panel states based on command
                this.updatePanelsFromCommand(command);
            } else {
                this.addLogEntry(`❌ ${command} - ${result.message}`, 'error');
            }
            
            // Clear input
            commandInput.value = '';
            
        } catch (error) {
            this.addLogEntry(`❌ Error sending command: ${error.message}`, 'error');
        }
    }
    
    updatePanelsFromCommand(command) {
        // Parse panel commands and update visual state
        if (command.startsWith(':OP')) {
            const panelNum = parseInt(command.substring(3));
            if (panelNum === 0) {
                // Open all panels
                this.panels.forEach(panel => this.setPanelState(panel, 'open'));
            } else if (panelNum >= 1 && panelNum <= 16) {
                this.setPanelState(this.panels[panelNum - 1], 'open');
            }
        } else if (command.startsWith(':CL')) {
            const panelNum = parseInt(command.substring(3));
            if (panelNum === 0) {
                // Close all panels
                this.panels.forEach(panel => this.setPanelState(panel, 'closed'));
            } else if (panelNum >= 1 && panelNum <= 16) {
                this.setPanelState(this.panels[panelNum - 1], 'closed');
            }
        }
    }
    
    setPanelState(panel, state) {
        panel.className = `panel ${state}`;
        
        if (state === 'open') {
            panel.style.background = '#4CAF50';
        } else if (state === 'closed') {
            panel.style.background = '#333';
        }
    }
    
    togglePanel(panelNum) {
        const panel = this.panels[panelNum - 1];
        const isOpen = panel.classList.contains('open');
        
        if (isOpen) {
            this.setPanelState(panel, 'closed');
        } else {
            this.setPanelState(panel, 'open');
        }
    }
    
    async loadWaveSequence() {
        const waveSequence = {
            name: 'R2-D2 Wave',
            description: 'Classic wave sequence',
            steps: [
                {
                    time_ms: 200,
                    servo_positions: [2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000],
                    description: 'Close all panels'
                },
                {
                    time_ms: 300,
                    servo_positions: [1000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000],
                    description: 'Open panel 1'
                },
                {
                    time_ms: 300,
                    servo_positions: [2000, 1000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000],
                    description: 'Open panel 2'
                },
                {
                    time_ms: 300,
                    servo_positions: [2000, 2000, 1000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000],
                    description: 'Open panel 3'
                },
                {
                    time_ms: 300,
                    servo_positions: [2000, 2000, 2000, 1000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000],
                    description: 'Open panel 4'
                },
                {
                    time_ms: 600,
                    servo_positions: [2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000],
                    description: 'Close all panels'
                }
            ]
        };
        
        await this.loadSequence(waveSequence);
    }
    
    async loadScreamSequence() {
        const screamSequence = {
            name: 'R2-D2 Scream',
            description: 'Scream sequence with all panels',
            steps: [
                {
                    time_ms: 200,
                    servo_positions: [2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000],
                    description: 'Close all panels'
                },
                {
                    time_ms: 1000,
                    servo_positions: [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
                    description: 'SCREAM! Open all panels'
                },
                {
                    time_ms: 1500,
                    servo_positions: [2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000],
                    description: 'Close all panels'
                }
            ]
        };
        
        await this.loadSequence(screamSequence);
    }
    
    async loadSequence(sequenceData) {
        try {
            const response = await fetch('/api/sequence', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ sequence: sequenceData })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.currentSequence = sequenceData;
                this.addLogEntry(`✅ Loaded sequence: ${sequenceData.name} (${result.steps} steps)`, 'success');
                document.getElementById('startSequence').disabled = false;
            } else {
                this.addLogEntry(`❌ Failed to load sequence: ${result.error}`, 'error');
            }
            
        } catch (error) {
            this.addLogEntry(`❌ Error loading sequence: ${error.message}`, 'error');
        }
    }
    
    async startSequence() {
        try {
            const response = await fetch('/api/sequence/start', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.addLogEntry('🚀 Sequence started', 'success');
                this.updateSequenceButtons(true);
            } else {
                this.addLogEntry(`❌ Failed to start sequence: ${result.error}`, 'error');
            }
            
        } catch (error) {
            this.addLogEntry(`❌ Error starting sequence: ${error.message}`, 'error');
        }
    }
    
    async pauseSequence() {
        try {
            const response = await fetch('/api/sequence/pause', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.addLogEntry('⏸️ Sequence paused', 'info');
                this.updateSequenceButtons(true, true);
            }
            
        } catch (error) {
            this.addLogEntry(`❌ Error pausing sequence: ${error.message}`, 'error');
        }
    }
    
    async resumeSequence() {
        try {
            const response = await fetch('/api/sequence/resume', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.addLogEntry('▶️ Sequence resumed', 'success');
                this.updateSequenceButtons(true);
            }
            
        } catch (error) {
            this.addLogEntry(`❌ Error resuming sequence: ${error.message}`, 'error');
        }
    }
    
    async stopSequence() {
        try {
            const response = await fetch('/api/sequence/stop', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.addLogEntry('🛑 Sequence stopped', 'info');
                this.updateSequenceButtons(false);
                this.updateSequenceStatus({
                    current_step: 0,
                    total_steps: 0,
                    state: 'stopped',
                    progress: 0
                });
            }
            
        } catch (error) {
            this.addLogEntry(`❌ Error stopping sequence: ${error.message}`, 'error');
        }
    }
    
    updateSequenceButtons(running, paused = false) {
        document.getElementById('startSequence').disabled = running;
        document.getElementById('pauseSequence').disabled = !running || paused;
        document.getElementById('resumeSequence').disabled = !running || !paused;
        document.getElementById('stopSequence').disabled = !running;
    }
    
    updateSequenceStatus(data) {
        document.getElementById('sequenceStatus').textContent = data.state;
        document.getElementById('currentStep').textContent = `${data.current_step} / ${data.total_steps}`;
        
        const progress = Math.round(data.progress * 100);
        document.getElementById('progressFill').style.width = `${progress}%`;
        document.getElementById('progressText').textContent = `${progress}%`;
        
        // Update panel states based on sequence progress
        if (this.currentSequence && this.currentSequence.steps) {
            const step = this.currentSequence.steps[data.current_step];
            if (step && step.servo_positions) {
                this.updatePanelsFromSequence(step.servo_positions);
            }
        }
    }
    
    updatePanelsFromSequence(servoPositions) {
        // Update panel states based on servo positions
        servoPositions.forEach((position, index) => {
            if (index < this.panels.length) {
                const panel = this.panels[index];
                if (position === 1000) {
                    this.setPanelState(panel, 'open');
                } else if (position === 2000) {
                    this.setPanelState(panel, 'closed');
                }
            }
        });
    }
    
    addLogEntry(message, type = 'info') {
        const logContainer = document.getElementById('commandLog');
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${type}`;
        logEntry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        
        logContainer.appendChild(logEntry);
        logContainer.scrollTop = logContainer.scrollHeight;
        
        // Keep only last 100 entries
        while (logContainer.children.length > 100) {
            logContainer.removeChild(logContainer.firstChild);
        }
    }
    
    clearLog() {
        document.getElementById('commandLog').innerHTML = '<div class="log-entry">Log cleared...</div>';
    }
    
    async refreshLog() {
        try {
            const response = await fetch('/api/commands');
            const commands = await response.json();
            
            const logContainer = document.getElementById('commandLog');
            logContainer.innerHTML = '';
            
            commands.forEach(cmd => {
                const logEntry = document.createElement('div');
                logEntry.className = 'log-entry info';
                logEntry.textContent = `[${new Date(cmd.timestamp * 1000).toLocaleTimeString()}] ${cmd.command}`;
                logContainer.appendChild(logEntry);
            });
            
            logContainer.scrollTop = logContainer.scrollHeight;
            
        } catch (error) {
            this.addLogEntry(`❌ Error refreshing log: ${error.message}`, 'error');
        }
    }
    
    updateCommandCount(count) {
        document.getElementById('commandCount').textContent = count;
    }
}

// Initialize the simulator when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new SITHSimulator();
});