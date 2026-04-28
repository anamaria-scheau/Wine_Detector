"""
WSGI entry point for PythonAnywhere deployment
"""

import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project path - REPLACE WITH YOUR USERNAME
PROJECT_PATH = '/home/anamariascheau/mysite'
# PROJECT_PATH = '/home/WineDetector/mysite'
if PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)
    logger.info(f"Added {PROJECT_PATH} to Python path")

# Import Flask application
try:
    from app import application
    logger.info("Successfully imported Flask application")
except ImportError as e:
    logger.error(f"Failed to import application: {e}")
    raise

# For debugging
logger.info(f"Python version: {sys.version}")
logger.info(f"Current directory: {os.getcwd()}")
logger.info("WSGI initialization complete")