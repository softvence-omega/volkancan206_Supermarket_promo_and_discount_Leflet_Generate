from fastapi import APIRouter, HTTPException
import math
import os
from PIL import Image
import logging
import uuid

from app.schemas.Campaign_Info import FlyerRequest, FlyerResponse
from app.services.flyer_service import generate_flyer, download_image, format_products_info
from app.services.upload import upload_image


logger = logging.getLogger(__name__)

FIRST_PROMPT_TEMPLATE = """
Create a professional supermarket flyer for {supermarket_name}.
- Theme: {theme_style}
- Campaign: {why_this_campaign}
- Grid Layout: {grid_layout} layout with {product_count} products
- Address: {supermarket_address}
- Phone number: {phone_number}
- Email: {email}
- Campaign Period: {campaign_start_date} to {campaign_end_date}

CRITICAL: USE ONLY THE EXACT PRICES PROVIDED BELOW - DO NOT MODIFY ANY NUMBERS:

{products_info}

ABSOLUTE REQUIREMENTS FOR PRICE ACCURACY:
1. NEVER change, round, or modify the provided price numbers
2. NEVER create your own price calculations
3. NEVER use different prices than what's specified above
4. ALWAYS double-check that displayed prices match the provided data exactly
5. Each product MUST show the exact old price and new price as listed

DESIGN REQUIREMENTS:
1. PRODUCT CARD BACKGROUNDS:
   - NO solid white backgrounds for product cards
   - Use semi-transparent themed backgrounds that match the overall flyer design
   - Product cards should have subtle gradient backgrounds or textured backgrounds
   - Cards should blend harmoniously with the main flyer background

2. LOGO INTEGRATION REQUIREMENTS:
   - DO NOT place the logo on a solid white background or any solid colored background
   - Integrate the logo naturally into the themed flyer background
   - Logo should appear to "float" on the main flyer background with transparency
   - Use subtle shadow or glow effects around the logo if needed for visibility
   - Logo background should match and blend with the overall flyer theme
   - Ensure logo remains readable while maintaining theme integration

3. PRICE DISPLAY FORMAT:
   - Product Name (with secondary description)
   - OLD PRICE: [exact amount] [currency] (with strikethrough line)
   - NEW PRICE: [exact amount] [currency] (bold, larger font)
   - Discount badge: [X]% OFF (red circular badge)

4. VISUAL INTEGRATION:
   - Professional appearance with themed, integrated backgrounds
   - No stark white product cards
   - Maintain readability with proper contrast

5. IMPORTANT: 
   - DO NOT MODIFY ANY OF THE ABOVE NUMBERS OR PRICES IN ANY WAY. USE THEM EXACTLY AS PROVIDED.
   - DO NOT DUPLICATE THE SAME PRODUCT TWICE ON THE SAME FLYER.

WARNING: Any deviation from the provided price numbers will result in incorrect flyer information. Use ONLY the exact prices specified above.
"""

SECOND_PROMPT_TEMPLATE = """
Create a professional supermarket flyer for {supermarket_name}.
- Theme: {theme_style}
- Campaign: {why_this_campaign}
- Grid Layout: {grid_layout} layout with {product_count} products
- Address: {supermarket_address}
- Phone number: {phone_number}
- Email: {email}
- Campaign Period: {campaign_start_date} to {campaign_end_date}

EXACT PRODUCT PRICING TO DISPLAY:
{products_info}

MANDATORY DESIGN & FORMATTING RULES:

1. PRODUCT CARD BACKGROUNDS (CRITICAL):
   - ABSOLUTELY NO solid white backgrounds for product cards
   - Use the same design approach as the reference flyer
   - Product cards must have themed, integrated backgrounds
   - Examples: translucent overlays, themed textures, gradient backgrounds
   - Backgrounds should complement and match the overall flyer theme
   - Maintain visual continuity with the reference design style

2. PRICE FORMATTING:
   - Product Name (with secondary description)
   - OLD PRICE: [amount] [currency] (with strikethrough line)
   - NEW PRICE: [amount] [currency] (bold, larger font)
   - Discount badge: [X]% OFF (red circular badge)

3. REFERENCE DESIGN INTEGRATION:
   - Follow the reference flyer's background treatment for product areas
   - Maintain the same visual aesthetic and color harmony
   - Use similar background textures and transparency effects
   - Keep consistent typography and design elements from reference
   - Preserve the professional, integrated look of the reference

4. VISUAL COHESION:
   - Seamless integration between main background and product areas
   - Themed borders and decorative elements matching the reference
   - Sophisticated color blending throughout the design
   - Professional appearance with proper visual flow

5. IMPORTANT: 
   - DO NOT MODIFY ANY OF THE ABOVE NUMBERS OR PRICES IN ANY WAY. USE THEM EXACTLY AS PROVIDED.
   - FOLLOW THE REFERENCE DESIGN STYLE CLOSELY FOR BACKGROUNDS AND INTEGRATION ASPECTS.
   - DO NOT DUPLICATE THE SAME PRODUCT TWICE ON THE SAME FLYER.

Generate a flyer matching the reference design style with integrated themed backgrounds - NO white product card backgrounds.
"""


router = APIRouter(
    prefix="/flyer",
    tags=["Flyer"]
)

OUTPUTS_DIR = "outputs"

def get_optimal_grid_layout(product_count: int) -> str:
    """Determine optimal grid layout based on product count"""
    if product_count == 1:
        return "1x1 (single large product)"
    elif product_count == 2:
        return "1x2 or 2x1 (two products side by side )"
    elif product_count == 3:
        return "1x3 or 3x1 (three products in a row )"
    elif product_count == 4:
        return "2x2 (four products in a square grid)"
    elif product_count == 5:
        return "flexible 2x3 or 3x2 with one larger product"
    elif product_count == 6:
        return "2x3 or 3x2 (six products in rectangular grid)"
    elif product_count <= 8:
        return "2x4 or 4x2 (eight products maximum)"
    else:
        return "3x3 or flexible grid (arrange efficiently)"
    
@router.post("/generate-flyers", response_model=FlyerResponse)
async def generate_flyers(request: FlyerRequest):
    """Generate flyers based on products with 4 products per flyer"""
    
    try:
        # Download logo image
        logo_image = download_image(request.supermarket_logo_url)
        
        # Calculate number of flyers needed
        total_products = len(request.products)
        num_flyers = math.ceil(total_products / request.products_per_page)
        
        generated_flyers = []
        reference_flyer = None
        
        for flyer_index in range(num_flyers):
            # Get products for this flyer
            start_idx = flyer_index * request.products_per_page
            end_idx = min(start_idx + request.products_per_page, total_products)
            current_products = request.products[start_idx:end_idx]
            grid_layout = get_optimal_grid_layout(len(current_products))

            # Download product images
            product_images = []
            for product in current_products:
                img = download_image(product.image_url)
                product_images.append(img)
            
            # Format products info for prompt
            products_info = format_products_info(current_products)
            
            # Choose prompt based on flyer index
            if flyer_index == 0:
                # First flyer - use first prompt with logo
                prompt = FIRST_PROMPT_TEMPLATE.format(
                    supermarket_name=request.supermarket_name,
                    theme_style=request.theme_style,
                    why_this_campaign=request.why_this_campaign,
                    supermarket_address=request.supermarket_address,
                    phone_number=request.phone_number,
                    email=request.email,
                    campaign_start_date=request.campaign_start_date,
                    campaign_end_date=request.campaign_end_date,
                    products_info=products_info,
                    grid_layout=grid_layout,
                    product_count=len(current_products)
                )
                
                flyer_images = generate_flyer(prompt, product_images, logo_image)
                
                # Save the first generated flyer as reference for subsequent flyers
                if flyer_images:
                    # Load the first saved image as reference
                    first_image_path = flyer_images[0].replace("http://localhost:8000/outputs/", "")
                    reference_flyer = Image.open(os.path.join(OUTPUTS_DIR, first_image_path))
                
            else:
                # Subsequent flyers - use second prompt with reference, no logo
                prompt = SECOND_PROMPT_TEMPLATE.format(
                    supermarket_name=request.supermarket_name,
                    theme_style=request.theme_style,
                    why_this_campaign=request.why_this_campaign,
                    supermarket_address=request.supermarket_address,
                    phone_number=request.phone_number,
                    email=request.email,
                    campaign_start_date=request.campaign_start_date,
                    campaign_end_date=request.campaign_end_date,
                    products_info=products_info,
                    grid_layout=grid_layout,
                    product_count=len(current_products)
                )
                
                flyer_images = generate_flyer(prompt, product_images, None, reference_flyer)
            
            generated_flyers.extend(flyer_images)
        
        ret_urls = []
        local_img_paths = []
        for img_url in generated_flyers:
            img_path = img_url.replace("http://localhost:8000/outputs/", "")
            logger.info(f"Processing image path: {img_path}")
            img_path = os.path.join(OUTPUTS_DIR, img_path)
            local_img_paths.append(img_path)
            logger.info(f"Final image path: {img_path}")

            img_url = upload_image(img_path)
            ret_urls.append(img_url)
            logger.info(f"Uploaded image URL: {img_url}")

        output_pdf = f"{OUTPUTS_DIR}/{uuid.uuid4().hex}_flyer.pdf"
        pdf_url = generate_pdf(local_img_paths, output_pdf)
        try:
            if os.path.exists(output_pdf):
                os.remove(output_pdf)
                logger.info(f"Deleted local PDF: {output_pdf}")
            
            for img_path in local_img_paths:
                if os.path.exists(img_path):
                    os.remove(img_path)
                    logger.info(f"Deleted local image: {img_path}")
        except Exception as e:
            logger.error(f"Error deleting local files: {str(e)}")



        return FlyerResponse(
            success=True,
            message=f"Successfully generated {len(generated_flyers)} flyer(s)",
            flyers_generated=len(generated_flyers),
            pdf_url=pdf_url,
            img_urls=ret_urls

        )
        
    except Exception as e:
        logger.error(f"Error in /generate-flyers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

from typing import List
from app.services.upload import upload_pdf

def generate_pdf(flyer_images: List[str], output_pdf: str = "outputs/final_flyer.pdf"):
    # Merge all pages into a single PDF
    try:
        if flyer_images:
            pil_imgs = []
            for f in flyer_images:
                with Image.open(f) as img:
                    if img.mode in ("P", "RGBA"):
                        img = img.convert("RGB")
                    pil_imgs.append(img.copy())

            pil_imgs[0].save(output_pdf, save_all=True, append_images=pil_imgs[1:])
            print(f"Final flyer PDF saved: {output_pdf}")
        else:
            print("No flyer images generated.")

        # Upload PDF to Cloudinary
        uploaded_pdf = upload_pdf(output_pdf)

        return uploaded_pdf
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating PDF")