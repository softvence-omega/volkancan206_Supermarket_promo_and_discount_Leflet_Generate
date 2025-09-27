from fastapi import  HTTPException
from typing import List, Optional
from google import genai
from PIL import Image
from io import BytesIO
import requests
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime
import logging

from app.schemas.Campaign_Info import  Product

load_dotenv()

OUTPUTS_DIR = "outputs"
if not os.path.exists(OUTPUTS_DIR):
    os.makedirs(OUTPUTS_DIR)


# Initialize Gemini client
client = genai.Client()
logger = logging.getLogger(__name__)

def download_image(url: str) -> Image.Image:
    """Download image from URL and return PIL Image object"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        response = requests.get(str(url), timeout=30, headers=headers, allow_redirects=True)
        if response.status_code != 200:
            logger.error(f"Failed to download image from {url}: {response.status_code}")

        response.raise_for_status()
        
        # Try to open the image directly - PIL will validate if it's a real image
        try:
            image = Image.open(BytesIO(response.content))
            # Verify it's actually an image by trying to access basic properties
            _ = image.size
            _ = image.mode
            return image
        except Exception as img_error:
            # If PIL can't open it, it's not a valid image
            content_type = response.headers.get('content-type', 'unknown')
            raise ValueError(f"Downloaded content is not a valid image. Content-Type: {content_type}, Size: {len(response.content)} bytes")
            
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to download image from {url}: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid image from {url}: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process image from {url}: {str(e)}")

def format_products_info(products: List[Product]) -> str:
    """Format products information for the prompt"""
    products_info = []
    for product in products:
        discount_percent = ((product.old_price - product.new_price) / product.old_price) * 100
        products_info.append(
            f"- {product.name} - old price: {product.old_price} {product.currency}, "
            f"new price: {product.new_price} {product.currency}, "
            f"discount: {discount_percent:.0f}%"
        )
    return "\n".join(products_info)

def generate_flyer(prompt: str, product_images: List[Image.Image], logo_image: Optional[Image.Image] = None, reference_image: Optional[Image.Image] = None) -> List[str]:
    """Generate flyer using Gemini API and save to local files"""
    try:
        # Prepare content list
        content = [prompt]
        content.extend(product_images)
        
        if logo_image:
            content.append(logo_image)
            
        if reference_image:
            content.append(reference_image)

        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=content,
        )

        generated_image_urls = []
        for i, part in enumerate(response.candidates[0].content.parts):
            if part.inline_data is not None:
                # Generate unique filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_id = str(uuid.uuid4())[:8]
                filename = f"flyer_{timestamp}_{unique_id}_{i}.png"
                filepath = os.path.join(OUTPUTS_DIR, filename)
                
                # Save image to local file
                image = Image.open(BytesIO(part.inline_data.data))
                image.save(filepath, "PNG")
                
                # Create localhost URL
                image_url = f"http://localhost:8000/outputs/{filename}"
                generated_image_urls.append(image_url)
                
        return generated_image_urls
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate flyer: {str(e)}")
