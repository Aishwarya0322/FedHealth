# 🏥 FedHealth — Federated Learning for Healthcare

A privacy-preserving federated learning system designed for multi-hospital collaboration. Hospitals can collaboratively train machine learning models on patient data **without sharing raw data**, using Homomorphic Encryption (HE), TLS communication, and gradient integrity verification.

Built a secure web application accessible only to authorized hospital administrators. Administrators can enter patient symptoms, which are analyzed using the federated learning model. The system predicts the disease risk level, generates a detailed diagnostic report with recommendations, and automatically forwards the report to the appropriate specialist doctor for further review and treatment. This approach improves collaborative healthcare intelligence while maintaining strict patient privacy and regulatory compliance


## 🔒 Privacy Notice

> **Some files and directories have been intentionally excluded from this repository to protect patient privacy and institutional confidentiality.**
>
> The following categories of files are **not included**:
> - 🗄️ **Patient datasets** — `.csv`, `.db`, `.sqlite`, and any raw health records
> - 🔐 **TLS certificates & keys** — `*.pem`, `*.key`, `*.crt` (self-signed or CA-issued)

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

