
from app.config import HF_TOKEN

from huggingface_hub import InferenceClient

client = InferenceClient(
    provider="auto",
    api_key=HF_TOKEN,
)
prompt ="Milk"
# output is a PIL.Image object
image = client.text_to_image(
    prompt,
    model="black-forest-labs/FLUX.1-dev",
)

image.save("milk.png")

def campaign_generate(request):
    # Implement the campaign generation logic here
   pass


