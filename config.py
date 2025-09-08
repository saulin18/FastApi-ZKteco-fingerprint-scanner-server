# Configuration file for FastAPI Fingerprint API
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Server configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fingerprints.db")
DATABASE_PATH = os.getenv("DATABASE_PATH", "fingerprints.db")

# Device configuration
DEVICE_INDEX = int(os.getenv("DEVICE_INDEX", 0))  # Index of the fingerprint device to use
DEVICE_TIMEOUT = int(os.getenv("DEVICE_TIMEOUT", 30))  # Timeout for fingerprint capture in seconds

# Image configuration
IMAGE_FORMAT = os.getenv("IMAGE_FORMAT", "PNG")
IMAGE_QUALITY = int(os.getenv("IMAGE_QUALITY", 95))

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs.log")

# API configuration
API_TITLE = os.getenv("API_TITLE", "Fingerprint API")
API_DESCRIPTION = os.getenv("API_DESCRIPTION", "API for fingerprint capture and management using ZKTeco devices")
API_VERSION = os.getenv("API_VERSION", "1.0.0")
