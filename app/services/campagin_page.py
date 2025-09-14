import os
import logging
from fastapi import HTTPException
from app.services.save_image import download_image_by_product, download_image_by_logo
from app.services.product_name_image import generate_product_image
from app.config import LOGO_DIR, PRODUCT_DIR, GENERATED_DIR
from app.services.leaflet_generator import generate_flyer_pdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def campaign_generate(request: dict):
    try:
        # --- Validate and create directories ---
        for dir_path in [LOGO_DIR, PRODUCT_DIR, GENERATED_DIR]:
            if not dir_path:
                raise ValueError(f"Directory path is empty: {dir_path}")
            os.makedirs(dir_path, exist_ok=True)
            if not os.access(dir_path, os.W_OK):
                raise ValueError(f"Directory is not writable: {dir_path}")

        # --- Validate basic request fields ---
        if not request.get("supermarket_name"):
            raise HTTPException(status_code=422, detail="Supermarket name is required")
        if not request.get("supermarket_logo_url"):
            raise HTTPException(status_code=422, detail="Supermarket logo URL is required")
        if not request.get("products"):
            raise HTTPException(status_code=422, detail="At least one product is required")

        for product in request["products"]:
            if not product.get("name"):
                raise HTTPException(status_code=422, detail="Product name is required for all products")

        supermarket_name = request["supermarket_name"]
        supermarket_logo_url = request["supermarket_logo_url"]
        products = request["products"]

        logger.info(f"Received request for supermarket: {supermarket_name}")

        # --- Download/process supermarket logo ---
        logo_path = download_image_by_logo(supermarket_name, supermarket_logo_url)
        logger.info(f"Supermarket logo saved at: {logo_path}")

        # --- Process each product ---
        updated_products = []
        for product in products:
            product_name = product["name"]
            product_image_url = product.get("image_url")

            # Download URL or generate image
            if product_image_url:
                product_image_path = download_image_by_product(product_name, product_image_url)
                logger.info(f"Product image processed at: {product_image_path}")
            else:
                product_image_path = generate_product_image(product_name)
                logger.info(f"Generated product image at: {product_image_path}")

            if not os.path.exists(product_image_path):
                raise HTTPException(status_code=500, detail=f"Product image path does not exist: {product_image_path}")

            product_copy = product.copy()
            product_copy["product_path"] = product_image_path
            updated_products.append(product_copy)

        # --- Prepare dictionary for template design ---
        request_dict = request.copy()
        request_dict["products"] = updated_products
        request_dict["logo_path"] = logo_path

        # --- Sanitize output path ---
        # safe_output_path = "".join(c for c in supermarket_name if c.isalnum() or c in ("_", "-")).lower()
        
        output_path= os.path.join(GENERATED_DIR, supermarket_name)
        os.makedirs(output_path, exist_ok=True)

        logger.info(f"Calling template design with {len(updated_products)} products")

        # --- Generate flyer/template ---
        leaflet_path = generate_flyer_pdf(
            request_dict,
            output_pdf=os.path.join(GENERATED_DIR, os.path.join(output_path, f"flyer.pdf"))
        )

        logger.info(f"Generated leaflet at: {leaflet_path}")
        return leaflet_path

    except Exception as e:
        logger.error(f"Error generating campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating campaign: {str(e)}")


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
