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


# def generate_prompt_design(request: dict) -> str:
#     """
#     Generate an enhanced flyer/leaflet design prompt using an LLM.
#     Input: CampaignRequest (dict or Pydantic model)
#     Output: Enhanced marketing design prompt (string)
#     """
#     # Handle both dict and Pydantic model inputs
#     request_data = request.get("data", {}) if hasattr(request, "get") else request
#     print(f"[DEBUG] Request Data: {request_data}")

#     # --- Build Base Prompt ---
#     base_prompt = f"""
#     Supermarket: {request_data.get('supermarket_name')}
#     Address: {request_data.get('supermarket_address')}
#     Campaign Period: {request_data.get('campaign_start_date')} → {request_data.get('campaign_end_date')}
#     Campaign Type: {request_data.get('template_instruction')}
#     Theme Style: {request_data.get('theme_style')}

#     Products on Promotion:
#     {chr(10).join([f"- {p.name}: {p.description or ''} (Old Price: {p.old_price} {p.currency}, New Price: {p.new_price} {p.currency}, Discount: {p.discount}%)" for p in request_data.get('products', [])])}
#     """

#    # --- LLM Instruction ---
#     system_prompt = f"""
#         You are an expert **visual design prompt engineer**.
#         Your task is to transform the following supermarket campaign details 
#         into a **single powerful prompt** for generating a **leaflet/flyer image** 
#         with an AI image generation model (e.g., Stable Diffusion).

#          Enhancement Guidelines:
#         1. Describe the **overall layout** (e.g., A4 leaflet, bold headline at top, product grid in center, supermarket logo at corner).
#         2. Add **visual elements** (discount tags, banners, colorful sale stickers, price labels).
#         3. Specify **color schemes** that attract customers (e.g., red/yellow for discounts, green for freshness).
#         4. Recommend **typography style** (bold, modern, sans-serif for clarity).
#         5. Highlight **visual hierarchy** (headline → product images → discounts → address).
#         6. Ensure the style matches the theme: "{request_data.get('theme_style')}".
#         7. Keep the output as a **single descriptive prompt for image generation**.

#         --- Campaign Brief ---
#         {base_prompt}

#         --- Final Image Generation Prompt (ONLY the improved version, no explanation) ---
#     """


#     try:
#         # Tokenize input
#         inputs = tokenizer(system_prompt, return_tensors="pt", truncation=True, max_length=4000)
#         inputs = {k: v.to(device) for k, v in inputs.items()}

#         # Generate response
#         with torch.no_grad():
#             outputs = model.generate(
#                 **inputs,
#                 max_new_tokens=1000,
#                 temperature=0.7,
#                 do_sample=True,
#                 pad_token_id=tokenizer.eos_token_id,
#                 repetition_penalty=1.1
#             )

#         # Decode text
#         generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

#         # Extract clean enhanced prompt
#         if "--- Enhanced Prompt" in generated_text:
#             augmented_prompt = generated_text.split("--- Enhanced Prompt")[-1].strip()
#         else:
#             augmented_prompt = generated_text[len(system_prompt):].strip()

#         return augmented_prompt 

#     except Exception as e:
#         print(f"[ERROR] Failed to generate augmented prompt: {str(e)}")
#         return base_prompt
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

    # --- LLM Instruction ---
    system_prompt = f"""
    You are an expert **visual design prompt engineer**.
    Your task is to transform the following supermarket campaign details 
    into a **single powerful prompt** for generating a **leaflet/flyer image** 
    with an AI image generation model (e.g., Stable Diffusion).

    Enhancement Guidelines:
    1. Describe the **overall layout** (e.g., A4 leaflet, bold headline at top, product grid in center, supermarket logo at corner).
    2. Add **visual elements** (discount tags, banners, colorful sale stickers, price labels).
    3. Specify **color schemes** that attract customers (e.g., red/yellow for discounts, green for freshness).
    4. Recommend **typography style** (bold, modern, sans-serif for clarity).
    5. Highlight **visual hierarchy** (headline → product images → discounts → address).
    6. Ensure the style matches the theme: "{request_data.get('theme_style')}".
    7. Keep the output as a **single descriptive prompt for image generation**.

    --- Campaign Brief ---
    {base_prompt}

    --- Final Image Generation Prompt (ONLY the improved version, no explanation) ---
    """

    try:
        # Tokenize input
        inputs = tokenizer(system_prompt, return_tensors="pt", truncation=True, max_length=4000)
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

        # Extract clean enhanced prompt
        if "--- Final Image Generation Prompt" in generated_text:
            augmented_prompt = generated_text.split("--- Final Image Generation Prompt")[-1].strip()
        else:
            augmented_prompt = generated_text[len(system_prompt):].strip()

        return augmented_prompt or base_prompt

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
                image_url="https://example.com/images/apple.png",
                currency="USD"
            ),
            Product(
                name="Milk",
                description="Whole milk, 1L carton",
                old_price=2.0,
                new_price=1.7,
                discount=15,
                image_url="https://example.com/images/milk.png",
                currency="USD"
            ),
            Product(
                name="Onion",
                description="Yellow onions, per lb",
                old_price=1.2,
                new_price=1.0,
                discount=17,
                image_url="https://example.com/images/onion.png",
                currency="USD"
            ),
            Product(
                name="Potato",
                description="Fresh potatoes, per lb",
                old_price=1.5,
                new_price=1.2,
                discount=20,
                image_url="https://example.com/images/potato.png",
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
