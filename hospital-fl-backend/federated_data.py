"""
Disjoint splits — one CSV per federated hospital per disease.
Each disease uses its OWN feature columns.
Heart data is sourced from existing data_HOSP-00X.csv files.
"""
import os
import numpy as np
import pandas as pd

from logger_config import setup_logging
from data_loader import (
    DISEASE_FEATURES,
    load_heart_disease_dataset,
    load_cancer_dataset,
    load_anaemia_dataset,
    generate_synthetic_data,
)

logger = setup_logging("FederatedData")
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _hospital_csv_path(hospital_id: str, disease: str) -> str:
    return f"data_{str(hospital_id).replace(' ', '_')}_{disease}.csv"


def _load_disease_data(disease: str, hospital_id=None):
    """
    Load the source dataset for the given disease.
    """
    feat_info = DISEASE_FEATURES[disease]
    feat_cols = feat_info['feature_cols']

    if disease == 'heart':
        # Special case: heart data should come from data_HOSP-00X.csv if hospital_id is provided
        if hospital_id:
            src_path = os.path.join(PROJECT_ROOT, "hospital-fl-backend", f"data_{hospital_id.replace(' ', '_')}.csv")
            if os.path.exists(src_path):
                logger.info(f"Loading heart data for {hospital_id} from existing source: {src_path}")
                df = pd.read_csv(src_path)
                # Keep only valid heart feature columns + result
                valid_cols = [c for c in feat_cols if c in df.columns]
                X = df[valid_cols].values.astype(float)
                if X.shape[1] < feat_info['n_features']:
                    X = np.hstack([X, np.zeros((X.shape[0], feat_info['n_features'] - X.shape[1]))])
                y = df['result'].values if 'result' in df.columns else np.zeros(len(df))
                return X, y, feat_cols

        # Fallback if no specific source found
        result = load_heart_disease_dataset()
        if result is None:
            logger.warning("Using synthetic data for heart.")
            X_raw, y = generate_synthetic_data('heart', 200)
        else:
            X_raw, y = result
        return X_raw, y, feat_cols

    # For other diseases
    custom_csv = os.path.join(PROJECT_ROOT, f"{disease}.csv")
    if not os.path.exists(custom_csv):
        logger.warning(f"No {custom_csv} found. Using synthetic data for {disease}.")
        X_raw, y = generate_synthetic_data(disease, 200)
        return X_raw, y, feat_cols

    logger.info(f"Loading {disease} dataset from {custom_csv}")
    try:
        if disease == 'cancer':
            X_raw, y = load_cancer_dataset(custom_csv)
        elif disease == 'anaemia':
            X_raw, y = load_anaemia_dataset(custom_csv)
        else:
            X_raw, y = generate_synthetic_data(disease, 200)
        return X_raw, y, feat_cols
    except Exception as e:
        logger.error(f"Failed to load {custom_csv}: {e}")
        X_raw, y = generate_synthetic_data(disease, 200)
        return X_raw, y, feat_cols


def materialize_disjoint_hospital_csvs(hospital_ids: list, force: bool = False) -> None:
    diseases = ['heart', 'cancer', 'anaemia']

    for disease in diseases:
        feat_info = DISEASE_FEATURES[disease]
        feat_cols = feat_info['feature_cols']

        for hospital_id in hospital_ids:
            path = _hospital_csv_path(hospital_id, disease)
            
            # If heart, we load specifically for this hospital
            if disease == 'heart':
                X_h, y_h, f_cols = _load_disease_data('heart', hospital_id)
                n_feat = min(X_h.shape[1], len(f_cols))
                row_dict = {f_cols[i]: X_h[:, i] for i in range(n_feat)}
                df_h = pd.DataFrame(row_dict)
                df_h["result"] = y_h
                df_h.to_csv(path, index=False)
                logger.info(f"Sync-ed heart data for {hospital_id} -> {path}")
                continue

            # For others, we split the global set once (outside this inner loop usually, 
            # but let's keep it simple and just do it once per disease)
            if hospital_id == hospital_ids[0] or force:
                 # Load global data and split
                 X_raw, y, f_cols = _load_disease_data(disease)
                 n_total = len(X_raw)
                 rng = np.random.RandomState(42)
                 perm = rng.permutation(n_total)
                 K = len(hospital_ids)
                 stripes = [perm[i::K] for i in range(K)]
                 
                 for i, h_id in enumerate(hospital_ids):
                     p = _hospital_csv_path(h_id, disease)
                     idx = stripes[i]
                     X_sub = X_raw[idx]
                     y_sub = y[idx]
                     
                     n_f = min(X_sub.shape[1], len(f_cols))
                     d = {f_cols[j]: X_sub[:, j] for j in range(n_f)}
                     df_sub = pd.DataFrame(d)
                     df_sub.drop(columns=[c for c in df_sub.columns if c.startswith('_f')], inplace=True, errors='ignore')
                     df_sub["result"] = y_sub
                     df_sub.to_csv(p, index=False)
                     logger.info(f"Split {disease} for {h_id} -> {p}")


def partition_bootstrap_on_startup(hospital_ids: list) -> None:
    force = os.environ.get("FL_FORCE_PARTITION") == "1"
    materialize_disjoint_hospital_csvs(hospital_ids, force=force)