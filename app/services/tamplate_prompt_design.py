from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from app.schemas.Campaign_Info import CampaignRequest
from app.config import HF_TOKEN
from typing import Dict

# -----------------------------
# Model & Tokenizer Setup
# -----------------------------
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, token=HF_TOKEN)

# Load model with memory-optimized config
if device == "cuda":
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        device_map="auto",       # Automatically spread across devices
        load_in_4bit=True,       # Quantization for 8GB GPUs
        token=HF_TOKEN
    )
else:
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float32,
        token=HF_TOKEN
    )
def generate_prompt_design(request) -> str:
    """
    Generate an enhanced flyer/leaflet design prompt using an LLM.
    Accepts CampaignRequest (pydantic) or dict.
    Returns: Enhanced image generation prompt (string)
    """
    # Normalize request into dict
    if hasattr(request, "dict"):   # Pydantic object
        request_data = request.dict()
    elif isinstance(request, dict):
        request_data = request
    else:
        raise ValueError("Request must be dict or Pydantic CampaignRequest")

    # --- Build Base Prompt ---
    base_prompt = f"""
    Supermarket: {request_data.get('supermarket_name')}
    Address: {request_data.get('supermarket_address')}
    Campaign Period: {request_data.get('campaign_start_date')} → {request_data.get('campaign_end_date')}
    Campaign Type: {request_data.get('template_instruction')}
    Theme Style: {request_data.get('theme_style')}

    Products on Promotion:
    {chr(10).join([
        f"- {p['name']}: {p.get('description','')} "
        f"(Old Price: {p.get('old_price')} {p.get('currency')}, "
        f"New Price: {p.get('new_price')} {p.get('currency')}, "
        f"Discount: {p.get('discount')}%)"
        for p in request_data.get('products', [])
    ])}
    """
    product_names = ", ".join([p["name"] for p in request_data.get("products", [])])
    # --- LLM Instruction ---
    system_prompt = f"""
    You are an expert visual design prompt engineer.
    Your task is to transform the following supermarket campaign details 
    into a single powerful prompt for generating a leaflet/flyer image 
    with an AI image generation model. 
        DESIGN REQUIREMENTS:

        1. Layout & Grid System:
        - Dynamically divide A4 space based on {len(request_data.get('products', []))} products
        - For 1-3 products: Use large grid with prominent product showcase
        - For 4-6 products: Use 2x3 or 3x2 balanced grid
        - For 7-12 products: Use 3x4 or 4x3 compact grid
        - For 12+ products: Use 4x4+ dense grid with smaller product cards
        - Each layout should feel unique and well-balanced

        2. Product Display (CRITICAL):
        - Product name MUST appear exactly as written: '{product_names}' - character-for-character accuracy
        - Place product name directly below product image
        - Show prices clearly: Strike-through old price, highlight new price
        - Display discount percentage prominently
        - Ensure all text is legible and well-contrasted

        3. Visual Hierarchy:
        - Header: Store name (large, bold) + campaign period
        - Body: Product grid with images, names, and prices
        - Footer: Store address and additional information

        4. Typography & Design:
        - Use creative, modern fonts that enhance readability
        - Vary font weights and sizes for visual interest
        - Support multilingual text (English, Turkish, Japanese characters)
        - Apply consistent color scheme matching theme style

        5. Color & Branding:
        - Use theme-appropriate color palette
        - Create visual consistency without repetitive logo placement
        - Apply attractive gradients, shadows, or modern design elements
        - Ensure sufficient contrast for all text elements

        6. Quality Standards:
        - High-resolution, print-ready quality
        - Professional supermarket aesthetic
        - Clean, organized layout with proper spacing
        - Mobile-friendly visual hierarchy

        STRICT ACCURACY REQUIREMENTS:
        - Product names: 100% character-accurate reproduction
        - Prices: Exact numerical values with correct currency symbols
        - Store information: Precise spelling and formatting
        - Campaign dates: Accurate date representation

        Generate a visually stunning, unique flyer layout that maximizes visual appeal while maintaining perfect information accuracy.
        """
    new_prompt = base_prompt + system_prompt
    try:
        # Tokenize input
        inputs = tokenizer(new_prompt, return_tensors="pt", truncation=True, max_length=4000)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        # Generate response
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=1000,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                repetition_penalty=1.1
            )

        # Decode text
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print("=== Generated Enhanced Prompt ===")
        print(generated_text)



        return generated_text.strip()

    except Exception as e:
        print(f"[ERROR] Failed to generate augmented prompt: {str(e)}")
        return base_prompt


if __name__ == "__main__":
    from datetime import date
    from app.schemas.Campaign_Info import Product


    example_request = CampaignRequest(
        supermarket_name="Interfood Supermarket",
        supermarket_address="123 Market Street, City Center",
        campaign_start_date=date(2025, 9, 1),
        campaign_end_date=date(2025, 9, 30),
        supermarket_logo_url="https://example.com/interfood_logo.png",
        products=[
            Product(
                name="Apple",
                description="Fresh red apples, crisp and juicy",
                old_price=3.5,
                new_price=2.8,
                discount=20,
                image_url="apple.png",
                currency="USD"
            ),
            Product(
                name="Milk",
                description="Whole milk, 1L carton",
                old_price=2.0,
                new_price=1.7,
                discount=15,
                image_url="milk.png",
                currency="USD"
            ),
            Product(
                name="Onion",
                description="Yellow onions, per lb",
                old_price=1.2,
                new_price=1.0,
                discount=17,
                image_url="onion.png",
                currency="USD"
            ),
            Product(
                name="Potato",
                description="Fresh potatoes, per lb",
                old_price=1.5,
                new_price=1.2,
                discount=20,
                image_url="potato.png",
                currency="USD"
            )
        ],
        products_per_page=9,
        template_instruction="Discount Flyer",
        theme_style="modern",
        target_languages=["en"]
    )

    enhanced_prompt = generate_prompt_design(example_request)
    print("\n--- Enhanced Prompt ---\n")
    print(enhanced_prompt)
