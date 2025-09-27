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

# Upload image function
def upload_image(file_path: str) -> str:
    """Uploads an image to Cloudinary and returns the secure URL."""
    result = cloudinary.uploader.upload(
        file_path,
        resource_type="image",      # image files
        type="upload"               # public by default
    )
    return result["secure_url"]

# Upload PDF (or any raw file)
def upload_pdf(file_path: str) -> str:
    """Uploads a PDF (or any raw file) to Cloudinary and returns a permanent public secure URL."""
    result = cloudinary.uploader.upload(
        file_path,
        resource_type="raw",        # for pdf/docx/zip etc.
        type="upload"               # public delivery (no expiry)
    )
    return result["secure_url"]

# Example usage
if __name__ == "__main__":
    pdf_url = upload_pdf("Flyer_Campaign.pdf")
    print("Permanent PDF URL:", pdf_url)

    img_url = upload_image("beef.png")
    print("Uploaded Image URL:", img_url)
