"""
Logger configuration module.It sets up logging to a file with timestamps.
"""

import logging
import os
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True) # exists_ok=True to avoid error if dir exists

# Create a log file with the current timestamp
LOG_FILE = os.path.join(LOG_DIR, f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")

# Configure logging
## filename is set to LOG_FILE
## format includes timestamp, log level, and message
logging.basicConfig(
    filename=LOG_FILE,
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def get_logger(name):
    """Function to get the configured logger. It returns a logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger