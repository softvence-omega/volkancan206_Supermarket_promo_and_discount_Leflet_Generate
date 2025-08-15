# llm_utils.py
from transformers import AutoTokenizer, AutoModelForCausalLM, logging
import torch
import json
from huggingface_hub import login
from dotenv import load_dotenv
import os

from diffusers import DiffusionPipeline
from diffusers.utils import load_image
import torch
from typing import List, Dict, Optional
# -----------------------------
# 0. Load environment variables
# -----------------------------
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise ValueError("HF_TOKEN not found in environment variables. Add it to your .env file.")

# -----------------------------
# 1. Hugging Face login
# -----------------------------
login(token=HF_TOKEN)

# -----------------------------
# 2. Suppress transformers warnings
# -----------------------------
logging.set_verbosity_error()

# -----------------------------
# 3. Model setup
# -----------------------------
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"
device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"[INFO] Loading {MODEL_NAME} on {device}...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_auth_token=HF_TOKEN)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    use_auth_token=HF_TOKEN,
    device_map="auto",
    torch_dtype=torch.float16,
    offload_folder="offload"
)

print(f"[INFO] Model loaded successfully!")

# -----------------------------
# 4. Campaign template generation function
# -----------------------------
def generate_campaign_templates(
    supermarket_name: str,
    supermarket_address: str,
    campaign_start_date: str,
    campaign_end_date: str,
    supermarket_logo_filename: str,
    pages: list,
    template_instruction: str,
    languages: list
):
    """
    Generates structured JSON templates for each page of a supermarket campaign using Mistral-7B.
    """
    generated_pages = []

    for page in pages:
        prompt = f"""
            You are a campaign template assistant.
            Generate a structured JSON template for a supermarket campaign page.

            Supermarket: {supermarket_name}, Address: {supermarket_address}
            Campaign Dates: {campaign_start_date} to {campaign_end_date}
            Logo Filename: {supermarket_logo_filename}

            Products on this page:
            {json.dumps(page['products'], indent=2)}

            Instruction: {template_instruction}
            Languages: {', '.join(languages)}

            Generate a JSON object containing:
            - title
            - subtitle
            - products[] (with name, price, discount, image if available)
            - instruction_text
            Output JSON only.
            """
        inputs = tokenizer(prompt, return_tensors="pt").to(device)

        try:
            outputs = model.generate(
                **inputs,
                max_new_tokens=500,
                temperature=0.7,
                do_sample=True,
                top_p=0.9
            )
            llm_json = tokenizer.decode(outputs[0], skip_special_tokens=True)
        except RuntimeError as e:
            print(f"[ERROR] Generation failed for page {page.get('page_number', 0)}:", e)
            llm_json = "{}"

        # Safely parse JSON if possible
        try:
            llm_json_parsed = json.loads(llm_json)
        except json.JSONDecodeError:
            llm_json_parsed = llm_json  # fallback to raw string if invalid JSON

        generated_pages.append({
            "page_number": page.get("page_number", 0),
            "products": page['products'],
            "llm_generated_json": llm_json_parsed
        })

    return generated_pages



def generate_leaflet_diffusers(supermarket_name: str,
                               campaign_dates: str,
                               products: List[Dict],
                               logo_url: Optional[str] = None,
                               languages: List[str] = ["english"],
                               prompt_extra: Optional[str] = None,
                               device: str = "cuda") -> "Image":
    """
    Generate a realistic supermarket campaign leaflet using FLUX.1-Kontext-dev diffusion model.
    
    Args:
        supermarket_name: Name of the supermarket.
        campaign_dates: Campaign duration.
        products: List of dicts with keys: name, unit, old_price, new_price, discount.
        logo_url: Optional logo URL.
        languages: List of languages to include in the leaflet.
        prompt_extra: Any extra instructions for layout/style.
        device: "cuda" or "cpu".
    
    Returns:
        PIL Image object of the generated leaflet.
    """

    # Construct product description
    product_lines = []
    for p in products:
        line = f"{p['name']} ({p.get('unit','unit')}): {p.get('new_price')} (was {p.get('old_price')})"
        if p.get('discount'):
            line += f", Discount: {p['discount']}"
        product_lines.append(line)
    product_text = "\n".join(product_lines)

    # Build prompt
    prompt = f"""
    Create a realistic supermarket campaign leaflet.
    Supermarket: {supermarket_name}
    Campaign Dates: {campaign_dates}
    Products:
    {product_text}
    Logo URL: {logo_url or 'Not provided'}
    Languages: {', '.join(languages)}
    {prompt_extra or ''}
    High-quality, modern layout, bold discount labels, professional design.
    """

    # Load the model
    pipe = DiffusionPipeline.from_pretrained("black-forest-labs/FLUX.1-Kontext-dev", torch_dtype=torch.float16)
    pipe.to(device)

    # Generate a base image (optional: can pass a reference image if needed)
    image = pipe(prompt=prompt).images[0]

    return image


# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    products_example = [
        {"name": "Sugar", "unit": "kg", "old_price": 60, "new_price": 50, "discount": "16%"},
        {"name": "Rice", "unit": "kg", "old_price": 70, "new_price": 60, "discount": "14%"},
        {"name": "Powdered Sugar", "unit": "kg", "old_price": 55, "new_price": 48, "discount": "12%"}
    ]

    leaflet_image = generate_leaflet_diffusers(
        supermarket_name="Interfood Supermarket",
        campaign_dates="15 Aug 2025 - 25 Aug 2025",
        products=products_example,
        logo_url="https://drive.google.com/file/d/1TgcknezgDLQc7D7kA9Btamfz25WfNzoh/view?usp=sharing",
        languages=["english", "bangla"]
    )

    # Save locally
    leaflet_image.save("supermarket_leaflet.png")
    print("Leaflet saved as supermarket_leaflet.png")
