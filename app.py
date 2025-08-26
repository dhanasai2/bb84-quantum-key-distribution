from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import qiskit
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_bloch_multivector
from qiskit.quantum_info import Statevector
import numpy as np
import random
import threading
import time
import base64
import io
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime
port = int(os.getenv('PORT', 5000))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'quantum_secret_key_bb84'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Global variables for quantum state
quantum_state = {
    'theta': 90,
    'phi': 90,
    'active': False,
    'bits_sent': 0,
    'bits_received': 0,
    'current_bit': None,
    'basis_choice': None,
    'alice_basis': None,
    'bob_basis': None
}

eavesdropper_state = {
    'active': False,
    'attack_percentage': 69,
    'detection_threshold': 11,
    'intercepts': 0,
    'detections': 0,
    'qber': 2.0,
    'history': {'time': [], 'intercepts': [], 'detections': [], 'qber': []},
    'current_attack': None,
    'last_intercept_time': None
}

security_metrics = {
    'status': 'SECURE',
    'key_rate': 336,
    'efficiency': 42,
    'history': {'time': [], 'key_rate': [], 'efficiency': [], 'status': []},
    'total_key_bits': 0,
    'secure_key_bits': 0
}

demo_active = False
update_thread = None
simulation_time = 0

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('quantum_update', quantum_state)
    emit('eavesdropper_update', eavesdropper_state)
    emit('security_update', security_metrics)
    emit('detailed_log', {'message': 'Client connected to BB84 system', 'type': 'system'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('start_demo')
def handle_start_demo():
    global demo_active, update_thread, simulation_time
    print("Starting BB84 Demo")
    demo_active = True
    simulation_time = 0
    
    # Don't reset counters on start, only on reset
    if update_thread is None or not update_thread.is_alive():
        update_thread = socketio.start_background_task(quantum_simulation_loop)
    
    emit('demo_status', {'status': 'started'}, broadcast=True)
    emit('detailed_log', {'message': 'BB84 demonstration started', 'type': 'demo'}, broadcast=True)

@socketio.on('stop_demo')
def handle_stop_demo():
    global demo_active
    print("Stopping BB84 Demo")
    demo_active = False
    emit('demo_status', {'status': 'stopped'}, broadcast=True)
    emit('detailed_log', {'message': 'BB84 demonstration stopped', 'type': 'demo'}, broadcast=True)

@socketio.on('reset_demo')
def handle_reset_demo():
    global demo_active, quantum_state, eavesdropper_state, security_metrics, simulation_time
    print("Resetting BB84 Demo - Complete Reset")
    
    # Stop demo first
    demo_active = False
    simulation_time = 0
    
    # Complete reset of all states
    quantum_state.update({
        'theta': 90, 'phi': 90, 'active': False, 
        'bits_sent': 0, 'bits_received': 0, 
        'current_bit': None, 'basis_choice': None,
        'alice_basis': None, 'bob_basis': None
    })
    
    eavesdropper_state.update({
        'intercepts': 0, 'detections': 0, 'qber': 2.0,
        'history': {'time': [], 'intercepts': [], 'detections': [], 'qber': []},
        'current_attack': None, 'last_intercept_time': None
    })
    
    security_metrics.update({
        'status': 'SECURE', 'key_rate': 336, 'efficiency': 42,
        'history': {'time': [], 'key_rate': [], 'efficiency': [], 'status': []},
        'total_key_bits': 0, 'secure_key_bits': 0
    })
    
    # Emit reset state to all clients
    emit('quantum_update', quantum_state, broadcast=True)
    emit('eavesdropper_update', eavesdropper_state, broadcast=True)
    emit('security_update', security_metrics, broadcast=True)
    emit('demo_status', {'status': 'reset'}, broadcast=True)
    emit('detailed_log', {'message': 'System completely reset to initial state', 'type': 'system'}, broadcast=True)
    emit('clear_logs', {}, broadcast=True)  # Clear all logs

@socketio.on('toggle_eavesdropper')
def handle_toggle_eavesdropper(data):
    eavesdropper_state['active'] = data['active']
    status = 'activated' if data['active'] else 'deactivated'
    print(f"Eavesdropper {status}")
    emit('eavesdropper_update', eavesdropper_state, broadcast=True)
    emit('detailed_log', {
        'message': f'Eavesdropper {status} with {eavesdropper_state["attack_percentage"]}% attack rate', 
        'type': 'eavesdropper'
    }, broadcast=True)

@socketio.on('update_attack_params')
def handle_attack_params(data):
    eavesdropper_state['attack_percentage'] = data['attack_percentage']
    eavesdropper_state['detection_threshold'] = data['detection_threshold']
    emit('eavesdropper_update', eavesdropper_state, broadcast=True)
    emit('detailed_log', {
        'message': f'Attack parameters updated: {data["attack_percentage"]}% attack, {data["detection_threshold"]}% detection threshold',
        'type': 'eavesdropper'
    }, broadcast=True)

def quantum_simulation_loop():
    """Main simulation loop for real-time quantum updates"""
    global demo_active, simulation_time
    
    socketio.sleep(1)
    print("Starting quantum simulation loop")
    
    while demo_active:
        try:
            simulation_time += 0.5
            
            # Simulate BB84 bit transfer
            simulate_bb84_bit_transfer()
            
            # Update eavesdropper activity if active
            if eavesdropper_state['active']:
                simulate_eavesdropper_activity()
            
            # Update security analysis
            update_security_metrics()
            
            # Generate 3D Bloch sphere visualization
            quantum_viz = generate_3d_bloch_sphere()
            
            # Generate graphs for eavesdropper and security
            eavesdrop_graph = generate_eavesdropper_graph()
            security_graph = generate_security_graph()
            
            # Emit updates
            socketio.emit('quantum_update', {
                **quantum_state,
                'visualization': quantum_viz
            })
            socketio.emit('eavesdropper_update', {
                **eavesdropper_state,
                'graph': eavesdrop_graph
            })
            socketio.emit('security_update', {
                **security_metrics,
                'graph': security_graph
            })
            socketio.emit('bit_transfer_update', {
                'alice_sending': quantum_state['current_bit'],
                'bob_receiving': quantum_state['basis_choice'],
                'alice_basis': quantum_state['alice_basis'],
                'bob_basis': quantum_state['bob_basis'],
                'progress': min(100, (quantum_state['bits_sent'] / 50) * 100),
                'success': quantum_state['alice_basis'] == quantum_state['bob_basis'] if quantum_state['alice_basis'] else None
            })
            
            print(f"Time: {simulation_time:.1f}s, Bits: {quantum_state['bits_sent']}, Intercepts: {eavesdropper_state['intercepts']}")
            
            socketio.sleep(0.5)
            
        except Exception as e:
            print(f"Error in simulation loop: {e}")
            import traceback
            traceback.print_exc()
            break
    
    print("Quantum simulation loop ended")

def simulate_bb84_bit_transfer():
    """Enhanced BB84 bit transfer simulation with detailed logging"""
    global quantum_state
    
    # Generate random bit and basis for Alice
    quantum_state['current_bit'] = random.choice([0, 1])
    quantum_state['alice_basis'] = random.choice(['rectilinear', 'diagonal'])
    
    # Bob randomly chooses measurement basis
    quantum_state['bob_basis'] = random.choice(['rectilinear', 'diagonal'])
    quantum_state['basis_choice'] = quantum_state['bob_basis']
    
    # Set quantum state based on Alice's encoding
    if quantum_state['alice_basis'] == 'rectilinear':
        if quantum_state['current_bit'] == 0:
            quantum_state['theta'] = 0    # |0⟩ state
            quantum_state['phi'] = 0
        else:
            quantum_state['theta'] = 180  # |1⟩ state
            quantum_state['phi'] = 0
    else:  # diagonal basis
        if quantum_state['current_bit'] == 0:
            quantum_state['theta'] = 90   # |+⟩ state
            quantum_state['phi'] = 0
        else:
            quantum_state['theta'] = 90   # |-⟩ state
            quantum_state['phi'] = 180
    
    # Add some quantum noise
    quantum_state['theta'] += random.uniform(-3, 3)
    quantum_state['phi'] += random.uniform(-3, 3)
    
    quantum_state['bits_sent'] += 1
    
    # Bob measures (successful if bases match)
    basis_match = quantum_state['alice_basis'] == quantum_state['bob_basis']
    if basis_match:
        quantum_state['bits_received'] += 1
        security_metrics['secure_key_bits'] += 1
    
    security_metrics['total_key_bits'] += 1
    quantum_state['active'] = True
    
    # Emit detailed transfer log
    socketio.emit('detailed_log', {
        'message': f'Bit {quantum_state["current_bit"]} sent via {quantum_state["alice_basis"]} basis, Bob measured with {quantum_state["bob_basis"]} basis - {"SUCCESS" if basis_match else "DISCARDED"}',
        'type': 'transfer'
    })

def simulate_eavesdropper_activity():
    """Enhanced eavesdropper simulation with detailed attack logging"""
    global eavesdropper_state, simulation_time
    
    attack_prob = eavesdropper_state['attack_percentage'] / 100
    
    # Simulate intercepts
    if random.random() < attack_prob * 0.3:
        eavesdropper_state['intercepts'] += 1
        eavesdropper_state['current_attack'] = f'Intercepted bit {quantum_state["current_bit"]}'
        eavesdropper_state['last_intercept_time'] = datetime.now().strftime('%H:%M:%S')
        
        # Detection probability
        if random.random() < (eavesdropper_state['detection_threshold'] / 100):
            eavesdropper_state['detections'] += 1
            socketio.emit('detailed_log', {
                'message': f'SECURITY ALERT: Eavesdropping detected! Intercept #{eavesdropper_state["intercepts"]} at {eavesdropper_state["last_intercept_time"]}',
                'type': 'security_alert'
            })
        else:
            socketio.emit('detailed_log', {
                'message': f'Eavesdropper attack: Bit intercepted but undetected - Attack #{eavesdropper_state["intercepts"]}',
                'type': 'eavesdropper'
            })
    
    # Update QBER with realistic quantum effects
    if eavesdropper_state['intercepts'] > 0:
        base_error = (eavesdropper_state['detections'] / eavesdropper_state['intercepts']) * 100
        eavesdropper_state['qber'] = min(25.0, base_error + random.uniform(-0.5, 1.5))
    else:
        eavesdropper_state['qber'] = 2.0 + random.uniform(0, 0.5)
    
    # Store history for graphs
    eavesdropper_state['history']['time'].append(simulation_time)
    eavesdropper_state['history']['intercepts'].append(eavesdropper_state['intercepts'])
    eavesdropper_state['history']['detections'].append(eavesdropper_state['detections'])
    eavesdropper_state['history']['qber'].append(eavesdropper_state['qber'])
    
    # Keep only last 20 data points
    for key in eavesdropper_state['history']:
        if len(eavesdropper_state['history'][key]) > 20:
            eavesdropper_state['history'][key] = eavesdropper_state['history'][key][-20:]

def update_security_metrics():
    """Enhanced security analysis with detailed status reporting"""
    global security_metrics, simulation_time
    
    qber = eavesdropper_state['qber']
    old_status = security_metrics['status']
    
    # Realistic security assessment
    if qber < 5:
        security_metrics['status'] = 'SECURE'
        security_metrics['key_rate'] = random.randint(300, 400)
        security_metrics['efficiency'] = random.randint(40, 50)
    elif qber < 11:
        security_metrics['status'] = 'WARNING'
        security_metrics['key_rate'] = random.randint(200, 300)
        security_metrics['efficiency'] = random.randint(25, 40)
    else:
        security_metrics['status'] = 'COMPROMISED'
        security_metrics['key_rate'] = random.randint(50, 150)
        security_metrics['efficiency'] = random.randint(10, 25)
    
    # Log security status changes
    if old_status != security_metrics['status']:
        socketio.emit('detailed_log', {
            'message': f'SECURITY STATUS CHANGED: {old_status} → {security_metrics["status"]} (QBER: {qber:.1f}%)',
            'type': 'security_status'
        })
    
    # Store history
    security_metrics['history']['time'].append(simulation_time)
    security_metrics['history']['key_rate'].append(security_metrics['key_rate'])
    security_metrics['history']['efficiency'].append(security_metrics['efficiency'])
    security_metrics['history']['status'].append(security_metrics['status'])
    
    # Keep only last 20 data points
    for key in security_metrics['history']:
        if len(security_metrics['history'][key]) > 20:
            security_metrics['history'][key] = security_metrics['history'][key][-20:]

def generate_3d_bloch_sphere():
    """Generate proper 3D Bloch sphere visualization"""
    try:
        # Create quantum circuit
        qc = QuantumCircuit(1)
        
        # Apply rotations based on current state
        theta_rad = np.radians(quantum_state['theta'])
        phi_rad = np.radians(quantum_state['phi'])
        
        qc.ry(theta_rad, 0)
        qc.rz(phi_rad, 0)
        
        # Get statevector
        simulator = AerSimulator(method='statevector')
        transpiled_qc = transpile(qc, simulator)
        job = simulator.run(transpiled_qc, shots=1)
        result = job.result()
        statevector = result.get_statevector(transpiled_qc)
        
        # Create 3D Bloch sphere
        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(111, projection='3d')
        
        # Draw sphere
        u = np.linspace(0, 2 * np.pi, 50)
        v = np.linspace(0, np.pi, 50)
        sphere_x = np.outer(np.cos(u), np.sin(v))
        sphere_y = np.outer(np.sin(u), np.sin(v))
        sphere_z = np.outer(np.ones(np.size(u)), np.cos(v))
        
        ax.plot_surface(sphere_x, sphere_y, sphere_z, alpha=0.15, color='cyan')
        
        # Calculate Bloch vector
        x = 2 * np.real(statevector[0] * np.conj(statevector[1]))
        y = 2 * np.imag(statevector[1] * np.conj(statevector[0]))
        z = np.abs(statevector[0])**2 - np.abs(statevector[1])**2
        
        # Draw state vector with better visibility
        ax.quiver(0, 0, 0, x, y, z, color='#FF6B6B', arrow_length_ratio=0.1, linewidth=4)
        
        # Add coordinate axes
        ax.quiver(0, 0, 0, 1.2, 0, 0, color='white', alpha=0.7, linewidth=2)
        ax.quiver(0, 0, 0, 0, 1.2, 0, color='white', alpha=0.7, linewidth=2)
        ax.quiver(0, 0, 0, 0, 0, 1.2, color='white', alpha=0.7, linewidth=2)
        
        # Labels
        ax.text(1.3, 0, 0, 'X', fontsize=14, color='white')
        ax.text(0, 1.3, 0, 'Y', fontsize=14, color='white')
        ax.text(0, 0, 1.3, 'Z', fontsize=14, color='white')
        
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
        ax.set_zlim(-1.2, 1.2)
        ax.set_facecolor('#0D1117')
        fig.patch.set_facecolor('#0D1117')
        
        # Add title with current bit info
        bit_info = f"Bit: {quantum_state['current_bit']}, Alice: {quantum_state['alice_basis']}, Bob: {quantum_state['bob_basis']}"
        ax.set_title(f'Quantum State Bloch Sphere\n{bit_info}', color='white', fontsize=12)
        
        # Hide axes
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])
        
        # Convert to base64
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=100, facecolor='#0D1117')
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close(fig)
        
        return img_str
        
    except Exception as e:
        print(f"Error generating 3D Bloch sphere: {e}")
        return generate_fallback_sphere()

def generate_fallback_sphere():
    """Generate a simple 3D sphere as fallback"""
    try:
        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(111, projection='3d')
        
        # Create sphere
        u = np.linspace(0, 2 * np.pi, 30)
        v = np.linspace(0, np.pi, 20)
        x = np.outer(np.cos(u), np.sin(v))
        y = np.outer(np.sin(u), np.sin(v))
        z = np.outer(np.ones(np.size(u)), np.cos(v))
        
        ax.plot_surface(x, y, z, alpha=0.3, color='cyan')
        
        # Add state vector
        theta_rad = np.radians(quantum_state['theta'])
        phi_rad = np.radians(quantum_state['phi'])
        
        vec_x = np.sin(theta_rad) * np.cos(phi_rad)
        vec_y = np.sin(theta_rad) * np.sin(phi_rad)
        vec_z = np.cos(theta_rad)
        
        ax.quiver(0, 0, 0, vec_x, vec_y, vec_z, color='#FF6B6B', linewidth=4)
        
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
        ax.set_zlim(-1.2, 1.2)
        ax.set_facecolor('#0D1117')
        fig.patch.set_facecolor('#0D1117')
        ax.set_title(f'Quantum State\nθ={quantum_state["theta"]:.0f}°, φ={quantum_state["phi"]:.0f}°', 
                    color='white')
        
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=100, facecolor='#0D1117')
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close(fig)
        
        return img_str
    except:
        return None

def generate_eavesdropper_graph():
    """Generate real-time eavesdropper activity graph with dark theme"""
    try:
        if len(eavesdropper_state['history']['time']) < 2:
            return None
            
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor('#0D1117')
        ax.set_facecolor('#161B22')
        
        times = eavesdropper_state['history']['time']
        intercepts = eavesdropper_state['history']['intercepts']
        detections = eavesdropper_state['history']['detections']
        
        ax.plot(times, intercepts, '#FF6B6B', label='Intercepts', linewidth=2)
        ax.plot(times, detections, '#FFB366', label='Detections', linewidth=2)
        
        ax.set_xlabel('Time (s)', color='white')
        ax.set_ylabel('Count', color='white')
        ax.set_title('Eavesdropper Activity Over Time', color='white')
        ax.legend()
        ax.grid(True, alpha=0.3, color='white')
        
        ax.tick_params(colors='white')
        
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=100, facecolor='#0D1117')
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close(fig)
        
        return img_str
    except Exception as e:
        print(f"Error generating eavesdropper graph: {e}")
        return None

def generate_security_graph():
    """Generate real-time security analysis graph with dark theme"""
    try:
        if len(security_metrics['history']['time']) < 2:
            return None
            
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
        fig.patch.set_facecolor('#0D1117')
        
        times = security_metrics['history']['time']
        key_rates = security_metrics['history']['key_rate']
        efficiency = security_metrics['history']['efficiency']
        
        # Key rate plot
        ax1.plot(times, key_rates, '#4CAF50', linewidth=2)
        ax1.set_ylabel('Key Rate (bps)', color='white')
        ax1.set_title('Security Metrics Over Time', color='white')
        ax1.grid(True, alpha=0.3, color='white')
        ax1.set_facecolor('#161B22')
        ax1.tick_params(colors='white')
        
        # Efficiency plot
        ax2.plot(times, efficiency, '#2196F3', linewidth=2)
        ax2.set_xlabel('Time (s)', color='white')
        ax2.set_ylabel('Efficiency (%)', color='white')
        ax2.grid(True, alpha=0.3, color='white')
        ax2.set_facecolor('#161B22')
        ax2.tick_params(colors='white')
        
        plt.tight_layout()
        
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=100, facecolor='#0D1117')
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close(fig)
        
        return img_str
    except Exception as e:
        print(f"Error generating security graph: {e}")
        return None

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
