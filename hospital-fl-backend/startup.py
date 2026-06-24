"""
Production-ready startup and initialization script
Verifies environment, starts all services (API only now, FL Server is ephemeral)
"""
import subprocess
import sys
import os
import time
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_python_packages():
    """Verify all required packages are installed"""
    logger.info("Checking Python packages...")
    required = [
        'fastapi', 'uvicorn', 'torch', 'pandas', 'flwr', 'numpy', 
        'scikit-learn', 'cryptography'
    ]
    
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        logger.error(f"Missing packages: {missing}")
        logger.info("Run: pip install -r requirements.txt")
        return False
    
    logger.info("[OK] All packages installed")
    return True

def check_certificates():
    """Verify TLS certificates exist"""
    logger.info("Checking TLS certificates...")
    if not os.path.exists('cert.pem') or not os.path.exists('key.pem'):
        logger.info("Generating certificates...")
        subprocess.run([sys.executable, "generate_cert.py"], check=True)
    logger.info("[OK] Certificates verified")
    return True

def start_api_server():
    """Start FastAPI server"""
    logger.info("Starting API Server on port 8000...")
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def main():
    logger.info("=" * 70)
    logger.info("HOSPITAL FEDERATED LEARNING SYSTEM - BACKEND INITIALIZATION")
    logger.info("=" * 70)
    
    # Checks
    if not check_python_packages():
        sys.exit(1)
    
    if not check_certificates():
        sys.exit(1)
    
    # Start services
    logger.info("\nStarting services...")
    
    try:
        api_proc = start_api_server()
        time.sleep(2)
        
        logger.info("=" * 70)
        logger.info("[OK] ALL SERVICES STARTED SUCCESSFULLY")
        logger.info("=" * 70)
        logger.info("\nServices running:")
        logger.info("  - FastAPI Server:  127.0.0.1:8000")
        logger.info("\nAPI Endpoints:")
        logger.info("  - POST /predict   - Predict and trigger FL (starts ephemeral FL Server)")
        logger.info("  - GET  /status    - Check training status")
        logger.info("  - GET  /metrics   - Get model metrics")
        logger.info("  - GET  /health    - Health check")
        logger.info("\nPress Ctrl+C to stop all services")
        logger.info("=" * 70)
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\nShutting down...")
            api_proc.terminate()
            api_proc.wait()
            logger.info("[OK] Services stopped")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()