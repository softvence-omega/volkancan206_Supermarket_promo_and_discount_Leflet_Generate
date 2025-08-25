# # nano.py
# from huggingface_hub import InferenceClient
# from PIL import Image
# import io
# import os

# # set your Hugging Face token (environment variable is safer)
# from app.config import HF_TOKEN  # make sure you've set it in your system

# client = InferenceClient(
#     model="Qwen/Qwen-Image-Edit",
#     token=HF_TOKEN
# )

# # Prompt for leaflet
# input_images = ["basmoti_rice.png", "milk.png", "shop_logo.png"]



# # Open all images
# imgs = [Image.open(p).convert("RGBA") for p in input_images]

# # --- Merge into a single canvas ---
# # Find max width and total height
# max_width = max(i.width for i in imgs)
# total_height = sum(i.height for i in imgs)

# canvas = Image.new("RGBA", (max_width, total_height), (255, 255, 255, 255))

# # Paste images vertically
# y_offset = 0
# for im in imgs:
#     canvas.paste(im, (0, y_offset), im)
#     y_offset += im.height

# # Save merged image temporarily
# merged_path = "merged_input.png"
# canvas.save(merged_path)

# # Send merged image to model
# with open(merged_path, "rb") as f:
#     image_bytes = f.read()
# prompt = """
# Create a vibrant and eye-catching leaflet design for Interfood Supermarket.
# The leaflet should prominently feature the supermarket logo{input_images[2]} along with images of fresh basmati rice{input_images[0]} and milk{input_images[1]}.
# The headline should read:
# ‘Fresh Offer! 20% OFF on Your Favorite Basmati Rice{input_images[0]} & Milk{input_images[1]}!’ in bold, colorful fonts.
# Below the headline, display the offer details:
# ‘Get 20% OFF on all basmati rice{input_images[0]} and milk{input_images[1]}! Stock up and save on the freshest produce and rice.’

# The leaflet should also include the following information:
# Interfood Supermarket
# Address: 123 Green Street, Dhaka, Bangladesh
# Phone: +8801XXXXXXX
# Email: info@interfood.com
# Website: www.interfood.com

# Make sure the leaflet is visually appealing with clear, concise text. 
# Use bright colors to make it attractive and grab attention.
# """
# result = client.image_to_image(
#     image=image_bytes,
#     prompt=prompt
# )

# # Save output
# output_path = "leaflet_final.png"
# result.save(output_path)
# print(f"✅ Leaflet created and saved to {output_path}")
# nano.py
from huggingface_hub import InferenceClient
from PIL import Image, ImageDraw, ImageFont
import os, math

from app.config import HF_TOKEN  # your token

client = InferenceClient(
    model="Qwen/Qwen-Image-Edit",
    token=HF_TOKEN
)

# --- Input images ---
# Add as many as you want, it will auto-layout
input_images = {
    "Basmati Rice": "basmoti_rice.png",
    "Milk": "milk.png",
    "Shop Logo": "shop_logo.png"
}

# Open images
imgs = {name: Image.open(path).convert("RGBA") for name, path in input_images.items()}

# --- Card settings ---
card_w, card_h = 400, 400
padding = 30

# Make product cards
cards = []
for name, im in imgs.items():
    if name == "Shop Logo":
        continue  # logo separate

    card = Image.new("RGBA", (card_w, card_h), (255, 255, 255, 255))
    im = im.resize((card_w - 40, card_h - 100))  # fit product
    card.paste(im, (20, 20), im)

    # Add product name + offer
    draw = ImageDraw.Draw(card)
    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except:
        font = ImageFont.load_default()
    draw.text((20, card_h - 60), f"{name}\n20% OFF", fill="black", font=font)

    cards.append(card)

# --- Dynamic grid calculation ---
num_products = len(cards)
cols = 2  # 2 per row (you can make it 3 if more products)
rows = math.ceil(num_products / cols)

canvas_w = cols * (card_w + padding) + padding
canvas_h = rows * (card_h + padding) + 500  # space for header/footer

canvas = Image.new("RGBA", (canvas_w, canvas_h), (255, 255, 255, 255))

# --- Header ---
logo = imgs["Shop Logo"].resize((200, 200))
canvas.paste(logo, ((canvas_w - logo.width) // 2, 20), logo)

draw = ImageDraw.Draw(canvas)
try:
    font_head = ImageFont.truetype("arialbd.ttf", 45)
except:
    font_head = ImageFont.load_default()
draw.text((padding, 250), "Fresh Offer! 20% OFF on Your Favorites!", fill="red", font=font_head)

# --- Place product cards ---
y_start = 320
x, y = padding, y_start
for i, card in enumerate(cards):
    canvas.paste(card, (x, y), card)
    x += card_w + padding
    if (i + 1) % cols == 0:
        x = padding
        y += card_h + padding

# --- Footer ---
try:
    font_footer = ImageFont.truetype("arial.ttf", 25)
except:
    font_footer = ImageFont.load_default()
footer_text = """Interfood Supermarket
123 Green Street, Dhaka
Phone: +8801XXXXXXX
Email: info@interfood.com
Website: www.interfood.com
"""
draw.text((padding, canvas_h - 150), footer_text, fill="black", font=font_footer)

merged_path = "leaflet_layout.png"
canvas.save(merged_path)

# --- Send to model for beautification ---
with open(merged_path, "rb") as f:
    image_bytes = f.read()

prompt = """
Turn this layout into a professional, colorful supermarket leaflet.
Keep products inside their cards but add shadows, borders, and a vibrant background.
Make headline bold and footer cleanly styled.
"""

result = client.image_to_image(
    image=image_bytes,
    prompt=prompt
)

output_path = "leaflet_final.png"
result.save(output_path)
print(f"✅ Leaflet created dynamically and saved to {output_path}")
