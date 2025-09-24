import os
import logging
from fastapi import HTTPException
from app.services.save_image import download_image_by_product, download_image_by_logo
from app.services.product_name_image import generate_product_image
from app.config import LOGO_DIR, PRODUCT_DIR, GENERATED_DIR
from app.services.leaflet_generator import generate_flyer_pdf
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import httpx
import time
import uuid  

logger = logging.getLogger(__name__)



# prompt = """Create a supermarket flyer for {supermarket_name}.
# - Theme: {theme_style}
# - Grid: 2x2 or 3x2 with products
# - Add supermarket name, logo, campaign tagline, address, and dates
# - Show English names, old price crossed, new price, discount badge
# - Address : {supermarket_address}
# - Campaign Dates: {campaign_start_date} to {campaign_end_date}
# - Template Instruction: {template_instruction}
# - Why this campaign: {why_this_campaign}

# """

# prompt_tail = """Note:
# **Generate a flyer and don't change any information (e.g., logo image,  product images and prices).**
# **No need to calculate prices or discounts, just use the provided data.**
# **Please ensure correct spelling in all words. Do not make any spelling mistakes.**
# """

prompt = """Create a professional supermarket flyer for {supermarket_name}.

CRITICAL REQUIREMENTS:
1. USE THE PROVIDED LOGO IMAGE EXACTLY AS IS - DO NOT modify, recreate, or change the logo in any way
2. For prices: Show OLD PRICE with strikethrough/crossed line, NEW PRICE clearly visible (NOT crossed out)
3. Keep all product names and information exactly as provided
4. Use the provided product images exactly as shown

FLYER DETAILS:
- Supermarket Name: {supermarket_name}
- Theme Style: {theme_style}
- Layout: 2x2 or 3x2 grid with products
- Address: {supermarket_address}
- Campaign Dates: {campaign_start_date} to {campaign_end_date}
- Campaign Purpose: {why_this_campaign}
- Design Instructions: {template_instruction}

PRICE DISPLAY FORMAT:
- Show original price with strikethrough (crossed out)
- Show new price clearly visible and prominent
- Display discount/save amount in a badge or highlight
- Use the exact currency provided for each product

DESIGN ELEMENTS TO INCLUDE:
- Supermarket name prominently displayed
- The exact logo provided (DO NOT recreate or modify)
- Campaign tagline/purpose
- Store address
- Campaign validity dates
- Professional layout matching the theme style
"""

prompt_tail = """
IMPORTANT RULES:
1. **USE THE PROVIDED LOGO IMAGE EXACTLY - DO NOT create a new logo or modify the existing one**
2. **PRICE DISPLAY: Only cross out the OLD price, keep the NEW price clear and readable**
3. **Keep all product information exactly as provided - no changes to names, prices, or discounts**
4. **Use provided product images without modification**
5. **Maintain professional spelling and formatting**
6. **Follow the specified theme and layout style**

"""


def call_gemini_api(prompt, images):
    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-2.5-flash-image-preview",
        contents=[prompt, images],
    )

    i = 0
    img_urls = []
    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            file_name = uuid.uuid4().hex
            image = Image.open(BytesIO(part.inline_data.data))
            image.save(f"outputs/{file_name}.png")
            i += 1
            img_urls.append(f"outputs/{file_name}.png")

    return img_urls[0] if img_urls else None


def generate_flyer(prompt, products, reference_image_path=None):
    if len(products) > 0:
        logger.info(f"Generating flyer with {len(products)} products")
        prompt += "Here is the product list:\n"

    images = []
    for i, product in enumerate(products):
        # Format currency properly
        currency = product.get('currency', 'USD').strip()
        old_price = product['old_price']
        new_price = product['new_price']
        discount = product.get('discount', 0)
        
        # Calculate discount if not provided
        if discount == 0 and old_price > new_price:
            discount = round(((old_price - new_price) / old_price) * 100)
        
        single_product_info = f"""
            Product {i+1}:
            - Name: {product['name']}
            - Original Price: {currency} {old_price} (CROSS THIS OUT)
            - Sale Price: {currency} {new_price} (SHOW CLEARLY - DO NOT CROSS OUT)
            - Discount: {discount} % OFF or SAVE {currency} {old_price - new_price}
            - Currency: {currency}
            """
        prompt += single_product_info

        image_url = product.get("image_url")
        if image_url:
            time.sleep(1)  # To avoid rapid requests
            logger.info(f"Downloading image for product: {product['name']} from {image_url}")
            response = httpx.get(image_url)
            response.raise_for_status()
            
            image = Image.open(BytesIO(response.content))
            image.load()
            images.append(image)
            logger.info(f"Downloaded image for product: {product['name']}")

    prompt += prompt_tail
    if reference_image_path and os.path.exists(reference_image_path):
        logger.info(f"Using reference image for style: {reference_image_path}")
        prompt += "\n\nSTYLE REFERENCE: Use the last image as a style reference. Generate a new flyer with the same design layout and styling, but with the new product information and images provided above."

        with open(reference_image_path, "rb") as ref_img_file:
            ref_image = Image.open(ref_img_file)
            ref_image.load()
            images.append(ref_image)
    

    flyer_path = call_gemini_api(prompt, images)
    logger.info(f"Flyer generated at: {flyer_path}")

    return flyer_path

def campaign_generate(request: dict):
    supermarket_name = request["supermarket_name"]
    why_this_campaign = request["why_this_campaign"]
    supermarket_address = request["supermarket_address"]
    campaign_start_date = request["campaign_start_date"]
    campaign_end_date = request["campaign_end_date"]
    supermarket_logo_url = request["supermarket_logo_url"]
    products = request["products"]
    products_per_page = request["products_per_page"]
    template_instruction = request["template_instruction"]
    theme_style = request["theme_style"]


    print("Supermarket Name:", supermarket_name)
    print("Why this Campaign:", why_this_campaign)
    print("Supermarket Address:", supermarket_address)
    print("Campaign Start Date:", campaign_start_date)
    print("Campaign End Date:", campaign_end_date)
    print("Supermarket Logo URL:", supermarket_logo_url)
    print("Products:", products)
    print("Products per Page:", products_per_page)
    print("Template Instruction:", template_instruction)
    print("Theme Style:", theme_style)

    prompt_filled = prompt.format(
        supermarket_name=supermarket_name,
        why_this_campaign=why_this_campaign,
        supermarket_address=supermarket_address,
        campaign_start_date=campaign_start_date,
        campaign_end_date=campaign_end_date,
        template_instruction=template_instruction,
        theme_style=theme_style
    )
    
    reference_image_path = None
    ret = []
    if len(products) > 4:
        for i in range(0, len(products), products_per_page):
            batch = products[i:i + products_per_page]
            logger.info(f"Generating flyer for products {i + 1} to {i + len(batch)}")
            flyer_url = generate_flyer(prompt_filled, batch, reference_image_path)
            ret.append(flyer_url)
            reference_image_path = flyer_url
            print("Generated flyer URL:", flyer_url)

            time.sleep(5)

    

    return ret
    # try:
    #     # --- Validate and create directories ---
    #     for dir_path in [LOGO_DIR, PRODUCT_DIR, GENERATED_DIR]:
    #         if not dir_path:
    #             raise ValueError(f"Directory path is empty: {dir_path}")
    #         os.makedirs(dir_path, exist_ok=True)
    #         if not os.access(dir_path, os.W_OK):
    #             raise ValueError(f"Directory is not writable: {dir_path}")

    #     # --- Validate basic request fields ---
    #     if not request.get("supermarket_name"):
    #         raise HTTPException(status_code=422, detail="Supermarket name is required")
    #     if not request.get("supermarket_logo_url"):
    #         raise HTTPException(status_code=422, detail="Supermarket logo URL is required")
    #     if not request.get("products"):
    #         raise HTTPException(status_code=422, detail="At least one product is required")

    #     for product in request["products"]:
    #         if not product.get("name"):
    #             raise HTTPException(status_code=422, detail="Product name is required for all products")

    #     supermarket_name = request["supermarket_name"]
    #     supermarket_logo_url = request["supermarket_logo_url"]
    #     products = request["products"]

    #     logger.info(f"Received request for supermarket: {supermarket_name}")

    #     # --- Download/process supermarket logo ---
    #     logo_path = download_image_by_logo(supermarket_name, supermarket_logo_url)
    #     logger.info(f"Supermarket logo saved at: {logo_path}")

    #     # --- Process each product ---
    #     updated_products = []
    #     for product in products:
    #         product_name = product["name"]
    #         product_image_url = product.get("image_url")

    #         # Download URL or generate image
    #         if product_image_url:
    #             product_image_path = download_image_by_product(product_name, product_image_url)
    #             logger.info(f"Product image processed at: {product_image_path}")
    #         else:
    #             product_image_path = generate_product_image(product_name)
    #             logger.info(f"Generated product image at: {product_image_path}")

    #         if not os.path.exists(product_image_path):
    #             raise HTTPException(status_code=500, detail=f"Product image path does not exist: {product_image_path}")

    #         product_copy = product.copy()
    #         product_copy["product_path"] = product_image_path
    #         updated_products.append(product_copy)

    #     # --- Prepare dictionary for template design ---
    #     request_dict = request.copy()
    #     request_dict["products"] = updated_products
    #     request_dict["logo_path"] = logo_path

    #     # --- Sanitize output path ---
    #     # safe_output_path = "".join(c for c in supermarket_name if c.isalnum() or c in ("_", "-")).lower()
        
    #     output_path= os.path.join(GENERATED_DIR, supermarket_name)
    #     os.makedirs(output_path, exist_ok=True)

    #     logger.info(f"Calling template design with {len(updated_products)} products")

    #     # --- Generate flyer/template ---
    #     leaflet_path = generate_flyer_pdf(
    #         request_dict,
    #         output_pdf=os.path.join(GENERATED_DIR, os.path.join(output_path, f"flyer.pdf"))
    #     )

    #     logger.info(f"Generated leaflet at: {leaflet_path}")
        
    #     #-----clean up log ----
    #     os.remove(logo_path)
        
    #     # --- Clean up product images ---
    #     for product in updated_products:
    #         product_path = product.get("product_path")
    #         if product_path and os.path.exists(product_path):
    #             try:
    #                 os.remove(product_path)
    #                 logger.info(f"Deleted product image: {product_path}")
    #             except Exception as e:
    #                 logger.warning(f"Failed to delete product image {product_path}: {e}")
        
    #     return leaflet_path

    # except Exception as e:
    #     logger.error(f"Error generating campaign: {str(e)}")
    #     raise HTTPException(status_code=500, detail=f"Error generating campaign: {str(e)}")


if __name__ == "__main__":
    example_request = {
        "supermarket_name": "Interfood",
        "Why_this_campaign": "Massive Eid Discounts!",
        "supermarket_address": "CAN Nürnberg, Ingolstädter Str. 53, 90461 Nürnberg, Telefon 09 11/99 44 83 70, Mo. - Sa. 08.00 - 20.00 Uhr",
        "campaign_start_date": "2025-09-10",
        "campaign_end_date": "2025-09-25",
        "supermarket_logo_url": "temp/logo/supermart.png",
        "products": [
            {
                "name": "cocacola",
                "secondary_name": "تفاح",
                "old_price": 5.0,
                "new_price": 3.5,
                "discount": 30,
                "image_url": "https://drive.google.com/file/d/1h_V076e89aEkT-qN-GzMKnoq_jR7ymPR/view?usp=drive_link",
                "currency": "$"
            },
            {
                "name": "mango",
                "secondary_name": "أرز",
                "old_price": 20.0,
                "new_price": 15.0,
                "discount": 25,
                "image_url": "https://drive.google.com/file/d/1jxkmc6RXSpbO3TYup0tiH7QK5qe8XuZC/view?usp=drive_link",
                "currency": "$"
            },
            {
                "name": "souce",
                "secondary_name": "لحم",
                "old_price": 200,
                "new_price": 150,
                "discount": 25,
                "image_url": "https://drive.google.com/file/d/1hyc90sjFnZ7As7QfdeZgtdNEp91VhwtU/view?usp=drive_link",
                "currency": "Tk"
            }
        ],
        "products_per_page": 2,
        "template_instruction": "Clean modern layout, green eco theme",
        "theme_style": "organic and minimal",
    }

    result = campaign_generate(example_request)
    print("Flyer generated at:", result)
