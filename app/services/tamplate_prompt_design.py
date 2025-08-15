# llm_utils.py
from transformers import AutoTokenizer, AutoModelForCausalLM, logging
import torch
import json
from huggingface_hub import login
from dotenv import load_dotenv
import os

logging.set_verbosity_error()  # suppress warnings

# -----------------------------
# 0Load environment variables
# -----------------------------
load_dotenv()  # read .env file
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise ValueError("HF_TOKEN not found in environment variables. Add it to your .env file.")

# -----------------------------
#  Hugging Face login
# -----------------------------
login(token=HF_TOKEN)

# -----------------------------
#  Load Llama 2 once globally
# -----------------------------
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"

print("[INFO] Loading Llama 2 model...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_auth_token=HF_TOKEN)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    use_auth_token=HF_TOKEN,
    device_map="auto",       # Automatically use GPU if available
    torch_dtype=torch.float16  # FP16 for faster inference
)
print("[INFO] Model loaded successfully!")

# -----------------------------
#  Function to generate JSON templates per campaign
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
    Generates structured JSON templates for each page of a supermarket campaign using Llama 2.
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
            - instruction_text (for layout/design)
            Output JSON only.
        """

        # Tokenize input and send to GPU
        inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

        # Generate output
        outputs = model.generate(
            **inputs,
            max_new_tokens=500,
            temperature=0.7,
            do_sample=True,
            top_p=0.9
        )

        # Decode LLM result
        llm_json = tokenizer.decode(outputs[0], skip_special_tokens=True)

        generated_pages.append({
            "page_number": page.get("page_number", 0),
            "products": page['products'],
            "llm_generated_json": llm_json
        })

    return generated_pages
