# quantum_core/quantum_states.py
"""
Quantum State Calculations and Bloch Sphere Mathematics
Handles all quantum mechanics computations for the web interface
"""

import numpy as np
import math
from typing import Dict, List, Tuple
import cmath

class QuantumStateCalculator:
    def __init__(self):
        self.current_state = {'theta': 0.0, 'phi': 0.0}
        
    def angles_to_bloch(self, theta: float, phi: float) -> Dict[str, float]:
        """Convert spherical angles to Bloch sphere Cartesian coordinates"""
        th = math.radians(theta)
        ph = math.radians(phi)
        
        x = math.sin(th) * math.cos(ph)
        y = math.sin(th) * math.sin(ph)
        z = math.cos(th)
        
        return {'x': x, 'y': y, 'z': z}
    
    def angles_to_state_vector(self, theta: float, phi: float) -> np.ndarray:
        """Convert spherical angles to quantum state vector"""
        th = math.radians(theta) / 2  # Half angle for quantum state
        ph = math.radians(phi)
        
        alpha = math.cos(th)
        beta = math.sin(th) * cmath.exp(1j * ph)
        
        return np.array([alpha, beta])
    
    def state_vector_to_bloch(self, state_vector: np.ndarray) -> Dict[str, float]:
        """Convert state vector to Bloch sphere coordinates"""
        alpha, beta = state_vector[0], state_vector[1]
        
        # Pauli matrices expectations
        x = 2 * np.real(np.conj(alpha) * beta)
        y = 2 * np.imag(np.conj(alpha) * beta)
        z = np.abs(alpha)**2 - np.abs(beta)**2
        
        return {'x': float(x), 'y': float(y), 'z': float(z)}
    
    def calculate_probabilities(self, theta: float, phi: float) -> Dict[str, float]:
        """Calculate measurement probabilities for |0⟩ and |1⟩"""
        state_vector = self.angles_to_state_vector(theta, phi)
        
        prob_0 = np.abs(state_vector[0])**2
        prob_1 = np.abs(state_vector[1])**2
        
        return {'prob_0': float(prob_0), 'prob_1': float(prob_1)}
    
    def identify_state_name(self, theta: float, phi: float, tolerance: float = 1.0) -> str:
        """Identify common quantum state names"""
        # Normalize angles
        theta = theta % 360
        phi = phi % 360
        
        # Check for common states
        if abs(theta) < tolerance:
            return "|0⟩"
        elif abs(theta - 180) < tolerance:
            return "|1⟩"
        elif abs(theta - 90) < tolerance:
            if abs(phi) < tolerance:
                return "|+⟩"
            elif abs(phi - 180) < tolerance:
                return "|-⟩"
            elif abs(phi - 90) < tolerance:
                return "|+i⟩"
            elif abs(phi - 270) < tolerance:
                return "|-i⟩"
        
        return "|ψ⟩"  # General superposition state
    
    def generate_trajectory(self, start_angles: Tuple[float, float], 
                          end_angles: Tuple[float, float], 
                          num_points: int = 20) -> List[Dict]:
        """Generate trajectory points between two quantum states"""
        start_theta, start_phi = start_angles
        end_theta, end_phi = end_angles
        
        trajectory = []
        for i in range(num_points + 1):
            t = i / num_points
            
            # Linear interpolation of angles
            theta = start_theta + t * (end_theta - start_theta)
            phi = start_phi + t * (end_phi - start_phi)
            
            # Calculate Bloch coordinates
            bloch = self.angles_to_bloch(theta, phi)
            probabilities = self.calculate_probabilities(theta, phi)
            
            trajectory.append({
                'theta': theta,
                'phi': phi,
                'bloch': bloch,
                'probabilities': probabilities,
                'state_name': self.identify_state_name(theta, phi)
            })
        
        return trajectory
    
    def apply_rotation(self, theta: float, phi: float, 
                      rotation_axis: str, rotation_angle: float) -> Dict[str, float]:
        """Apply rotation around X, Y, or Z axis"""
        # Convert to state vector
        state = self.angles_to_state_vector(theta, phi)
        
        # Define rotation matrices
        angle = math.radians(rotation_angle) / 2
        
        if rotation_axis.upper() == 'X':
            # Rotation around X-axis (σₓ rotation)
            rotation_matrix = np.array([
                [math.cos(angle), -1j * math.sin(angle)],
                [-1j * math.sin(angle), math.cos(angle)]
            ])
        elif rotation_axis.upper() == 'Y':
            # Rotation around Y-axis (σᵧ rotation)
            rotation_matrix = np.array([
                [math.cos(angle), -math.sin(angle)],
                [math.sin(angle), math.cos(angle)]
            ])
        elif rotation_axis.upper() == 'Z':
            # Rotation around Z-axis (σᵤ rotation)
            rotation_matrix = np.array([
                [cmath.exp(-1j * angle), 0],
                [0, cmath.exp(1j * angle)]
            ])
        else:
            raise ValueError("Rotation axis must be 'X', 'Y', or 'Z'")
        
        # Apply rotation
        rotated_state = rotation_matrix @ state
        
        # Convert back to Bloch coordinates
        return self.state_vector_to_bloch(rotated_state)
    
    def measure_state(self, theta: float, phi: float, 
                     measurement_basis: str) -> Dict[str, float]:
        """Simulate quantum measurement in specified basis"""
        if measurement_basis.upper() == 'Z':
            # Computational basis measurement
            probabilities = self.calculate_probabilities(theta, phi)
            return {
                'basis': 'Z',
                'prob_0': probabilities['prob_0'],
                'prob_1': probabilities['prob_1'],
                'result': '0' if np.random.random() < probabilities['prob_0'] else '1'
            }
        elif measurement_basis.upper() == 'X':
            # Hadamard basis measurement
            # First apply Hadamard transformation
            rotated_bloch = self.apply_rotation(theta, phi, 'Y', 90)
            # Then measure in Z basis
            rotated_angles = self.bloch_to_angles(rotated_bloch)
            return self.measure_state(rotated_angles['theta'], rotated_angles['phi'], 'Z')
        else:
            raise ValueError("Measurement basis must be 'X' or 'Z'")
    
    def bloch_to_angles(self, bloch_coords: Dict[str, float]) -> Dict[str, float]:
        """Convert Bloch coordinates back to spherical angles"""
        x, y, z = bloch_coords['x'], bloch_coords['y'], bloch_coords['z']
        
        # Calculate theta
        theta = math.degrees(math.acos(z))
        
        # Calculate phi
        if abs(x) < 1e-10 and abs(y) < 1e-10:
            phi = 0.0  # Arbitrary when on z-axis
        else:
            phi = math.degrees(math.atan2(y, x))
            if phi < 0:
                phi += 360
        
        return {'theta': theta, 'phi': phi}
    
    def get_state_info(self, theta: float, phi: float) -> Dict:
        """Get comprehensive information about quantum state"""
        bloch = self.angles_to_bloch(theta, phi)
        probabilities = self.calculate_probabilities(theta, phi)
        state_name = self.identify_state_name(theta, phi)
        state_vector = self.angles_to_state_vector(theta, phi)
        
        return {
            'angles': {'theta': theta, 'phi': phi},
            'bloch_coords': bloch,
            'probabilities': probabilities,
            'state_name': state_name,
            'state_vector': {
                'alpha': complex(state_vector[0]),
                'beta': complex(state_vector[1])
            },
            'purity': 1.0,  # Pure states always have purity 1
            'entanglement': 0.0  # Single qubits are not entangled
        }

# Example usage and testing
if __name__ == "__main__":
    calc = QuantumStateCalculator()
    
    # Test various quantum states
    states_to_test = [
        (0, 0, "|0⟩"),
        (180, 0, "|1⟩"),
        (90, 0, "|+⟩"),
        (90, 180, "|-⟩"),
        (90, 90, "|+i⟩"),
        (45, 30, "Superposition")
    ]
    
    print("Quantum State Testing:")
    print("=" * 50)
    
    for theta, phi, expected_name in states_to_test:
        info = calc.get_state_info(theta, phi)
        print(f"\nState: {expected_name}")
        print(f"Angles: θ={theta}°, φ={phi}°")
        print(f"Identified as: {info['state_name']}")
        print(f"Bloch coords: ({info['bloch_coords']['x']:.3f}, "
              f"{info['bloch_coords']['y']:.3f}, {info['bloch_coords']['z']:.3f})")
        print(f"P(|0⟩) = {info['probabilities']['prob_0']:.3f}, "
              f"P(|1⟩) = {info['probabilities']['prob_1']:.3f}")
