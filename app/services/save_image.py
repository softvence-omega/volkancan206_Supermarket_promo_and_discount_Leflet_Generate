import requests
import os
import uuid
from fastapi import HTTPException
def download_image(url: str, save_dir: str, filename: str) -> str:
    """Download image from URL and save locally with custom filename."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        safe_filename = "".join(c for c in filename if c.isalnum() or c in ("_", "-")).strip()
        file_path = os.path.join(save_dir, f"{safe_filename}_{uuid.uuid4().hex}.jpg")

        with open(file_path, "wb") as f:
            f.write(response.content)

        return file_path
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to download image from {url}: {str(e)}")
