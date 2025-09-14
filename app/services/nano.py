from PIL import Image
from io import BytesIO
import os
from app.config import HF_TOKEN, CARD_DIR, GENERATED_DIR
from app.schemas.Campaign_Info import CampaignRequest
from pydantic import BaseModel
from huggingface_hub import InferenceClient

client = InferenceClient(
    model="Qwen/Qwen-Image-Edit",
    token=HF_TOKEN
)

def product_card_design(product_info):
    print("Converted product_info to dict:\n=============================================\n", product_info)
    if isinstance(product_info, BaseModel):
        product_info = product_info.model_dump()

    print("Designing product card for:", product_info['name'])
    # Use image_url if product_path is not available
    image_path = product_info.get('product_path') or product_info.get('image_url')
    print("Using image:", image_path)
    
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    prompt = f"""
    1. Take this product image
    2. Add white space below the image  
    3. Write "{product_info['name']}" in bold 
    4. Write "{product_info['secondary_name']}" in italic
    5. Write "Old Price: {product_info['currency']}{product_info['old_price']}" with strikethrough
    6. Write "New Price: {product_info['currency']}{product_info['new_price']}" in green and bold 
    7. Add red "{product_info['discount']}% OFF" badge.
    Professional product card design A6 card.
    """

    result = client.image_to_image(
        image=image_bytes,
        prompt=prompt
    )
    output_path = f"{CARD_DIR}/{product_info['name'].replace(' ', '_')}_card.png"
    result.save(output_path)
    return output_path

def template_Design(Super_market_info: dict, product_list: list, shop_logo: str, output_path: str):
    # --- A4 width, dynamic height based on product count ---
    a4_width = 595
    base_height = 400  # Minimum height
    max_cards_per_page = 6  # Maximum 6 cards per page
    
    # Calculate total products to determine sizing scale
    # (Currently used for future enhancements)

    flyers = []
    for flyer_index in range(0, len(product_list), max_cards_per_page):
        chunk = product_list[flyer_index: flyer_index + max_cards_per_page]
        num_cards = len(chunk)
        
        # --- Dynamic flyer height based on number of products ---
        # More products = taller flyer to accommodate them properly
        if num_cards == 1:
            flyer_height = base_height + 200  # 600px total
        elif num_cards == 2:
            flyer_height = base_height + 300  # 700px total
        elif num_cards <= 4:
            flyer_height = base_height + 400  # 800px total
        elif num_cards <= 6:
            flyer_height = base_height + 500  # 900px total - maximum height
        else:
            flyer_height = base_height + 500  # 900px total
        
        # Use 95% of the flyer space for logo + cards
        usable_height = int(flyer_height * 0.95)
        padding = int(flyer_height * 0.025)  # 2.5% for padding
        
        # --- Dynamic layout calculation ---
        if num_cards == 1:
            cards_per_row = 1
        elif num_cards == 2:
            cards_per_row = 2
        elif num_cards <= 4:
            cards_per_row = 2
        else:  # 5-6 cards
            cards_per_row = 3
            
        num_rows = (num_cards + cards_per_row - 1) // cards_per_row
        
        # --- Divide usable space: 20% for logo, 80% for cards ---
        logo_section_height = int(usable_height * 0.20)
        cards_section_height = int(usable_height * 0.80)
        
        # --- Load and resize logo to fit its section ---
        logo = Image.open(shop_logo).convert("RGBA")
        logo_max_width = a4_width - 2 * padding
        logo_max_height = logo_section_height - padding
        
        if logo.width > logo_max_width or logo.height > logo_max_height:
            width_ratio = logo_max_width / logo.width
            height_ratio = logo_max_height / logo.height
            ratio = min(width_ratio, height_ratio)
            logo = logo.resize((int(logo.width * ratio), int(logo.height * ratio)), Image.LANCZOS)

        # --- Generate and resize product cards to fit cards section ---
        product_cards = []
        
        # Calculate card dimensions based on available space and number of cards
        available_width = a4_width - (cards_per_row + 1) * padding
        card_max_width = available_width // cards_per_row
        
        available_height = cards_section_height - (num_rows + 1) * padding
        card_max_height = available_height // num_rows
        
        for product in chunk:
            card_path = product_card_design(product)
            card = Image.open(card_path).convert("RGBA")
            
            # Resize card to fit within calculated bounds
            if card.width > card_max_width or card.height > card_max_height:
                width_ratio = card_max_width / card.width
                height_ratio = card_max_height / card.height
                ratio = min(width_ratio, height_ratio)
                card = card.resize((int(card.width * ratio), int(card.height * ratio)), Image.LANCZOS)
            product_cards.append(card)

        # --- Create canvas with dynamic height ---
        canvas = Image.new("RGBA", (a4_width, flyer_height), (255, 255, 255, 255))

        # --- Place logo in top section (centered) ---
        y_offset = padding
        x_logo = (a4_width - logo.width) // 2
        canvas.paste(logo, (x_logo, y_offset), logo)
        y_offset = logo_section_height + padding

        # --- Place product cards in cards section ---
        if num_cards > 0:
            # Get actual card dimensions after resizing
            if product_cards:
                actual_card_height = max([card.height for card in product_cards])
            else:
                actual_card_height = 100
            
            card_index = 0
            for row in range(num_rows):
                # Calculate how many cards in this row
                cards_in_this_row = min(cards_per_row, num_cards - card_index)
                row_cards = product_cards[card_index:card_index + cards_in_this_row]
                
                # Center the row horizontally
                row_width = sum(card.width for card in row_cards) + (len(row_cards) - 1) * padding
                x_offset = (a4_width - row_width) // 2
                
                for card in row_cards:
                    canvas.paste(card, (x_offset, y_offset), card)
                    x_offset += card.width + padding
                
                y_offset += actual_card_height + padding
                card_index += cards_in_this_row

        # --- Save draft flyer ---
        os.makedirs(f"{GENERATED_DIR}/{output_path}", exist_ok=True)
        draft_path = f"{GENERATED_DIR}/{output_path}/flyer_base_{flyer_index // max_cards_per_page + 1}.png"
        canvas.save(draft_path, format="PNG")
        print(f"✅ Draft flyer saved at: {draft_path}")
        print(f"   Flyer dimensions: {a4_width}x{flyer_height}px")
        print(f"   Cards: {num_cards}, Layout: {cards_per_row} per row, {num_rows} rows")
        print(f"   Logo section: {logo_section_height}px, Cards section: {cards_section_height}px")

        # --- Send to AI for design polish ---
        buf = BytesIO()
        canvas.save(buf, format="PNG")
        merged_bytes = buf.getvalue()

        # Prompt for AI enhancement
        prompt = f"""
        Design a clean, modern supermarket campaign leaflet.
        Keep the layout exactly as in the base flyer:
        - Leaflet design style: {Super_market_info['theme_style']}
        - Theme should reflect colors, fonts, and overall look of the chosen style.
        - Images and text should blend naturally with the theme.

        1. Supermarket logo centered at top.
        2. Below the logo:
        - Write: "{Super_market_info['supermarket_name']}" (bold, 24pt).
        - Write: "{Super_market_info['Why_this_campaign']}" (italic, 16pt).
        - Write: "{Super_market_info['campaign_start_date']} to {Super_market_info['campaign_end_date']}" (14pt).
        3. Product cards stay exactly as provided; no changes.
        4. Write: "{Super_market_info['supermarket_address']}" footer at leaflet.
        """

        #Uncomment when using Qwen or OpenAI
        result = client.image_to_image(
            image=merged_bytes,
            prompt=prompt
        )
        final_path = f"{GENERATED_DIR}/{output_path}/flyer_{flyer_index // max_cards_per_page + 1}.png"
        result.save(final_path)
        print(f"🎨 Final flyer saved at: {final_path}")
        flyers.append(final_path)
        
    return flyers[0] if len(flyers) == 1 else flyers

if __name__ == "__main__":
    # Example product info
    example_product = {
        "name": "Potato",
        "secondary_name": "بطاطس طازجة",
        "old_price": 3.5,
        "new_price": 2.8,
        "discount": 20,
        "image_url": "temp/product_images/potato.png",
        "currency": "$"
    }

    #Generate product card
    img = product_card_design(example_product)
    print("Product card image generated in -----", img)

    #Campaign request
    example_request = CampaignRequest(
        supermarket_name="SuperMart",
        Why_this_campaign="Best prices for fresh produce!",
        supermarket_address="123 Main St",
        campaign_start_date="2024-06-01",
        campaign_end_date="2024-06-15",
        supermarket_logo_url="temp/logo/shop_logo.png",
        products=[
            {
                "name": "Potato",
                "secondary_name": "بطاطس طازجة",
                "old_price": 3.5,
                "new_price": 2.8,
                "discount": 20,
                "image_url": "temp/product_images/potato.png",
                "currency": "$"
            },
            {
                "name": "Tomato",
                "secondary_name": "طماطم طازجة",
                "old_price": 4.0,
                "new_price": 3.2,
                "discount": 20,
                "image_url": "temp/product_images/tomato.png",
                "currency": "$"
            },
            {
                "name": "Tomato",
                "secondary_name": "طماطم طازجة",
                "old_price": 4.0,
                "new_price": 3.2,
                "discount": 20,
                "image_url": "temp/product_images/tomato.png",
                "currency": "$"
            },
            {
                "name": "Onion",
                "secondary_name": "بصل طازج",
                "old_price": 2.0,
                "new_price": 1.5,
                "discount": 25,
                "image_url": "temp/product_images/onion.png",
                "currency": "$"
            }
        ],
        products_per_page=9,
        template_instruction="Discount Flyer for green and organic products",
        theme_style="modern",
    )

    # Generate flyer
    flyer_path = template_Design(example_request, example_request.products, example_request.supermarket_logo_url, "example_flyer")


    print("Flyer generated in -----", flyer_path)
