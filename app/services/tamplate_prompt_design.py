from transformers import AutoTokenizer, AutoModelForCausalLM, logging
import torch
import json
from huggingface_hub import login
from dotenv import load_dotenv
import os
import random

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

login(token=HF_TOKEN)

logging.set_verbosity_error()

MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"
device = "cuda" if torch.cuda.is_available() else "cpu"

# Global variables for model and tokenizer
tokenizer = None
model = None
MODEL_LOADED = False

def load_mistral_model():
    """Load the Mistral model and tokenizer"""
    global tokenizer, model, MODEL_LOADED
    
    if MODEL_LOADED:
        return
    
    try:
        print(f"[INFO] Loading {MODEL_NAME} on {device}...")
        
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, token=HF_TOKEN)
        
        # Add missing imports and better configuration
        from transformers import BitsAndBytesConfig
        
        # Configure quantization for better memory usage
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )
        
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            token=HF_TOKEN,
            device_map="auto",
            torch_dtype=torch.float16,
            quantization_config=quantization_config,  # Use proper quantization config
            trust_remote_code=True,  # May be needed for some models
            low_cpu_mem_usage=True,  # Optimize memory usage
            # Remove offload_folder as it's not a standard parameter
        )
        
        # Set pad token if it doesn't exist
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        MODEL_LOADED = True
        print(f"[INFO] Model loaded successfully on {device}!")
    
        
    except Exception as e:
        print(f"[WARNING] Failed to load Mistral model: {str(e)}")
        print("[INFO] Will use basic prompt generation only")
        MODEL_LOADED = False

# Try to load the model on import, but don't fail if it doesn't work
try:
    load_mistral_model()
except Exception as e:
    print(f"[WARNING] Could not load model on import: {str(e)}")
    MODEL_LOADED = False

def get_campaign_prompt(request: dict, use_augmentation: bool = True) -> str:
    """Get the campaign prompt, optionally using augmentation with Mistral model"""
    if use_augmentation and MODEL_LOADED:
        return generate_augmented_prompt(request)
    else:
        return generate_prompt_design(request)


DESIGN_THEMES = [
    "Modern minimalist with clean lines and whitespace",
    "Vibrant gradient backgrounds with dynamic shapes", 
    "Vintage/retro aesthetic with classic typography",
    "Nature-inspired with organic patterns",
    "Geometric patterns with bold color blocking",
    "Watercolor artistic style with soft edges",
    "Industrial/urban with metallic accents",
    "Elegant luxury with gold/silver highlights",
    "Playful illustration-based design",
    "High-tech futuristic with neon accents"
]

LAYOUT_ARRANGEMENTS = [
    "grid layout",
    "carousel style", 
    "featured spotlight",
    "asymmetrical artistic arrangement"
]

def generate_color_palette(theme: str, industry: str) -> List[str]:
    """Generate a unique color palette based on theme and industry"""
    color_palettes = {
        "modern": ["#2C3E50", "#ECF0F1", "#3498DB", "#E74C3C"],
        "vibrant": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"],
        "vintage": ["#D4A574", "#8B4513", "#F4E4BC", "#CD853F"],
        "nature": ["#2E8B57", "#98FB98", "#228B22", "#F0E68C"],
        "geometric": ["#FF4757", "#5352ED", "#2ED573", "#FFA502"],
        "watercolor": ["#FFB6C1", "#87CEEB", "#DDA0DD", "#F0E68C"],
        "industrial": ["#36454F", "#C0C0C0", "#708090", "#B22222"],
        "luxury": ["#FFD700", "#C0C0C0", "#000000", "#FFFFFF"],
        "playful": ["#FF69B4", "#00CED1", "#FFE135", "#32CD32"],
        "futuristic": ["#00FFFF", "#FF1493", "#7FFF00", "#9400D3"]
    }
    
    # Extract theme key from description
    theme_key = theme.split()[0].lower()
    return color_palettes.get(theme_key, ["#2C3E50", "#ECF0F1", "#3498DB", "#E74C3C"])

def generate_prompt_design(request: dict) -> str:
    """Generate a comprehensive prompt for flyer design based on campaign request"""
    
    # Extract information from the request
    supermarket_name = request.get("supermarket_name", "")
    supermarket_address = request.get("supermarket_address", "")
    supermarket_logo = str(request.get("supermarket_logo", ""))
    products = request.get("products", [])
    template_instruction = request.get("template_instruction", "")
    theme_style = request.get("theme_style", "modern")
    campaign_start_date = request.get("campaign_start_date", "")
    campaign_end_date = request.get("campaign_end_date", "")
    background_image = str(request.get("background_image", "")) if request.get("background_image") else None

    # Use theme_style from request or select random if not provided
    if theme_style and theme_style != "modern":
        # Try to find matching theme or use the provided one
        matching_themes = [theme for theme in DESIGN_THEMES if theme_style.lower() in theme.lower()]
        selected_theme = matching_themes[0] if matching_themes else random.choice(DESIGN_THEMES)
    else:
        selected_theme = random.choice(DESIGN_THEMES)
    
    selected_layout = random.choice(LAYOUT_ARRANGEMENTS)
    color_palette = generate_color_palette(selected_theme, "supermarket/retail")

    # Format products information
    products_text = ""
    for product in products:
        product_name = product.get("name", "")
        old_price = product.get("old_price", "")
        new_price = product.get("new_price", "")
        discount = product.get("discount", "")
        currency = product.get("currency", "USD")
        product_image = str(product.get("image", "")) if product.get("image") else "No image"
        description = product.get("description", "")
        
        # Format price display based on available information
        price_display = ""
        if old_price and new_price:
            price_display = f"Was {currency} {old_price}, Now {currency} {new_price}"
            if discount:
                price_display += f" (Save {discount}%)"
        elif new_price:
            price_display = f"{currency} {new_price}"
        elif old_price:
            price_display = f"{currency} {old_price}"
        else:
            price_display = "Price on request"
        
        products_text += f"- {product_name}: {price_display}"
        if description:
            products_text += f" - {description}"
        products_text += f" (Image: {product_image})\n"
    
    # Generate typography style based on theme
    typography_styles = {
        "Modern": "Clean sans-serif fonts, minimal weight variations",
        "Vibrant": "Bold, dynamic fonts with gradient effects", 
        "Vintage": "Classic serif fonts with ornamental details",
        "Nature": "Organic, handwritten-style fonts",
        "Geometric": "Angular, geometric fonts with bold weights",
        "Watercolor": "Soft, flowing script fonts",
        "Industrial": "Strong, mechanical fonts with sharp edges",
        "Elegant": "Refined serif fonts with elegant spacing",
        "Playful": "Fun, rounded fonts with varying sizes",
        "High-tech": "Futuristic, digital-style fonts"
    }
    
    theme_key = selected_theme.split()[0]
    typography = typography_styles.get(theme_key, "Clean sans-serif fonts")
    
    # Generate visual elements
    visual_elements = [
        "Background patterns complementing supermarket/retail industry",
        "Decorative borders enhancing the overall design",
        "Icons relevant to supermarket/retail business"
    ]
    
    # Add background image instruction if provided
    background_instruction = ""
    if background_image:
        background_instruction = f"\n- Use provided background image: {background_image}"
    
    # Create campaign date information
    campaign_dates = f"Campaign Period: {campaign_start_date.strftime('%B %d, %Y')} to {campaign_end_date.strftime('%B %d, %Y')}"
    
    # Create the comprehensive prompt
    flyer_prompt = f"""
        Create a professional, eye-catching {template_instruction} design with the following specifications:

        CAMPAIGN INFORMATION:
        - {campaign_dates}
        - Template Type: {template_instruction}

        LAYOUT STRUCTURE:
        - Header: Place {supermarket_name} logo ({supermarket_logo}) prominently at the top center of the flyer
        - Main Content Area: Showcase the products in an engaging {selected_layout}
        - Footer: Display {supermarket_address} clearly at the bottom

        DESIGN THEME: {selected_theme}

        COLOR PALETTE: {', '.join(color_palette)}

        PRODUCT DISPLAY INSTRUCTIONS:
        {products_text}

        CRITICAL REQUIREMENTS:
        - Use each product image exactly as provided with NO modifications, filters, effects, or alterations whatsoever
        - Product images must remain completely unchanged and unedited
        - Show product names in clear, readable typography
        - Display prices prominently near each product
        - Show discount percentages and savings clearly when available
        - Arrange products in {selected_layout}{background_instruction}

        TYPOGRAPHY STYLE: {typography}
        - Header font for supermarket name/titles
        - Body font for product names and details  
        - Price font (bold/emphasized)
        - Campaign dates font (clear and visible)

        VISUAL ELEMENTS:
        {chr(10).join([f"- {element}" for element in visual_elements])}

        SPECIFIC REQUIREMENTS:
        - The supermarket logo ({supermarket_logo}) must remain unchanged and be positioned at the top center
        - CRITICAL: All product images must be used exactly as provided with absolutely NO modifications, edits, filters, or visual changes
        - All product names and prices must be displayed exactly as provided
        - {supermarket_address} must be clearly visible in the footer
        - Campaign dates must be prominently displayed
        - Overall design should be print-ready and professional
        - Maintain good contrast and readability
        - Design should be suitable for supermarket/retail business type
        - Only the design elements around the products (backgrounds, borders, text styling) should be modified - never the actual product images

        COMPANY INFORMATION:
        - Supermarket Name: {supermarket_name}
        - Industry: Supermarket/Retail
        - Address: {supermarket_address}
        - Campaign Duration: {campaign_dates}

        Final Output: A cohesive {template_instruction} design that balances creativity with professional presentation, ensuring all required elements are prominently displayed while creating visual interest through the {selected_theme} design theme.
        """
    
    return flyer_prompt

def generate_augmented_prompt(request:dict) -> str:
    """Generate an augmented prompt using Mistral model based on campaign request"""
    
    # Check if model is loaded
    if not MODEL_LOADED or tokenizer is None or model is None:
        print("[WARNING] Mistral model not loaded, returning basic prompt")
        return generate_prompt_design(request)
    
    # First generate the base prompt
    base_prompt = generate_prompt_design(request)
    
    # Create instruction for Mistral to enhance the prompt
    mistral_instruction = f"""
You are an expert marketing and design prompt engineer. Your task is to take the following flyer design prompt and enhance it to make it more creative, detailed, and effective for generating stunning marketing materials.

Please improve the prompt by:
1. Adding more specific visual details and creative elements
2. Enhancing the marketing language to be more compelling
3. Including specific design techniques that would make the flyer more eye-catching
4. Adding details about visual hierarchy and composition
5. Suggesting specific color combinations and typography that would work well
6. Making the overall prompt more actionable for an AI image generator

Original Prompt:
{base_prompt}

Enhanced Prompt (provide only the improved version):
"""
    
    try:
        # Tokenize the instruction
        inputs = tokenizer(mistral_instruction, return_tensors="pt", truncation=True, max_length=4000)
        
        # Move inputs to the same device as the model
        inputs = {key: value.to(device) for key, value in inputs.items()}
        
        # Generate response using the model
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=1500,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                repetition_penalty=1.1
            )
        
        # Decode the response
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the enhanced prompt (remove the instruction part)
        if "Enhanced Prompt (provide only the improved version):" in generated_text:
            augmented_prompt = generated_text.split("Enhanced Prompt (provide only the improved version):")[1].strip()
        else:
            # Fallback: take the part after the original prompt
            augmented_prompt = generated_text[len(mistral_instruction):].strip()
        
        # If the augmented prompt is too short or empty, return the original
        if len(augmented_prompt) < 100:
            print("[WARNING] Generated prompt too short, returning original")
            return base_prompt
            
        return augmented_prompt
        
    except Exception as e:
        print(f"[ERROR] Failed to generate augmented prompt: {str(e)}")
        print("[INFO] Returning original prompt")
        return base_prompt

if __name__ == "__main__":
    from datetime import date
    from app.schemas.Campaign_Info import Product
    
    # Example products with enhanced information
    products_example = [
        Product(
            name="Sugar", 
            old_price=60, 
            new_price=50, 
            discount=16,
            image="sugar_product.jpg",
            currency="USD",
            description="Premium quality sugar"
        ),
        Product(
            name="Rice", 
            old_price=70, 
            new_price=60, 
            discount=14,
            image="rice_product.jpg",
            currency="USD",
            description="Long grain basmati rice"
        ),
        Product(
            name="Powdered Sugar", 
            old_price=55, 
            new_price=48, 
            discount=12,
            image="powdered_sugar_product.jpg",
            currency="USD",
            description="Fine powdered sugar"
        )
    ]

    # Create example campaign request
    example_request = CampaignRequest(
        supermarket_name="Interfood Supermarket",
        supermarket_address="123 Market Street, City Center",
        campaign_start_date=date(2025, 9, 1),
        campaign_end_date=date(2025, 9, 30),
        supermarket_logo="https://example.com/interfood_logo.png",
        products=products_example,
        products_per_page=9,
        template_instruction="Discount Flyer",
        theme_style="modern"
    )

    # Test creative prompt generation
    print("=== Testing Creative Prompt Generation ===")
    print(f"Model loaded: {MODEL_LOADED}")
    print("\n1. Original Prompt:")
    creative_prompt = generate_prompt_design(example_request)
    print(creative_prompt)
    print("\n" + "="*50 + "\n")
    
    print("2. Testing get_campaign_prompt function:")
    final_prompt = get_campaign_prompt(example_request, use_augmentation=True)
    print("Final prompt (may be augmented if model is available):")
    print(final_prompt)
    print("\n" + "="*50 + "\n")
    
    if MODEL_LOADED:
        print("3. Augmented Prompt (Enhanced by Mistral):")
        augmented_prompt = generate_augmented_prompt(example_request)
        print(augmented_prompt)
        print("\n" + "="*50 + "\n")
    else:
        print("3. Skipping augmented prompt test - model not loaded")