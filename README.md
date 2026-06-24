# 🏥 FedHealth — Federated Learning for Healthcare

A privacy-preserving federated learning system designed for multi-hospital collaboration. Hospitals can collaboratively train machine learning models on patient data **without sharing raw data**, using Homomorphic Encryption (HE), TLS communication, and gradient integrity verification.

---

## 🔒 Privacy Notice

> **Some files and directories have been intentionally excluded from this repository to protect patient privacy and institutional confidentiality.**
>
> The following categories of files are **not included**:
> - 🗄️ **Patient datasets** — `.csv`, `.db`, `.sqlite`, and any raw health records
> - 🔐 **TLS certificates & keys** — `*.pem`, `*.key`, `*.crt` (self-signed or CA-issued)
> - 🌍 **Environment configs** — `.env` files containing API keys, DB credentials, or hospital endpoints
> - 📦 **Virtual environments** — `venv/`, `.venv/`, Python package caches
> - 📁 **Node modules** — `node_modules/` (install via `npm install`)
> - 🏗️ **Build artifacts** — `dist/`, `dist-ssr/`
>
> These exclusions are enforced via `.gitignore` at both the frontend and backend levels.

---

## 📁 Project Structure

```
FedHealth/
│
├── hospital-fl-backend/          # Python — Federated Learning Server & Client
│   ├── server.py                 # FL aggregation server (FedAvg strategy)
│   ├── client.py                 # Hospital FL client (local training)
│   ├── model.py                  # Neural network model definition
│   ├── data_loader.py            # Data loading & preprocessing pipeline
│   ├── federated_data.py         # Federated data partitioning utilities
│   ├── api.py                    # REST API (Flask) — exposes FL metrics & results
│   ├── fl_he.py                  # Homomorphic Encryption layer (Paillier)
│   ├── fl_tls.py                 # TLS mutual authentication setup
│   ├── fl_integrity.py           # Gradient integrity verification (hashing)
│   ├── fl_config.py              # Global FL hyperparameters & config
│   ├── evaluator.py              # Model evaluation utilities (accuracy, F1, AUC)
│   ├── logger_config.py          # Centralized logging configuration
│   ├── startup.py                # Server startup & initialization script
│   ├── generate_cert.py          # TLS self-signed certificate generator
│   ├── check_models.py           # Sanity-check saved model weights
│   ├── test_set.py               # Holdout test set evaluation script
│   ├── verify.py                 # End-to-end verification of FL round results
│   └── requirements.txt          # Python dependencies
│
├── hospital-fl-app/              # React + Vite — Hospital Dashboard Frontend
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx     # Main FL monitoring dashboard
│   │   │   ├── Login.jsx         # Hospital authentication page
│   │   │   └── Report.jsx        # FL round reports & analytics
│   │   ├── App.jsx               # Root application component & routing
│   │   ├── auth.js               # Authentication utilities (JWT handling)
│   │   ├── App.css               # Global application styles
│   │   ├── index.css             # Base styles & CSS variables
│   │   └── main.jsx              # React entry point
│   ├── public/                   # Static assets
│   ├── server.js                 # Express dev proxy server
│   ├── index.html                # HTML entry point
│   ├── vite.config.js            # Vite bundler configuration
│   ├── eslint.config.js          # ESLint rules
│   └── package.json              # Node.js dependencies & scripts
│
└── README.md                     # Project documentation (this file)
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- `pip` and `npm`

### 1. Backend Setup

```bash
cd hospital-fl-backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Generate TLS certificates (for local development)
python generate_cert.py

# Start the FL server
python startup.py
```

### 2. Frontend Setup

```bash
cd hospital-fl-app

# Install dependencies
npm install

# Start the development server
npm run dev
```

The dashboard will be available at `http://localhost:5173`.

---

## 🧠 Key Features

| Feature | Description |
|---|---|
| **Federated Averaging (FedAvg)** | Hospitals train locally; only model weights are shared |
| **Homomorphic Encryption** | Gradients are encrypted before transmission |
| **TLS Mutual Auth** | Encrypted, authenticated communication between nodes |
| **Gradient Integrity** | Hash-based verification to detect tampering |
| **Real-time Dashboard** | Monitor FL rounds, accuracy, and loss live |
| **Audit Reports** | Per-round analytics and model performance reports |

---

## 🛠️ Tech Stack

**Backend**
- Python, Flower (FL framework), PyTorch / scikit-learn
- Flask (REST API), PyCryptodome (HE), OpenSSL (TLS)

**Frontend**
- React 18, Vite, JavaScript (ES2022)
- Recharts (data visualization), Axios

---

## ⚠️ Disclaimer

This repository is intended for **research and educational purposes**. It does **not** include any real patient data. All datasets used during development were synthetic or properly anonymized under institutional guidelines.

---

## 📄 License

This project is shared publicly for academic reference. Please contact the repository owner before using it in production or derivative research.
