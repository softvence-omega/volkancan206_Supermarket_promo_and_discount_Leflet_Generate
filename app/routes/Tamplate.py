# app/routes/Tamplate.py
from fastapi import APIRouter, Form, File, UploadFile, HTTPException
from typing import List, Optional
from datetime import date
import math
import json
import os
import shutil
import time
import requests

from app.config import LOGO_UPLOAD_DIR, PRODUCT_IMAGE_UPLOAD_DIR,OPENAI_API_KEY
from app.services.tamplate_prompt_design import generate_campaign_templates

router = APIRouter()

# -----------------------------
# Utility function to save uploaded files
# -----------------------------
async def save_file(file: UploadFile, save_dir: str) -> str:
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, file.filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return save_path

# -----------------------------
# Function to generate product/page images via OpenAI
# -----------------------------
def generate_leaflet_image(prompt: str, size: str = "1024x1024") -> Optional[str]:
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    system_prompt = "Create a high-quality sticker or leaflet design"
    full_prompt = f"{system_prompt} {prompt}"
    
    data = {
        "model": "dall-e-3",
        "prompt": full_prompt,
        "n": 1,
        "size": size
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['data'][0]['url']
    else:
        print(f"[ERROR] OpenAI Image Generation Failed: {response.status_code} - {response.text}")
        return None

# -----------------------------
# Campaign creation endpoint
# -----------------------------
@router.post("/create-campaign")
async def create_campaign(
    supermarket_name: str = Form(...),
    supermarket_address: str = Form(...),
    campaign_start_date: date = Form(...),
    campaign_end_date: date = Form(...),
    supermarket_logo: UploadFile = File(...),
    products_data: Optional[str] = Form(None),
    product_images: Optional[List[UploadFile]] = File(None),
    products_per_page: int = Form(...),
    template_instruction: str = Form(...),
    target_languages: Optional[List[str]] = Form(None),
    additional_language: Optional[str] = Form(None),
    show_secondary_language: bool = Form(False),
    show_discount: bool = Form(True),
    show_old_price: bool = Form(True)
):
    # -----------------------------
    # Validate products
    # -----------------------------
    if not products_data:
        raise HTTPException(status_code=400, detail="products_data JSON is required")

    # Save supermarket logo
    await save_file(supermarket_logo, LOGO_UPLOAD_DIR)

    # Parse products JSON
    try:
        products_list = json.loads(products_data)
        if not isinstance(products_list, list):
            raise ValueError
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid products_data JSON. Must be a list.")

    # Map uploaded images to product names
    if product_images:
        for img in product_images:
            name_base = os.path.splitext(img.filename)[0].lower()
            matched = False
            for prod in products_list:
                if prod.get("name_primary", "").lower() == name_base:
                    saved_path = await save_file(img, PRODUCT_IMAGE_UPLOAD_DIR)
                    prod.setdefault("uploaded_images", []).append(os.path.basename(saved_path))
                    matched = True
                    break
            if not matched:
                await save_file(img, PRODUCT_IMAGE_UPLOAD_DIR)

    # Calculate discount if missing
    for prod in products_list:
        if "new_price" in prod and "old_price" in prod and not prod.get("discount"):
            try:
                old = float(prod["old_price"])
                new = float(prod["new_price"])
                prod["discount"] = f"{round((old - new) / old * 100)}%"
            except Exception:
                prod["discount"] = None

    # Language handling
    DEFAULT_LANGUAGES = ["english", "turkish", "japanese", "bangla"]
    languages = target_languages or DEFAULT_LANGUAGES
    if additional_language:
        additional_language = additional_language.strip().lower()
        if additional_language not in languages:
            languages.append(additional_language)

    # Split products into pages
    total_pages = max(1, math.ceil(len(products_list) / products_per_page))
    pages = []
    for i in range(total_pages):
        page_products = products_list[i*products_per_page : (i+1)*products_per_page]
        pages.append({
            "page_number": i+1,
            "products": page_products
        })

    # Generate LLM templates
    llm_pages = generate_campaign_templates(
        supermarket_name=supermarket_name,
        supermarket_address=supermarket_address,
        campaign_start_date=str(campaign_start_date),
        campaign_end_date=str(campaign_end_date),
        supermarket_logo_filename=supermarket_logo.filename,
        pages=pages,
        template_instruction=template_instruction,
        languages=languages
    )

    # -----------------------------
    # Generate leaflet images per page
    # -----------------------------
    for page in llm_pages:
        prompt_text = f"Supermarket campaign page with products: {[p['name_primary'] for p in page['products']]}, show prices, discount, layout as per template."
        image_url = generate_leaflet_image(prompt_text)
        page['leaflet_image_url'] = image_url

    campaign_data = {
        "supermarket": {
            "name": supermarket_name,
            "address": supermarket_address,
            "start_date": str(campaign_start_date),
            "end_date": str(campaign_end_date),
            "logo_filename": supermarket_logo.filename
        },
        "pages": llm_pages,
        "products_per_page": products_per_page,
        "template_instruction": template_instruction,
        "languages": languages,
        "show_secondary_language": show_secondary_language,
        "show_discount": show_discount,
        "show_old_price": show_old_price
    }

    return {"status": "success", "campaign_data": campaign_data}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(router, host="0.0.0.0", port=8000)
    