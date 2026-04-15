# 🚀 ManttoAI - IoT Predictive Maintenance Platform

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB.svg?logo=react&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?logo=docker&logoColor=white)
![Machine Learning](https://img.shields.io/badge/ML-Scikit_Learn-F7931E.svg)

**ManttoAI** is an open-source, lightweight predictive maintenance platform. It captures real-time telemetry from IoT devices (ESP32) via MQTT, evaluates operational thresholds, and runs a Machine Learning model (Random Forest) to predict equipment failures before they happen.

---

## ✨ Key Features

- **📡 Real-time IoT Telemetry:** Native MQTT integration (Mosquitto) for capturing temperature, humidity, and vibration.
- **🧠 Machine Learning Predictions:** Built-in Random Forest model (94.1% F1-Score) to evaluate failure risks.
- **🚨 Smart Alerts:** Automated evaluation of operational thresholds with email notifications.
- **📊 Interactive Dashboard:** React SPA with auto-refresh, historical trends, and equipment management.
- **🛠️ Built-in IoT Simulator:** No hardware? No problem. Includes a 24/7 software simulator to generate realistic sensor data out of the box.

## 🏗️ Tech Stack

- **Backend:** FastAPI, SQLAlchemy, Pydantic, MySQL 8
- **Frontend:** React 18, Vite, Tailwind CSS
- **IoT & Messaging:** ESP32 (Firmware), Eclipse Mosquitto (MQTT)
- **Machine Learning:** Scikit-learn, Pandas, Numpy
- **Infrastructure:** Docker, Docker Compose, Nginx (Dokploy ready)

---

## 🚀 Quick Start (Local Development)

You can run the entire platform locally using Docker Compose. No external dependencies are required.

### Prerequisites
- Docker & Docker Compose V2
- GNU Make

### 1. Start the platform
```bash
# Generate local .env files and MQTT credentials
make setup-env

# Spin up the entire stack (Backend, Frontend, MySQL, Mosquitto)
make up
```

### 2. Seed data & simulate
```bash
# Create the admin user, sample equipment, and thresholds
make seed

# Start sending realistic simulated MQTT telemetry
make simulate
```

### 3. Access the Dashboard
- **Frontend:** `http://localhost:5173` (or port 80 if fully deployed)
- **API Docs (Swagger):** `http://localhost:8000/docs`
- **Default Login:** `admin@manttoai.local` (Password generated in `backend/.env` after `make setup-env`)

---

## 📂 Repository Structure

```text
├── backend/       # FastAPI application, ML models, and business logic
├── frontend/      # React 18 SPA dashboard
├── iot/           # ESP32 C++ firmware and MQTT simulation scripts
├── mosquitto/     # MQTT broker configuration and auth
├── scripts/       # Operational and deployment utilities
└── docs/          # Architecture and academic documentation
```

## 🤝 Contributing

We welcome contributions from the community! If you'd like to help:
1. Check the [Issues](https://github.com/sebitabravo/ManttoAI/issues) tab for open tasks.
2. Fork the repository and create a feature branch (`feature/amazing-idea`).
3. Ensure your code passes all checks (`make lint` and `make test`).
4. Open a Pull Request.

---

## 🎓 Academic Context (PMBOK)

*This project originated as a Capstone Project (Gestión de Proyectos Informáticos) at INACAP.* 

If you are an academic evaluator or looking for the formal PMBOK project management artifacts (Project Charter, WBS, RACI, Risk Matrix, etc.), please refer to the dedicated management index:

👉 **[Ver Documentación PMBOK / Evaluación Académica](docs/gestion-proyecto/INDEX.md)**

---
*Maintained by the ManttoAI Team. Open source for the community.*
