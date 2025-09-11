import os
import logging
from fastapi import HTTPException
from app.services.save_image import download_image_by_product, download_image_by_logo
from app.services.product_name_image import generate_product_image
from app.config import LOGO_DIR, PRODUCT_DIR, GENERATED_DIR
from app.services.nano import template_Design
from app.schemas.Campaign_Info import CampaignRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def campaign_generate(request: CampaignRequest):
    try:
        # --- Validate and create directories ---
        for dir_path in [LOGO_DIR, PRODUCT_DIR, GENERATED_DIR]:
            if not dir_path:
                raise ValueError(f"Directory path is empty: {dir_path}")
            os.makedirs(dir_path, exist_ok=True)
            if not os.access(dir_path, os.W_OK):
                raise ValueError(f"Directory is not writable: {dir_path}")

        # --- Validate basic request fields ---
        if not request.supermarket_name:
            raise HTTPException(status_code=422, detail="Supermarket name is required")
        if not request.supermarket_logo_url:
            raise HTTPException(status_code=422, detail="Supermarket logo URL is required")
        if not request.products:
            raise HTTPException(status_code=422, detail="At least one product is required")

        for product in request.products:
            if not product.name:
                raise HTTPException(status_code=422, detail="Product name is required for all products")

        supermarket_name = request.supermarket_name
        supermarket_logo_url = request.supermarket_logo_url
        products = request.products

        logger.info(f"Received request for supermarket: {supermarket_name}")

        # --- Download/process supermarket logo ---
        logo_path = download_image_by_logo(supermarket_name, supermarket_logo_url)
        logger.info(f"Supermarket logo saved at: {logo_path}")

        # --- Process each product ---
        updated_products = []
        for product in products:
            product_name = product.name
            product_image_url = product.image_url

            # Always download URL or copy local path
            if product_image_url:
                product_image_path = download_image_by_product(product_name, product_image_url)
                logger.info(f"Product image processed at: {product_image_path}")
            else:
                product_image_path = generate_product_image(product_name)
                logger.info(f"Generated product image at: {product_image_path}")

            if not os.path.exists(product_image_path):
                raise HTTPException(status_code=500, detail=f"Product image path does not exist: {product_image_path}")

            product_dict = product.model_dump()
            product_dict["product_path"] = product_image_path
            updated_products.append(product_dict)

        # --- Prepare dictionary for template design ---
        request_dict = request.model_dump()
        request_dict["products"] = updated_products
        request_dict["logo_path"] = logo_path

        # --- Sanitize output path ---
        safe_output_path = "".join(c for c in supermarket_name if c.isalnum() or c in ("_", "-")).lower()

        logger.info(f"Calling template_Design with {len(updated_products)} products")

        # --- Generate flyer/template ---
        leaflet_path = template_Design(
            Super_market_info=request_dict,
            product_list=updated_products,
            shop_logo=logo_path,
            output_path=safe_output_path
        )

        logger.info(f"Generated leaflet at: {leaflet_path}")
        return leaflet_path

    except Exception as e:
        logger.error(f"Error generating campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating campaign: {str(e)}")


if __name__ == "__main__":
    example_request = {
        "supermarket_name": "FreshMart",
        "Why_this_campaign": "Massive Eid Discounts!",
        "supermarket_address": "123 Main Road",
        "campaign_start_date": "2025-09-10",
        "campaign_end_date": "2025-09-25",
        "supermarket_logo_url": "temp/logo/supermart.png",
        "products": [
            {
                "name": "Apple",
                "secondary_name": "تفاح",
                "old_price": 5.0,
                "new_price": 3.5,
                "discount": 30,
                "image_url": "temp/product_images/organic_apples.png",
                "currency": "$"
            },
            {
                "name": "Rice",
                "secondary_name": "أرز",
                "old_price": 20.0,
                "new_price": 15.0,
                "discount": 25,
                "image_url": "temp/product_images/basmati_rice.png",
                "currency": "$"
            },
        ],
        "products_per_page": 3,
        "template_instruction": "Clean modern layout, green eco theme",
        "theme_style": "organic and minimal",
    }

    result = campaign_generate(example_request)
    # result2= generate_leaflet1(example_request)
    
    print("🎉 Campaign Leaflet Generated:", result)
    # print("🎉 Leaflet1 Generated:", result2)
