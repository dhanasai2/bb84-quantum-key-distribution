# quantum_core/eavesdropper.py
"""
Eavesdropper Detection and Security Analysis
Advanced security monitoring for QKD systems
"""

import numpy as np
import random
import math
from typing import List, Dict, Tuple
from collections import deque
import time

class EavesdropperDetector:
    def __init__(self, detection_threshold: float = 0.11, window_size: int = 100):
        self.detection_threshold = detection_threshold
        self.window_size = window_size
        
        # Historical data
        self.qber_history = deque(maxlen=window_size)
        self.intercept_history = deque(maxlen=window_size)
        self.security_metrics = deque(maxlen=window_size)
        
        # Current session data
        self.session_intercepts = 0
        self.session_detections = 0
        self.session_qubits = 0
        self.start_time = time.time()
        
        # Threat levels
        self.threat_levels = {
            'LOW': (0.0, 0.05),
            'MEDIUM': (0.05, 0.11),
            'HIGH': (0.11, 0.20),
            'CRITICAL': (0.20, 1.0)
        }
    
    def simulate_eavesdropping(self, qubits: List[Dict], 
                             intercept_probability: float) -> Tuple[List[Dict], Dict]:
        """Simulate Eve's interception and measure impact"""
        intercepted_qubits = []
        intercept_data = {
            'total_intercepts': 0,
            'detection_events': 0,
            'estimated_information_gain': 0.0,
            'attack_pattern': []
        }
        
        for i, qubit in enumerate(qubits):
            if random.random() < intercept_probability:
                # Eve intercepts
                intercept_data['total_intercepts'] += 1
                self.session_intercepts += 1
                
                # Eve measures in random basis
                eve_basis = random.choice(['Z', 'X'])
                original_bit = qubit['bit']
                original_basis = qubit['basis']
                
                # Measure with quantum uncertainty
                if eve_basis == original_basis:
                    # Same basis - Eve gets correct result
                    eve_bit = original_bit
                    information_gain = 1.0
                else:
                    # Different basis - random result
                    eve_bit = random.choice(['0', '1'])
                    information_gain = 0.5
                
                intercept_data['estimated_information_gain'] += information_gain
                
                # Eve re-prepares qubit (introduces errors)
                disturbed_qubit = self._prepare_disturbed_qubit(
                    eve_bit, eve_basis, original_basis
                )
                intercepted_qubits.append(disturbed_qubit)
                
                # Record attack pattern
                intercept_data['attack_pattern'].append({
                    'qubit_index': i,
                    'eve_basis': eve_basis,
                    'original_basis': original_basis,
                    'information_gain': information_gain
                })
                
                # Check if this intercept would be detected
                if self._would_be_detected(original_basis, eve_basis):
                    intercept_data['detection_events'] += 1
                    self.session_detections += 1
                    
            else:
                # No interception - qubit passes through unchanged
                intercepted_qubits.append(qubit)
        
        # Update statistics
        self.session_qubits += len(qubits)
        
        # Calculate normalized information gain
        if intercept_data['total_intercepts'] > 0:
            intercept_data['estimated_information_gain'] /= intercept_data['total_intercepts']
        
        return intercepted_qubits, intercept_data
    
    def _prepare_disturbed_qubit(self, bit: str, eve_basis: str, 
                               original_basis: str) -> Dict:
        """Prepare qubit after Eve's measurement (introduces disturbance)"""
        # Calculate new quantum state based on Eve's measurement
        if eve_basis == 'Z':
            theta = 0 if bit == '0' else 180
            phi = 0
        else:  # X basis
            theta = 90
            phi = 0 if bit == '0' else 180
        
        # Add quantum noise due to measurement disturbance
        if eve_basis != original_basis:
            # Add small random perturbation
            noise_amplitude = 5.0  # degrees
            theta += random.uniform(-noise_amplitude, noise_amplitude)
            phi += random.uniform(-noise_amplitude, noise_amplitude)
        
        return {
            'bit': bit,
            'basis': eve_basis,
            'theta': theta,
            'phi': phi,
            'bloch_coords': self._get_bloch_coords(theta, phi),
            'disturbed': eve_basis != original_basis
        }
    
    def _get_bloch_coords(self, theta: float, phi: float) -> Dict[str, float]:
        """Calculate Bloch sphere coordinates"""
        th = math.radians(theta)
        ph = math.radians(phi)
        
        x = math.sin(th) * math.cos(ph)
        y = math.sin(th) * math.sin(ph)
        z = math.cos(th)
        
        return {'x': x, 'y': y, 'z': z}
    
    def _would_be_detected(self, original_basis: str, eve_basis: str) -> bool:
        """Determine if Eve's interference would be detected"""
        if original_basis != eve_basis:
            # Different bases create detectable errors
            return random.random() < 0.5  # 50% chance of detection
        return False
    
    def calculate_qber(self, alice_bits: List[str], bob_bits: List[str]) -> float:
        """Calculate Quantum Bit Error Rate"""
        if not alice_bits or len(alice_bits) != len(bob_bits):
            return 0.0
        
        errors = sum(1 for a, b in zip(alice_bits, bob_bits) if a != b)
        qber = errors / len(alice_bits)
        
        # Add to history
        self.qber_history.append(qber)
        
        return qber
    
    def analyze_security(self, qber: float) -> Dict:
        """Comprehensive security analysis"""
        # Determine threat level
        threat_level = self._determine_threat_level(qber)
        
        # Calculate security metrics
        security_score = max(0, 1 - (qber / 0.20))  # Normalized security score
        efficiency = max(0, 1 - qber * 2)  # Efficiency degrades with QBER
        
        # Key rate estimation (simplified)
        if qber > 0.11:
            estimated_key_rate = 0
        else:
            estimated_key_rate = max(0, 1 - 2 * qber) * 1000  # bps
        
        # Eavesdropper detection confidence
        detection_confidence = min(1.0, qber / self.detection_threshold)
        
        # Statistical analysis
        stats = self._calculate_security_statistics()
        
        security_analysis = {
            'qber': qber,
            'threat_level': threat_level,
            'security_score': security_score,
            'efficiency': efficiency,
            'estimated_key_rate': int(estimated_key_rate),
            'detection_confidence': detection_confidence,
            'eavesdropper_detected': qber > self.detection_threshold,
            'recommendation': self._get_security_recommendation(qber),
            'statistics': stats
        }
        
        # Add to security metrics history
        self.security_metrics.append(security_analysis)
        
        return security_analysis
    
    def _determine_threat_level(self, qber: float) -> str:
        """Determine threat level based on QBER"""
        for level, (min_qber, max_qber) in self.threat_levels.items():
            if min_qber <= qber < max_qber:
                return level
        return 'CRITICAL'
    
    def _get_security_recommendation(self, qber: float) -> str:
        """Get security recommendation based on QBER"""
        if qber < 0.02:
            return "Secure - Continue normal operation"
        elif qber < 0.05:
            return "Monitor - Slightly elevated error rate"
        elif qber < 0.11:
            return "Caution - Approaching detection threshold"
        else:
            return "Alert - Potential eavesdropper detected! Abort key exchange"
    
    def _calculate_security_statistics(self) -> Dict:
        """Calculate comprehensive security statistics"""
        uptime = time.time() - self.start_time
        
        # Calculate session statistics
        session_qber = (self.session_detections / max(1, self.session_qubits))
        success_rate = 1 - session_qber
        
        # Historical analysis
        if len(self.qber_history) > 1:
            avg_qber = sum(self.qber_history) / len(self.qber_history)
            qber_trend = self._calculate_trend(list(self.qber_history))
            qber_std = np.std(self.qber_history) if len(self.qber_history) > 1 else 0
        else:
            avg_qber = session_qber
            qber_trend = 0.0
            qber_std = 0.0
        
        return {
            'uptime_seconds': int(uptime),
            'session_qubits': self.session_qubits,
            'session_intercepts': self.session_intercepts,
            'session_detections': self.session_detections,
            'session_qber': session_qber,
            'success_rate': success_rate,
            'average_qber': avg_qber,
            'qber_trend': qber_trend,
            'qber_standard_deviation': qber_std,
            'detection_efficiency': (self.session_detections / max(1, self.session_intercepts))
        }
    
    def _calculate_trend(self, data: List[float]) -> float:
        """Calculate trend direction (-1 to 1)"""
        if len(data) < 2:
            return 0.0
        
        # Simple linear trend calculation
        n = len(data)
        x = list(range(n))
        y = data
        
        # Linear regression slope
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        
        # Normalize slope to [-1, 1] range
        return max(-1, min(1, slope * n))
    
    def generate_security_report(self) -> Dict:
        """Generate comprehensive security report"""
        current_qber = list(self.qber_history)[-1] if self.qber_history else 0.0
        analysis = self.analyze_security(current_qber)
        
        # Generate threat assessment
        threat_assessment = self._generate_threat_assessment()
        
        # Mitigation strategies
        mitigation = self._suggest_mitigation_strategies(analysis)
        
        return {
            'timestamp': time.time(),
            'security_analysis': analysis,
            'threat_assessment': threat_assessment,
            'mitigation_strategies': mitigation,
            'system_health': self._assess_system_health()
        }
    
    def _generate_threat_assessment(self) -> Dict:
        """Generate detailed threat assessment"""
        stats = self._calculate_security_statistics()
        
        # Risk factors
        risk_factors = []
        if stats['session_qber'] > 0.05:
            risk_factors.append("Elevated error rate detected")
        if stats['qber_trend'] > 0.5:
            risk_factors.append("Increasing error trend")
        if stats['session_intercepts'] > stats['session_qubits'] * 0.1:
            risk_factors.append("High interception rate")
        
        # Confidence level
        confidence_level = min(100, stats['session_qubits'] / 10)  # More data = higher confidence
        
        return {
            'overall_risk': self._determine_threat_level(stats['session_qber']),
            'risk_factors': risk_factors,
            'confidence_level': confidence_level,
            'data_quality': 'High' if stats['session_qubits'] > 50 else 'Medium' if stats['session_qubits'] > 20 else 'Low'
        }
    
    def _suggest_mitigation_strategies(self, analysis: Dict) -> List[str]:
        """Suggest mitigation strategies based on security analysis"""
        strategies = []
        
        if analysis['eavesdropper_detected']:
            strategies.extend([
                "Immediately halt key distribution",
                "Increase qubit transmission rate",
                "Implement quantum error correction",
                "Switch to backup quantum channel"
            ])
        elif analysis['qber'] > 0.05:
            strategies.extend([
                "Monitor channel continuously",
                "Increase basis randomization",
                "Implement privacy amplification"
            ])
        else:
            strategies.append("Continue normal operation with regular monitoring")
        
        return strategies
    
    def _assess_system_health(self) -> str:
        """Assess overall system health"""
        stats = self._calculate_security_statistics()
        
        if stats['session_qber'] > 0.15:
            return "CRITICAL"
        elif stats['session_qber'] > 0.08:
            return "DEGRADED"
        elif stats['session_qber'] > 0.03:
            return "MARGINAL"
        else:
            return "OPTIMAL"
    
    def reset_session(self):
        """Reset session statistics"""
        self.session_intercepts = 0
        self.session_detections = 0
        self.session_qubits = 0
        self.start_time = time.time()

# Example usage and testing
if __name__ == "__main__":
    detector = EavesdropperDetector()
    
    # Simulate some qubits
    test_qubits = [
        {'bit': '0', 'basis': 'Z', 'theta': 0, 'phi': 0, 'bloch_coords': {'x': 0, 'y': 0, 'z': 1}},
        {'bit': '1', 'basis': 'Z', 'theta': 180, 'phi': 0, 'bloch_coords': {'x': 0, 'y': 0, 'z': -1}},
        {'bit': '0', 'basis': 'X', 'theta': 90, 'phi': 0, 'bloch_coords': {'x': 1, 'y': 0, 'z': 0}},
        {'bit': '1', 'basis': 'X', 'theta': 90, 'phi': 180, 'bloch_coords': {'x': -1, 'y': 0, 'z': 0}}
    ]
    
    # Test eavesdropping simulation
    print("Testing Eavesdropper Detection:")
    print("=" * 50)
    
    for intercept_prob in [0.0, 0.3, 0.7]:
        print(f"\nIntercept Probability: {intercept_prob:.1%}")
        
        intercepted, data = detector.simulate_eavesdropping(test_qubits, intercept_prob)
        alice_bits = ['0', '1', '0', '1']
        bob_bits = [q['bit'] for q in intercepted]
        
        qber = detector.calculate_qber(alice_bits, bob_bits)
        analysis = detector.analyze_security(qber)
        
        print(f"Intercepts: {data['total_intercepts']}")
        print(f"Detections: {data['detection_events']}")
        print(f"QBER: {qber:.3f}")
        print(f"Threat Level: {analysis['threat_level']}")
        print(f"Eavesdropper Detected: {analysis['eavesdropper_detected']}")
        
        detector.reset_session()  # Reset for next test
