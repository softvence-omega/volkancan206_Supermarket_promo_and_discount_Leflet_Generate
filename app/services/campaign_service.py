
from app.services.save_image import download_image_by_product, download_image_by_logo
from app.services.tamplate_prompt_design import generate_prompt_design
from app.services.product_name_image import generate_product_image
from app.services.nano import _template_generate

def campaign_generate(request: dict):
    supermarket_name = request.get("supermarket_name")
    supermarket_logo_url = request.get("supermarket_logo")

    products = request.get("products", [])

    # Download the supermarket logo
    logo_path = download_image_by_logo(supermarket_name, supermarket_logo_url)

    # Process each product
    updated_products = []
    for product in products:
        product_name = product.get("name")
        product_image_url = product.get("image")

        if product_image_url:
            product_image_path = download_image_by_product(product_name, product_image_url)
        else:
            product_image_path = generate_product_image(product_name)

        # Add image path to product dict
        product['product_path'] = product_image_path
        updated_products.append(product)

    # Update the request with the processed products
    request['products'] = updated_products
    request['logo_path'] = logo_path

    # Generate the flyer design prompt using updated products
    flyer_prompt = generate_prompt_design(request)
    leaflet_path = _template_generate(flyer_prompt, request['products'])

    return {
        "leaflet_path": leaflet_path
    }

