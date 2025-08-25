
import base64
import requests

from app.config import HF_TOKEN

API_URL = "https://router.huggingface.co/fal-ai/fal-ai/flux-kontext/dev?_subdomain=queue"
headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
}

def query(payload):
    with open(payload["inputs"], "rb") as f:
        img = f.read()
        payload["inputs"] = base64.b64encode(img).decode("utf-8")
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content

image_bytes = query({
    "inputs": "cat.png",
    "parameters": {
        "prompt": "Turn the cat into a tiger."
    }
})
print(image_bytes)
# You can access the image with PIL.Image for example
