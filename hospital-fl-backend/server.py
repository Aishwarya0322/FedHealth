"""
Federated Learning Central Aggregation Server
Implements FedAvg algorithm for secure global model aggregation.
Security layers:
  - TLS (gRPC channel encryption)
  - SHA-256 integrity verification of client parameters
  - Homomorphic Encryption (CKKS) aggregation on ciphertext
"""
import flwr as fl
import torch
import os
import argparse
from model import HealthNet
from data_loader import DISEASE_FEATURES
from logger_config import setup_logging
from fl_config import federated_hospital_count
from fl_tls import load_server_certificate_tuple
from fl_integrity import verify_params_hash
from fl_he import (
    he_enabled, aggregate_encrypted, decrypt_params,
    pack_encrypted_to_ndarrays, unpack_ndarrays_to_encrypted, is_he_packed
)

logger = setup_logging('Server')

class SaveModelStrategy(fl.server.strategy.FedAvg):
    """
    Custom FedAvg strategy that saves the global model after aggregation, specific to a disease.
    """
    def __init__(self, disease, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.disease = disease

    def aggregate_fit(self, server_round, results, failures):
        logger.info(f"--- Aggregation Round {server_round} for {self.disease} ---")

        # ── Step 8: Integrity verification ────────────────────────────────
        # Each client embeds a SHA-256 hash of its (pre-encryption) params
        # in metrics.  We reconstruct the plaintext params and verify before
        # allowing them into aggregation.
        verified_results = []
        for client_proxy, fit_res in results:
            metrics = fit_res.metrics or {}
            expected_hash = metrics.get("params_hash", None)
            raw_params = fl.common.parameters_to_ndarrays(fit_res.parameters)

            # Verify hash on the exact raw payload received
            if expected_hash:
                ok = verify_params_hash(raw_params, expected_hash)
                if not ok:
                    logger.warning(
                        "[Integrity] Rejecting update from client (hash mismatch) "
                        "in round %d", server_round
                    )
                    continue  # drop tampered update
            else:
                logger.warning("[Integrity] Client sent no hash — accepting without verification")

            verified_results.append((client_proxy, fit_res))

        if not verified_results:
            logger.error("All client updates were rejected! Skipping round %d", server_round)
            return None, {}

        rejected = len(results) - len(verified_results)
        if rejected:
            logger.warning("%d client update(s) rejected due to integrity failure", rejected)

        # ── Trust Score Calculation (Novelty) ──────────────────────────────
        trust_scores = []
        for _, fit_res in verified_results:
            metrics = fit_res.metrics or {}
            # Use local_accuracy as the trust score metric
            acc = metrics.get("local_accuracy", 0.0)
            # Add a small epsilon to prevent a client from having exactly 0 influence
            trust_scores.append(max(acc, 0.01))

        total_trust = sum(trust_scores)
        weights = [ts / total_trust for ts in trust_scores]
        logger.info("[Trust Score] Normalized weights: " + ", ".join(f"{w:.3f}" for w in weights))

        # ── Step 9: HE Aggregation ─────────────────────────────────────────
        # If all verified clients sent encrypted params, do FedAvg on ciphertext.
        all_he = all(
            bool((r[1].metrics or {}).get("he_encrypted", 0))
            for r in verified_results
        )

        if all_he and he_enabled():
            logger.info("[HE] All clients sent encrypted parameters — performing Trust-Score Encrypted FedAvg")
            all_blobs = []
            shapes_ref = None
            for _, fit_res in verified_results:
                raw = fl.common.parameters_to_ndarrays(fit_res.parameters)
                enc_blobs, shapes = unpack_ndarrays_to_encrypted(raw)
                all_blobs.append(enc_blobs)
                if shapes_ref is None:
                    shapes_ref = shapes

            try:
                # NEW: aggregate_encrypted returns (blobs, norm_factor)
                agg_blobs, norm_factor = aggregate_encrypted(all_blobs, weights)
                # NEW: decrypt_params takes norm_factor to normalize after integer scaling
                agg_plain = decrypt_params(agg_blobs, shapes_ref, norm_factor)
                
                # DEBUG: Log min/max of aggregated parameters
                for i, layer in enumerate(agg_plain):
                    logger.info(f"[DEBUG HE] Layer {i} aggregated min: {layer.min():.4f}, max: {layer.max():.4f}")
                
                logger.info("[HE] Trust-Score Encrypted FedAvg complete — decrypted for model save")

                # Re-encrypt for sending back to clients
                re_enc_blobs, _ = __import__('fl_he').encrypt_params(agg_plain)
                packed = pack_encrypted_to_ndarrays(re_enc_blobs, shapes_ref)
                aggregated_parameters = fl.common.ndarrays_to_parameters(packed)
                aggregated_metrics = {}

                # Save the aggregated plaintext model
                self._save_model(agg_plain, server_round)
                return aggregated_parameters, aggregated_metrics

            except Exception as e:
                logger.error("[HE] Encrypted aggregation failed (%s) — falling back to plaintext", e)
                # Fall through to standard FedAvg

        # ── Standard (plaintext) FedAvg with Trust Scores ──────────────────
        import copy
        trusted_verified_results = []
        for (client_proxy, fit_res), weight in zip(verified_results, weights):
            new_res = copy.copy(fit_res)
            # Spoof num_examples so that Flower's native FedAvg uses the Trust Score weights
            new_res.num_examples = max(1, int(weight * 100000))
            trusted_verified_results.append((client_proxy, new_res))

        aggregated_parameters, aggregated_metrics = super().aggregate_fit(
            server_round, trusted_verified_results, failures
        )

        if aggregated_parameters is not None:
            plain = fl.common.parameters_to_ndarrays(aggregated_parameters)
            self._save_model(plain, server_round)

        return aggregated_parameters, aggregated_metrics

    def _save_model(self, param_arrays, server_round):
        """Save the aggregated global model weights to disk."""
        input_dim = DISEASE_FEATURES.get(self.disease, DISEASE_FEATURES['heart'])['n_features']
        net = HealthNet(input_dim=input_dim)
        try:
            params_dict = zip(net.state_dict().keys(), param_arrays)
            state_dict = {k: torch.tensor(v, dtype=torch.float32) for k, v in params_dict}
            net.load_state_dict(state_dict, strict=True)
            model_name = f'global_model_{self.disease}.pth'
            torch.save(net.state_dict(), model_name)
            logger.info(f"[OK] Global model saved as {model_name} (Round {server_round})")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")

def start_server(disease, num_rounds=3, min_clients=None):
    if min_clients is None:
        min_clients = federated_hospital_count()
    logger.info("=" * 60)
    logger.info(f"FEDERATED LEARNING SERVER STARTING FOR DISEASE: {disease.upper()}")
    logger.info("=" * 60)
    logger.info(f"Configuration: {num_rounds} rounds, min {min_clients} clients")
    
    # Check if we should initialize with existing weights
    initial_parameters = None
    model_name = f'global_model_{disease}.pth'
    input_dim = DISEASE_FEATURES.get(disease, DISEASE_FEATURES['heart'])['n_features']
    if os.path.exists(model_name):
        try:
            checkpoint = torch.load(model_name, map_location='cpu')
            # Validate that the saved checkpoint matches this disease's feature dimension.
            # fc1.weight has shape [32, input_dim]; mismatch means a stale/wrong checkpoint.
            saved_input_dim = checkpoint['fc1.weight'].shape[1]
            if saved_input_dim != input_dim:
                logger.warning(
                    "Checkpoint '%s' has input_dim=%d but disease '%s' expects %d. "
                    "Discarding stale checkpoint and starting from scratch.",
                    model_name, saved_input_dim, disease, input_dim,
                )
            else:
                net = HealthNet(input_dim=input_dim)
                net.load_state_dict(checkpoint)
                initial_parameters = fl.common.ndarrays_to_parameters(
                    [val.cpu().numpy() for _, val in net.state_dict().items()]
                )
                logger.info(f"Loading existing global model weights from {model_name}")
        except Exception as e:
            logger.warning("Could not load checkpoint '%s': %s. Starting from scratch.", model_name, e)

    strategy = SaveModelStrategy(
        disease=disease,
        fraction_fit=1.0,
        fraction_evaluate=1.0,
        min_fit_clients=min_clients,
        min_evaluate_clients=min_clients,
        min_available_clients=min_clients,
        initial_parameters=initial_parameters
    )
    
    certs = load_server_certificate_tuple()
    if certs is not None:
        logger.info("Flower server: TLS enabled on 0.0.0.0:8080")
    else:
        logger.warning("Flower server: insecure gRPC on 0.0.0.0:8080")
        
    fl.server.start_server(
        server_address="0.0.0.0:8080",
        strategy=strategy,
        config=fl.server.ServerConfig(num_rounds=num_rounds),
        certificates=certs,
    )
    
    logger.info("=" * 60)
    logger.info("SERVER SHUTDOWN")
    logger.info("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FL Server")
    parser.add_argument('--disease', type=str, default='heart', help='Disease context for FL')
    parser.add_argument('--rounds', type=int, default=3, help='Number of rounds')
    parser.add_argument('--clients', type=int, default=None, help='Minimum clients')
    
    args = parser.parse_args()
    
    start_server(disease=args.disease, num_rounds=args.rounds, min_clients=args.clients)