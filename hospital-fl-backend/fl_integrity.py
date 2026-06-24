"""
fl_integrity.py
---------------
SHA-256 based integrity verification for Federated Learning model parameters.

Each hospital client computes a hash of its parameter arrays before transmission.
The central server verifies the hash on receipt to detect any tampering or
corruption in transit.

Usage:
    # Client side — before sending
    digest = compute_params_hash(param_list)

    # Server side — after receiving
    ok = verify_params_hash(received_params, expected_digest)
"""
from __future__ import annotations

import hashlib
import json
import numpy as np

from logger_config import setup_logging

logger = setup_logging("Integrity")


def compute_params_hash(parameters: list[np.ndarray]) -> str:
    """
    Compute a deterministic SHA-256 digest over a list of numpy parameter arrays.

    The hash covers:
      - Number of layers
      - dtype, shape, and raw byte content of every array

    Returns:
        Hex string (64 characters).
    """
    hasher = hashlib.sha256()

    # Include structural metadata so that a shape-change also invalidates the hash
    meta = json.dumps(
        [{"dtype": str(a.dtype), "shape": list(a.shape)} for a in parameters],
        sort_keys=True,
    ).encode()
    hasher.update(meta)

    for arr in parameters:
        hasher.update(np.ascontiguousarray(arr).tobytes())

    digest = hasher.hexdigest()
    logger.debug("Computed parameter hash: %s…", digest[:16])
    return digest


def verify_params_hash(parameters: list[np.ndarray], expected_hash: str) -> bool:
    """
    Verify that received parameters match the expected SHA-256 digest.

    Returns True if the hash matches, False otherwise.
    Logs a warning on mismatch so it appears in the FL system log.
    """
    actual = compute_params_hash(parameters)
    if actual == expected_hash:
        logger.info("[Integrity OK] Parameter hash verified: %s…", actual[:16])
        return True
    else:
        logger.warning(
            "[Integrity FAIL] Hash mismatch! "
            "Expected: %s…  Got: %s…  — update will be REJECTED.",
            expected_hash[:16],
            actual[:16],
        )
        return False
