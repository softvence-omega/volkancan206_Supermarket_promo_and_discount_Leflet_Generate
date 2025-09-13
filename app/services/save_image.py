import os
import base64
import requests
from fastapi import HTTPException
from app.config import LOGO_DIR, PRODUCT_DIR

os.makedirs(LOGO_DIR, exist_ok=True)
os.makedirs(PRODUCT_DIR, exist_ok=True)


def _save_base64_image(base64_str: str, file_path: str):
    try:
        mime_type, data = base64_str.split(",", 1)
        image_data = base64.b64decode(data)
        with open(file_path, "wb") as f:
            f.write(image_data)
        return file_path
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to decode Base64 image: {str(e)}")


def _save_from_url(url: str, file_path: str):
    try:
        # Handle Google Drive share links
        if "drive.google.com" in url:
            # Convert to direct download link
            if "uc?id=" not in url:
                file_id = url.split("/d/")[1].split("/")[0]
                url = f"https://drive.google.com/uc?id={file_id}&export=download"

        # TODO: Add similar logic for OneDrive if needed

        response = requests.get(url, timeout=15, stream=True)
        response.raise_for_status()
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return file_path
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to download image: {str(e)}")


def _save_from_local(local_path: str, file_path: str):
    if not os.path.exists(local_path):
        raise HTTPException(status_code=422, detail=f"Local file does not exist: {local_path}")
    try:
        with open(local_path, "rb") as src, open(file_path, "wb") as dst:
            dst.write(src.read())
        return file_path
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to copy local file: {str(e)}")


def _download_image(name: str, url: str, folder: str) -> str:
    if not name:
        raise HTTPException(status_code=422, detail="Name cannot be empty")
    if not url:
        raise HTTPException(status_code=422, detail="Image URL is required")

    safe_name = name.lower().replace(" ", "_")
    file_path = os.path.join(folder, f"{safe_name}.png")

    if os.path.exists(file_path):
        return file_path

    if url.startswith("data:image/"):
        return _save_base64_image(url, file_path)
    elif url.startswith("http://") or url.startswith("https://"):
        return _save_from_url(url, file_path)
    else:  # treat as local path
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        local_path = os.path.join(project_root, url.lstrip("./").lstrip("/"))
        return _save_from_local(local_path, file_path)

# Public APIs
def download_image_by_logo(supermarket_name: str, supermarket_logo_url: str) -> str:
    return _download_image(supermarket_name, supermarket_logo_url, LOGO_DIR)


def download_image_by_product(product_name: str, product_url: str) -> str:
    return _download_image(product_name, product_url, PRODUCT_DIR)

