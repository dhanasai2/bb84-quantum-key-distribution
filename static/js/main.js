// static/js/main.js - Main Application Logic
class QKDWebApp {
    constructor() {
        this.socket = io();
        this.setupEventListeners();
        this.setupSocketEvents();
        this.state = {
            theta: 0,
            phi: 0,
            eveActive: false
        };
    }
    
    setupEventListeners() {
        // Quantum state controls
        const thetaSlider = document.getElementById('theta-slider');
        const phiSlider = document.getElementById('phi-slider');
        
        thetaSlider.addEventListener('input', (e) => {
            this.state.theta = parseFloat(e.target.value);
            this.updateQuantumState();
        });
        
        phiSlider.addEventListener('input', (e) => {
            this.state.phi = parseFloat(e.target.value);
            this.updateQuantumState();
        });
        
        // Eavesdropper controls
        const eveActive = document.getElementById('eve-active');
        const attackSlider = document.getElementById('attack-slider');
        const thresholdSlider = document.getElementById('threshold-slider');
        
        eveActive.addEventListener('change', (e) => {
            this.state.eveActive = e.target.checked;
            this.updateEavesdropper();
        });
        
        attackSlider.addEventListener('input', (e) => {
            document.getElementById('attack-value').textContent = e.target.value + '%';
            this.updateEavesdropper();
        });
        
        thresholdSlider.addEventListener('input', (e) => {
            document.getElementById('threshold-value').textContent = e.target.value + '%';
            this.updateEavesdropper();
        });
        
        // Action buttons
        document.getElementById('start-btn').addEventListener('click', () => this.startTransfer());
        document.getElementById('demo-btn').addEventListener('click', () => this.startDemo());
        document.getElementById('attack-btn').addEventListener('click', () => this.simulateAttack());
        document.getElementById('stop-btn').addEventListener('click', () => this.stopTransfer());
        document.getElementById('reset-btn').addEventListener('click', () => this.resetSystem());
        
        // Update displays on slider change
        thetaSlider.addEventListener('input', (e) => {
            document.getElementById('theta-value').textContent = e.target.value + '°';
        });
        
        phiSlider.addEventListener('input', (e) => {
            document.getElementById('phi-value').textContent = e.target.value + '°';
        });
    }
    
    setupSocketEvents() {
        this.socket.on('connect', () => {
            console.log('Connected to QKD server');
            this.addLog('SYSTEM', 'Connected to Ultimate QKD System');
        });
        
        this.socket.on('bloch_update', (data) => {
            if (window.blochSphere) {
                window.blochSphere.updateStateVector(data.x, data.y, data.z);
            }
            this.updateQuantumInfo(data);
        });
        
        this.socket.on('qubit_transfer', (data) => {
            this.visualizeQubitTransfer(data);
            this.addLog('ALICE', `Sent ${data.basis}:${data.bit}`);
            this.addLog('BOB', `Received qubit ${data.qubit_number}`);
            
            // Update Bloch sphere during transfer
            if (window.blochSphere) {
                window.blochSphere.updateStateVector(data.x, data.y, data.z);
            }
        });
        
        this.socket.on('stats_update', (data) => {
            this.updateStatistics(data);
        });
        
        this.socket.on('transfer_complete', (data) => {
            this.addLog('SYSTEM', `✅ Transfer complete: ${data.total_sent} qubits`);
            this.addLog('SYSTEM', `Intercepts: ${data.intercepts}, Detections: ${data.detections}`);
            document.getElementById('protocol-status').textContent = 
                `Complete • Efficiency: 42% • QBER: 4.7% • Key: Generated`;
        });
        
        this.socket.on('system_reset', (data) => {
            this.addLog('SYSTEM', '🔄 System reset complete');
            location.reload(); // Simple reset approach
        });
    }
    
    updateQuantumState() {
        // Calculate Bloch coordinates
        const th = this.state.theta * Math.PI / 180;
        const ph = this.state.phi * Math.PI / 180;
        const x = Math.sin(th) * Math.cos(ph);
        const y = Math.sin(th) * Math.sin(ph);
        const z = Math.cos(th);
        
        // Update server
        fetch('/api/quantum_state', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ theta: this.state.theta, phi: this.state.phi })
        });
        
        // Update local display
        if (window.blochSphere) {
            window.blochSphere.updateStateVector(x, y, z);
        }
        this.updateQuantumInfo({ x, y, z, theta: this.state.theta, phi: this.state.phi });
    }
    
    updateEavesdropper() {
        const attackProb = document.getElementById('attack-slider').value;
        const threshold = document.getElementById('threshold-slider').value;
        
        fetch('/api/eavesdropper', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                active: this.state.eveActive,
                attack_prob: parseFloat(attackProb),
                threshold: parseFloat(threshold)
            })
        });
    }
    
    startTransfer() {
        const nQubits = document.getElementById('n-qubits').value;
        
        fetch('/api/start_transfer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ n_qubits: parseInt(nQubits) })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.addLog('SYSTEM', '🚀 Starting BB84 transfer');
                document.getElementById('protocol-status').textContent = 
                    'Active • Alice: Sending • Bob: Receiving • Key: Generating';
            }
        });
    }
    
    startDemo() {
        this.addLog('DEMO', '🔮 Starting quantum state demonstration');
        
        const states = [
            { theta: 0, phi: 0, name: '|0⟩' },
            { theta: 180, phi: 0, name: '|1⟩' },
            { theta: 90, phi: 0, name: '|+⟩' },
            { theta: 90, phi: 180, name: '|-⟩' },
            { theta: 90, phi: 90, name: '|+i⟩' }
        ];
        
        let index = 0;
        const demoInterval = setInterval(() => {
            if (index >= states.length) {
                clearInterval(demoInterval);
                this.addLog('DEMO', '✅ Demo complete');
                return;
            }
            
            const state = states[index];
            this.state.theta = state.theta;
            this.state.phi = state.phi;
            
            document.getElementById('theta-slider').value = state.theta;
            document.getElementById('phi-slider').value = state.phi;
            document.getElementById('theta-value').textContent = state.theta + '°';
            document.getElementById('phi-value').textContent = state.phi + '°';
            
            this.updateQuantumState();
            this.addLog('DEMO', `State: ${state.name} (θ=${state.theta}°, φ=${state.phi}°)`);
            
            index++;
        }, 2000);
    }
    
    simulateAttack() {
        if (!this.state.eveActive) {
            document.getElementById('eve-active').checked = true;
            this.state.eveActive = true;
            this.updateEavesdropper();
        }
        
        this.addLog('EVE', '🧨 Attack burst initiated');
        
        // Simulate attack burst
        let burstCount = 0;
        const attackInterval = setInterval(() => {
            if (burstCount >= 10) {
                clearInterval(attackInterval);
                return;
            }
            
            const intensity = Math.random() * 0.8 + 0.2;
            if (window.qkdCharts) {
                window.qkdCharts.updateEveChart(intensity);
            }
            
            burstCount++;
        }, 200);
    }
    
    stopTransfer() {
        fetch('/api/stop_transfer', { method: 'POST' })
        .then(() => {
            this.addLog('SYSTEM', '⏹ Transfer stopped');
            document.getElementById('protocol-status').textContent = 
                'Stopped • Alice: Idle • Bob: Idle • Key: None';
        });
    }
    
    resetSystem() {
        fetch('/api/reset', { method: 'POST' })
        .then(() => {
            this.addLog('SYSTEM', '🔄 Resetting system...');
        });
    }
    
    updateQuantumInfo(data) {
        // Determine state name
        let stateName = '|ψ⟩';
        if (Math.abs(data.theta) < 1) stateName = '|0⟩';
        else if (Math.abs(data.theta - 180) < 1) stateName = '|1⟩';
        else if (Math.abs(data.theta - 90) < 1) {
            if (Math.abs(data.phi) < 1) stateName = '|+⟩';
            else if (Math.abs(data.phi - 180) < 1) stateName = '|-⟩';
        }
        
        document.getElementById('state-name').textContent = stateName;
        document.getElementById('info-theta').textContent = data.theta.toFixed(1) + '°';
        document.getElementById('info-phi').textContent = data.phi.toFixed(1) + '°';
        document.getElementById('bloch-x').textContent = data.x.toFixed(3);
        document.getElementById('bloch-y').textContent = data.y.toFixed(3);
        document.getElementById('bloch-z').textContent = data.z.toFixed(3);
    }
    
    updateStatistics(data) {
        document.getElementById('stat-intercepts').textContent = data.intercepts;
        document.getElementById('stat-detections').textContent = data.detections;
        
        const qber = ((data.detections / (data.total_sent || 1)) * 100).toFixed(1) + '%';
        document.getElementById('stat-qber').textContent = qber;
        
        // Update charts if available
        if (window.qkdCharts && data.intercepts > 0) {
            const intensity = data.intercepts / data.total_sent;
            window.qkdCharts.updateEveChart(intensity);
            window.qkdCharts.updateSecurityChart(intensity * 0.15);
        }
    }
    
    visualizeQubitTransfer(data) {
        // Create flying qubit animation
        const channel = document.querySelector('.channel-line');
        const qubit = document.createElement('div');
        qubit.className = 'flying-qubit';
        qubit.style.backgroundColor = this.getQubitColor(data.bit, data.basis);
        qubit.textContent = `${data.bit}${data.basis}`;
        
        channel.appendChild(qubit);
        
        // Animate qubit
        setTimeout(() => {
            qubit.style.transform = 'translateX(400px)';
        }, 10);
        
        setTimeout(() => {
            if (qubit.parentNode) {
                qubit.parentNode.removeChild(qubit);
            }
        }, 2000);
    }
    
    getQubitColor(bit, basis) {
        const colors = {
            '0Z': '#73B7FF',
            '1Z': '#FF4CA3', 
            '0X': '#39D98A',
            '1X': '#FF9D42'
        };
        return colors[bit + basis] || '#50E3C2';
    }
    
    addLog(sender, message) {
        const log = document.getElementById('communication-log');
        const timestamp = new Date().toLocaleTimeString();
        const entry = document.createElement('div');
        entry.innerHTML = `<span class="timestamp">[${timestamp}]</span> <span class="sender">${sender}:</span> ${message}`;
        log.appendChild(entry);
        log.scrollTop = log.scrollHeight;
        
        // Keep only last 20 entries
        while (log.children.length > 20) {
            log.removeChild(log.firstChild);
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.qkdApp = new QKDWebApp();
});
