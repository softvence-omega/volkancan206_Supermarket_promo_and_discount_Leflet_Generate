import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

# Load .env file
load_dotenv()

# Config from env
cloudinary.config( 
  cloud_name = os.getenv("CLOUD_NAME"),
  api_key = os.getenv("API_KEY"),
  api_secret = os.getenv("API_SECRET") 
)

# Upload PDF function
def upload_pdf(file_path: str) -> str:
    """Uploads a PDF to Cloudinary and returns the secure URL."""
    result = cloudinary.uploader.upload(file_path, resource_type="raw")
    return result["secure_url"]

# Upload image function
def upload_image(file_path: str) -> str:
    """Uploads an image to Cloudinary and returns the secure URL."""
    result = cloudinary.uploader.upload(file_path, resource_type="image")
    return result["secure_url"]


# Example usage
if __name__ == "__main__":
    pdf_url = upload_pdf("flyer_campaign.pdf")
    print("Uploaded PDF URL:", pdf_url)

    img_url = upload_image("supermarket_logo.png")
    print("Uploaded Image URL:", img_url)
