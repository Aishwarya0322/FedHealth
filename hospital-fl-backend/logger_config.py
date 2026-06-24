"""
Logging Configuration for Federated Learning System
"""
import logging
import logging.handlers
import os
from datetime import datetime

LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, f"fl_system_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

def setup_logging(name, level=logging.INFO):
    """
    Configure logging for FL components.
    Logs to both file and console with UTF-8 encoding.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # File handler (UTF-8 encoding for Windows compatibility)
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(level)
    
    # Console handler (UTF-8 encoding for Windows compatibility)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    # Force UTF-8 on Windows console
    if hasattr(console_handler.stream, 'reconfigure'):
        console_handler.stream.reconfigure(encoding='utf-8')
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger