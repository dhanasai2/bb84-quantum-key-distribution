# quantum_core/qkd_protocol.py
"""
BB84 Quantum Key Distribution Protocol Implementation
Preserves core functionality from the original Tkinter version
"""

import numpy as np
import random
import math
from typing import List, Tuple, Dict
import time

class BB84Protocol:
    def __init__(self):
        self.alice_bits = []
        self.alice_bases = []
        self.bob_bases = []
        self.bob_measurements = []
        self.shared_key = []
        self.qber = 0.0
        self.eavesdropper_detected = False
        
    def generate_random_bits(self, n_qubits: int) -> List[str]:
        """Generate random bits for Alice"""
        return [random.choice(['0', '1']) for _ in range(n_qubits)]
    
    def generate_random_bases(self, n_qubits: int) -> List[str]:
        """Generate random measurement bases"""
        return [random.choice(['Z', 'X']) for _ in range(n_qubits)]
    
    def encode_qubits(self, bits: List[str], bases: List[str]) -> List[Dict]:
        """Encode bits into quantum states based on bases"""
        qubits = []
        for bit, basis in zip(bits, bases):
            if basis == 'Z':
                # Z basis: |0⟩ or |1⟩
                theta = 0 if bit == '0' else 180
                phi = 0
            else:  # X basis
                # X basis: |+⟩ or |-⟩  
                theta = 90
                phi = 0 if bit == '0' else 180
            
            qubits.append({
                'bit': bit,
                'basis': basis,
                'theta': theta,
                'phi': phi,
                'bloch_coords': self._get_bloch_coords(theta, phi)
            })
        
        return qubits
    
    def _get_bloch_coords(self, theta: float, phi: float) -> Dict[str, float]:
        """Calculate Bloch sphere coordinates"""
        th = math.radians(theta)
        ph = math.radians(phi)
        
        x = math.sin(th) * math.cos(ph)
        y = math.sin(th) * math.sin(ph)  
        z = math.cos(th)
        
        return {'x': x, 'y': y, 'z': z}
    
    def measure_qubits(self, qubits: List[Dict], bases: List[str]) -> List[str]:
        """Bob measures qubits in random bases"""
        measurements = []
        
        for qubit, measure_basis in zip(qubits, bases):
            original_basis = qubit['basis']
            original_bit = qubit['bit']
            
            if original_basis == measure_basis:
                # Same basis - measurement is deterministic
                measurements.append(original_bit)
            else:
                # Different basis - measurement is random (50/50)
                measurements.append(random.choice(['0', '1']))
        
        return measurements
    
    def sift_key(self, alice_bases: List[str], bob_bases: List[str], 
                 alice_bits: List[str], bob_measurements: List[str]) -> Tuple[List[str], List[int]]:
        """Sift shared key from matching bases"""
        shared_key = []
        matching_indices = []
        
        for i, (a_basis, b_basis, a_bit, b_bit) in enumerate(
            zip(alice_bases, bob_bases, alice_bits, bob_measurements)
        ):
            if a_basis == b_basis:
                shared_key.append(a_bit)
                matching_indices.append(i)
        
        return shared_key, matching_indices
    
    def calculate_qber(self, alice_key: List[str], bob_key: List[str], 
                      sample_size: int = None) -> float:
        """Calculate Quantum Bit Error Rate"""
        if not alice_key or len(alice_key) != len(bob_key):
            return 0.0
        
        if sample_size is None:
            sample_size = min(len(alice_key) // 4, 50)  # Use 25% for testing
        
        if sample_size == 0:
            return 0.0
        
        # Random sampling for QBER calculation
        test_indices = random.sample(range(len(alice_key)), 
                                   min(sample_size, len(alice_key)))
        
        errors = 0
        for i in test_indices:
            if alice_key[i] != bob_key[i]:
                errors += 1
        
        qber = errors / len(test_indices) if test_indices else 0.0
        return qber
    
    def run_protocol(self, n_qubits: int, eve_intercept_prob: float = 0.0) -> Dict:
        """Run complete BB84 protocol with optional eavesdropping"""
        
        # Step 1: Alice generates random bits and bases
        self.alice_bits = self.generate_random_bits(n_qubits)
        self.alice_bases = self.generate_random_bases(n_qubits)
        
        # Step 2: Alice encodes qubits
        qubits = self.encode_qubits(self.alice_bits, self.alice_bases)
        
        # Step 3: Optional eavesdropping
        intercepts = 0
        if eve_intercept_prob > 0:
            for i, qubit in enumerate(qubits):
                if random.random() < eve_intercept_prob:
                    intercepts += 1
                    # Eve measures in random basis
                    eve_basis = random.choice(['Z', 'X'])
                    eve_measurement = self.measure_qubits([qubit], [eve_basis])[0]
                    
                    # Eve re-encodes and sends to Bob
                    qubits[i] = self.encode_qubits([eve_measurement], [eve_basis])[0]
        
        # Step 4: Bob generates random bases and measures
        self.bob_bases = self.generate_random_bases(n_qubits)
        self.bob_measurements = self.measure_qubits(qubits, self.bob_bases)
        
        # Step 5: Public discussion - basis comparison
        alice_key, matching_indices = self.sift_key(
            self.alice_bases, self.bob_bases, 
            self.alice_bits, self.bob_measurements
        )
        
        bob_key = [self.bob_measurements[i] for i in matching_indices]
        
        # Step 6: QBER calculation and eavesdropper detection
        self.qber = self.calculate_qber(alice_key, bob_key)
        self.eavesdropper_detected = self.qber > 0.11  # 11% threshold
        
        # Step 7: Final shared key (after error correction)
        if not self.eavesdropper_detected:
            self.shared_key = alice_key
        else:
            self.shared_key = []  # Abort if eavesdropper detected
        
        return {
            'success': True,
            'qubits_sent': n_qubits,
            'qubits_sifted': len(alice_key),
            'shared_key_length': len(self.shared_key),
            'qber': self.qber,
            'eavesdropper_detected': self.eavesdropper_detected,
            'intercepts': intercepts,
            'efficiency': len(self.shared_key) / n_qubits if n_qubits > 0 else 0,
            'qubits_data': qubits  # For visualization
        }

# Example usage
if __name__ == "__main__":
    protocol = BB84Protocol()
    result = protocol.run_protocol(n_qubits=16, eve_intercept_prob=0.3)
    print(f"Protocol result: {result}")
