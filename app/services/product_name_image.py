from app.config import HF_TOKEN
from huggingface_hub import InferenceClient
import os
from diffusers import DiffusionPipeline
from diffusers.utils import load_image
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"
device = "cuda" if torch.cuda.is_available() else "cpu"

# --- Load tokenizer ---
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# --- Load model safely for 8GB GPU ---
if device == "cuda":
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        device_map="auto",       # automatically splits model across GPU/CPU
        load_in_4bit=True        # reduce memory usage with 8-bit quantization
    )
else:
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        device_map={"": "cpu"}   # CPU only
    )

def generate_system_prompt(product_name: str, max_tokens: int = 150) -> str:
    """
    Generate a dynamic, ad-style system prompt for any supermarket product.
    """
    user_instruction = f"""
    You are a creative assistant that generates professional, high-quality image description prompts
    for supermarket products. The prompt should:
    - Focus only on the product "{product_name}"
    - Suggest realistic commercial/advertising arrangements (e.g., multiple apples and a sliced apple, bunch of bananas, basket of potatoes)
    - Include proper lighting, clean background, visually appealing composition
    - Suitable for online ads or e-commerce
    - Keep it concise and ready for text-to-image generation
    Generate the prompt as if describing the perfect ad image.
    """

    inputs = tokenizer(user_instruction, return_tensors="pt").to(device)

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.9
        )

    generated_prompt = tokenizer.decode(output[0], skip_special_tokens=True)
    return generated_prompt.strip()
# Initialize client once
client = InferenceClient(
    provider="auto",
    api_key=HF_TOKEN,
)

def generate_product_image(product_name: str, save_path: str = None) -> str:

    prompt = generate_system_prompt(product_name)
    print(f"Generated prompt for '{product_name}': {prompt}")

    # Generate image
    image = client.text_to_image(
        prompt,
        model="black-forest-labs/FLUX.1-dev",
    )
    
    # Default save path if none provided
    if save_path is None:
        safe_name = product_name.replace(" ", "_").lower()
        save_path = f"{safe_name}.png"
    
    image.save(save_path)
    return save_path

# Example usage
if __name__ == "__main__":
    file_path = generate_product_image("potato")
    print(f"Image saved at: {file_path}")
