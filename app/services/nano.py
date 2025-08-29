
from huggingface_hub import InferenceClient
from PIL import Image
import os
from app.config import HF_TOKEN
# from openai import OpenAI
# # from app.config import HF_TOKEN
# HF_TOKEN = "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"
# from app.config import OPENAI_API_KEY
# client = OpenAI(api_key=OPENAI_API_KEY)
# def prompt_design(product_info: dict) -> str:
#     """
#     Generate a supermarket product card design suggestion using OpenAI.
#     """

#     system_prompt = f"""
#     You are a professional supermarket product card designer.
#     Create a clear and visually appealing design suggestion for the following product:

#     - Layout: white background, rounded corners, soft drop shadow
#     - Product Name: "{product_info['name']}" (bold, headline, centered)
#     - Old Price: "{product_info['old_price']} {product_info['currency']}" with strikethrough (red)
#     - New Price: "{product_info['new_price']} {product_info['currency']}" large, bold, green
#     - Discount: "{product_info['discount']}%" shown inside a red circular badge at top-right
#     - Extra Info at bottom: "Description: {product_info['description']}"
#     - Place a high-quality photo of the product on the left side
#     - Keep design minimal, professional, clean, print-ready
#     - Suitable for supermarket grocery and vegetable products
#     - No extra text, logos, or branding
#     """

#     response = client.chat.completions.create(
#         model="gpt-4o",  # fast + affordable, can change to gpt-4o for higher quality
#         messages=[
#             {"role": "system", "content": "You are an expert in graphic/product card design."},
#             {"role": "user", "content": system_prompt}
#         ],
#         temperature=0.7
#     )
#     prompt = response.choices[0].message.content.strip()
#     print(f"Design Prompt for {product_info['name']}:-------------------------------\n{prompt}\n")
#     return prompt

client1 = InferenceClient(
    model="Qwen/Qwen-Image-Edit",
    token=HF_TOKEN
)
def product_card_design(product_info: dict):
    image_path = product_info["image_url"]
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    # prompt = f"""
    # Create a professional product card with these exact specifications:
    
    # LAYOUT (top to bottom):
    # 1. Product image: centered, occupy upper 30% of card, maintain aspect ratio
    # 2. Text section: lower 70% with white/light background, adequate padding
    
    # VISUAL ELEMENTS:
    # - Card: white background, rounded corners (15px), soft drop shadow
    # - Discount badge: red circle, top-right corner of image, white text "{product_info['discount']}% OFF"
    
    # TEXT FORMATTING (in text section, centered alignment):
    # - Product name: "{product_info['name']}" - large bold font (24px), dark color
    # - Description: "{product_info['description']}" - medium font (16px), gray color  
    # - Old price: "{product_info['currency']}{product_info['old_price']}" - crossed out with line-through, gray color
    # - New price: "{product_info['currency']}{product_info['new_price']}" - large bold font (22px), green color (#00B050)
    
    # CRITICAL REQUIREMENTS:
    # - Currency symbol must appear before the number
    # - Old price must have visible strikethrough/line-through effect
    # - Ensure sufficient space between image and text elements
    # - Professional grocery store aesthetic
    # - Clean, minimal design with proper spacing
    # - High resolution, print-ready quality
    
    # Style: Modern supermarket product card, clean typography, professional lighting
    # """

    prompt = f"""
    1. Take this product image
    2. Add white space below the image  
    3. Write "{product_info['name']}" in bold
    4. Write "Old Price: {product_info['currency']}{product_info['old_price']}" with strikethrough
    5. Write "New Price: {product_info['currency']}{product_info['new_price']}" in green
    6. Add red "{product_info['discount']}% OFF" badge.
    Professional product card design.
    """

    result = client1.image_to_image(
        image=image_bytes,
        prompt=prompt
    )

    output_path = f"{product_info['name'].replace(' ', '_')}_card.png"
    result.save(output_path)

    return output_path

def generate_leaflet(flyer_prompt: str, product_list: list, shop_logo: str = None, output_path: str = "leaflet_final.png"):

    # --- Step 1: Generate product cards ---
    product_cards = []
    for product in product_list:
       card_img = product_card_design(product)
       product_cards.append(card_img)

    # --- Step 2: Load logo if exists ---
    logo_img = None
    if shop_logo and os.path.exists(shop_logo):
        logo_img = Image.open(shop_logo).convert("RGBA")

    # --- Step 3: Create base canvas ---
    canvas_w, canvas_h = 1200, 1600  # adjust size as needed
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (255, 255, 255, 255))

    # Place logo at top center
    y_offset = 30
    if logo_img:
        logo_img = logo_img.resize((250, 250))
        canvas.paste(logo_img, ((canvas_w - logo_img.width)//2, y_offset), logo_img)
        y_offset += logo_img.height + 30

    # Place product cards in grid layout
    x, y = 50, y_offset
    max_w, max_h = 350, 350
    padding_x, padding_y = 50, 50
    for card in product_cards:
        card_resized = card.resize((max_w, max_h))
        canvas.paste(card_resized, (x, y), card_resized)
        y += max_h + padding_y
        if y + max_h > canvas_h - 50:
            y = y_offset
            x += max_w + padding_x

    # --- Step 4: Save base layout for reference ---
    base_layout_path = "leaflet_base.png"
    canvas.save(base_layout_path)
    print(f"✅ Base layout saved at {base_layout_path}")

    # --- Step 5: Enhance with AI (optional) ---
    with open(base_layout_path, "rb") as f:
        image_bytes = f.read()
    result = client1.image_to_image(
        image=image_bytes,
        prompt=flyer_prompt
    )
    result.save(output_path)
    print(f"✅ Leaflet generated and saved at {output_path}")

    return output_path


# Example usage
if __name__ == "__main__":

    example_product = {
            "name": "Hand towel",
            "description": "Soft and absorbent hand towel",
            "old_price": 3.5,
            "new_price": 2.8,
            "discount": 20,
            "image_url": "tissue.png",
            "currency": "$"
        }
    img=product_card_design(example_product)
    print("Product card image generated in -----",img)
    products = [
        {
            "name": "Potato",
            "description": "Fresh potatoes, per lb",
            "old_price": 1.5,
            "new_price": 1.2,
            "discount": 20,
            "image_url": "potato.png",
            "currency": "USD"
        },
        {
            "name": "Milk",
            "description": "Organic fresh milk, 1L",
            "old_price": 2.5,
            "new_price": 2.0,
            "discount": 20,
            "image_url": "milk.png",
            "currency": "USD"
        },
        {
            "name": "Onion",
            "description": "Yellow onions, per lb",
            "old_price": 1.2,
            "new_price": 1.0,
            "discount": 17,
            "image_url": "onion.png",
            "currency": "USD"
        },
        {
            "name": "Apple",
            "description": "Fresh red apples, crisp and juicy",
            "old_price": 3.5,
            "new_price": 2.8,
            "discount": 20,
            "image_url": "apple.png",
            "currency": "USD"
        }
    ]

    prompt = """
    Create a professional, colorful supermarket leaflet.
    Add a big headline: "新鮮なお得情報 - 期間限定！"
    Use a vibrant background, modern typography, and highlight discounts in bold red.
    and footer for placed supermarket address:  
        Interfood Supermarket
        123 Green Street, Dhaka
        Phone: +8801XXXXXXX
        Email: info@interfood.com
        Website: www.interfood.com
    """
    

    #generate_leaflet(prompt, products, shop_logo="shop_logo.png", output_path="leaflet_new_final.png")
