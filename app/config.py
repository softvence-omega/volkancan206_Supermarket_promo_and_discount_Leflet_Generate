import os
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "images")

BASE_TEMP_DIR = os.path.join(BASE_DIR, "temp")
LOGO_DIR = os.path.join(BASE_TEMP_DIR, "logo")
PRODUCT_DIR = os.path.join(BASE_TEMP_DIR, "product_images")
GENERATED_DIR = os.path.join(BASE_TEMP_DIR, "generated_campaigns")

# Create folders if they don't exist
os.makedirs(BASE_TEMP_DIR, exist_ok=True)
os.makedirs(LOGO_DIR, exist_ok=True)
os.makedirs(PRODUCT_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

HF_TOKEN = os.getenv("HF_TOKEN")