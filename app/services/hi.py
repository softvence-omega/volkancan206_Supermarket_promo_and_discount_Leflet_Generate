# from PIL import Image, ImageDraw, ImageFont
# from io import BytesIO
# import os
# from app.config import HF_TOKEN, CARD_DIR, GENERATED_DIR
# from app.schemas.Campaign_Info import CampaignRequest
# from pydantic import BaseModel
# from huggingface_hub import InferenceClient
# from colorthief import ColorThief

# client = InferenceClient(
#     model="Qwen/Qwen-Image-Edit",
#     token=HF_TOKEN
# )

# def product_card_design(product_info):
#     print("Converted product_info to dict:\n=============================================\n", product_info)
#     if isinstance(product_info, BaseModel):
#         product_info = product_info.model_dump()

#     print("Designing product card for:", product_info['name'])
#     print("Using image:", product_info['product_path'])
#     image_path = product_info['product_path']
#     with open(image_path, "rb") as f:
#         image_bytes = f.read()

#     prompt = f"""
#     1. Take this product image
#     2. Add white space below the image  
#     3. Write "{product_info['name']}" in bold 
#     4. Write "{product_info['secondary_name']}" in italic
#     5. Write "Old Price: {product_info['currency']}{product_info['old_price']}" with strikethrough
#     6. Write "New Price: {product_info['currency']}{product_info['new_price']}" in green and bold 
#     7. Add red "{product_info['discount']}% OFF" badge.
#     Professional product card design A6 card.
#     """

#     result = client.image_to_image(
#         image=image_bytes,
#         prompt=prompt
#     )
#     output_path = f"{CARD_DIR}/{product_info['name'].replace(' ', '_')}_card.png"
#     result.save(output_path)
#     return output_path



# # client1 = InferenceClient(provider="auto", api_key=HF_TOKEN)

# # GENERATED_DIR = "./generated"  # output directory

# # # =====================
# # # Helper: Generate Background using AI
# # # =====================
# # def generate_background(theme: str, size: tuple) -> Image.Image:
# #     """Generate a background image from text prompt using HF model."""
# #     prompt = f"Create a {size[0]}x{size[1]} image with a {theme} background."
# #     image = client1.text_to_image(prompt, model="black-forest-labs/FLUX.1-dev")
# #     # Ensure image is RGBA and resized to exact size
# #     image = image.convert("RGBA").resize(size, Image.LANCZOS)
# #     return image

# # # =====================
# # # Helper: Get Dominant Color from Image
# # # =====================
# # def extract_dominant_color(image_path: str) -> tuple:
# #     try:
# #         ct = ColorThief(image_path)
# #         return ct.get_color(quality=1)
# #     except Exception:
# #         return (50, 50, 50)  # fallback grey


# # # =====================
# # # Helper: Draw Wrapped Text
# # # =====================
# # # =====================
# # # Helper: Draw Wrapped Text (fixed for newer PIL)
# # # =====================
# # def draw_wrapped_text(draw, text, position, font, max_width, fill=(0,0,0)):
# #     words = text.split()
# #     lines, line = [], ""
# #     for w in words:
# #         test_line = f"{line} {w}".strip()
# #         # Use font.getsize instead of draw.textsize
# #         width, _ = font.getsize(test_line)
# #         if width <= max_width:
# #             line = test_line
# #         else:
# #             lines.append(line)
# #             line = w
# #     lines.append(line)
    
# #     x, y = position
# #     # Approximate line height
# #     line_height = font.getsize("A")[1] + 4
# #     for l in lines:
# #         draw.text((x, y), l, font=font, fill=fill)
# #         y += line_height
# #     return y


# # # =====================
# # # Main Template Design Function
# # # =====================
# # def template_Design(Super_market_info: dict, product_list: list, shop_logo: str, output_path: str):
# #     a4_width, a4_height = 595, 842
# #     padding = 30
# #     flyers = []

# #     # --- Open logo ---
# #     logo = Image.open(shop_logo).convert("RGBA")
# #     logo_max_width = a4_width - 2 * padding
# #     if logo.width > logo_max_width:
# #         ratio = logo_max_width / logo.width
# #         logo = logo.resize((int(logo.width * ratio), int(logo.height * ratio)), Image.LANCZOS)

# #     # --- Loop pages ---
# #     products_per_page = Super_market_info.get("products_per_page", 9)
# #     for flyer_index in range(0, len(product_list), products_per_page):
# #         chunk = product_list[flyer_index: flyer_index + products_per_page]

# #         # Adaptive grid
# #         n = len(chunk)
# #         if n <= 4: max_cards_per_row, max_rows = 2, 2
# #         elif n <= 9: max_cards_per_row, max_rows = 3, 3
# #         else: max_cards_per_row, max_rows = 4, 4

# #         # --- Collect product cards ---
# #         product_cards = []
# #         for product in chunk:
# #             card_path = product_card_design(product)
# #             card = Image.open(card_path).convert("RGBA")
# #             card_max_size = (a4_width - (max_cards_per_row + 1) * padding) // max_cards_per_row
# #             if card.width > card_max_size or card.height > card_max_size:
# #                 ratio = card_max_size / max(card.width, card.height)
# #                 card = card.resize((int(card.width * ratio), int(card.height * ratio)), Image.LANCZOS)
# #             product_cards.append(card)

# #         # --- Dynamic Heights ---
# #         card_height = max([c.height for c in product_cards], default=120)
# #         cards_section_height = (len(product_cards) // max_cards_per_row + 1) * (card_height + padding)
# #         text_section_height = 150
# #         footer_height = 60
# #         total_height = logo.height + text_section_height + cards_section_height + footer_height + 4 * padding
# #         canvas_height = max(a4_height, total_height)

# #         # --- Generate Background ---
# #         canvas = generate_background(Super_market_info["theme_style"], (a4_width, canvas_height))

# #         # --- Paste Logo ---
# #         y_offset = padding
# #         x_logo = (a4_width - logo.width) // 2
# #         canvas.paste(logo, (x_logo, y_offset), logo)
# #         y_offset += logo.height + padding

# #         # --- Draw Campaign Text ---
# #         draw = ImageDraw.Draw(canvas)
# #         title_font = ImageFont.load_default()
# #         subtitle_font = ImageFont.load_default()
# #         small_font = ImageFont.load_default()

# #         x_text = padding
# #         y_text = y_offset
# #         y_text = draw_wrapped_text(draw, Super_market_info["supermarket_name"], (x_text, y_text), title_font, a4_width-2*padding, fill=(0,0,0))
# #         y_text = draw_wrapped_text(draw, Super_market_info["Why_this_campaign"], (x_text, y_text+5), subtitle_font, a4_width-2*padding, fill=(50,50,50))
# #         campaign_dates = f"{Super_market_info['campaign_start_date']} to {Super_market_info['campaign_end_date']}"
# #         y_text = draw_wrapped_text(draw, campaign_dates, (x_text, y_text+5), small_font, a4_width-2*padding, fill=(50,50,50))

# #         y_offset = y_text + padding

# #         # --- Place Product Cards ---
# #         for i in range(0, len(product_cards), max_cards_per_row):
# #             row_cards = product_cards[i:i + max_cards_per_row]
# #             row_width = sum(c.width for c in row_cards) + (len(row_cards)-1)*padding
# #             x_offset = (a4_width - row_width)//2
# #             for card in row_cards:
# #                 canvas.paste(card, (x_offset, y_offset), card)
# #                 x_offset += card.width + padding
# #             y_offset += card_height + padding

# #         # --- Footer Strip with Dominant Color ---
# #         dom_color = extract_dominant_color(shop_logo)
# #         footer_strip = Image.new("RGBA", (a4_width, footer_height), dom_color + (180,))
# #         canvas.paste(footer_strip, (0, canvas_height-footer_height), footer_strip)
# #         draw_wrapped_text(draw, Super_market_info["supermarket_address"], (padding, canvas_height-footer_height+20), small_font, a4_width-2*padding, fill=(255,255,255))

# #         # --- Save Draft Flyer ---
# #         os.makedirs(f"{GENERATED_DIR}/{output_path}", exist_ok=True)
# #         draft_path = f"{GENERATED_DIR}/{output_path}/flyer_base_{flyer_index//products_per_page + 1}.png"
# #         canvas.save(draft_path, format="PNG")
# #         print(f"Draft flyer saved at: {draft_path}")

# #         # --- Optional AI Polishing ---
# #         buf = BytesIO()
# #         canvas.save(buf, format="PNG")
# #         merged_bytes = buf.getvalue()
# #         prompt = f"Design a professional supermarket leaflet. Theme: {Super_market_info['theme_style']}. Keep grid + logo + cards same. Add stylistic polish, smooth gradients."
# #         # Uncomment below if you want AI polishing
# #         # result = client1.image_to_image(image=merged_bytes, prompt=prompt)
# #         # final_path = f"{GENERATED_DIR}/{output_path}/flyer_{flyer_index//products_per_page + 1}.png"
# #         # result.save(final_path)

# #         final_path = draft_path  # fallback
# #         flyers.append(final_path)

# #     return final_path if len(flyers) == 1 else flyers


# def template_Design(Super_market_info: dict, product_list: list, shop_logo: str, output_path: str):
#     # --- A4 size in pixels at 72 DPI (595x842 pixels) ---
#     a4_width, a4_height = 595, 842
#     padding = 30
#     max_cards_per_row = 3
#     max_rows = 3
#     max_cards_per_page = max_cards_per_row * max_rows  # 9 per flyer

#     # --- Open shop logo ---
#     logo = Image.open(shop_logo).convert("RGBA")
#     logo_max_width = a4_width - 2 * padding
#     if logo.width > logo_max_width:
#         ratio = logo_max_width / logo.width
#         logo = logo.resize((int(logo.width * ratio), int(logo.height * ratio)), Image.LANCZOS)

#     flyers = []
#     for flyer_index in range(0, len(product_list), max_cards_per_page):
#         chunk = product_list[flyer_index: flyer_index + max_cards_per_page]

#         # --- Collect product cards ---
#         product_cards = []
#         for product in chunk:
#             card_path = product_card_design(product)
#             card = Image.open(card_path).convert("RGBA")
#             card_max_size = (a4_width - (max_cards_per_row + 1) * padding) // max_cards_per_row
#             if card.width > card_max_size or card.height > card_max_size:
#                 ratio = card_max_size / max(card.width, card.height)
#                 card = card.resize((int(card.width * ratio), int(card.height * ratio)), Image.LANCZOS)
#             product_cards.append(card)

#         # --- Layout dimensions ---
#         num_cards = len(product_cards)
#         cards_per_row = min(max_cards_per_row, num_cards) if num_cards > 0 else 1
#         num_rows = (num_cards + cards_per_row - 1) // cards_per_row
#         num_rows = min(num_rows, max_rows)

#         card_height = max([card.height for card in product_cards], default=100)
#         cards_section_height = num_rows * card_height + (num_rows + 1) * padding
#         text_section_height = 250
#         footer_height = 50

#         total_height = (
#             logo.height
#             + text_section_height
#             + cards_section_height
#             + footer_height
#             + 4 * padding
#         )
#         canvas_height = max(a4_height, total_height)

#         canvas = Image.new("RGBA", (a4_width, canvas_height), (255, 255, 255, 255))

#         # --- Paste logo ---
#         y_offset = padding
#         x_logo = (a4_width - logo.width) // 2
#         canvas.paste(logo, (x_logo, y_offset), logo)
#         y_offset += logo.height + padding

#         # --- Reserve text section ---
#         y_offset += text_section_height + padding

#         # --- Place product cards ---
#         if num_cards > 0:
#             for i in range(0, num_cards, max_cards_per_row):
#                 row_cards = product_cards[i:i + max_cards_per_row]
#                 row_width = sum(card.width for card in row_cards) + (len(row_cards) - 1) * padding
#                 x_offset = (a4_width - row_width) // 2
#                 for card in row_cards:
#                     canvas.paste(card, (x_offset, y_offset), card)
#                     x_offset += card.width + padding
#                 y_offset += card_height + padding

#         y_offset += footer_height

#         # --- Save draft flyer ---
#         os.makedirs(f"{GENERATED_DIR}/{output_path}", exist_ok=True)
#         draft_path = f"{GENERATED_DIR}/{output_path}/flyer_base_{flyer_index // max_cards_per_page + 1}.png"
#         canvas.save(draft_path, format="PNG")
#         print(f"✅ Draft flyer saved at: {draft_path}")

#         # --- Send to AI for design polish ---
#         buf = BytesIO()
#         canvas.save(buf, format="PNG")
#         merged_bytes = buf.getvalue()

#         # Prompt for AI enhancement
#         prompt = f"""
#         Design a clean, modern A4 supermarket campaign leaflet.
#         Keep the layout exactly as in the base flyer:
#         - Leaflet design style: {Super_market_info['theme_style']}
#         - Theme should reflect colors, fonts, and overall look of the chosen style.
#         - Images and text should blend naturally with the theme.

#         1. Supermarket logo centered at top.
#         2. Below the logo:
#         - Write: "{Super_market_info['supermarket_name']}" (bold, 24pt).
#         - Write: "{Super_market_info['Why_this_campaign']}" (italic, 16pt).
#         - Write: "{Super_market_info['campaign_start_date']} to {Super_market_info['campaign_end_date']}" (14pt).
#         3. Product cards stay exactly as provided; no changes.
#         4. Write: "{Super_market_info['supermarket_address']}" place at footer.
#         """

#         #Uncomment when using Qwen or OpenAI
#         result = client.image_to_image(
#             image=merged_bytes,
#             prompt=prompt
#         )
#         final_path = f"{GENERATED_DIR}/{output_path}/flyer_{flyer_index // max_cards_per_page + 1}.png"
#         result.save(final_path)
#         print(f"🎨 Final flyer saved at: {final_path}")
#         flyers.append(final_path)
        
#         return final_path if len(flyers) == 1 else flyers

# if __name__ == "__main__":
#     # Example product info
#     example_product = {
#         "name": "Potato",
#         "secondary_name": "بطاطس طازجة",
#         "old_price": 3.5,
#         "new_price": 2.8,
#         "discount": 20,
#         "image_url": "./app/temp/product_images/potato.png",
#         "currency": "$"
#     }

#     # Generate product card
#     img = product_card_design(example_product)
#     print("Product card image generated in -----", img)

#     # Campaign request
#     example_request = CampaignRequest(
#         supermarket_name="SuperMart",
#         Why_this_campaign="Best prices for fresh produce!",
#         supermarket_address="123 Main St",
#         campaign_start_date="2024-06-01",
#         campaign_end_date="2024-06-15",
#         supermarket_logo_url="./app/temp/logo/shop_logo.png",
#         products=[
#             {
#                 "name": "Potato",
#                 "secondary_name": "بطاطس طازجة",
#                 "old_price": 3.5,
#                 "new_price": 2.8,
#                 "discount": 20,
#                 "image_url": "./app/temp/product_images/potato.png",
#                 "currency": "$"
#             },
#             {
#                 "name": "Tomato",
#                 "secondary_name": "طماطم طازجة",
#                 "old_price": 4.0,
#                 "new_price": 3.2,
#                 "discount": 20,
#                 "image_url": "./app/temp/product_images/tomatoes.png",
#                 "currency": "$"
#             },
#             {
#                 "name": "Tomato",
#                 "secondary_name": "طماطم طازجة",
#                 "old_price": 4.0,
#                 "new_price": 3.2,
#                 "discount": 20,
#                 "image_url": "./app/temp/product_images/tomatoes.png",
#                 "currency": "$"
#             },
#             {
#                 "name": "Onion",
#                 "secondary_name": "بصل طازج",
#                 "old_price": 2.0,
#                 "new_price": 1.5,
#                 "discount": 25,
#                 "image_url": "./app/temp/product_images/onions.png",
#                 "currency": "$"
#             }
#         ],
#         products_per_page=9,
#         template_instruction="Discount Flyer for green and organic products",
#         theme_style="modern",
#     )

#     # Generate flyer
#     flyer_path = template_Design(
#         Super_market_info=example_request.model_dump(),
#         product_list=example_request.products,
#         shop_logo=example_request.supermarket_logo_url,
#         output_path="campaign_001"
#     )

#     print("Flyer generated in -----", flyer_path)

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
    # --- A4 size in pixels at 72 DPI (595x842 pixels) ---
    a4_width, a4_height = 595, 842
    padding = 30
    max_cards_per_page = 6  # Maximum 6 cards per page

    # --- Open shop logo ---
    logo = Image.open(shop_logo).convert("RGBA")
    logo_max_width = a4_width - 2 * padding
    logo_max_height = 120  # Set maximum logo height
    
    # Resize logo to fit within bounds
    if logo.width > logo_max_width or logo.height > logo_max_height:
        width_ratio = logo_max_width / logo.width
        height_ratio = logo_max_height / logo.height
        ratio = min(width_ratio, height_ratio)
        logo = logo.resize((int(logo.width * ratio), int(logo.height * ratio)), Image.LANCZOS)

    flyers = []
    for flyer_index in range(0, len(product_list), max_cards_per_page):
        chunk = product_list[flyer_index: flyer_index + max_cards_per_page]
        num_cards = len(chunk)
        
        # --- Dynamic layout calculation based on number of cards ---
        if num_cards == 1:
            cards_per_row = 1
        elif num_cards == 2:
            cards_per_row = 2
        elif num_cards <= 4:
            cards_per_row = 2
        else:  # 5-6 cards
            cards_per_row = 3
            
        num_rows = (num_cards + cards_per_row - 1) // cards_per_row

        # --- Collect and resize product cards ---
        product_cards = []
        for product in chunk:
            card_path = product_card_design(product)
            card = Image.open(card_path).convert("RGBA")
            
            # Dynamic card sizing based on layout
            available_width = a4_width - (cards_per_row + 1) * padding
            card_max_width = available_width // cards_per_row
            
            # Reserve space for text sections and calculate available height for cards
            text_section_height = 250
            footer_height = 50
            available_height_for_cards = a4_height - logo.height - text_section_height - footer_height - (num_rows + 3) * padding
            card_max_height = available_height_for_cards // num_rows
            
            # Resize card to fit within bounds
            if card.width > card_max_width or card.height > card_max_height:
                width_ratio = card_max_width / card.width
                height_ratio = card_max_height / card.height
                ratio = min(width_ratio, height_ratio)
                card = card.resize((int(card.width * ratio), int(card.height * ratio)), Image.LANCZOS)
            product_cards.append(card)

        # --- Calculate actual card dimensions after resizing ---
        if product_cards:
            card_height = max([card.height for card in product_cards])
        else:
            card_height = 100

        # --- Calculate canvas dimensions ---
        cards_section_height = num_rows * card_height + (num_rows + 1) * padding
        text_section_height = 250
        footer_height = 50

        total_height = (
            logo.height
            + text_section_height
            + cards_section_height
            + footer_height
            + 4 * padding
        )
        canvas_height = max(a4_height, total_height)

        canvas = Image.new("RGBA", (a4_width, canvas_height), (255, 255, 255, 255))

        # --- Paste logo ---
        y_offset = padding
        x_logo = (a4_width - logo.width) // 2
        canvas.paste(logo, (x_logo, y_offset), logo)
        y_offset += logo.height + padding

        # --- Reserve text section ---
        y_offset += text_section_height + padding

        # --- Place product cards with dynamic layout ---
        if num_cards > 0:
            card_index = 0
            for row in range(num_rows):
                # Calculate how many cards in this row
                cards_in_this_row = min(cards_per_row, num_cards - card_index)
                row_cards = product_cards[card_index:card_index + cards_in_this_row]
                
                # Center the row
                row_width = sum(card.width for card in row_cards) + (len(row_cards) - 1) * padding
                x_offset = (a4_width - row_width) // 2
                
                for card in row_cards:
                    canvas.paste(card, (x_offset, y_offset), card)
                    x_offset += card.width + padding
                
                y_offset += card_height + padding
                card_index += cards_in_this_row

        y_offset += footer_height

        # --- Save draft flyer ---
        os.makedirs(f"{GENERATED_DIR}/{output_path}", exist_ok=True)
        draft_path = f"{GENERATED_DIR}/{output_path}/flyer_base_{flyer_index // max_cards_per_page + 1}.png"
        canvas.save(draft_path, format="PNG")
        print(f"✅ Draft flyer saved at: {draft_path}")

        # --- Send to AI for design polish ---
        buf = BytesIO()
        canvas.save(buf, format="PNG")
        merged_bytes = buf.getvalue()

        # Prompt for AI enhancement
        prompt = f"""
        Design a clean, modern A4 supermarket campaign leaflet.
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
        4. Write: "{Super_market_info['supermarket_address']}" centered.
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
            },
            {
                "name": "Tomato",
                "secondary_name": "طماطم طازجة",
                "old_price": 4.0,
                "new_price": 3.2,
                "discount": 20,
                "image_url": "./app/temp/product_images/tomato.png",
                "currency": "$"
            },
            {
                "name": "Onion",
                "secondary_name": "بصل طازج",
                "old_price": 2.0,
                "new_price": 1.5,
                "discount": 25,
                "image_url": "./app/temp/product_images/onion.png",
                "currency": "$"
            }
        ],
        products_per_page=9,
        template_instruction="Discount Flyer for green and organic products",
        theme_style="modern",
    )

    # Generate flyer
    flyer_path = template_Design(
        Super_market_info=example_request.model_dump(),
        product_list=example_request.products,
        shop_logo=example_request.supermarket_logo_url,
        output_path="campaign_001"
    )

    print("Flyer generated in -----", flyer_path)