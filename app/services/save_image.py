# app/utils/image_downloader.py
import requests
import os
from app.config import PRODUCT_DIR, LOGO_DIR

def download_image_by_product(product_name: str, image_url: str, folder: str = PRODUCT_DIR) -> str:

    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"{product_name.lower().replace(' ', '_')}.png")

    if not os.path.exists(file_path):  # Avoid re-downloading
        url = f"{image_url}"
        response = requests.get(url)
        with open(file_path, "wb") as f:
            f.write(response.content)

    return file_path
def download_image_by_logo(supermarket_name: str, supermarket_logo_url: str, folder: str = LOGO_DIR) -> str:

    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"{supermarket_name.lower().replace(' ', '_')}.png")

    if not os.path.exists(file_path):  # Avoid re-downloading
        url = f"{supermarket_logo_url}"
        response = requests.get(url)
        with open(file_path, "wb") as f:
            f.write(response.content)

    return file_path
