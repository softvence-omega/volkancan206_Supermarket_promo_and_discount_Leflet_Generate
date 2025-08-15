import os
from dotenv import load_dotenv

load_dotenv()

BASE_TEMP_DIR = os.path.join(os.getcwd(), "temp")
LOGO_UPLOAD_DIR = os.path.join(BASE_TEMP_DIR, "logo")
PRODUCT_IMAGE_UPLOAD_DIR = os.path.join(BASE_TEMP_DIR, "product_images")

# Create folders if they don't exist
os.makedirs(BASE_TEMP_DIR, exist_ok=True)
os.makedirs(LOGO_UPLOAD_DIR, exist_ok=True)
os.makedirs(PRODUCT_IMAGE_UPLOAD_DIR, exist_ok=True)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")