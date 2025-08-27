# BB84 Quantum Key Distribution - Advanced Web Application

A real-time interactive web application demonstrating the **BB84 Quantum Key Distribution protocol** with 3D Bloch sphere visualization, eavesdropping simulation, and comprehensive security analysis.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![Qiskit](https://img.shields.io/badge/Qiskit-1.1.0+-red.svg)](https://qiskit.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

![BB84 Demo](https://img.shields.io/badge/Live%20Demo-Available-brightgreen.svg)

---

## 🌟 Features

- **🔬 3D Bloch Sphere Visualization** – Real-time quantum state representation using Qiskit  
- **📊 Interactive Monitoring** – Live graphs showing eavesdropper activity and security metrics  
- **🕵️ Eavesdropping Simulation** – Real-time attack detection with QBER (Quantum Bit Error Rate) calculation  
- **📡 Alice-Bob Communication** – Animated bit transfer visualization between quantum parties  
- **⚛️ WebSocket Integration** – Real-time updates without page refresh using Flask-SocketIO  
- **🛡️ Security Analysis** – Live monitoring of key generation rate, efficiency, and security status  
- **🎮 Interactive Controls** – Adjustable quantum state parameters and eavesdropper settings  
- **📱 Responsive Design** – Modern dark theme UI compatible with desktop and mobile devices  

---

## 🎯 Demo

**Live Application**: [Your Deployed URL Here]

### Screenshots

┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐
│ Quantum State │ │ Eavesdropper │ │ Security Analysis │
│ Visualization │ │ Monitoring │ │ Dashboard │
│ │ │ │ │ │
│ 🌐 Bloch Sphere │ │ 📊 Live Graphs │ │ 🛡️ Real-time QBER │
│ │ │ │ │ Tracking │
└─────────────────────┘ └─────────────────────┘ └─────────────────────┘

yaml
Copy code

---

## 🚀 Quick Start

### Prerequisites
- Python **3.11+**  
- Virtual environment support  
- Modern web browser with WebSocket support  

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/dhanasai2/bb84-quantum-key-distribution.git
   cd bb84-quantum-key-distribution
Create and activate virtual environment

bash
Copy code
python -m venv .venv
Windows

powershell
Copy code
.venv\Scripts\Activate.ps1
Linux/macOS

bash
Copy code
source .venv/bin/activate
Install dependencies

bash
Copy code
pip install -r requirements.txt
Run the application

bash
Copy code
python app.py
Access the application

Local: http://localhost:5000

Network: http://your-ip:5000

💻 Usage
Basic Operations
Start Quantum Communication

Click 🚀 Start to begin BB84 simulation

Watch real-time 3D Bloch sphere visualization

Monitor Alice-Bob bit transfer animation

Simulate Eavesdropping Attack

Click ⚡ Attack to activate eavesdropper

Adjust parameters:

Attack Rate – Percentage of bits intercepted

Detection Threshold – Probability of attack detection

Observe QBER changes and security status

Monitor Security Metrics

✅ SECURE: QBER < 5% (Green)

⚠️ WARNING: QBER 5–11% (Orange)

❌ COMPROMISED: QBER > 11% (Red)

Interactive Controls

Adjust θ, φ with sliders

Set number of qubits

Reset to initial state

🏗️ Architecture
Backend
app.py – Flask + Flask-SocketIO server

Qiskit quantum simulation

Real-time threading

Frontend
templates/index.html – Responsive UI

WebSocket client

Interactive dashboard + 3D visualization

Key Files
File	Description
app.py	Main Flask app with quantum simulation
templates/index.html	Frontend with WebSocket integration
requirements.txt	Python dependencies
gunicorn_config.py	Production server configuration
runtime.txt	Python version specification

🧮 Quantum Implementation
BB84 Protocol Features
Rectilinear & diagonal basis encoding

Basis reconciliation

Key distillation (error correction & privacy amplification)

QBER calculation in real-time

Qiskit Example
python
Copy code
qc = QuantumCircuit(1)
qc.ry(theta_rad, 0)  # Rotation around Y
qc.rz(phi_rad, 0)    # Rotation around Z

simulator = AerSimulator(method='statevector')
statevector = execute(qc, simulator).result().get_statevector()
🔧 Configuration
Environment Variables
Development

env
Copy code
FLASK_ENV=development
DEBUG=True
Production

env
Copy code
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
PORT=5000
🚀 Deployment
Local
bash
Copy code
python app.py
Access: http://localhost:5000

Render.com (Recommended)
Build: pip install -r requirements.txt

Start: gunicorn --config gunicorn_config.py app:app

Docker
bash
Copy code
docker build -t bb84-quantum .
docker run -p 5000:5000 bb84-quantum
Heroku
bash
Copy code
heroku login
heroku create bb84-quantum-app
git push heroku main
🔬 Educational Content
Learning Objectives
Quantum cryptography (BB84 protocol)

Quantum state visualization

Eavesdropping & QBER detection

Real-time WebSocket updates

Practical Qiskit integration

Use Cases
Academic research & teaching

Interactive quantum learning

Security training

Technology showcase

🛠️ Development
Contributing
Fork repo

Create branch: git checkout -b feature-name

Commit: git commit -m "Add feature"

Push: git push origin feature-name

Open Pull Request

Development Setup
bash
Copy code
pip install -r requirements-dev.txt
pytest tests/
black app.py
flake8 app.py
mypy app.py
📊 Performance
RAM: 512MB min, 1GB recommended

CPU: Single-core sufficient

Quantum state updates: 60 FPS

WebSocket latency: <50ms

Real-time up to 100 qubits

10+ concurrent users supported

📚 Resources
Qiskit Documentation

Flask-SocketIO Guide

BB84 Protocol Paper

Quantum Cryptography - Wikipedia

📝 License
This project is licensed under the MIT License – see the LICENSE file.

👥 Authors
Gundumogula Dhana Sai – Initial Work – @dhanasai2

🙏 Acknowledgments
IBM Qiskit Team – Quantum computing framework

Flask Community – Web framework support

Quantum Community – Education resources

Bennett & Brassard – Original BB84 protocol

📞 Support
GitHub Issues

GitHub Discussions

📧 Email: saigundumogula5@gmail.com

⭐ Star this repository if you found it helpful!
🔗 Live Demo: https://sai27309.pythonanywhere.com/
🚀 Built with: Python • Flask • Qiskit • WebSockets • Modern Web Tech
