import pandas as pd
import numpy as np
import os

# ──────────────────────────────────────────────────────────────────────────────
# Disease-specific feature definitions
# ──────────────────────────────────────────────────────────────────────────────

DISEASE_FEATURES = {
    'heart': {
        'feature_cols': [
            'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs',
            'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal'
        ],
        'norm': np.array([100.0, 1.0, 3.0, 200.0, 400.0, 1.0, 2.0, 200.0, 1.0, 10.0, 2.0, 3.0, 7.0]),
        'target_col': 'target',
        'result_col': 'result',
        'n_features': 13,
    },
    'cancer': {
        'feature_cols': [
            'Age', 'Gender', 'Air Pollution', 'Alcohol use', 'Dust Allergy',
            'OccuPational Hazards', 'Genetic Risk', 'Chronic Lung Disease',
            'Balanced Diet', 'Obesity', 'Smoking', 'Passive Smoker', 'Chest Pain',
            'Coughing of Blood', 'Fatigue', 'Weight Loss', 'Shortness of Breath',
            'Wheezing', 'Swallowing Difficulty', 'Clubbing of Finger Nails',
            'Frequent Cold', 'Dry Cough', 'Snoring'
        ],
        'norm': np.array([
            100.0, 1.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 
            9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 
            9.0, 9.0, 9.0
        ]),
        'target_col': 'Level',
        'result_col': 'result',
        'n_features': 23,
    },
    'anaemia': {
        'feature_cols': [
            'Sex', '%Red Pixel', '%Green Pixel', '%Blue Pixel', 'Hb'
        ],
        'norm': np.array([1.0, 100.0, 100.0, 100.0, 25.0]),
        'target_col': 'Anaemic',
        'result_col': 'result',
        'n_features': 5,
    },
}

# Legacy aliases so existing imports keep working
FEATURE_COLS = DISEASE_FEATURES['heart']['feature_cols']
NORM = DISEASE_FEATURES['heart']['norm']


def get_feature_cols(disease: str):
    return DISEASE_FEATURES.get(disease, DISEASE_FEATURES['heart'])['feature_cols']


def get_norm(disease: str):
    return DISEASE_FEATURES.get(disease, DISEASE_FEATURES['heart'])['norm']


# ──────────────────────────────────────────────────────────────────────────────
# Dataset loaders
# ──────────────────────────────────────────────────────────────────────────────

def load_heart_disease_dataset():
    """Load UCI Heart Disease dataset (downloads if not cached)."""
    csv_file = 'heart_disease.csv'
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
    else:
        print("Downloading UCI Heart Disease dataset...")
        try:
            url = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart/processed.cleveland.data"
            column_names = [
                'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg',
                'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'target'
            ]
            df = pd.read_csv(url, names=column_names, na_values='?')
            df.to_csv(csv_file, index=False)
        except Exception as e:
            print(f"Download failed: {e}. Using synthetic data instead.")
            return None
    df = df.dropna()
    feat_cols = DISEASE_FEATURES['heart']['feature_cols']
    X = df[feat_cols].values.astype(float)
    y = (df['target'] > 0).astype(int).values
    return X, y




def load_cancer_dataset(csv_path: str):
    """Load lung cancer CSV with correct features."""
    df = pd.read_csv(csv_path).dropna()
    feat_info = DISEASE_FEATURES['cancer']
    feat_cols = feat_info['feature_cols']
    n_features = feat_info['n_features']
    
    # Gender / Sex column may have string values
    if 'Gender' in df.columns:
        df['Gender'] = (df['Gender'].str.lower() == 'male').astype(int)
        
    available = [c for c in feat_cols if c in df.columns]
    X = df[available].values.astype(float)
    
    # Pad or truncate to n_features if necessary (usually they should match)
    if X.shape[1] < n_features:
        X = np.hstack([X, np.zeros((X.shape[0], n_features - X.shape[1]))])
    elif X.shape[1] > n_features:
        X = X[:, :n_features]
        
    target_col = feat_info['target_col']
    y_raw = df[target_col].values if target_col in df.columns else df.iloc[:, -1].values
    if pd.api.types.is_numeric_dtype(y_raw):
        y = (pd.Series(y_raw).astype(float) > 1.5).astype(int).values # Level 1, 2, 3 -> Low, Medium, High. User might want binary? Let's assume High/Medium is 1.
    else:
        y = (pd.Series(y_raw).str.lower().isin(['high', 'medium', 'positive', 'yes', '1'])).astype(int).values
    return X, y


def load_anaemia_dataset(csv_path: str):
    """Load anaemia CSV with correct features."""
    df = pd.read_csv(csv_path).dropna()
    feat_info = DISEASE_FEATURES['anaemia']
    feat_cols = feat_info['feature_cols']
    n_features = feat_info['n_features']

    # Sex column: Male=1, Female=0
    if 'Sex' in df.columns:
        df['Sex'] = (df['Sex'].str.lower() == 'male').astype(int)
        
    available = [c for c in feat_cols if c in df.columns]
    X = df[available].values.astype(float)
    
    # Pad or truncate if necessary
    if X.shape[1] < n_features:
        X = np.hstack([X, np.zeros((X.shape[0], n_features - X.shape[1]))])
    elif X.shape[1] > n_features:
        X = X[:, :n_features]
        
    target_col = feat_info['target_col']
    y_raw = df[target_col].values if target_col in df.columns else df.iloc[:, -1].values
    if pd.api.types.is_numeric_dtype(y_raw):
        y = (y_raw > 0).astype(int)
    else:
        y = (pd.Series(y_raw).str.lower().isin(['yes', '1', 'positive', 'anaemic', 'anemic'])).astype(int).values
    return X, y


def generate_synthetic_data(disease_type, num_samples=100):
    """Generate synthetic data shaped for each disease type."""
    feat_info = DISEASE_FEATURES.get(disease_type, DISEASE_FEATURES['heart'])
    n_features = feat_info['n_features']
    norm = feat_info['norm']
    
    X_raw = np.random.rand(num_samples, n_features) * norm
    y = np.random.randint(0, 2, num_samples)
    return X_raw, y


# ──────────────────────────────────────────────────────────────────────────────
# Hospital dataset builder
# ──────────────────────────────────────────────────────────────────────────────

def get_hospital_dataset(hospital_id, test_size=0.2, disease_type='heart'):
    """
    Build train/test DataLoaders for a hospital node for a specific disease.
    Reads from disease-specific CSV: data_<hospital_id>_<disease_type>.csv
    """
    import torch
    from torch.utils.data import DataLoader, TensorDataset

    disease_info = DISEASE_FEATURES.get(disease_type, DISEASE_FEATURES['heart'])
    feat_cols = disease_info['feature_cols']
    norm = disease_info['norm']

    hospital_csv = f"data_{str(hospital_id).replace(' ', '_')}_{disease_type}.csv"

    if os.path.exists(hospital_csv):
        df = pd.read_csv(hospital_csv)
        # Use whatever feature columns are present in the CSV
        available_feats = [c for c in feat_cols if c in df.columns]
        if not available_feats or 'result' not in df.columns:
            print(f"WARNING: {hospital_csv} missing expected columns. Falling back to synthetic.")
            X_raw, y = generate_synthetic_data(disease_type, 100)
        else:
            X_raw = df[available_feats].values.astype(float)
            # Pad or truncate if necessary
            if X_raw.shape[1] < disease_info['n_features']:
                pad = np.zeros((X_raw.shape[0], disease_info['n_features'] - X_raw.shape[1]))
                X_raw = np.hstack([X_raw, pad])
            elif X_raw.shape[1] > disease_info['n_features']:
                X_raw = X_raw[:, :disease_info['n_features']]
            y = df['result'].values.astype(int)
            print(f"Hospital {hospital_id} ({disease_type}): loaded {len(df)} samples from {hospital_csv}")
    else:
        print(f"No CSV found for {hospital_id} ({disease_type}), generating synthetic data")
        X_raw, y = generate_synthetic_data(disease_type, 100)

    # Normalize
    norm_arr = get_norm(disease_type)
    X = X_raw / norm_arr

    tensor_x = torch.Tensor(X)
    tensor_y = torch.Tensor(y)
    dataset = TensorDataset(tensor_x, tensor_y)
    n = len(dataset)
    if n < 2:
        train_dataset = dataset
        test_dataset = dataset
    else:
        train_size = max(1, min(n - 1, int((1 - test_size) * n)))
        test_size_count = n - train_size
        train_dataset, test_dataset = torch.utils.data.random_split(
            dataset, [train_size, test_size_count]
        )

    trainloader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    testloader = DataLoader(test_dataset, batch_size=16)
    return trainloader, testloader