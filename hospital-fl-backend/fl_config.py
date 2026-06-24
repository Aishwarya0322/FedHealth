"""
Federated network configuration — hospitals that join the same Flower session.
Must match identities you use in the UI / auth (e.g. HOSP-001 … HOSP-004).
"""
import os

# Hospitals included in every FedAvg round (each needs data_<id>.csv for training)
_default_ids = ["HOSP-001", "HOSP-002", "HOSP-003", "HOSP-004"]

_raw = os.environ.get("FL_HOSPITAL_IDS", "")
if _raw.strip():
    FEDERATED_HOSPITAL_IDS = [x.strip() for x in _raw.split(",") if x.strip()]
else:
    FEDERATED_HOSPITAL_IDS = list(_default_ids)


def federated_hospital_count() -> int:
    return len(FEDERATED_HOSPITAL_IDS)