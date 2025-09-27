import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(override=True)

# Project root (three levels up if this file is in app/services/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Temporary and output directories
BASE_TEMP_DIR = os.path.join(BASE_DIR, "temp")
LOGO_DIR = os.path.join(BASE_TEMP_DIR, "logo")
PRODUCT_DIR = os.path.join(BASE_TEMP_DIR, "product_images")
CARD_DIR = os.path.join(BASE_TEMP_DIR, "cards")
GENERATED_DIR = os.path.join(BASE_TEMP_DIR, "generated_campaigns")

# Create folders if they don't exist
os.makedirs(BASE_TEMP_DIR, exist_ok=True)
os.makedirs(LOGO_DIR, exist_ok=True)
os.makedirs(PRODUCT_DIR, exist_ok=True)
os.makedirs(CARD_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)

# API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


