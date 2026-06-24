"""
Hospital Client Node for Federated Learning
Implements:
- Step 5: Local Training with PyTorch
- Step 6: Differential Privacy Protection
- Step 7: Secure Transmission via TLS
- Step 8: SHA-256 Integrity Hashing of parameters before transmission
- Step 9: Homomorphic Encryption (TenSEAL CKKS) of parameters
"""
import flwr as fl
import torch
import numpy as np
import argparse
from torch.utils.data import DataLoader
from model import HealthNet, train, test
from data_loader import get_hospital_dataset, DISEASE_FEATURES
from logger_config import setup_logging
from fl_tls import client_tls_kwargs
from fl_integrity import compute_params_hash
from fl_he import (
    he_enabled, encrypt_params, decrypt_params,
    pack_encrypted_to_ndarrays, unpack_ndarrays_to_encrypted, is_he_packed
)

logger = setup_logging('Client')

class HospitalClient(fl.client.NumPyClient):
    """
    Flower NumPyClient for hospital nodes.
    Trains locally and sends aggregated parameters to server.
    """
    
    def __init__(self, net, trainloader, testloader, hospital_id, disease):
        self.net = net
        self.trainloader = trainloader
        self.testloader = testloader
        self.hospital_id = hospital_id
        self.disease = disease
        self.round = 0
        logger.info(f"Client initialized: {hospital_id} for {disease}")
        logger.info(f"Train samples: {len(trainloader.dataset)}, Test samples: {len(testloader.dataset)}")

    def get_parameters(self, config):
        """Extract model parameters as numpy arrays"""
        logger.debug("get_parameters() called")
        return [val.cpu().numpy() for _, val in self.net.state_dict().items()]

    def set_parameters(self, parameters):
        """Load parameters into model — auto-decrypts HE-packed params if needed."""
        logger.debug(f"set_parameters() called with {len(parameters)} tensors")

        # Detect and decrypt homomorphically-encrypted parameters from server
        if is_he_packed(parameters) and he_enabled():
            logger.info("[HE] Received encrypted global parameters — decrypting …")
            enc_blobs, shapes = unpack_ndarrays_to_encrypted(list(parameters))
            parameters = decrypt_params(enc_blobs, shapes)
            logger.info("[HE] Decryption complete")

        params_dict = zip(self.net.state_dict().keys(), parameters)
        state_dict = {k: torch.tensor(v, dtype=torch.float32) for k, v in params_dict}
        self.net.load_state_dict(state_dict, strict=True)

    def fit(self, parameters, config):
        self.round += 1
        logger.info(f"=== Training Round {self.round} ===")
        
        self.set_parameters(parameters)
        logger.info("Global parameters loaded")
        
        logger.info("Starting local training...")
        try:
            train(self.net, self.trainloader, epochs=1)
            logger.info("[OK] Local training completed")
        except Exception as e:
            logger.error(f"Training error: {e}", exc_info=True)
        
        # ── Step 6: Differential Privacy ──────────────────────────────────
        dp_params = []
        try:
            epsilon = 1.0
            noise_scale = 1.0 / epsilon
            for param in self.get_parameters(config={}):
                noise = np.random.laplace(0, noise_scale, param.shape)
                noisy_param = param.astype(np.float32) + noise.astype(np.float32)
                dp_params.append(noisy_param)
            logger.info(f"[OK] Differential Privacy applied (epsilon={epsilon})")
        except Exception as e:
            logger.error(f"DP application error: {e}")
            dp_params = self.get_parameters(config={})

        # ── Step 9: Homomorphic Encryption ───────────────────────────────
        outgoing_params = dp_params
        
        # DEBUG: Log min/max of dp_params before encryption
        for i, param in enumerate(dp_params):
            logger.info(f"[DEBUG CLIENT] Layer {i} min: {param.min():.4f}, max: {param.max():.4f}")
            
        he_used = False
        if he_enabled():
            try:
                enc_blobs, shapes = encrypt_params(dp_params)
                outgoing_params = pack_encrypted_to_ndarrays(enc_blobs, shapes)
                he_used = True
                logger.info("[HE] Parameters encrypted with CKKS before transmission")
            except Exception as e:
                logger.warning("[HE] Encryption failed (%s) — sending plaintext", e)

        # ── Step 8: Integrity Hash ────────────────────────────────────────
        params_hash = compute_params_hash(outgoing_params)
        logger.info("[Integrity] SHA-256 of outgoing params: %s…", params_hash[:16])

        try:
            loss, accuracy = test(self.net, self.testloader)
            logger.info(f"Local Test: Loss={loss:.4f}, Accuracy={accuracy:.4f}")
        except Exception as e:
            logger.error(f"Local evaluation error: {e}")
            loss, accuracy = 0.0, 0.0

        metrics = {
            "hospital_id": self.hospital_id,
            "disease": self.disease,
            "local_loss": float(loss),
            "local_accuracy": float(accuracy),
            "round": self.round,
            "params_hash": params_hash,        # for server-side integrity check
            "he_encrypted": int(he_used),      # flag so server knows format
        }

        logger.info(
            "Returning %d parameter layers | HE=%s | hash=%s…",
            len(outgoing_params), he_used, params_hash[:16]
        )
        return outgoing_params, len(self.trainloader.dataset), metrics

    def evaluate(self, parameters, config):
        logger.info(f"Evaluation requested (Round {self.round})")
        
        self.set_parameters(parameters)
        loss, accuracy = test(self.net, self.testloader)
        
        logger.info(f"Round {self.round} Eval: Loss={loss:.4f}, Accuracy={accuracy:.4f}")
        
        return float(loss), len(self.testloader.dataset), {
            "accuracy": float(accuracy),
            "hospital_id": self.hospital_id,
            "disease": self.disease
        }

def start_client(hospital_id="Hospital_1", disease="heart"):
    logger.info("=" * 60)
    logger.info(f"HOSPITAL CLIENT STARTING: {hospital_id} FOR {disease.upper()}")
    logger.info("=" * 60)
    
    try:
        logger.info(f"Loading dataset for {hospital_id} ({disease})...")
        trainloader, testloader = get_hospital_dataset(hospital_id, disease_type=disease)
        logger.info(f"[OK] Dataset loaded")
        
        input_dim = DISEASE_FEATURES.get(disease, DISEASE_FEATURES['heart'])['n_features']
        net = HealthNet(input_dim=input_dim)
        logger.info(f"[OK] Model initialized")
        
        client = HospitalClient(net, trainloader, testloader, hospital_id, disease)
        
        tls_kw = client_tls_kwargs()
        logger.info(f"Connecting to Flower server at 127.0.0.1:8080 (TLS={not tls_kw.get('insecure', True)})...")
        fl.client.start_client(
            server_address="127.0.0.1:8080",
            client=client.to_client(),
            **tls_kw,
        )
        
        logger.info("=" * 60)
        logger.info("CLIENT SHUTDOWN")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Client error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FL Client")
    parser.add_argument('--hospital_id', type=str, required=True, help='Hospital ID')
    parser.add_argument('--disease', type=str, default='heart', help='Disease context for FL')
    
    args = parser.parse_args()
    
    start_client(args.hospital_id, args.disease)