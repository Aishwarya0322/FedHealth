"""
TLS helpers for Flower gRPC (server + clients).

Uses self-signed cert.pem / key.pem from generate_cert.py. For a self-signed
server certificate, the CA byte blob in Flower's server tuple is the same PEM
as the server certificate (grpc ssl_server_credentials API).

Set FL_USE_TLS=0 to force plaintext gRPC (development only).
"""
from __future__ import annotations

import os
from pathlib import Path

from logger_config import setup_logging

logger = setup_logging("TLS")

BACKEND_ROOT = Path(__file__).resolve().parent
CERT_FILE = BACKEND_ROOT / "cert.pem"
KEY_FILE = BACKEND_ROOT / "key.pem"


def tls_enabled() -> bool:
    v = os.environ.get("FL_USE_TLS", "1").strip().lower()
    if v in ("0", "false", "no", "off"):
        return False
    return True


def load_server_certificate_tuple() -> tuple[bytes, bytes, bytes] | None:
    """
    Flower expects: (CA certificate PEM, server certificate PEM, server private key PEM).
    Self-signed: use the same PEM for CA and server cert so clients can trust with one file.
    """
    if not tls_enabled():
        return None
    if not CERT_FILE.is_file() or not KEY_FILE.is_file():
        logger.warning(
            "TLS requested but cert.pem or key.pem missing under %s. "
            "Run: python generate_cert.py  (or set FL_USE_TLS=0 for insecure gRPC)",
            BACKEND_ROOT,
        )
        return None
    cert_b = CERT_FILE.read_bytes()
    key_b = KEY_FILE.read_bytes()
    return (cert_b, cert_b, key_b)


def client_tls_kwargs() -> dict:
    """Keyword args for fl.client.start_client."""
    if not tls_enabled():
        logger.info("Flower client: insecure gRPC (FL_USE_TLS=0)")
        return {"insecure": True, "root_certificates": None}
    if not CERT_FILE.is_file():
        logger.warning("Flower client: no cert.pem; using insecure gRPC")
        return {"insecure": True, "root_certificates": None}
    logger.info("Flower client: TLS enabled (trusting %s)", CERT_FILE.name)
    return {
        "insecure": False,
        "root_certificates": CERT_FILE.read_bytes(),
    }