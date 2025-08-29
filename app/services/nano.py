
from huggingface_hub import InferenceClient
from PIL import Image
import os
from app.config import HF_TOKEN,CARD_DIR,GENERATED_DIR
from app.schemas.Campaign_Info import CampaignRequest
from io import BytesIO


client1 = InferenceClient(
    model="Qwen/Qwen-Image-Edit",
    token=HF_TOKEN
)
def product_card_design(product_info: dict):
    print("Designing product card for:", product_info.get('name'))
    print("Using image:", product_info.get('image_url'))
    image_path = product_info.get('image_url')
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    prompt = f"""
    1. Take this product image
    2. Add white space below the image  
    3. Write "{product_info['name']}" in bold 
    4. Write "{product_info['secondary_name']}" in italic
    4. Write "Old Price: {product_info['currency']}{product_info['old_price']}" with strikethrough
    5. Write "New Price: {product_info['currency']}{product_info['new_price']}" in green
    6. Add red "{product_info['discount']}% OFF" badge.
    Professional product card design A6 card.
    """

    result = client1.image_to_image(
        image=image_bytes,
        prompt=prompt
    )
    output_path = f"{CARD_DIR}/{product_info['name'].replace(' ', '_')}_card.png"
    result.save(output_path)

    return output_path



def template_Design(Super_market_info: dict, product_list: list, shop_logo: str, output_path: str):
    # --- Open shop logo ---
    logo = Image.open(shop_logo).convert("RGBA")

    # --- Open and collect product cards ---
    product_cards = []
    for product in product_list:
        card_path = product_card_design(product)  # generates card and returns path
        product_cards.append(Image.open(card_path).convert("RGBA"))

    # --- Calculate canvas size ---
    max_width = max([logo.width] + [c.width for c in product_cards])
    total_height = logo.height + sum(c.height for c in product_cards)
    padding = 30
    total_height += padding * (len(product_cards) + 1)

    # --- Create merged canvas ---
    canvas = Image.new("RGBA", (max_width, total_height), (255, 255, 255, 255))

    # --- Paste logo centered ---
    y_offset = padding
    x_logo = (max_width - logo.width) // 2
    canvas.paste(logo, (x_logo, y_offset), logo)
    y_offset += logo.height + padding

    # --- Paste product cards stacked ---
    for card in product_cards:
        x_card = (max_width - card.width) // 2
        canvas.paste(card, (x_card, y_offset), card)
        y_offset += card.height + padding

    # --- Save merged image bytes ---
    buf = BytesIO()
    canvas.save(buf, format="PNG")
    merged_bytes = buf.getvalue()

    # --- Build Qwen prompt ---
    prompt = f"""
    Enhance this supermarket flyer.
    - Keep logo on top.
    - Product cards stacked below.
    - Add supermarket name: {Super_market_info['supermarket_name']}
    - Tagline: {Super_market_info['Why_this_campaign']}
    - Campaign dates: {Super_market_info['campaign_start_date']} to {Super_market_info['campaign_end_date']}
    - Address: {Super_market_info['supermarket_address']} at footer.
    - Style: clean, modern, visually appealing, balanced layout.
    """

    # --- Send merged image to Qwen ---
    result = client1.image_to_image(
        image=merged_bytes,
        prompt=prompt
    )

    # --- Save final flyer ---
    os.makedirs(f"{GENERATED_DIR}/{output_path}", exist_ok=True)
    final_path = f"{GENERATED_DIR}/{output_path}/flyer_design.png"
    result.save(final_path)
    print("✅ Flyer saved at:", final_path)
    return final_path

    


if __name__ == "__main__":
    # Example product info
    example_product = {
        "name": "Potato",
        "secondary_name": "بطاطس طازجة",
        "old_price": 3.5,
        "new_price": 2.8,
        "discount": 20,
        "image_url": "./app/temp/product_images/potato.png",
        "currency": "$"
    }

    # Generate product card
    img = product_card_design(example_product)
    print("Product card image generated in -----", img)

    # Campaign request
    example_request = CampaignRequest(
        supermarket_name="SuperMart",
        Why_this_campaign="Best prices for fresh produce!",
        supermarket_address="123 Main St",
        campaign_start_date="2024-06-01",
        campaign_end_date="2024-06-15",
        supermarket_logo_url="./app/temp/logo/shop_logo.png",
        products=[
            {
                "name": "Potato",
                "secondary_name": "بطاطس طازجة",
                "old_price": 3.5,
                "new_price": 2.8,
                "discount": 20,
                "image_url": "./app/temp/product_images/potato.png",
                "currency": "$"
            },
            {
                "name": "Tomato",
                "secondary_name": "طماطم طازجة",
                "old_price": 4.0,
                "new_price": 3.2,
                "discount": 20,
                "image_url": "./app/temp/product_images/tomato.png",
                "currency": "$"
            }
            ],
        products_per_page=9,
        template_instruction="Discount Flyer",
        theme_style="modern",
    )

    # Generate flyer
    flyer_path = template_Design(
        Super_market_info=example_request.dict(),
        product_list=example_request.products,
        shop_logo=example_request.supermarket_logo_url,
        output_path="campaign_001"
    )

    print("Flyer generated in -----", flyer_path)
