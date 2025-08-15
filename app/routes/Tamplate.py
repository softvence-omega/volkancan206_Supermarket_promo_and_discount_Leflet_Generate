# app/routes/Tamplate.py
from fastapi import APIRouter, Form, File, UploadFile, HTTPException
from typing import List, Optional
from datetime import date
import math
import json
import os
import shutil
from app.config import LOGO_UPLOAD_DIR, PRODUCT_IMAGE_UPLOAD_DIR
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
    product_names: Optional[List[str]] = Form(None),
    product_images: Optional[List[UploadFile]] = File(None),

    products_per_page: int = Form(...),
    template_instruction: str = Form(...),

    target_languages: Optional[List[str]] = Form(None),
    additional_language: Optional[str] = Form(None)
):

    # Validate at least one product
    if not products_data and not product_names and not product_images:
        raise HTTPException(status_code=400, detail="At least one product must be provided.")

    # Save logo
    logo_path = await save_file(supermarket_logo, LOGO_UPLOAD_DIR)

    # Parse products JSON
    products_list = []
    if products_data:
        try:
            products_list = json.loads(products_data)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid products_data JSON")

    # Add individual products
    if product_names or product_images:
        max_len = max(len(product_names) if product_names else 0,
                      len(product_images) if product_images else 0)
        for i in range(max_len):
            name = product_names[i] if product_names and i < len(product_names) else ""
            images = []
            if product_images and i < len(product_images):
                img_file = product_images[i]
                img_path = await save_file(img_file, PRODUCT_IMAGE_UPLOAD_DIR)
                images.append(img_file.filename)
            if not name and not images:
                continue
            products_list.append({
                "name_primary": name,
                "uploaded_images": images
            })

    # Languages
    DEFAULT_LANGUAGES = ["english", "turkish", "japanese", "bangla"]
    languages = target_languages if target_languages else DEFAULT_LANGUAGES
    if additional_language:
        additional_language = additional_language.strip().lower()
        if additional_language not in languages:
            languages.append(additional_language)

    # Split products into pages
    total_pages = max(1, math.ceil(len(products_list) / products_per_page))
    pages = []
    for i in range(total_pages):
        page_products = products_list[i*products_per_page : (i+1)*products_per_page]
        page_id = f"page_{i+1}"

        pages.append({
            "page_number": i+1,
            "products": page_products
        })

    # Call LLM service to generate JSON templates
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
        "languages": languages
    }

    return {"status": "success", "campaign_data": campaign_data}
