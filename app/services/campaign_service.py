
from app.config import HF_TOKEN

from huggingface_hub import InferenceClient

client = InferenceClient(
    provider="auto",
    api_key=HF_TOKEN,
)
prompt = """
    Create a vibrant and eye-catching leaflet design for Fresh Mart Supermarket. The leaflet should prominently feature the supermarket logo along with images of fresh apples, bananas, mangoes, and kacha rice. The headline should read:
    ‘Fresh Offer! 20% OFF on Your Favorite Fruits & Kacha Rice!’ in bold, colorful fonts. Below the headline, display the offer details:
    ‘Get 20% OFF on all apples, bananas, mangoes, and kacha rice! Stock up and save on the freshest produce and rice.’

    The leaflet should also include the following information:
    Fresh Mart Supermarket
    Address: 123 Green Street, Dhaka, Bangladesh
    Phone: +8801XXXXXXX
    Email: info@freshmart.com

    Website: www.freshmart.com

    Make sure the leaflet is visually appealing with clear, concise text. Use bright colors to make it attractive and grab attention
"""
# output is a PIL.Image object
image = client.text_to_image(
    prompt,
    model="black-forest-labs/FLUX.1-dev",
)

image.save("leaflet.png")

def campaign_generate(request):
    # Implement the campaign generation logic here
   pass


