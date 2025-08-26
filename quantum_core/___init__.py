# quantum_core/__init__.py
"""
Ultimate QKD Core Quantum Module
Contains all quantum mechanics calculations and BB84 protocol logic
"""

__version__ = "1.0.0"
__author__ = "Ultimate QKD System"

from .qkd_protocol import BB84Protocol
from .quantum_states import QuantumStateCalculator
from .eavesdropper import EavesdropperDetector

__all__ = ['BB84Protocol', 'QuantumStateCalculator', 'EavesdropperDetector']
