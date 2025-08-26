
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
print(f" Leaflet created dynamically and saved to {output_path}")

def _template_generate(flyer_prompt: str, product_list: list):
    input_images = {}
    for product in product_list:
        input_images={
            product['name']: product['product_path']
        }

    result = client.image_to_image(
        image=image_bytes,
        prompt=flyer_prompt
    )
    output_path = "leaflet_final.png"
result.save(output_path)
print(f" Leaflet created dynamically and saved to {output_path}")
