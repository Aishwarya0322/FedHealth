"""
Hospital Federated Learning API Server
FastAPI backend - Multi-Disease Support with Specialist Routing
"""
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from contextlib import asynccontextmanager
import pandas as pd
import torch
import os
import json
import subprocess
import threading
import sys
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Optional, Any, Dict

from model import HealthNet
from evaluator import ModelEvaluator
from test_set import create_holdout_test_set
from logger_config import setup_logging
import fl_config
from federated_data import partition_bootstrap_on_startup
from data_loader import DISEASE_FEATURES, get_norm

logger = setup_logging('API')
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=== Hospital FL API Starting ===")
    for d in ['heart', 'cancer', 'anaemia']:
        create_holdout_test_set(d)
    partition_bootstrap_on_startup(fl_config.FEDERATED_HOSPITAL_IDS)
    logger.info("System initialized successfully")
    yield
    logger.info("Hospital FL API shutting down...")


app = FastAPI(title="Hospital FL API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Generic flexible model for /predict ---
class PatientData(BaseModel):
    hospital_id: str
    disease: str = "heart"
    fields: Dict[str, Any]

class PredictionResponse(BaseModel):
    prediction: str
    probability: float
    status: str
    message: str

class StatusResponse(BaseModel):
    status: str
    message: str

class MetricsResponse(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    loss: float
    true_positives: int
    true_negatives: int
    false_positives: int
    false_negatives: int
    n_samples: int

training_status = {"status": "idle", "current_hospital": None, "last_update": None, "error_message": None}
training_lock = threading.Lock()


def get_specialist(hospital_id: str, disease: str) -> str:
    """Matches the ID format in auth.js: DOC-[DIS]-[HOSP_NUM]"""
    # Extract number (e.g., '001' from 'HOSP-001')
    import re
    match = re.search(r'(\d+)', hospital_id)
    h_num = match.group(1) if match else "001"
    
    prefix_map = {
        "heart": "HRT",
        "cancer": "ONC",
        "anaemia": "HEM"
    }
    prefix = prefix_map.get(disease.lower(), "GEN")
    return f"DOC-{prefix}-{h_num}"


def _fields_to_input_vector(disease: str, fields: dict) -> list:
    feat_info = DISEASE_FEATURES.get(disease, DISEASE_FEATURES['heart'])
    feat_cols = feat_info['feature_cols']
    n_features = feat_info['n_features']
    vec = []
    for col in feat_cols:
        val = fields.get(col, fields.get(col.replace(' ', '_'), 0.0))
        try:
            vec.append(float(val))
        except:
            vec.append(0.0)
    # Ensure exact length
    if len(vec) < n_features:
        vec.extend([0.0] * (n_features - len(vec)))
    return vec[:n_features]


@app.get("/records")
def get_hospital_records(hospital_id: str, doctor_id: str = None):
    safe_id = hospital_id.replace(" ", "_")
    all_records = []

    # 1. Search for data_HOSP-XXX_disease.csv
    csv_paths = glob.glob(os.path.join(BACKEND_DIR, f"data_{safe_id}_*.csv"))
    
    # 2. Check for the non-suffixed version data_HOSP-XXX.csv (Treat as Heart)
    base_csv = os.path.join(BACKEND_DIR, f"data_{safe_id}.csv")
    if os.path.exists(base_csv) and base_csv not in csv_paths:
        csv_paths.append(base_csv)

    for csv_path in sorted(csv_paths):
        fname = os.path.basename(csv_path)
        # Try to extract disease suffix
        parts = fname.replace(".csv", "").split("_")
        if len(parts) >= 3:
            disease_part = parts[-1].lower()
        else:
            disease_part = "heart" # Default for data_HOSP-001.csv
            
        if disease_part not in ('heart', 'cancer', 'anaemia'):
            disease_part = "heart"

        try:
            df = pd.read_csv(csv_path)
            if df.empty: continue
            
            # Clean up records
            records = json.loads(df.to_json(orient="records"))
            for row in records:
                row['disease'] = disease_part.capitalize()
                res = row.get("result")
                try:
                    ri = int(float(res))
                    row["result_label"] = "Positive (High Risk)" if ri == 1 else "Negative (Low Risk)"
                except:
                    row["result_label"] = str(res)
                
                if not row.get('assigned_doctor'):
                    row['assigned_doctor'] = get_specialist(hospital_id, disease_part)
                
                # Filtering Logic:
                if doctor_id:
                    # Doctor Role: Show ONLY their assigned, newly predicted records
                    if row.get('assigned_doctor') == doctor_id and row.get('timestamp'):
                        all_records.append(row)
                else:
                    # Admin Role: Show everything
                    all_records.append(row)
        except Exception as e:
            logger.error(f"Error reading {csv_path}: {e}")

    # Sort and add row numbers
    all_records.sort(key=lambda x: str(x.get('timestamp', '')), reverse=True)
    for idx, row in enumerate(all_records):
        row["row"] = idx + 1
    return all_records


@app.post("/predict", response_model=PredictionResponse)
async def predict_and_save(patient: PatientData, background_tasks: BackgroundTasks):
    try:
        disease = patient.disease.lower()
        model_path = f'global_model_{disease}.pth'
        input_dim = DISEASE_FEATURES.get(disease, DISEASE_FEATURES['heart'])['n_features']
        net = HealthNet(input_dim=input_dim)
        if os.path.exists(model_path):
            try:
                checkpoint = torch.load(model_path, map_location='cpu')
                # Verify dimensions match
                if checkpoint['fc1.weight'].shape[1] == input_dim:
                    net.load_state_dict(checkpoint)
                    logger.info(f"Loaded existing model for {disease} prediction")
                else:
                    logger.warning(f"Model {model_path} dimensions mismatch for {disease}. Using fresh model.")
            except Exception as e:
                logger.error(f"Error loading model {model_path}: {e}")
        net.eval()

        raw_vec = _fields_to_input_vector(disease, patient.fields)
        norm = get_norm(disease)
        norm_vec = [raw_vec[i] / norm[i] if norm[i] != 0 else raw_vec[i] for i in range(len(raw_vec))]
        
        with torch.no_grad():
            output = net(torch.Tensor([norm_vec]))
            probability = float(output.item())

        prediction = 1 if probability > 0.5 else 0
        prediction_str = "Positive (High Risk)" if prediction == 1 else "Negative (Low Risk)"
        
        specialist = get_specialist(patient.hospital_id, disease)

        # Save record
        
        csv_path = f"data_{patient.hospital_id.replace(' ', '_')}_{disease}.csv"
        new_row = {k: v for k, v in patient.fields.items() if not k.startswith('_')}
        new_row["result"] = prediction
        new_row["timestamp"] = datetime.now().isoformat()[:10]
        new_row["assigned_doctor"] = specialist
        
        df_new = pd.DataFrame([new_row])
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df = pd.concat([df, df_new], ignore_index=True)
        else:
            df = df_new
        df.to_csv(csv_path, index=False)

        background_tasks.add_task(trigger_fl_cycle, patient.hospital_id, disease)

        return PredictionResponse(
            prediction=prediction_str,
            probability=probability,
            status="success",
            message=f"Report sent to specialist {specialist}."
        )
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
def get_status():
    return training_status


@app.get("/metrics")
def get_metrics(disease: str = "heart"):
    model_path = f'global_model_{disease}.pth'
    if not os.path.exists(model_path):
        return {"accuracy": 0, "precision": 0, "recall": 0, "f1_score": 0, "loss": 0, "n_samples": 0}
    input_dim = DISEASE_FEATURES.get(disease, DISEASE_FEATURES['heart'])['n_features']
    try:
        checkpoint = torch.load(model_path, map_location='cpu')
        if checkpoint['fc1.weight'].shape[1] != input_dim:
            logger.warning(f"Metrics: {model_path} has wrong input_dim for {disease}, skipping")
            return {"accuracy": 0, "precision": 0, "recall": 0, "f1_score": 0, "loss": 0, "n_samples": 0}
        net = HealthNet(input_dim=input_dim)
        net.load_state_dict(checkpoint)
    except Exception as e:
        logger.error(f"Could not load model for metrics: {e}")
        return {"accuracy": 0, "precision": 0, "recall": 0, "f1_score": 0, "loss": 0, "n_samples": 0}
    net.eval()
    return ModelEvaluator.evaluate(net, disease=disease)


@app.get("/disease_features")
def get_disease_features():
    res = {}
    for d, info in DISEASE_FEATURES.items():
        res[d] = {"feature_cols": [c for c in info['feature_cols'] if not c.startswith('_')], "n_features": info['n_features']}
    return res


def _kill_flower_server_on_port(port: int = 8080):
    """Kill any existing process listening on the Flower gRPC port to avoid conflicts."""
    import time as _time
    try:
        # Find PIDs listening on the port
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True, text=True, timeout=5
        )
        pids_to_kill = set()
        for line in result.stdout.splitlines():
            if f":{port}" in line and "LISTENING" in line:
                parts = line.split()
                if parts:
                    try:
                        pids_to_kill.add(int(parts[-1]))
                    except ValueError:
                        pass
        for pid in pids_to_kill:
            try:
                subprocess.run(["taskkill", "/F", "/PID", str(pid)],
                               capture_output=True, timeout=5)
                logger.info(f"Killed existing process on port {port} (PID {pid})")
            except Exception:
                pass
        if pids_to_kill:
            _time.sleep(1)  # Give OS time to release the port
    except Exception as e:
        logger.warning(f"Could not check/kill port {port}: {e}")


def trigger_fl_cycle(hospital_id: str, disease: str):
    global training_status
    with training_lock:
        if training_status['status'] == 'training': return
        training_status['status'] = 'training'
        training_status['current_hospital'] = f"{hospital_id} ({disease})"

    try:
        import time

        # Kill any stale Flower server occupying port 8080 to prevent
        # clients from connecting to a server loaded with the wrong disease model.
        _kill_flower_server_on_port(8080)

        server_proc = subprocess.Popen(
            [sys.executable, "server.py", "--disease", disease, "--rounds", "3"],
            cwd=BACKEND_DIR
        )
        # Wait for the new server to bind before launching clients
        time.sleep(4)
        
        fed_ids = fl_config.FEDERATED_HOSPITAL_IDS
        def run_c(hid):
            subprocess.run([sys.executable, "client.py", "--hospital_id", hid.replace(" ", "_"), "--disease", disease], cwd=BACKEND_DIR)
        
        with ThreadPoolExecutor(max_workers=len(fed_ids)) as pool:
            [pool.submit(run_c, hid) for hid in fed_ids]
            
        server_proc.terminate()
        with training_lock: training_status['status'] = 'complete'
    except Exception as e:
        with training_lock:
            training_status['status'] = 'error'
            training_status['error_message'] = str(e)
    finally:
        threading.Timer(5, lambda: training_status.update({"status": "idle"})).start()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
