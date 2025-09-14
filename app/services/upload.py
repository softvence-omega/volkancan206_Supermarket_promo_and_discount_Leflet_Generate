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

# Upload image function
def upload_image(file_path: str) -> str:
    """Uploads an image to Cloudinary and returns the secure URL."""
    result = cloudinary.uploader.upload(file_path, resource_type="image")
    return result["secure_url"]
    
    # Upload PDF (or any file)
def upload_pdf(file_path: str) -> str:
    result = cloudinary.uploader.upload(file_path, resource_type="raw",access_mode="public")  # important: raw
    # Generate download link
    download_url = cloudinary.utils.cloudinary_url(
        result['public_id'],
        resource_type="raw",
        attachment=True,   # forces download
        sign_url=True,     # creates temporary signed URL
        expires_at=None    # optional: can set specific expiration timestamp
    )[0]
    return result["secure_url"],download_url

# Example usage
if __name__ == "__main__":
    # Assuming the function upload_pdf_to_drive is already defined as before

    # Your PDF file
    pdf_file = "flyer_campaign.pdf"

    # Upload it to Google Drive
    pdf_url = upload_pdf("Flyer_Campaign.pdf")  # "Flyer_Campaign.pdf" will be the name on Drive
    print("---------------------",pdf_url)

    # Print the shareable link


    img_url = upload_image("beef.png")
    print("Uploaded Image URL:", img_url)
