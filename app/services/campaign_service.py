
from app.services.save_image import download_image_by_product, download_image_by_logo
from app.services.product_name_image import generate_product_image
from app.config import LOGO_DIR, PRODUCT_DIR, GENERATED_DIR
from app.services.nano import product_card_design
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
            print("product downloaded path------", product_image_path)
        else:
            product_image_path = generate_product_image(product_name)
            print("Generated product image path------", product_image_path)

        # Add image path to product dict
        product['product_path'] = product_image_path
        updated_products.append(product)

    # Update the request with the processed products
    request['products'] = updated_products
    request['logo_path'] = logo_path
    Product_list={
        product['name']:product['product_path']
    }

    # Generate product cards for each product
    for product in updated_products:
        product_card_path = product_card_design(product)
        print("Product card generated path------", product_card_path)



if __name__ == "__main__":
    example_request = {
        "supermarket_name": "Interfood Supermarket",
        "supermarket_logo": "/app/temp/logo/shop_logo.png",
        "products": [
            {
                "name": "Hand towel",
                "description": "Soft and absorbent hand towel",
                "old_price": 3.5,
                "new_price": 2.8,
                "discount": 20,
                "image_url": "/app/temp/product_images/tissue.png",
                "currency": "$"
            }
        ]
    }

    product_card_design(example_request["products"])
    print("Campaign generation completed.")