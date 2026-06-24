import os
import json
import logging
import numpy as np
from typing import Optional

# Set up logging
logger = logging.getLogger("HE")
logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------------------------
# Homomorphic Encryption (HE) Configuration
# ---------------------------------------------------------------------------

_context = None
_context_bytes = None

def he_enabled() -> bool:
    v = os.environ.get("FL_USE_HE", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def _get_context():
    """Return (or lazily create/load) the shared TenSEAL CKKS context."""
    global _context, _context_bytes
    if _context is not None:
        return _context

    try:
        import tenseal as ts
    except ImportError:
        raise RuntimeError("TenSEAL is not installed.")

    context_path = "he_context.bin"
    
    if os.path.exists(context_path):
        logger.info(f"Loading shared TenSEAL context from {context_path} …")
        with open(context_path, "rb") as f:
            _context_bytes = f.read()
        _context = ts.context_from(_context_bytes)
    else:
        logger.info("Generating new shared TenSEAL CKKS context (Stable Config) …")
        # Standard stable config for Depth 1
        ctx = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=8192,
            coeff_mod_bit_sizes=[60, 40, 60],
        )
        ctx.generate_galois_keys()
        ctx.global_scale = 2 ** 40
        ctx.auto_relin = True
        ctx.auto_rescale = True
        
        _context_bytes = ctx.serialize(save_secret_key=True)
        with open(context_path, "wb") as f:
            f.write(_context_bytes)
        _context = ctx
        logger.info(f"Shared CKKS context saved to {context_path}")

    return _context


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def encrypt_params(parameters: list[np.ndarray]) -> tuple[list[bytes], list]:
    import tenseal as ts
    ctx = _get_context()
    shapes = [arr.shape for arr in parameters]
    encrypted_blobs = []
    for i, arr in enumerate(parameters):
        # Ensure values are float and reasonably small
        flat = arr.flatten().astype(float).tolist()
        enc_vec = ts.ckks_vector(ctx, flat)
        encrypted_blobs.append(enc_vec.serialize())
    logger.info("[HE] Encrypted %d parameter layers", len(parameters))
    return encrypted_blobs, shapes


def decrypt_params(encrypted_blobs: list[bytes], shapes: list, scale_factor: float = 1.0) -> list[np.ndarray]:
    import tenseal as ts
    ctx = _get_context()
    decrypted = []
    for blob, shape in zip(encrypted_blobs, shapes):
        enc_vec = ts.ckks_vector_from(ctx, blob)
        # Decrypt and apply normalisation
        vals = np.array(enc_vec.decrypt()) * scale_factor
        # Final safety check for NaNs/Infs
        vals = np.nan_to_num(vals, nan=0.0, posinf=10.0, neginf=-10.0)
        
        expected = int(np.prod(shape))
        flat = vals[:expected].astype(np.float32)
        decrypted.append(flat.reshape(shape))
    logger.info("[HE] Decrypted %d parameter layers", len(decrypted))
    return decrypted


def aggregate_encrypted(
    all_blobs: list[list[bytes]],
    weights: list[float],
) -> tuple[list[bytes], float]:
    """
    Weighted FedAvg on ciphertexts using float-ciphertext multiplication.
    With Depth 1 context [60, 40, 60], this is the standard TenSEAL way.
    """
    import tenseal as ts
    ctx = _get_context()
    n_layers = len(all_blobs[0])
    n_clients = len(all_blobs)
    
    result_blobs = []
    for layer_idx in range(n_layers):
        # Sum_i( Ciphertext_i * weight_i )
        agg = ts.ckks_vector_from(ctx, all_blobs[0][layer_idx]) * weights[0]
        for client_idx in range(1, n_clients):
            other = ts.ckks_vector_from(ctx, all_blobs[client_idx][layer_idx])
            agg = agg + (other * weights[client_idx])
        result_blobs.append(agg.serialize())

    logger.info("[HE] Weighted aggregation complete (float-weights)")
    return result_blobs, 1.0  # Normalisation is already handled by float weights summing to 1


# ---------------------------------------------------------------------------
# Serialisation helpers
# ---------------------------------------------------------------------------

def pack_encrypted_to_ndarrays(encrypted_blobs: list[bytes], shapes: list) -> list[np.ndarray]:
    meta = json.dumps([list(s) for s in shapes]).encode()
    meta_arr = np.frombuffer(meta, dtype=np.uint8)
    packed = [meta_arr]
    for blob in encrypted_blobs:
        packed.append(np.frombuffer(blob, dtype=np.uint8))
    return packed


def unpack_ndarrays_to_encrypted(packed: list[np.ndarray]) -> tuple[list[bytes], list]:
    meta_arr = packed[0]
    shapes_raw = json.loads(meta_arr.tobytes().decode())
    shapes = [tuple(s) for s in shapes_raw]
    encrypted_blobs = [arr.tobytes() for arr in packed[1:]]
    return encrypted_blobs, shapes


def is_he_packed(parameters: list[np.ndarray]) -> bool:
    if not parameters:
        return False
    return parameters[0].dtype == np.uint8 and parameters[0].ndim == 1
