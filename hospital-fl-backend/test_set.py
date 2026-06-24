"""
Secure Federated Learning Test Set Module
Creates and persists a central holdout test set for evaluation
"""
import numpy as np
import pandas as pd
import torch
from torch.utils.data import TensorDataset, DataLoader
import os

from data_loader import DISEASE_FEATURES, load_heart_disease_dataset, load_cancer_dataset, load_anaemia_dataset

def get_holdout_file(disease):
    return f'holdout_test_set_{disease}.csv'

HOLDOUT_SIZE = 0.1

def create_holdout_test_set(disease='heart'):
    """
    Creates a central test set for a specific disease.
    """
    fname = get_holdout_file(disease)
    if os.path.exists(fname):
        print(f"Holdout test set already exists: {fname}")
        return
    
    print(f"Creating holdout test set for {disease}...")
    
    feat_info = DISEASE_FEATURES[disease]
    feat_cols = feat_info['feature_cols']
    
    try:
        if disease == 'heart':
            result = load_heart_disease_dataset()
            X, y = result if result else (None, None)
        elif disease == 'cancer':
            X, y = load_cancer_dataset('cancer.csv')
        elif disease == 'anaemia':
            X, y = load_anaemia_dataset('anaemia.csv')
        else:
            X, y = None, None

        if X is None:
            raise ValueError(f"No data for {disease}")
            
        # Create holdout set
        n_holdout = max(5, int(HOLDOUT_SIZE * len(X)))
        indices = np.random.RandomState(42).permutation(len(X))
        X_holdout = X[indices[:n_holdout]]
        y_holdout = y[indices[:n_holdout]]
        
        df_holdout = pd.DataFrame(X_holdout, columns=feat_cols)
        df_holdout['result'] = y_holdout
        df_holdout.to_csv(fname, index=False)
        print(f"Holdout set created: {len(df_holdout)} samples for {disease}")
        
    except Exception as e:
        print(f"Failed to create holdout set for {disease}: {e}. Generating synthetic fallback.")
        from data_loader import generate_synthetic_data
        X_holdout, y_holdout = generate_synthetic_data(disease, 30)
        df_holdout = pd.DataFrame(X_holdout, columns=feat_cols)
        df_holdout['result'] = y_holdout
        df_holdout.to_csv(fname, index=False)

def get_holdout_test_loader(disease='heart', batch_size=16):
    """
    Loads the central holdout test set for a specific disease.
    Returns PyTorch DataLoader for evaluation.
    """
    fname = get_holdout_file(disease)
    if not os.path.exists(fname):
        create_holdout_test_set(disease)
    
    df = pd.read_csv(fname)
    feat_info = DISEASE_FEATURES[disease]
    feat_cols = feat_info['feature_cols']
    norm = feat_info['norm']
    
    X = df[feat_cols].values / norm
    y = df['result'].values
    
    tensor_x = torch.Tensor(X)
    tensor_y = torch.Tensor(y)
    dataset = TensorDataset(tensor_x, tensor_y)
    return DataLoader(dataset, batch_size=batch_size, shuffle=False)
